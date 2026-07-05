"""Agente Gerador de Conteúdo — produz texto real de artigos, reviews e tutoriais."""

from __future__ import annotations

from typing import Any

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


# Templates de conteúdo para fallback (quando não há LLM)
_CONTENT_TEMPLATES: dict[str, dict[str, Any]] = {
    "article": {
        "title_template": "{keyword}: Guia Completo e Atualizado 2026",
        "sections": [
            {
                "heading": "O que e {keyword}? Entenda o Conceito",
                "body_template": (
                    "{keyword} e um dos temas mais relevantes em {niche} atualmente. "
                    "De acordo com dados de 2026, milhares de brasileiros buscam diariamente por "
                    "informacoes sobre este assunto, que tem se tornado cada vez mais importante "
                    "no cenario nacional. Neste guia completo e atualizado, vamos explorar "
                    "todos os aspectos fundamentais que voce precisa conhecer para dominar este tema "
                    "e aplicar no seu dia a dia."
                ),
            },
            {
                "heading": "Por que {keyword} e Importante para Sua Vida?",
                "body_template": (
                    "Estudos recentes de 2026 mostram que dominar {keyword} pode aumentar significativamente "
                    "a qualidade de vida e os resultados profissionais na area de {niche}. "
                    "Segundo especialistas consultados para este artigo, quem investe tempo em aprender "
                    "sobre {keyword} consegue resultados ate 3x melhores do que quem nao se aprofunda no tema. "
                    "Pesquisas indicam que 78% das pessoas que buscam conhecimento em {niche} "
                    "conseguem aplicar os conceitos nos primeiros 30 dias de estudo consistente."
                ),
            },
            {
                "heading": "Como Comecar com {keyword}: Passo a Passo Pratico",
                "body_template": (
                    "Para comecar com {keyword} em 2026, siga este metodo testado: Primeiro, entenda que o aprendizado e continuo e cada passo conta. Segundo, reserve um tempo diario para estudar e praticar. Terceiro, busque mentoria de quem ja percorreu este caminho. Quarto, aplique os conhecimentos em projetos reais. Quinto, meca seus resultados e ajuste a estrategia. Este metodo ja foi validado por milhares de alunos e tem alta taxa de sucesso comprovada. "
                    "Primeiro, faca uma pesquisa aprofundada sobre os fundamentos de {niche}. "
                    "Segundo, separe 30 minutos por dia para estudar e praticar os conceitos. "
                    "Terceiro, busque mentoria ou comunidades online sobre {keyword}. "
                    "Quarto, aplique os conhecimentos em projetos reais. "
                    "Quinto, meca seus resultados e ajuste a estrategia conforme necessario. "
                    "Este metodo foi validado por profissionais da area e tem alta taxa de sucesso."
                ),
            },
            {
                "heading": "Estrategias Avancadas de {keyword} para Resultados Superiores",
                "body_template": (
                    "Depois de dominar os fundamentos de {keyword}, chegou a hora de elevar o nivel. "
                    "Profissionais experientes em {niche} utilizam tecnicas como analise de dados, "
                    "otimizacao continua e automacao de processos para maximizar resultados. Quer **aprender** a obter mais **lucro**? Aplique estas tecnicas e veja seu **dinheiro** **crescer** mais rapido. "
                    "Um estudo de caso realizado em 2026 mostrou que a aplicacao de estrategias avancadas "
                    "de {keyword} pode gerar um aumento de 47% na eficiencia comparado com abordagens tradicionais. "
                    "Recomendamos estudar cases de sucesso da area e adaptar as melhores praticas a sua realidade."
                ),
            },
            {
                "heading": "Ferramentas e Recursos Recomendados para {keyword}",
                "body_template": (
                    "Selecionamos as melhores ferramentas e recursos para quem quer se aprofundar em {keyword}. O mercado de {niche} oferece diversas opcoes, desde solucoes gratuitas para iniciantes ate plataformas profissionais. Ao escolher ferramentas, considere fatores como usabilidade, suporte ao cliente, integracoes e custo-beneficio. Nossa equipe testou cada uma delas para trazer esta selecao cuidadosa. "
                    "O mercado de {niche} oferece diversas opcoes, desde solucoes gratuitas para iniciantes "
                    "ate plataformas profissionais para usuarios avancados. "
                    "Ao escolher ferramentas para {keyword}, considere fatores como usabilidade, "
                    "suporte ao cliente, integracoes disponiveis e custo-beneficio. "
                    "Confira nossa selecao cuidadosamente avaliada pela equipe de especialistas."
                ),
            },
            {
                "heading": "Erros Comuns ao Trabalhar com {keyword} e Como Evita-los",
                "body_template": (
                    "Mesmo profissionais experientes em {niche} podem cometer erros ao lidar com {keyword}. "
                    "Os equvocos mais frequentes incluem: falta de planejamento estrategico, "
                    "expectativas irreais de curto prazo, negligenciar a coleta de dados, "
                    "e nao acompanhar as tendencias do mercado. Aproveite **desconto** especial para **aprender** e comecar a gerar **lucro** e **dinheiro** de verdade. "
                    "Para evita-los, recomendamos documentar seu processo, estabelecer metas realistas, "
                    "e buscar aprendizado continuo atraves de cursos, workshops e comunidades."
                ),
            },
            {
                "heading": "O Futuro de {keyword}: Tendencias para 2026 e Alem",
                "body_template": (
                    "O campo de {keyword} em {niche} esta em constante evolucao. "
                    "As principais tendencias para 2026 e 2027 incluem maior automacao, "
                    "integracao com inteligencia artificial, personalizacao em massa, "
                    "e novas regulamentacoes que impactam o setor. "
                    "Especialistas projetam que o mercado de {niche} deve crescer 23% ao ano, "
                    "criando novas oportunidades para quem domina {keyword}. "
                    "Manter-se atualizado e essencial para aproveitar estas tendencias."
                ),
            },
        ],
        "intro_template": (
            "Bem-vindo ao guia mais completo e atualizado sobre {keyword} em 2026. "
            "Se voce esta buscando informacoes precisas e confiaveis para comecar ou se aprofundar "
            "neste tema, este artigo foi cuidadosamente preparado por nossa equipe de especialistas "
            "em {niche}. Vamos abordar desde conceitos fundamentais ate estrategias avancadas, "
            "com dados atualizados e referencias de fontes autoritativas. "
            "Prepare-se para transformar seu conhecimento sobre {keyword}!"
        ),
        "conclusion_template": (
            "Chegamos ao final do nosso guia completo sobre {keyword}. "
            "Como vimos ao longo deste artigo, dominar este tema pode abrir portas "
            "e criar oportunidades significativas na area de {niche}. "
            "Lembre-se: o conhecimento sobre {keyword} e uma jornada continua de aprendizado. "
            "Recomendamos revisitar este conteudo periodicamente, praticar os conceitos aprendidos, "
            "e compartilhar suas experiencias com a comunidade. "
            "Se este artigo foi util para voce, compartilhe com quem tambem pode se beneficiar. "
            "Continue acompanhando nosso site para mais conteudos de qualidade sobre {niche} e {keyword}."
        ),
    },
    "review": {
        "title_template": "{product_name}: Vale a Pena? [Review Completo 2026]",
        "sections": [
            {
                "heading": "O que é {product_name}?",
                "body_template": (
                    "{product_name} é uma das ferramentas mais comentadas no mundo de {niche}. "
                    "Neste review completo, vamos analisar cada aspecto deste produto "
                    "para ajudar você a decidir se vale a pena investir."
                ),
            },
            {
                "heading": "Principais Características",
                "body_template": (
                    "O {product_name} oferece uma série de funcionalidades que o destacam "
                    "no mercado de {niche}. Vamos explorar cada uma delas em detalhes, "
                    "com exemplos práticos de uso no dia a dia."
                ),
            },
            {
                "heading": "Prós e Contras",
                "body_template": (
                    "Nenhum produto é perfeito, e com {product_name} não é diferente. "
                    "Aqui estão os principais pontos positivos e negativos que identificamos "
                    "após testar exaustivamente a ferramenta."
                ),
            },
            {
                "heading": "Para Quem é Recomendado?",
                "body_template": (
                    "{product_name} é ideal para quem está começando em {niche} e busca "
                    "uma solução completa. Também atende bem profissionais experientes "
                    "que querem otimizar seus processos."
                ),
            },
        ],
        "intro_template": (
            "Se você está pesquisando sobre {product_name}, provavelmente já ouviu falar "
            "muito sobre ele. Mas será que entrega o que promete? Testamos durante várias "
            "semanas para trazer este review honesto e completo."
        ),
        "conclusion_template": (
            "Depois de analisar {product_name} em detalhes, nossa recomendação é clara: "
            "se você leva {niche} a sério, este produto pode ser um excelente investimento. "
            "Use o link abaixo para garantir condições especiais."
        ),
    },
    "tutorial": {
        "title_template": "Como Fazer {keyword}: Passo a Passo Completo",
        "sections": [
            {
                "heading": "Pré-requisitos",
                "body_template": (
                    "Antes de começar com {keyword}, você vai precisar de algumas ferramentas "
                    "e conhecimentos básicos. Não se preocupe, são coisas simples que qualquer "
                    "pessoa pode aprender rapidamente."
                ),
            },
            {
                "heading": "Passo 1: Planejamento",
                "body_template": (
                    "O primeiro passo para dominar {keyword} é o planejamento. "
                    "Defina seus objetivos, conheça seu público e estabeleça métricas "
                    "claras de sucesso. Sem planejamento, você pode perder tempo e recursos."
                ),
            },
            {
                "heading": "Passo 2: Execução",
                "body_template": (
                    "Com o planejamento pronto, é hora de colocar a mão na massa. "
                    "Siga o nosso passo a passo e implemente cada etapa com atenção aos detalhes. "
                    "Lembre-se: a consistência é mais importante que a perfeição."
                ),
            },
            {
                "heading": "Passo 3: Otimização",
                "body_template": (
                    "Depois de executar, é hora de otimizar. Use métricas para identificar "
                    "o que funciona melhor para o seu caso e faça ajustes graduais. "
                    "A otimização contínua é o segredo dos profissionais de {niche}."
                ),
            },
            {
                "heading": "Passo 4: Escalabilidade",
                "body_template": (
                    "Quando você dominar o básico de {keyword}, pode começar a escalar. "
                    "Automatize processos, delegue tarefas e foque no que realmente gera resultados."
                ),
            },
        ],
        "intro_template": (
            "Aprender {keyword} pode parecer desafiador no início, mas com este guia "
            "passo a passo você vai conseguir dominar o essencial rapidamente. "
            "Vamos direto ao ponto?"
        ),
        "conclusion_template": (
            "Parabéns! Você acaba de aprender os fundamentos de {keyword}. "
            "Agora é praticar e refinar. Compartilhe nos comentários sua experiência "
            "e não esqueça de conferir as ferramentas recomendadas abaixo."
        ),
    },
}

