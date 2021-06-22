/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
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
 */

#ifndef KITTI_TRACE_BURST_GENERATOR_H
#define KITTI_TRACE_BURST_GENERATOR_H

#include <ns3/trace-file-burst-generator.h>
#include <queue>

namespace ns3 {

class Time;

/** 
 * \ingroup applications
 * 
 * \brief Reads a traffic trace file to generate bursts
 * 
 * The generator reads a trace file obtained from the Kitti Dataset and generates bursts accordingly.
 * A trace file should be formatted following the guidelines given
 * by the documentation of ns3::CsvReader.
 * 
 */
class KittiTraceBurstGenerator : public TraceFileBurstGenerator
{
public:
  KittiTraceBurstGenerator ();
  virtual ~KittiTraceBurstGenerator ();

  // inherited from Object
  static TypeId GetTypeId ();

  // inherited from BurstGenerator
  virtual std::pair<uint32_t, Time> GenerateBurst (void) override;
  /**
   * \brief Returns true while more bursts are present in the trace
   * \return false when the end of the trace is reached
   */
  virtual bool HasNextBurst (void) override;
  /**
   * \brief Set the scene that LIDAR is seeing
   * \param scn number representing the scene 
   */
  void SetScene (int scn);

  /**
   * \brief Returns the index associated to the scene
   * \return the scene index
   */
  int GetScene (void) const;
  /**
   * \brief Set the traffic model representing the LIDAR data collection
   * \param mdl traffic model index 
   */
  void SetModel (uint32_t mdl);
  /**
   * \brief Returns the index associated to the traffic model
   * \return traffic model index
   */
  uint32_t GetModel (void) const;
  /**
   * \brief Set the time period between two distinct LIDAR frames
   * \param period new frame period 
   */
  void SetFramePeriod (Time period);
  /**
   * \brief Returns the time period between two distinct LIDAR frames
   * \return frame period
   */
  Time GetFramePeriod (void) const;

protected:
  virtual void DoDispose (void) override;

private:
  
    /**
   * Import the trace file into the burst queue
   */
  void ImportTrace (void);

  // Structure representing one row from the Kitti dataset
  struct FrameInfo
  {
    FrameInfo (uint32_t bSize, uint16_t encoTime, uint16_t decoTime)
        : m_burstSize (bSize), m_encodingTime (encoTime), m_decodingTime (decoTime)
    {
    }

    uint32_t m_burstSize;
    uint16_t m_encodingTime;
    uint16_t m_decodingTime;
  };

  std::vector< std::map<uint16_t, struct FrameInfo> > m_frameVector;

  std::string m_traceFile{""}; //!< The name of the trace file
  uint32_t m_frameNumber{0}; //!< The frame number associated to a specific scene
  Time m_framePeriod{MilliSeconds (100)}; //!< The time distance between two distinct LIDAR frames
  int m_scene{0}; //!< The index of the scene of interest
  uint8_t m_readingMode; //!< Flag indicating how to read the traces
  uint32_t m_model{1150}; //!< The index representing the used traffic model
  bool m_isFinalized{false}; //!< The generator is finalized only once ImportTrace ends with no errors
};

} // namespace ns3

#endif // TRACE_FILE_BURST_GENERATOR_H
