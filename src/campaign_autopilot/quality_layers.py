"""Quality Layers — Output Critic, Multi-Agent Debate, Benchmark DB, Campaign RAG,
CIA Governance, ELO Ranking.

AG-Kit Evolution Phase 21+ quality architecture.
Zero new dependencies (stdlib + SQLite).
Ponytail: compact modules, single file, reusable patterns.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable


# ═══════════════════════════════════════════════════════════════
# LAYER 1 — OUTPUT CRITIC
# ═══════════════════════════════════════════════════════════════


class Criterion(Enum):
    CLARITY = "clarity"
    ORIGINALITY = "originality"
    EXECUTION = "execution"
    BUSINESS_VALUE = "business_value"
    CONSISTENCY = "consistency"
    SEO_QUALITY = "seo_quality"
    CONVERSION = "conversion"
    BRAND_ALIGNMENT = "brand_alignment"


@dataclass
class CriticScore:
    """Score from a single criterion evaluation."""

    criterion: Criterion
    score: float  # 0-100
    reasoning: str = ""
    suggestions: list[str] = field(default_factory=list)


@dataclass
class CriticVerdict:
    """Complete critic evaluation of an artifact."""

    artifact_id: str
    artifact_type: str  # "landing_page", "email", "article", "image", "video", "ad"
    scores: dict[str, float]  # criterion_name -> score
    overall: float  # 0-100 weighted
    passed: bool
    reasoning: str
    suggestions: list[str] = field(default_factory=list)
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


class OutputCritic:
    """Evaluates artifacts against quality criteria.

    Threshold: artifacts below 85 are rejected and flagged for regeneration.

    Ponytail: uses simple heuristic scoring (no LLM dependency).
    Can be upgraded to LLM-based scoring when available.
    """

    PASS_THRESHOLD = 85

    # Weights per criterion (must sum to 1.0)
    WEIGHTS: dict[Criterion, float] = {
        Criterion.CLARITY: 0.20,
        Criterion.ORIGINALITY: 0.15,
        Criterion.EXECUTION: 0.20,
        Criterion.BUSINESS_VALUE: 0.20,
        Criterion.CONSISTENCY: 0.15,
        Criterion.SEO_QUALITY: 0.10,
    }

    # Minimum criteria that must be evaluated for each type
    REQUIRED_CRITERIA: dict[str, list[Criterion]] = {
        "landing_page": [
            Criterion.CLARITY,
            Criterion.EXECUTION,
            Criterion.BUSINESS_VALUE,
            Criterion.CONSISTENCY,
        ],
        "email": [
            Criterion.CLARITY,
            Criterion.CONSISTENCY,
            Criterion.CONVERSION,
        ],
        "article": [
            Criterion.CLARITY,
            Criterion.ORIGINALITY,
            Criterion.SEO_QUALITY,
            Criterion.CONSISTENCY,
        ],
        "image": [
            Criterion.CLARITY,
            Criterion.ORIGINALITY,
            Criterion.BRAND_ALIGNMENT,
        ],
        "ad": [
            Criterion.CLARITY,
            Criterion.CONVERSION,
            Criterion.BUSINESS_VALUE,
            Criterion.BRAND_ALIGNMENT,
        ],
    }

    def __init__(self, threshold: float = PASS_THRESHOLD):
        self.threshold = threshold
        self._results: list[CriticVerdict] = []

    def evaluate(
        self,
        artifact_id: str,
        artifact_type: str,
        content: str,
        context: dict[str, Any] | None = None,
    ) -> CriticVerdict:
        """Evaluate an artifact against quality criteria.

        Scoring is heuristic-based (length, structure, keywords).
        In production, upgrade to use LLM-based evaluation.
        """
        context = context or {}
        scores: dict[str, float] = {}
        suggestions: list[str] = []

        content_len = len(content)
        words = content.split()
        word_count = len(words)
        has_heading = any(marker in content for marker in ["<h1", "<h2", "# ", "## "])
        has_cta = any(
            marker in content.lower()
            for marker in [
                "compre",
                "inscreva",
                "saiba mais",
                "clique",
                "button",
                "cta",
                "comece",
                "gratis",
                "oferta",
            ]
        )
        has_link = "href=" in content or "http" in content
        lines = content.split("\n")
        has_images = "img src" in content or "![image]" in content

        # ── CLARITY ──
        clarity = 70.0
        if word_count >= 50:
            clarity = 85.0
        if has_heading:
            clarity += 5
        if word_count > 200:
            clarity += 5
        if word_count > 500:
            clarity += 3
        if word_count > 800:
            clarity += 2
        if has_images:
            clarity += 3
        if content.count("\n") > 10:
            clarity += 2  # structured with multiple paragraphs
        scores["clarity"] = min(100, max(0, clarity))
        if word_count < 30:
            suggestions.append(
                "Conteúdo muito curto — expanda para pelo menos 50 palavras"
            )

        # ── ORIGINALITY ──
        originality = 75.0
        if word_count >= 100:
            originality = 85.0
        if has_heading and has_cta:
            originality += 5
        if word_count > 300:
            originality += 5
        if has_images:
            originality += 3
        if content.count("<h2") > 2:
            originality += 2
        scores["originality"] = min(100, max(0, originality))

        # ── EXECUTION ──
        execution = 70.0
        if has_heading:
            execution += 10
        if has_cta:
            execution += 10
        if has_link:
            execution += 5
        if has_images:
            execution += 5
        scores["execution"] = min(100, execution)
        if not has_cta:
            suggestions.append("Adicione um CTA claro (call-to-action)")
        if not has_heading:
            suggestions.append("Adicione headings estruturados")

        # ── BUSINESS VALUE ──
        biz_value = 70.0
        value_signals = [
            "oferta",
            "desconto",
            "resultado",
            "transformar",
            "aprender",
            "lucro",
            "dinheiro",
            "crescer",
        ]
        signal_count = sum(1 for s in value_signals if s in content.lower())
        biz_value += signal_count * 5
        if has_cta:
            biz_value += 10
        scores["business_value"] = min(100, biz_value)
        if signal_count == 0:
            suggestions.append("Adicione termos de valor/benefício")

        # ── CONSISTENCY ──
        consistency = 80.0
        if has_heading:
            consistency += 5
        # Check length consistency (not too short, not too long)
        if 100 <= word_count <= 2000:
            consistency += 5
        if word_count > 300:
            consistency += 5
        if has_cta and has_images:
            consistency += 5
        scores["consistency"] = min(100, max(0, consistency))

        # ── SEO QUALITY (if applicable) ──
        if "article" in artifact_type or "landing" in artifact_type:
            seo = 65.0
            if word_count >= 300:
                seo = 85.0
            if has_heading:
                seo += 5
            if has_link:
                seo += 5
            if has_images:
                seo += 3
            if word_count > 500:
                seo += 2
            scores["seo_quality"] = min(100, max(0, seo))

        # ── CONVERSION (if applicable) ──
        if artifact_type in ("email", "ad", "landing_page"):
            conversion = 65.0
            if has_cta:
                conversion += 15
            if has_link:
                conversion += 10
            scores["conversion"] = min(100, conversion)

        # ── BRAND ALIGNMENT (if applicable) ──
        if artifact_type in ("image", "ad", "landing_page"):
            brand = 80.0
            brand_signals = ["lyzer", "labs", "campaign", "autopilot"]
            if any(s in content.lower() for s in brand_signals):
                brand += 10
            scores["brand_alignment"] = min(100, brand)

        # ── Compute weighted overall score ──
        total_weight = 0.0
        weighted_sum = 0.0
        for criterion, weight in self.WEIGHTS.items():
            key = criterion.value
            if key in scores:
                weighted_sum += scores[key] * weight
                total_weight += weight

        overall = (
            round(weighted_sum / max(0.001, total_weight), 1)
            if total_weight > 0
            else 0.0
        )
        passed = overall >= self.threshold
        reasoning_msg = f"Artifact scores {overall:.1f}/{self.threshold} threshold. Passed: {'yes' if passed else 'no'}."

        # Ponytail-approved hybrid check: query LLM dynamically for semantic analysis
        # if the score is in the gray zone (70 to 90) to prevent false positives/negatives.
        if 70.0 <= overall <= 90.0:
            try:
                from .media_providers import TextProvider
                provider = TextProvider.best()
                if provider.name() not in ("stdlib", "fallback", "stdlib_fallback"):
                    prompt = (
                        f"Você é um especialista em garantia de qualidade de marketing.\n"
                        f"Analise o seguinte conteúdo do tipo '{artifact_type}':\n\n"
                        f"--- CONTEÚDO ---\n{content}\n\n"
                        f"Forneça uma nota de 0 a 100 baseada na clareza, originalidade e alinhamento.\n"
                        f"Responda EXCLUSIVAMENTE com um JSON no formato:\n"
                        f'{{"score": 85, "reason": "motivo", "suggestions": ["sugestão 1"]}}'
                    )
                    llm_resp = provider.generate(prompt, max_tokens=256)
                    if llm_resp:
                        import re
                        match = re.search(r'\{.*\}', llm_resp.strip(), re.DOTALL)
                        if match:
                            data = json.loads(match.group(0))
                            llm_score = float(data.get("score", overall))
                            reason = data.get("reason", "")
                            llm_suggs = data.get("suggestions", [])
                            
                            overall = round((overall + llm_score) / 2.0, 1)
                            passed = overall >= self.threshold
                            reasoning_msg = (
                                f"Artifact scores {overall:.1f}/{self.threshold} threshold (Hybrid). "
                                f"Passed: {'yes' if passed else 'no'}. LLM Review: {reason}"
                            )
                            suggestions.extend(llm_suggs)
            except Exception:
                pass

        verdict = CriticVerdict(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            scores=scores,
            overall=overall,
            passed=passed,
            reasoning=reasoning_msg,
            suggestions=suggestions,
        )
        self._results.append(verdict)
        return verdict

    def last_results(self, n: int = 10) -> list[CriticVerdict]:
        return self._results[-n:]

    def approval_rate(self) -> float:
        if not self._results:
            return 0.0
        return sum(1 for r in self._results if r.passed) / len(self._results) * 100


# ═══════════════════════════════════════════════════════════════
# LAYER 2 — MULTI-AGENT DEBATE
# ═══════════════════════════════════════════════════════════════


@dataclass
class DebateRound:
    """A single round of multi-agent debate."""

    round_id: str
    topic: str
    perspectives: dict[str, dict[str, Any]]  # agent_name -> output
    synthesis: dict[str, Any] | None = None
    final_score: float = 0.0
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class DebateOrchestrator:
    """Runs multiple agents on the same topic, then synthesizes.

    Pattern: Designer + Marketer + Researcher + Conversion Agent
    → Each produces a view
    → Synthesis Agent consolidates
    → Final output has reduced single-perspective bias
    """

    def __init__(self):
        self._rounds: list[DebateRound] = []
        self._lock = threading.Lock()

    def run_debate(
        self,
        topic: str,
        agents: dict[str, Callable[[str], dict[str, Any]]],
    ) -> DebateRound:
        """Run a multi-agent debate.

        Args:
            topic: The topic/problem to debate
            agents: name -> callable(topic) -> output dict

        Returns:
            DebateRound with all perspectives + synthesis
        """
        round_id = str(uuid.uuid4())[:8]
        perspectives: dict[str, dict[str, Any]] = {}

        for name, agent_fn in agents.items():
            try:
                result = agent_fn(topic)
                perspectives[name] = self._normalize_output(result)
            except Exception as e:
                perspectives[name] = {"error": str(e), "status": "failed"}

        # Synthesis: combine perspectives
        synthesis = self._synthesize(perspectives, topic)

        # Score: based on consensus strength
        successful = [p for p in perspectives.values() if "error" not in p]
        consensus_ratio = len(successful) / max(1, len(perspectives))
        final_score = round(consensus_ratio * 100, 1)

        round_result = DebateRound(
            round_id=round_id,
            topic=topic,
            perspectives=perspectives,
            synthesis=synthesis,
            final_score=final_score,
        )

        with self._lock:
            self._rounds.append(round_result)

        return round_result

    def _normalize_output(self, output: Any) -> dict[str, Any]:
        if isinstance(output, dict):
            return output
        return {"output": str(output)}

    def _synthesize(self, perspectives: dict[str, dict], topic: str) -> dict[str, Any]:
        """Combine multiple perspectives into a consolidated view."""
        all_points: list[str] = []
        agreements: list[str] = []
        disagreements: list[str] = []

        for name, view in perspectives.items():
            if "error" in view:
                continue
            content = str(view.get("output", view.get("content", str(view))))
            if content:
                all_points.append(f"{name}: {content[:200]}")

        return {
            "topic": topic,
            "agents_contributing": len(all_points),
            "total_agents": len(perspectives),
            "summary": f"Synthesized {len(all_points)} perspectives",
            "details": all_points[:5],
        }

    def recent_rounds(self, n: int = 5) -> list[DebateRound]:
        return self._rounds[-n:]


# ═══════════════════════════════════════════════════════════════
# LAYER 3 — BENCHMARK DATABASE
# ═══════════════════════════════════════════════════════════════


class BenchmarkDB:
    """Stores approved outputs with scores for learning.

    Only outputs scoring above threshold are stored.
    The system learns its own winning patterns.
    """

    def __init__(self, db_path: str = ".state/benchmark.db"):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._lock = threading.Lock()
        self._ensure_schema()

    def _ensure_schema(self):
        with self._lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS approved_outputs (
                    id TEXT PRIMARY KEY,
                    artifact_type TEXT NOT NULL,
                    score REAL NOT NULL,
                    content_summary TEXT,
                    campaign_type TEXT,
                    why_it_worked TEXT,
                    metadata TEXT,
                    created_at REAL NOT NULL
                )
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_approved_type
                ON approved_outputs(artifact_type)
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_approved_score
                ON approved_outputs(score DESC)
            """)
            self._conn.commit()

    def record(
        self,
        artifact_type: str,
        score: float,
        verdict: CriticVerdict,
        campaign_type: str = "",
        why_it_worked: str = "",
    ) -> str:
        """Record an approved output."""
        record_id = str(uuid.uuid4())[:8]
        with self._lock:
            self._conn.execute(
                "INSERT INTO approved_outputs (id, artifact_type, score, "
                "content_summary, campaign_type, why_it_worked, metadata, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record_id,
                    artifact_type,
                    score,
                    verdict.reasoning[:200],
                    campaign_type,
                    why_it_worked,
                    json.dumps(verdict.to_dict()),
                    time.time(),
                ),
            )
            self._conn.commit()
        return record_id

    def top_outputs(
        self, artifact_type: str = "", limit: int = 20
    ) -> list[dict[str, Any]]:
        """Get top-scoring approved outputs."""
        import sqlite3

        with self._lock:
            self._conn.row_factory = sqlite3.Row
            if artifact_type:
                rows = self._conn.execute(
                    "SELECT * FROM approved_outputs WHERE artifact_type=? "
                    "ORDER BY score DESC LIMIT ?",
                    (artifact_type, limit),
                ).fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT * FROM approved_outputs ORDER BY score DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            self._conn.row_factory = None
        return [dict(r) for r in rows]

    def count(self) -> int:
        with self._lock:
            return self._conn.execute(
                "SELECT COUNT(*) FROM approved_outputs"
            ).fetchone()[0]

    def stats(self) -> dict[str, Any]:
        with self._lock:
            total = self._conn.execute(
                "SELECT COUNT(*) FROM approved_outputs"
            ).fetchone()[0]
            avg = (
                self._conn.execute(
                    "SELECT AVG(score) FROM approved_outputs"
                ).fetchone()[0]
                or 0.0
            )
            import sqlite3

            self._conn.row_factory = sqlite3.Row
            by_type = self._conn.execute(
                "SELECT artifact_type, COUNT(*), AVG(score) "
                "FROM approved_outputs GROUP BY artifact_type"
            ).fetchall()
            self._conn.row_factory = None
        return {
            "total": total,
            "avg_score": round(avg, 1),
            "by_type": [
                {"type": r[0], "count": r[1], "avg_score": round(r[2], 1)}
                for r in by_type
            ],
        }


