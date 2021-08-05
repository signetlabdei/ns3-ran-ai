#include <numeric>
#include "ns3/ran-ai.h"
#include "ns3/log.h"

using namespace ns3;
using namespace mmwave;

NS_LOG_COMPONENT_DEFINE("ns3::RanAI");

RanAI::RanAI(uint16_t id) : Ns3AIRL<ranAIEnv, ranAIAct>(id)
{
  SetCond(2, 0);
}

uint16_t RanAI::ReportMeasures (uint8_t attr)
{
  auto env = EnvSetterCond();
  env->testAttr = attr;
  
  // uint8_t counter = 0;
  // for (const auto& i : cellSinrMap)
  // {
  //   NS_ASSERT_MSG ((counter + 1) < MAX_NUM_CELL, "Too many cells");
    
  //   uint16_t cellId = i.first;
  //   double sinr = i.second;
  //   env->cellSinrMap [counter] [0] = (int32_t)cellId;
  //   env->cellSinrMap [counter] [1] = (int32_t)(10 * std::log10 (sinr));
  //   NS_LOG_DEBUG ("Handover Agent reports: cell " << cellId << 
  //   " sinr " << (int32_t)(10 * std::log10 (sinr)) << 
  //   " counter " << +counter);
    
  //   ++counter;
  // }
  
  // counter = 0;
  // for (const auto& i : bufferStatusMap)
  // {
  //   NS_ASSERT_MSG ((counter + 1) < MAX_NUM_LC, "Too many logical channels");
    
  //   uint8_t lcid = i.first;
  //   uint32_t bufferSize = i.second;
  //   env->bufferStatusMap [counter] [0] = (uint32_t)lcid;
  //   env->bufferStatusMap [counter] [1] = bufferSize;
    
  //   ++counter;
  // }

  SetCompleted();
  
  auto act = ActionGetterCond();
  int action = act->testAct;

  std::cout << Simulator::Now().GetSeconds() << " Action is " << action << std::endl;
  GetCompleted();

  return action;
}

