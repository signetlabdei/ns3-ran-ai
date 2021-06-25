/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
//
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

#include <sstream>
#include "ns3/log.h"
#include "ns3/random-variable-stream.h"
#include "ns3/string.h"
#include "ns3/uinteger.h"
#include "ns3/integer.h"
#include "ns3/double.h"
#include "ns3/nstime.h"
#include "ns3/csv-reader.h"
#include "kitti-trace-burst-generator.h"

namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("KittiTraceBurstGenerator");

NS_OBJECT_ENSURE_REGISTERED (KittiTraceBurstGenerator);

TypeId
KittiTraceBurstGenerator::GetTypeId (void)
{
  static TypeId tid =
      TypeId ("ns3::KittiTraceBurstGenerator")
          .SetParent<BurstGenerator> ()
          .SetGroupName ("Applications")
          .AddConstructor<KittiTraceBurstGenerator> ()
          .AddAttribute ("TraceFile", "The path to the trace file", StringValue (""),
                         MakeStringAccessor (&KittiTraceBurstGenerator::m_traceFile),
                         MakeStringChecker ())
          .AddAttribute ("Scene", "The scene to be considered by the application", IntegerValue (0),
                         MakeIntegerAccessor (&KittiTraceBurstGenerator::SetScene,
                                              &KittiTraceBurstGenerator::GetScene),
                         MakeIntegerChecker<int> (0))
          .AddAttribute ("Model",
                         "Traffic model to be used by the application. As of now only [0, 1, 2, "
                         "1150, 1450, 1451, 1452] are supported",
                         UintegerValue (1450),
                         MakeUintegerAccessor (&KittiTraceBurstGenerator::SetModel,
                                               &KittiTraceBurstGenerator::GetModel),
                         MakeUintegerChecker<uint32_t> ())
          .AddAttribute ("FramePeriod",
                         "Distance between two consecutive LIDAR-collected frames, in milliseconds",
                         TimeValue (MilliSeconds (100)),
                         MakeTimeAccessor (&KittiTraceBurstGenerator::SetFramePeriod,
                                           &KittiTraceBurstGenerator::GetFramePeriod),
                         MakeTimeChecker ())
          .AddAttribute ("ReadingMode",
                         "Determine what the reader should do when it reaches the end of a scene."
                         "0 - the application stops as the scene ends;"
                         "1 - the reader restarts from the beginning of the same scene.",
                         IntegerValue (0),
                         MakeIntegerAccessor (&KittiTraceBurstGenerator::m_readingMode),
                         MakeIntegerChecker<int> (0));
  ;
  return tid;
}

KittiTraceBurstGenerator::KittiTraceBurstGenerator ()
{
  NS_LOG_FUNCTION (this);
}

KittiTraceBurstGenerator::~KittiTraceBurstGenerator ()
{
  NS_LOG_FUNCTION (this);
}

void
KittiTraceBurstGenerator::DoDispose (void)
{
  NS_LOG_FUNCTION (this);

  // chain up
  BurstGenerator::DoDispose ();
}

bool
KittiTraceBurstGenerator::HasNextBurst (void)
{
  NS_LOG_FUNCTION (this);

  bool hasNext = false;

  if (!m_isFinalized)
    {
      ImportTrace ();
    }

  if (m_frameNumber < m_frameVector.size())
    {
      NS_LOG_DEBUG ("Prepare to read frame " << m_frameNumber << " ...");
      hasNext = true;
    }
  else
    {
      NS_LOG_DEBUG ("End of the scene.");
      if (m_readingMode == 1)
        {
          NS_LOG_DEBUG ("Restart from the beginning of scene number " << m_scene);
          m_frameNumber = 0; // restart from the beginning of the scene
          hasNext = true;
        }
      else
        {
          NS_LOG_DEBUG ("End of the scene.");
        }
    }

  return hasNext;
}

std::pair<uint32_t, Time>
KittiTraceBurstGenerator::GenerateBurst ()
{
  NS_LOG_FUNCTION (this);
  if (!m_isFinalized)
    {
      ImportTrace ();
    }

  uint32_t burstSize = m_frameVector[m_frameNumber].at(m_model).m_burstSize;

  std::pair<uint32_t, Time> burst (burstSize, m_framePeriod);
  
  m_frameNumber++;
  return burst;
}

void 
KittiTraceBurstGenerator::SetScene (int scn)
{
  NS_ABORT_MSG_IF(scn < 0 || scn > 10, "This scene is not supported.");
  m_scene = scn;
}

int 
KittiTraceBurstGenerator::GetScene () const
{
  return m_scene;
}

void
KittiTraceBurstGenerator::SetModel (uint32_t mdl)
{
  NS_ABORT_MSG_IF (mdl != 0 && mdl != 1 && mdl != 2 && 
                   mdl !=  1150 && mdl != 1450 && mdl != 1451 && mdl != 1452, 
                   "This traffic model is not supported.");
  m_model = mdl;
}

uint32_t
KittiTraceBurstGenerator::GetModel () const
{
  return m_model;
}

void
KittiTraceBurstGenerator::SetFramePeriod (Time period)
{
  m_framePeriod = period;
}

Time
KittiTraceBurstGenerator::GetFramePeriod () const
{
  return m_framePeriod;
}

void
KittiTraceBurstGenerator::ImportTrace (void)
{
  NS_LOG_FUNCTION (this);

  // extract trace from file
  char delimiter = ';';
  CsvReader csv (m_traceFile, delimiter);

  std::string name;
  uint16_t model;
  uint32_t burstSize;
  uint16_t encodingTime;
  uint16_t decodingTime;
  int frame = 0;

  std::map<uint16_t, struct FrameInfo> info;

  while (csv.FetchNextRow ())
    {
      // Ignore blank lines and first line
      if (csv.IsBlankRow () || csv.RowNumber () == 1)
        {
          continue;
        }

      // Expecting burst size and period to next burst
      bool ok = csv.GetValue (0, name);
      ok |= csv.GetValue (1, model);
      ok |= csv.GetValue (2, burstSize);
      ok |= csv.GetValue (3, encodingTime);
      ok |= csv.GetValue (4, decodingTime);

      std::string delimiter = ".";
      std::string sceneFrame = name.substr (0, name.find (delimiter));
      
      // Get the scene and frame index
      delimiter = "/";
      int scene = stoi( sceneFrame.substr (0, sceneFrame.find (delimiter)));
      int newFrame = stoi( sceneFrame.substr (sceneFrame.find (delimiter) + 1));

      if (scene != m_scene)
      {
        // consider only the scene that we are interested in
        continue;
      }

      NS_LOG_DEBUG (scene << " " << frame << " " << model << " " << burstSize << " " << encodingTime << " " << decodingTime);

      FrameInfo frameInfo (burstSize, encodingTime, decodingTime);

      if (frame != newFrame)
      {
        // each row of m_frameVector is associated to a specific frame
        // once each traffic model is added, we can move to the next frame 
        m_frameVector.push_back(info);
        info.clear();
        info.insert ({model, frameInfo});
        frame = newFrame;
      }
      else
      {
        info.insert({model, frameInfo});
      }
      
      NS_ABORT_MSG_IF (!ok, "Something went wrong on line " << csv.RowNumber () << " of file " << m_traceFile);

    } // while FetchNextRow

  m_isFinalized = true;
}

} // Namespace ns3
