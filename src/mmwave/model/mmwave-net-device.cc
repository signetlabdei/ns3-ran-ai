/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
*   Copyright (c) 2011 Centre Tecnologic de Telecomunicacions de Catalunya (CTTC)
*   Copyright (c) 2015, NYU WIRELESS, Tandon School of Engineering, New York University
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
*/



#include <ns3/simulator.h>
#include <ns3/callback.h>
#include <ns3/node.h>
#include <ns3/packet.h>
#include <ns3/log.h>
#include "ns3/ipv4-header.h"
#include <ns3/ipv4-l3-protocol.h>
#include "ns3/ipv6-header.h"
#include <ns3/ipv6-l3-protocol.h>
#include "mmwave-net-device.h"
#include "ns3/uinteger.h"
#include "ns3/mmwave-component-carrier.h"
#include <ns3/object-map.h>
#include <ns3/kitti-header.h>
#include <ns3/kitti-trace-burst-generator.h>
#include <ns3/bursty-application.h>

namespace ns3 {

namespace mmwave {

NS_LOG_COMPONENT_DEFINE ("MmWaveNetDevice");

NS_OBJECT_ENSURE_REGISTERED (MmWaveNetDevice);

TypeId MmWaveNetDevice::GetTypeId ()
{
  static TypeId
    tid =
    TypeId ("ns3::MmWaveNetDevice")
    .SetParent<NetDevice> ()
    .AddAttribute ("Mtu", "The MAC-level Maximum Transmission Unit",
                   UintegerValue (30000),
                   MakeUintegerAccessor (&MmWaveNetDevice::SetMtu,
                                         &MmWaveNetDevice::GetMtu),
                   MakeUintegerChecker<uint16_t> ())
    .AddAttribute ("AntennaNum",
                   "Number of antenna elements for the device",
                   UintegerValue (64),
                   MakeUintegerAccessor (&MmWaveNetDevice::SetAntennaNum,
                                         &MmWaveNetDevice::GetAntennaNum),
                   MakeUintegerChecker<uint16_t> ())
    .AddAttribute ("ComponentCarrierMap",
                   "List of component carriers",
                   ObjectMapValue (),
                   MakeObjectMapAccessor (&MmWaveNetDevice::m_ccMap),
                   MakeObjectMapChecker<MmWaveComponentCarrier> ())
  ;

  return tid;
}

MmWaveNetDevice::MmWaveNetDevice (void)
  : m_isConstructed (false)
{
  NS_LOG_FUNCTION (this);
}


MmWaveNetDevice::~MmWaveNetDevice (void)
{
  NS_LOG_FUNCTION (this);
}

void
MmWaveNetDevice::DoDispose (void)
{
  m_node = 0;
  NetDevice::DoDispose ();
}

void
MmWaveNetDevice::SetIfIndex (const uint32_t index)
{
  m_ifIndex = index;
}
uint32_t
MmWaveNetDevice::GetIfIndex (void) const
{
  return m_ifIndex;
}
Ptr<Channel>
MmWaveNetDevice::GetChannel (void) const
{
  return 0;
}
void
MmWaveNetDevice::SetAddress (Address address)
{
  NS_LOG_FUNCTION (this << address);
  m_macaddress = Mac64Address::ConvertFrom (address);
}
Address
MmWaveNetDevice::GetAddress (void) const
{
  NS_LOG_FUNCTION (this);
  return m_macaddress;
}
bool
MmWaveNetDevice::SetMtu (const uint16_t mtu)
{
  m_mtu = mtu;
  return true;
}
uint16_t
MmWaveNetDevice::GetMtu (void) const
{
  return m_mtu;
}
bool
MmWaveNetDevice::IsLinkUp (void) const
{
  return m_linkUp;
}
void
MmWaveNetDevice::AddLinkChangeCallback (Callback<void> callback)
{

}
bool
MmWaveNetDevice::IsBroadcast (void) const
{
  return false;
}
Address
MmWaveNetDevice::GetBroadcast (void) const
{
  return Mac48Address::GetBroadcast ();
}
bool
MmWaveNetDevice::IsMulticast (void) const
{
  return false;
}
Address
MmWaveNetDevice::GetMulticast (Ipv4Address multicastGroup) const
{
  return Mac48Address ("01:00:5e:00:00:00");
}
bool
MmWaveNetDevice::IsBridge (void) const
{
  return false;
}
bool
MmWaveNetDevice::IsPointToPoint (void) const
{
  return false;
}

bool
MmWaveNetDevice::SendFrom (Ptr<Packet> packet, const Address& source, const Address& dest, uint16_t protocolNumber)
{
  NS_FATAL_ERROR ("Send from not supported");
  return false;
}

Ptr<Node>
MmWaveNetDevice::GetNode (void) const
{
  return m_node;
}

void
MmWaveNetDevice::SetNode (Ptr<Node> node)
{
  m_node = node;
}

bool
MmWaveNetDevice::NeedsArp (void) const
{
  return false;
}

Address
MmWaveNetDevice::GetMulticast (Ipv6Address addr) const
{
  Address dummy;
  return dummy;
}

void
MmWaveNetDevice::SetReceiveCallback (ReceiveCallback cb)
{
  NS_LOG_FUNCTION (this);
  m_rxCallback = cb;
}

void
MmWaveNetDevice::SetPromiscReceiveCallback (PromiscReceiveCallback cb)
{

}

bool
MmWaveNetDevice::SupportsSendFrom (void) const
{
  return false;
}

void
MmWaveNetDevice::Receive (Ptr<Packet> p)
{
  NS_LOG_FUNCTION (this << p);
  Ipv4Header ipv4Header;
  Ipv6Header ipv6Header;
  KittiHeader kittiHdr; 

  if (p->PeekHeader (ipv4Header) != 0)
    {
      NS_LOG_LOGIC ("IPv4 stack...");
      m_rxCallback (this, p, Ipv4L3Protocol::PROT_NUMBER, Address ());      
      
    }
  else if  (p->PeekHeader (ipv6Header) != 0)
    {
      NS_LOG_LOGIC ("IPv6 stack...");
      m_rxCallback (this, p, Ipv6L3Protocol::PROT_NUMBER, Address ());
    }
  else if (p->PeekHeader (kittiHdr) != 0)
    {
      NS_LOG_UNCOND ("Kitti Header retrieved on node with " << m_node->GetNApplications () << " apps");
      p->RemoveHeader(kittiHdr);

      // Check among all applications installed in this node if there is the application, compatible
      // with the KittiHeader; if it is not found, then there could an error, so the simulation is aborted.
      bool foundKittApp = false;
      for (uint32_t i = 0; i < m_node->GetNApplications (); i++)
      {
        if (DynamicCast<BurstyApplication> (m_node->GetApplication (i)) != NULL)
        {
          Ptr<KittiTraceBurstGenerator> burstGenerator = DynamicCast<KittiTraceBurstGenerator> (
              DynamicCast<BurstyApplication> (m_node->GetApplication (i))->GetBurstGenerator ());
          NS_LOG_UNCOND ("Action " << kittiHdr.GetAction() << " is set for NodeID " << m_node->GetId () << " IMSI " << kittiHdr.GetImsi() << " RNTI " << kittiHdr.GetRnti ());
          burstGenerator->SetModel (kittiHdr.GetAction ());
          foundKittApp = true;
          break;
        }
      }
      NS_ABORT_MSG_IF(!foundKittApp, "Not found Kitti Application, packet sent to wrong user or something is broken.");
    }
  else
    {
      NS_ABORT_MSG ("MmWaveNetDevice::Receive - Unknown IP type...");
    }
}

bool
MmWaveNetDevice::Send (Ptr<Packet> packet, const Address& dest, uint16_t protocolNumber)
{
  bool ret = DoSend ( packet, dest, protocolNumber);
  return ret;
}

Ipv4Address
MmWaveNetDevice::GetPacketDestination (Ptr<Packet> packet)
{
  Ipv4Address dest_ip;
  Ptr<Packet> q = packet->Copy ();

  Ipv4Header ipHeader;
  q->PeekHeader (ipHeader);
  dest_ip = ipHeader.GetDestination ();
  return dest_ip;
}

uint16_t
MmWaveNetDevice::GetEarfcn () const
{
  NS_LOG_FUNCTION (this);
  return m_earfcn;
}

void
MmWaveNetDevice::SetEarfcn (uint16_t earfcn)
{
  NS_LOG_FUNCTION (this << earfcn);
  m_earfcn = earfcn;
}

uint16_t
MmWaveNetDevice::GetAntennaNum () const
{
  NS_LOG_FUNCTION (this);
  return m_antennaNum;
}

void
MmWaveNetDevice::SetAntennaNum (uint16_t antennaNum)
{
  NS_LOG_FUNCTION (this << antennaNum);
  NS_ASSERT_MSG (std::floor (std::sqrt(antennaNum)) == std::sqrt(antennaNum), "Only square antenna arrays are currently supported.");
  m_antennaNum = antennaNum;
}

std::map <uint8_t, Ptr<MmWaveComponentCarrier> >
MmWaveNetDevice::GetCcMap () const
{
  NS_LOG_FUNCTION (this);
  return m_ccMap;
}

void
MmWaveNetDevice::SetCcMap (std::map<uint8_t, Ptr<MmWaveComponentCarrier> > ccm)
{
  NS_LOG_FUNCTION (this);
  m_ccMap = ccm;
}

Ptr<ThreeGppAntennaArrayModel>
MmWaveNetDevice::GetAntenna (uint8_t ccId) const
{
  NS_LOG_FUNCTION (this << +ccId);
  return m_ccMap.at (ccId)->GetAntenna ();
}


}

}
