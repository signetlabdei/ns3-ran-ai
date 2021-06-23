/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright 2012 Eric Gamess
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

/*
 * ns-3 script to read a TCL trace file and export one CSV file for each 
 * node containing (Time, Position) pairs
 */

#include "ns3/core-module.h"
#include "ns3/mobility-module.h"
#include "ns3/trace-helper.h"

using namespace ns3;

void showPosition (Ptr<Node> node, double deltaTime, Ptr<OutputStreamWrapper> stream)
{
  Ptr<MobilityModel> mobModel = node->GetObject<MobilityModel> ();
  Vector3D pos = mobModel->GetPosition ();
            
  *stream->GetStream () << Simulator::Now ().GetSeconds () << " " << pos.x << " " << pos.y << "\n";
            
  Simulator::Schedule (Seconds (deltaTime), &showPosition, node, deltaTime, stream);
}

int main (int argc, char *argv[])
{
  std::cout.precision (10);
  std::cout.setf (std::ios::fixed);

  double deltaTime = 0.1;
  std::string traceFile = "input/bolognaLeftHalfRSU3_50vehicles_100sec/bolognaLeftHalfRSU3-mobility-trace.tcl";

  CommandLine cmd (__FILE__);
  cmd.AddValue ("traceFile", "Ns2 movement trace file", traceFile);
  cmd.AddValue ("deltaTime", "time interval (s) between updates (default 100)", deltaTime);
  cmd.Parse (argc, argv);

  NodeContainer c;
  c.Create (50);

  Ns2MobilityHelper ns2 = Ns2MobilityHelper (traceFile);
  ns2.Install ();
  
  AsciiTraceHelper asciiHelper; 
  std::string path = "input/bolognaLeftHalfRSU3_50vehicles_100sec/mobility/nodes/";
  for (uint32_t i = 0; i < c.GetN (); i++)
  {
    std::stringstream fileName;
    fileName << path << "node-" << c.Get (i)->GetId () << ".txt";
    Ptr<OutputStreamWrapper> stream = asciiHelper.CreateFileStream (fileName.str ());
    Simulator::Schedule (Seconds (0.0), &showPosition, c.Get (i), deltaTime, stream);
  }

  Simulator::Stop (Seconds (90.0));
  Simulator::Run ();
  Simulator::Destroy ();
  return 0;
}
