/*
 * Copyright (c) 2021 SIGNET Lab, Department of Information Engineering,
 * University of Padova
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 */

#include <fstream>
#include <iomanip>
#include "ns3/core-module.h"
#include "ns3/mobility-module.h"
#include "ns3/gemv-propagation-loss-model.h"
#include "ns3/gemv-tag.h"
#include "ns3/log.h"
#include "ns3/simulator.h"
#include "ns3/network-module.h"
#include "ns3/applications-module.h"
#include "ns3/multi-model-spectrum-channel.h"
#include "ns3/mmwave-helper.h"
#include "ns3/mmwave-point-to-point-epc-helper.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-helper.h"
#include <unistd.h>

#include "ns3/seq-ts-size-frag-header.h"
#include "ns3/bursty-helper.h"
#include "ns3/burst-sink-helper.h"
#include "ns3/bursty-app-stats-calculator.h"

using namespace ns3;
using namespace mmwave;

NS_LOG_COMPONENT_DEFINE ("GemvIntegrationExample");

static void
RxBurstCallback (uint32_t nodeId, Ptr<BurstyAppStatsCalculator> statsCalculator, Ptr<const Packet> burst, const Address &from,
         const Address &to, const SeqTsSizeFragHeader &header)
{
  statsCalculator->RxBurst (nodeId, burst, from, to, header);
}

static void
TxBurstCallback (uint32_t nodeId, Ptr<BurstyAppStatsCalculator> statsCalculator, Ptr<const Packet> burst,
                 const Address &from, const Address &to, const SeqTsSizeFragHeader &header)
{
  statsCalculator->TxBurst (nodeId, burst, from, to, header);
}