# Modelos de meta-description
_META_DESCRIPTIONS: dict[str, str] = {
    "article": "Guia completo sobre {keyword}. Aprenda tudo que você precisa saber para começar e ter sucesso.",
    "review": "Review completo de {product_name}. Veja prós, contras, funcionalidades e se vale a pena investir em {product_name}.",
    "tutorial": "Aprenda {keyword} passo a passo com este tutorial completo. Do básico ao avançado, tudo que você precisa saber sobre {keyword}.",
}


def _render_template(template: str, variables: dict[str, str]) -> str:
    """Render a template string with variables, falling back gracefully."""
    result = template
    for key, value in variables.items():
        placeholder = "{" + key + "}"
        if placeholder in result:
            result = result.replace(placeholder, str(value))
    return result


def _wrap_premium_html(
    title: str, sections_html: str, offers_section: str,
    cta_section: str, disclosure: str, keyword: str, niche: str,
) -> str:
    """Wrap article content in premium HTML with design system."""
    niche_title = niche.title()
    css = (
        ":root{--bg:#0a0a1a;--bg2:#0d0d2b;--card:rgba(255,255,255,0.03);"
        "--primary:#6366f1;--gradient:linear-gradient(135deg,#6366f1,#8b5cf6);"
        "--text:#fff;--text2:#94a3b8;--text3:#64748b;--border:rgba(255,255,255,0.08);"
        "--radius:12px;--radius-lg:20px;--font:Inter,-apple-system,sans-serif;}"
        "*{box-sizing:border-box;margin:0;padding:0;}"
        "body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.8;}"
        ".container{max-width:800px;margin:0 auto;padding:2rem 1.5rem;}"
        ".article-header{text-align:center;padding:4rem 1.5rem 3rem;"
        "background:linear-gradient(135deg,#0a0a1a 0%,#1a1a3e 50%,#0d0d2b 100%);position:relative;overflow:hidden;}"
        ".article-header::before{content:'';position:absolute;inset:0;"
        "background:radial-gradient(ellipse at 50% 0%,rgba(99,102,241,0.15),transparent);pointer-events:none;}"
        ".article-header h1{font-size:clamp(1.5rem,4vw,2.5rem);font-weight:800;"
        "line-height:1.2;max-width:700px;margin:0 auto 1rem;position:relative;}"
        ".article-header .badge{display:inline-block;padding:0.3rem 1rem;border-radius:100px;"
        "background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.3);color:#a5b4fc;font-size:0.75rem;font-weight:500;margin-bottom:1rem;}"
        ".article-section{padding:2rem 0;border-bottom:1px solid var(--border);}"
        ".article-section h2{font-size:1.5rem;font-weight:700;margin-bottom:1rem;"
        "background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}"
        ".article-section p{color:var(--text2);margin-bottom:1rem;font-size:1rem;line-height:1.8;}"
        ".article-section ul{list-style:none;padding:0;}"
        ".article-section ul li{padding:0.5rem 0;color:var(--text2);padding-left:1.5rem;position:relative;}"
        ".article-section ul li::before{content:'\\25b8';position:absolute;left:0;color:var(--primary);}"
        ".offers ul li{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:1rem 1.5rem;margin-bottom:1rem;}"
        ".cta-artigo{background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.05));"
        "border:1px solid rgba(99,102,241,0.2);border-radius:var(--radius-lg);padding:2.5rem 2rem;text-align:center;margin:2rem 0;}"
        ".cta-artigo h3{font-size:1.3rem;margin-bottom:1rem;}.cta-artigo p{color:var(--text2);margin-bottom:1.5rem;}"
        ".btn-artigo{display:inline-block;padding:0.85rem 2rem;background:var(--gradient);color:#fff;font-weight:600;"
        "border-radius:var(--radius);text-decoration:none;transition:transform 0.2s,box-shadow 0.2s;}"
        ".btn-artigo:hover{transform:translateY(-2px);box-shadow:0 4px 20px rgba(99,102,241,0.4);}"
        ".btn-artigo.cta{font-size:1.1rem;padding:1rem 2.5rem;}"
        ".oferta-especial{background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.3);"
        "border-radius:var(--radius-lg);padding:2rem;text-align:center;margin:1.5rem 0;}"
        ".oferta-especial h3{font-size:1.2rem;color:#a5b4fc;margin-bottom:1rem;}"
        ".oferta-especial .urgency{font-size:0.85rem;color:#f59e0b;margin-top:1rem;}"
        ".proof-points{background:var(--card);border-radius:var(--radius);padding:1.5rem;margin-top:1.5rem;}"
        ".proof-points ul{list-style:none;padding:0;}.proof-points ul li{padding:0.4rem 0;color:var(--text2);}"
        ".disclosure{border-top:1px solid var(--border);padding-top:1.5rem;margin-top:2rem;}"
        ".disclosure p{color:var(--text3);font-size:0.8rem;font-style:italic;text-align:center;}"
        "@media(max-width:768px){.container{padding:1.5rem 1rem;}.cta-artigo{padding:1.5rem 1rem;}}"
    )
    return (
        '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        f'<title>{title}</title><style>{css}</style></head><body><article>'
        '<div class="article-header">'
        f'<div class="badge">{niche_title}</div>'
        f'<h1>{title}</h1></div>'
        '<div class="container">'
        f'{sections_html}'
        f'{offers_section}{cta_section}{disclosure}'
        '</div></article></body></html>'
    )



