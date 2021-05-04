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

#include <fstream>
#include "ns3/core-module.h"
#include "ns3/mobility-module.h"
#include "ns3/gemv-propagation-loss-model.h"
#include "ns3/log.h"
#include "ns3/simulator.h"
#include "ns3/network-module.h"
#include "ns3/applications-module.h"
using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("GemvPropagationTest");

void static 
ReadPower (Ptr<OutputStreamWrapper> stream, Ptr<GemvPropagationLossModel> gemv, double txPowerDbm, Ptr<MobilityModel> mm1, Ptr<MobilityModel> mm2)
{
  NS_LOG_UNCOND("Received power at time " << Simulator::Now().GetSeconds() << "s is " << gemv->DoCalcRxPower(0, mm1, mm2) << " dBm");
  *stream->GetStream () << Simulator::Now ().GetSeconds () << "\t" << gemv->DoCalcRxPower(0, mm1, mm2) << std::endl;
}

int
main (int argc, char *argv[])
{
  CommandLine cmd;
  cmd.Parse (argc, argv);

  Config::SetDefault ("ns3::GemvPropagationLossModel::InputPath", StringValue("/home/dragomat/Documents/ns3-mmwave-pqos/input/"));
  
  Ptr<GemvPropagationLossModel> gemv = CreateObject<GemvPropagationLossModel> ();
  
  Ptr<ConstantPositionMobilityModel> mm = CreateObject<ConstantPositionMobilityModel>();

  AsciiTraceHelper asciiTraceHelper;
  Ptr<OutputStreamWrapper> stream = asciiTraceHelper.CreateFileStream ("powerTest-3-12.txt");

  for (uint8_t i = 0; i < 25; i++)
  {
    Simulator::Schedule(Seconds(i), &ReadPower, stream, gemv, 0, mm, mm);
  } 

  Simulator::Run();
  Simulator::Stop(Seconds(25));
  return 0;
}