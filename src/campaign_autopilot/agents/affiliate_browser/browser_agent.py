"""AffiliateBrowserAgent — Automacao de navegacao em marketplaces de afiliados.

Usa Playwright para:
1. Navegar ate a conta do usuario nos marketplaces
2. Varrer categorias/nichos em busca de produtos
3. Extrair links de afiliado reais
4. Aplicar scoring do Hotmart Intelligence Protocol
5. Registrar no ProductLinkRegistry

Plataformas suportadas:
- Hotmart (hotmart.com/pt-br/marketplace)
- Kiwify (kiwify.com.br/marketplace)
- Eduzz (eduzz.com/marketplace)
- Monetizze (monetizze.com.br)
- Mercado Livre (mercadolivre.com.br/afiliados)
- Shopee (shopee.com.br/afiliados)
- Shein (shein.com.br/afiliados)
- AliExpress (aliexpress.com/afiliados)

Cada plataforma requer sessao salva (login unico do usuario).
O sistema reusa cookies salvos em .state/browser_sessions/
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
    TimeoutError as PlaywrightTimeout,
)

from ...affiliate import ProductLinkRegistry

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
_SESSION_DIR = _PROJECT_ROOT / ".state" / "browser_sessions"
_SESSION_DIR.mkdir(parents=True, exist_ok=True)
_PRODUCT_LINKS_DB = str(_PROJECT_ROOT / ".state" / "product_links.db")


# ── Plataformas configuradas ─────────────────────────────────────────

PLATFORM_CONFIGS: dict[str, dict[str, Any]] = {
    "hotmart": {
        "name": "Hotmart",
        "login_url": "https://sso.hotmart.com/login",
        "marketplace_url": "https://hotmart.com/marketplace",
        "selectors": {
            "email_input": 'input#username',
            "password_input": 'input#password',
            "login_button": 'button:has-text("Log in")',
            "search_input": 'input[placeholder*="search"], input[type="search"]',
            "product_card": 'div[class*="card"], a[href*="/product"]',
            "product_name": 'p[class*="title"], h2',
            "product_price": 'p[class*="price"]',
            "affiliate_btn": 'button:has-text("Promote"), a:has-text("Promote")',
            "affiliate_link": 'input[readonly], [class*="affiliate-link"]',
        },
        "cookie_name": "hotmart_session.json",
    },
    "kiwify": {
        "name": "Kiwify",
        "login_url": "https://kiwify.com.br/login",
        "marketplace_url": "https://kiwify.com.br/marketplace",
        "selectors": {
            "search_input": 'input[type="search"], input[placeholder*="busca"]',
            "product_card": '[class*="product"], [class*="card"]',
            "product_name": 'h2, h3, [class*="name"]',
            "product_price": '[class*="price"]',
            "affiliate_btn": 'button:has-text("Promover"), a:has-text("Afiliar")',
            "affiliate_link": '[class*="link"], input[readonly]',
        },
        "cookie_name": "kiwify_session.json",
    },
    "eduzz": {
        "name": "Eduzz",
        "login_url": "https://eduzz.com/login",
        "marketplace_url": "https://eduzz.com/marketplace",
        "selectors": {
            "search_input": 'input[type="search"]',
            "product_card": '[class*="product"]',
            "product_name": 'h2, h3',
            "product_price": '[class*="price"]',
            "affiliate_btn": 'a:has-text("Promover"), button:has-text("Afiliar")',
            "affiliate_link": 'input[readonly], [class*="link"]',
        },
        "cookie_name": "eduzz_session.json",
    },
    "monetizze": {
        "name": "Monetizze",
        "login_url": "https://monetizze.com.br/login",
        "marketplace_url": "https://monetizze.com.br/marketplace",
        "selectors": {},
        "cookie_name": "monetizze_session.json",
    },
}


# ── Gerenciador de Sessoes ───────────────────────────────────────────

class SessionManager:
    """Gerencia sessoes salvas (cookies) para cada plataforma."""

    @staticmethod
    def save_session(context: BrowserContext, platform: str) -> None:
        """Salva cookies apos login manual do usuario."""
        cookies = context.cookies()
        path = _SESSION_DIR / PLATFORM_CONFIGS[platform]["cookie_name"]
        with open(path, "w") as f:
            json.dump(cookies, f)
        print(f"  ✅ Sessao salva: {path}")

    @staticmethod
    def load_session(context: BrowserContext, platform: str) -> bool:
        """Carrega cookies salvos."""
        path = _SESSION_DIR / PLATFORM_CONFIGS[platform]["cookie_name"]
        if not path.exists():
            return False
        try:
            with open(path) as f:
                cookies = json.load(f)
            context.add_cookies(cookies)
            return True
        except Exception:
            return False

    @staticmethod
    def has_session(platform: str) -> bool:
        path = _SESSION_DIR / PLATFORM_CONFIGS[platform]["cookie_name"]
        return path.exists()

    @staticmethod
    def session_info() -> dict[str, bool]:
        return {
            p: SessionManager.has_session(p)
            for p in PLATFORM_CONFIGS
        }


# ── Login Manager ────────────────────────────────────────────────────

class LoginManager:
    """Gerencia login do usuario nas plataformas.

    Fluxo:
    1. Tenta carregar sessao salva
    2. Se falhar, tenta login headless com credenciais
    3. Se falhar, orienta usuario a exportar cookies manualmente
    4. Salva sessao para uso futuro
    """

    @staticmethod
    def ensure_login(platform: str, page: Page, playwright: Playwright,
                     headless: bool = True) -> bool:
        """Garante que o usuario esta logado na plataforma."""
        cfg = PLATFORM_CONFIGS[platform]

        # Tentar carregar sessao salva
        context = page.context
        if SessionManager.load_session(context, platform):
            # Verificar se sessao ainda e valida
            page.goto(cfg["marketplace_url"], wait_until="domcontentloaded",
                      timeout=30000)
            time.sleep(2)
            # Se nao redirecionou para login, sessao valida
            if "login" not in page.url.lower():
                return True

        # Tenta login headless com credenciais do .env ou prompt
        email = os.environ.get(f"{platform.upper()}_EMAIL", "")
        password = os.environ.get(f"{platform.upper()}_PASSWORD", "")

        if not email or not password:
            print(f"\n🔐 Login necessario para {cfg['name']}")
            print(f"   Nao ha credenciais configuradas em .env")
            print(f"   Adicione ao .env:")
            print(f"   {platform.upper()}_EMAIL=seu@email.com")
            print(f"   {platform.upper()}_PASSWORD=sua_senha")
            print(f"\n   Ou exporte os cookies manualmente:")
            print(f"   1. Faca login no {cfg['login_url']} pelo navegador")
            print(f"   2. Instale extensao 'Get cookies.txt' ")
            print(f"   3. Exporte cookies para .state/browser_sessions/{cfg['cookie_name']}")
            return False

        # Login headless
        try:
            page.goto(cfg["login_url"], wait_until="networkidle", timeout=30000)
            time.sleep(2)

            # Preencher email
            email_input = page.query_selector("input[type='email'], input[name='email'], input[name='login']")
            if email_input:
                email_input.fill(email)
                time.sleep(1)

            # Preencher senha
            password_input = page.query_selector("input[type='password']")
            if password_input:
                password_input.fill(password)
                time.sleep(1)

            # Clicar em entrar
            submit_btn = page.query_selector(
                "button[type='submit'], button:has-text('Entrar'), button:has-text('Login')"
            )
            if submit_btn:
                submit_btn.click()
                time.sleep(5)

            # Aguardar navegacao pos-login
            try:
                page.wait_for_url(
                    "**/marketplace**/**",
                    timeout=30000,
                )
            except PlaywrightTimeout:
                pass

            # Verificar se o login foi bem-sucedido
            if "login" not in page.url.lower():
                # Salvar sessao
                SessionManager.save_session(context, platform)
                print(f"   ✅ Login automatizado bem-sucedido!")
                return True
            else:
                print(f"   ❌ Login falhou. Verifique credenciais em .env")
                return False

        except Exception as e:
            print(f"   ❌ Erro durante login: {e}")
            return False

    @staticmethod
    def login_with_credentials(platform: str, email: str, password: str,
                                playwright: Playwright | None = None,
                                context: BrowserContext | None = None) -> bool:
        """Login direto com credenciais fornecidas."""
        if playwright is None:
            p = sync_playwright().start()
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context()
            page = ctx.new_page()
        else:
            p = playwright
            ctx = context or p.chromium.launch(headless=True).new_context()
            page = ctx.new_page()

        cfg = PLATFORM_CONFIGS[platform]
        try:
            page.goto(cfg["login_url"], wait_until="networkidle", timeout=30000)
            time.sleep(2)

            # Tenta varios seletores de email
            cfg_sel = PLATFORM_CONFIGS.get(platform, {})
            email_sel = cfg_sel.get('selectors', {}).get('email_input', "input#username")
            pw_sel = cfg_sel.get('selectors', {}).get('password_input', "input#password")
            btn_sel = cfg_sel.get('selectors', {}).get('login_button', "button[type='submit']")
            
            inp = page.query_selector(email_sel)
            if inp:
                inp.fill(email)
                time.sleep(1)
            else:
                for sel in ["input[type='email']", "input[name='email']", 
                            "input[name='login']", "input[placeholder*='email']", "input#username"]:
                    inp = page.query_selector(sel)
                    if inp:
                        inp.fill(email)
                        break
            time.sleep(1)

            # Senha
            pw = page.query_selector(pw_sel)
            if pw:
                pw.fill(password)
            else:
                pw = page.query_selector("input[type='password']")
                if pw:
                    pw.fill(password)
            time.sleep(1)

            # Submit
            btn = page.query_selector(btn_sel)
            if btn:
                btn.click()
            else:
                for sel in ["button[type='submit']", "button:has-text('Entrar')",
                            "button:has-text('Log in')", "button:has-text('Login')", "button:has-text('Continuar')"]:
                    btn = page.query_selector(sel)
                    if btn:
                        btn.click()
                        break
            time.sleep(5)

            success = "login" not in page.url.lower()
            if success:
                SessionManager.save_session(ctx, platform)
                print(f"   ✅ Login em {cfg['name']} bem-sucedido!")
            return success
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return False
        finally:
            if playwright is None:
                page.close()
                ctx.close()
                browser.close()
                p.stop()


# ── Scraper Base ─────────────────────────────────────────────────────

class PlatformScraper:
    """Scraper base para uma plataforma de afiliados."""

    def __init__(self, platform: str, page: Page, playwright: Playwright,
                 registry: ProductLinkRegistry | None = None):
        self.platform = platform
        self.cfg = PLATFORM_CONFIGS[platform]
        self.page = page
        self.playwright = playwright
        self.registry = registry or ProductLinkRegistry()
        self._headless = True

    def discover_products(self, niche: str, max_products: int = 20) -> list[dict[str, Any]]:
        """Descobre produtos no marketplace para um nicho."""
        raise NotImplementedError

    def get_affiliate_link(self, product_url: str) -> str:
        """Obtem o link de afiliado real para um produto."""
        raise NotImplementedError


class HotmartScraper(PlatformScraper):
    """Scraper para Hotmart Marketplace."""

    def __init__(self, page: Page, playwright: Playwright,
                 registry: ProductLinkRegistry | None = None):
        super().__init__("hotmart", page, playwright, registry)

    def discover_products(self, niche: str, max_products: int = 20) -> list[dict[str, Any]]:
        """Navega no marketplace Hotmart e extrai produtos."""
        results: list[dict[str, Any]] = []
        try:
            # Navegar para o marketplace
            url = f"{self.cfg['marketplace_url']}?query={niche}"
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            # Tentar scroll para carregar mais produtos
            for _ in range(3):
                self.page.evaluate("window.scrollBy(0, 800)")
                time.sleep(1)

            # Extrair produtos
            cards = self.page.query_selector_all(
                self.cfg["selectors"].get("product_card", "article, [class*='product']")
            )
            for card in cards[:max_products]:
                try:
                    name_el = card.query_selector(
                        self.cfg["selectors"].get("product_name", "h2, h3")
                    )
                    price_el = card.query_selector(
                        self.cfg["selectors"].get("product_price", "[class*='price']")
                    )
                    name = name_el.inner_text().strip() if name_el else ""
                    price_text = price_el.inner_text().strip() if price_el else ""

                    # Tentar obter link de afiliado
                    affiliate_link = self._get_affiliate_link_from_card(card)

                    product_data = {
                        "network": self.platform,
                        "product_name": name,
                        "price": price_text,
                        "affiliate_link": affiliate_link or "",
                        "niche": niche,
                    }
                    if name:
                        results.append(product_data)
                except Exception:
                    continue

        except Exception as e:
            print(f"  ⚠️ Erro ao sondar {self.platform}: {e}")

        return results

    def _get_affiliate_link_from_card(self, card) -> str:
        """Tenta extrair link de afiliado de um card de produto."""
        try:
            btn = card.query_selector(
                self.cfg["selectors"].get("affiliate_btn", "button, a")
            )
            if btn:
                btn.click()
                time.sleep(2)
                link_el = self.page.query_selector(
                    self.cfg["selectors"].get("affiliate_link", "input[readonly]")
                )
                if link_el:
                    return link_el.get_attribute("value") or link_el.inner_text().strip()
        except Exception:
            pass
        return ""

    def get_affiliate_link(self, product_url: str) -> str:
        """Navega ate a pagina do produto e obtem link de afiliado."""
        try:
            self.page.goto(product_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            btn = self.page.query_selector(
                self.cfg["selectors"].get("affiliate_btn", 'a:has-text("Promover")')
            )
            if btn:
                btn.click()
                time.sleep(2)
                link_el = self.page.query_selector(
                    self.cfg["selectors"].get("affiliate_link", "input[readonly]")
                )
                if link_el:
                    return link_el.get_attribute("value") or link_el.inner_text().strip()
        except Exception:
            pass
        return ""


class KiwifyScraper(PlatformScraper):
    """Scraper para Kiwify Marketplace."""

    def __init__(self, page: Page, playwright: Playwright,
                 registry: ProductLinkRegistry | None = None):
        super().__init__("kiwify", page, playwright, registry)

    def discover_products(self, niche: str, max_products: int = 20) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        try:
            url = f"{self.cfg['marketplace_url']}?q={niche}"
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            items = self.page.query_selector_all(
                self.cfg["selectors"].get("product_card", "a[href*='product'], [class*='product']")
            )
            for item in items[:max_products]:
                try:
                    href = item.get_attribute("href") or ""
                    name = item.inner_text().strip().split("\n")[0]
                    results.append({
                        "network": self.platform,
                        "product_name": name,
                        "affiliate_link": href if "pay.kiwify" in href else "",
                        "niche": niche,
                    })
                except Exception:
                    continue

        except Exception as e:
            print(f"  ⚠️ Erro ao sondar {self.platform}: {e}")

        return results

    def get_affiliate_link(self, product_url: str) -> str:
        return product_url  # Kiwify links are direct


# ── Orquestrador Principal ───────────────────────────────────────────

class AffiliateBrowserAgent:
    """Agente orquestrador de automacao de navegacao em marketplaces.

    Uso:
        agent = AffiliateBrowserAgent()
        agent.login("hotmart")  # Login manual unico
        results = agent.scan_platform("hotmart", "marketing digital")
        agent.register_results(results)
    """

    def __init__(self, registry: ProductLinkRegistry | None = None):
        self.registry = registry or ProductLinkRegistry()
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._initialized = False

    def _init_browser(self, headless: bool = True) -> None:
        """Inicializa o Playwright browser."""
        if self._initialized:
            return
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        self._context = self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 720},
        )
        self._page = self._context.new_page()
        self._initialized = True

    def close(self) -> None:
        """Fecha o browser."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self._initialized = False

    def __enter__(self) -> "AffiliateBrowserAgent":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ── Login ──────────────────────────────────────────────────────

    def login(self, platform: str, headless: bool = True) -> bool:
        """Faz login na plataforma (manual na primeira vez, depois reusa sessao)."""
        if platform not in PLATFORM_CONFIGS:
            print(f"  ❌ Plataforma '{platform}' nao configurada")
            return False

        self._init_browser(headless=headless)
        assert self._page is not None
        assert self._playwright is not None

        return LoginManager.ensure_login(
            platform, self._page, self._playwright, headless=headless
        )

    def login_interactive(self, platform: str) -> bool:
        """Obtem cookies de sessao para login com Google/OAuth.

        Como voce usa login com Google, o metodo recomendado e:
        1. Faca login no navegador NORMAL
        2. Exporte cookies via extensao
        3. Salve no diretorio de sessoes
        """
        cfg = PLATFORM_CONFIGS.get(platform, {})
        cookie_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / ".state" / "browser_sessions"
        cookie_path = cookie_dir / cfg.get("cookie_name", f"{platform}_session.json")

        print(f"\n🔔 Configurar Login: {cfg.get('name', platform)}")
        print(f"   URL: {cfg.get('login_url', '')}")
        print()
        print("   COMO EXPORTAR COOKIES (login com Google):")
        print("   1. Acesse a URL acima no seu navegador NORMAL")
        print("   2. Faca login com sua conta Google")
        print("   3. Instale extensao exportadora de cookies:")
        print("      Chrome: 'Get cookies.txt' ou 'Cookie-Editor'")
        print("      Firefox: 'cookies.txt' ou 'Cookie Quick Manager'")
        print("   4. Exporte os cookies da pagina (formato JSON)")
        print(f"   5. Salve o arquivo como: {cookie_path}")
        print()
        print("   Formato JSON esperado:")
        print('     [{"name":"session","value":"abc","domain":".hotmart.com",...}]')
        print()
        print("   Ou configure .env para login automatico:")
        print(f"     {platform.upper()}_EMAIL=seu@email.com")
        print(f"     {platform.upper()}_PASSWORD=sua_senha")

        if cookie_path.exists():
            print(f"\n   ✅ Cookie ja existe: {cookie_path}")
            return True

        ans = input("\n   Tentar abrir navegador virtual (xvfb)? (s/N): ").strip().lower()
        if ans == 's':
            return self._xvfb_login(platform)

        print()
        print("   Exporte os cookies manualmente e tente novamente.")
        return False

    def _xvfb_login(self, platform: str) -> bool:
        """Fallback: login via xvfb."""
        cfg = PLATFORM_CONFIGS.get(platform, {})
        print("\n   ⏳ Abrindo navegador virtual via xvfb...")
        import subprocess as _sp
        _script = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts" / "affiliate_browser.py"
        _cmd = ["xvfb-run", "-a", "--auto-servernum", sys.executable, str(_script), "_login_browser", platform]
        try:
            _sp.run(_cmd, capture_output=False, timeout=300)
        except _sp.TimeoutExpired:
            print("\n   ⚠️ Timeout.")
        if SessionManager.has_session(platform):
            print("\n   ✅ Sessao salva!")
            return True
        print("\n   ❌ Sessao NAO foi salva.")
        return False

    def scan_platform(self, platform: str, niche: str,
                      max_products: int = 20) -> list[dict[str, Any]]:
        """Varre uma plataforma em busca de produtos para um nicho."""
        if platform not in PLATFORM_CONFIGS:
            print(f"  ❌ Plataforma '{platform}' nao configurada")
            return []

        self._init_browser()
        assert self._page is not None
        assert self._playwright is not None

        # Garantir que esta logado
        if not self.login(platform):
            print(f"  ❌ Nao foi possivel fazer login em {platform}")
            return []

        # Criar scraper especifico
        scrapers: dict[str, type[PlatformScraper]] = {
            "hotmart": HotmartScraper,
            "kiwify": KiwifyScraper,
        }
        scraper_cls = scrapers.get(platform)
        if scraper_cls is None:
            print(f"  ⚠️ Scraper para {platform} ainda nao implementado")
            return []

        scraper = scraper_cls(self._page, self._playwright, self.registry)
        print(f"  🔍 Sondando {PLATFORM_CONFIGS[platform]['name']} para '{niche}'...")
        results = scraper.discover_products(niche, max_products)
        print(f"  ✅ Encontrados {len(results)} produtos em {platform}")
        return results

    def scan_all_platforms(self, niche: str,
                           max_products_per_platform: int = 10) -> dict[str, list[dict]]:
        """Varre todas as plataformas configuradas para um nicho."""
        all_results: dict[str, list[dict]] = {}
        for platform in PLATFORM_CONFIGS:
            try:
                results = self.scan_platform(platform, niche, max_products_per_platform)
                if results:
                    all_results[platform] = results
            except Exception as e:
                print(f"  ❌ Erro em {platform}: {e}")
        return all_results

    # ── Registro ───────────────────────────────────────────────────

    def register_results(self, results: list[dict[str, Any]],
                         auto_approve: bool = True) -> int:
        """Registra produtos encontrados no ProductLinkRegistry."""
        registered = 0
        for product in results:
            link = product.get("affiliate_link", "")
            name = product.get("product_name", "")
            network = product.get("network", "")
            niche = product.get("niche", "")

            if not link or not name:
                continue

            # Verificar se ja existe
            existing = self.registry.get_link(name, network)
            if existing:
                # Atualizar se o link for diferente
                if existing["affiliate_link"] != link:
                    self.registry.update_link(existing["link_id"], link)
                continue

            # Registrar
            self.registry.register(
                network=network,
                product_name=name,
                affiliate_link=link,
                category=niche,
                notes="Descoberto automaticamente via AffiliateBrowserAgent",
            )
            registered += 1

        return registered

    # ── Utilitarios ────────────────────────────────────────────────

    def session_status(self) -> dict[str, bool]:
        """Status das sessoes salvas."""
        return SessionManager.session_info()

    def run_full_scan(self, niches: list[str] | None = None,
                      max_per_platform: int = 10) -> dict[str, Any]:
        """Scan completo: todas as plataformas, todos os nichos.

        Fluxo:
        1. Para cada plataforma
        2. Para cada nicho
        3. Descobre produtos
        4. Aplica scoring basico
        5. Registra links
        """
        if niches is None:
            niches = [
                "marketing digital", "financas", "empreendedorismo",
                "ia", "saude", "desenvolvimento pessoal",
                "tecnologia", "moda", "beleza", "esportes",
            ]

        total_products = 0
        total_registered = 0
        platforms_ok = 0
        platforms_fail = 0

        for platform in PLATFORM_CONFIGS:
            print(f"\n{'='*50}")
            print(f"📦 Plataforma: {PLATFORM_CONFIGS[platform]['name']}")
            print(f"{'='*50}")

            try:
                all_results: list[dict] = []
                for niche in niches:
                    results = self.scan_platform(platform, niche, max_per_platform)
                    all_results.extend(results)

                # Registrar
                reg_count = self.register_results(all_results)
                total_registered += reg_count
                total_products += len(all_results)
                platforms_ok += 1

                print(f"  📝 {reg_count} novos links registrados")

            except Exception as e:
                print(f"  ❌ Falha: {e}")
                platforms_fail += 1

        return {
            "platforms_scanned": platforms_ok,
            "platforms_failed": platforms_fail,
            "total_products_found": total_products,
            "total_registered": total_registered,
        }


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    """CLI para o AffiliateBrowserAgent."""
    import argparse

    parser = argparse.ArgumentParser(description="Affiliate Browser Automation")
    sub = parser.add_subparsers(dest="command")

    p_login = sub.add_parser("login", help="Fazer login em uma plataforma")
    p_login.add_argument("--method", choices=["auto", "oauth", "credentials"], default="auto", help="Metodo de login")
    p_login.add_argument("platform", choices=list(PLATFORM_CONFIGS.keys()))

    p_scan = sub.add_parser("scan", help="Varrer produtos em uma plataforma")
    p_scan.add_argument("platform", choices=list(PLATFORM_CONFIGS.keys()))
    p_scan.add_argument("--niche", default="marketing digital")
    p_scan.add_argument("--max", type=int, default=10)

    p_browser_login = sub.add_parser("_login_browser", help=argparse.SUPPRESS)
    p_browser_login.add_argument("platform", choices=list(PLATFORM_CONFIGS.keys()))

    p_full = sub.add_parser("full-scan", help="Varrer todas as plataformas")
    p_full.add_argument("--niches", nargs="+", default=None)
    p_full.add_argument("--max", type=int, default=10)

    p_status = sub.add_parser("status", help="Status das sessoes")

    args = parser.parse_args()

    agent = AffiliateBrowserAgent()

    if args.command == "login":
        method = getattr(args, 'method', 'auto')
        if method == "oauth":
            agent.login_interactive(args.platform)
        elif method == "credentials":
            email = os.environ.get(f"{args.platform.upper()}_EMAIL", "")
            password = os.environ.get(f"{args.platform.upper()}_PASSWORD", "")
            if email and password:
                agent.login(args.platform, headless=True)
            else:
                print(f"❌ Credenciais nao encontradas no .env")
                print(f"   Adicione {args.platform.upper()}_EMAIL e {args.platform.upper()}_PASSWORD")
        else:  # auto
            email = os.environ.get(f"{args.platform.upper()}_EMAIL", "")
            password = os.environ.get(f"{args.platform.upper()}_PASSWORD", "")
            if email and password:
                agent.login(args.platform, headless=True)
            else:
                agent.login_interactive(args.platform)
    elif args.command == "scan":
        results = agent.scan_platform(args.platform, args.niche, args.max)
        reg = agent.register_results(results)
        print(f"\n✅ {len(results)} produtos encontrados, {reg} registrados")
    elif args.command == "full-scan":
        result = agent.run_full_scan(args.niches, args.max)
        print(f"\n{'='*50}")
        print(f"✅ Scan completo:")
        print(f"   Plataformas OK: {result['platforms_scanned']}")
        print(f"   Produtos encontrados: {result['total_products_found']}")
        print(f"   Links registrados: {result['total_registered']}")
    elif args.command == "status":
        status = agent.session_status()
        print("\n📊 Status das sessoes:")
        for platform, has_session in status.items():
            icon = "✅" if has_session else "❌"
            print(f"  {icon} {PLATFORM_CONFIGS[platform]['name']:15} {'(sessao salva)' if has_session else '(sem sessao)'}")

    agent.close()


if __name__ == "__main__":
    main()
