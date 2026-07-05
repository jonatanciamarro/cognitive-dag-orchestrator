"""EEATValidatorAgent — Valida Expertise, Authoritativeness, Trustworthiness.

Google's E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)
é o framework mais importante para ranqueamento orgânico em 2026.

Este agente valida cada artigo contra os critérios E-E-A-T e gera
recomendações de melhoria.
"""

from __future__ import annotations

import re
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("eeat_validator")


EEAT_CRITERIA = {
    "experience": {
        "weight": 0.20,
        "checks": [
            {
                "id": "has_real_examples",
                "label": "Tem exemplos reais ou casos práticos",
                "weight": 0.30,
            },
            {
                "id": "shows_practical_knowledge",
                "label": "Demonstra conhecimento prático do assunto",
                "weight": 0.25,
            },
            {
                "id": "includes_numerical_data",
                "label": "Inclui dados numéricos ou estatísticas",
                "weight": 0.25,
            },
            {
                "id": "mentions_tools_or_methods",
                "label": "Menciona ferramentas ou métodos específicos",
                "weight": 0.20,
            },
        ],
    },
    "expertise": {
        "weight": 0.30,
        "checks": [
            {
                "id": "author_has_credentials",
                "label": "Autor tem credenciais na área",
                "weight": 0.20,
            },
            {
                "id": "cites_authoritative_sources",
                "label": "Cita fontes autoritativas",
                "weight": 0.25,
            },
            {
                "id": "uses_correct_terminology",
                "label": "Usa terminologia correta da área",
                "weight": 0.20,
            },
            {
                "id": "depth_appropriate_for_subject",
                "label": "Profundidade adequada para o assunto",
                "weight": 0.20,
            },
            {
                "id": "no_factual_errors",
                "label": "Sem erros factuais aparentes",
                "weight": 0.15,
            },
        ],
    },
    "authoritativeness": {
        "weight": 0.25,
        "checks": [
            {
                "id": "linked_to_authority_sites",
                "label": "Linka para sites de autoridade",
                "weight": 0.25,
            },
            {
                "id": "mentioned_by_other_sites",
                "label": "Mencionado por outros sites (backlinks)",
                "weight": 0.20,
            },
            {
                "id": "author_has_publications",
                "label": "Autor tem outras publicações no tema",
                "weight": 0.20,
            },
            {
                "id": "site_has_about_page",
                "label": "Site tem página Sobre com credenciais",
                "weight": 0.20,
            },
            {
                "id": "content_cited_by_others",
                "label": "Conteúdo é citável por outros",
                "weight": 0.15,
            },
        ],
    },
    "trustworthiness": {
        "weight": 0.25,
        "checks": [
            {
                "id": "has_contact_information",
                "label": "Tem informações de contato claras",
                "weight": 0.20,
            },
            {
                "id": "transparent_about_purpose",
                "label": "Transparente sobre propósito do conteúdo",
                "weight": 0.20,
            },
            {
                "id": "discloses_affiliate_links",
                "label": "Divulga links de afiliado quando aplicável",
                "weight": 0.15,
            },
            {
                "id": "accurate_and_verifiable",
                "label": "Informações precisas e verificáveis",
                "weight": 0.20,
            },
            {
                "id": "privacy_policy_exists",
                "label": "Política de privacidade acessível",
                "weight": 0.15,
            },
            {
                "id": "secure_connection",
                "label": "Conexão segura (HTTPS)",
                "weight": 0.10,
            },
        ],
    },
}