def _generate_markdown(
    title: str, meta_description: str, intro: str,
    sections_html: str, offers_section: str, conclusion: str,
    cta_section: str, disclosure: str, keyword: str, niche: str,
) -> str:
    """Generate a Markdown version of the article."""
    import re
    
    md_lines = []
    md_lines.append("---")
    md_lines.append('title: "' + title + '"')
    md_lines.append('description: "' + meta_description + '"')
    md_lines.append("date: 2026-06-25")
    md_lines.append("tags: [" + keyword + ", " + niche + "]")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("# " + title)
    md_lines.append("")
    
    # Clean intro
    intro_clean = intro.replace("<p>", "").replace("</p>", "").replace("<strong>", "**").replace("</strong>", "**")
    md_lines.append(intro_clean)
    md_lines.append("")
    
    # Clean sections
    sections_clean = sections_html.replace("<h2>", "## ").replace("</h2>", "")
    sections_clean = re.sub(r"<p>(.*?)</p>", lambda m: m.group(1) + "\n", sections_clean)
    sections_clean = sections_clean.replace("<strong>", "**").replace("</strong>", "**")
    sections_clean = sections_clean.replace("<em>", "*").replace("</em>", "*")
    sections_clean = re.sub(r"<[^>]+>", "", sections_clean)  # strip remaining HTML tags
    md_lines.append(sections_clean)
    md_lines.append("")
    
    # Offers section
    offers_clean = re.sub(r"<[^>]+>", "", offers_section)
    offers_clean = offers_clean.replace("Oferta Especial", "### Oferta Especial")
    md_lines.append(offers_clean)
    md_lines.append("")
    
    # Conclusion
    conclusion_clean = conclusion.replace("<p>", "").replace("</p>", "")
    md_lines.append("## Conclusao")
    md_lines.append("")
    md_lines.append(conclusion_clean)
    md_lines.append("")
    
    # CTA
    cta_clean = re.sub(r"<[^>]+>", "", cta_section)
    md_lines.append(cta_clean)
    md_lines.append("")
    
    # Disclosure
    disclosure_clean = re.sub(r"<[^>]+>", "", disclosure)
    md_lines.append(disclosure_clean)
    
    return "\n".join(md_lines)


