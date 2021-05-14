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

#ifndef GEMV_PROPAGATION_LOSS_MODEL_H
#define GEMV_PROPAGATION_LOSS_MODEL_H

#include "ns3/propagation-loss-model.h"
#include "ns3/nstime.h"

namespace ns3 {

class GemvPropagationLossModel : public PropagationLossModel
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
  GemvPropagationLossModel ();

  /**
   * Destructor
   */
  virtual ~GemvPropagationLossModel () override;

  /**
   * Set the time granularity used by the channel traces
   *
   * \param t time resolution in seconds
   */
  void SetTimeResolution(Time t);

  /**
   * Get the time granularity used by the channel traces
   *
   * \return time resolution in seconds
   */
  Time GetTimeResolution(void) const;

  /**
   * Set the traces path
   *
   * \param path string representing the path of the input path
   */
  void SetPath(std::string path);

  /**
   * Get the traces path
   *
   * \return path of the input traces
   */
  std::string GetPath(void) const;

  /**
   * Returns the Rx Power taking into account only the particular
   * PropagationLossModel.
   *
   * \param txPowerDbm current transmission power (in dBm)
   * \param a the mobility model of the source
   * \param b the mobility model of the destination
   * \returns the reception power after adding/multiplying propagation loss (in dBm)
   */
  virtual double DoCalcRxPower (double txPowerDbm,
                                Ptr<MobilityModel> a,
                                Ptr<MobilityModel> b) const;

  /**
   * Returns a list of distinct IDs associated to RSU/vehicles in the traces
   *
   * \param checkRsu true if we search for RSU IDs, false otherwise   
   * \returns list of distinct RSU/vehicle IDs
   */
  std::vector<uint16_t> GetDistinctIds (bool checkRsu);

  /**
   * Returns the LOS condition of the (a, b) pair
   *
   * \param a the mobility model of the source
   * \param b the mobility model of the destination
   * \returns 0-invalid; 1-LOS; 2-NLOSb; 3-NLOSv
   */
  uint8_t ReadPairLosCondition (Ptr<MobilityModel> a,
                                Ptr<MobilityModel> b) const;

  private :
      /**
   * \brief Copy constructor
   *
   * Defined and unimplemented to avoid misuse
   */
  GemvPropagationLossModel (const GemvPropagationLossModel &) = delete;
  /**
   * \brief Copy constructor
   *
   * Defined and unimplemented to avoid misuse
   */
  GemvPropagationLossModel &operator = (const GemvPropagationLossModel &) = delete;
  /**
   * Get from numCommPairsPerTimestep_V2I.csv the line intervals associated to a timestep 
   * 
   * \param index the time step index to read from the traces 
   * \param commType type of communication pair, i.e., V2I or V2V
   * \returns pair of indexes indicating the interval of rows to check in the communication pairs file 
   */
  std::pair<uint32_t, uint32_t> ReadTimestep (uint32_t index, std::string commType) const;
  /**
   * Get from commPairs_V2I.csv the line number associated to a specific RSU-UE pair in a specific timestep
   * 
   * \param start the left limit of the search interval
   * \param end the right limit of the search interval
   * \param nodeOne the ID associated to the RSU if commType is V2I, to another UE otherwise
   * \param nodeTwo the ID associated to the UE
   * \param commType type of communication pair, i.e., V2I or V2V
   * \returns the line to check to get the rx power / pathloss from the GEMV file
   */
  int32_t ReadCommPairs (uint32_t start, uint32_t end, uint16_t nodeOne, uint16_t nodeTwo, std::string commType) const;
  /**
   * Read from largeScalePwr_V2I.csv the pathloss of a specific RSU-UE pair in a specific timestep
   * 
   * \param index line to read
   * \param fileName file to read
   * \returns the value of loss, i.e., pathloss or small scale variations
   */
  double ReadRxPower (uint32_t index, std::string fileName) const;
  /**
   * Parse the ausiliar traces to find the index corresponding to the line to read   
   * 
   * \param nodeOne the ID associated to the RSU if commType is V2I, to another UE otherwise
   * \param nodeTwo the ID associated to the UE
   * \param commType type of communication pair, i.e., V2I or V2V
   * \returns the file index to read
   */
  int32_t GetIndex (uint16_t nodeOne, uint16_t nodeTwo, std::string commType) const;
  /**
   * If this model uses objects of type RandomVariableStream,
   * set the stream numbers to the integers starting with the offset
   * 'stream'. Return the number of streams (possibly zero) that
   * have been assigned.
   *
   * \param stream
   * \return the number of stream indices assigned by this model
   */
  virtual int64_t DoAssignStreams (int64_t stream) override;

  Time m_timeResolution; //!< time resolution used by the input traces 
  std::string m_path; //!< absolute path to the input traces
  bool m_smallScaleEnabled; //!< flag indicator for including small scale variation in rx power evaluations
};

} // namespace ns3

#endif /* GEMV_PROPAGATION_LOSS_MODEL_H */
