#pragma once
#include "ns3/ns3-ai-module.h"
#include "ns3/mmwave-bearer-stats-calculator.h"
#include "ns3/bursty-app-stats-calculator.h"
#include <map>

namespace ns3 {
namespace mmwave {

#define MAX_NUM_USERS 50 // maximum number of users

struct ranAIEnv
{
  double imsiStatsMap[MAX_NUM_USERS][28]; // [max # of users][# of statistics]
} Packed;

struct ranAIAct
{
  uint16_t act[MAX_NUM_USERS][2];
};

class RanAI : public Ns3AIRL<ranAIEnv, ranAIAct>
{
  public:
    RanAI ();
    RanAI (uint16_t id);

    std::map<uint16_t, uint16_t> ReportMeasures (std::map<double, std::vector<double>> stats);
};

} // namespace mmwave
} // namespace ns3