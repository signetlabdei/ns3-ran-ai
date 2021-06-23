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

#include "algorithm"    
#include "ns3/log.h"
#include "ns3/object.h"
#include "ns3/double.h"
#include "ns3/string.h"
#include "gemv-propagation-loss-model.h"
#include "ns3/simulator.h"
#include "ns3/csv-reader.h"
#include "ns3/nstime.h"
#include "ns3/boolean.h"
#include "ns3/node.h"
#include "ns3/gemv-tag.h"
#include "ns3/mobility-module.h"
#include "ns3/matrix-based-channel-model.h"

namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("GemvPropagationLossModel");

NS_OBJECT_ENSURE_REGISTERED (GemvPropagationLossModel);

TypeId
GemvPropagationLossModel::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::GemvPropagationLossModel")
    .SetParent<PropagationLossModel> ()
    .SetGroupName ("Propagation")
    .AddConstructor<GemvPropagationLossModel> ()
    .AddAttribute ("TimeResolution", "The time resolution in seconds.",
                   TimeValue (Seconds(1.0)),
                   MakeTimeAccessor (&GemvPropagationLossModel::SetTimeResolution,
                                       &GemvPropagationLossModel::GetTimeResolution),
                   MakeTimeChecker ())
    .AddAttribute ("InputPath", "path to the folder containing the input traces",
                   StringValue ("./"),
                   MakeStringAccessor (&GemvPropagationLossModel::SetPath,
                                       &GemvPropagationLossModel::GetPath),
                   MakeStringChecker ())
    .AddAttribute ("IncludeSmallScale", "flag to determine if we should add small scale variations to the rx power",
                   BooleanValue (true),
                   MakeBooleanAccessor (&GemvPropagationLossModel::m_smallScaleEnabled),
                   MakeBooleanChecker ())
  ;
  return tid;
}

GemvPropagationLossModel::GemvPropagationLossModel ()
  : PropagationLossModel ()
{
  NS_LOG_FUNCTION (this);
}

GemvPropagationLossModel::~GemvPropagationLossModel ()
{
  NS_LOG_FUNCTION (this);
}

std::vector<uint16_t>
GemvPropagationLossModel::GetDistinctIds (bool checkRsu)
{
  std::string fileName {m_path+"commPairs_V2I.csv"};
  CsvReader csv (fileName, ',');
  uint16_t rsu {};
  uint16_t ue {};

  std::vector<uint16_t> distinctId;
  while (csv.FetchNextRow ())
    {
      // Ignore blank lines
      if (csv.IsBlankRow ())
        continue;
      
      // Expecting two values
      bool ok = csv.GetValue (0, rsu);
      ok |= csv.GetValue (1, ue);
      NS_ABORT_MSG_IF (!ok, "Something went wrong while parsing the file: " << fileName);

      if (checkRsu)
        distinctId.push_back(rsu);
      else
        distinctId.push_back(ue);

    } // while FetchNextRow
  
  // eliminate duplicate ids from the list
  sort(distinctId.begin(), distinctId.end());
  distinctId.erase( unique( distinctId.begin(), distinctId.end() ), distinctId.end() );

  return distinctId;
}

std::pair<uint32_t, uint32_t>
GemvPropagationLossModel::ReadTimestep (uint32_t index, std::string commType) const
{
  uint32_t shift = 1; // CsvReader count rows starting from 1
  uint32_t numCommPairs = 0;

  std::string fileName{m_path + "numCommPairsPerTimestep_" + commType + ".csv"};
  CsvReader csv (fileName, '\n');
  std::string varValue {};

  while (csv.FetchNextRow ())
    {
      // Ignore blank lines
      if (csv.IsBlankRow ())
        {
          continue;
        }

      // Expecting one value
      bool ok = csv.GetValue (0, varValue);
      NS_ABORT_MSG_IF (!ok, "Something went wrong while parsing the file: " << fileName);

      numCommPairs = atoi (varValue.c_str ());

      if (csv.RowNumber() == index)
        break;

      shift += numCommPairs;

    } // while FetchNextRow

  return std::make_pair(shift, shift+numCommPairs-1);
}

