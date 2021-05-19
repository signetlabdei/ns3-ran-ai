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
#include "ns3/core-module.h"
#include "ns3/mobility-module.h"
#include "ns3/gemv-propagation-loss-model.h"
#include "ns3/gemv-tag.h"
#include "ns3/log.h"
#include "ns3/simulator.h"
#include "ns3/network-module.h"
#include "ns3/applications-module.h"
using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("GemvPropagationTest");

void static
PrintHeader (Ptr<OutputStreamWrapper> stream, NodeContainer ues)
{
  *stream->GetStream () << "Time\t";
  for (uint16_t i = 0; i < ues.GetN(); i++)
  {
    *stream->GetStream () << "node-" << +i << "\t";
  }
  *stream->GetStream () << std::endl;
}

void static 
ReadPower (Ptr<OutputStreamWrapper> stream, Ptr<GemvPropagationLossModel> gemv, double txPowerDbm, Ptr<Node> rsu, NodeContainer ues)
{
  if (Simulator::Now ().IsZero ())
  {
    PrintHeader (stream, ues);
  }
  
  // print the rx power
  *stream->GetStream () << Simulator::Now ().GetSeconds () << "\t" ; 
  for (uint16_t i = 0; i < ues.GetN(); i++)
  {
    NS_LOG_DEBUG ("Time " << Simulator::Now ().GetSeconds () << " node " << +i << 
                  " gain " <<  gemv->DoCalcRxPower(txPowerDbm, rsu->GetObject<MobilityModel> (), ues.Get(i)->GetObject<MobilityModel> ()));
    *stream->GetStream () << gemv->DoCalcRxPower(txPowerDbm, rsu->GetObject<MobilityModel> (), ues.Get(i)->GetObject<MobilityModel> ()) << "\t";
  }
  *stream->GetStream () << std::endl;
}

void static 
ReadLosCondition (Ptr<OutputStreamWrapper> stream, Ptr<GemvPropagationLossModel> gemv, Ptr<Node> rsu, NodeContainer ues)
{
  // print the header
  if (Simulator::Now ().IsZero ())
  {
    PrintHeader (stream, ues);
  }
  
  // print the los condition
  *stream->GetStream () << Simulator::Now ().GetSeconds () << "\t";
  for (uint8_t i = 0; i < ues.GetN (); i++)
    {
      NS_LOG_DEBUG ("Time " << Simulator::Now ().GetSeconds () << " node " << +i << 
                    " los condition " <<  +gemv->ReadPairLosCondition (rsu->GetObject<MobilityModel> (), ues.Get (i)->GetObject<MobilityModel> ()));
      *stream->GetStream () << +gemv->ReadPairLosCondition (rsu->GetObject<MobilityModel> (), ues.Get (i)->GetObject<MobilityModel> ()) << "\t";
    }
  *stream->GetStream () << std::endl;
}

int
main (int argc, char *argv[])
{
  CommandLine cmd;
  cmd.Parse (argc, argv);
  
  Ptr<GemvPropagationLossModel> gemv = CreateObject<GemvPropagationLossModel> ();
  gemv->SetPath ("/home/tommaso/workspace/huawei-pqos/GEMV2PackageV1.2/outputSim/bolognaLeftHalfRSU3_50vehicles_100sec/13-May-2021_");
  Time timeRes = MilliSeconds (100);
  gemv->SetTimeResolution (timeRes);
  Time simTime = gemv->GetMaxSimulationTime ();
  NS_LOG_UNCOND ("Simulation time: " << simTime.GetSeconds () << " s");
  gemv->SetAttribute ("IncludeSmallScale", BooleanValue (false));

  std::vector<uint16_t> rsuList = gemv->GetDistinctIds(true);
  std::vector<uint16_t> ueList = gemv->GetDistinctIds(false);
  
  NodeContainer rsuNodes;  
  NodeContainer ueNodes;
  
  for (const auto& i : rsuList)
  {
    // create the RSU node and add it to the container
    Ptr<Node> n = CreateObject<Node> ();
    rsuNodes.Add (n);
    
    // create the gemv tag and aggregate it to the node
    Ptr<GemvTag> tag = CreateObject<GemvTag>();
    tag->SetTagId(i);
    tag->SetNodeType(true);
    n->AggregateObject (tag);
  }
  NS_LOG_UNCOND ("Number of RSU nodes: " << rsuNodes.GetN ());
  NS_ABORT_MSG_IF (rsuNodes.GetN () > 1, "This example works with a single RSU");
  
  for (const auto& i : ueList)
  {
    // create the vehicular node and add it to the container
    Ptr<Node> n = CreateObject<Node> ();
    ueNodes.Add (n);
    
    // create the gemv tag and aggregate it to the node
    Ptr<GemvTag> tag = CreateObject<GemvTag>();
    tag->SetTagId(i);
    tag->SetNodeType(false);
    n->AggregateObject (tag);
  }
  NS_LOG_UNCOND ("Number of UE nodes: " << ueNodes.GetN ());

  // Install Mobility Model
  // NB: mobility of vehicular nodes is already taken into account in GEMV 
  // traces, we use a constant position mobility model
  MobilityHelper mobility;
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (rsuNodes);
  mobility.Install (ueNodes);

  AsciiTraceHelper asciiTraceHelper;
  Ptr<OutputStreamWrapper> stream_1 = asciiTraceHelper.CreateFileStream ("receivedPower.txt");
  Ptr<OutputStreamWrapper> stream_2 = asciiTraceHelper.CreateFileStream ("losCondition.txt");

  for (auto i = 0; i < simTime / timeRes; i++)
  {
    Simulator::Schedule (timeRes * i, &ReadPower, stream_1, gemv, 0, rsuNodes.Get (0), ueNodes);
    Simulator::Schedule (timeRes * i, &ReadLosCondition, stream_2, gemv, rsuNodes.Get (0), ueNodes);
  } 

  Simulator::Run();
  Simulator::Stop(simTime);
  return 0;
}
