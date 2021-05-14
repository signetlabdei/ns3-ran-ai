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

#ifndef GEMV_TAG_H
#define GEMV_TAG_H

#include "ns3/object.h"

namespace ns3 {

/**
 * \brief Tag to be aggregated to the node in order to be aligned to the traces parsed from GEMV module
 * 
 */
class GemvTag : public Object
{
public:
  /**
   * Get the type ID.
   * \brief Get the type ID.
   * \return the object TypeId
   */
  static TypeId GetTypeId (void);

  /**
   * Constructor
   */
  GemvTag ();

  /**
   * Destructor
   */
  virtual ~GemvTag ();

  /**
   * Set the tag ID
   *
   * \param id identification number associated to vehicle/RSU
   */
  void SetTagId(uint16_t id);
  
  /**
   * Get the tag ID
   *
   * \return node identification tag
   */
  uint16_t GetTagId(void) const;

  /**
   * Set the node type
   *
   * \param isRsu node type, i.e., true if RSU, false otherwise
   */
  void SetNodeType (bool isRsu);

  /**
   * Determine if a node is an RSU
   *
   * \return true if the node represent an RSU, false otherwise
   */
  bool IsNodeRsu (void) const;

  uint16_t m_tagId;  //!< node identification number
  bool m_isRsu;     //!< boolean flag representing node type

};

} // namespace ns3

#endif /* GEMV_TAG_H */
