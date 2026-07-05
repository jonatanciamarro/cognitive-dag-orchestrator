# 🧠 Content Excellence Pipeline Skill

## Visão Geral
Pipeline de criação de conteúdo psicologicamente informado, usando **apenas ferramentas gratuitas** (stdlib Python).

## Arquitetura

### Módulo Core: `src/campaign_autopilot/content_pipeline/`
| Engine | Arquivo | Função |
|--------|---------|--------|
| Storytelling | `storytelling_engine.py` | Arcos narrativos (Jornada do Herói, 3 Atos, PAS, AIDA, BAB) |
| Psicologia | `psychology_engine.py` | Vieses cognitivos, princípios de persuasão (Cialdini), gatilhos |
| Psicanálise | `psychoanalysis_engine.py` | Triggers profundos (sombra, persona, individuação), arquétipos Junguianos |
| Neuromarketing | `neuromarketing_engine.py` | Dopamina, ocitocina, fluência cognitiva, neurônios-espelho |
| Comunicação | `communication_engine.py` | Framing (ganho/perda), tom de voz, dispositivos retóricos |
| Arquétipos | `archetype_engine.py` | 12 arquétipos de marca Junguianos com aplicações de conteúdo |
| Copywriting | `copywriting_engine.py` | Frameworks AIDA, PAS, BAB, FAB, geração de hooks/CTAs |

### Agentes: `src/campaign_autopilot/agents/`
| Agente | Função |
|--------|--------|
| `ContentExcellenceAgent` | Orquestrador principal de todas as melhorias |
| `StorytellingSpecialistAgent` | Seleciona estrutura narrativa, gera hooks |
| `PsychologySpecialistAgent` | Aplica vieses e princípios de persuasão |
| `NeuromarketingSpecialistAgent` | Otimiza para resposta cerebral |

### Sub-agentes incorporados nas engines:
- **Psicanálise**: interpretação de desejo inconsciente, shadow marketing, individuação
- **Comunicação**: perfil de tom de voz, guia de escrita, headlines framed
- **Arquétipos**: seleção por nicho, blend de arquétipos, voz de marca
- **Copywriting**: frameworks de copy, objeções, CTAs, urgência

## Frameworks Disponíveis

### Storytelling
- **Jornada do Herói**: artigos inspiradores, cases
- **3 Atos**: tutoriais, webinars
- **PAS (Problema-Agonize-Solução)**: maior conversão comprovada
- **AIDA**: funil completo
- **BAB (Before-After-Bridge)**: conteúdo aspiracional
- **Hook-Story-Offer**: TikTok/Reels

### Psicologia
- 7 princípios de Cialdini (Reciprocidade, Escassez, Autoridade, etc.)
- 15+ vieses cognitivos (Prova Social, Aversão à Perda, Ancoragem, etc.)
- Gatilhos emocionais (Medo, Ganância, Vaidade, Curiosidade, etc.)

### Psicanálise
- Jung: Sombra, Persona, Individuação, Inconsciente Coletivo
- Lacan: Desejo, Jouissance, Olhar do Outro
- Arquétipos: 12 tipos com aplicações de marca

## Workflows
```bash
# Pipeline standalone
.venv/bin/python scripts/autopilot.py \
  --workflow workflows/content_excellence_workflow.json \
  --context examples/affiliate_context.json \
  --db .state/db.sqlite3

# Workflow principal (43 steps)
make run
```

## Exemplo Rápido
```python
from src.campaign_autopilot.content_pipeline.storytelling_engine import StorytellingEngine
from src.campaign_autopilot.content_pipeline.psychology_engine import PsychologyEngine

# Criar arco narrativo
arc = StorytellingEngine.create_arc(StorytellingEngine.select_structure("blog_article", "persuade"))
print(arc.render_outline("marketing de afiliados", "marketing digital"))

# Perfil de persuasão
profile = PsychologyEngine.create_profile("marketing digital", "iniciantes")
print(profile.get_applications()[:3])
```
