"""Lyzer Labs — Color Palette & Design Tokens.

Especificação completa de cores, gradientes, sombras e tipografia
no formato compatível com Open Design system.
"""

from __future__ import annotations

from typing import Dict


# ═══════════════════════════════════════════════════════════════
# LYZER LABS — Brand Colors
# ═══════════════════════════════════════════════════════════════

# ── Primary Palette ───────────────────────────────────────────
# Roxo quantum — identidade central da marca
LYZER_COLORS: Dict[str, str] = {
    # Primary
    "primary-50": "#f3e8ff",
    "primary-100": "#e2d1ff",
    "primary-200": "#c9a4ff",
    "primary-300": "#ae77ff",
    "primary-400": "#9350ff",
    "primary-500": "#7c2dff",  # Principal
    "primary-600": "#6414e6",
    "primary-700": "#4c0dbf",
    "primary-800": "#370999",
    "primary-900": "#250673",
    "primary-950": "#140347",
    # Secondary — ciano elétrico (acento tech)
    "secondary-50": "#e0faff",
    "secondary-100": "#b8f0ff",
    "secondary-200": "#80e4ff",
    "secondary-300": "#40d4ff",
    "secondary-400": "#00c2ff",
    "secondary-500": "#00aaff",  # Principal
    "secondary-600": "#0088cc",
    "secondary-700": "#006699",
    "secondary-800": "#004d73",
    "secondary-900": "#00334d",
    "secondary-950": "#001a26",
    # Accent — dourado (destaque, CTA, premium)
    "accent-50": "#fffbeb",
    "accent-100": "#fff3c4",
    "accent-200": "#ffe880",
    "accent-300": "#ffdb40",
    "accent-400": "#ffcc00",
    "accent-500": "#f0b400",  # Principal
    "accent-600": "#cc9600",
    "accent-700": "#a67a00",
    "accent-800": "#805e00",
    "accent-900": "#594200",
    "accent-950": "#332600",
    # Neutral — tons de cinza quente
    "neutral-50": "#fafaf9",
    "neutral-100": "#f2f2f0",
    "neutral-200": "#e3e3df",
    "neutral-300": "#cdccc7",
    "neutral-400": "#a8a7a0",
    "neutral-500": "#84837b",
    "neutral-600": "#65645d",
    "neutral-700": "#4f4e48",
    "neutral-800": "#3a3a35",
    "neutral-900": "#262623",
    "neutral-950": "#141412",
    # Success — verde quantum
    "success": "#00e676",
    "warning": "#ffab00",
    "error": "#ff1744",
    "info": "#00b0ff",
    # Background
    "bg-dark": "#0a0a0f",
    "bg-card": "#12121f",
    "bg-elevated": "#1a1a2e",
    "bg-light": "#f8f7ff",
    # Text
    "text-primary": "#f0f0ff",
    "text-secondary": "#a0a0c0",
    "text-muted": "#606080",
    "text-inverse": "#0a0a0f",
    # Borders
    "border": "#2a2a3e",
    "border-light": "#3a3a5e",
    "border-focus": "#7c2dff",
}

# ── Gradients ─────────────────────────────────────────────────
LYZER_GRADIENTS: Dict[str, str] = {
    "quantum": "linear-gradient(135deg, #7c2dff 0%, #00aaff 100%)",
    "quantum-dark": "linear-gradient(135deg, #250673 0%, #00334d 100%)",
    "sunset": "linear-gradient(135deg, #7c2dff 0%, #f0b400 100%)",
    "neon": "linear-gradient(135deg, #00e676 0%, #00b0ff 100%)",
    "fire": "linear-gradient(135deg, #ff1744 0%, #ffab00 100%)",
    "deep": "linear-gradient(180deg, #0a0a0f 0%, #12121f 50%, #1a1a2e 100%)",
    "card": "linear-gradient(145deg, #1a1a2e 0%, #12121f 100%)",
    "glow": "radial-gradient(circle at 50% 0%, #7c2dff22 0%, transparent 70%)",
}

