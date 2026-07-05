/*
 * Hotmart Cookie Extractor — Bookmarklet
 * ============================================
 * 
 * COMO USAR NO CELULAR (Android Chrome):
 * 
 * 1. Abra o Chrome e acesse: app.hotmart.com/products/affiliations
 * 2. Faça login normalmente (com Google)
 * 3. Na barra de URL, digite: javascript:
 * 4. Cole o código abaixo (tudo em uma linha)
 * 5. Pressione Enter
 * 6. O script vai criar um arquivo cookies.json para download
 * 
 * SE O CÓDIGO NÃO FUNCIONAR (Android Chrome bloqueia javascript:):
 * - Método alternativo 1: Use um site como https://bookmarklets.org/maker/
 * - Método alternativo 2: Use a extensão "Cookie-Editor" da Chrome Web Store
 * - Método alternativo 3: Abra o DevTools (se disponível) e cole no console
 * 
 * APÓS EXTRAIR OS COOKIES:
 * 1. Salve o arquivo como hotmart_session.json
 * 2. Transfira para o computador/servidor
 * 3. Coloque em: .state/browser_sessions/hotmart_session.json
 * 4. Execute: python scripts/affiliate_browser.py scan hotmart --all
 */

(function() {
    const cookies = document.cookie.split(';').map(c => {
        const [name, ...rest] = c.trim().split('=');
        const value = rest.join('=');
        return {
            name: name.trim(),
            value: decodeURIComponent(value.trim()),
            domain: window.location.hostname,
            path: '/',
            secure: true,
            httpOnly: false,
            sameSite: 'Lax'
        };
    });

    // Also try to get all cookies from the browser
    if (window.chrome && window.chrome.cookies) {
        // Extension-based access (not available in normal pages)
    }

    const output = JSON.stringify(cookies, null, 2);
    const blob = new Blob([output], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'hotmart_session.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    alert(`✅ ${cookies.length} cookies extraídos!\n\nArquivo: hotmart_session.json\n\nEnvie este arquivo para a pasta:\n.state/browser_sessions/hotmart_session.json`);
})();
