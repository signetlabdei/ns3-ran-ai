/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
*   Copyright (c) 2011 Centre Tecnologic de Telecomunicacions de Catalunya (CTTC)
*   Copyright (c) 2015, NYU WIRELESS, Tandon School of Engineering, New York University
*   Copyright (c) 2016, 2018, University of Padova, Dep. of Information Engineering, SIGNET lab.
*
*   This program is free software; you can redistribute it and/or modify
*   it under the terms of the GNU General Public License version 2 as
*   published by the Free Software Foundation;
*
*   This program is distributed in the hope that it will be useful,
*   but WITHOUT ANY WARRANTY; without even the implied warranty of
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*   GNU General Public License for more details.
*
*   You should have received a copy of the GNU General Public License
*   along with this program; if not, write to the Free Software
*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*
*   Author: Marco Miozzo <marco.miozzo@cttc.es>
*           Nicola Baldo  <nbaldo@cttc.es>
*
*   Modified by: Marco Mezzavilla < mezzavilla@nyu.edu>
*                         Sourjya Dutta <sdutta@nyu.edu>
*                         Russell Ford <russell.ford@nyu.edu>
*                         Menglei Zhang <menglei@nyu.edu>
*
*       Modified by: Tommaso Zugno <tommasozugno@gmail.com>
*								 Integration of Carrier Aggregation
*/


#include <ns3/llc-snap-header.h>
#include <ns3/simulator.h>
#include <ns3/callback.h>
#include <ns3/node.h>
#include <ns3/packet.h>
#include "mmwave-net-device.h"
#include <ns3/packet-burst.h>
#include <ns3/uinteger.h>
#include <ns3/trace-source-accessor.h>
#include <ns3/pointer.h>
#include <ns3/enum.h>
#include <ns3/uinteger.h>
#include "mmwave-enb-net-device.h"
#include "mmwave-ue-net-device.h"
#include <ns3/lte-enb-rrc.h>
#include <ns3/ipv4-l3-protocol.h>
#include <ns3/ipv6-l3-protocol.h>
#include <ns3/abort.h>
#include <ns3/log.h>
#include <ns3/lte-enb-component-carrier-manager.h>
#include <ns3/mmwave-component-carrier-enb.h>
#include <ns3/ran-ai.h>
#include <ns3/mmwave-bearer-stats-calculator.h>
#include <ns3/mmwave-phy-trace.h>
#include <numeric>
#include <ns3/application.h>
#include <ns3/bursty-application.h>
#include <ns3/kitti-trace-burst-generator.h>
#include <ns3/bursty-app-stats-calculator.h>
#include <ns3/eps-bearer-tag.h>
#include <ns3/kitti-header.h>

namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("MmWaveEnbNetDevice");

