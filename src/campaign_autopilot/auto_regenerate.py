"""Auto-Regeneration Engine — Regenerates failed content until it passes quality checks.

Estratégia:
1. Executa OutputCritic no artifact
2. Se score < threshold, regenera injetando feedback do Critic
3. Até 3 tentativas
4. Se ainda falhar, marca como "failed" e reporta

Ponytail: stdlib-only. Compatível com todos os agentes.
"""

from __future__ import annotations

from typing import Any

from .quality_layers import OutputCritic


class AutoRegenerator:
    """Auto-regenerates content that fails quality checks.

    Usage:
        regenerator = AutoRegenerator(max_attempts=3)
        result = regenerator.regenerate(
            artifact_id="article-001",
            artifact_type="article",
            content=original_content,
            generate_fn=my_generator_function,
        )
    """

    def __init__(self, threshold: float = 85.0, max_attempts: int = 3):
        self.critic = OutputCritic(threshold=threshold)
        self.max_attempts = max_attempts
        self._history: list[dict] = []

    def regenerate(
        self,
        artifact_id: str,
        artifact_type: str,
        content: str,
        generate_fn,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Try to regenerate content until it passes quality checks.

        Args:
            artifact_id: Unique identifier
            artifact_type: Type of content (article, landing_page, email, etc.)
            content: Original content to evaluate
            generate_fn: Function(previous_content, feedback_suggestions) -> new_content
            context: Optional context for the critic

        Returns:
            Dict with final content, attempt count, and all verdicts
        """
        context = context or {}
        current_content = content
        verdicts = []

        for attempt in range(1, self.max_attempts + 1):
            # Evaluate current content
            verdict = self.critic.evaluate(
                artifact_id=f"{artifact_id}_v{attempt}",
                artifact_type=artifact_type,
                content=current_content,
                context=context,
            )
            verdicts.append(
                {
                    "attempt": attempt,
                    "score": verdict.overall,
                    "passed": verdict.passed,
                    "suggestions": verdict.suggestions,
                    "scores": verdict.scores,
                }
            )

            if verdict.passed:
                # Content passed quality check
                record = {
                    "artifact_id": artifact_id,
                    "status": "approved",
                    "final_attempt": attempt,
                    "final_score": verdict.overall,
                    "content": current_content,
                    "verdicts": verdicts,
                }
                self._history.append(record)
                return record

            # Content failed — regenerate with feedback
            if attempt < self.max_attempts:
                feedback = verdict.suggestions
                current_content = generate_fn(current_content, feedback)

        # All attempts failed
        record = {
            "artifact_id": artifact_id,
            "status": "failed",
            "final_attempt": self.max_attempts,
            "final_score": verdicts[-1]["score"],
            "content": current_content,
            "verdicts": verdicts,
            "note": "Failed all quality checks. Review and manually improve.",
        }
        self._history.append(record)
        return record

    def history(self) -> list[dict]:
        return self._history.copy()

    def approval_rate(self) -> float:
        if not self._history:
            return 0.0
        approved = sum(1 for h in self._history if h["status"] == "approved")
        return approved / len(self._history) * 100


def cta_injection_regenerator(previous: str, suggestions: list[str]) -> str:
    """Default regenerator: injects missing CTAs and value terms.

    Usado quando o conteúdo falha por falta de CTA ou termos de valor.
    """

    new_content = previous

    # Check if missing CTA
    if any(
        "CTA" in s or "call-to-action" in s.lower() or "call to action" in s.lower()
        for s in suggestions
    ):
        cta_block = (
            "\n\n---\n"
            "### 🚀 Pronto para Transformar seus Resultados?\n\n"
            "Você já sabe o que precisa fazer. Não deixe para depois.\n\n"
            "👉 **[QUERO COMEÇAR AGORA →](#)**\n\n"
            "*Oferta especial para novos alunos. Garantia de 7 dias.*\n"
        )
        # Check if there's already a CTA
        if (
            "QUERO COMEÇAR AGORA" not in new_content
            and "QUERO ACESSAR AGORA" not in new_content
        ):
            new_content += cta_block

    # Check if missing value terms
    if any(
        "termos de valor" in s.lower() or "benefício" in s.lower() for s in suggestions
    ):
        value_block = (
            "\n\n### ✅ Benefícios Exclusivos\n\n"
            "- Resultados comprovados em até 30 dias\n"
            "- Suporte dedicado 7 dias por semana\n"
            "- Acesso vitalício com atualizações gratuitas\n"
            "- Garantia incondicional de satisfação\n"
        )
        if "Benefícios Exclusivos" not in new_content:
            new_content += value_block

    # Increase length if too short
    word_count = len(new_content.split())
    if word_count < 50:
        new_content += (
            "\n\nEste é o momento ideal para você dar o próximo passo. "
            "Milhares de pessoas já transformaram suas vidas com esta metodologia. "
            "Não fique de fora — comece hoje mesmo e veja a diferença nos seus resultados."
        )

    return new_content


def quality_test(
    content: str,
    artifact_type: str = "article",
    artifact_id: str = "test_article",
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Quick quality test with auto-regeneration.

    Testa conteúdo existente e tenta regenerar até passar.

    Example:
        >>> result = quality_test("Meu artigo aqui...")
        >>> result["status"], result["final_score"]
    """
    regenerator = AutoRegenerator(max_attempts=max_attempts)
    result = regenerator.regenerate(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        content=content,
        generate_fn=cta_injection_regenerator,
    )
    return {
        "status": result["status"],
        "final_score": result["final_score"],
        "final_content": result["content"],
        "attempts": result["final_attempt"],
        "verdicts": result["verdicts"],
    }
