# SiteDeployAgent

## Função
Gera site estático completo com todo o conteúdo produzido no ciclo. Produz um site HTML publicável.

## Entrada
- Artigos (do ContentGeneratorAgent)
- Conteúdo repurpado (do ContentRepurposerAgent)
- Lead magnets (do LeadCaptureAgent)

## Saída
- index.html (home com últimos artigos)
- /blog/artigo-slug.html (cada artigo individual)
- /pages/sobre.html, contato.html, privacidade.html, disclosure.html
- lead-capture.html (landing page de captura)
- sitemap.xml
- robots.txt
- rss.xml
- assets/css/style.css

## O site inclui
- Design responsivo (mobile-first)
- SEO (meta tags, canonical, structured)
- Lead capture forms em cada artigo
- Disclosure de afiliado em todas as páginas
- Sitemap para indexação Google
- RSS feed para assinantes

## Deploy
- Upload para Netlify (grátis): arrastar pasta "site/"
- Upload para Vercel (grátis): conectar repositório
- Upload para GitHub Pages
- Upload manual para qualquer hosting

## Observações
- Site 100% estático (HTML + CSS puro)
- Zero dependências de runtime
- Pronto para subir em produção
- Configurar site_url para SEO correto