# ═══════════════════════════════════════════════════════════════
# LAYER 4 — CAMPAIGN RAG (SQLite-based)
# ═══════════════════════════════════════════════════════════════


class CampaignKnowledge:
    """Retrieval-Augmented Generation for campaigns.

    SQLite-based (no vector DB needed — ponytail).
    Uses keyword matching + tag-based retrieval.
    """

    def __init__(self, db_path: str = ".state/campaign_knowledge.db"):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._lock = threading.Lock()
        self._ensure_schema()

    def _ensure_schema(self):
        with self._lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    content TEXT,
                    tags TEXT,
                    source TEXT,
                    score REAL DEFAULT 0,
                    created_at REAL NOT NULL
                )
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_tags
                ON knowledge_entries(content_type)
            """)
            self._conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts
                USING fts5(title, content, tags)
            """)
            self._conn.commit()

    def add(
        self,
        title: str,
        content_type: str,
        content: str,
        tags: list[str] | None = None,
        source: str = "",
        score: float = 0.0,
    ) -> str:
        """Add a knowledge entry."""
        entry_id = str(uuid.uuid4())[:8]
        tags_str = " ".join(tags or [])
        with self._lock:
            self._conn.execute(
                "INSERT INTO knowledge_entries "
                "(id, title, content_type, content, tags, source, score, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    entry_id,
                    title,
                    content_type,
                    content[:2000],
                    tags_str,
                    source,
                    score,
                    time.time(),
                ),
            )
            try:
                self._conn.execute(
                    "INSERT INTO knowledge_fts (rowid, title, content, tags) "
                    "VALUES (?, ?, ?, ?)",
                    (
                        self._conn.execute(
                            "SELECT rowid FROM knowledge_entries WHERE id=?",
                            (entry_id,),
                        ).fetchone()[0],
                        title,
                        content[:2000],
                        tags_str,
                    ),
                )
            except Exception:
                pass  # FTS might not be available
            self._conn.commit()
        return entry_id

    def retrieve(
        self, query: str, content_type: str = "", limit: int = 5
    ) -> list[dict[str, Any]]:
        """Retrieve relevant entries by keyword matching."""
        keywords = query.lower().split()[:5]
        conditions = " OR ".join(
            f"(title LIKE '%{k}%' OR content LIKE '%{k}%' OR tags LIKE '%{k}%')"
            for k in keywords
        )
        with self._lock:
            try:
                # Try FTS first
                import sqlite3

                self._conn.row_factory = sqlite3.Row
                fts_query = " OR ".join(keywords)
                rows = self._conn.execute(
                    "SELECT ke.* FROM knowledge_fts kf "
                    "JOIN knowledge_entries ke ON ke.id = ("
                    "SELECT id FROM knowledge_entries WHERE rowid=kf.rowid"
                    ") WHERE kf.content MATCH ? "
                    "ORDER BY ke.score DESC LIMIT ?",
                    (fts_query, limit),
                ).fetchall()
                self._conn.row_factory = None
                if rows:
                    return [dict(r) for r in rows]
            except Exception:
                self._conn.row_factory = None
                pass

            # Fallback: LIKE matching
            import sqlite3

            self._conn.row_factory = sqlite3.Row
            sql = f"SELECT * FROM knowledge_entries WHERE {conditions}"
            if content_type:
                sql += f" AND content_type='{content_type}'"
            sql += " ORDER BY score DESC, created_at DESC LIMIT ?"
            rows = self._conn.execute(sql, (limit,)).fetchall()
            self._conn.row_factory = None

        return [dict(r) for r in rows]

    def count(self) -> int:
        with self._lock:
            return self._conn.execute(
                "SELECT COUNT(*) FROM knowledge_entries"
            ).fetchone()[0]


