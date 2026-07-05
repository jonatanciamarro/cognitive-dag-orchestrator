"""Agente de Deploy do Site — gera site estático completo a partir de todo conteúdo do ciclo."""

from __future__ import annotations

import sys
from pathlib import Path

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


class SiteDeployAgent(AgentBase):
    """Gera site estático completo com todo o conteúdo produzido no ciclo.

    Depende de: content_generator, content_repurposer, lead_capture
    Produz: site HTML completo com blog, sitemap, RSS, SEO, lead capture
    """

    def __init__(
        self,
        output_dir: str = "site",
        site_url: str = "https://seudominio.com",
        **kwargs,
    ) -> None:
        super().__init__("site_deploy", **kwargs)
        self.output_dir = output_dir
        self.site_url = site_url

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )
        site_title = f"Guia Completo de {niche.title()} para Iniciantes"

        # Collect articles
        gen = context.step_results.get("content_generator", {})
        gen_out = gen.get("output", {}) if isinstance(gen, dict) else {}
        articles = gen_out.get("articles", [])

        # Collect repurposed content
        rp = context.step_results.get("content_repurposer", {})
        rp_out = rp.get("output", {}) if isinstance(rp, dict) else {}
        repurposed = rp_out.get("repurposed_content", [])

        # Collect lead magnets
        lc = context.step_results.get("lead_capture", {})
        lc_out = lc.get("output", {}) if isinstance(lc, dict) else {}
        lead_magnets = lc_out.get("lead_magnets", [])

        # Collect pin data
        pin = context.step_results.get("pinterest_marketing", {})
        pin_out = pin.get("output", {}) if isinstance(pin, dict) else {}
        pin_data = pin_out.get("pins", [])

        # Generate site
        try:
            sys.path.insert(
                0, str(Path(__file__).resolve().parent.parent.parent.parent)
            )
            from site_generator import SiteGenerator

            gen = SiteGenerator(output_dir=self.output_dir)
            result = gen.generate(
                articles=articles,
                repurposed=repurposed,
                lead_magnets=lead_magnets,
                pin_data=pin_data,
                niche=niche,
                site_title=site_title,
                site_url=self.site_url,
                author="Equipe Autopilot",
            )

            output = {
                **result,
                "niche": niche,
                "site_url": self.site_url,
                "pages_generated": [
                    "/index.html (home)",
                    "/lead-capture.html (lead capture)",
                    "/pages/sobre.html",
                    "/pages/contato.html",
                    "/pages/privacidade.html",
                    "/pages/disclosure.html",
                    "/sitemap.xml",
                    "/robots.txt",
                    "/rss.xml",
                ]
                + [f"/blog/{a.get('slug', 'artigo')}.html" for a in articles],
                "recommendation": (
                    f"Site estático gerado em {self.output_dir}/ com {result['files_generated']} arquivos. "
                    f"Para publicar: faça upload para Netlify, Vercel ou GitHub Pages. "
                    f"Configure {self.site_url} no seu domínio."
                ),
            }

        except ImportError as exc:
            output = {
                "error": f"SiteGenerator não encontrado: {exc}",
                "files_generated": 0,
                "output_directory": self.output_dir,
                "site_url": self.site_url,
            }
        except Exception as exc:
            output = {
                "error": f"Erro ao gerar site: {exc}",
                "files_generated": 0,
                "output_directory": self.output_dir,
                "site_url": self.site_url,
            }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="site_deploy",
                input_state={"articles": len(articles), "niche": niche},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={"files": output.get("files_generated", 0)},
            )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="site_deploy",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou site estático com {output.get('files_generated', 0)} arquivos em {self.output_dir}"
            ],
            metadata={
                "files": output.get("files_generated", 0),
                "articles": len(articles),
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