namespace mmwave {

NS_OBJECT_ENSURE_REGISTERED ( MmWaveEnbNetDevice);

TypeId MmWaveEnbNetDevice::GetTypeId ()
{
  static TypeId
    tid =
    TypeId ("ns3::MmWaveEnbNetDevice")
    .SetParent<MmWaveNetDevice> ()
    .AddConstructor<MmWaveEnbNetDevice> ()
    .AddAttribute ("LteEnbComponentCarrierManager",
                   "The ComponentCarrierManager associated to this EnbNetDevice",
                   PointerValue (),
                   MakePointerAccessor (&MmWaveEnbNetDevice::m_componentCarrierManager),
                   MakePointerChecker <LteEnbComponentCarrierManager> ())
    .AddAttribute ("LteEnbRrc",
                   "The RRC layer associated with the ENB",
                   PointerValue (),
                   MakePointerAccessor (&MmWaveEnbNetDevice::m_rrc),
                   MakePointerChecker <LteEnbRrc> ())
    .AddAttribute ("CellId",
                   "Cell Identifier",
                   UintegerValue (0),
                   MakeUintegerAccessor (&MmWaveEnbNetDevice::m_cellId),
                   MakeUintegerChecker<uint16_t> ())
    .AddAttribute ("StatusUpdate",
                   "Periodicity of the RAN-AI status update",
                   TimeValue (MilliSeconds (100)),
                   MakeTimeAccessor (&MmWaveEnbNetDevice::m_statusUpdate),
                   MakeTimeChecker ())
    .AddAttribute ("IdealActionUpdate",
                   "Whether to automatically notify the action to the user application (true)"
                   "or to send a packet carrying the selected action through the channel",
                   BooleanValue (true),
                   MakeBooleanAccessor (&MmWaveEnbNetDevice::m_idealActionUpdate),
                   MakeBooleanChecker ())
  ;
  return tid;
}

MmWaveEnbNetDevice::MmWaveEnbNetDevice ()
//:m_cellId(0),
// m_Bandwidth (72),
// m_Earfcn(1),
  : m_componentCarrierManager (0),
    m_isConfigured (false)
{
  NS_LOG_FUNCTION (this);
}

MmWaveEnbNetDevice::~MmWaveEnbNetDevice ()
{
  NS_LOG_FUNCTION (this);
}

void
MmWaveEnbNetDevice::DoInitialize (void)
{
  NS_LOG_FUNCTION (this);
  m_isConstructed = true;
  UpdateConfig ();
  for (auto it = m_ccMap.begin (); it != m_ccMap.end (); ++it)
    {
      it->second->Initialize ();
    }
  m_rrc->Initialize ();
  m_componentCarrierManager->Initialize ();
}

void
MmWaveEnbNetDevice::DoDispose ()
{
  NS_LOG_FUNCTION (this);

  m_rrc->Dispose ();
  m_rrc = 0;

  m_componentCarrierManager->Dispose ();
  m_componentCarrierManager = 0;
  // MmWaveComponentCarrierEnb::DoDispose() will call DoDispose
  // of its PHY, MAC, FFR and scheduler instance
  for (uint32_t i = 0; i < m_ccMap.size (); i++)
    {
      m_ccMap.at (i)->Dispose ();
      m_ccMap.at (i) = 0;
    }

  m_ranAiStats.close ();

  MmWaveNetDevice::DoDispose ();
}

Ptr<MmWaveEnbPhy>
MmWaveEnbNetDevice::GetPhy (void) const
{
  NS_LOG_FUNCTION (this);
  return DynamicCast<MmWaveComponentCarrierEnb> (m_ccMap.at (0))->GetPhy ();
}

Ptr<MmWaveEnbPhy>
MmWaveEnbNetDevice::GetPhy (uint8_t index)
{
  return DynamicCast<MmWaveComponentCarrierEnb> (m_ccMap.at (index))->GetPhy ();
}


uint16_t
MmWaveEnbNetDevice::GetCellId () const
{
  NS_LOG_FUNCTION (this);
  return m_cellId;
}

bool
MmWaveEnbNetDevice::HasCellId (uint16_t cellId) const
{
  for (auto &it : m_ccMap)
    {

      if (DynamicCast<MmWaveComponentCarrierEnb> (it.second)->GetCellId () == cellId)
        {
          return true;
        }
    }
  return false;
}

uint8_t
MmWaveEnbNetDevice::GetBandwidth () const
{
  NS_LOG_FUNCTION (this);
  return m_Bandwidth;
}

void
MmWaveEnbNetDevice::SetBandwidth (uint8_t bw)
{
  NS_LOG_FUNCTION (this << bw);
  m_Bandwidth = bw;
}

Ptr<MmWaveEnbMac>
MmWaveEnbNetDevice::GetMac (void)
{
  return DynamicCast<MmWaveComponentCarrierEnb> (m_ccMap.at (0))->GetMac ();
}

Ptr<MmWaveEnbMac>
MmWaveEnbNetDevice::GetMac (uint8_t index)
{
  return DynamicCast<MmWaveComponentCarrierEnb> (m_ccMap.at (index))->GetMac ();
}

void
MmWaveEnbNetDevice::SetRrc (Ptr<LteEnbRrc> rrc)
{
  m_rrc = rrc;
}

Ptr<LteEnbRrc>
MmWaveEnbNetDevice::GetRrc (void)
{
  return m_rrc;
}

bool
MmWaveEnbNetDevice::DoSend (Ptr<Packet> packet, const Address& dest, uint16_t protocolNumber)
{
  NS_LOG_FUNCTION (this << packet   << dest << protocolNumber);
  NS_ABORT_MSG_IF (protocolNumber != Ipv4L3Protocol::PROT_NUMBER
                   && protocolNumber != Ipv6L3Protocol::PROT_NUMBER,
                   "unsupported protocol " << protocolNumber << ", only IPv4/IPv6 is supported");
  return m_rrc->SendData (packet);
}

void
MmWaveEnbNetDevice::UpdateConfig (void)
{
  NS_LOG_FUNCTION (this);

  if (m_isConstructed)
    {
      if (!m_isConfigured)
        {
          NS_LOG_LOGIC (this << " Configure cell " << m_cellId);
          // we have to make sure that this function is called only once
          //m_rrc->ConfigureCell (m_Bandwidth, m_Bandwidth, m_Earfcn, m_Earfcn, m_cellId);
          NS_ASSERT (!m_ccMap.empty ());

          // create the MmWaveComponentCarrierConf map used for the RRC setup
          std::map<uint8_t, LteEnbRrc::MmWaveComponentCarrierConf> ccConfMap;
          for (auto it = m_ccMap.begin (); it != m_ccMap.end (); ++it)
            {
              Ptr<MmWaveComponentCarrierEnb> ccEnb = DynamicCast<MmWaveComponentCarrierEnb> (it->second);
              LteEnbRrc::MmWaveComponentCarrierConf ccConf;
              ccConf.m_ccId = ccEnb->GetConfigurationParameters ()->GetCcId ();
              ccConf.m_cellId = ccEnb->GetCellId ();
              ccConf.m_bandwidth = ccEnb->GetBandwidthInRb ();

              ccConfMap[it->first] = ccConf;
            }

          m_rrc->ConfigureCell (ccConfMap);
          m_isConfigured = true;
        }

      //m_rrc->SetCsgId (m_csgId, m_csgIndication);
    }
  else
    {
      /*
      * Lower layers are not ready yet, so do nothing now and expect
      * ``DoInitialize`` to re-invoke this function.
      */
    }
}

void
MmWaveEnbNetDevice::SetCcMap (std::map< uint8_t, Ptr<MmWaveComponentCarrier> > ccm)
{
  NS_ASSERT_MSG (!m_isConfigured, "attempt to set CC map after configuration");
  m_ccMap = ccm;
}

void
MmWaveEnbNetDevice::InstallRanAI (int memBlockKey, 
                                  Ptr<MmWaveBearerStatsCalculator> rlcStats, 
                                  Ptr<MmWaveBearerStatsCalculator> pdcpStats, 
                                  std::map<uint16_t, Ptr<Application>> imsiApplication,
                                  Ptr<BurstyAppStatsCalculator> appStats)
{
  NS_LOG_DEBUG("Install RAN-AI entity on the eNB");

  // Create an instance of the RAN-AI entity and schedule the periodic status update
  m_ranAI = Create<RanAI>(memBlockKey);
  m_rlcStats = rlcStats;
  m_pdcpStats = pdcpStats;
  m_imsiApp = imsiApplication;
  m_appStats = appStats;

  // Use the bearer status calculator already available, for the collection of metrics at RLC and PDCP
  Simulator::Schedule (m_statusUpdate, &MmWaveEnbNetDevice::SendStatusUpdate, this);
}

void
MmWaveEnbNetDevice::InstallFakeRanAI (Ptr<MmWaveBearerStatsCalculator> rlcStats, 
                                      Ptr<MmWaveBearerStatsCalculator> pdcpStats, 
                                      std::map<uint16_t, Ptr<Application>> imsiApplication, 
                                      Ptr<BurstyAppStatsCalculator> appStats)
{
  NS_LOG_DEBUG("Install FAKE RAN-AI entity on the eNB");

  m_imsiApp = imsiApplication;
  m_rlcStats = rlcStats;
  m_pdcpStats = pdcpStats;
  m_imsiApp = imsiApplication;
  m_appStats = appStats;

  // Use the bearer status calculator already available, for the collection of metrics at RLC and PDCP
  Simulator::Schedule (m_statusUpdate, &MmWaveEnbNetDevice::SendStatusUpdate, this);

  // Create a file to log the stats collected by the fake RAN AI
  m_ranAiStats.open ("RanAiStats.txt", std::ios::out);
  m_ranAiStats << "Time [s]\t" <<
                  "IMSI\t" <<
                  "MCS\t"<<
                  "avg syms\t" <<
                  "avg SINR" <<
                  "RLC txPackets\t" <<
                  "RLC txData\t" <<
                  "RLC rxPackets\t" <<
                  "RLC rxData\t" <<
                  "RLC delayMean\t" <<
                  "RLC delayStdev\t" <<
                  "RLC delayMin\t" <<
                  "RLC delayMax\t" <<
                  "PDCP txPackets\t" <<
                  "PDCP txData\t" <<
                  "PDCP rxPackets\t" <<
                  "PDCP rxData\t" <<
                  "PDCP delayMean\t" <<
                  "PDCP delayStdev\t" <<
                  "PDCP delayMin\t" <<
                  "PDCP delayMax\t" <<
                  "APP txBursts\t" <<
                  "APP txData\t" <<
                  "APP rxBursts\t" <<
                  "APP rxData\t" <<
                  "APP delayMean\t" <<
                  "APP delayStdev\t" <<
                  "APP delayMin\t" <<
                  "APP delayMax\n";
}

void
MmWaveEnbNetDevice::RxPacketTraceEnbCallback (std::string path, RxPacketTraceParams params)
{
  NS_LOG_FUNCTION(this);

  uint64_t imsi = m_rrc->GetImsiFromRnti(params.m_rnti);

  // Find if there is an SINR history associated to this IMSI
  // if not, create one.  If there is one for SINR, there must be also for symbols and MCS, 
  // so there is no need for distinct if-else
  
  auto it = m_sinrHistory.find(imsi);
  if (it != m_sinrHistory.end())
  {
    it->second.push_back (10 * std::log10 (params.m_sinr));
    
    auto it2 = m_symbolsHistory.find (imsi);
    it2->second.push_back (params.m_numSym);
    
    auto it3 = m_mcsHistory.find (imsi);
    it3->second.push_back (params.m_mcs);
  }
  else
  {
    std::vector<double> sinr;
    sinr.push_back (10 * std::log10 (params.m_sinr));
    m_sinrHistory.insert(std::make_pair(imsi, sinr));
    
    std::vector<double> symbols;
    symbols.push_back (params.m_numSym);
    m_symbolsHistory.insert (std::make_pair (imsi, symbols));
    
    std::vector<double> mcs;
    mcs.push_back (params.m_mcs);
    m_mcsHistory.insert (std::make_pair (imsi, mcs));
  }

}

void
MmWaveEnbNetDevice::SendStatusUpdate ()
{
  NS_LOG_DEBUG ("Send update to the RL agent");

  // Retrieve all RLC and PDCP stats collected for this eNB
  std::map<uint16_t, UlDlResults> rlcResults = m_rlcStats->ReadUlResults (m_cellId);
  std::map<uint16_t, UlDlResults> pdcpResults = m_pdcpStats->ReadUlResults (m_cellId);

  // Read also DL results to trigger writing on traces
  m_rlcStats->ReadDlResults (m_cellId);
  m_pdcpStats->ReadDlResults (m_cellId);

  std::map<uint16_t, AppResults> appResults = m_appStats->ReadResults ();

  std::map<double, std::vector<double>> imsiStatsMap;
  
  // Send to the RAN-AI information about **each user**, in order to get the associated action
  for (auto it = rlcResults.begin (); it != rlcResults.end (); it++)
    {
      auto itPdcp = pdcpResults.find(it->first);
      if (itPdcp != pdcpResults.end())
      {
        // Read sinr values collected since last update, evaluate the mean and clear the vector for the following update window 
        auto itSinr = m_sinrHistory.find(it->first);
        if (itSinr == m_sinrHistory.end())
        {
          NS_LOG_WARN ("There isn't an SINR history associated to IMSI " << it->first);
        }
        double sinrMean = std::accumulate (itSinr->second.begin (), itSinr->second.end (), 0.0) / itSinr->second.size ();
        itSinr->second.erase (itSinr->second.begin (), itSinr->second.end ());

        // Read number of symbols used by this user, on average since last update; then, evaluate the mean and clear the vector for the following update window
        auto itSymbols = m_symbolsHistory.find(it->first);
        if (itSymbols == m_symbolsHistory.end ())
          {
            NS_LOG_WARN ("There isn't an history of used symbols associated to IMSI " << it->first);
          }
        
        double symbolsMean = 0;
        if (itSymbols->second.size () > 0)
          {
            symbolsMean = std::accumulate (itSymbols->second.begin (), itSymbols->second.end (), 0.0) / itSymbols->second.size ();
            itSymbols->second.erase (itSymbols->second.begin (), itSymbols->second.end ());
          }

        // Read number of symbols used by this user, on average since last update; then, evaluate the mean and clear the vector for the following update window
        auto itMcs = m_mcsHistory.find(it->first);
        if (itMcs == m_mcsHistory.end ())
          {
            NS_LOG_WARN ("There isn't an history of used MCSs associated to IMSI " << it->first);
          }

        double mcs = 0;
        if (itMcs->second.size () > 0)
          {
            mcs = std::accumulate (itMcs->second.begin (), itMcs->second.end (), 0.0) / itMcs->second.size ();
            itMcs->second.erase (itMcs->second.begin (), itMcs->second.end ());
          }

        // Read stats from the application corresponding to this IMSI
        auto itApp = appResults.find(it->first);
        if (itApp == appResults.end ())
          {
            NS_LOG_WARN ("There isn't any APP information associated to IMSI " << it->first);
          }
        
        // print to check if we are collecting information on the same IMSI at each level
        NS_LOG_DEBUG("IMSI checker " << " " << it->first << " " << itPdcp->first << " " << itSinr->first << " " << itSymbols->first << " " << itApp->second.imsi);

        std::vector<double> stats = {
            mcs,
            symbolsMean,
            sinrMean,
            (double) it->second.txPackets,
            (double) it->second.txData,
            (double) it->second.rxPackets,
            (double) it->second.rxData,
            it->second.delayMean,
            it->second.delayStdev,
            it->second.delayMin,
            it->second.delayMax,
            (double) itPdcp->second.txPackets,
            (double) itPdcp->second.txData,
            (double) itPdcp->second.rxPackets,
            (double) itPdcp->second.rxData,
            itPdcp->second.delayMean,
            itPdcp->second.delayStdev,
            itPdcp->second.delayMin,
            itPdcp->second.delayMax,
            (double) itApp->second.txBursts,
            (double) itApp->second.txData,
            (double) itApp->second.rxBursts,
            (double) itApp->second.rxData,
            itApp->second.delayMean,
            itApp->second.delayStdev,
            itApp->second.delayMin,
            itApp->second.delayMax,
        };

        imsiStatsMap.insert(std::make_pair(it->first, stats));
      }
      else
      {
        NS_LOG_WARN ("There should be a PDCP trace for this IMSI, please check.");
      }
    }
  
  if (m_ranAI)
  {// This is executed if a real RAN AI entity is instantiated
    
    // Report measure window and get the associated actions
    std::map<uint16_t, uint16_t> actions = m_ranAI->ReportMeasures (imsiStatsMap);  
  
    // propagate actions to all UEs
    for (const auto& i: actions)
    {
      auto it = m_lastAction.find(i.first);
      bool update = true;

      if (it != m_lastAction.end())
      {
        // there was something stored about *rnti*, check if new action is same of the old one or not
        if (it->second == i.second)
        {
          // old one and new one are the same, do not send message to the user
          update = false;
        }
        else
        {
          // update the entry and send the update to the user
          it->second = i.second;
        }
      }
      else
      {
        // nothing stored about this user, communicate the action
        m_lastAction [i.first] = i.second;
      }

      if (update)
      {
        if (m_idealActionUpdate)
        {
          NotifyActionIdeal (i.first, i.second);
        }
        else
        {
          NotifyActionReal (i.first, i.second);
        }
      }
    }
  }
  else
  { // This is executed when NO RAN AI entity is instantiated
    // This method is used to collect metrics without a real interaction with 
    // the RAN AI. In this case, no action is taken.
    PrintRanAiStatsToFile (imsiStatsMap);
  }

  // Schedule next status update
  Simulator::Schedule (m_statusUpdate, &MmWaveEnbNetDevice::SendStatusUpdate, this);
}

void
MmWaveEnbNetDevice::NotifyActionIdeal (uint16_t imsi, uint16_t action)
{
  NS_LOG_FUNCTION(this);
  // Retrieve pointer to application associated to IMSI
  auto app = m_imsiApp.find (imsi);
  if (app != m_imsiApp.end ())
    {
      Ptr<BurstyApplication> bursty = (app->second)->GetObject<BurstyApplication> ();

      // Propagate the action to the application associated to this IMSI
      Ptr<KittiTraceBurstGenerator> burstGenerator = DynamicCast<KittiTraceBurstGenerator> (
          DynamicCast<BurstyApplication> (app->second)->GetBurstGenerator ());
      NS_LOG_DEBUG ("Action is set to " << action << " for IMSI "
                                        << imsi);
      burstGenerator->SetModel (action);
    }
  else
    {
      NS_LOG_UNCOND ("Cannot find an application associated to IMSI " << imsi);
    }
}

void
MmWaveEnbNetDevice::NotifyActionReal (uint16_t imsi, uint16_t action)
{
  NS_LOG_FUNCTION (this);
  uint16_t rnti = m_rrc->GetRntiFromImsi (imsi);

  Ptr<Packet> pkt =
      Create<Packet> (40); // TODO: check what is the minimum packet size for the kitti header
  KittiHeader kitti;

  kitti.SetAction (action);
  kitti.SetImsi (imsi);
  kitti.SetRnti (rnti);
  pkt->AddHeader (kitti);
  EpsBearerTag tag = EpsBearerTag (rnti, 1);
  pkt->AddPacketTag (tag);

  NS_LOG_DEBUG (Simulator::Now () << " " << pkt->GetUid () << " " << pkt->GetSize () << " RNTI "
                                  << rnti << " action " << action);
  DoSend (pkt, Address (), Ipv4L3Protocol::PROT_NUMBER);
}

void
MmWaveEnbNetDevice::PrintRanAiStatsToFile (std::map<double, std::vector<double>> imsiStatsMap)
{
  for (const auto& kv : imsiStatsMap)
  {
    m_ranAiStats << Simulator::Now ().GetSeconds () << "\t" << 
                    +kv.first;
    for (const auto& i : kv.second)
    {
      m_ranAiStats  << "\t" << +i;    
    }
    m_ranAiStats << "\n";
  }
}

}
}
