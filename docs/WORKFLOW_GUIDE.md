# ⚡ Workflow Guide — Campaign Autopilot v5.2.1

> Guia prático de todos os **30 workflows** e quando usar cada um.

---

## Workflows Completos

---

## Índice

1. [campaign_cycle](#campaign-cycle) — campaign_cycle
2. [content_excellence_workflow](#content-excellence-workflow) — content_excellence
3. [deploy_workflow](#deploy-workflow) — deploy_workflow
4. [fifth_order_workflow](#fifth-order-workflow) — fifth_order_workflow
5. [final_workflow](#final-workflow) — final_workflow
6. [fourth_order_workflow](#fourth-order-workflow) — fourth_order_workflow
7. [full_distribution_workflow](#full-distribution-workflow) — full_distribution_workflow
8. [governance_workflow](#governance-workflow) — governance
9. [hotmart_collection_workflow](#hotmart-collection-workflow) — hotmart_collection_workflow
10. [hotmart_product_selection_workflow](#hotmart-product-selection-workflow) — Hotmart — Seleção Inteligente de Produtos
11. [media_pipeline_workflow](#media-pipeline-workflow) — media_pipeline
12. [money_workflow](#money-workflow) — money_workflow
13. [multi_channel_workflow](#multi-channel-workflow) — multi_channel_workflow
14. [organic_affiliate_cycle](#organic-affiliate-cycle) — organic_affiliate_cycle
15. [organic_content_workflow](#organic-content-workflow) — organic_content_workflow
16. [organic_cycle](#organic-cycle) — organic_cycle
17. [paid_traffic_workflow](#paid-traffic-workflow) — paid_traffic_workflow
18. [production_workflow](#production-workflow) — production_workflow
19. [parallel_revenue_tree](#parallel-revenue-tree) — 🌳 Árvore de 13 Fontes de Renda em Paralelo
19. [revenue_orchestration_workflow](#revenue-orchestration-workflow) — Onda 2 — Orquestração de Múltiplas Fontes de Renda
20. [revenue_workflow](#revenue-workflow) — revenue_workflow
21. [safe_mass_posting_workflow](#safe-mass-posting-workflow) — safe_mass_posting_workflow
22. [seo_content_workflow](#seo-content-workflow) — Ciclo Diário de Conteúdo SEO-Otimizado
23. [sixth_order_workflow](#sixth-order-workflow) — sixth_order_workflow
24. [third_order_transcendence](#third-order-transcendence) — Onda 3 — Transcendência: Sistema Autopilot de 3ª Ordem
25. [third_order_workflow](#third-order-workflow) — third_order
26. [traffic_recycling_workflow](#traffic-recycling-workflow) — traffic_recycling_workflow
27. [ultimate_workflow](#ultimate-workflow) — ultimate_workflow
28. [teamworker_preview](#teamworker-preview) — teamworker_preview — Preview de ofertas, conteúdo e mídia antes da execução

---

## campaign_cycle

**Nome:** campaign_cycle
**Descrição:** Parallel analytics/compliance/memory lookups followed by optimization and execution planning.
**Total de steps:** 5
**Workers máximos:** 4

   **1. analytics** → `analytics`
      _Analyze the current campaign performance signals._
      Sem dependências

   **2. compliance** → `compliance`
      _Check campaign content and settings against policy._
      Sem dependências

   **3. memory_lookup** → `memory_lookup`
      _Search the campaign memory for similar historical runs._
      Sem dependências

   **4. optimization** → `optimization`
      _Synthesize optimization actions from the upstream agents._
      Depende de: analytics, compliance, memory_lookup

   **5. execution_planning** → `execution_planning`
      _Convert the optimization output into a serializable execution plan._
      Depende de: optimization

**Fluxo DAG:**
   `analytics` → optimization
   `compliance` → optimization
   `memory_lookup` → optimization
   `optimization` → execution_planning

---

## content_excellence_workflow

**Nome:** content_excellence
**Descrição:** 🧠 PIPELINE DE EXCELÊNCIA DE CONTEÚDO — Storytelling → Psicologia → Neuromarketing → Copywriting → Orquestração. Aplica ciência cognitiva, psicologia profunda e neuromarketing para criar conteúdo de alto impacto.
**Total de steps:** 4
**Workers máximos:** 4

   **1. storytelling_specialist** → `storytelling_specialist`
      _Selecionar estrutura narrativa ideal (Jornada do Herói, 3 Atos, PAS, AIDA)._
      Sem dependências

   **2. psychology_specialist** → `psychology_specialist`
      _Aplicar vieses cognitivos e princípios de persuasão (Cialdini, Kahneman)._
      Sem dependências

   **3. neuromarketing_specialist** → `neuromarketing_specialist`
      _Otimizar conteúdo para o cérebro (dopamina, ocitocina, fluência cognitiva)._
      Sem dependências

   **4. content_excellence** → `content_excellence`
      _Orquestrar todas as melhorias: storytelling + psicologia + neuromarketing + arquétipos + copywriting._
      Depende de: storytelling_specialist, psychology_specialist, neuromarketing_specialist

**Fluxo DAG:**
   `storytelling_specialist` → content_excellence
   `psychology_specialist` → content_excellence
   `neuromarketing_specialist` → content_excellence

---

## deploy_workflow

**Nome:** deploy_workflow
**Descrição:** 🌐 WORKFLOW DE DEPLOY — Gera site completo publicável a partir do conteúdo do ciclo.
**Total de steps:** 24
**Workers máximos:** 14

   **1. competitor_analysis** → `competitor_analysis`
      _Analisar concorrentes e gaps._
      Sem dependências

   **2. seo_scraper** → `seo_scraper`
      _Dados reais de SEO do Google._
      Sem dependências

   **3. compliance** → `compliance`
      _Validar compliance do conteúdo._
      Sem dependências

   **4. memory_lookup** → `memory_lookup`
      _Lições de ciclos anteriores._
      Sem dependências

   **5. offer_lookup** → `offer_lookup`
      _Ofertas de afiliados._
      Depende de: seo_scraper, competitor_analysis

   **6. content_planner** → `content_planner`
      _Briefings de conteúdo._
      Depende de: seo_scraper, offer_lookup, memory_lookup

   **7. content_generator** → `content_generator`
      _Gerar artigos para o site._
      Depende de: content_planner

   **8. free_image_gen** → `free_image_gen`
      _Gerar imagens gratuitas (Pillow) para blog, YouTube, Pinterest, Instagram._
      Depende de: content_generator, content_repurposer, site_deploy

   **9. free_video_producer** → `free_video_producer`
      _Produzir vídeos gratuitos (moviepy) para YouTube e TikTok._
      Depende de: content_generator, content_repurposer, site_deploy

   **10. platform_compliance** → `platform_compliance`
      _Validar conteúdo contra regras de cada plataforma para evitar bloqueios._
      Depende de: content_generator, free_image_gen, free_video_producer

   **11. content_repurposer** → `content_repurposer`
      _Multiplicar conteúdo._
      Depende de: content_generator, offer_lookup

   **12. youtube_marketing** → `youtube_marketing`
      _Scripts para YouTube._
      Depende de: seo_scraper, offer_lookup, content_generator

   **13. instagram_marketing** → `instagram_marketing`
      _Posts para Instagram._
      Depende de: seo_scraper, offer_lookup, content_generator

   **14. tiktok_marketing** → `tiktok_marketing`
      _Vídeos para TikTok._
      Depende de: seo_scraper, offer_lookup, content_generator

   **15. pinterest_marketing** → `pinterest_marketing`
      _Pins para Pinterest._
      Depende de: seo_scraper, offer_lookup, content_generator

   **16. twitter_marketing** → `twitter_marketing`
      _Threads para Twitter._
      Depende de: seo_scraper, offer_lookup, content_generator

   **17. lead_capture** → `lead_capture`
      _Lead magnets para captura._
      Depende de: seo_scraper, offer_lookup, content_generator

   **18. site_deploy** → `site_deploy`
      _Gerar site estático completo._
      Depende de: content_generator, content_repurposer, lead_capture

   **19. revenue_monitor** → `revenue_monitor`
      _Projeção de receita do site._
      Depende de: content_repurposer, offer_lookup, content_generator

   **20. analytics_feedback** → `analytics_feedback`
      _Feedback completo do ciclo._
      Depende de: site_deploy, revenue_monitor

   **21. organic_growth** → `organic_growth`
      _Analisar ciclo e gerar recomendações de growth hacking orgânico._
      Depende de: analytics_feedback, platform_compliance, revenue_monitor

   **22. agent_perf_monitor** → `agent_perf_monitor`
      _Monitorar performance individual de cada agente no ciclo._
      Depende de: organic_growth

   **23. meta_orchestrator** → `meta_orchestrator`
      _Auto-observar execução e modificar estrutura do workflow._
      Depende de: agent_perf_monitor

   **24. strategy_evolution** → `strategy_evolution`
      _Planejamento estratégico evolutivo entre ciclos._
      Depende de: meta_orchestrator

**Fluxo DAG:**
   `seo_scraper` → offer_lookup → content_planner → youtube_marketing → instagram_marketing → tiktok_marketing → pinterest_marketing → twitter_marketing → lead_capture
   `competitor_analysis` → offer_lookup
   `offer_lookup` → content_planner → content_repurposer → youtube_marketing → instagram_marketing → tiktok_marketing → pinterest_marketing → twitter_marketing → lead_capture → revenue_monitor
   `memory_lookup` → content_planner
   `content_planner` → content_generator
   `content_generator` → free_image_gen → free_video_producer → platform_compliance → content_repurposer → youtube_marketing → instagram_marketing → tiktok_marketing → pinterest_marketing → twitter_marketing → lead_capture → site_deploy → revenue_monitor
   `content_repurposer` → free_image_gen → free_video_producer → site_deploy → revenue_monitor
   `site_deploy` → free_image_gen → free_video_producer → analytics_feedback
   `free_image_gen` → platform_compliance
   `free_video_producer` → platform_compliance
   `lead_capture` → site_deploy
   `revenue_monitor` → analytics_feedback → organic_growth
   `analytics_feedback` → organic_growth
   `platform_compliance` → organic_growth
   `organic_growth` → agent_perf_monitor
   `agent_perf_monitor` → meta_orchestrator
   `meta_orchestrator` → strategy_evolution

---

## fifth_order_workflow

**Nome:** fifth_order_workflow
**Descrição:** 5a Ordem: Inteligencia Temporal. Conecta passado, presente e futuro. Detecta padroes sazonais, projeta trajetorias e otimiza timing estrategico.
**Total de steps:** 3
**Workers máximos:** 2

   **1. temporal_record** → `temporal_engine`
      _Registrar ciclo atual na timeline e atualizar NarrativeSelf._
      Sem dependências

   **2. temporal_foresight** → `temporal_engine`
      _Projetar 30/60/90 dias e detectar eventos sazonais._
      Depende de: temporal_record

   **3. temporal_recommend** → `temporal_engine`
      _Gerar recomendacoes de timing de conteudo e metas._
      Depende de: temporal_foresight

**Fluxo DAG:**
   `temporal_record` → temporal_foresight
   `temporal_foresight` → temporal_recommend

---

## final_workflow

**Nome:** final_workflow
**Descrição:** 🏆 WORKFLOW FINAL — Análise → Conteúdo → Otimização → Rank Tracking → Publicação em Lote → Receita. Sistema completo de ponta a ponta.
**Total de steps:** 24
**Workers máximos:** 14

   **1. competitor_analysis** → `competitor_analysis`
      _Analisar concorrentes e gaps._
      Sem dependências

   **2. seo_scraper** → `seo_scraper`
      _Dados reais de SEO._
      Sem dependências

   **3. compliance** → `compliance`
      _Validar compliance._
      Sem dependências

   **4. memory_lookup** → `memory_lookup`
      _Lições de ciclos anteriores._
      Sem dependências

   **5. offer_lookup** → `offer_lookup`
      _Ofertas baseadas em gaps._
      Depende de: seo_scraper, competitor_analysis

   **6. content_planner** → `content_planner`
      _Briefings de conteúdo._
      Depende de: seo_scraper, offer_lookup, memory_lookup

   **7. content_generator** → `content_generator`
      _Gerar artigos._
      Depende de: content_planner

   **8. content_repurposer** → `content_repurposer`
      _Multiplicar para 5 canais._
      Depende de: content_generator, offer_lookup

   **9. free_image_gen** → `free_image_gen`
      _Gerar imagens gratuitas (Pillow) para blog, YouTube, Pinterest, Instagram._
      Depende de: content_generator, content_repurposer

   **10. free_video_producer** → `free_video_producer`
      _Produzir vídeos gratuitos (moviepy) para YouTube e TikTok._
      Depende de: content_generator, content_repurposer

   **11. platform_compliance** → `platform_compliance`
      _Validar conteúdo contra regras de cada plataforma para evitar bloqueios._
      Depende de: content_generator, content_repurposer, free_image_gen, free_video_producer

   **12. instagram_marketing** → `instagram_marketing`
      _Posts para Instagram._
      Depende de: seo_scraper, offer_lookup, content_generator

   **13. tiktok_marketing** → `tiktok_marketing`
      _Vídeos para TikTok._
      Depende de: seo_scraper, offer_lookup, content_generator

   **14. twitter_marketing** → `twitter_marketing`
      _Threads para Twitter._
      Depende de: seo_scraper, offer_lookup, content_generator

   **15. content_optimizer** → `content_optimizer`
      _Otimizar SEO do conteúdo._
      Depende de: content_generator, content_repurposer, seo_scraper

   **16. wp_publisher** → `wp_publisher`
      _Publicar no WordPress._
      Depende de: content_generator, compliance

   **17. rank_tracker** → `rank_tracker`
      _Trackear rankings no Google._
      Depende de: seo_scraper

   **18. bulk_publisher** → `bulk_publisher`
      _Agendar tudo em lote._
      Depende de: content_generator, content_repurposer, wp_publisher, content_generator

   **19. revenue_monitor** → `revenue_monitor`
      _Projeção de receita._
      Depende de: content_repurposer, offer_lookup, rank_tracker, content_optimizer

   **20. analytics_feedback** → `analytics_feedback`
      _Feedback e aprendizado._
      Depende de: content_optimizer, revenue_monitor, rank_tracker, bulk_publisher

   **21. organic_growth** → `organic_growth`
      _Analisar ciclo e gerar recomendações de growth hacking orgânico._
      Depende de: analytics_feedback, platform_compliance, revenue_monitor

   **22. agent_perf_monitor** → `agent_perf_monitor`
      _Monitorar performance individual de cada agente no ciclo._
      Depende de: organic_growth

   **23. meta_orchestrator** → `meta_orchestrator`
      _Auto-observar execução e modificar estrutura do workflow._
      Depende de: agent_perf_monitor

   **24. strategy_evolution** → `strategy_evolution`
      _Planejamento estratégico evolutivo entre ciclos._
      Depende de: meta_orchestrator

**Fluxo DAG:**
   `seo_scraper` → offer_lookup → content_planner → instagram_marketing → tiktok_marketing → twitter_marketing → content_optimizer → rank_tracker
   `competitor_analysis` → offer_lookup
   `offer_lookup` → content_planner → content_repurposer → instagram_marketing → tiktok_marketing → twitter_marketing → revenue_monitor
   `memory_lookup` → content_planner
   `content_planner` → content_generator
   `content_generator` → content_repurposer → free_image_gen → free_video_producer → platform_compliance → instagram_marketing → tiktok_marketing → twitter_marketing → content_optimizer → wp_publisher → bulk_publisher → bulk_publisher
   `content_repurposer` → free_image_gen → free_video_producer → platform_compliance → content_optimizer → bulk_publisher → revenue_monitor
   `free_image_gen` → platform_compliance
   `free_video_producer` → platform_compliance
   `compliance` → wp_publisher
   `wp_publisher` → bulk_publisher
   `rank_tracker` → revenue_monitor → analytics_feedback
   `content_optimizer` → revenue_monitor → analytics_feedback
   `revenue_monitor` → analytics_feedback → organic_growth
   `bulk_publisher` → analytics_feedback
   `analytics_feedback` → organic_growth
   `platform_compliance` → organic_growth
   `organic_growth` → agent_perf_monitor
   `agent_perf_monitor` → meta_orchestrator
   `meta_orchestrator` → strategy_evolution

---

## fourth_order_workflow

**Nome:** fourth_order_workflow
**Descrição:** 4a Ordem: Inteligencia Coletiva Cross-Nicho. Conecta todos os nichos em barramento de conhecimento. Detecta padroes, distribui estrategias, evolui ontologia compartilhada.
**Total de steps:** 4
**Workers máximos:** 3

   **1. kollektiv_collect** → `kollektiv`
      _Coletar resultados de todos os nichos do ciclo atual._
      Sem dependências

   **2. kollektiv_analyze** → `kollektiv`
      _Analisar padroes cross-nicho e detectar estrategias vencedoras._
      Depende de: kollektiv_collect

   **3. kollektiv_recommend** → `kollektiv`
      _Distribuir recomendacoes para cada nicho baseado em aprendizados dos outros._
      Depende de: kollektiv_analyze

   **4. kollektiv_report** → `kollektiv`
      _Gerar sintese com vault health, padroes encontrados e ontologia compartilhada._
      Depende de: kollektiv_recommend

**Fluxo DAG:**
   `kollektiv_collect` → kollektiv_analyze
   `kollektiv_analyze` → kollektiv_recommend
   `kollektiv_recommend` → kollektiv_report

---

## full_distribution_workflow

**Nome:** full_distribution_workflow
**Descrição:** Workflow completo de distribuição multi-canal: blog + YouTube + email + Pinterest + feedback analítico.
**Total de steps:** 11
**Workers máximos:** 8

   **1. seo_research** → `seo_research`
      _Pesquisar palavras-chave e tópicos no nicho._
      Sem dependências

   **2. compliance** → `compliance`
      _Validar nicho e ofertas contra regras de compliance._
      Sem dependências

   **3. memory_lookup** → `memory_lookup`
      _Buscar lições de ciclos anteriores._
      Sem dependências

   **4. offer_lookup** → `offer_lookup`
      _Encontrar ofertas de afiliados compatíveis._
      Depende de: seo_research

   **5. content_planner** → `content_planner`
      _Briefings de conteúdo integrados._
      Depende de: seo_research, offer_lookup, memory_lookup

   **6. content_generator** → `content_generator`
      _Artigos para blog._
      Depende de: content_planner

   **7. youtube_marketing** → `youtube_marketing`
      _Scripts de vídeo para YouTube._
      Depende de: seo_research, offer_lookup

   **8. email_marketing** → `email_marketing`
      _Sequências de email marketing._
      Depende de: seo_research, offer_lookup

   **9. pinterest_marketing** → `pinterest_marketing`
      _Pins e boards para Pinterest._
      Depende de: seo_research, offer_lookup

   **10. wp_publisher** → `wp_publisher`
      _Publicar artigos no WordPress / arquivos._
      Depende de: content_generator, compliance

   **11. analytics_feedback** → `analytics_feedback`
      _Avaliar ciclo e alimentar aprendizado._
      Depende de: content_generator, youtube_marketing, email_marketing, pinterest_marketing, wp_publisher

**Fluxo DAG:**
   `seo_research` → offer_lookup → content_planner → youtube_marketing → email_marketing → pinterest_marketing
   `offer_lookup` → content_planner → youtube_marketing → email_marketing → pinterest_marketing
   `memory_lookup` → content_planner
   `content_planner` → content_generator
   `content_generator` → wp_publisher → analytics_feedback
   `compliance` → wp_publisher
   `youtube_marketing` → analytics_feedback
   `email_marketing` → analytics_feedback
   `pinterest_marketing` → analytics_feedback
   `wp_publisher` → analytics_feedback

---

## governance_workflow

**Nome:** governance
**Descrição:** 🏛️ PIPELINE DE GOVERNANÇA DE SEGUNDA ORDEM — Recursos → Qualidade → Riscos → Externo → Rollback → Síntese. Governança completa do sistema com gestão de recursos, QA, riscos, monitoramento externo e rollback.
**Total de steps:** 5
**Workers máximos:** 4

   **1. resource_manager** → `resource_manager`
      _Gerenciar orçamento de recursos, filas e rate limits._
      Sem dependências

   **2. quality_assurance** → `quality_assurance`
      _Validar qualidade dos outputs contra benchmarks._
      Sem dependências

   **3. risk_management** → `risk_management`
      _Avaliar riscos operacionais e estratégicos._
      Sem dependências

   **4. external_monitor** → `external_monitor`
      _Monitorar mudanças externas e saturação de nicho._
      Sem dependências

   **5. rollback_manager** → `rollback_manager`
      _Gerenciar versionamento e rollback de mudanças._
      Depende de: resource_manager, quality_assurance, risk_management, external_monitor

**Fluxo DAG:**
   `resource_manager` → rollback_manager
   `quality_assurance` → rollback_manager
   `risk_management` → rollback_manager
   `external_monitor` → rollback_manager

---

## hotmart_collection_workflow

**Nome:** hotmart_collection_workflow
**Descrição:** Pipeline de coleta e validacao de links Hotmart: valida, armazena e atualiza config.
**Total de steps:** 4
**Workers máximos:** 2

   **1. validate_link** → `link_validator`
      _Validar formato do link, presenca de ?aff=, detectar placeholders._
      Sem dependências

   **2. match_product** → `product_matcher`
      _Analisar nome do produto e sugerir keywords, comissao, nicho._
      Depende de: validate_link

   **3. store_link** → `hotmart_link_manager`
      _Armazenar link no banco SQLite com metadados._
      Depende de: validate_link, match_product

   **4. update_config** → `config_updater`
      _Sincronizar banco SQLite com configs/affiliate_offers.json._
      Depende de: store_link

**Fluxo DAG:**
   `validate_link` → match_product → store_link
   `match_product` → store_link
   `store_link` → update_config

---

## hotmart_product_selection_workflow

**Nome:** Hotmart — Seleção Inteligente de Produtos
**Descrição:** Pipeline que pesquisa, ranqueia e seleciona os melhores produtos Hotmart para afiliacao, priorizando ganhos rapidos
**Total de steps:** 3

   **1. research_products** → `hotmart_product_researcher`
      _Pesquisa produtos Hotmart em todos os nichos e ranqueia por potencial de ganho_
      Sem dependências

   **2. select_best** → `hotmart_affiliate_selector`
      _Seleciona os 3 melhores produtos priorizando velocidade de ganhos_
      Sem dependências

   **3. generate_hunt_list** → `hotmart_product_researcher`
      _Gera lista final de produtos para o usuario coletar links_
      Sem dependências


---

## media_pipeline_workflow

**Nome:** media_pipeline
**Descrição:** 🎬 PIPELINE CINEMATOGRÁFICO DE MÍDIA — Storyboard → Imagens → Vídeos → Áudio → Orquestração. Pipeline completo com qualidade cinematográfica usando ferramentas gratuitas.
**Total de steps:** 5
**Workers máximos:** 3

   **1. storyboard** → `storyboard`
      _Planejar storyboards visuais para vídeos e imagens._
      Sem dependências

   **2. cinematic_image_gen** → `cinematic_image_gen`
      _Gerar imagens cinematográficas com color grading, iluminação, tipografia._
      Depende de: storyboard

   **3. audio_production** → `audio_production`
      _Produzir narração TTS + música de fundo + mixagem profissional._
      Depende de: storyboard

   **4. cinematic_video_producer** → `cinematic_video_producer`
      _Produzir vídeos cinematográficos com Ken Burns, transições e áudio._
      Depende de: storyboard, audio_production, cinematic_image_gen

   **5. media_pipeline** → `media_pipeline`
      _Orquestrar pipeline de mídia e gerar relatório de qualidade._
      Depende de: cinematic_image_gen, cinematic_video_producer, audio_production

**Fluxo DAG:**
   `storyboard` → cinematic_image_gen → audio_production → cinematic_video_producer
   `audio_production` → cinematic_video_producer → media_pipeline
   `cinematic_image_gen` → cinematic_video_producer → media_pipeline
   `cinematic_video_producer` → media_pipeline

---

## money_workflow

**Nome:** money_workflow
**Descrição:** 🚀 WORKFLOW DEFINITIVO — Análise de concorrência → SEO real → Conteúdo → Repurposing 5x → Receita. Máquina de fazer dinheiro.
**Total de steps:** 21
**Workers máximos:** 14

   **1. competitor_analysis** → `competitor_analysis`
      _Analisar concorrentes e gaps._
      Sem dependências

   **2. seo_scraper** → `seo_scraper`
      _Dados reais de SEO do Google._
      Sem dependências

   **3. compliance** → `compliance`
      _Validar compliance._
      Sem dependências

   **4. memory_lookup** → `memory_lookup`
      _Lições de ciclos anteriores._
      Sem dependências

   **5. offer_lookup** → `offer_lookup`
      _Ofertas baseadas em gaps._
      Depende de: seo_scraper, competitor_analysis

   **6. content_planner** → `content_planner`
      _Briefings baseados em oportunidades reais._
      Depende de: seo_scraper, competitor_analysis, offer_lookup, memory_lookup

   **7. content_generator** → `content_generator`
      _Artigos otimizados para SEO._
      Depende de: content_planner

   **8. content_repurposer** → `content_repurposer`
      _Multiplicar 5 canais automaticamente._
      Depende de: content_generator, offer_lookup

   **9. free_image_gen** → `free_image_gen`
      _Gerar imagens gratuitas (Pillow) para blog, YouTube, Pinterest, Instagram._
      Depende de: content_generator, content_repurposer

   **10. free_video_producer** → `free_video_producer`
      _Produzir vídeos gratuitos (moviepy) para YouTube e TikTok._
      Depende de: content_generator, content_repurposer

   **11. platform_compliance** → `platform_compliance`
      _Validar conteúdo contra regras de cada plataforma para evitar bloqueios._
      Depende de: content_generator, content_repurposer, free_image_gen, free_video_producer

   **12. instagram_marketing** → `instagram_marketing`
      _Posts para Instagram._
      Depende de: seo_scraper, offer_lookup, content_generator

   **13. tiktok_marketing** → `tiktok_marketing`
      _Vídeos para TikTok._
      Depende de: seo_scraper, offer_lookup, content_generator

   **14. twitter_marketing** → `twitter_marketing`
      _Threads para Twitter._
      Depende de: seo_scraper, offer_lookup, content_generator

   **15. wp_publisher** → `wp_publisher`
      _Publicar no WordPress._
      Depende de: content_generator, compliance

   **16. revenue_monitor** → `revenue_monitor`
      _Projeção de receita e ROI._
      Depende de: content_repurposer, offer_lookup, wp_publisher

   **17. analytics_feedback** → `analytics_feedback`
      _Feedback e aprendizado do ciclo._
      Depende de: content_repurposer, revenue_monitor, wp_publisher

   **18. organic_growth** → `organic_growth`
      _Analisar ciclo e gerar recomendações de growth hacking orgânico._
      Depende de: analytics_feedback, platform_compliance, revenue_monitor

   **19. agent_perf_monitor** → `agent_perf_monitor`
      _Monitorar performance individual de cada agente no ciclo._
      Depende de: organic_growth

   **20. meta_orchestrator** → `meta_orchestrator`
      _Auto-observar execução e modificar estrutura do workflow._
      Depende de: agent_perf_monitor

   **21. strategy_evolution** → `strategy_evolution`
      _Planejamento estratégico evolutivo entre ciclos._
      Depende de: meta_orchestrator

**Fluxo DAG:**
   `seo_scraper` → offer_lookup → content_planner → instagram_marketing → tiktok_marketing → twitter_marketing
   `competitor_analysis` → offer_lookup → content_planner
   `offer_lookup` → content_planner → content_repurposer → instagram_marketing → tiktok_marketing → twitter_marketing → revenue_monitor
   `memory_lookup` → content_planner
   `content_planner` → content_generator
   `content_generator` → content_repurposer → free_image_gen → free_video_producer → platform_compliance → instagram_marketing → tiktok_marketing → twitter_marketing → wp_publisher
   `content_repurposer` → free_image_gen → free_video_producer → platform_compliance → revenue_monitor → analytics_feedback
   `free_image_gen` → platform_compliance
   `free_video_producer` → platform_compliance
   `compliance` → wp_publisher
   `wp_publisher` → revenue_monitor → analytics_feedback
   `revenue_monitor` → analytics_feedback → organic_growth
   `analytics_feedback` → organic_growth
   `platform_compliance` → organic_growth
   `organic_growth` → agent_perf_monitor
   `agent_perf_monitor` → meta_orchestrator
   `meta_orchestrator` → strategy_evolution

---

## multi_channel_workflow

**Nome:** multi_channel_workflow
**Descrição:** Workflow multi-canal completo: blog → YouTube → email marketing. Gera conteúdo para 3 canais orgânicos simultaneamente.
**Total de steps:** 9
**Workers máximos:** 6

   **1. seo_research** → `seo_research`
      _Pesquisar palavras-chave e tópicos no nicho._
      Sem dependências

   **2. compliance** → `compliance`
      _Validar nicho e ofertas contra regras de compliance._
      Sem dependências

   **3. memory_lookup** → `memory_lookup`
      _Buscar lições de ciclos anteriores._
      Sem dependências

   **4. offer_lookup** → `offer_lookup`
      _Encontrar ofertas de afiliados compatíveis com as keywords._
      Depende de: seo_research

   **5. content_planner** → `content_planner`
      _Combinar pesquisa + ofertas em briefings de conteúdo._
      Depende de: seo_research, offer_lookup, memory_lookup

   **6. content_generator** → `content_generator`
      _Gerar artigos para blog a partir dos briefings._
      Depende de: content_planner

   **7. youtube_marketing** → `youtube_marketing`
      _Gerar scripts de vídeo, descrições e tags para YouTube._
      Depende de: seo_research, offer_lookup

   **8. email_marketing** → `email_marketing`
      _Gerar sequências de email marketing com ofertas._
      Depende de: seo_research, offer_lookup

   **9. wp_publisher** → `wp_publisher`
      _Publicar artigos gerados (simulado ou WordPress real)._
      Depende de: content_generator, compliance

**Fluxo DAG:**
   `seo_research` → offer_lookup → content_planner → youtube_marketing → email_marketing
   `offer_lookup` → content_planner → youtube_marketing → email_marketing
   `memory_lookup` → content_planner
   `content_planner` → content_generator
   `content_generator` → wp_publisher
   `compliance` → wp_publisher

---

## organic_affiliate_cycle

**Nome:** organic_affiliate_cycle
**Descrição:** Ciclo completo de marketing de afiliados orgânico: pesquisa SEO → ofertas → conteúdo → compliance → publicação.
**Total de steps:** 6
**Workers máximos:** 4

   **1. seo_research** → `seo_research`
      _Pesquisar palavras-chave e tópicos no nicho._
      Sem dependências

   **2. compliance** → `compliance`
      _Validar nicho e ofertas contra regras de compliance._
      Sem dependências

   **3. memory_lookup** → `memory_lookup`
      _Buscar lições de ciclos anteriores de conteúdo._
      Sem dependências

   **4. offer_lookup** → `offer_lookup`
      _Encontrar ofertas de afiliados compatíveis com as keywords._
      Depende de: seo_research

   **5. content_planner** → `content_planner`
      _Combinar pesquisa + ofertas em briefings de conteúdo._
      Depende de: seo_research, offer_lookup, memory_lookup

   **6. publisher** → `publisher`
      _Criar cronograma de publicação e estimar resultados._
      Depende de: content_planner, compliance

**Fluxo DAG:**
   `seo_research` → offer_lookup → content_planner
   `offer_lookup` → content_planner
   `memory_lookup` → content_planner
   `content_planner` → publisher
   `compliance` → publisher

---

## organic_content_workflow

**Nome:** organic_content_workflow
**Descrição:** Workflow completo de geração de conteúdo orgânico: pesquisa SEO → ofertas → planejamento → geração de texto → publicação.
**Total de steps:** 7
**Workers máximos:** 4

   **1. seo_research** → `seo_research`
      _Pesquisar palavras-chave e tópicos no nicho._
      Sem dependências

   **2. compliance** → `compliance`
      _Validar nicho e ofertas contra regras de compliance._
      Sem dependências

   **3. memory_lookup** → `memory_lookup`
      _Buscar lições de ciclos anteriores._
      Sem dependências

   **4. offer_lookup** → `offer_lookup`
      _Encontrar ofertas de afiliados compatíveis com as keywords._
      Depende de: seo_research

   **5. content_planner** → `content_planner`
      _Combinar pesquisa + ofertas em briefings de conteúdo._
      Depende de: seo_research, offer_lookup, memory_lookup

   **6. content_generator** → `content_generator`
      _Gerar texto real dos artigos usando templates ou IA._
      Depende de: content_planner

   **7. wp_publisher** → `wp_publisher`
      _Publicar conteúdo gerado (simulado ou WordPress real)._
      Depende de: content_generator, compliance

**Fluxo DAG:**
   `seo_research` → offer_lookup → content_planner
   `offer_lookup` → content_planner
   `memory_lookup` → content_planner
   `content_planner` → content_generator
   `content_generator` → wp_publisher
   `compliance` → wp_publisher

---

## organic_cycle

**Nome:** organic_cycle
**Descrição:** Free organic acquisition workflow with parallel research and content planning.
**Total de steps:** 5
**Workers máximos:** 4

   **1. research** → `analytics`
      _Assess what topics and channels are currently working._
      Sem dependências

   **2. compliance** → `compliance`
      _Validate the content and channel plan against opt-in rules._
      Sem dependências

   **3. memory_lookup** → `memory_lookup`
      _Look for winning topics, hooks, and channels from history._
      Sem dependências

   **4. optimization** → `optimization`
      _Choose the smallest organic improvement to ship next._
      Depende de: research, compliance, memory_lookup

   **5. execution_planning** → `execution_planning`
      _Convert the organic recommendation into a versioned action plan._
      Depende de: optimization

**Fluxo DAG:**
   `research` → optimization
   `compliance` → optimization
   `memory_lookup` → optimization
   `optimization` → execution_planning

---

## paid_traffic_workflow

**Nome:** paid_traffic_workflow
**Descrição:** Sem descrição
**Total de steps:** 9

   **1. revenue_monitor** → `revenue_monitor`
      _Verifica se receita mensal atingiu threshold para ativar tráfego pago_
      Sem dependências

   **2. budget_optimizer** → `budget_optimizer`
      _Aloca orçamento entre plataformas baseado em ROAS histórico_
      Sem dependências

   **3. paid_traffic_orchestrator** → `paid_traffic_orchestrator`
      _Cria plano de campanhas multi-plataforma_
      Sem dependências

   **4. ad_copy_generator** → `ad_copy_generator`
      _Gera criativos de anúncio a partir de artigos existentes_
      Sem dependências

   **5. landing_page_generator** → `landing_page`
      _Cria landing pages otimizadas para conversão_
      Sem dependências

   **6. google_ads_setup** → `google_ads`
      _Configura campanha no Google Ads_
      Sem dependências

   **7. meta_ads_setup** → `meta_ads`
      _Configura campanha no Meta Ads_
      Sem dependências

   **8. native_ads_setup** → `native_ads`
      _Configura campanha de native ads_
      Sem dependências

   **9. performance_tracker** → `performance_tracker`
      _Monitora ROAS e recomenda ações (escalar, manter, reduzir, pausar)_
      Sem dependências


---

## production_workflow

**Nome:** production_workflow
**Descrição:** 🏭 WORKFLOW DE PRODUÇÃO COMPLETO — 9 canais de tráfego orgânico. Concorrência → SEO → Conteúdo → 9 Canais → Site → Receita. Máquina completa de monetização orgânica sem tráfego pago.
**Total de steps:** 48
**Workers máximos:** 4

   **1. competitor_analysis** → `competitor_analysis`
      _Analisar concorrentes e encontrar gaps de conteúdo._
      Sem dependências

   **2. seo_scraper** → `seo_scraper`
      _Dados reais de SEO do Google._
      Sem dependências

   **3. compliance** → `compliance`
      _Validar compliance do conteúdo e ofertas._
      Sem dependências

   **4. memory_lookup** → `memory_lookup`
      _Lições de ciclos anteriores._
      Sem dependências

   **5. offer_lookup** → `offer_lookup`
      _Ofertas de afiliados baseadas em gaps._
      Depende de: seo_scraper, competitor_analysis

   **6. content_planner** → `content_planner`
      _Briefings baseados em oportunidades reais._
      Depende de: seo_scraper, competitor_analysis, offer_lookup, memory_lookup

   **7. storytelling_specialist** → `storytelling_specialist`
      _Selecionar estrutura narrativa ideal e gerar hooks._
      Depende de: content_planner

   **8. psychology_specialist** → `psychology_specialist`
      _Aplicar vieses cognitivos e princípios de persuasão._
      Depende de: content_planner

   **9. neuromarketing_specialist** → `neuromarketing_specialist`
      _Otimizar conteúdo para resposta cerebral._
      Depende de: content_planner

   **10. content_excellence** → `content_excellence`
      _Orquestrar todas as melhorias de conteúdo._
      Depende de: storytelling_specialist, psychology_specialist, neuromarketing_specialist

   **11. content_generator** → `content_generator`
      _Artigos otimizados para SEO._
      Depende de: content_planner, content_excellence

   **12. content_repurposer** → `content_repurposer`
      _Multiplicar para todos os canais._
      Depende de: content_generator, offer_lookup

   **13. storyboard** → `storyboard`
      _Planejar storyboards visuais para vídeos e imagens._
      Depende de: content_generator, seo_scraper

   **14. cinematic_image_gen** → `cinematic_image_gen`
      _Gerar imagens cinematográficas (color grading, iluminação, tipografia)._
      Depende de: content_generator, storyboard

   **15. audio_production** → `audio_production`
      _Produzir narração TTS + música de fundo + mixagem profissional._
      Depende de: content_repurposer, storyboard

   **16. cinematic_video_producer** → `cinematic_video_producer`
      _Produzir vídeos cinematográficos com Ken Burns, transições e áudio._
      Depende de: storyboard, audio_production, content_repurposer

   **17. media_pipeline** → `media_pipeline`
      _Orquestrar pipeline de mídia e gerar relatório de qualidade._
      Depende de: cinematic_image_gen, cinematic_video_producer, audio_production

   **18. free_image_gen** → `free_image_gen`
      _Gerar imagens (fallback) gratuitas (Pillow) para blog, YouTube, Pinterest, Instagram._
      Depende de: site_deploy, cinematic_image_gen, content_repurposer, content_generator

   **19. free_video_producer** → `free_video_producer`
      _Produzir (fallback) vídeos gratuitos (moviepy) para YouTube e TikTok._
      Depende de: site_deploy, cinematic_video_producer, content_repurposer, content_generator

   **20. platform_compliance** → `platform_compliance`
      _Validar conteúdo contra regras de cada plataforma para evitar bloqueios._
      Depende de: content_generator, content_repurposer, free_image_gen, free_video_producer

   **21. wp_publisher** → `wp_publisher`
      _Publicar no WordPress._
      Depende de: content_generator, compliance

   **22. lead_capture** → `lead_capture`
      _Lead magnets para captura de emails._
      Depende de: seo_scraper, offer_lookup, content_generator

   **23. youtube_marketing** → `youtube_marketing`
      _Scripts de vídeo e SEO para YouTube._
      Depende de: seo_scraper, offer_lookup, content_generator

   **24. email_marketing** → `email_marketing`
      _Sequências de email marketing._
      Depende de: seo_scraper, offer_lookup

   **25. pinterest_marketing** → `pinterest_marketing`
      _Pins otimizados para Pinterest._
      Depende de: seo_scraper, offer_lookup, content_generator

   **26. instagram_marketing** → `instagram_marketing`
      _Posts, reels e carrosséis para Instagram._
      Depende de: seo_scraper, offer_lookup, content_generator

   **27. tiktok_marketing** → `tiktok_marketing`
      _Scripts de vídeos curtos para TikTok._
      Depende de: seo_scraper, offer_lookup, content_generator

   **28. twitter_marketing** → `twitter_marketing`
      _Threads e posts para Twitter/X._
      Depende de: seo_scraper, offer_lookup, content_generator

   **29. whatsapp_marketing** → `whatsapp_marketing`
      _Mensagens para WhatsApp Marketing._
      Depende de: seo_scraper, offer_lookup, content_generator

   **30. site_deploy** → `site_deploy`
      _Gerar site estático completo._
      Depende de: content_generator, content_repurposer, lead_capture

   **31. content_optimizer** → `content_optimizer`
      _Otimizar SEO do conteúdo._
      Depende de: content_generator, content_repurposer, seo_scraper

   **32. rank_tracker** → `rank_tracker`
      _Trackear rankings no Google._
      Depende de: seo_scraper

   **33. bulk_publisher** → `bulk_publisher`
      _Agendar tudo em lote._
      Depende de: content_generator, content_repurposer, wp_publisher

   **34. revenue_monitor** → `revenue_monitor`
      _Projeção de receita multi-canal._
      Depende de: content_repurposer, offer_lookup, rank_tracker, youtube_marketing, email_marketing, pinterest_marketing

   **35. analytics_feedback** → `analytics_feedback`
      _Feedback e aprendizado completo do ciclo._
      Depende de: content_optimizer, revenue_monitor, rank_tracker, bulk_publisher, site_deploy, youtube_marketing, instagram_marketing, tiktok_marketing, twitter_marketing, whatsapp_marketing

   **36. organic_growth** → `organic_growth`
      _Analisar ciclo e gerar recomendações de growth hacking orgânico._
      Depende de: analytics_feedback, platform_compliance, revenue_monitor

   **37. agent_perf_monitor** → `agent_perf_monitor`
      _Monitorar performance individual de cada agente no ciclo._
      Depende de: organic_growth

   **38. meta_orchestrator** → `meta_orchestrator`
      _Auto-observar execução e modificar estrutura do workflow._
      Depende de: agent_perf_monitor

   **39. strategy_evolution** → `strategy_evolution`
      _Planejamento estratégico evolutivo entre ciclos._
      Depende de: meta_orchestrator

   **40. self_healing** → `self_healing`
      _Auto-reparo: verificar saúde do sistema e executar ações corretivas._
      Depende de: strategy_evolution

   **41. agent_factory** → `agent_factory`
      _Detectar gaps e criar novos agentes automaticamente._
      Depende de: self_healing

   **42. evolution_engine** → `evolution_engine`
      _Aplicar prescrições do MetaOrchestrator nos workflows._
      Depende de: agent_factory

   **43. circuit_breaker** → `circuit_breaker`
      _Monitorar saúde do sistema e ativar modos de emergência._
      Depende de: agent_factory

   **44. third_order_orchestrator** → `third_order_orchestrator`
      _Síntese transcendente e recomendações de auto-evolução._
      Depende de: epistemic, observer_fusion, value_evolution, recursive_observer

   **45. recursive_observer** → `recursive_observer`
      _Auditar governança do MetaOrchestrator._
      Depende de: meta_orchestrator

   **46. value_evolution** → `value_evolution`
      _Evolução do sistema de valores baseada em performance._
      Depende de: epistemic

   **47. observer_fusion** → `observer_fusion`
      _Análise multi-perspectiva da estratégia._
      Depende de: epistemic

   **48. epistemic** → `epistemic`
      _Auto-questionamento epistêmico: mapear conhecimento e pontos cegos._
      Depende de: revenue_monitor, analytics_feedback

**Fluxo DAG:**
   `seo_scraper` → offer_lookup → content_planner → storyboard → lead_capture → youtube_marketing → email_marketing → pinterest_marketing → instagram_marketing → tiktok_marketing → twitter_marketing → whatsapp_marketing → content_optimizer → rank_tracker
   `competitor_analysis` → offer_lookup → content_planner
   `offer_lookup` → content_planner → content_repurposer → lead_capture → youtube_marketing → email_marketing → pinterest_marketing → instagram_marketing → tiktok_marketing → twitter_marketing → whatsapp_marketing → revenue_monitor
   `memory_lookup` → content_planner
   `content_planner` → storytelling_specialist → psychology_specialist → neuromarketing_specialist → content_generator
   `storytelling_specialist` → content_excellence
   `psychology_specialist` → content_excellence
   `neuromarketing_specialist` → content_excellence
   `content_excellence` → content_generator
   `content_generator` → content_repurposer → storyboard → cinematic_image_gen → free_image_gen → free_video_producer → platform_compliance → wp_publisher → lead_capture → youtube_marketing → pinterest_marketing → instagram_marketing → tiktok_marketing → twitter_marketing → whatsapp_marketing → site_deploy → content_optimizer → bulk_publisher
   `storyboard` → cinematic_image_gen → audio_production → cinematic_video_producer
   `content_repurposer` → audio_production → cinematic_video_producer → free_image_gen → free_video_producer → platform_compliance → site_deploy → content_optimizer → bulk_publisher → revenue_monitor
   `audio_production` → cinematic_video_producer → media_pipeline
   `cinematic_image_gen` → media_pipeline → free_image_gen
   `cinematic_video_producer` → media_pipeline → free_video_producer
   `site_deploy` → free_image_gen → free_video_producer → analytics_feedback
   `free_image_gen` → platform_compliance
   `free_video_producer` → platform_compliance
   `compliance` → wp_publisher
   `lead_capture` → site_deploy
   `wp_publisher` → bulk_publisher
   `rank_tracker` → revenue_monitor → analytics_feedback
   `youtube_marketing` → revenue_monitor → analytics_feedback
   `email_marketing` → revenue_monitor
   `pinterest_marketing` → revenue_monitor
   `content_optimizer` → analytics_feedback
   `revenue_monitor` → analytics_feedback → organic_growth → epistemic
   `bulk_publisher` → analytics_feedback
   `instagram_marketing` → analytics_feedback
   `tiktok_marketing` → analytics_feedback
   `twitter_marketing` → analytics_feedback
   `whatsapp_marketing` → analytics_feedback
   `analytics_feedback` → organic_growth → epistemic
   `platform_compliance` → organic_growth
   `organic_growth` → agent_perf_monitor
   `agent_perf_monitor` → meta_orchestrator
   `meta_orchestrator` → strategy_evolution → recursive_observer
   `strategy_evolution` → self_healing
   `self_healing` → agent_factory
   `agent_factory` → evolution_engine → circuit_breaker
   `epistemic` → third_order_orchestrator → value_evolution → observer_fusion
   `observer_fusion` → third_order_orchestrator
   `value_evolution` → third_order_orchestrator
   `recursive_observer` → third_order_orchestrator

---

\
## parallel_revenue_tree\
\
**Nome:** 🌳 Árvore de Múltiplas Fontes de Renda\
**Descrição:** Dispara TODAS as 13 fontes de renda simultaneamente via ThreadPoolExecutor. Cada fonte roda em sua própria thread. O step agregador só executa após todas terminarem.\
**Total de steps:** 14 (13 fontes + 1 agregador)\
\
```\
TODAS RODAM EM PARALELO (deps=[])\
├── revenue_hotmart       → Hotmart (Infoprodutos)\
├── revenue_kiwify        → Kiwify (Infoprodutos)\
├── revenue_eduzz         → Eduzz (Infoprodutos)\
├── revenue_monetizze     → Monetizze (Infoprodutos)\
├── revenue_mercadolivre  → Mercado Livre (Marketplace)\
├── revenue_shopee        → Shopee (Marketplace)\
├── revenue_shein         → SheIn (Moda)\
├── revenue_aliexpress    → AliExpress (Marketplace Global)\
├── revenue_amazon        → Amazon Associates\
├── revenue_adsense       → Google AdSense\
├── revenue_cpa           → CPA Marketing\
├── revenue_digital_product → Produtos Digitais\
├── revenue_membership    → Assinaturas\
└── aggregate_revenue     → Agrega resultados de TODAS\
```\
\
**Uso:**\
```bash\
python scripts/money_loop.py --workflow workflows/parallel_revenue_tree.json --once\
```\
\
**Dependências entre steps:**\
- Todos os 13 revenue_* steps: `deps=[]` (rodam em paralelo)\
- aggregate_revenue: `deps=[todos os 13]` (só depois que todos terminarem)
## revenue_orchestration_workflow

**Nome:** Onda 2 — Orquestração de Múltiplas Fontes de Renda
**Descrição:** Analisa portfólio, detecta oportunidades, cria produtos, otimiza alocação e reinveste (ADR-002)
**Total de steps:** 13

   **1. opportunity_scan** → `OpportunityDetectorAgent`
      _Escaneia mercado em busca de novas oportunidades de receita_
      Sem dependências

   **2. portfolio_analysis** → `PortfolioOptimizerAgent`
      _Analisa portfólio atual de fontes de renda e recomenda alocação_
      Sem dependências

   **3. digital_product_creation** → `DigitalProductAgent`
      _Cria produtos digitais baseados nas oportunidades detectadas_
      Sem dependências

   **4. membership_planning** → `MembershipAgent`
      _Planeja planos de assinatura e conteúdo exclusivo_
      Sem dependências

   **5. email_sequence_upgrade** → `EmailMarketingAgent`
      _Atualiza sequências de email para novas ofertas e produtos_
      Sem dependências

   **6. compounding_plan** → `CompoundingEngine`
      _Calcula reinvestimento: receita direta → passiva → residual_
      Sem dependências

   **7. revenue_dashboard** → `RevenueOrchestratorAgent`
      _Gera dashboard completo de todas as 13 fontes de renda_
      Sem dependências

   **8. revenue_protocol_check** → `RevenueProtocolAgent`
      _Verifica status de configuracao de cada fonte de renda_
      Sem dependências

   **9. generic_affiliate_scan** → `GenericAffiliateNetworkAgent`
      _Valida links das redes genericas (Monetizze, Kiwify, Eduzz)_
      Sem dependências

   **10. adsense_optimization** → `AdSenseAgent`
      _Otimiza unidades de anuncio do Google AdSense_
      Sem dependências

   **11. cpa_discovery** → `CPAAgent`
      _Descobre novas ofertas CPA nos nichos ativos_
      Sem dependências

   **12. revenue_next_steps** → `RevenueOrchestratorAgent`
      _Recomenda proximos passos baseado no estado atual_
      Sem dependências

   **13. revenue_report** → `RevenueMonitorAgent`
      _Compila relatório completo de receita por fonte_
      Sem dependências


---

## revenue_workflow

**Nome:** revenue_workflow
**Descrição:** Workflow focado em receita: conteúdo → repurposing → monitoramento de receita. Máximo ROI por ciclo.
**Total de steps:** 20
**Workers máximos:** 14

   **1. seo_research** → `seo_research`
      _Keywords com potencial de conversão._
      Sem dependências

   **2. compliance** → `compliance`
      _Validar compliance._
      Sem dependências

   **3. memory_lookup** → `memory_lookup`
      _Lições de ciclos anteriores._
      Sem dependências

   **4. offer_lookup** → `offer_lookup`
      _Ofertas de afiliados com maior comissão._
      Depende de: seo_research

   **5. content_planner** → `content_planner`
      _Briefings otimizados para conversão._
      Depende de: seo_research, offer_lookup, memory_lookup

   **6. content_generator** → `content_generator`
      _Artigos foco em conversão._
      Depende de: content_planner

   **7. content_repurposer** → `content_repurposer`
      _Multiplicar para 5 canais automaticamente._
      Depende de: content_generator, offer_lookup, seo_research

   **8. free_image_gen** → `free_image_gen`
      _Gerar imagens gratuitas (Pillow) para blog, YouTube, Pinterest, Instagram._
      Depende de: content_generator, content_repurposer

   **9. free_video_producer** → `free_video_producer`
      _Produzir vídeos gratuitos (moviepy) para YouTube e TikTok._
      Depende de: content_generator, content_repurposer

   **10. platform_compliance** → `platform_compliance`
      _Validar conteúdo contra regras de cada plataforma para evitar bloqueios._
      Depende de: content_generator, content_repurposer, free_image_gen, free_video_producer

   **11. instagram_marketing** → `instagram_marketing`
      _Posts para Instagram._
      Depende de: seo_research, offer_lookup, content_generator

   **12. tiktok_marketing** → `tiktok_marketing`
      _Vídeos para TikTok._
      Depende de: seo_research, offer_lookup, content_generator

   **13. twitter_marketing** → `twitter_marketing`
      _Threads para Twitter._
      Depende de: seo_research, offer_lookup, content_generator

   **14. wp_publisher** → `wp_publisher`
      _Publicar no WordPress._
      Depende de: content_generator, compliance

   **15. revenue_monitor** → `revenue_monitor`
      _Projeções de receita e ROI._
      Depende de: content_repurposer, offer_lookup, wp_publisher

   **16. analytics_feedback** → `analytics_feedback`
      _Feedback final do ciclo._
      Depende de: content_repurposer, revenue_monitor, wp_publisher

   **17. organic_growth** → `organic_growth`
      _Analisar ciclo e gerar recomendações de growth hacking orgânico._
      Depende de: analytics_feedback, platform_compliance, revenue_monitor

   **18. agent_perf_monitor** → `agent_perf_monitor`
      _Monitorar performance individual de cada agente no ciclo._
      Depende de: organic_growth

   **19. meta_orchestrator** → `meta_orchestrator`
      _Auto-observar execução e modificar estrutura do workflow._
      Depende de: agent_perf_monitor

   **20. strategy_evolution** → `strategy_evolution`
      _Planejamento estratégico evolutivo entre ciclos._
      Depende de: meta_orchestrator

**Fluxo DAG:**
   `seo_research` → offer_lookup → content_planner → content_repurposer → instagram_marketing → tiktok_marketing → twitter_marketing
   `offer_lookup` → content_planner → content_repurposer → instagram_marketing → tiktok_marketing → twitter_marketing → revenue_monitor
   `memory_lookup` → content_planner
   `content_planner` → content_generator
   `content_generator` → content_repurposer → free_image_gen → free_video_producer → platform_compliance → instagram_marketing → tiktok_marketing → twitter_marketing → wp_publisher
   `content_repurposer` → free_image_gen → free_video_producer → platform_compliance → revenue_monitor → analytics_feedback
   `free_image_gen` → platform_compliance
   `free_video_producer` → platform_compliance
   `compliance` → wp_publisher
   `wp_publisher` → revenue_monitor → analytics_feedback
   `revenue_monitor` → analytics_feedback → organic_growth
   `analytics_feedback` → organic_growth
   `platform_compliance` → organic_growth
   `organic_growth` → agent_perf_monitor
   `agent_perf_monitor` → meta_orchestrator
   `meta_orchestrator` → strategy_evolution

---

## safe_mass_posting_workflow

**Nome:** safe_mass_posting_workflow
**Descrição:** Sem descrição
**Total de steps:** 8

   **1. collect_articles** → `content_generator`
      _Coleta artigos gerados para distribuicao_
      Sem dependências

   **2. validate_all_posts** → `safe_mass_posting`
      _Valida cada artigo para cada plataforma contra limites de spam_
      Sem dependências

   **3. check_compliance** → `platform_compliance`
      _Verifica regras especificas de cada plataforma (termos, copyright, disclosure)_
      Sem dependências

   **4. generate_posting_plan** → `safe_mass_posting`
      _Gera plano de postagem com timing ideal e volume seguro_
      Sem dependências

   **5. repurpose_for_platforms** → `content_repurposer`
      _Adapta cada artigo para o formato ideal de cada plataforma_
      Sem dependências

   **6. schedule_posts** → `content_scheduler`
      _Agenda posts nos melhores horarios de cada plataforma_
      Sem dependências

   **7. execute_posts** → `social_publishers`
      _Publica ou salva arquivos prontos para cada plataforma_
      Sem dependências

   **8. log_and_memory** → `safe_mass_posting`
      _Registra todos os posts publicados na memoria para controle anti-spam_
      Sem dependências


---

## seo_content_workflow

**Nome:** Ciclo Diário de Conteúdo SEO-Otimizado
**Descrição:** Pesquisa, gera, valida e publica conteúdo otimizado para Google, Bing e Yahoo (ADR-002)
**Total de steps:** 9

   **1. keyword_research** → `ContentResearchAgent`
      _Pesquisa keywords com potencial de busca, analisa concorrência e identifica gaps_
      Sem dependências

   **2. content_strategy** → `ContentStrategistAgent`
      _Define pauta baseada nos dados de pesquisa_
      Sem dependências

   **3. seo_content_writing** → `SEOContentWriterAgent`
      _Escreve artigos completos otimizados para múltiplos buscadores_
      Sem dependências

   **4. eeat_validation** → `EEATValidatorAgent`
      _Valida artigos contra critérios E-E-A-T do Google_
      Sem dependências

   **5. seo_technical** → `SEOTechnicalAgent`
      _Aplica schema markup, meta tags, Open Graph, Twitter Cards_
      Sem dependências

   **6. multimedia_generation** → `SEOMultimediaAgent`
      _Gera imagens destacadas, infográficos e tabelas comparativas_
      Sem dependências

   **7. internal_linking** → `InternalLinkerAgent`
      _Cria malha de links internos entre artigos_
      Sem dependências

   **8. site_publish** → `SitePublisherAgent`
      _Publica site estático, sitemap.xml e robots.txt_
      Sem dependências

   **9. search_console_submit** → `SitePublisherAgent`
      _Notifica Google e Bing sobre novos artigos_
      Sem dependências


---

## sixth_order_workflow

**Nome:** sixth_order_workflow
**Descrição:** 6a Ordem: Inteligencia Criativa. Descobre novos nichos, cria configuracoes, gera produtos e ofertas. Expansao autonoma do sistema.
**Total de steps:** 4
**Workers máximos:** 3

   **1. market_scan** → `creative_engine`
      _Escaneiar 15+ dominios de mercado e rankear oportunidades._
      Sem dependências

   **2. niche_genesis** → `niche_genesis`
      _Criar configuracao completa de nicho para top oportunidades._
      Depende de: market_scan

   **3. value_generation** → `novel_value`
      _Gerar produtos digitais, servicos e angulos de conteudo._
      Depende de: niche_genesis

   **4. creative_synthesis** → `creative_engine`
      _Sintetizar resultados: nichos prontos para lancamento._
      Depende de: market_scan, niche_genesis, value_generation

**Fluxo DAG:**
   `market_scan` → niche_genesis → creative_synthesis
   `niche_genesis` → value_generation → creative_synthesis
   `value_generation` → creative_synthesis

---

## third_order_transcendence

**Nome:** Onda 3 — Transcendência: Sistema Autopilot de 3ª Ordem
**Descrição:** Ciclo de auto-transcendência: conecta Onda 1 (SEO) + Onda 2 (Receita) + aprende + evolui + cruza domínios
**Total de steps:** 9

   **1. knowledge_synthesis** → `KnowledgeSynthesisBridge`
      _Sintetiza conhecimento de todos os domínios: SEO, Receita, Conteúdo, Meta_
      Sem dependências

   **2. cross_pollination** → `CrossPollinationHub`
      _Ativa loops virtuosos entre domínios: conteúdo → produto → receita → mais conteúdo_
      Sem dependências

   **3. epistemic** → `EpistemicAgent`
      _Auto-questionamento epistêmico: o que o sistema sabe, o que não sabe, pontos cegos_
      Sem dependências

   **4. observer_fusion** → `ObserverFusionAgent`
      _Modelagem multi-perspectiva do estado atual do sistema_
      Sem dependências

   **5. value_evolution** → `ValueEvolutionAgent`
      _Evolui os critérios de sucesso baseado em performance multi-domínio_
      Sem dependências

   **6. agent_factory** → `AgentFactory`
      _Detecta necessidade de novos agentes e gera código_
      Sem dependências

   **7. meta_orchestrator** → `MetaOrchestratorAgent`
      _Analisa performance de todos os ciclos e gera prescrições de evolução_
      Sem dependências

   **8. recursive_observer** → `RecursiveObserverAgent`
      _Meta-meta: observa o MetaOrchestrator e sugere melhorias na governança_
      Sem dependências

   **9. third_order_orchestrator** → `ThirdOrderOrchestrator`
      _Sintetiza todos os insights de 3ª ordem em recomendações transcendentes_
      Sem dependências


---

## third_order_workflow

**Nome:** third_order
**Descrição:** 🌀 PIPELINE DE AUTO-TRANSCENDÊNCIA (3ª ORDEM) — Epistêmico → Fusão de Observadores → Evolução de Valores → Observador Recursivo → Orquestração Transcendente. O sistema que observa como se observa.
**Total de steps:** 5
**Workers máximos:** 4

   **1. epistemic** → `epistemic`
      _Auto-questionamento epistêmico: mapear conhecimento, detectar pontos cegos, gerar hipóteses alternativas._
      Sem dependências

   **2. observer_fusion** → `observer_fusion`
      _Modelagem multi-perspectiva: analisar problema sob múltiplos observadores simultaneamente._
      Sem dependências

   **3. value_evolution** → `value_evolution`
      _Evolução do sistema de valores: detectar conflitos e sugerir evolução dos critérios de sucesso._
      Sem dependências

   **4. recursive_observer** → `recursive_observer`
      _Meta-meta-orquestração: auditar a governança do sistema e sugerir melhorias no MetaOrchestrator._
      Sem dependências

   **5. third_order_orchestrator** → `third_order_orchestrator`
      _Sintetizar insights de terceira ordem e gerar recomendações de auto-transcendência._
      Depende de: epistemic, observer_fusion, value_evolution, recursive_observer

**Fluxo DAG:**
   `epistemic` → third_order_orchestrator
   `observer_fusion` → third_order_orchestrator
   `value_evolution` → third_order_orchestrator
   `recursive_observer` → third_order_orchestrator

---

## traffic_recycling_workflow

**Nome:** traffic_recycling_workflow
**Descrição:** Sem descrição
**Total de steps:** 4

   **1. traffic_recycling_analysis** → `traffic_recycler`
      _Analisa artigos e recomenda caminhos de monetização adicionais_
      Sem dependências

   **2. generate_interstitials** → `traffic_recycler`
      _Gera HTML para elementos de monetização (lead magnet, popup, cross-niche)_
      Sem dependências

   **3. update_site_template** → `site_deploy`
      _Adiciona elementos de reciclagem ao template do site_
      Sem dependências

   **4. memory_update** → `traffic_recycler`
      _Atualiza memória com dados de conversão e performance_
      Sem dependências


---

## ultimate_workflow

**Nome:** ultimate_workflow
**Descrição:** 🏆 WORKFLOW DEFINITIVO — 9 canais de tráfego orgânico: blog + YouTube + email + Pinterest + Instagram + TikTok + Twitter + WhatsApp + lead capture + site.
**Total de steps:** 27
**Workers máximos:** 14

   **1. competitor_analysis** → `competitor_analysis`
      _Analisar concorrentes e gaps._
      Sem dependências

   **2. seo_scraper** → `seo_scraper`
      _Dados reais de SEO do Google._
      Depende de: competitor_analysis

   **3. compliance** → `compliance`
      _Validar compliance._
      Sem dependências

   **4. memory_lookup** → `memory_lookup`
      _Buscar lições de ciclos anteriores._
      Sem dependências

   **5. offer_lookup** → `offer_lookup`
      _Ofertas de afiliados compatíveis._
      Depende de: seo_scraper, competitor_analysis

   **6. content_planner** → `content_planner`
      _Briefings integrados._
      Depende de: seo_scraper, offer_lookup, memory_lookup

   **7. content_generator** → `content_generator`
      _Artigos para blog._
      Depende de: content_planner

   **8. content_repurposer** → `content_repurposer`
      _Multiplicar conteúdo para todos os canais._
      Depende de: content_generator, offer_lookup

   **9. free_image_gen** → `free_image_gen`
      _Gerar imagens gratuitas (Pillow) para blog, YouTube, Pinterest, Instagram._
      Depende de: content_generator, content_repurposer, site_deploy

   **10. free_video_producer** → `free_video_producer`
      _Produzir vídeos gratuitos (moviepy) para YouTube e TikTok._
      Depende de: content_generator, content_repurposer, site_deploy

   **11. platform_compliance** → `platform_compliance`
      _Validar conteúdo contra regras de cada plataforma para evitar bloqueios._
      Depende de: content_generator, content_repurposer, free_image_gen, free_video_producer

   **12. youtube_marketing** → `youtube_marketing`
      _Scripts para YouTube._
      Depende de: seo_scraper, offer_lookup, content_generator

   **13. email_marketing** → `email_marketing`
      _Sequências de email._
      Depende de: seo_scraper, offer_lookup

   **14. pinterest_marketing** → `pinterest_marketing`
      _Pins para Pinterest._
      Depende de: seo_scraper, offer_lookup, content_generator

   **15. instagram_marketing** → `instagram_marketing`
      _Posts para Instagram._
      Depende de: seo_scraper, offer_lookup, content_generator

   **16. tiktok_marketing** → `tiktok_marketing`
      _Vídeos para TikTok._
      Depende de: seo_scraper, offer_lookup, content_generator

   **17. twitter_marketing** → `twitter_marketing`
      _Threads para Twitter._
      Depende de: seo_scraper, offer_lookup, content_generator

   **18. whatsapp_marketing** → `whatsapp_marketing`
      _Mensagens para WhatsApp._
      Depende de: seo_scraper, offer_lookup, content_generator

   **19. lead_capture** → `lead_capture`
      _Lead magnets e landing page._
      Depende de: seo_scraper, offer_lookup, content_generator

   **20. wp_publisher** → `wp_publisher`
      _Publicar no WordPress._
      Depende de: content_generator, compliance

   **21. site_deploy** → `site_deploy`
      _Gerar site estático._
      Depende de: content_generator, lead_capture

   **22. revenue_monitor** → `revenue_monitor`
      _Projeção de receita._
      Depende de: content_repurposer, offer_lookup, youtube_marketing, email_marketing

   **23. analytics_feedback** → `analytics_feedback`
      _Avaliar ciclo e aprender._
      Depende de: site_deploy, revenue_monitor, youtube_marketing, instagram_marketing, tiktok_marketing, twitter_marketing, whatsapp_marketing, lead_capture, wp_publisher

   **24. organic_growth** → `organic_growth`
      _Analisar ciclo e gerar recomendações de growth hacking orgânico._
      Depende de: analytics_feedback, platform_compliance, revenue_monitor

   **25. agent_perf_monitor** → `agent_perf_monitor`
      _Monitorar performance individual de cada agente no ciclo._
      Depende de: organic_growth

   **26. meta_orchestrator** → `meta_orchestrator`
      _Auto-observar execução e modificar estrutura do workflow._
      Depende de: agent_perf_monitor

   **27. strategy_evolution** → `strategy_evolution`
      _Planejamento estratégico evolutivo entre ciclos._
      Depende de: meta_orchestrator

**Fluxo DAG:**
   `competitor_analysis` → seo_scraper → offer_lookup
   `seo_scraper` → offer_lookup → content_planner → youtube_marketing → email_marketing → pinterest_marketing → instagram_marketing → tiktok_marketing → twitter_marketing → whatsapp_marketing → lead_capture
   `offer_lookup` → content_planner → content_repurposer → youtube_marketing → email_marketing → pinterest_marketing → instagram_marketing → tiktok_marketing → twitter_marketing → whatsapp_marketing → lead_capture → revenue_monitor
   `memory_lookup` → content_planner
   `content_planner` → content_generator
   `content_generator` → content_repurposer → free_image_gen → free_video_producer → platform_compliance → youtube_marketing → pinterest_marketing → instagram_marketing → tiktok_marketing → twitter_marketing → whatsapp_marketing → lead_capture → wp_publisher → site_deploy
   `content_repurposer` → free_image_gen → free_video_producer → platform_compliance → revenue_monitor
   `site_deploy` → free_image_gen → free_video_producer → analytics_feedback
   `free_image_gen` → platform_compliance
   `free_video_producer` → platform_compliance
   `compliance` → wp_publisher
   `lead_capture` → site_deploy → analytics_feedback
   `youtube_marketing` → revenue_monitor → analytics_feedback
   `email_marketing` → revenue_monitor
   `revenue_monitor` → analytics_feedback → organic_growth
   `instagram_marketing` → analytics_feedback
   `tiktok_marketing` → analytics_feedback
   `twitter_marketing` → analytics_feedback
   `whatsapp_marketing` → analytics_feedback
   `wp_publisher` → analytics_feedback
   `analytics_feedback` → organic_growth
   `platform_compliance` → organic_growth
   `organic_growth` → agent_perf_monitor
   `agent_perf_monitor` → meta_orchestrator
   `meta_orchestrator` → strategy_evolution

---

---

## 🎨 UI Design Workflow (NOVO)

**Workflow:** `ui_design_workflow.json` — Gera landing pages completas com componentes UI/UX 21st.dev

**Steps:**
| Step | Agent | Depends On | Descrição |
|------|-------|-----------|-----------|
| 1. niche_analysis | analytics | — | Análise de nicho e objetivo |
| 2. hero_generation | ui_hero | niche_analysis | Hero section com badge, CTA, proof |
| 3. pricing_generation | ui_pricing | niche_analysis | Tabela de preços 3 planos |
| 4. faq_generation | ui_faq | niche_analysis | FAQ accordion schema.org |
| 5. testimonial_generation | ui_testimonial | niche_analysis | Cards de depoimento |
| 6. page_composition | ui_full_page | steps 2-5 | Landing page completa |
| 7. quality_check | memory_lookup | page_composition | Validação OutputCritic ≥85 |

```bash
# Executar workflow de design
PYTHONPATH=src python3 -c "
from campaign_autopilot.workflow import WorkflowRunner
runner = WorkflowRunner('workflows/ui_design_workflow.json', max_workers=3)
runner.run({'campaign': {'niche': 'marketing digital', 'goal': 'landing page'}})
"
```


## 👁️ teamworker_preview (NOVO)

**Workflow:** `teamworker_preview.json` — Preview completo do pipeline antes da execução real.

**Objetivo:** Verificar se existem produtos afiliados disponíveis antes de gerar qualquer conteúdo. Garantir que a ordem de operação seja: produtos → conteúdo → mídia → design.

**Steps:**
| Step | Agent | Depends On | Descrição |
|------|-------|-----------|-----------|
| 1. offer_lookup | offer_lookup | — | Busca produtos afiliados em 9 redes (Hotmart, Kiwify, Eduzz, Amazon, etc) |
| 2. compliance | compliance | — | Verifica conformidade dos produtos encontrados |
| 3. content_planner | content_planner | offer_lookup | Planeja conteúdo baseado nos produtos disponíveis |
| 4. content_preview | content_generator | content_planner | Gera preview do conteúdo sem publicar |
| 5. media_preview | free_image_gen | content_preview | Preview das mídias associadas |
| 6. ui_preview | ui_design | content_preview | Preview do design/landing page |
| 7. preview_summary | analytics | media_preview, ui_preview | Relatório consolidado do preview |

```bash
# Executar preview
PYTHONPATH=src python3 -c "
from campaign_autopilot.workflow import WorkflowRunner
runner = WorkflowRunner('workflows/teamworker_preview.json', max_workers=4)
runner.run({'campaign': {'mode': 'preview', 'validate_offers': True}})
"
```
