# 🏛️ GovernanceAgent — Consolidação de 7 Agentes de Governança

> **Campaign Autopilot v5.2.1** — 7 delegates em 1 agente

> Um único agente que substitui 7 thin wrappers, cada um seguindo o mesmo padrão: delegar a um módulo de governança, empacotar resultado em AgentResult.

## Motivação

Os 7 agentes de governança originais eram idênticos em estrutura (~25 linhas cada):

```
quality_assurance_agent.py:  QualityAssurance.get_content_benchmarks() → AgentResult
external_monitor_agent.py:   ExternalMonitor.generate_monitoring_report() → AgentResult
risk_management_agent.py:    RiskManager.assess_system_risks() → AgentResult
rollback_manager_agent.py:   RollbackManager.health_check() → AgentResult
performance_analytics.py:    PerformanceAnalytics.generate_channel_report() → AgentResult
resource_manager_agent.py:   ResourceManager.create_budget() → AgentResult
ab_testing_agent.py:         ABTestingEngine.generate_headline_variants() → AgentResult
```

**Simplificação Ponytail:** 7 arquivos → 1 arquivo, -120 linhas, 6 arquivos eliminados.

## Deleges Disponíveis

| Delegate | Handler | Módulo |
|----------|---------|--------|
| `quality_assurance` | `_run_quality_assurance` | `governance.quality_assurance.QualityAssurance` |
| `external_monitor` | `_run_external_monitor` | `governance.external_monitor.ExternalMonitor` |
| `risk_management` | `_run_risk_management` | `governance.risk_management.RiskManager` |
| `rollback_manager` | `_run_rollback_manager` | `governance.rollback_manager.RollbackManager` |
| `performance_analytics` | `_run_performance_analytics` | `governance.performance_analytics.PerformanceAnalytics` |
| `resource_manager` | `_run_resource_manager` | `governance.resource_manager.ResourceManager` |
| `ab_testing` | `_run_ab_testing` | `execution.ab_testing.ABTestingEngine` |

## Uso

```python
from campaign_autopilot.agents.governance_agent import GovernanceAgent
from campaign_autopilot.agents.base import CampaignContext

# Qualidade
qa = GovernanceAgent(delegate="quality_assurance")
result = qa.run(CampaignContext())

# Risco
risk = GovernanceAgent(delegate="risk_management")
result = risk.run(CampaignContext(campaign={"niche": "marketing digital"}))

# No Orchestrator (registry automático)
orchestrator = CampaignOrchestrator(...)
result = orchestrator.run_agent("risk_management", context)
```

## Tratamento de Erros

Se um delegate inválido for passado, `GovernanceAgent.__init__` levanta `ValueError`:

```python
GovernanceAgent(delegate="invalid")  # ValueError: Unknown governance delegate: invalid
```

Erros durante a execução do handler são capturados e retornam `status="error"` no `AgentResult`.

## Como Adicionar Novo Delegate

1. Criar função handler em `src/campaign_autopilot/agents/governance_agent.py`
2. Mapear no dict `_GOVERNANCE_HANDLERS`
3. Pronto — sem novo arquivo, sem nova classe

```python
def _run_meu_servico(ctx: CampaignContext) -> dict[str, Any]:
    from ..governance.meu_servico import MeuServico
    result = MeuServico.executar()
    return {"status": "success", "data": result,
            "_notes": ["Serviço executado"], "_metadata": {}}

_GOVERNANCE_HANDLERS["meu_servico"] = _run_meu_servico
```

---

*Parte da documentação do Campaign Autopilot v5.2.0 — Atualizado em 2026-06-24.*
