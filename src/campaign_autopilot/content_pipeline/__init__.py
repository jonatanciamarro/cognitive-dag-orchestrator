"""Content Excellence Pipeline — psychologically-informed content creation.

Provides engines for:
- Storytelling (narrative structures, beats)
- Psychology (cognitive biases, persuasion)
- Psychoanalysis (deep triggers, Jungian concepts)
- Neuromarketing (brain-based marketing)
- Communication (framing, tone, rhetoric)
- Archetypes (12 Jungian brand archetypes)
- Content Design (visual content principles)
- Copywriting (conversion copy frameworks)
"""

from .storytelling_engine import (
    StorytellingEngine,
    NarrativeStructure,
    StoryBeat,
    StoryArc,
)

from .psychology_engine import (
    PsychologyEngine,
    CognitiveBias,
    PersuasionPrinciple,
    PsychologicalTrigger,
)

from .psychoanalysis_engine import (
    PsychoanalysisEngine,
    DeepTrigger,
    JungianConcept,
)

from .neuromarketing_engine import (
    NeuromarketingEngine,
    BrainPrinciple,
    SensoryTrigger,
)

from .communication_engine import (
    CommunicationEngine,
    MessageFrame,
    ToneOfVoice,
    RhetoricalDevice,
)

from .archetype_engine import (
    ArchetypeEngine,
    BrandArchetype,
    ArchetypeExpression,
)

from .copywriting_engine import (
    CopywritingEngine,
    CopyFramework,
    PersuasiveElement,
)

__all__ = [
    "StorytellingEngine",
    "NarrativeStructure",
    "StoryBeat",
    "StoryArc",
    "PsychologyEngine",
    "CognitiveBias",
    "PersuasionPrinciple",
    "PsychologicalTrigger",
    "PsychoanalysisEngine",
    "DeepTrigger",
    "JungianConcept",
    "NeuromarketingEngine",
    "BrainPrinciple",
    "SensoryTrigger",
    "CommunicationEngine",
    "MessageFrame",
    "ToneOfVoice",
    "RhetoricalDevice",
    "ArchetypeEngine",
    "BrandArchetype",
    "ArchetypeExpression",
    "CopywritingEngine",
    "CopyFramework",
    "PersuasiveElement",
]