# ── Shadows ───────────────────────────────────────────────────
LYZER_SHADOWS: Dict[str, str] = {
    "sm": "0 1px 2px rgba(0,0,0,0.3)",
    "md": "0 4px 6px rgba(0,0,0,0.4)",
    "lg": "0 8px 24px rgba(0,0,0,0.5)",
    "xl": "0 12px 48px rgba(0,0,0,0.6)",
    "glow": "0 0 20px rgba(124,45,255,0.3)",
    "glow-blue": "0 0 20px rgba(0,170,255,0.3)",
    "glow-gold": "0 0 20px rgba(240,180,0,0.3)",
    "inner": "inset 0 1px 3px rgba(0,0,0,0.3)",
}

# ── Typography ────────────────────────────────────────────────
LYZER_TYPOGRAPHY: Dict[str, Dict[str, str]] = {
    "font-family": {
        "sans": "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
        "display": "'Space Grotesk', 'Inter', sans-serif",
        "mono": "'JetBrains Mono', 'Fira Code', monospace",
    },
    "font-size": {
        "xs": "0.75rem",
        "sm": "0.875rem",
        "base": "1rem",
        "lg": "1.125rem",
        "xl": "1.25rem",
        "2xl": "1.5rem",
        "3xl": "1.875rem",
        "4xl": "2.25rem",
        "5xl": "3rem",
        "6xl": "3.75rem",
        "7xl": "4.5rem",
    },
    "font-weight": {
        "normal": "400",
        "medium": "500",
        "semibold": "600",
        "bold": "700",
        "extrabold": "800",
    },
    "line-height": {
        "tight": "1.1",
        "normal": "1.5",
        "relaxed": "1.75",
    },
    "letter-spacing": {
        "tight": "-0.02em",
        "normal": "0",
        "wide": "0.02em",
        "wider": "0.05em",
    },
}

# ── Spacing ───────────────────────────────────────────────────
LYZER_SPACING: Dict[str, str] = {
    "0": "0",
    "px": "1px",
    "0.5": "0.125rem",
    "1": "0.25rem",
    "2": "0.5rem",
    "3": "0.75rem",
    "4": "1rem",
    "5": "1.25rem",
    "6": "1.5rem",
    "8": "2rem",
    "10": "2.5rem",
    "12": "3rem",
    "16": "4rem",
    "20": "5rem",
    "24": "6rem",
    "32": "8rem",
    "40": "10rem",
    "48": "12rem",
    "56": "14rem",
    "64": "16rem",
}

# ── Border Radius ─────────────────────────────────────────────
LYZER_RADIUS: Dict[str, str] = {
    "none": "0",
    "sm": "0.25rem",
    "md": "0.5rem",
    "lg": "0.75rem",
    "xl": "1rem",
    "2xl": "1.5rem",
    "full": "9999px",
}


# ═══════════════════════════════════════════════════════════════
# Generators
# ═══════════════════════════════════════════════════════════════


def generate_css_variables(prefix: str = "lyzer") -> str:
    """Gera variáveis CSS custom properties a partir dos tokens."""
    lines = [":root {"]
    for name, value in LYZER_COLORS.items():
        lines.append(f"  --{prefix}-{name}: {value};")
    # Gradients
    for name, value in LYZER_GRADIENTS.items():
        lines.append(f"  --{prefix}-gradient-{name}: {value};")
    # Shadows
    for name, value in LYZER_SHADOWS.items():
        lines.append(f"  --{prefix}-shadow-{name}: {value};")
    # Typography
    for category, tokens in LYZER_TYPOGRAPHY.items():
        css_name = category.replace("_", "-")
        for name, value in tokens.items():
            lines.append(f"  --{prefix}-{css_name}-{name}: {value};")
    # Spacing
    for name, value in LYZER_SPACING.items():
        if name in ("0", "px", "0.5", "1", "2", "3"):
            lines.append(f"  --{prefix}-space-{name}: {value};")
    # Border radius
    for name, value in LYZER_RADIUS.items():
        lines.append(f"  --{prefix}-radius-{name}: {value};")
    lines.append("}")
    return "\n".join(lines)


