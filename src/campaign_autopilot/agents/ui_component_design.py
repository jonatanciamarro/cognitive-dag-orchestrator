"""UI Component Design Agent — 21st.dev-style component generation.

Gera componentes UI/UX completos com HTML/CSS responsivo,
design system tokens e variantes. Integrado ao UIComponentRegistry.
"""

from __future__ import annotations


from .base import AgentBase, AgentResult, CampaignContext


class UIComponentDesignAgent(AgentBase):
    """Agent that designs and generates UI components (21st.dev style).

    Usa o UIComponentRegistry para:
    - Listar componentes disponiveis
    - Gerar novas variantes
    - Renderizar paginas completas
    - Sugerir componentes baseado no contexto
    """

    def __init__(self, name: str = "ui_component_design"):
        super().__init__(name)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign or {}
        niche = campaign.get("niche", "marketing digital")
        goal = campaign.get("goal", "landing page")
        artifacts = context.artifacts or {}

        try:
            from ..ui_component_registry import UIComponentRegistry

            registry = UIComponentRegistry()
            stats = registry.stats()

            # Determine which components to use based on goal
            goal_lower = goal.lower()
            components_to_use = []

            # Always include navbar
            components_to_use.append(
                {
                    "component": "navbar-default",
                    "params": {
                        "logo": niche.title(),
                        "links": '<a href="#features">Recursos</a><a href="#pricing">Precos</a><a href="#faq">Ajuda</a>',
                        "cta_text": "Comecar",
                        "cta_link": "#cta",
                    },
                }
            )

            # Hero section
            components_to_use.append(
                {
                    "component": "hero-default",
                    "params": {
                        "badge": niche.title(),
                        "title": f"Domine {niche.title()} em 2026",
                        "subtitle": f"Estrategias comprovadas para crescer seu negocio de {niche}",
                        "cta_text": "Comecar Agora",
                        "cta_link": "#cta",
                        "secondary_text": "Saiba Mais",
                        "secondary_link": "#features",
                    },
                }
            )

            # Features
            components_to_use.append(
                {
                    "component": "features-grid",
                    "params": {
                        "section_title": "Recursos Principais",
                        "section_subtitle": f"Tudo que voce precisa para {niche}",
                        "features": '<div class="lyzer-card"><h3>Automacao</h3><p>Processos automatizados</p></div>'
                        '<div class="lyzer-card"><h3>Analytics</h3><p>Dados em tempo real</p></div>'
                        '<div class="lyzer-card"><h3>Escalabilidade</h3><p>Cresca sem limites</p></div>',
                    },
                }
            )

            # Pricing or CTA
            if (
                "venda" in goal_lower
                or "preco" in goal_lower
                or "pricing" in goal_lower
            ):
                components_to_use.append(
                    {
                        "component": "pricing-table",
                        "params": {
                            "section_title": "Planos e Precos",
                            "section_subtitle": "Escolha o plano ideal para voce",
                            "plans": '<div class="lyzer-card"><h3>Basico</h3></div><div class="lyzer-card"><h3>Pro</h3></div><div class="lyzer-card"><h3>Enterprise</h3></div>',
                        },
                    }
                )

            # Always include CTA
            components_to_use.append(
                {
                    "component": "cta-section",
                    "params": {
                        "title": "Pronto para comecar?",
                        "description": f"Transforme seus resultados com {niche}",
                        "button_text": "Iniciar Agora",
                        "button_link": "#signup",
                        "urgency_text": "Oferta por tempo limitado",
                    },
                }
            )

            # Footer
            components_to_use.append(
                {
                    "component": "footer-default",
                    "params": {
                        "brand_name": niche.title(),
                        "brand_description": f"Sua plataforma de {niche}",
                        "columns": "<div><h4>Produto</h4></div><div><h4>Empresa</h4></div><div><h4>Suporte</h4></div>",
                        "copyright": f"© 2026 {niche.title()}. Todos os direitos reservados.",
                    },
                }
            )

            # Render the complete page
            page_html = registry.render_page(components_to_use)

            # Save to output
            from pathlib import Path

            output_dir = Path("output") / "ui_design"
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{niche.lower().replace(' ', '-')}_21st_dev_landing_page.html"
            output_path = output_dir / filename
            with open(output_path, "w") as f:
                f.write(page_html)

            output = {
                "status": "success",
                "niche": niche,
                "goal": goal,
                "components_used": len(components_to_use),
                "components_list": [c["component"] for c in components_to_use],
                "total_page_chars": len(page_html),
                "output_file": str(output_path),
                "registry_stats": stats,
            }

        except Exception as e:
            output = {
                "status": "error",
                "error": str(e),
                "niche": niche,
            }

        finished_at = self._utcnow_iso()
        return AgentResult(
            agent=self.name,
            status=output.get("status", "error"),
            output=output,
            trace=self._build_trace(started_at, finished_at),
        )
