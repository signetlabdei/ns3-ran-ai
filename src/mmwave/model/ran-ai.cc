#include <numeric>
#include "ns3/ran-ai.h"
#include "ns3/log.h"
#include "ns3/mmwave-bearer-stats-calculator.h"
#include "ns3/bursty-app-stats-calculator.h"

using namespace ns3;
using namespace mmwave;

NS_LOG_COMPONENT_DEFINE("ns3::RanAI");

RanAI::RanAI(uint16_t id) : Ns3AIRL<ranAIEnv, ranAIAct>(id)
{
  SetCond(2, 0);
}

uint16_t RanAI::ReportMeasures (double mcs, double symbols, double sinr, UlDlResults rlcResults, UlDlResults pdcpResults, AppResults appResults)
{
  auto env = EnvSetterCond();

  env->mcs = mcs;
  env->symbols = symbols;
  env->sinr = sinr;

  env->rlcTxPackets = rlcResults.txPackets;
  env->rlcTxData = rlcResults.txData;
  env->rlcRxPackets = rlcResults.rxPackets;
  env->rlcRxData = rlcResults.rxData;
  env->rlcDelayMean = rlcResults.delayMean;
  env->rlcDelayStdev = rlcResults.delayStdev;
  env->rlcDelayMin = rlcResults.delayMin;
  env->rlcDelayMax = rlcResults.delayMax;

  env->pdcpTxPackets = pdcpResults.txPackets;
  env->pdcpTxData = pdcpResults.txData;
  env->pdcpRxPackets = pdcpResults.rxPackets;
  env->pdcpRxData = pdcpResults.rxData;
  env->pdcpDelayMean = pdcpResults.delayMean;
  env->pdcpDelayStdev = pdcpResults.delayStdev;
  env->pdcpDelayMin = pdcpResults.delayMin;
  env->pdcpDelayMax = pdcpResults.delayMax;

  env->appTxBursts = appResults.txBursts;
  env->appTxData = appResults.txData;
  env->appRxBursts = appResults.rxBursts;
  env->appRxData = appResults.rxData;
  env->appDelayMean = appResults.delayMean;
  env->appDelayStdev = appResults.delayStdev;
  env->appDelayMin = appResults.delayMin;
  env->appDelayMax = appResults.delayMax;

  SetCompleted();
  
  auto newAct = ActionGetterCond();
  int action = newAct->act;

  GetCompleted();

  return action;
}

