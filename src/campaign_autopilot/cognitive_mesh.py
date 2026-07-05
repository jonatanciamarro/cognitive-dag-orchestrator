"""Cognitive Mesh — AG-Kit Evolution Phase 15.

Agents share embeddings, traces, hypotheses, and beliefs directly
— without going through the orchestrator — via a shared pub/sub mesh.

Architecture shift:
  Before: Orchestrator → Agent A, B, C (hub-and-spoke)
  After:  Agent A ⟷ Agent B ⟷ Agent C (mesh, orchestrator observes only)

Core Components:
  - MessageBus: topic-based pub/sub for agent communication
  - HypothesisShare: agents publish hypotheses, others validate
  - BeliefPropagation: beliefs converge via weighted consensus
  - MeshAgent: agent that communicates via the mesh (optional, wraps AgentBase)
  - MeshOrchestrator: lightweight coordinator (observer, not controller)

Design Principles (Ponytail):
  - Zero new dependencies (stdlib only — threading, queue, collections)
  - Compatible with existing AgentBase — MeshAgent wraps, does NOT replace
  - Orchestrator can observe without controlling
  - Thread-safe, JSON-serializable messages
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable


# ── Types ─────────────────────────────────────────────────────


class MessagePriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class HypothesisStatus(Enum):
    PROPOSED = "proposed"
    TESTING = "testing"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"


# ── Message Formats ───────────────────────────────────────────


@dataclass
class MeshMessage:
    """A message sent between agents via the mesh."""

    message_id: str
    topic: str
    sender: str
    content: Any
    msg_type: str = "message"  # "message", "hypothesis", "belief", "trace", "embedding"
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = 0.0
    ttl_seconds: float = 3600.0  # auto-expire after this
    reply_to: str | None = None  # for request-response patterns
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()

    def expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl_seconds

    def to_dict(self) -> dict:
        d = asdict(self)
        d["priority"] = self.priority.value
        return d


@dataclass
class Hypothesis:
    """A hypothesis proposed by an agent for others to validate."""

    hypothesis_id: str
    proposer: str
    claim: str
    evidence: str = ""
    confidence: float = 0.5  # proposer's initial confidence
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    validations: list[dict] = field(
        default_factory=list
    )  # [{agent, agrees, confidence, reasoning}]
    timestamp: float = 0.0
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()

    def validate(
        self, agent_id: str, agrees: bool, confidence: float = 0.5, reasoning: str = ""
    ) -> None:
        """Record a validation from another agent."""
        self.validations.append(
            {
                "agent": agent_id,
                "agrees": agrees,
                "confidence": confidence,
                "reasoning": reasoning,
                "timestamp": time.time(),
            }
        )
        self._update_status()

    def _update_status(self) -> None:
        if len(self.validations) < 2:
            self.status = HypothesisStatus.TESTING
            return
        agrees = sum(1 for v in self.validations if v["agrees"])
        ratio = agrees / len(self.validations)
        total_conf = sum(v["confidence"] for v in self.validations) / len(
            self.validations
        )
        if ratio >= 0.7 and total_conf >= 0.6:
            self.status = HypothesisStatus.CONFIRMED
        elif ratio < 0.3 and total_conf >= 0.5:
            self.status = HypothesisStatus.REFUTED
        elif len(self.validations) >= 5:
            self.status = HypothesisStatus.INCONCLUSIVE

    def consensus(self) -> float:
        """Agreement level 0.0 (all disagree) to 1.0 (all agree)."""
        if not self.validations:
            return 0.0
        return sum(1 for v in self.validations if v["agrees"]) / len(self.validations)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        d["consensus"] = self.consensus()
        return d


@dataclass
class Belief:
    """A belief held by the mesh (converged from multiple agents)."""

    belief_id: str
    statement: str
    confidence: float
    supporting_agents: list[str] = field(default_factory=list)
    opposing_agents: list[str] = field(default_factory=list)
    source_hypotheses: list[str] = field(default_factory=list)
    last_updated: float = 0.0

    def update(self, confidence_delta: float, agent_id: str, supports: bool) -> None:
        self.confidence = max(0.0, min(1.0, self.confidence + confidence_delta))
        if supports and agent_id not in self.supporting_agents:
            self.supporting_agents.append(agent_id)
        elif not supports and agent_id not in self.opposing_agents:
            self.opposing_agents.append(agent_id)
        self.last_updated = time.time()

    def to_dict(self) -> dict:
        return asdict(self)


# ── Message Bus ───────────────────────────────────────────────


class MessageBus:
    """Topic-based pub/sub message bus for agent communication.

    Agents subscribe to topics and publish messages.
    Messages have TTL and auto-expire.
    """

    def __init__(self) -> None:
        self._subscriptions: dict[str, list[Callable[[MeshMessage], None]]] = (
            defaultdict(list)
        )
        self._history: dict[str, list[MeshMessage]] = defaultdict(
            list
        )  # topic → messages
        self._lock = threading.Lock()
        self._max_history = 100

    def publish(self, message: MeshMessage) -> int:
        """Publish a message to its topic. Returns number of subscribers notified."""
        with self._lock:
            subs = list(self._subscriptions.get(message.topic, []))
            self._history[message.topic].append(message)
            # Trim history
            if len(self._history[message.topic]) > self._max_history:
                self._history[message.topic] = self._history[message.topic][
                    -self._max_history :
                ]

        # Notify subscribers (outside lock to avoid deadlock)
        count = 0
        for sub in subs:
            try:
                sub(message)
                count += 1
            except Exception:
                pass
        return count

    def subscribe(self, topic: str, callback: Callable[[MeshMessage], None]) -> None:
        with self._lock:
            if callback not in self._subscriptions[topic]:
                self._subscriptions[topic].append(callback)

    def unsubscribe(self, topic: str, callback: Callable[[MeshMessage], None]) -> None:
        with self._lock:
            if callback in self._subscriptions.get(topic, []):
                self._subscriptions[topic].remove(callback)

    def get_history(self, topic: str, n: int = 10) -> list[MeshMessage]:
        with self._lock:
            msgs = list(self._history.get(topic, []))
        return msgs[-n:]

    def topics(self) -> list[str]:
        with self._lock:
            return list(self._subscriptions.keys())

    def subscriber_count(self, topic: str) -> int:
        with self._lock:
            return len(self._subscriptions.get(topic, []))

    def clean_expired(self) -> int:
        """Remove expired messages from history. Returns count removed."""
        removed = 0
        with self._lock:
            for topic in self._history:
                before = len(self._history[topic])
                self._history[topic] = [
                    m for m in self._history[topic] if not m.expired()
                ]
                removed += before - len(self._history[topic])
        return removed

    @staticmethod
    def create_message(
        topic: str,
        sender: str,
        content: Any,
        msg_type: str = "message",
        priority: MessagePriority = MessagePriority.NORMAL,
        reply_to: str | None = None,
    ) -> MeshMessage:
        return MeshMessage(
            message_id=uuid.uuid4().hex[:12],
            topic=topic,
            sender=sender,
            content=content,
            msg_type=msg_type,
            priority=priority,
            reply_to=reply_to,
        )


# ── Hypothesis Share ──────────────────────────────────────────


class HypothesisShare:
    """Agents publish hypotheses for others to validate.

    Uses the MessageBus for transport and provides consensus tracking.
    """

    def __init__(self, bus: MessageBus) -> None:
        self.bus = bus
        self._hypotheses: dict[str, Hypothesis] = {}
        self._lock = threading.Lock()

        # Auto-subscribe to hypothesis topics
        bus.subscribe("hypothesis", self._on_hypothesis_message)

    def propose(self, hypothesis: Hypothesis) -> None:
        """Propose a hypothesis to the mesh."""
        with self._lock:
            self._hypotheses[hypothesis.hypothesis_id] = hypothesis
        self.bus.publish(
            MeshMessage(
                message_id=uuid.uuid4().hex[:12],
                topic="hypothesis",
                sender=hypothesis.proposer,
                content={
                    "action": "propose",
                    "hypothesis_id": hypothesis.hypothesis_id,
                    "claim": hypothesis.claim,
                    "confidence": hypothesis.confidence,
                },
                msg_type="hypothesis",
            )
        )

    def validate(
        self,
        hypothesis_id: str,
        agent_id: str,
        agrees: bool,
        confidence: float = 0.5,
        reasoning: str = "",
    ) -> bool:
        """Validate a hypothesis in the mesh."""
        with self._lock:
            h = self._hypotheses.get(hypothesis_id)
            if h is None:
                return False
            h.validate(agent_id, agrees, confidence, reasoning)
            status = h.status.value

        self.bus.publish(
            MeshMessage(
                message_id=uuid.uuid4().hex[:12],
                topic="hypothesis",
                sender=agent_id,
                content={
                    "action": "validate",
                    "hypothesis_id": hypothesis_id,
                    "agrees": agrees,
                    "status": status,
                },
                msg_type="hypothesis",
            )
        )
        return True

    def get(self, hypothesis_id: str) -> Hypothesis | None:
        return self._hypotheses.get(hypothesis_id)

    def confirmed(self) -> list[Hypothesis]:
        return [
            h
            for h in self._hypotheses.values()
            if h.status == HypothesisStatus.CONFIRMED
        ]

    def refuted(self) -> list[Hypothesis]:
        return [
            h for h in self._hypotheses.values() if h.status == HypothesisStatus.REFUTED
        ]

    def pending(self) -> list[Hypothesis]:
        return [
            h
            for h in self._hypotheses.values()
            if h.status in (HypothesisStatus.PROPOSED, HypothesisStatus.TESTING)
        ]

    def all(self) -> list[Hypothesis]:
        return list(self._hypotheses.values())

    def _on_hypothesis_message(self, message: MeshMessage) -> None:
        """Auto-process hypothesis messages if needed."""
        # Currently just logging — actual validation is explicit
        pass


# ── Belief Propagation ────────────────────────────────────────


class BeliefPropagation:
    """Beliefs converge via weighted consensus across the mesh.

    Takes confirmed hypotheses and propagates them as shared beliefs.
    Agents can update beliefs (agree/disagree), causing confidence to shift.
    """

    def __init__(self, bus: MessageBus, hypothesis_share: HypothesisShare) -> None:
        self.bus = bus
        self.hypotheses = hypothesis_share
        self._beliefs: dict[str, Belief] = {}
        self._lock = threading.Lock()

        bus.subscribe("belief", self._on_belief_message)

    def adopt_from_hypothesis(self, hypothesis_id: str) -> Belief | None:
        """Convert a confirmed hypothesis into a shared belief."""
        h = self.hypotheses.get(hypothesis_id)
        if h is None or h.status != HypothesisStatus.CONFIRMED:
            return None

        belief = Belief(
            belief_id=uuid.uuid4().hex[:12],
            statement=h.claim,
            confidence=h.confidence * h.consensus(),
            supporting_agents=[v["agent"] for v in h.validations if v["agrees"]],
            opposing_agents=[v["agent"] for v in h.validations if not v["agrees"]],
            source_hypotheses=[hypothesis_id],
        )

        with self._lock:
            self._beliefs[belief.belief_id] = belief

        self.bus.publish(
            MeshMessage(
                message_id=uuid.uuid4().hex[:12],
                topic="belief",
                sender="mesh",
                content={
                    "action": "new_belief",
                    "belief_id": belief.belief_id,
                    "statement": belief.statement,
                    "confidence": belief.confidence,
                },
                msg_type="belief",
            )
        )
        return belief

    def update_belief(
        self,
        belief_id: str,
        agent_id: str,
        supports: bool,
        confidence_delta: float = 0.1,
    ) -> bool:
        """Update a belief based on agent input."""
        with self._lock:
            b = self._beliefs.get(belief_id)
            if b is None:
                return False
            b.update(confidence_delta, agent_id, supports)
        return True

    def get(self, belief_id: str) -> Belief | None:
        return self._beliefs.get(belief_id)

    def all(self) -> list[Belief]:
        return list(self._beliefs.values())

    def high_confidence(self, threshold: float = 0.8) -> list[Belief]:
        return [b for b in self._beliefs.values() if b.confidence >= threshold]

    def controversial(self, threshold: float = 0.3) -> list[Belief]:
        """Beliefs with significant opposition."""
        return [
            b
            for b in self._beliefs.values()
            if len(b.opposing_agents)
            / max(len(b.supporting_agents + b.opposing_agents), 1)
            > threshold
        ]

    def converge_all(self) -> dict[str, float]:
        """Propagate all confirmed hypotheses into beliefs."""
        adopted = {}
        for h in self.hypotheses.confirmed():
            belief = self.adopt_from_hypothesis(h.hypothesis_id)
            if belief:
                adopted[h.hypothesis_id] = belief.confidence
        return adopted

    def _on_belief_message(self, message: MeshMessage) -> None:
        content = message.content
        if isinstance(content, dict) and content.get("action") == "update":
            self.update_belief(
                content.get("belief_id", ""),
                message.sender,
                content.get("supports", True),
                content.get("delta", 0.1),
            )


# ── Mesh Agent ────────────────────────────────────────────────


class MeshAgent:
    """Agent that communicates via the cognitive mesh.

    Wraps any callable (function or AgentBase.run) and adds mesh
    communication capabilities: publish, subscribe, hypothesize, vote.

    Usage:
        agent = MeshAgent("my_agent", my_agent.run, bus)
        agent.subscribe("traffic_alerts", lambda m: print(m.content))
        agent.publish("traffic_alerts", {"traffic_drop": 0.3})
        agent.propose_hypothesis("SEO update caused traffic drop", evidence="data")
    """

    def __init__(
        self, agent_id: str, executor: Callable | None, bus: MessageBus
    ) -> None:
        self.agent_id = agent_id
        self.executor = executor
        self.bus = bus
        self._subscriptions: list[str] = []

    def subscribe(self, topic: str) -> None:
        """Subscribe to a mesh topic."""
        self.bus.subscribe(topic, self._on_message)
        self._subscriptions.append(topic)

    def publish(
        self,
        topic: str,
        content: Any,
        msg_type: str = "message",
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> MeshMessage:
        """Publish a message to a topic."""
        msg = self.bus.create_message(topic, self.agent_id, content, msg_type, priority)
        self.bus.publish(msg)
        return msg

    def propose_hypothesis(
        self,
        claim: str,
        evidence: str = "",
        confidence: float = 0.5,
        hypothesis_share: HypothesisShare | None = None,
    ) -> str | None:
        """Propose a hypothesis to the mesh."""
        if hypothesis_share is None:
            return None
        h = Hypothesis(
            hypothesis_id=uuid.uuid4().hex[:12],
            proposer=self.agent_id,
            claim=claim,
            evidence=evidence,
            confidence=confidence,
            tags=[self.agent_id],
        )
        hypothesis_share.propose(h)
        return h.hypothesis_id

    def vote_on_hypothesis(
        self,
        hypothesis_id: str,
        agrees: bool,
        confidence: float = 0.5,
        reasoning: str = "",
        hypothesis_share: HypothesisShare | None = None,
    ) -> bool:
        """Vote on a hypothesis."""
        if hypothesis_share is None:
            return False
        return hypothesis_share.validate(
            hypothesis_id, self.agent_id, agrees, confidence, reasoning
        )

    def update_belief(
        self,
        belief_id: str,
        supports: bool,
        belief_propagation: BeliefPropagation | None = None,
    ) -> bool:
        """Update a shared belief."""
        if belief_propagation is None:
            return False
        return belief_propagation.update_belief(belief_id, self.agent_id, supports)

    def _on_message(self, message: MeshMessage) -> None:
        """Handle incoming mesh messages."""
        pass  # Override in subclass or pass callbacks


# ── Cognitive Mesh (Orchestrator) ─────────────────────────────


class CognitiveMesh:
    """Main cognitive mesh. Coordinates all components.

    Usage:
        mesh = CognitiveMesh()
        mesh.create_agent("seo_v1", seo_agent.run)
        mesh.create_agent("content_v1", content_agent.run)

        # Agents communicate directly
        mesh.agents["seo_v1"].publish("keywords", {"keyword": "AI tools"})
        mesh.agents["content_v1"].subscribe("keywords")

        # Hypotheses and beliefs
        mesh.hypotheses.propose(Hypothesis(...))
        mesh.beliefs.converge_all()

        # Observer
        messages = mesh.bus.get_history("keywords")
    """

    def __init__(self) -> None:
        self.bus = MessageBus()
        self.hypotheses = HypothesisShare(self.bus)
        self.beliefs = BeliefPropagation(self.bus, self.hypotheses)
        self.agents: dict[str, MeshAgent] = {}
        self._lock = threading.Lock()

    def create_agent(
        self, agent_id: str, executor: Callable | None = None
    ) -> MeshAgent:
        """Create and register a mesh agent."""
        agent = MeshAgent(agent_id, executor, self.bus)
        with self._lock:
            self.agents[agent_id] = agent
        return agent

    def remove_agent(self, agent_id: str) -> None:
        with self._lock:
            self.agents.pop(agent_id, None)

    def total_messages(self) -> int:
        """Count all messages across all topics."""
        total = 0
        for topic in self.bus.topics():
            total += len(self.bus.get_history(topic, n=999999))
        return total

    def snapshot(self) -> dict:
        return {
            "agents": len(self.agents),
            "topics": len(self.bus.topics()),
            "messages": self.total_messages(),
            "hypotheses": {
                "total": len(self.hypotheses.all()),
                "confirmed": len(self.hypotheses.confirmed()),
                "refuted": len(self.hypotheses.refuted()),
                "pending": len(self.hypotheses.pending()),
            },
            "beliefs": {
                "total": len(self.beliefs.all()),
                "high_confidence": len(self.beliefs.high_confidence()),
                "controversial": len(self.beliefs.controversial()),
            },
        }


# ── Quick Diagnostic ──────────────────────────────────────────


def demo() -> None:
    """Demonstrate the Cognitive Mesh."""
    mesh = CognitiveMesh()

    # Create agents
    seo = mesh.create_agent("seo_research")
    content = mesh.create_agent("content_generator")
    analytics = mesh.create_agent("analytics")

    # Subscribe agents to topics
    content.subscribe("keywords")
    analytics.subscribe("hypothesis")

    print("=== Cognitive Mesh — Demo ===")
    print(f"Agents: {len(mesh.agents)}")

    # Agents communicate directly (P2P, not through orchestrator)
    print("\n1. SEO agent publishes keywords → content agent receives them:")
    seo.publish("keywords", {"keyword": "AI marketing tools", "volume": 5000})

    content_msg = mesh.bus.get_history("keywords")[-1]
    print(f"   Message: {content_msg.content}")

    # Hypothesis and validation
    print("\n2. SEO proposes hypothesis → analytics validates:")
    h = Hypothesis(
        hypothesis_id=uuid.uuid4().hex[:12],
        proposer="seo_research",
        claim="AI keywords are gaining search volume faster than traditional marketing terms",
        evidence="Historical keyword data shows 40% growth in AI terms vs 5% in traditional",
        confidence=0.7,
        tags=["seo", "trend"],
    )
    mesh.hypotheses.propose(h)

    # Analytics validates
    mesh.hypotheses.validate(
        h.hypothesis_id,
        "analytics",
        agrees=True,
        confidence=0.8,
        reasoning="Confirmed by search volume data",
    )
    # Content validates
    mesh.hypotheses.validate(
        h.hypothesis_id,
        "content_generator",
        agrees=True,
        confidence=0.6,
        reasoning="Aligned with content engagement metrics",
    )

    h2 = mesh.hypotheses.get(h.hypothesis_id)
    print(f"   Hypothesis: {h2.claim}")
    print(f"   Status: {h2.status.value}")
    print(f"   Consensus: {h2.consensus():.0%}")
    print(f"   Validations: {len(h2.validations)}")

    # Belief propagation
    print("\n3. Confirmed hypothesis → shared belief:")
    belief = mesh.beliefs.adopt_from_hypothesis(h.hypothesis_id)
    if belief:
        print(f"   Belief: {belief.statement}")
        print(f"   Confidence: {belief.confidence:.1%}")
        print(f"   Supporting agents: {belief.supporting_agents}")

    # Belief update
    print("\n4. Content agent updates belief:")
    mesh.beliefs.update_belief(
        belief.belief_id, "content_generator", supports=True, confidence_delta=0.1
    )
    b2 = mesh.beliefs.get(belief.belief_id)
    print(f"   Updated confidence: {b2.confidence:.1%}")

    print()
    print("Mesh snapshot:")
    print(json.dumps(mesh.snapshot(), indent=2))


if __name__ == "__main__":
    demo()
