# news — Sub-agents Package

## Purpose
SEO e conteudo algoritmo-centrado: pesquisa, escrita, EEAT, tecnico, multimedia

## Agents
- content_research
- eeat_validator
- internal_linker
- seo_content_writer
- seo_multimedia
- seo_technical
- site_publisher

## Rules
- All agents extend AgentBase from agents/base.py
- Each agent implements run(context) -> AgentResult
- Zero external dependencies for core logic
- Thread-safe with RLock for shared state
