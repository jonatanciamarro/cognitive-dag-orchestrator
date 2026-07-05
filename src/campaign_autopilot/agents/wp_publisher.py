"""Agente de Publicação WordPress — publica conteúdo em sites WordPress via REST API ou simulação."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


class WordPressPublisherAgent(AgentBase):
    """Publica conteúdo gerado em sites WordPress.

    Modos de operação:
    - 'api': Usa WordPress REST API (requer WP_CREDENTIALS no .env)
    - 'file': Salva como arquivos .md localmente (modo simulado, padrão)
    - 'dry_run': Apenas registra o que seria publicado
    """

    def __init__(
        self, publish_mode: str = "file", output_dir: str = "output/content", **kwargs
    ) -> None:
        super().__init__("wp_publisher", **kwargs)
        self.publish_mode = publish_mode
        self.output_dir = Path(output_dir)

    def _publish_to_file(self, article: dict[str, Any], channel: str) -> dict[str, Any]:
        """Salva o artigo como arquivo .md no diretório de output."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        slug = article.get("slug", "post-" + str(uuid.uuid4())[:8])
        filename = f"{slug}.md"
        filepath = self.output_dir / filename

        # Monta frontmatter YAML-like
        content = f"""---
title: "{article.get("title", "Untitled")}"
slug: {slug}
date: {datetime.now(timezone.utc).isoformat()}
type: {article.get("content_type", "article")}
meta_description: "{article.get("meta_description", "")}"
word_count: {article.get("word_count", 0)}
estimated_reading_time: {article.get("estimated_reading_time", 1)}min
status: draft
---

{article.get("body", "")}
"""

        filepath.write_text(content, encoding="utf-8")

        return {
            "filename": filename,
            "path": str(filepath.absolute()),
            "status": "draft",
            "mode": "file",
            "word_count": article.get("word_count", 0),
        }

    def _publish_to_api(self, article: dict[str, Any]) -> dict[str, Any]:
        """Publica via WordPress REST API.

        Requer variáveis de ambiente:
        - WP_URL: URL base do WordPress (ex: https://meusite.com)
        - WP_USER: Usuário da aplicação
        - WP_PASSWORD: Application Password (gerado no perfil do WordPress)
        """
        wp_url = os.environ.get("WP_URL", "")
        wp_user = os.environ.get("WP_USER", "")
        wp_password = os.environ.get("WP_PASSWORD", "")

        if not all([wp_url, wp_user, wp_password]):
            return {
                "error": "Credenciais WordPress não configuradas. Configure WP_URL, WP_USER e WP_PASSWORD no .env",
                "fallback_mode": "file",
                **self._publish_to_file(article, "wordpress"),
            }

        try:
            import urllib.request
            import base64

            api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts"
            credentials = base64.b64encode(f"{wp_user}:{wp_password}".encode()).decode()

            post_data = json.dumps(
                {
                    "title": article.get("title", ""),
                    "content": article.get("body", ""),
                    "slug": article.get("slug", ""),
                    "excerpt": article.get("meta_description", ""),
                    "status": "draft",
                    "meta": {
                        "campaign_autopilot": True,
                        "content_type": article.get("content_type", "article"),
                        "keyword": article.get("keyword", ""),
                    },
                }
            ).encode("utf-8")

            req = urllib.request.Request(
                api_url,
                data=post_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {credentials}",
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))

            return {
                "wp_post_id": result.get("id"),
                "wp_link": result.get("link"),
                "status": "draft",
                "mode": "api",
                "word_count": article.get("word_count", 0),
            }

        except Exception as exc:
            return {
                "error": f"Falha ao publicar via API: {exc}",
                "fallback_mode": "file",
                **self._publish_to_file(article, "wordpress"),
            }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign

        # Pega artigos do content_generator
        generator = context.step_results.get("content_generator", {})
        generator_output = (
            generator.get("output", {}) if isinstance(generator, dict) else {}
        )
        articles = generator_output.get("articles", [])

        if not articles:
            # Fallback: verificar se veio do content_planner
            planning = context.step_results.get("content_planner", {})
            planning_output = (
                planning.get("output", {}) if isinstance(planning, dict) else {}
            )
            briefs = planning_output.get("briefs", [])
            if briefs:
                articles = [
                    {
                        "title": brief.get("topic", brief.get("keyword", "Post")),
                        "slug": brief.get("keyword", "post").lower().replace(" ", "-"),
                        "body": f"Conteúdo sobre {brief.get('topic', brief.get('keyword', ''))}",
                        "content_type": brief.get("content_type", "article"),
                        "keyword": brief.get("keyword", ""),
                        "word_count": 50,
                        "meta_description": f"Conteúdo sobre {brief.get('topic', '')}",
                    }
                    for brief in briefs[:3]
                ]

        # Determinar modo de publicação
        mode = self.publish_mode
        if mode == "api":
            # Só usa API se credenciais estiverem configuradas
            if os.environ.get("WP_URL"):
                mode = "api"
            else:
                mode = "file"

        channels = list(campaign.get("channels", ["seo"]))
        now = datetime.now(timezone.utc)

        # Publicar cada artigo
        publications = []
        for i, article in enumerate(articles):
            pub_date = now + timedelta(days=i * 3)

            if mode == "api":
                result = self._publish_to_api(article)
            elif mode == "dry_run":
                result = {
                    "mode": "dry_run",
                    "title": article.get("title", ""),
                    "status": "dry_run",
                    "scheduled_date": pub_date.isoformat(),
                }
            else:
                result = self._publish_to_file(
                    article, channels[i % len(channels)] if channels else "seo"
                )

            result["title"] = article.get("title", "")
            result["content_type"] = article.get("content_type", "article")
            result["keyword"] = article.get("keyword", "")
            result["scheduled_date"] = pub_date.isoformat()
            publications.append(result)

        # Estatísticas
        api_count = sum(1 for p in publications if p.get("mode") == "api")
        file_count = sum(1 for p in publications if p.get("mode") == "file")
        errors = [p.get("error") for p in publications if p.get("error")]
        total_words = sum(p.get("word_count", 0) for p in publications)

        output = {
            "publications": publications,
            "total_published": len(publications),
            "total_words": total_words,
            "mode_used": mode,
            "api_count": api_count,
            "file_count": file_count,
            "error_count": len(errors),
            "errors": errors,
            "output_directory": str(self.output_dir.absolute())
            if mode == "file"
            else None,
            "publishing_plan": (
                f"Publicados {len(publications)} artigos (modo: {mode}). "
                f"Total: ~{total_words} palavras. "
                f"{'Erros: ' + str(len(errors)) if errors else 'Sem erros.'}"
            ),
        }

        # Registrar explicação
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="wordpress_publishing",
                input_state={
                    "articles": len(articles),
                    "mode": mode,
                    "channels": channels,
                },
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "published": len(publications),
                    "mode": mode,
                    "errors": len(errors),
                },
            )

        # Conhecimento semântico
        if self.semantic_memory and publications:
            pub_concept_id = self.semantic_memory.register_concept(
                f"publish_cycle_{context.run_id[:8]}",
                "publishing",
                f"Ciclo de publicação: {len(publications)} artigos via {mode}",
            )
            for pub in publications:
                article_concept = self.semantic_memory.find_concept(
                    f"article_{pub.get('keyword', '')[:20]}", "content"
                )
                if article_concept:
                    self.semantic_memory.assert_claim(
                        subject=pub_concept_id,
                        predicate="published",
                        object=article_concept["concept_id"],
                        confidence=0.9 if pub.get("mode") != "dry_run" else 0.5,
                        evidence_type="DIRECT_OBSERVATION",
                        epistemic_status="VERIFIED"
                        if pub.get("mode") == "api"
                        else "INFERRED",
                        supporting_data=pub,
                        source_cycle_id=context.run_id,
                        asserted_by=self.name,
                        observer_id=self.name,
                    )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="wp_publisher",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[f"Publicou {len(publications)} artigos no modo '{mode}'"],
            metadata={
                "publications": len(publications),
                "mode": mode,
                "errors": len(errors),
                "total_words": total_words,
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