# ═══════════════════════════════════════════════════════════════
# LAYER 5 — CIA GOVERNANCE (Truth, Risk, Consistency)
# ═══════════════════════════════════════════════════════════════


class TruthAgent:
    """Detects hallucinations, contradictions, unsupported claims."""

    def verify(self, content: str) -> dict[str, Any]:
        issues: list[str] = []
        warnings: list[str] = []

        # Check for unsupported absolute claims
        absolutes = ["sempre", "nunca", "todos", "ninguém", "100%", "garantido"]
        for a in absolutes:
            if a in content.lower():
                warnings.append(f"Afirmação absoluta: '{a}'")

        # Check for missing evidence markers
        evidence_markers = ["segundo", "de acordo com", "pesquisa", "estudo", "dados"]
        has_evidence = any(m in content.lower() for m in evidence_markers)
        if not has_evidence and len(content) > 500:
            warnings.append("Sem referências ou evidências citadas")

        # Check for conflicting statements (naive heuristic)
        sentences = [s.strip() for s in content.split(".") if len(s.strip()) > 20]
        for i, s1 in enumerate(sentences):
            for s2 in sentences[i + 1 :]:
                # Simple contradiction detection
                if any(neg in s1.lower() for neg in ["não", "nunca"]):
                    if any(pos in s2.lower() for pos in ["é sim", "sempre foi"]):
                        issues.append("Possível contradição entre sentenças")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": max(0, 100 - len(issues) * 30 - len(warnings) * 10),
        }


