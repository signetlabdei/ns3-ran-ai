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

#include "gemv-tag.h"

namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("GemvTag");

NS_OBJECT_ENSURE_REGISTERED (GemvTag);

TypeId
GemvTag::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::GemvTag")
    .SetParent<Object> ()
    .AddConstructor<GemvTag> ()
  ;
  return tid;
}

GemvTag::GemvTag ()
{
  NS_LOG_FUNCTION (this);
}

GemvTag::~GemvTag ()
{
  NS_LOG_FUNCTION (this);
}

void
GemvTag::SetTagId (uint16_t id)
{
  m_tagId = id;
}

uint16_t
GemvTag::GetTagId (void) const
{
  return m_tagId;
}

void
GemvTag::SetNodeType (bool isRsu)
{
  m_isRsu = isRsu;
}

bool
GemvTag::IsNodeRsu (void) const
{
  return m_isRsu;
}


} // namespace ns3
