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

#ifndef KITTI_HEADER_H
#define KITTI_HEADER_H

#include "ns3/header.h"
#include "ns3/nstime.h"

namespace ns3 {
/**
 * \ingroup applications
 *
 **/

class KittiHeader : public Header
{
public:
  KittiHeader ();

  /**
   * \brief Get the type ID.
   * \return the object TypeId
   */
  static TypeId GetTypeId (void);

  virtual TypeId GetInstanceTypeId (void) const;
  virtual void Print (std::ostream &os) const;
  virtual uint32_t GetSerializedSize (void) const;
  virtual void Serialize (Buffer::Iterator start) const;
  virtual uint32_t Deserialize (Buffer::Iterator start);

  /**
   * Get the action carried by this header 
   * Supported values: 0, 1, 2, 1150, 1450, 1451, 1452
   * \return the action
   */
  uint32_t GetAction (void) const;
  
  /**
   * Set the action to be carried by this header
   * \param action the action to insert into this header
   */
  void SetAction(uint32_t action);

  /**
   * Get the IMSI carried by this header, representing the target vehicle/UE 
   * \return the imsi
   */
  uint16_t GetImsi (void) const;

  /**
   * Set the IMSI to be carried by this header
   * \param imsi the imsi to insert into this header
   */
  void SetImsi (uint16_t imsi);

  /**
   * Get the RNTI carried by this header, representing the target vehicle/UE 
   * \return the rnti
   */
  uint16_t GetRnti (void) const;

  /**
   * Set the RNTI to be carried by this header
   * \param rnti the rnti to insert into this header
   */
  void SetRnti (uint16_t rnti);

private:
  uint32_t m_action;
  uint16_t m_imsi;
  uint16_t m_rnti;

};

} // namespace ns3

#endif /* KITTI_HEADER_H */