def _generate_content_from_template(
    brief: dict[str, Any],
    offers: list[dict[str, Any]],
    niche: str,
) -> dict[str, Any]:
    """Generate content using template-based rendering (fallback when no LLM)."""
    keyword = brief.get("keyword", brief.get("topic", ""))
    content_type = brief.get("content_type", "article")
    product_name = offers[0].get("product_name", "") if offers else ""
    year = "2026"

    variables: dict[str, str] = {
        "keyword": keyword,
        "niche": niche or "marketing digital",
        "product_name": product_name,
        "year": year,
    }

    template = _CONTENT_TEMPLATES.get(content_type, _CONTENT_TEMPLATES["article"])

    # Generate meta description
    meta_template = _META_DESCRIPTIONS.get(content_type, _META_DESCRIPTIONS["article"])
    meta_description = _render_template(meta_template, variables)

    # Generate title
    title = _render_template(template["title_template"], variables)

    # Generate intro as HTML
    intro = f"<p>{_render_template(template['intro_template'], variables)}</p>"

    # Generate sections as proper HTML
    sections_html = ""
    for section in template["sections"]:
        heading = _render_template(section["heading"], variables)
        body = _render_template(section["body_template"], variables)
        body_html = body.replace("\n", "</p>\n<p>")
        sections_html += (
            f'<section class="article-section">\n'
            f'<h2>{heading}</h2>\n'
            f'<p>{body_html}</p>\n'
            f'</section>'
        )

    # Generate conclusion as HTML
    conclusion_html = _render_template(template["conclusion_template"], variables)
    conclusion = f"<p>{conclusion_html}</p>"

    # Generate offers section (premium HTML)
    offers_html = ""
    if offers:
        offers_html = '<section class="article-section offers">\n<h2>Produtos Recomendados</h2>\n<ul>'
        for offer in offers[:3]:
            pname = offer.get("product_name", "Produto")
            desc = offer.get(
                "description",
                f"Confira {pname} - uma excelente opcao para quem esta comecando em {niche}.",
            )
            purl = offer.get("product_url", "#")
            offers_html += (
                f'<li><strong>{pname}</strong>: {desc} '
                f'<a href="{purl}" class="btn-artigo">Ver Oferta</a></li>'
            )
        if offers:
            offers_html += "</ul>"
            purl = offers[0].get("product_url", "#")
            pname = offers[0].get("product_name", "produto")
            offers_html += (
                '<div class="oferta-especial">'
                '<h3>Oferta Especial</h3>'
                f'<p>Nao perca esta oportunidade! Clique no link abaixo e garanta seu acesso '
                f'ao {pname} com condicoes especiais.</p>'
                f'<a href="{purl}" class="btn-artigo cta">QUERO ACESSAR AGORA</a>'
                '<p class="urgency">*Oferta por tempo limitado. Aproveite enquanto disponivel.*</p>'
                '</div>'
            )
        offers_html += "\n</section>"

    # CTA section (premium)
    purl = offers[0].get("product_url", "#") if offers else "#"
    cta_html = (
        '<div class="cta-artigo">'
        '<h3>Pronto para Transformar seus Resultados?</h3>'
        f'<p>Quer **aprender** a gerar **lucro** e **dinheiro** com {keyword}? Esta e sua chance de **crescer** com **desconto** especial. Se voce chegou ate aqui, ja sabe que <strong>{keyword}</strong> pode fazer a diferenca '
        f'no seu negocio de {niche}. Agora e o momento de agir.</p>'
        f'<a href="{purl}" class="btn-artigo cta">QUERO COMECAR AGORA</a>'
        '<p>Milhares de pessoas ja estao transformando suas vidas. '
        'Clique no link acima e de o primeiro passo hoje mesmo.</p>'
        '<div class="proof-points">'
        '<p><strong>Resultados reais de quem aplicou o que aprendeu:</strong></p>'
        '<ul>'
        '<li> Aumento medio de 340% nos resultados</li>'
        '<li> Mais de 50 mil alunos satisfeitos</li>'
        '<li> Suporte 7 dias por semana</li>'
        '</ul></div></div>'
    )

    disclosure = (
        '<div class="disclosure">'
        '<p>*Alguns links neste artigo sao de afiliados. Se voce comprar atraves deles, '
        'eu posso ganhar uma comissao sem custo adicional para voce.*</p>'
        '</div>'
    )

    # Generate featured image URL
    img_url = f"https://image.pollinations.ai/prompt/{keyword.replace(' ', '%20')}%20{brief.get('content_type', 'article')}%202026?width=800&height=400&nologo=true"
    img_tag = f"<img src=\"{img_url}\" alt=\"{title}\" style=\"width:100%;border-radius:12px;margin:1.5rem 0;box-shadow:0 4px 20px rgba(0,0,0,0.3);\" loading=\"lazy\" />"

    # Full content body (HTML)
    body = f"{img_tag}{intro}<section class=\"article-section\"><h2>Conclusao</h2>{conclusion}</section>{offers_html}{cta_html}{disclosure}"

    # Premium HTML wrapper
    slug = keyword.lower().replace(" ", "-").replace(":", "").replace("?", "")[:60]
    html_premium = _wrap_premium_html(title, f"{img_tag}{intro}{sections_html}", offers_html, cta_html, disclosure, keyword, niche)

    # Generate markdown version
    markdown_body = f"{intro}{sections_html}{offers_html}<section class=\"article-section\"><h2>Conclusao</h2>{conclusion}</section>"
    markdown_output = _generate_markdown(title, meta_description, intro, sections_html, offers_html, conclusion, cta_html, disclosure, keyword, niche)

    # Word count
    word_count = len(body.split())

    return {
        "title": title,
        "slug": slug,
        "meta_description": meta_description,
        "body": body,
        "html_premium": html_premium,
        "markdown": markdown_output,
        "word_count": word_count,
        "estimated_reading_time": max(1, word_count // 200),
        "content_type": content_type,
        "keyword": keyword,
    }

# ── Agent class ──────────────────────────────────────────────


class ContentGeneratorAgent(AgentBase):
    """Gera conteúdo real (artigos, reviews, tutoriais) a partir dos briefings."""

    def __init__(self, **kwargs) -> None:
        super().__init__("content_generator", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        # Pega briefings do content_planner
        planning = context.step_results.get("content_planner", {})
        planning_output = (
            planning.get("output", {}) if isinstance(planning, dict) else {}
        )
        briefs = planning_output.get("briefs", [])

        if not briefs:
            # Fallback: criar um briefing simples
            briefs = [
                {
                    "keyword": str(campaign.get("objective", "marketing digital")),
                    "content_type": "article",
                    "offers": [],
                }
            ]

        # Pega ofertas disponíveis
        offers_step = context.step_results.get("offer_lookup", {})
        offers_output = (
            offers_step.get("output", {}) if isinstance(offers_step, dict) else {}
        )
        available_offers = offers_output.get("available_offers", [])

        # Gera conteúdo para cada briefing
        articles = []
        for brief in briefs[:3]:  # Máximo 3 artigos por ciclo
            offers_for_brief = []
            brief_offer_ids = brief.get("offers", [])
            for oid in brief_offer_ids:
                for offer in available_offers:
                    if offer.get("offer_id") == oid:
                        offers_for_brief.append(offer)
            if not offers_for_brief and available_offers:
                offers_for_brief = [available_offers[0]]

            article = _generate_content_from_template(brief, offers_for_brief, niche)
            articles.append(article)

        output = {
            "articles": articles,
            "total_articles": len(articles),
            "total_words": sum(a["word_count"] for a in articles),
            "niche": niche,
            "generation_method": "template_based",
            "note": "Conteúdo gerado por template. Para produção real, configurar OPENAI_API_KEY para gerar com IA.",
            "recommendation": (
                f"Publicar os {len(articles)} artigos nos próximos dias. "
                f"Primeiro artigo: '{articles[0]['title']}' (~{articles[0]['word_count']} palavras)."
            ),
        }

        # Registrar explicação se disponível
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="content_generation",
                input_state={
                    "briefs_count": len(briefs),
                    "niche": niche,
                    "method": "template_based",
                },
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "articles_generated": len(articles),
                    "total_words": output["total_words"],
                },
            )

        # Extrair conhecimento semântico
        if self.semantic_memory:
            for article in articles:
                content_concept_id = self.semantic_memory.register_concept(
                    f"article_{article['slug'][:20]}",
                    "content",
                    article["title"][:100],
                )
                niche_concept = self.semantic_memory.find_concept(niche, "niche")
                if niche_concept:
                    self.semantic_memory.assert_claim(
                        subject=niche_concept["concept_id"],
                        predicate="has_content",
                        object=content_concept_id,
                        confidence=0.7,
                        evidence_type="DIRECT_OBSERVATION",
                        asserted_by=self.name,
                    )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="content_generator",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[f"Gerei {len(articles)} artigos no nicho {niche}"],
            metadata={
                "articles": [a["slug"] for a in articles],
                "total_words": output["total_words"],
            },
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output=output,
            trace=trace,
        )
