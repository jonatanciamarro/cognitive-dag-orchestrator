# money — Sub-agents Package

## Purpose
Monetizacao: insercao de links de afiliado, produtos digitais, membresia

## Agents
- affiliate_link_inserter
- digital_product_agent
- membership_agent

## Rules
- All agents extend AgentBase from agents/base.py
- Each agent implements run(context) -> AgentResult
- Zero external dependencies for core logic
- Thread-safe with RLock for shared state
