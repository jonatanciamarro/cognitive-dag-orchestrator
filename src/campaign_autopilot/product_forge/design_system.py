"""Design System — Open Design compatible token system.

Implementa a especificação de design system no formato Open Design,
permitindo portabilidade entre ferramentas de design e geração de artefatos.
Formato compatível com: https://github.com/nexu-io/open-design
"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# ═══════════════════════════════════════════════════════════════
# Token System (Open Design format)
# ═══════════════════════════════════════════════════════════════


@dataclass
class DesignToken:
    """Base token — Open Design format compatible."""

    name: str
    value: Any
    type: str = "generic"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    deprecation: Optional[str] = None  # migration path if deprecated

    def to_dict(self) -> Dict[str, Any]:
        d = {"name": self.name, "value": self.value, "type": self.type}
        if self.description:
            d["description"] = self.description
        if self.tags:
            d["tags"] = self.tags
        if self.deprecation:
            d["deprecation"] = self.deprecation
        return d


@dataclass
class ColorToken(DesignToken):
    type: str = "color"
    value: str = "#000000"
    opacity: float = 1.0
    dark_value: Optional[str] = None  # dark mode variant

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        if self.opacity < 1.0:
            d["opacity"] = self.opacity
        if self.dark_value:
            d["dark"] = self.dark_value
        return d


@dataclass
class TypographyToken(DesignToken):
    type: str = "typography"
    font_family: str = "sans-serif"
    font_size: str = "1rem"
    font_weight: str = "400"
    line_height: str = "1.5"
    letter_spacing: str = "0"


@dataclass
class SpacingToken(DesignToken):
    type: str = "spacing"
    value: str = "0"
    unit: str = "rem"


@dataclass
class ComponentSpec:
    """Spec for a UI component — Open Design compatible."""

    name: str
    type: str  # section, card, button, input, etc.
    description: str = ""
    props: Dict[str, Any] = field(default_factory=dict)
    slots: Dict[str, str] = field(default_factory=dict)  # named slots
    variants: List[str] = field(default_factory=list)  # variant names
    default_variant: str = "default"
    design_tokens: Dict[str, str] = field(default_factory=dict)  # token references

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class LayoutSpec:
    """Grid/flex layout specification."""

    name: str
    columns: int = 1
    gap: str = "1rem"
    max_width: str = "1200px"
    padding: str = "1rem"
    responsive: Dict[str, int] = field(
        default_factory=lambda: {"sm": 1, "md": 2, "lg": 3, "xl": 4}
    )
    alignment: str = "start"  # start, center, end, stretch


# ═══════════════════════════════════════════════════════════════
# Design System (Open Design format)
# ═══════════════════════════════════════════════════════════════


@dataclass
class DesignSystem:
    """Complete design system — Open Design format spec.

    Compatível com exportação para Open Design / DESIGN.md.
    """

    name: str
    version: str = "1.0.0"
    description: str = ""
    tokens: Dict[str, DesignToken] = field(default_factory=dict)
    components: Dict[str, ComponentSpec] = field(default_factory=dict)
    layouts: Dict[str, LayoutSpec] = field(default_factory=dict)
    typography: Dict[str, TypographyToken] = field(default_factory=dict)
    spacing: Dict[str, SpacingToken] = field(default_factory=dict)
    breakpoints: Dict[str, str] = field(
        default_factory=lambda: {
            "sm": "640px",
            "md": "768px",
            "lg": "1024px",
            "xl": "1280px",
            "2xl": "1536px",
        }
    )
    metadata: Dict[str, Any] = field(
        default_factory=lambda: {
            "author": "Lyzer Labs",
            "framework": "Open Design Compatible",
            "generated": "2026-06-24",
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "tokens": {k: v.to_dict() for k, v in self.tokens.items()},
            "components": {k: v.to_dict() for k, v in self.components.items()},
            "layouts": {k: v.to_dict() for k, v in self.layouts.items()},
            "typography": {k: v.to_dict() for k, v in self.typography.items()},
            "spacing": {k: v.to_dict() for k, v in self.spacing.items()},
            "breakpoints": self.breakpoints,
            "metadata": self.metadata,
        }
        return result

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def export_design_md(self) -> str:
        """Exporta como DESIGN.md no formato Open Design."""
        return generate_design_md(self)

    def register_component(self, spec: ComponentSpec) -> None:
        self.components[spec.name] = spec

    def register_layout(self, spec: LayoutSpec) -> None:
        self.layouts[spec.name] = spec


# ═══════════════════════════════════════════════════════════════
# Registry
# ═══════════════════════════════════════════════════════════════


class DesignSystemRegistry:
    """Central registry for design systems — thread-safe with lock."""

    _instance: Optional["DesignSystemRegistry"] = None
    _systems: Dict[str, DesignSystem] = {}

    def __new__(cls) -> "DesignSystemRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._systems = {}
        return cls._instance

    def register(self, name: str, system: DesignSystem) -> None:
        self._systems[name] = system

    def get(self, name: str) -> Optional[DesignSystem]:
        return self._systems.get(name)

    def list(self) -> List[str]:
        return list(self._systems.keys())

    def get_default(self) -> DesignSystem:
        return self._systems.get("lyzer-labs", default_lyzer_design_system())


# ═══════════════════════════════════════════════════════════════
# Default Lyzer Labs Design System
# ═══════════════════════════════════════════════════════════════


def default_lyzer_design_system() -> DesignSystem:
    """Cria o Design System padrão do Lyzer Labs."""
    from .color_palette import (
        LYZER_COLORS,
    )

    ds = DesignSystem(
        name="Lyzer Labs",
        version="1.0.0",
        description="Quantum design system for Lyzer Labs ecosystem — "
        "dark-first, agent-native, AI-adaptive interface language.",
    )

    # ── Color Tokens ────────────────────────────────────────
    color_categories = {
        "primary": "primary-500",
        "secondary": "secondary-500",
        "accent": "accent-500",
        "bg-dark": "bg-dark",
        "bg-card": "bg-card",
        "text-primary": "text-primary",
        "text-secondary": "text-secondary",
        "border": "border",
        "success": "success",
        "warning": "warning",
        "error": "error",
        "info": "info",
    }
    for name, key in color_categories.items():
        ds.tokens[name] = ColorToken(
            name=name,
            value=LYZER_COLORS[key],
            description=f"{name} color token",
        )

    # ── Component Specs ─────────────────────────────────────
    ds.components["button"] = ComponentSpec(
        name="button",
        type="button",
        description="Primary action button",
        props={
            "variant": {
                "type": "string",
                "options": ["primary", "secondary", "ghost", "accent"],
            },
            "size": {"type": "string", "options": ["sm", "md", "lg"]},
            "fullWidth": {"type": "boolean", "default": False},
            "loading": {"type": "boolean", "default": False},
            "icon": {"type": "string", "optional": True},
        },
        variants=["primary", "secondary", "ghost", "accent"],
        default_variant="primary",
        design_tokens={
            "bg": "primary",
            "text": "text-primary",
            "border": "border",
        },
    )

    ds.components["card"] = ComponentSpec(
        name="card",
        type="card",
        description="Content container with glass effect",
        props={
            "variant": {"type": "string", "options": ["elevated", "outlined", "glass"]},
            "padding": {"type": "string", "default": "lg"},
            "hover": {"type": "boolean", "default": True},
        },
        variants=["elevated", "outlined", "glass"],
        design_tokens={"bg": "bg-card", "border": "border"},
    )

    ds.components["metric-card"] = ComponentSpec(
        name="metric-card",
        type="card",
        description="KPI metric display card",
        props={
            "label": {"type": "string"},
            "value": {"type": "string"},
            "change": {"type": "string", "optional": True},
            "trend": {"type": "string", "options": ["up", "down", "neutral"]},
            "icon": {"type": "string", "optional": True},
        },
        variants=["default", "compact"],
    )

    ds.components["hero-section"] = ComponentSpec(
        name="hero-section",
        type="section",
        description="Landing page hero with headline, subtitle, CTA",
        props={
            "headline": {"type": "string"},
            "subtitle": {"type": "string", "optional": True},
            "cta_text": {"type": "string"},
            "cta_link": {"type": "string"},
            "secondary_cta_text": {"type": "string", "optional": True},
            "background": {"type": "string", "default": "gradient"},
        },
    )

    ds.components["pricing-card"] = ComponentSpec(
        name="pricing-card",
        type="card",
        description="Pricing tier display",
        props={
            "tier": {"type": "string"},
            "price": {"type": "string"},
            "period": {"type": "string", "default": "/month"},
            "features": {"type": "array"},
            "cta_text": {"type": "string"},
            "featured": {"type": "boolean", "default": False},
        },
    )

    # ── Layouts ─────────────────────────────────────────────
    ds.layouts["page"] = LayoutSpec(
        name="page",
        columns=1,
        max_width="1200px",
        padding="2rem",
    )

    ds.layouts["grid-3"] = LayoutSpec(
        name="grid-3",
        columns=3,
        gap="1.5rem",
        max_width="1200px",
        padding="2rem",
        responsive={"sm": 1, "md": 2, "lg": 3, "xl": 3},
    )

    ds.layouts["sidebar-layout"] = LayoutSpec(
        name="sidebar-layout",
        columns=2,
        gap="2rem",
        max_width="1200px",
        padding="2rem",
        responsive={"sm": 1, "md": 1, "lg": 2, "xl": 2},
    )

    return ds


# ═══════════════════════════════════════════════════════════════
# DESIGN.md Generator
# ═══════════════════════════════════════════════════════════════


def generate_design_md(ds: DesignSystem) -> str:
    """Gera DESIGN.md no formato Open Design a partir do DesignSystem."""
    lines = []
    lines.append(f"# Design System — {ds.name}")
    lines.append("")
    lines.append(f"> Version {ds.version}")
    lines.append("")
    lines.append(ds.description or "")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Colors
    lines.append("## Colors")
    lines.append("")
    lines.append("| Token | Value | Description |")
    lines.append("|-------|-------|-------------|")
    for name, token in ds.tokens.items():
        if isinstance(token, ColorToken):
            lines.append(f"| `{name}` | `{token.value}` | {token.description} |")
    lines.append("")

    # Typography
    lines.append("## Typography")
    lines.append("")
    for name, token in ds.typography.items():
        if isinstance(token, TypographyToken):
            lines.append(
                f"- **{name}**: {token.font_family} / {token.font_size} / {token.font_weight}"
            )
    lines.append("")

    # Components
    lines.append("## Components")
    lines.append("")
    for name, comp in ds.components.items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"_{comp.description}_")
        lines.append("")
        if comp.variants:
            lines.append(f"**Variants:** {', '.join(comp.variants)}")
            lines.append("")
        if comp.props:
            lines.append("| Prop | Type | Default |")
            lines.append("|------|------|---------|")
            for prop_name, prop_spec in comp.props.items():
                default = (
                    prop_spec.get("default", "—")
                    if isinstance(prop_spec, dict)
                    else "—"
                )
                prop_type = (
                    prop_spec.get("type", "string")
                    if isinstance(prop_spec, dict)
                    else "string"
                )
                lines.append(f"| `{prop_name}` | {prop_type} | {default} |")
            lines.append("")

    # Layouts
    lines.append("## Layouts")
    lines.append("")
    for name, layout in ds.layouts.items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"- Columns: {layout.columns}")
        lines.append(f"- Max Width: {layout.max_width}")
        lines.append(f"- Gap: {layout.gap}")
        lines.append(f"- Responsive: {layout.responsive}")
        lines.append("")

    # Breakpoints
    lines.append("## Breakpoints")
    lines.append("")
    for name, size in ds.breakpoints.items():
        lines.append(f"- `{name}`: {size}")
    lines.append("")

    # Metadata
    lines.append("## Metadata")
    lines.append("")
    for key, value in ds.metadata.items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("_Generated by Lyzer Labs Product Forge — Open Design compatible_")
    lines.append("")

    return "\n".join(lines)


def load_design_system(path: str) -> DesignSystem:
    """Carrega um Design System de arquivo JSON ou DESIGN.md."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Design system not found: {path}")

    if p.suffix == ".json":
        with open(p) as f:
            data = json.load(f)
        return _from_dict(data)
    elif p.suffix == ".md" or p.name == "DESIGN.md":
        # Basic parser for DESIGN.md format
        return _parse_design_md(p.read_text())
    else:
        raise ValueError(f"Unsupported format: {p.suffix}")


