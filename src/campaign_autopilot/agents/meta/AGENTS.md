# meta — Sub-agents Package

## Purpose
Meta-cognicao e auto-evolucao: portfolio, compounding, deteccao de oportunidades

## Agents
- agent_factory
- compounding_engine
- cross_pollination_hub
- knowledge_synthesis_bridge
- opportunity_detector
- portfolio_optimizer

## Rules
- All agents extend AgentBase from agents/base.py
- Each agent implements run(context) -> AgentResult
- Zero external dependencies for core logic
- Thread-safe with RLock for shared state