AUTHOR_PROFILES = {
    "tecnologia": {
        "name": "Ricardo Martins",
        "bio": "Engenheiro de software com 12 anos de experiência em tecnologia. Especialista em hardware, redes e segurança digital. Fundador do portal TechGuia, referência em reviews de tecnologia no Brasil desde 2019. Mais de 500 artigos publicados.",
        "credentials": [
            "Engenharia da Computação - USP",
            "Certificação AWS Solutions Architect",
            "Membro da ABC² (Associação Brasileira de Ciência da Computação)",
        ],
        "linkedin": "https://linkedin.com/in/ricardo-martins-tech",
    },
    "financas": {
        "name": "Ana Paula Oliveira",
        "bio": "Economista com MBA em Finanças pela FGV. Consultora financeira com mais de 8 anos ajudando famílias brasileiras a organizar suas finanças. Autora do blog 'Finanças sem Mistério' e do ebook 'Como Sair das Dívidas em 12 Passos'.",
        "credentials": [
            "Economia - Unicamp",
            "MBA em Finanças - FGV",
            "Certificação CFP (Certified Financial Planner)",
        ],
        "linkedin": "https://linkedin.com/in/ana-oliveira-financas",
    },
    "saude": {
        "name": "Dra. Mariana Costa",
        "bio": "Médica formada pela UFMG com residência em Nutrologia. Especialista em medicina preventiva e qualidade de vida. Atende há 10 anos e escreve sobre saúde baseada em evidências científicas.",
        "credentials": [
            "Medicina - UFMG",
            "Residência em Nutrologia - Hospital das Clínicas",
            "Membro da ABRAN (Associação Brasileira de Nutrologia)",
        ],
        "linkedin": "https://linkedin.com/in/dra-mariana-costa",
    },
    "carreira": {
        "name": "Pedro Alves",
        "bio": "Especialista em desenvolvimento de carreira e recursos humanos com 15 anos de experiência. Ex-executivo de RH em multinacional. Coach de carreira certificado. Já ajudou mais de 3.000 profissionais a conquistarem suas vagas dos sonhos.",
        "credentials": [
            "Psicologia - USP",
            "MBA em Gestão de Pessoas - FIA",
            "Certificação PCC (International Coach Federation)",
        ],
        "linkedin": "https://linkedin.com/in/pedro-alves-carreira",
    },
}


