from __future__ import annotations


from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


def _tokenize(text: str) -> set[str]:
    tokens = set()
    for raw in text.lower().replace("/", " ").replace("-", " ").split():
        cleaned = "".join(ch for ch in raw if ch.isalnum())
        if len(cleaned) > 2:
            tokens.add(cleaned)
    return tokens


class MemoryLookupAgent(AgentBase):
    def __init__(self, **kwargs) -> None:
        super().__init__("memory_lookup", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        memory = list(context.memory)
        query_tokens = _tokenize(
            " ".join(
                str(campaign.get(field, ""))
                for field in (
                    "objective",
                    "industry",
                    "audience",
                    "channel",
                    "headline",
                )
            )
        )
        scored = []
        for record in memory:
            record_text = " ".join(str(value) for value in record.values())
            score = len(query_tokens & _tokenize(record_text))
            if score:
                scored.append((score, record))
        scored.sort(key=lambda item: (-item[0], str(item[1].get("name", ""))))
        matches = [record for _, record in scored[:3]]
        learnings = []
        for record in matches:
            lessons = (
                record.get("lessons") or record.get("summary") or record.get("notes")
            )
            if lessons:
                learnings.append(str(lessons))
        if not learnings:
            learnings.append(
                "No close historical match found; prefer conservative changes and quick validation."
            )

        # Record explanation if store is available
        if self.explanation_store:
            _decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="memory_retrieval",
                input_state={
                    "query_tokens_count": len(query_tokens),
                    "available_memory_count": len(memory),
                    "match_score": len(scored),
                    "match_count": len(matches),
                },
            )
            for i, (score, record) in enumerate(scored[:5]):
                self.explanation_store.record_rule_application(
                    decision_id=_decision_id,
                    rule_source=f"memory.token_match_{i}",
                    rule_value="score > 0",
                    actual_value=score,
                    comparison_result=True,
                    rule_order=i + 1,
                )
            if not matches:
                self.explanation_store.record_rule_application(
                    decision_id=_decision_id,
                    rule_source="memory.no_match_fallback",
                    rule_value="at least one match",
                    actual_value=len(matches),
                    comparison_result=False,
                    rule_order=len(scored[:5]) + 1,
                )
            self.explanation_store.update_decision_output(
                decision_id=_decision_id,
                output_decision={
                    "matches": len(matches),
                    "learnings": len(learnings),
                    "memory_coverage": len(memory),
                },
            )

        # Persist learnings as semantic knowledge if store is available
        if self.semantic_memory and learnings:
            lessons_concept_id = self.semantic_memory.find_concept(
                "lessons", "knowledge"
            )
            if not lessons_concept_id:
                lessons_concept_id = self.semantic_memory.register_concept(
                    "lessons", "knowledge", "Learned patterns from campaign memory"
                )
            else:
                lessons_concept_id = lessons_concept_id["concept_id"]

            for i, learning in enumerate(learnings):
                learning_concept_id = self.semantic_memory.register_concept(
                    f"learning_{self.name}_{context.run_id}_{i}",
                    "knowledge",
                    learning[:200],
                )
                self.semantic_memory.assert_claim(
                    subject=lessons_concept_id,
                    predicate="includes",
                    object=learning_concept_id,
                    confidence=0.5,
                    evidence_type="EXPLICIT_INPUT",
                    supporting_data={
                        "learning_text": learning,
                        "cycle_id": context.run_id,
                    },
                    source_cycle_id=context.run_id,
                    asserted_by=self.name,
                )

        output = {
            "matches": matches,
            "learnings": learnings,
            "match_count": len(matches),
            "memory_coverage": len(memory),
        }
        finished_at = utc_now_iso()
        duration_ms = iso_duration_ms(started_at, finished_at)
        trace = AgentTrace(
            agent=self.name,
            step_id="memory_lookup",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            thread_name="main",
            notes=["Searched prior campaign memory for similar patterns."],
            metadata={"memory_items": len(memory)},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