int32_t
GemvPropagationLossModel::ReadCommPairs (uint32_t start, uint32_t end, uint16_t nodeOne, uint16_t nodeTwo, std::string commType) const
{
  std::string fileName{m_path + "commPairs_" + commType + ".csv"};
  CsvReader csv (fileName, ',');
  uint16_t readOne {};
  uint16_t readTwo {};

  while (csv.FetchNextRow ())
    {
      // Ignore blank lines
      if (csv.IsBlankRow ())
        continue;

      if (csv.RowNumber() < start)
        continue;
      
      if (csv.RowNumber() > end)
        break;
      
      // Expecting two values
      bool ok = csv.GetValue (0, readOne);
      ok |= csv.GetValue (1, readTwo);
      NS_ABORT_MSG_IF (!ok, "Something went wrong while parsing the file: " << fileName);

      if (nodeOne == readOne && nodeTwo == readTwo)
        return csv.RowNumber();

    } // while FetchNextRow
  return -1;
}

int32_t
GemvPropagationLossModel::GetIndex (uint16_t nodeOne, uint16_t nodeTwo, std::string commType) const
{
  // The following snippet of code works both for V2I and V2V.
  // In case of V2I pair, nodeOne will always correspond to the RSU/eNB
  
  uint32_t timestep = GetTimestep ();
  
  std::pair<uint32_t, uint32_t> interval = ReadTimestep (timestep, commType);
  
  int32_t index = ReadCommPairs (interval.first, interval.second, nodeOne, nodeTwo, commType);

  return index;
}

double
GemvPropagationLossModel::ReadRxPower (uint32_t index, std::string fileName) const
{
  CsvReader csv (fileName, ',');
  
  double pwr {};

  while (csv.FetchNextRow ())
    {
      // Ignore blank lines
      if (csv.IsBlankRow ())
        continue;

      if (csv.RowNumber() == index)
      {
        // Expecting one values
        bool ok = csv.GetValue (0, pwr); 
        if (!ok)
        {
          // maybe it is an Inf value
          std::string sValue {};
          csv.GetValue (0, sValue);
          if (sValue == "Inf")
          {
            pwr = -std::numeric_limits<double>::infinity();
            ok = true;
          }
          else
          {
            ok = false;
          }
          NS_ABORT_MSG_IF (!ok, "Something went wrong while parsing the file: " << fileName
          << " at line " << +index);
        }
        return pwr;
      }
    } // while FetchNextRow
  return -1;
}

uint8_t
GemvPropagationLossModel::ReadPairLosCondition (Ptr<MobilityModel> a,
                                                Ptr<MobilityModel> b) const
{
  // extract tag ID from the nodes and check their type before
  // reading the received power from the GEMV traces

  Ptr<GemvTag> tagA = a->GetObject<Node> ()->GetObject<GemvTag> ();
  Ptr<GemvTag> tagB = b->GetObject<Node> ()->GetObject<GemvTag> ();

  uint16_t nodeOne{};
  uint16_t nodeTwo{};
  std::string commType{};

  NS_ABORT_MSG_IF (tagA->IsNodeRsu () && tagB->IsNodeRsu (),
                   "Communication between RSU is not supported.");

  if (!tagA->IsNodeRsu () && !tagB->IsNodeRsu ())
    {
      NS_LOG_DEBUG ("Both nodes are vehicles.");
      commType = "V2V";
      nodeOne = tagA->GetTagId ();
      nodeTwo = tagB->GetTagId ();
    }
  else
    {
      NS_LOG_DEBUG ("One of the two nodes is an RSU.");
      commType = "V2I";
      if (tagA->IsNodeRsu ())
        {
          nodeOne = tagA->GetTagId ();
          nodeTwo = tagB->GetTagId ();
        }
      else
        {
          nodeTwo = tagA->GetTagId ();
          nodeOne = tagB->GetTagId ();
        }
    }

  int32_t index = GetIndex (nodeOne, nodeTwo, commType);

  if (index != -1)
  {
    CsvReader csv (m_path+"commPairType_" + commType + ".csv", ',');

    uint8_t losCondition {};

    while (csv.FetchNextRow ())
      {
        // Ignore blank lines
        if (csv.IsBlankRow ())
          continue;

        if (csv.RowNumber () == (uint32_t)index)
          {
            // Expecting one values
            bool ok = csv.GetValue (0, losCondition);
            NS_ABORT_MSG_IF (!ok, "Something went wrong while parsing the file");
            return losCondition;
          }
      } // while FetchNextRow
  } 
  return 0; // corresponding to an invalid LOS condition (this pair is not in the traces)
}

bool 
GemvPropagationLossModel::NeedsUpdate (uint32_t key) const
{
  bool update = true;
  auto it = m_gainMap.find (key);
  if (it != m_gainMap.end ())
  {
    update = (it->second.first != GetTimestep ());
  }
  NS_LOG_DEBUG ("gain with key " << key << 
                " was generated at ts " << it->second.first <<
                " ,current ts " << GetTimestep () << 
                " ,update= " << update);
  return update;
}