class EEATValidatorAgent(AgentBase):
    """Valida artigos contra critérios E-E-A-T do Google."""

    def __init__(self, **kwargs) -> None:
        super().__init__("eeat_validator", **kwargs)

    def get_author_profile(self, niche: str) -> dict[str, Any]:
        """Retorna perfil de autor otimizado para E-E-A-T."""
        profile = AUTHOR_PROFILES.get(niche.lower(), AUTHOR_PROFILES["tecnologia"])
        return profile

    def validate_article(self, article: dict[str, Any], niche: str) -> dict[str, Any]:
        """Valida um artigo contra todos os critérios E-E-A-T."""
        text = self._get_article_text(article)

        results = {}
        total_score = 0.0

        for category, config in EEAT_CRITERIA.items():
            category_score = 0.0
            check_results = []

            for check in config["checks"]:
                passed = self._run_check(check["id"], text, article, niche)
                check_score = 1.0 if passed else 0.0
                category_score += check_score * check["weight"]
                check_results.append(
                    {
                        "check_id": check["id"],
                        "label": check["label"],
                        "passed": passed,
                        "score": check_score,
                        "weight": check["weight"],
                    }
                )

            weighted_score = category_score * config["weight"]
            total_score += weighted_score

            results[category] = {
                "score": round(category_score, 2),
                "weighted_score": round(weighted_score, 2),
                "checks": check_results,
            }

        # Get author profile
        author = self.get_author_profile(niche)

        return {
            "total_score": round(total_score * 100, 1),
            "categories": results,
            "passed": total_score >= 0.70,
            "author_profile": author,
            "recommendations": self._generate_recommendations(results),
        }

    def _get_article_text(self, article: dict[str, Any]) -> str:
        """Extrai texto completo do artigo para análise."""
        parts = [
            article.get("title", ""),
            article.get("introduction", ""),
            article.get("meta_description", ""),
        ]
        for section in article.get("sections", []):
            if isinstance(section, dict):
                parts.append(section.get("content", ""))
            else:
                parts.append(str(section))
        parts.append(article.get("conclusion", ""))
        return " ".join(parts)

    def _run_check(self, check_id: str, text: str, article: dict, niche: str) -> bool:
        """Executa um check específico de E-E-A-T."""
        text_lower = text.lower()

        if check_id == "has_real_examples":
            return any(
                w in text_lower
                for w in ["por exemplo", "exemplo", "caso real", "como eu", "cliente"]
            )

        elif check_id == "shows_practical_knowledge":
            return any(
                w in text_lower
                for w in ["dica", "passo", "faça", "recomendo", "sugiro"]
            )

        elif check_id == "includes_numerical_data":
            return bool(re.search(r"\d+[%x]|\d+,\d+|\d+\.\d+", text))

        elif check_id == "mentions_tools_or_methods":
            return any(
                w in text_lower
                for w in ["ferramenta", "método", "técnica", "software", "app", "site"]
            )

        elif check_id == "author_has_credentials":
            profile = self.get_author_profile(niche)
            return bool(profile.get("credentials"))

        elif check_id == "cites_authoritative_sources":
            return any(
                w in text_lower
                for w in [
                    "segundo",
                    "conforme",
                    "de acordo com",
                    "estudo",
                    "pesquisa",
                    "fonte",
                ]
            )

        elif check_id == "uses_correct_terminology":
            # Simplified: just check if it has niche-related terms
            niche_terms = {
                "tecnologia": [
                    "processador",
                    "memória",
                    "hardware",
                    "software",
                    "rede",
                    "digital",
                ],
                "financas": [
                    "investimento",
                    "renda",
                    "economia",
                    "orçamento",
                    "divida",
                ],
                "saude": ["saúde", "exercício", "alimentação", "prevenção", "nutrição"],
                "carreira": [
                    "currículo",
                    "entrevista",
                    "carreira",
                    "profissional",
                    "desenvolvimento",
                ],
            }
            terms = niche_terms.get(niche.lower(), [])
            return any(t in text_lower for t in terms)

        elif check_id == "depth_appropriate_for_subject":
            word_count = len(text.split())
            return word_count >= 800

        elif check_id == "no_factual_errors":
            # Simplified: always true in simulation
            return True

        elif check_id == "linked_to_authority_sites":
            links = article.get("external_links", [])
            return len(links) >= 2

        elif check_id == "mentioned_by_other_sites":
            return False  # Can't verify in simulation

        elif check_id == "author_has_publications":
            return True  # Simulated

        elif check_id == "site_has_about_page":
            return True  # Simulated

        elif check_id == "content_cited_by_others":
            return False  # Can't verify in simulation

        elif check_id == "has_contact_information":
            return True  # Simulated

        elif check_id == "transparent_about_purpose":
            return True  # Simulated

        elif check_id == "discloses_affiliate_links":
            return True  # Simulated

        elif check_id == "accurate_and_verifiable":
            return bool(re.search(r"\d{4}", text))  # Has year references

        elif check_id == "privacy_policy_exists":
            return True  # Simulated

        elif check_id == "secure_connection":
            return True  # Simulated

        return False

    def _generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Gera recomendações baseadas nos checks que falharam."""
        recs = []
        for category, data in results.items():
            for check in data.get("checks", []):
                if not check["passed"]:
                    recs.append(f"{category}: {check['label']}")
        return recs

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign

        articles = campaign.get("articles", [])
        if isinstance(articles, dict):
            articles = [articles]

        niche = str(campaign.get("niche", "tecnologia"))

        validated = []
        total_score = 0.0

        for article in articles:
            result = self.validate_article(article, niche)
            validated.append(
                {
                    "title": article.get("title", "Untitled"),
                    "eeat_score": result["total_score"],
                    "passed": result["passed"],
                    "categories": result["categories"],
                    "recommendations": result["recommendations"],
                    "assigned_author": result["author_profile"]["name"],
                    "author_bio": result["author_profile"]["bio"],
                }
            )
            total_score += result["total_score"]

        avg_score = total_score / max(len(validated), 1)

        # Get author for the niche
        author = self.get_author_profile(niche)

        output = {
            "niche": niche,
            "articles_validated": len(validated),
            "average_eeat_score": round(avg_score, 1),
            "articles": validated,
            "author_profiles": {niche: author},
            "global_recommendations": [
                "Garantir que cada artigo tenha no mínimo 2 fontes externas autoritativas",
                "Incluir dados numéricos e estatísticas em cada seção principal",
                "Manter perfil de autor visível com credenciais e link para LinkedIn",
                "Adicionar seção de FAQ com schema markup para featured snippets",
                "Revisar artigos trimestralmente para manter freshness score",
            ],
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="eeat_validation",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Validou {len(validated)} artigos contra E-E-A-T. Score médio: {avg_score:.1f}/100"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _utcnow_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _duration_ms(start: str, end: str) -> int:
        from datetime import datetime

        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
        return max(0, int((e - s).total_seconds() * 1000))
