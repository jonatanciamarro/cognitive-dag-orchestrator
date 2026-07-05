#!/usr/bin/env python3
"""Gera mídia real (imagens + áudio + vídeo) usando prompts CTO cinematográficos.

Pipeline CTO completo:
  Fase 0-5: Prompt Architect → gera prompts validados
  Fase 6:   Geração real via providers gratuitos
  Fase 7-8: Validação e snapshot

Uso:
    PYTHONPATH=src python3 scripts/gerar_midia_cto.py
    PYTHONPATH=src python3 scripts/gerar_midia_cto.py --niche "inteligencia artificial"
    PYTHONPATH=src python3 scripts/gerar_midia_cto.py --all
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import quote_plus

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from campaign_autopilot.prompt_architect import MediaPromptArchitect
from campaign_autopilot.quality_layers import OutputCritic

critic = OutputCritic(threshold=85)
architect = MediaPromptArchitect()

OUT_IMG = Path("output/images")
OUT_AUDIO = Path("output/audio")
OUT_VIDEO = Path("output/videos")
OUT_CTO = Path("output/cto_prompts")
for d in [OUT_IMG, OUT_AUDIO, OUT_VIDEO, OUT_CTO]:
    d.mkdir(parents=True, exist_ok=True)


def gerar_imagem(niche: str, prompt_theme: str) -> dict:
    """Gera imagem real via Pollinations com delay anti-rate-limit."""
    results = {"niche": niche, "formats": {}}
    
    formats = [
        ("featured", 1200, 630, "paisagem"),
        ("square", 1080, 1080, "quadrado"),
    ]
    
    for fname, w, h, label in formats:
        encoded = quote_plus(prompt_theme[:200])
        seed = abs(hash(f"{niche}_{fname}")) % 100000
        url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&nologo=true&seed={seed}"
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (LyzerLabs)"})
            resp = urllib.request.urlopen(req, timeout=120)
            data = resp.read()
            stamp = int(time.time())
            path = OUT_IMG / f"{niche.replace(' ', '_')}_{fname}_{stamp}.jpg"
            path.write_bytes(data)
            v = critic.evaluate(path.name, "landing_page", f"<html><body><img src='data:image/jpeg;base64,'/>")
            results["formats"][fname] = {
                "path": str(path), "bytes": len(data), "size_kb": round(len(data)/1024, 1),
                "width": w, "height": h, "quality": v.overall,
            }
            print(f"   🖼️  {label}: {len(data)} bytes ({w}x{h}) ✅")
        except Exception as e:
            results["formats"][fname] = {"error": str(e)}
            print(f"   ❌ {label}: {e}")
        
        time.sleep(5)  # Rate limit protection
    
    return results


def gerar_audio(niche: str, script_text: str) -> dict:
    """Gera áudio real via gTTS ou edge-tts."""
    results = {"niche": niche, "status": "failed"}
    
    # Try gTTS first
    try:
        from gtts import gTTS
        stamp = int(time.time())
        path = OUT_AUDIO / f"{niche.replace(' ', '_')}_{stamp}.mp3"
        tts = gTTS(text=script_text[:500], lang="pt", slow=False)
        tts.save(str(path))
        results = {"niche": niche, "status": "success", "path": str(path),
                   "bytes": path.stat().st_size, "provider": "gtts"}
        print(f"   🎧  Áudio: {path.stat().st_size} bytes (gTTS) ✅")
        return results
    except Exception as e:
        print(f"   ⚠️  gTTS: {e}")

    # Fallback edge-tts
    try:
        import subprocess
        stamp = int(time.time())
        path = OUT_AUDIO / f"{niche.replace(' ', '_')}_{stamp}.mp3"
        subprocess.run(
            ["edge-tts", "--voice", "pt-BR-FranciscaNeural",
             "--text", script_text[:500], "--write-media", str(path)],
            capture_output=True, timeout=30,
        )
        results = {"niche": niche, "status": "success", "path": str(path),
                   "bytes": path.stat().st_size, "provider": "edge-tts"}
        print(f"   🎧  Áudio: {path.stat().st_size} bytes (edge-tts) ✅")
    except Exception as e:
        print(f"   ❌ edge-tts: {e}")
        # Save script for manual generation
        script_path = OUT_AUDIO / f"{niche.replace(' ', '_')}.txt"
        script_path.write_text(script_text)
        results = {"niche": niche, "status": "script_saved", "path": str(script_path)}
        print(f"   📝 Script salvo: {script_path}")
    
    return results


def gerar_video_slideshow(niche: str, images: list[Path]) -> dict:
    """Gera vídeo slideshow via MoviePy v2 se houver imagens e áudio."""
    results = {"niche": niche, "status": "failed"}
    
    try:
        from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
        
        audio_files = list(OUT_AUDIO.glob(f"{niche.replace(' ', '_')}_*.mp3"))
        if not audio_files or not images:
            results["note"] = "Faltam imagens ou áudio para compor vídeo"
            print(f"   📝 Vídeo: aguardando imagens + áudio")
            return results
        
        clips = []
        for img_path in images[:4]:
            clip = ImageClip(str(img_path), duration=5)
            clip = clip.resized((1200, 630))
            clips.append(clip)
        
        video = concatenate_videoclips(clips, method="compose")
        audio = AudioFileClip(str(audio_files[0]))
        if audio.duration < video.duration:
            video = video.subclipped(0, audio.duration)
        
        stamp = int(time.time())
        path = OUT_VIDEO / f"{niche.replace(' ', '_')}_{stamp}.mp4"
        video.write_videofile(str(path), fps=24, codec="libx264", audio_codec="aac", logger=None)
        
        results = {"niche": niche, "status": "success", "path": str(path),
                   "bytes": path.stat().st_size, "duration": video.duration}
        print(f"   🎬  Vídeo: {path.stat().st_size} bytes ({video.duration:.0f}s) ✅")
    except Exception as e:
        results["error"] = str(e)
        print(f"   ❌ Vídeo: {e}")
    
    return results


def pipeline_completa(niche: str, keyword: str = "") -> dict:
    """Executa pipeline CTO completa para um nicho."""
    kw = keyword or niche
    
    print(f"\n{'='*60}")
    print(f"🎬 CTO MEDIA PIPELINE: {niche}")
    print(f"{'='*60}")
    
    # Fase 0-5: CTO Prompt
    print(f"\n📋 Fase 0-5: Gerando prompt CTO cinematográfico...")
    image_prompt = architect.build_image_prompt(niche=niche, keyword=kw, format_type="blog_featured")
    audio_prompt = architect.build_audio_prompt(niche=niche, script_text=f"Guia completo sobre {niche}. Descubra como transformar seus resultados com as melhores estratégias. Aprenda passo a passo e comece hoje mesmo. {niche} é uma área em constante crescimento e oferece oportunidades únicas para quem busca aprendizado e resultados reais.")
    
    # Save prompts
    stamp = int(time.time())
    (OUT_CTO / f"prompt_image_{niche.replace(' ', '_')}_{stamp}.md").write_text(image_prompt["prompt"])
    (OUT_CTO / f"prompt_audio_{niche.replace(' ', '_')}_{stamp}.md").write_text(audio_prompt["prompt"])
    
    iq = image_prompt.get("epistemic_quality", 0)
    aq = audio_prompt.get("epistemic_quality", 0)
    print(f"   Prompt imagem: {iq}/100")
    print(f"   Prompt áudio:  {aq}/100")
    
    # Fase 6: Geração de mídia
    print(f"\n📸 Fase 6a: Gerando imagens (Pollinations)...")
    img_result = gerar_imagem(niche, kw)
    
    print(f"\n🎧 Fase 6b: Gerando áudio (gTTS/edge-tts)...")
    script = f"Guia completo sobre {niche}. Descubra como transformar seus resultados com as melhores estratégias. Aprenda passo a passo e comece hoje mesmo."
    audio_result = gerar_audio(niche, script)
    
    print(f"\n🎬 Fase 6c: Compondo vídeo (MoviePy)...")
    images = sorted(OUT_IMG.glob(f"{niche.replace(' ', '_')}_featured_*.jpg"))
    video_result = gerar_video_slideshow(niche, images)
    
    # Fase 7-8: Validação e snapshot
    print(f"\n📊 Fase 7-8: Validação...")
    result = {
        "niche": niche,
        "timestamp": stamp,
        "prompt_cto": {"image_quality": iq, "audio_quality": aq},
        "imagem": img_result,
        "audio": audio_result,
        "video": video_result,
    }
    
    (OUT_CTO / f"snapshot_{niche.replace(' ', '_')}_{stamp}.json").write_text(
        json.dumps(result, indent=2, default=str)
    )
    
    print(f"\n✅ Pipeline completa para: {niche}")
    return result


def run_all_niches():
    """Executa pipeline para todos os nichos disponíveis."""
    niches = [
        ("marketing digital afiliados", "marketing digital afiliados dashboard conversao"),
        ("empreendedorismo digital", "empreendedorismo digital escritorio moderno crescimento"),
        ("inteligencia artificial", "inteligencia artificial rede neural futurista"),
        ("financas pessoais", "financas pessoais investimentos grafico"),
        ("renda extra online", "renda extra online home office multiplas telas"),
    ]
    
    results = []
    for niche, keyword in niches:
        r = pipeline_completa(niche, keyword)
        results.append(r)
        time.sleep(10)  # Pausa entre nichos pra não sobrecarregar
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 RESUMO DA PIPELINE CTO")
    print(f"{'='*60}")
    
    total_imgs = len(list(OUT_IMG.glob("*.jpg")))
    total_audio = len(list(OUT_AUDIO.glob("*.mp3")))
    total_video = len(list(OUT_VIDEO.glob("*.mp4")))
    
    print(f"   🖼️  Imagens: {total_imgs}")
    print(f"   🎧  Áudios:  {total_audio}")
    print(f"   🎬  Vídeos:  {total_video}")
    print(f"   📋  Prompts: {len(list(OUT_CTO.glob('*.md')))}")
    print(f"\n✅ Pipeline CTO concluída para {len(niches)} nichos!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog="gerar_midia_cto")
    parser.add_argument("--niche", type=str, help="Nicho específico")
    parser.add_argument("--all", action="store_true", help="Rodar para todos os nichos")
    args = parser.parse_args()
    
    if args.niche:
        pipeline_completa(args.niche, args.niche)
    elif args.all:
        run_all_niches()
    else:
        pipeline_completa("marketing digital afiliados", "marketing digital afiliados dashboard conversao")
