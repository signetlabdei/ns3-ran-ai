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

#include "ns3/log.h"
#include "ns3/object.h"
#include "ns3/double.h"
#include "ns3/string.h"
#include "gemv-propagation-loss-model.h"
#include "ns3/simulator.h"
#include "ns3/csv-reader.h"
#include "ns3/nstime.h"
#include "ns3/boolean.h"

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

std::pair<uint32_t, uint32_t>
GemvPropagationLossModel::ReadTimestep (uint32_t index) const
{
  uint32_t shift = 1; // CsvReader count rows starting from 1
  uint32_t numCommPairs = 0;

  std::string fileName {m_path+"numCommPairsPerTimestep_V2I.csv"};
  CsvReader csv (fileName, '\n');
  std::string varValue;

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
GemvPropagationLossModel::ReadCommPairs (uint32_t start, uint32_t end, uint32_t targetRsu, uint32_t targetUe) const
{
  std::string fileName {m_path+"commPairs_V2I.csv"};
  CsvReader csv (fileName, ',');
  uint32_t rsu;
  uint32_t ue;

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
      bool ok = csv.GetValue (0, rsu);
      ok |= csv.GetValue (1, ue);
      NS_ABORT_MSG_IF (!ok, "Something went wrong while parsing the file: " << fileName);

      NS_LOG_DEBUG ("targetRsu " << targetRsu << " targetUe " << targetUe << "rsu " << rsu << " ue " << ue );

      if (targetRsu == rsu and targetUe == ue)
        return csv.RowNumber();

    } // while FetchNextRow
  return -1;
}

double
GemvPropagationLossModel::ReadRxPower (uint32_t index, std::string fileName) const
{
  CsvReader csv (fileName, ',');
  
  double pwr;

  while (csv.FetchNextRow ())
    {
      // Ignore blank lines
      if (csv.IsBlankRow ())
        continue;

      if (csv.RowNumber() == index)
      {
        // Expecting one values
        bool ok = csv.GetValue (0, pwr); 
        NS_ABORT_MSG_IF (!ok, "Something went wrong while parsing the file: " << fileName);
        return pwr;
      }
    } // while FetchNextRow
  return -1;
}

double
GemvPropagationLossModel::DoCalcRxPower (double txPowerDbm,
                                             Ptr<MobilityModel> a,
                                             Ptr<MobilityModel> b) const
{
  NS_LOG_FUNCTION (this << Simulator::Now());
  
  // TODO: get RSU and UE IDs from nodes associated to the mobility models
  uint32_t rsu = 3;
  uint32_t ue = 13;
  uint32_t timestep = std::floor( (Simulator::Now() / m_timeResolution).GetDouble()) + 1; // row number to check (CsvReader counts rows starting from 1, while timestep takes values in [0,inf])

  std::pair<uint32_t, uint32_t> interval = ReadTimestep(timestep);

  int32_t index = ReadCommPairs(interval.first, interval.second, rsu, ue);

  double gain = 0;

  if (index != -1)
  {
    std::string fileName {m_path+"largeScalePwr_V2I.csv"};
    gain += ReadRxPower (index, fileName); // get pathloss
    if (m_smallScaleEnabled)
    {
    fileName = m_path+"smallScaleVar_V2I.csv";
      gain += ReadRxPower (index, fileName); // get small scale variations
    }
    NS_LOG_DEBUG("Gain:" << gain << " dBm");
  }
  else
  {
    gain = std::numeric_limits<double>::infinity();
    NS_LOG_DEBUG("UE " << ue << " is not in the communication range of RSU " << rsu);
  }

  return txPowerDbm + gain;
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