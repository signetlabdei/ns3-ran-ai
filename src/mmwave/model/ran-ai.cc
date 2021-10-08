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

std::map<uint16_t, uint16_t>
RanAI::ReportMeasures (std::map<double, std::vector<double>> stats)
{
  auto env = EnvSetterCond();

  uint8_t counter = 0;
  for (const auto &i : stats)
  {
    env->imsiStatsMap[counter][0] = i.first; // here it goes the IMSI

    env->imsiStatsMap[counter][1] = i.second[0]; //
    env->imsiStatsMap[counter][2] = i.second[1];
    env->imsiStatsMap[counter][3] = i.second[2];

    env->imsiStatsMap[counter][4] = i.second[3];
    env->imsiStatsMap[counter][5] = i.second[4];
    env->imsiStatsMap[counter][6] = i.second[5];
    env->imsiStatsMap[counter][7] = i.second[6];
    env->imsiStatsMap[counter][8] = i.second[7];
    env->imsiStatsMap[counter][9] = i.second[8];
    env->imsiStatsMap[counter][10] = i.second[9];
    env->imsiStatsMap[counter][11] = i.second[10];

    env->imsiStatsMap[counter][12] = i.second[11];
    env->imsiStatsMap[counter][13] = i.second[12];
    env->imsiStatsMap[counter][14] = i.second[13];
    env->imsiStatsMap[counter][15] = i.second[14];
    env->imsiStatsMap[counter][16] = i.second[15];
    env->imsiStatsMap[counter][17] = i.second[16];
    env->imsiStatsMap[counter][18] = i.second[17];
    env->imsiStatsMap[counter][19] = i.second[18];

    env->imsiStatsMap[counter][20] = i.second[19];
    env->imsiStatsMap[counter][21] = i.second[20];
    env->imsiStatsMap[counter][22] = i.second[21];
    env->imsiStatsMap[counter][23] = i.second[22];
    env->imsiStatsMap[counter][24] = i.second[23];
    env->imsiStatsMap[counter][25] = i.second[24];
    env->imsiStatsMap[counter][26] = i.second[25];
    env->imsiStatsMap[counter][27] = i.second[26];

    ++counter;
  }

  SetCompleted();
  
  auto newAct = ActionGetterCond();
  auto actions = newAct->act;

  std::map<uint16_t, uint16_t> acts;
  for (uint8_t i = 0; i < counter; ++i)
  {
    NS_LOG_DEBUG("Propagate action " << actions[i][1] << " for IMSI "<< actions[i][0]);
    acts.insert (std::make_pair (actions[i][0], actions[i][1]));
  }
  
  GetCompleted();

  return acts;
}

