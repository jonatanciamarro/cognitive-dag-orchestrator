"""Presentation Generator — Slide decks & presentations."""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class SlideType(str, Enum):
    TITLE = "title"
    CONTENT = "content"
    SECTION = "section"
    METRICS = "metrics"
    COMPARISON = "comparison"
    QUOTE = "quote"
    IMAGE = "image"
    THANK_YOU = "thank_you"


@dataclass
class SlideSection:
    """Content section within a slide."""

    type: str = "text"
    content: str = ""
    level: int = 1  # heading level
    columns: int = 1


@dataclass
class SlideSpec:
    """Individual slide specification."""

    type: SlideType = SlideType.CONTENT
    title: str = ""
    subtitle: str = ""
    sections: List[SlideSection] = field(default_factory=list)
    background: str = "default"
    notes: str = ""


@dataclass
class PresentationTheme:
    """Theme for the presentation."""

    name: str = "lyzer-dark"
    primary_color: str = "#7c2dff"
    secondary_color: str = "#00aaff"
    accent_color: str = "#f0b400"
    background: str = "#0a0a0f"
    text_color: str = "#f0f0ff"
    font_display: str = "'Space Grotesk', sans-serif"
    font_body: str = "'Inter', sans-serif"


@dataclass
class PresentationSpec:
    """Complete presentation specification."""

    title: str = ""
    subtitle: str = ""
    author: str = "Lyzer Labs"
    date: str = ""
    slides: List[SlideSpec] = field(default_factory=list)
    theme: PresentationTheme = field(default_factory=PresentationTheme)
    company_logo: str = "Lyzer <span>Labs</span>"


