/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
//
// Copyright (c) 2021 SIGNET Lab, Department of Information Engineering,
// University of Padova
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License version 2 as
// published by the Free Software Foundation;
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include "ns3/assert.h"
#include "ns3/log.h"
#include "ns3/header.h"
#include "ns3/simulator.h"
#include "kitti-header.h"

namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("KittiHeader");

NS_OBJECT_ENSURE_REGISTERED (KittiHeader);

KittiHeader::KittiHeader ()
{
  NS_LOG_FUNCTION (this);
  m_action = 0;
}

TypeId
KittiHeader::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::KittiHeader")
    .SetParent<Header> ()
    .SetGroupName("Applications")
    .AddConstructor<KittiHeader> ()
  ;
  return tid;
}
TypeId
KittiHeader::GetInstanceTypeId (void) const
{
  return GetTypeId ();
}
void
KittiHeader::Print (std::ostream &os) const
{
  NS_LOG_FUNCTION (this << &os);
}

uint32_t
KittiHeader::GetSerializedSize (void) const
{
  NS_LOG_FUNCTION (this);
  return 8;
}

void
KittiHeader::Serialize (Buffer::Iterator start) const
{
  NS_LOG_FUNCTION (this << &start);
  Buffer::Iterator i = start;
  i.WriteHtonU32 (m_action);
  i.WriteHtonU16 (m_imsi);
  i.WriteHtonU16 (m_rnti);
}
uint32_t
KittiHeader::Deserialize (Buffer::Iterator start)
{
  NS_LOG_FUNCTION (this << &start);
  Buffer::Iterator i = start;
  m_action = i.ReadNtohU32 ();
  m_imsi = i.ReadNtohU16 ();
  m_rnti = i.ReadNtohU16 ();
  return GetSerializedSize ();
}

void
KittiHeader::SetAction (uint32_t action)
{
  NS_LOG_FUNCTION (this);
  m_action = action;
}

uint32_t
KittiHeader::GetAction (void) const
{
  NS_LOG_FUNCTION (this);
  return m_action;
}

void
KittiHeader::SetImsi (uint16_t imsi)
{
  NS_LOG_FUNCTION (this);
  m_imsi = imsi;
}

uint16_t
KittiHeader::GetImsi (void) const
{
  NS_LOG_FUNCTION (this);
  return m_imsi;
}

void
KittiHeader::SetRnti (uint16_t rnti)
{
  NS_LOG_FUNCTION (this);
  m_rnti = rnti;
}

uint16_t
KittiHeader::GetRnti (void) const
{
  NS_LOG_FUNCTION (this);
  return m_rnti;
}

} // namespace ns3
