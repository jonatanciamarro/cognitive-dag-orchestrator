"""Agent Evolution Engine — AG-Kit Evolution Phase 14.

Agents mutate, compete, and evolve. The best survive.

Builds on AgentFactory (code generation) and adds:
  - AgentGenome: structured DNA of an agent
  - MutationEngine: mutate prompts, skills, tools, memory config
  - SelectionEngine: evaluate fitness (revenue, quality, cost)
  - AgentBreeder: combine genomes of top agents

Design Principles (Ponytail):
  - Zero new dependencies (stdlib only)
  - Extends AgentFactory, does NOT replace it
  - Thread-safe with threading.Lock
  - Useful even with single-agent systems (evolves configuration)
"""

from __future__ import annotations

import json
import random
import threading
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable


# ── Types ─────────────────────────────────────────────────────


class MutationType(Enum):
    PROMPT_TWEAK = "prompt_tweak"  # Small change to system prompt
    SKILL_ADD = "skill_add"  # Add a new skill
    SKILL_REMOVE = "skill_remove"  # Remove a skill
    TOOL_ADD = "tool_add"  # Add a tool
    TOOL_REMOVE = "tool_remove"  # Remove a tool
    MEMORY_CONFIG = "memory_config"  # Change memory settings
    CONSTRAINT_CHANGE = "constraint_change"  # Change constraint thresholds
    TEMPERATURE = "temperature"  # Change LLM temperature
    MAX_TOKENS = "max_tokens"  # Change max tokens


class FitnessMetric(Enum):
    REVENUE = "revenue"
    QUALITY = "quality"
    COST_EFFICIENCY = "cost_efficiency"
    SPEED = "speed"
    RELIABILITY = "reliability"
    COMPOSITE = "composite"


# ── Agent Genome ──────────────────────────────────────────────


@dataclass
class AgentGenome:
    """The complete DNA of an agent. Can be mutated and bred.

    Each genome defines the agent's skills, prompt, tools, memory
    configuration, and constraints. Fitness score tracks performance.
    """

    agent_id: str
    agent_type: str  # "marketing_channel", "seo_agent", "compliance"

    # Core
    skills: list[str] = field(default_factory=list)
    system_prompt: str = ""
    description: str = ""

    # Tools & Configuration
    tools: list[str] = field(default_factory=list)
    memory_config: dict[str, Any] = field(
        default_factory=lambda: {
            "session_ttl_hours": 24,
            "max_tokens": 4096,
            "temperature": 0.7,
        }
    )
    constraints: list[str] = field(default_factory=list)

    # Channel (for marketing agents)
    channel: str = ""
    platform: str = ""

    # Evolutionary metadata
    fitness_score: float = 0.0
    fitness_components: dict[str, float] = field(default_factory=dict)
    generation: int = 0
    parent_ids: list[str] = field(default_factory=list)
    mutation_history: list[str] = field(default_factory=list)
    created_at: float = 0.0
    last_evaluated: float = 0.0
    evaluation_count: int = 0

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = time.time()
        if not self.skills:
            self.skills = [f"{self.agent_type}_core"]
        if not self.system_prompt:
            self.system_prompt = (
                f"You are a {self.agent_type} agent for Campaign Autopilot."
            )

    def signature(self) -> str:
        """Unique signature: type + channel + skills hash."""
        return f"{self.agent_type}:{self.channel}:{hash(tuple(self.skills))}"

    def clone(
        self, new_id: str | None = None, parent_ids: list[str] | None = None
    ) -> AgentGenome:
        """Create a copy of this genome."""
        g = AgentGenome(
            agent_id=new_id or f"{self.agent_id}_clone",
            agent_type=self.agent_type,
            skills=list(self.skills),
            system_prompt=self.system_prompt,
            description=self.description,
            tools=list(self.tools),
            memory_config=dict(self.memory_config),
            constraints=list(self.constraints),
            channel=self.channel,
            platform=self.platform,
            generation=self.generation + 1,
            parent_ids=parent_ids if parent_ids is not None else [self.agent_id],
        )
        return g

    def to_dict(self) -> dict:
        return asdict(self)