class RiskAgent:
    """Assesses strategic and operational risks."""

    def assess(self, campaign: dict[str, Any]) -> dict[str, Any]:
        risks: list[dict] = []
        risk_score = 0

        # Check for common campaign risks
        niche = campaign.get("niche") or campaign.get("campaign", {}).get("niche", "")
        if not niche:
            risks.append(
                {
                    "type": "missing_niche",
                    "severity": "high",
                    "detail": "Nicho não definido",
                }
            )
            risk_score += 30

        goal = campaign.get("goal", "")
        if not goal:
            risks.append(
                {
                    "type": "missing_goal",
                    "severity": "high",
                    "detail": "Objetivo não definido",
                }
            )
            risk_score += 25

        # Check for single-point-of-failure (single affiliate platform)
        offers = campaign.get("artifacts", {}).get("offers", [])
        if len(offers) <= 1:
            risks.append(
                {
                    "type": "single_platform_dependency",
                    "severity": "medium",
                    "detail": "Dependência de única fonte de receita",
                    "suggestion": "Adicione mais plataformas de afiliados",
                }
            )
            risk_score += 15

        return {
            "risk_score": min(100, risk_score),
            "risks": risks,
            "safe": risk_score < 40,
            "recommendations": [
                r.get("suggestion", "") for r in risks if "suggestion" in r
            ],
        }


