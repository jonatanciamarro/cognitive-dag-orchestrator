# paid_traffic — Sub-agents Package

## Purpose
Trafego pago automatizado: Google Ads, Meta Ads, Native Ads com reinvestimento

## Agents
- ad_copy_generator
- budget_optimizer
- google_ads
- landing_page
- meta_ads
- native_ads
- paid_traffic_orchestrator
- performance_tracker
- revenue_monitor

## Rules
- All agents extend AgentBase from agents/base.py
- Each agent implements run(context) -> AgentResult
- Zero external dependencies for core logic
- Thread-safe with RLock for shared state