def generate_tailwind_config() -> str:
    """Gera configuração Tailwind CSS para o design system Lyzer Labs."""
    return f"""// tailwind.config.js
module.exports = {{
  theme: {{
    extend: {{
      colors: {{
        primary: {{
          50:  '{LYZER_COLORS["primary-50"]}',
          100: '{LYZER_COLORS["primary-100"]}',
          200: '{LYZER_COLORS["primary-200"]}',
          300: '{LYZER_COLORS["primary-300"]}',
          400: '{LYZER_COLORS["primary-400"]}',
          500: '{LYZER_COLORS["primary-500"]}',
          600: '{LYZER_COLORS["primary-600"]}',
          700: '{LYZER_COLORS["primary-700"]}',
          800: '{LYZER_COLORS["primary-800"]}',
          900: '{LYZER_COLORS["primary-900"]}',
          950: '{LYZER_COLORS["primary-950"]}',
        }},
        secondary: {{
          50:  '{LYZER_COLORS["secondary-50"]}',
          100: '{LYZER_COLORS["secondary-100"]}',
          200: '{LYZER_COLORS["secondary-200"]}',
          300: '{LYZER_COLORS["secondary-300"]}',
          400: '{LYZER_COLORS["secondary-400"]}',
          500: '{LYZER_COLORS["secondary-500"]}',
          600: '{LYZER_COLORS["secondary-600"]}',
          700: '{LYZER_COLORS["secondary-700"]}',
          800: '{LYZER_COLORS["secondary-800"]}',
          900: '{LYZER_COLORS["secondary-900"]}',
          950: '{LYZER_COLORS["secondary-950"]}',
        }},
        accent: {{
          50:  '{LYZER_COLORS["accent-50"]}',
          100: '{LYZER_COLORS["accent-100"]}',
          200: '{LYZER_COLORS["accent-200"]}',
          300: '{LYZER_COLORS["accent-300"]}',
          400: '{LYZER_COLORS["accent-400"]}',
          500: '{LYZER_COLORS["accent-500"]}',
          600: '{LYZER_COLORS["accent-600"]}',
          700: '{LYZER_COLORS["accent-700"]}',
          800: '{LYZER_COLORS["accent-800"]}',
          900: '{LYZER_COLORS["accent-900"]}',
          950: '{LYZER_COLORS["accent-950"]}',
        }},
        neutral: {{
          50:  '{LYZER_COLORS["neutral-50"]}',
          100: '{LYZER_COLORS["neutral-100"]}',
          200: '{LYZER_COLORS["neutral-200"]}',
          300: '{LYZER_COLORS["neutral-300"]}',
          400: '{LYZER_COLORS["neutral-400"]}',
          500: '{LYZER_COLORS["neutral-500"]}',
          600: '{LYZER_COLORS["neutral-600"]}',
          700: '{LYZER_COLORS["neutral-700"]}',
          800: '{LYZER_COLORS["neutral-800"]}',
          900: '{LYZER_COLORS["neutral-900"]}',
          950: '{LYZER_COLORS["neutral-950"]}',
        }},
        success: '{LYZER_COLORS["success"]}',
        warning: '{LYZER_COLORS["warning"]}',
        error:   '{LYZER_COLORS["error"]}',
        info:    '{LYZER_COLORS["info"]}',
      }},
      fontFamily: {{
        sans:    {json_quote(LYZER_TYPOGRAPHY["font-family"]["sans"])},
        display: {json_quote(LYZER_TYPOGRAPHY["font-family"]["display"])},
        mono:    {json_quote(LYZER_TYPOGRAPHY["font-family"]["mono"])},
      }},
      backgroundImage: {{
        'gradient-quantum':  '{LYZER_GRADIENTS["quantum"]}',
        'gradient-sunset':   '{LYZER_GRADIENTS["sunset"]}',
        'gradient-neon':     '{LYZER_GRADIENTS["neon"]}',
        'gradient-deep':     '{LYZER_GRADIENTS["deep"]}',
        'gradient-card':     '{LYZER_GRADIENTS["card"]}',
        'gradient-glow':     '{LYZER_GRADIENTS["glow"]}',
      }},
      boxShadow: {{
        'glow':     '{LYZER_SHADOWS["glow"]}',
        'glow-blue':'{LYZER_SHADOWS["glow-blue"]}',
        'glow-gold':'{LYZER_SHADOWS["glow-gold"]}',
      }},
    }}
  }}
}}"""


def json_quote(s: str) -> str:
    """Simple helper — wraps string in quotes, safe for tailwind config."""
    return '"' + s.replace('"', '\\"') + '"'