class ConsistencyAgent:
    """Verifies brand and strategy consistency across artifacts."""

    BRAND_SIGNALS = ["lyzer", "campaign", "autopilot", "digital", "marketing"]

    def check_brand(self, content: str) -> dict[str, Any]:
        found = [s for s in self.BRAND_SIGNALS if s in content.lower()]
        return {
            "brand_alignment": round(len(found) / len(self.BRAND_SIGNALS) * 100, 1),
            "brand_signals_found": found,
            "suggestion": "Adicione elementos de marca" if len(found) < 2 else "",
        }

    def check_consistency(self, artifacts: list[dict]) -> dict[str, Any]:
        """Check consistency across multiple artifacts."""
        if len(artifacts) < 2:
            return {"consistent": True, "note": "Apenas 1 artefato para comparar"}

        issues = []
        tones = []
        for a in artifacts:
            content = (a.get("content") or a.get("output", "") or str(a)).lower()
            # Detect tone
            formal_words = ["portanto", "entretanto", "consequentemente", "mediante"]
            casual_words = ["vamos", "bora", "olha", "então", "galera"]
            formal = sum(1 for w in formal_words if w in content)
            casual = sum(1 for w in casual_words if w in content)
            tone = (
                "formal"
                if formal > casual
                else "casual"
                if casual > formal
                else "neutral"
            )
            tones.append(tone)

        # Detect tone inconsistency
        if len(set(tones)) > 1:
            issues.append(f"Tom inconsistente entre artefatos: {set(tones)}")

        return {
            "consistent": len(issues) == 0,
            "issues": issues,
            "tones_found": tones,
        }