# ── Mutation Engine ───────────────────────────────────────────


class MutationEngine:
    """Applies mutations to agent genomes.

    Each mutation type has a probability and effect.
    Mutations can be random (evolution) or guided (targeted improvement).
    """

    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)
        self._mutators: dict[MutationType, Callable[[AgentGenome], str]] = {
            MutationType.PROMPT_TWEAK: self._mutate_prompt,
            MutationType.SKILL_ADD: self._mutate_add_skill,
            MutationType.SKILL_REMOVE: self._mutate_remove_skill,
            MutationType.TOOL_ADD: self._mutate_add_tool,
            MutationType.TOOL_REMOVE: self._mutate_remove_tool,
            MutationType.MEMORY_CONFIG: self._mutate_memory_config,
            MutationType.TEMPERATURE: self._mutate_temperature,
            MutationType.MAX_TOKENS: self._mutate_max_tokens,
        }
        # Default probabilities for each mutation type
        self._probabilities: dict[MutationType, float] = {
            MutationType.PROMPT_TWEAK: 0.30,
            MutationType.SKILL_ADD: 0.15,
            MutationType.SKILL_REMOVE: 0.05,
            MutationType.TOOL_ADD: 0.10,
            MutationType.TOOL_REMOVE: 0.05,
            MutationType.MEMORY_CONFIG: 0.15,
            MutationType.TEMPERATURE: 0.10,
            MutationType.MAX_TOKENS: 0.10,
        }

    def set_probability(self, mutation: MutationType, prob: float) -> None:
        self._probabilities[mutation] = max(0.0, min(1.0, prob))

    def mutate(
        self,
        genome: AgentGenome,
        mutations: int = 1,
        parent_ids: list[str] | None = None,
    ) -> AgentGenome:
        """Apply N random mutations to a genome. Returns new genome."""
        child = genome.clone(
            f"{genome.agent_id}_mut{genome.generation}", parent_ids=parent_ids
        )
        applied = []
        for _ in range(mutations):
            mtype = self._pick_mutation()
            if mtype:
                description = self._mutators[mtype](child)
                applied.append(description)
        child.mutation_history.extend(applied)
        return child

    def targeted_mutate(
        self, genome: AgentGenome, mutation_type: MutationType
    ) -> AgentGenome:
        """Apply a specific mutation type."""
        child = genome.clone(
            f"{genome.agent_id}_mut{genome.generation}", parent_ids=genome.parent_ids
        )
        if mutation_type in self._mutators:
            desc = self._mutators[mutation_type](child)
            child.mutation_history.append(desc)
        return child

    def _pick_mutation(self) -> MutationType | None:
        """Pick a mutation type weighted by probability."""
        r = self.rng.random()
        cumulative = 0.0
        for mtype, prob in sorted(self._probabilities.items(), key=lambda x: -x[1]):
            cumulative += prob
            if r <= cumulative:
                return mtype
        return None

    def _mutate_prompt(self, g: AgentGenome) -> str:
        """Tweak the system prompt slightly."""
        tweaks = [
            "seja mais conciso",
            "seja mais detalhado",
            "foque em conversão",
            "foque em qualidade",
            "otimize para SEO",
            "priorize velocidade",
            "use linguagem persuasiva",
            "use linguagem técnica",
            "adapte ao público iniciante",
            "adapte ao público avançado",
        ]
        tweak = self.rng.choice(tweaks)
        g.system_prompt += f" | Mutação: {tweak}"
        return f"prompt_tweak: {tweak}"

    def _mutate_add_skill(self, g: AgentGenome) -> str:
        skills_pool = [
            "seo",
            "copywriting",
            "analytics",
            "storytelling",
            "neuromarketing",
            "email",
            "social_media",
            "video",
            "audio",
            "design",
            "a_b_testing",
            "conversion_optimization",
            "keyword_research",
            "competitor_analysis",
            "content_planning",
            "data_analysis",
        ]
        new_skill = self.rng.choice(
            [s for s in skills_pool if s not in g.skills] + skills_pool[:1]
        )
        if new_skill not in g.skills:
            g.skills.append(new_skill)
            return f"skill_add: {new_skill}"
        return "skill_add: (already present)"

    def _mutate_remove_skill(self, g: AgentGenome) -> str:
        if len(g.skills) <= 1:
            return "skill_remove: (too few skills)"
        removed = g.skills.pop(self.rng.randint(0, len(g.skills) - 1))
        return f"skill_remove: {removed}"

    def _mutate_add_tool(self, g: AgentGenome) -> str:
        tools_pool = [
            "web_search",
            "image_gen",
            "video_edit",
            "translate",
            "summarize",
            "scrape",
            "api_call",
            "database_query",
        ]
        new_tool = self.rng.choice(
            [t for t in tools_pool if t not in g.tools] + tools_pool[:1]
        )
        if new_tool not in g.tools:
            g.tools.append(new_tool)
            return f"tool_add: {new_tool}"
        return "tool_add: (already present)"

    def _mutate_remove_tool(self, g: AgentGenome) -> str:
        if not g.tools:
            return "tool_remove: (no tools)"
        removed = g.tools.pop(self.rng.randint(0, len(g.tools) - 1))
        return f"tool_remove: {removed}"

    def _mutate_memory_config(self, g: AgentGenome) -> str:
        key = self.rng.choice(list(g.memory_config.keys()))
        current = g.memory_config[key]
        if isinstance(current, (int, float)):
            delta = current * 0.2 * (1 if self.rng.random() > 0.5 else -1)
            g.memory_config[key] = max(1, current + delta)
            if isinstance(current, int):
                g.memory_config[key] = int(g.memory_config[key])
        return f"memory_config: {key} {current} → {g.memory_config[key]}"

    def _mutate_temperature(self, g: AgentGenome) -> str:
        old = g.memory_config.get("temperature", 0.7)
        delta = 0.1 * (1 if self.rng.random() > 0.5 else -1)
        new = max(0.0, min(2.0, old + delta))
        g.memory_config["temperature"] = round(new, 2)
        return f"temperature: {old} → {new}"

    def _mutate_max_tokens(self, g: AgentGenome) -> str:
        old = g.memory_config.get("max_tokens", 4096)
        delta_mult = [0.5, 1.5, 2.0][self.rng.randint(0, 2)]
        new = max(256, min(32000, int(old * delta_mult)))
        g.memory_config["max_tokens"] = new
        return f"max_tokens: {old} → {new}"