def _from_dict(data: Dict) -> DesignSystem:
    """Reconstroi DesignSystem de dicionário."""
    ds = DesignSystem(
        name=data.get("name", "Unnamed"),
        version=data.get("version", "1.0.0"),
        description=data.get("description", ""),
        breakpoints=data.get("breakpoints", {}),
        metadata=data.get("metadata", {}),
    )
    # Tokens
    for name, tdata in data.get("tokens", {}).items():
        ttype = tdata.get("type", "generic")
        if ttype == "color":
            ds.tokens[name] = ColorToken(
                name=name,
                value=tdata.get("value", "#000"),
                description=tdata.get("description", ""),
                opacity=tdata.get("opacity", 1.0),
                dark_value=tdata.get("dark"),
            )
        else:
            ds.tokens[name] = DesignToken(
                name=name,
                value=tdata.get("value"),
                type=ttype,
                description=tdata.get("description", ""),
            )
    # Components
    for name, cdata in data.get("components", {}).items():
        ds.components[name] = ComponentSpec(**cdata)
    # Layouts
    for name, ldata in data.get("layouts", {}).items():
        ds.layouts[name] = LayoutSpec(**ldata)
    return ds


def _parse_design_md(text: str) -> DesignSystem:
    """Parsada básica de DESIGN.md para DesignSystem."""
    ds = DesignSystem(name="Imported from DESIGN.md")
    current_section = None
    for line in text.split("\n"):
        line_stripped = line.strip()
        if line_stripped.startswith("## "):
            current_section = line_stripped[3:].lower()
        elif (
            current_section == "colors"
            and "|" in line_stripped
            and line_stripped.startswith("| `")
        ):
            parts = [
                p.strip().strip("`") for p in line_stripped.split("|") if p.strip()
            ]
            if len(parts) >= 2:
                name = parts[0]
                value = parts[1]
                ds.tokens[name] = ColorToken(name=name, value=value)
    return ds