# ═══════════════════════════════════════════════════════════════
# LAYER 6 — RAG (Pre-Generation Retrieval)
# ═══════════════════════════════════════════════════════════════


class RAGEngine:
    """Retrieve → Reason → Generate pipeline.

    Before generating anything, retrieve similar successful artifacts,
    reason about their patterns, then generate with higher consistency.
    """

    def __init__(
        self,
        benchmark_db: BenchmarkDB | None = None,
        campaign_knowledge: CampaignKnowledge | None = None,
    ):
        self._benchmark = benchmark_db or BenchmarkDB()
        self._knowledge = campaign_knowledge or CampaignKnowledge()

    def retrieve_context(
        self, query: str, artifact_type: str = "", limit: int = 3
    ) -> dict[str, Any]:
        """Retrieve relevant context before generation."""
        # 1. Get top approved outputs of same type
        benchmarks = self._benchmark.top_outputs(
            artifact_type=artifact_type, limit=limit
        )

        # 2. Get knowledge entries
        knowledge = self._knowledge.retrieve(
            query=query, content_type=artifact_type, limit=limit
        )

        return {
            "benchmarks_count": len(benchmarks),
            "knowledge_count": len(knowledge),
            "benchmarks": [
                {
                    "score": b.get("score", 0),
                    "why_it_worked": b.get("why_it_worked", "")[:100],
                }
                for b in benchmarks
            ],
            "knowledge": [
                {"title": k.get("title", ""), "tags": k.get("tags", "")}
                for k in knowledge
            ],
            "context_available": len(benchmarks) > 0 or len(knowledge) > 0,
        }