class PresentationGenerator:
    """Generates HTML slide presentations from spec."""

    def __init__(self):
        pass

    def generate(self, spec: PresentationSpec, output_dir: str = "output") -> str:
        """Generate a standalone HTML presentation."""
        theme = spec.theme
        slide_htmls = []

        for i, slide in enumerate(spec.slides):
            sections_html = ""
            for sec in slide.sections:
                if sec.type == "text":
                    if sec.level == 1:
                        sections_html += f"<h3>{html.escape(sec.content)}</h3>"
                    elif sec.level == 2:
                        sections_html += f"<h4>{html.escape(sec.content)}</h4>"
                    else:
                        sections_html += f"<p>{html.escape(sec.content)}</p>"
                elif sec.type == "list":
                    items = sec.content.split("\n")
                    sections_html += (
                        "<ul>"
                        + "".join(
                            f"<li>{html.escape(item.strip())}</li>"
                            for item in items
                            if item.strip()
                        )
                        + "</ul>"
                    )
                elif sec.type == "metric":
                    parts = sec.content.split("|")
                    if len(parts) >= 2:
                        sections_html += (
                            f'<div style="text-align: center; padding: 1rem;">'
                            f'<div style="font-size: 3rem; font-weight: 800; '
                            f'font-family: {theme.font_display}; color: {theme.accent_color};">'
                            f"{html.escape(parts[0].strip())}</div>"
                            f'<div style="color: {theme.secondary_color};">'
                            f"{html.escape(parts[1].strip())}</div></div>"
                        )

            bg_style = (
                slide.background if slide.background != "default" else theme.background
            )
            slide_class = f"slide-{slide.type.value}"

            slide_htmls.append(f"""<div class="slide {slide_class}" style="background: {bg_style};">
              <div class="slide-header">
                <span class="slide-number">{i + 1}</span>
                <span class="slide-logo">{spec.company_logo}</span>
              </div>
              <div class="slide-content">
                <h2 class="slide-title">{html.escape(slide.title)}</h2>
                {f'<p class="slide-subtitle">{html.escape(slide.subtitle)}</p>' if slide.subtitle else ""}
                {sections_html}
              </div>
              {f'<div class="slide-notes">{html.escape(slide.notes)}</div>' if slide.notes else ""}
            </div>""")

        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(spec.title)} — Lyzer Labs</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: {theme.font_body}; background: {theme.background}; color: {theme.text_color}; }}
    .presentation {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
    .slide {{
      min-height: 80vh; display: flex; flex-direction: column;
      padding: 3rem; margin-bottom: 2rem;
      background: {theme.background};
      border: 1px solid #2a2a3e; border-radius: 1.5rem;
      position: relative; overflow: hidden;
    }}
    .slide::before {{
      content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
      background: radial-gradient(circle at 50% 0%, {theme.primary_color}11 0%, transparent 70%);
    }}
    .slide-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; position: relative; z-index: 1; }}
    .slide-number {{ font-size: 0.875rem; color: #606080; font-family: {theme.font_display}; }}
    .slide-logo {{ font-family: {theme.font_display}; font-weight: 800; font-size: 1.25rem; }}
    .slide-logo span {{ color: {theme.primary_color}; }}
    .slide-content {{ flex: 1; display: flex; flex-direction: column; justify-content: center; position: relative; z-index: 1; }}
    .slide-title {{ font-family: {theme.font_display}; font-size: 3rem; font-weight: 800; margin-bottom: 1rem; }}
    .slide-subtitle {{ color: #a0a0c0; font-size: 1.25rem; margin-bottom: 2rem; }}
    .slide-title {{ font-size: 2.5rem; }}
    .slide-content h3 {{ font-family: {theme.font_display}; font-size: 1.75rem; margin-top: 1.5rem; margin-bottom: 0.75rem; }}
    .slide-content h4 {{ font-family: {theme.font_display}; font-size: 1.25rem; margin-top: 1rem; margin-bottom: 0.5rem; color: {theme.secondary_color}; }}
    .slide-content p {{ line-height: 1.75; color: #a0a0c0; margin-bottom: 0.75rem; font-size: 1.125rem; }}
    .slide-content ul {{ list-style: none; margin: 1rem 0; }}
    .slide-content ul li {{ padding: 0.5rem 0; padding-left: 1.5rem; position: relative; color: #a0a0c0; }}
    .slide-content ul li::before {{ content: '▸'; position: absolute; left: 0; color: {theme.primary_color}; }}
    .slide-notes {{ margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #2a2a3e; font-size: 0.8rem; color: #606080; }}
    .slide-title.slide {{ text-align: center; }}
    .slide-title.slide .slide-content {{ align-items: center; }}
    .slide-title.slide .slide-title {{ font-size: 4rem; }}
    .slide-metrics.slide .slide-content {{ flex-direction: row; flex-wrap: wrap; gap: 1rem; justify-content: center; }}
    @media (max-width: 768px) {{ .slide {{ padding: 1.5rem; min-height: 60vh; }} .slide-title {{ font-size: 1.75rem; }} }}
    .nav-controls {{ position: fixed; bottom: 2rem; right: 2rem; display: flex; gap: 0.5rem; z-index: 100; }}
    .nav-btn {{ padding: 0.75rem 1.5rem; background: {theme.primary_color}; color: white; border: none; border-radius: 0.75rem; cursor: pointer; font-weight: 600; }}
    .nav-btn:hover {{ opacity: 0.9; }}
  </style>
</head>
<body>
  <div class="presentation" id="presentation">
    <header class="slide slide-title" style="background: linear-gradient(135deg, {theme.background} 0%, #1a0a2e 100%);">
      <div class="slide-content" style="align-items: center; text-align: center;">
        <h1 class="slide-title" style="font-size: 4rem; background: linear-gradient(135deg, {theme.text_color} 0%, {theme.secondary_color} 50%, {theme.primary_color} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{html.escape(spec.title)}</h1>
        {f'<p class="slide-subtitle" style="font-size: 1.5rem;">{html.escape(spec.subtitle)}</p>' if spec.subtitle else ""}
        <p style="color: #606080; margin-top: 2rem;">{html.escape(spec.author)} | {spec.date or datetime.utcnow().strftime("%B %Y")}</p>
      </div>
    </header>
    {"".join(slide_htmls)}
    <footer class="slide" style="align-items: center; justify-content: center; text-align: center; min-height: 40vh;">
      <div class="slide-content">
        <h2 style="font-family: {theme.font_display}; font-size: 3rem; margin-bottom: 1rem;">Obrigado!</h2>
        <p style="color: #a0a0c0; font-size: 1.25rem;">{html.escape(spec.author)}</p>
      </div>
    </footer>
  </div>
  <div class="nav-controls">
    <button class="nav-btn" onclick="document.getElementById('presentation').scrollBy(0, -window.innerHeight * 0.8)">← Anterior</button>
    <button class="nav-btn" onclick="document.getElementById('presentation').scrollBy(0, window.innerHeight * 0.8)">Próximo →</button>
  </div>
  <script>
    document.addEventListener('keydown', function(e) {{
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {{
        document.getElementById('presentation').scrollBy(0, window.innerHeight * 0.8);
      }} else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {{
        document.getElementById('presentation').scrollBy(0, -window.innerHeight * 0.8);
      }}
    }});
  </script>
</body>
</html>"""

        filepath = (
            f"{output_dir}/{spec.title.lower().replace(' ', '_')}_presentation.html"
        )
        import os

        os.makedirs(output_dir, exist_ok=True)
        with open(filepath, "w") as f:
            f.write(html_content)

        return filepath
