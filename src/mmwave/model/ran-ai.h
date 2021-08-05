#pragma once
#include "ns3/ns3-ai-module.h"
#include <map>

namespace ns3 {
namespace mmwave {
  
struct ranAIEnv
{
  int testAttr;
} Packed;

struct ranAIAct
{
  int testAct;
};

class RanAI : public Ns3AIRL<ranAIEnv, ranAIAct>
{
  public:
    RanAI ();
    RanAI (uint16_t id);
    
    uint16_t ReportMeasures (uint8_t testAttr);
};

} // namespace mmwave
} // namespace ns3