# ═══════════════════════════════════════════════════════════════
# LAYER 7 — ELO RANKING FOR SKILLS
# ═══════════════════════════════════════════════════════════════


class ELORanking:
    """ELO rating system for skills.

    Each skill has an ELO score.
    When two skills compete (same task), the winner gains ELO from the loser.
    Over time, the system learns which skills produce the best results.

    Base ELO: 1500
    K-factor: 32 (standard for rating periods)
    """

    BASE_ELO = 1500
    K_FACTOR = 32

    def __init__(self, db_path: str = ".state/elo_rankings.db"):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._lock = threading.Lock()
        self._ensure_schema()

    def _ensure_schema(self):
        with self._lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS elo_ratings (
                    skill_name TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    elo REAL NOT NULL DEFAULT 1500,
                    matches INTEGER NOT NULL DEFAULT 0,
                    wins INTEGER NOT NULL DEFAULT 0,
                    last_match REAL
                )
            """)
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS elo_matches (
                    match_id TEXT PRIMARY KEY,
                    skill_a TEXT NOT NULL,
                    skill_b TEXT NOT NULL,
                    winner TEXT NOT NULL,
                    context TEXT,
                    timestamp REAL NOT NULL
                )
            """)
            self._conn.commit()

    def get_rating(self, skill_name: str, category: str = "general") -> float:
        with self._lock:
            row = self._conn.execute(
                "SELECT elo FROM elo_ratings WHERE skill_name=?",
                (skill_name,),
            ).fetchone()
            if row:
                return row[0]
            # Create new entry
            self._conn.execute(
                "INSERT INTO elo_ratings (skill_name, category, elo) VALUES (?, ?, ?)",
                (skill_name, category, self.BASE_ELO),
            )
            self._conn.commit()
        return self.BASE_ELO

    def record_match(
        self, skill_a: str, skill_b: str, winner: str, context: str = ""
    ) -> tuple[float, float]:
        """Record a match between two skills.

        Args:
            skill_a: First skill name
            skill_b: Second skill name
            winner: 'a', 'b', or 'draw'
            context: What type of task was this

        Returns:
            (new_elo_a, new_elo_b)
        """
        cat = "general"
        rating_a = self.get_rating(skill_a, cat)
        rating_b = self.get_rating(skill_b, cat)

        # Expected scores
        expected_a = 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))
        expected_b = 1.0 - expected_a

        # Actual scores
        if winner == "a":
            actual_a, actual_b = 1.0, 0.0
        elif winner == "b":
            actual_a, actual_b = 0.0, 1.0
        else:  # draw
            actual_a, actual_b = 0.5, 0.5

        # New ratings
        new_a = rating_a + self.K_FACTOR * (actual_a - expected_a)
        new_b = rating_b + self.K_FACTOR * (actual_b - expected_b)

        now = time.time()
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO elo_ratings "
                "(skill_name, category, elo, matches, wins, last_match) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    skill_a,
                    cat,
                    new_a,
                    self._conn.execute(
                        "SELECT COALESCE(matches,0)+1 FROM elo_ratings WHERE skill_name=?",
                        (skill_a,),
                    ).fetchone()[0]
                    if self._conn.execute(
                        "SELECT COUNT(*) FROM elo_ratings WHERE skill_name=?",
                        (skill_a,),
                    ).fetchone()[0]
                    else 0,
                    self._conn.execute(
                        "SELECT COALESCE(wins,0)+? FROM elo_ratings WHERE skill_name=?",
                        (1 if winner == "a" else 0, skill_a),
                    ).fetchone()[0]
                    if self._conn.execute(
                        "SELECT COUNT(*) FROM elo_ratings WHERE skill_name=?",
                        (skill_a,),
                    ).fetchone()[0]
                    else 0,
                    now,
                ),
            )
            self._conn.commit()

        return round(new_a, 1), round(new_b, 1)

    def ranking(self, category: str = "", limit: int = 20) -> list[dict[str, Any]]:
        """Get ELO ranking."""
        with self._lock:
            if category:
                rows = self._conn.execute(
                    "SELECT skill_name, elo, matches, wins FROM elo_ratings "
                    "WHERE category=? ORDER BY elo DESC LIMIT ?",
                    (category, limit),
                ).fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT skill_name, elo, matches, wins FROM elo_ratings "
                    "ORDER BY elo DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [
            {"name": r[0], "elo": round(r[1], 1), "matches": r[2], "wins": r[3]}
            for r in rows
        ]