uint32_t
GemvPropagationLossModel::GetTimestep () const
{
  // Row number to check (CsvReader counts rows starting from 1, while timestep takes values in [0,inf])
  uint32_t timestep = std::floor ((Simulator::Now () / m_timeResolution).GetDouble ()) + 1;
  return timestep;
}

double
GemvPropagationLossModel::DoCalcRxPower (double txPowerDbm,
                                             Ptr<MobilityModel> a,
                                             Ptr<MobilityModel> b) const
{
  NS_LOG_FUNCTION (this << Simulator::Now());
  
  // extract tag ID from the nodes and check their type before
  // reading the received power from the GEMV traces
  
  Ptr<GemvTag> tagA = a->GetObject<Node> ()->GetObject<GemvTag> ();
  Ptr<GemvTag> tagB = b->GetObject<Node> ()->GetObject<GemvTag> ();

  uint16_t nodeOne {}; // in case of V2I link, this is the RSU
  uint16_t nodeTwo {}; // in case of V2I link, this is the vehicle
  std::string commType {};
  
  NS_ABORT_MSG_IF (tagA->IsNodeRsu () && tagB->IsNodeRsu (), "Communication between RSU is not supported.");

  if (!tagA->IsNodeRsu() && !tagB->IsNodeRsu())
  {
    NS_LOG_DEBUG("Both nodes are vehicles.");
    commType = "V2V";
    nodeOne = tagA->GetTagId ();
    nodeTwo = tagB->GetTagId ();
  }
  else
  {
    NS_LOG_DEBUG ("One of the two nodes is an RSU.");
    commType = "V2I";
    if (tagA->IsNodeRsu())
    {
      nodeOne = tagA->GetTagId();
      nodeTwo = tagB->GetTagId();
    }
    else
    {
      nodeTwo = tagA->GetTagId();
      nodeOne = tagB->GetTagId(); 
    }
  }

  // Compute the key which identifies the node pair. The key is simmetric, 
  // so that there is a single entry per node pair.
  uint32_t key = MatrixBasedChannelModel::GetKey (nodeOne, nodeTwo);
  
  // Check if the entry in the map associated with this key needs to be 
  // updated or if it is not present.
  bool update = NeedsUpdate (key);

  double gain {};
  
  if (update)
  {
    NS_LOG_DEBUG ("Update gain with key " << key);
    int32_t index = GetIndex (nodeOne, nodeTwo, commType);
    
    // In case the index is -1, there is not a correspondence for (nodeOne, nodeTwo) in the traces.
    // As a consequence, we return a -inf gain, representing the nodes not communicating.
    if (index != -1)
    {
      std::string fileName{m_path + "largeScalePwr_" + commType + ".csv"};
      gain += ReadRxPower (index, fileName); // get pathloss
      
      if (m_smallScaleEnabled)
      {
        fileName = m_path + "smallScaleVar_" + commType + ".csv";
        gain += ReadRxPower (index, fileName); // get small scale variations
      }
      
    }
    else
    {
      gain = -std::numeric_limits<double>::infinity();
    }

    // store the gain value in the m_gainMap
    GainItem item = std::make_pair (GetTimestep (), gain);
    m_gainMap [key] = item;
  }
  else
  {
    NS_LOG_DEBUG ("key " << key << " uses the old gain value");
    gain = m_gainMap.at (key).second;
  }
  NS_LOG_DEBUG("Gain:" << gain << " dBm");

  return txPowerDbm + gain;
}

Time
GemvPropagationLossModel::GetMaxSimulationTime () const
{
  std::string fileName {m_path + "numCommPairsPerTimestep_V2V.csv"};
  CsvReader csv (fileName, '\n');
  uint64_t index = 0;
  while (csv.FetchNextRow ())
    {
      // Ignore blank lines
      if (csv.IsBlankRow ())
        {
          continue;
        }
      ++index;
    } // while FetchNextRow
  return index * m_timeResolution;
}

void
GemvPropagationLossModel::SetTimeResolution (Time t)
{
  m_timeResolution = t;
}

Time
GemvPropagationLossModel::GetTimeResolution (void) const
{
  return m_timeResolution;
}

void
GemvPropagationLossModel::SetPath (std::string path)
{
  m_path = path;
}

std::string
GemvPropagationLossModel::GetPath (void) const
{
  return m_path;
}

int64_t 
GemvPropagationLossModel::DoAssignStreams (int64_t stream)
{
  return 0;
}

} // namespace ns3