int
main (int argc, char *argv[])
{
  uint32_t numUes = 1;
  uint32_t firstVehicleIndex = 0;
  uint32_t packetSizeBytes = 20000;
  double ulIpiMicroS = 100e3;
  double dlIpiMicroS = 500e3;
  double bandwidth = 50e6;
  std::string appTracesPath = "input/kitti-dataset.csv";
  std::string gemvTracesPath = "/home/dragomat/Documents/ns3-mmwave-pqos/input/bolognaLeftHalfRSU3_50vehicles_100sec/13-May-2021_";
  std::string appType = "kitti";
  uint32_t kittiModel = 1450;
  double txPower = 30.0;

  CommandLine cmd;
  cmd.AddValue ("numUes", "Number of UE nodes", numUes);
  cmd.AddValue ("firstVehicleIndex", "Index of the trajectory to be assigned to the first node."
                                     "If there are multiple nodes, subsequent trajectory indeces" 
                                     "will be assigned", firstVehicleIndex);
  cmd.AddValue ("ulIpiMicroS", "Uplink IPI in ms", ulIpiMicroS);
  cmd.AddValue ("dlIpiMicroS", "Downlink IPI in ms", dlIpiMicroS);
  cmd.AddValue ("gemvTracesPath", "Path of the GEMv2 traces", gemvTracesPath);
  cmd.AddValue ("appTracesPath", "The path to the input trace of the application, if applicable.",
                appTracesPath);
  cmd.AddValue ("applicationType", "Uplink application to install in the clients [classic, kitti].", appType);
  cmd.AddValue ("kittiModel", "Compression type [1450, 1451, 1452, 1150]", kittiModel);
  cmd.AddValue ("txPower", "The vehicle tx power in dBm", txPower);
  cmd.Parse (argc, argv);
  
  Config::SetDefault ("ns3::MmWaveBearerStatsCalculator::AggregatedStats", BooleanValue (true));
  Config::SetDefault ("ns3::MmWaveBearerStatsCalculator::EpochDuration", TimeValue (Seconds (0.1)));
  Config::SetDefault ("ns3::BurstyAppStatsCalculator::EpochDuration", TimeValue (Seconds (0.1)));
  Config::SetDefault ("ns3::KittiTraceBurstGenerator::Model", UintegerValue (kittiModel));
  Config::SetDefault ("ns3::MmWavePhyMacCommon::Bandwidth", DoubleValue (bandwidth));
  Config::SetDefault ("ns3::MmWaveHelper::RlcAmEnabled", BooleanValue (true));
  Config::SetDefault ("ns3::UdpClient::PacketSize", UintegerValue (packetSizeBytes));
  Config::SetDefault ("ns3::MmWavePhyMacCommon::NumHarqProcess", UintegerValue (100));
  Config::SetDefault ("ns3::LteRlcAm::PollRetransmitTimer", TimeValue (MilliSeconds (100)));
  Config::SetDefault ("ns3::MmWaveUePhy::TxPower", DoubleValue (txPower));
  
  Ptr<GemvPropagationLossModel> gemv = CreateObject<GemvPropagationLossModel> ();
  
  char buffer [256];
  std::cout << "Current path is " << getcwd (buffer, sizeof (buffer)) << std::endl;
  gemv->SetPath (gemvTracesPath);
  Time timeRes = MilliSeconds (100);
  gemv->SetTimeResolution (timeRes);
  Time maxSimTime = gemv->GetMaxSimulationTime ();
  gemv->SetAttribute ("IncludeSmallScale", BooleanValue (true));

  std::vector<uint16_t> rsuList = gemv->GetDistinctIds(true);
  std::vector<uint16_t> ueList = gemv->GetDistinctIds(false);

  std::cout << ueList.size ()<< std::endl;
  NS_ABORT_MSG_IF (ueList.size () < numUes, "Too many UEs");
  
  NodeContainer rsuNodes;  
  NodeContainer ueNodes;
  
  for (const auto& i : rsuList)
  {
    // create the RSU node and add it to the container
    Ptr<Node> n = CreateObject<Node> ();
    rsuNodes.Add (n);
    
    // create the gemv tag and aggrgate it to the node
    Ptr<GemvTag> tag = CreateObject<GemvTag>();
    tag->SetTagId(i);
    tag->SetNodeType(true);
    n->AggregateObject (tag);
  }
  std::cout << "Number of RSU nodes: " << rsuNodes.GetN () << std::endl;
  NS_ABORT_MSG_IF (rsuNodes.GetN () > 1, "This example works with a single RSU");
  
  for (size_t i = firstVehicleIndex; i < firstVehicleIndex + numUes; i++)
  {
    // create the vehicular node and add it to the container
    Ptr<Node> n = CreateObject<Node> ();
    ueNodes.Add (n);
    
    // create the gemv tag and aggrgate it to the node
    Ptr<GemvTag> tag = CreateObject<GemvTag>();
    tag->SetTagId (ueList.at (i));
    tag->SetNodeType (false);
    n->AggregateObject (tag);
  }
  std::cout << "Number of UE nodes: " << ueNodes.GetN () << std::endl;
  NS_ABORT_MSG_IF (ueNodes.GetN () < 1, "At least one UE is required");

  // Install Mobility Model
  // NB: mobility of vehicular nodes is already taken into account in GEMV 
  // traces, we use a constant position mobility model
  MobilityHelper mobility;
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (NodeContainer (rsuNodes, ueNodes));
  
  // Manually create a new SpectrumChannel and add the GemvPropagationLossModel
  Ptr<MultiModelSpectrumChannel> channel = CreateObject<MultiModelSpectrumChannel> ();
  channel->AddPropagationLossModel (gemv);
  
  // Create the MmWaveHelper and manually set the SpectrumChannel to be used
  Ptr<MmWaveHelper> mmWaveHelper = CreateObject<MmWaveHelper> ();
  Ptr<MmWavePointToPointEpcHelper>  epcHelper = CreateObject<MmWavePointToPointEpcHelper> ();
  mmWaveHelper->SetEpcHelper (epcHelper);
  mmWaveHelper->SetChannel (channel, 0);
  
  Ptr<Node> pgw = epcHelper->GetPgwNode ();

  // Create a single RemoteHost
  Ptr<Node> remoteHost = CreateObject<Node> ();
  InternetStackHelper internet;
  internet.Install (remoteHost);

  // Create the Internet
  PointToPointHelper p2ph;
  p2ph.SetDeviceAttribute ("DataRate", DataRateValue (DataRate ("100Gb/s")));
  p2ph.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2ph.SetChannelAttribute ("Delay", TimeValue (Seconds (0.010)));
  NetDeviceContainer internetDevices = p2ph.Install (pgw, remoteHost);
  Ipv4AddressHelper ipv4h;
  ipv4h.SetBase ("1.0.0.0", "255.0.0.0");
  Ipv4InterfaceContainer internetIpIfaces = ipv4h.Assign (internetDevices);
  // interface 0 is localhost, 1 is the p2p device
  Ipv4Address remoteHostAddr = internetIpIfaces.GetAddress (1);

  Ipv4StaticRoutingHelper ipv4RoutingHelper;
  Ptr<Ipv4StaticRouting> remoteHostStaticRouting = ipv4RoutingHelper.GetStaticRouting (remoteHost->GetObject<Ipv4> ());
  remoteHostStaticRouting->AddNetworkRouteTo (Ipv4Address ("7.0.0.0"), Ipv4Mask ("255.0.0.0"), 1);
  
  NetDeviceContainer rsuDevs = mmWaveHelper->InstallSub6EnbDevice (rsuNodes);
  NetDeviceContainer ueDevs = mmWaveHelper->InstallSub6UeDevice (ueNodes);
  
  // Install the IP stack on the UEs
  internet.Install (ueNodes);
  Ipv4InterfaceContainer ueIpIface;
  ueIpIface = epcHelper->AssignUeIpv4Address (NetDeviceContainer (ueDevs));
  
  // Assign IP address to UEs, and install applications
  for (uint32_t u = 0; u < ueNodes.GetN (); ++u)
    {
      Ptr<Node> ueNode = ueNodes.Get (u);
      // Set the default gateway for the UE
      Ptr<Ipv4StaticRouting> ueStaticRouting = ipv4RoutingHelper.GetStaticRouting (ueNode->GetObject<Ipv4> ());
      ueStaticRouting->SetDefaultRoute (epcHelper->GetUeDefaultGatewayAddress (), 1);
    }

  // Attach the UEs to the RSU
  mmWaveHelper->AttachToClosestEnb (ueDevs, rsuDevs);

  // Install and start applications on UEs and remote host
  uint16_t dlPort = 1000;
  uint16_t ulPort = 2000;
  ApplicationContainer clientApps;
  ApplicationContainer serverApps;
  Ptr<BurstyAppStatsCalculator> statsCalculator = CreateObject<BurstyAppStatsCalculator>();
  Time ulIpi = MicroSeconds (ulIpiMicroS);
  Time dlIpi = MicroSeconds (dlIpiMicroS);
  
  for (uint32_t u = 0; u < ueNodes.GetN (); ++u)
    {
      // Set up DL application
      PacketSinkHelper dlPacketSinkHelper ("ns3::UdpSocketFactory",
                                           InetSocketAddress (Ipv4Address::GetAny (), dlPort));
      dlPacketSinkHelper.SetAttribute ("EnableSeqTsSizeHeader", BooleanValue (true));
      serverApps.Add (dlPacketSinkHelper.Install (ueNodes.Get (u)));

      UdpClientHelper dlClient (ueIpIface.GetAddress (u), dlPort);
      dlClient.SetAttribute ("Interval", TimeValue (dlIpi));
      dlClient.SetAttribute ("MaxPackets", UintegerValue (0xFFFFF));

      clientApps.Add (dlClient.Install (remoteHost));


      // Set up UL Application

      if (appType == "classic")
        {
          PacketSinkHelper ulPacketSinkHelper ("ns3::UdpSocketFactory",
                                               InetSocketAddress (Ipv4Address::GetAny (), ulPort));
          ulPacketSinkHelper.SetAttribute ("EnableSeqTsSizeHeader", BooleanValue (true));
          serverApps.Add (ulPacketSinkHelper.Install (remoteHost));

          UdpClientHelper ulClient (remoteHostAddr, ulPort);
          ulClient.SetAttribute ("Interval", TimeValue (ulIpi));
          ulClient.SetAttribute ("MaxPackets", UintegerValue (0xFFFFF));

          clientApps.Add (ulClient.Install (ueNodes.Get (u)));
        }
      else if (appType == "kitti")
        {
          // Create bursty application helper
          BurstyHelper burstyHelper ("ns3::UdpSocketFactory",
                                     InetSocketAddress (remoteHostAddr, ulPort));
          burstyHelper.SetAttribute ("FragmentSize", UintegerValue (1200));
          burstyHelper.SetBurstGenerator ("ns3::KittiTraceBurstGenerator", "TraceFile", StringValue (appTracesPath));

          clientApps.Add (burstyHelper.Install (ueNodes.Get (u)));

          Ptr<BurstyApplication> burstyApp = DynamicCast<BurstyApplication>  (clientApps.Get ( clientApps.GetN() - 1 )); // obtain the last one inserted
          burstyApp->TraceConnectWithoutContext ("BurstTx", MakeBoundCallback (&TxBurstCallback, ueNodes.Get (u)->GetId(), statsCalculator));

          // Create burst sink helper
          BurstSinkHelper burstSinkHelper ("ns3::UdpSocketFactory",
                                           InetSocketAddress (Ipv4Address::GetAny (), ulPort));
          // Install bursty sink
          serverApps.Add (burstSinkHelper.Install (remoteHost));
          Ptr<BurstSink> burstSink = DynamicCast<BurstSink> (serverApps.Get ( serverApps.GetN() - 1 )); // obtain the last one inserted

          // Connect application traces
          burstSink->TraceConnectWithoutContext ("BurstRx", MakeBoundCallback (&RxBurstCallback, ueNodes.Get (u)->GetId(), statsCalculator));
        }
      else
        {
          NS_FATAL_ERROR ("Application not supported.");
        }

      ++ulPort;
    }
  
  if (appType == "classic")
  {
    std::cout << "UL APP: UDP | Total UL rate " << packetSizeBytes * 8 / ulIpi.GetSeconds () / 1e6 * numUes << " Mbps" << std::endl;
  }
  else if (appType == "kitti")
  {
    std::cout << "UL APP: kitti | Compression level " << kittiModel << std::endl;
  }
  std::cout << "DL APP: UDP | Total DL rate " << packetSizeBytes * 8 / dlIpi.GetSeconds () / 1e6 * numUes << " Mbps" << std::endl;

  serverApps.Start (MilliSeconds (10));
  clientApps.Start (MilliSeconds (100));
  clientApps.Stop (maxSimTime - Seconds (2.0));
  mmWaveHelper->EnableTraces ();
  
  Time simTime = maxSimTime - Seconds (1.0);
  std::cout << "Max simulation time: " << maxSimTime.GetSeconds () << " s" << "\n";
  std::cout << "Actual simulation time: " << simTime.GetSeconds () << " s" << "\n";
  Simulator::Stop(simTime); 
  Simulator::Run();

  Simulator::Destroy ();
  return 0;
}
