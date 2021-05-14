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
#include "ns3/gemv-tag.h"
#include "ns3/log.h"
#include "ns3/simulator.h"
#include "ns3/network-module.h"
#include "ns3/applications-module.h"
using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("GemvPropagationTest");

void static 
ReadPower (Ptr<OutputStreamWrapper> stream, Ptr<GemvPropagationLossModel> gemv, double txPowerDbm, Ptr<Node> rsu, NodeContainer ues)
{
  *stream->GetStream () << Simulator::Now ().GetSeconds () << "\t" ; 
  for (uint8_t i = 0; i < ues.GetN(); i++)
  {
    *stream->GetStream () << gemv->DoCalcRxPower(txPowerDbm, rsu->GetObject<MobilityModel> (), ues.Get(i)->GetObject<MobilityModel> ()) << "\t";
  }
  *stream->GetStream () << std::endl;
}

void static 
ReadLosCondition (Ptr<OutputStreamWrapper> stream, Ptr<GemvPropagationLossModel> gemv, Ptr<Node> rsu, NodeContainer ues)
{
  *stream->GetStream () << Simulator::Now ().GetSeconds () << "\t";
  for (uint8_t i = 0; i < ues.GetN (); i++)
    {
      *stream->GetStream () << uint32_t( gemv->ReadPairLosCondition (rsu->GetObject<MobilityModel> (),
                                                    ues.Get (i)->GetObject<MobilityModel> ()) )
                            << "\t";
    }
  *stream->GetStream () << std::endl;
}

int
main (int argc, char *argv[])
{
  CommandLine cmd;
  cmd.Parse (argc, argv);

  Config::SetDefault ("ns3::GemvPropagationLossModel::InputPath", StringValue("/home/dragomat/Documents/ns3-mmwave-pqos/input/"));
  
  Ptr<GemvPropagationLossModel> gemv = CreateObject<GemvPropagationLossModel> ();

  NodeContainer nodes;
  nodes.Create (1);

  std::vector<uint16_t> rsuList = gemv->GetDistinctIds(true);
  std::vector<uint16_t> ueList = gemv->GetDistinctIds(false);

  Ptr<GemvTag> tagRsu = CreateObject<GemvTag>();
  tagRsu->SetTagId(3);
  tagRsu->SetNodeType(true);
  Ptr<Object> object = nodes.Get(0);
  object->AggregateObject (tagRsu);

  NodeContainer ueNodes;
  ueNodes.Create (ueList.size());

  for (uint16_t i = 0; i < ueList.size(); i++)
  {
    Ptr<GemvTag> tagUe = CreateObject<GemvTag>();
    tagUe->SetTagId(ueList.at(i));
    tagUe->SetNodeType(false);
    object = ueNodes.Get(i);
    object->AggregateObject (tagUe);
  }

  // Install Mobility Model
  MobilityHelper mobility;
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (nodes);
  mobility.Install (ueNodes);

  AsciiTraceHelper asciiTraceHelper;
  Ptr<OutputStreamWrapper> stream_1 = asciiTraceHelper.CreateFileStream ("powerTest-3.txt");
  Ptr<OutputStreamWrapper> stream_2 = asciiTraceHelper.CreateFileStream ("losCondition-3.txt");

  for (uint8_t i = 0; i < 25; i++)
  {
    Simulator::Schedule (Seconds (i), &ReadPower, stream_1, gemv, 0, nodes.Get (0), ueNodes);
    Simulator::Schedule (Seconds (i), &ReadLosCondition, stream_2, gemv, nodes.Get (0), ueNodes);
  } 

  Simulator::Run();
  Simulator::Stop(Seconds(25));
  return 0;
}