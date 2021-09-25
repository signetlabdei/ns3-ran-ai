#pragma once
#include "ns3/ns3-ai-module.h"
#include "ns3/mmwave-bearer-stats-calculator.h"
#include "ns3/bursty-app-stats-calculator.h"
#include <map>

namespace ns3 {
namespace mmwave {
  
struct ranAIEnv
{
  double mcs;
  double symbols;
  double sinr;
  uint16_t rlcTxPackets;
  uint32_t rlcTxData;
  uint16_t rlcRxPackets;
  uint32_t rlcRxData;
  double rlcDelayMean;
  double rlcDelayStdev;
  double rlcDelayMin;
  double rlcDelayMax;
  uint16_t pdcpTxPackets;
  uint32_t pdcpTxData;
  uint16_t pdcpRxPackets;
  uint32_t pdcpRxData;
  double pdcpDelayMean;
  double pdcpDelayStdev;
  double pdcpDelayMin;
  double pdcpDelayMax;
  uint16_t appTxBursts;
  uint32_t appTxData;
  uint16_t appRxBursts;
  uint32_t appRxData;
  double appDelayMean;
  double appDelayStdev;
  double appDelayMin;
  double appDelayMax;
} Packed;

struct ranAIAct
{
  int act;
};

class RanAI : public Ns3AIRL<ranAIEnv, ranAIAct>
{
  public:
    RanAI ();
    RanAI (uint16_t id);

    uint16_t ReportMeasures (double mcs, double symbols, double sinr, UlDlResults rlcResults, UlDlResults pdcpResults, AppResults appResults);
};

} // namespace mmwave
} // namespace ns3