# ── Selection Engine ──────────────────────────────────────────


class SelectionEngine:
    """Evaluates agent fitness and selects the best genomes for breeding.

    Fitness is scored 0.0 (worst) to 1.0 (perfect) based on:
      - Revenue contribution (weighted)
      - Output quality (if measurable)
      - Cost efficiency (revenue / cost)
      - Reliability (success rate)
      - Speed (latency)
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._evaluations: dict[
            str, list[dict]
        ] = {}  # agent_id -> [evaluation snapshots]

    def evaluate(
        self, genome: AgentGenome, metrics: dict[FitnessMetric, float] | None = None
    ) -> float:
        """Score a genome. Returns 0.0-1.0 fitness."""
        with self._lock:
            components = {}

            if metrics:
                # Use provided metrics
                weights = {
                    FitnessMetric.REVENUE: 0.35,
                    FitnessMetric.QUALITY: 0.25,
                    FitnessMetric.COST_EFFICIENCY: 0.20,
                    FitnessMetric.SPEED: 0.10,
                    FitnessMetric.RELIABILITY: 0.10,
                }
                score = 0.0
                for metric, value in metrics.items():
                    w = weights.get(metric, 0.1)
                    normalized = max(0.0, min(1.0, value))
                    components[metric.value] = normalized
                    score += w * normalized
            else:
                # Default score based on genome properties
                score = 0.5  # baseline
                components["baseline"] = 0.5
                # Bonus for diverse skills
                skill_bonus = min(len(genome.skills) * 0.05, 0.2)
                score += skill_bonus
                components["skill_diversity"] = skill_bonus
                # Bonus for tools
                tool_bonus = min(len(genome.tools) * 0.03, 0.15)
                score += tool_bonus
                components["tool_diversity"] = tool_bonus
                # Penalty for very long prompts (overfitting risk)
                if len(genome.system_prompt) > 500:
                    penalty = -0.1
                    score += penalty
                    components["prompt_length_penalty"] = penalty

            score = max(0.0, min(1.0, score))
            genome.fitness_score = score
            genome.fitness_components = components
            genome.last_evaluated = time.time()
            genome.evaluation_count += 1

            # Store evaluation history
            if genome.agent_id not in self._evaluations:
                self._evaluations[genome.agent_id] = []
            self._evaluations[genome.agent_id].append(
                {
                    "timestamp": time.time(),
                    "score": score,
                    "components": dict(components),
                }
            )

            return score

    def select(
        self, population: list[AgentGenome], n: int = 2, method: str = "tournament"
    ) -> list[AgentGenome]:
        """Select the top N genomes from a population.

        Methods:
          - tournament: random tournament selection (avoids premature convergence)
          - elite: always pick the absolute best
          - roulette: fitness-proportional selection
        """
        if not population:
            return []
        n = min(n, len(population))

        if method == "elite":
            ranked = sorted(population, key=lambda g: -g.fitness_score)
            return ranked[:n]

        elif method == "roulette":
            total_fitness = sum(max(g.fitness_score, 0.01) for g in population)
            selected = []
            rng = random.Random()
            for _ in range(n):
                pick = rng.random() * total_fitness
                cumulative = 0.0
                for g in population:
                    cumulative += max(g.fitness_score, 0.01)
                    if cumulative >= pick and g not in selected:
                        selected.append(g)
                        break
                if len(selected) < _ + 1:
                    selected.append(population[0])
            return selected

        else:  # tournament (default)
            selected = []
            rng = random.Random()
            pool = list(population)
            for _ in range(n):
                if len(pool) <= 1:
                    selected.extend(pool)
                    break
                # Pick 3 random candidates, keep the best
                candidates = rng.sample(pool, min(3, len(pool)))
                winner = max(candidates, key=lambda g: g.fitness_score)
                selected.append(winner)
                pool.remove(winner)
            return selected

    def get_history(self, agent_id: str) -> list[dict]:
        return self._evaluations.get(agent_id, [])


# ── Agent Breeder ─────────────────────────────────────────────


class AgentBreeder:
    """Combines genomes of top-performing agents to create offspring.

    Crossover: child inherits skills/tools from both parents.
    Followed by optional mutation.
    """

    def __init__(self, mutation_engine: MutationEngine | None = None) -> None:
        self.mutation = mutation_engine or MutationEngine()

    def breed(
        self,
        parent_a: AgentGenome,
        parent_b: AgentGenome,
        agent_id: str | None = None,
        mutations: int = 1,
    ) -> AgentGenome:
        """Create a child from two parents via crossover + optional mutation."""
        child = AgentGenome(
            agent_id=agent_id or f"{parent_a.agent_type}_offspring_{int(time.time())}",
            agent_type=parent_a.agent_type,
            channel=parent_a.channel or parent_b.channel,
            generation=max(parent_a.generation, parent_b.generation) + 1,
            parent_ids=[parent_a.agent_id, parent_b.agent_id],
        )

        # Crossover: skills (union with preference for higher-fitness parent)
        if parent_a.fitness_score >= parent_b.fitness_score:
            child.skills = list(set(parent_a.skills + parent_b.skills))
        else:
            child.skills = list(set(parent_b.skills + parent_a.skills))

        # Crossover: tools (union)
        child.tools = list(set(parent_a.tools + parent_b.tools))

        # Crossover: prompt (pick the better one)
        if parent_a.fitness_score >= parent_b.fitness_score:
            child.system_prompt = parent_a.system_prompt
        else:
            child.system_prompt = parent_b.system_prompt

        # Crossover: memory config (average numeric values)
        all_keys = set(parent_a.memory_config.keys()) | set(
            parent_b.memory_config.keys()
        )
        for key in all_keys:
            va = parent_a.memory_config.get(key)
            vb = parent_b.memory_config.get(key)
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                child.memory_config[key] = round((va + vb) / 2, 2)
                if isinstance(va, int) and isinstance(vb, int):
                    child.memory_config[key] = int(child.memory_config[key])
            else:
                child.memory_config[key] = va or vb or 0.7

        # Crossover: constraints (union)
        child.constraints = list(set(parent_a.constraints + parent_b.constraints))

        child.description = f"Offspring of {parent_a.agent_id} + {parent_b.agent_id}"

        # Apply mutation
        if mutations > 0:
            child = self.mutation.mutate(
                child,
                mutations=mutations,
                parent_ids=child.parent_ids.copy() if child.parent_ids else None,
            )

        return child


# ── Evolution Engine (Orchestrator) ───────────────────────────


class AgentEvolutionEngine:
    """Main evolution engine. Coordinates mutation, selection, and breeding.

    Usage:
        ee = AgentEvolutionEngine()
        ee.register(genome_a)
        ee.register(genome_b)
        ee.evaluate_all(...)  # score every genome
        best = ee.evolve()    # select + breed + mutate
    """

    def __init__(self) -> None:
        self.mutation = MutationEngine()
        self.selection = SelectionEngine()
        self.breeder = AgentBreeder(self.mutation)
        self._population: dict[str, AgentGenome] = {}
        self._lock = threading.Lock()
        self._generation = 0

    def register(self, genome: AgentGenome) -> None:
        with self._lock:
            self._population[genome.agent_id] = genome

    def register_from_factory(
        self,
        agent_id: str,
        agent_type: str,
        channel: str = "",
        skills: list[str] | None = None,
    ) -> AgentGenome:
        """Register a genome based on an AgentFactory-created agent."""
        genome = AgentGenome(
            agent_id=agent_id,
            agent_type=agent_type,
            channel=channel,
            skills=skills or [f"{agent_type}_core"],
        )
        self.register(genome)
        return genome

    def get(self, agent_id: str) -> AgentGenome | None:
        return self._population.get(agent_id)

    def population(self) -> list[AgentGenome]:
        return list(self._population.values())

    def evaluate_all(
        self, metrics: dict[str, dict[FitnessMetric, float]] | None = None
    ) -> None:
        """Evaluate all genomes in population."""
        for g in self.population():
            m = metrics.get(g.agent_id) if metrics else None
            self.selection.evaluate(g, m)

    def evolve(
        self,
        n_parents: int = 2,
        n_offspring: int = 3,
        mutations: int = 2,
        method: str = "tournament",
    ) -> list[AgentGenome]:
        """Run one evolution cycle: select → breed → mutate.

        Returns the new offspring genomes.
        """
        self._generation += 1
        parents = self.selection.select(self.population(), n=n_parents, method=method)
        if len(parents) < 2:
            return []  # Need at least 2 parents to breed

        offspring = []
        rng = random.Random()
        for i in range(n_offspring):
            pa = rng.choice(parents)
            pb = rng.choice(
                [p for p in parents if p.agent_id != pa.agent_id] or parents
            )
            child = self.breeder.breed(pa, pb, mutations=mutations)
            child.agent_id = f"{pa.agent_type}_gen{self._generation}_offspring_{i}"
            self.register(child)
            offspring.append(child)

        return offspring

    def evolve_continuous(
        self,
        generations: int = 5,
        metrics: dict[str, dict[FitnessMetric, float]] | None = None,
        method: str = "tournament",
    ) -> list[AgentGenome]:
        """Run multiple evolution generations."""
        all_offspring = []
        for g in range(generations):
            self.evaluate_all(metrics)
            new = self.evolve(method=method)
            all_offspring.extend(new)
        return all_offspring

    def top(self, n: int = 3) -> list[AgentGenome]:
        """Get the N best genomes by fitness score."""
        ranked = sorted(self.population(), key=lambda g: -g.fitness_score)
        return ranked[:n]

    def report(self) -> dict:
        """Full evolution report."""
        pop = self.population()
        scored = [g for g in pop if g.evaluation_count > 0]
        return {
            "population_size": len(pop),
            "generation": self._generation,
            "scored_agents": len(scored),
            "best_score": max((g.fitness_score for g in scored), default=0.0),
            "avg_score": sum(g.fitness_score for g in scored) / max(len(scored), 1),
            "top_agents": [
                {
                    "id": g.agent_id,
                    "type": g.agent_type,
                    "fitness": g.fitness_score,
                    "skills": g.skills,
                    "generation": g.generation,
                }
                for g in self.top(5)
            ],
        }


# ── Quick Diagnostic ──────────────────────────────────────────


def demo() -> None:
    """Demonstrate the Agent Evolution Engine."""
    ee = AgentEvolutionEngine()

    # Seed population with diverse genomes
    genomes = [
        AgentGenome(
            "seo_v1",
            "seo_agent",
            skills=["seo", "keyword_research"],
            system_prompt="SEO specialist focused on organic traffic.",
        ),
        AgentGenome(
            "content_v1",
            "marketing_channel",
            channel="blog",
            skills=["copywriting", "storytelling"],
            system_prompt="Content creator for blog articles.",
        ),
        AgentGenome(
            "social_v1",
            "marketing_channel",
            channel="pinterest",
            skills=["social_media", "design"],
            system_prompt="Social media specialist for Pinterest.",
        ),
        AgentGenome(
            "email_v1",
            "marketing_channel",
            channel="email",
            skills=["email", "copywriting", "analytics"],
            system_prompt="Email marketing specialist.",
        ),
    ]
    for g in genomes:
        ee.register(g)

    print("=== Agent Evolution Engine — Demo ===")
    print(f"Initial population: {len(ee.population())}")
    print()

    # Evaluate with simulated metrics
    metrics = {
        "seo_v1": {
            FitnessMetric.REVENUE: 0.6,
            FitnessMetric.QUALITY: 0.8,
            FitnessMetric.COST_EFFICIENCY: 0.5,
        },
        "content_v1": {
            FitnessMetric.REVENUE: 0.7,
            FitnessMetric.QUALITY: 0.6,
            FitnessMetric.COST_EFFICIENCY: 0.7,
        },
        "social_v1": {
            FitnessMetric.REVENUE: 0.4,
            FitnessMetric.QUALITY: 0.5,
            FitnessMetric.COST_EFFICIENCY: 0.8,
        },
        "email_v1": {
            FitnessMetric.REVENUE: 0.9,
            FitnessMetric.QUALITY: 0.7,
            FitnessMetric.COST_EFFICIENCY: 0.9,
        },
    }
    ee.evaluate_all(metrics)

    print("Initial rankings:")
    for g in ee.top(len(ee.population())):
        print(f"  {g.agent_id:15s} fitness={g.fitness_score:.3f}  skills={g.skills}")

    # Evolve
    offspring = ee.evolve(n_parents=2, n_offspring=3, mutations=2)
    print(f"\nEvolved {len(offspring)} offspring (generation {ee._generation}):")

    # Evaluate offspring with moderate scores
    for o in offspring:
        base = random.Random(hash(o.agent_id)).uniform(0.4, 0.8)
        ee.selection.evaluate(
            o,
            {
                FitnessMetric.REVENUE: base,
                FitnessMetric.QUALITY: base * 1.1,
                FitnessMetric.COST_EFFICIENCY: base * 0.9,
            },
        )
        print(
            f"  {o.agent_id:30s} fitness={o.fitness_score:.3f}  "
            f"parents={o.parent_ids}  mutations={o.mutation_history}"
        )

    print()
    print("New top 3:")
    for g in ee.top(3):
        print(
            f"  {g.agent_id:30s} fitness={g.fitness_score:.3f}  "
            f"gen={g.generation}  skills={g.skills}"
        )

    print()
    print("Evolution report:")
    print(json.dumps(ee.report(), indent=2, default=str))


if __name__ == "__main__":
    demo()
