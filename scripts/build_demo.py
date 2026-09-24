"""Build static demo presentation from the existing app shell; no secrets or backend files."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
out = root / "demo"
html = (root / "web/index.html").read_text(encoding="utf-8")
html = html.replace('<script src="/app.js" defer></script>', '<script type="module" src="/app.js"></script>')
html = html.replace('CampaignLab · Marketing, con evidencia', 'CampaignLab · Demo interactiva')
html = html.replace('<button id="disconnect" class="quiet" hidden>Desconectar</button>', '<a class="repo-link" href="https://github.com/DimaGutierrez/campaignlab" target="_blank" rel="noopener noreferrer">Ver código ↗</a>')
html = html.replace('USD · Histórico completo', 'DEMO · Datos ficticios · USD')
html = html.replace('WORKSPACE / PERFORMANCE', 'DEMO INTERACTIVA / SIN REGISTRO')
html = re.sub(r'<section id="connection".*?</section>', '''<section class="demo-banner"><strong>Explorá sin registrarte.</strong><p>Esta demo funciona en tu navegador con datos ficticios. Los clics y conversiones se simulan; no hay seguimiento real ni conexión al backend.</p><p id="storage-note"></p></section>''', html, flags=re.S)
html = html.replace('<div id="dashboard" hidden>', '<div id="dashboard">')
html = html.replace('<button id="refresh" class="quiet">Actualizar</button>', '<button id="reset" class="quiet">Reiniciar demo</button>')
html = html.replace('Reportados por tu backend', 'Importes ficticios de la demo').replace('Solicitudes al enlace de campaña', 'Clics ficticios y simulados')
html = html.replace('Atribución de 30 días. Sin deduplicación de personas ni promesas de causalidad.', 'Simulación educativa. El backend real del repositorio aplica una ventana de 30 días.')
html = html.replace('Un identificador de clic conecta el enlace con un evento de tu backend.', 'Probá un clic, una conversión y un reintento en el simulador. Observá cómo cambian los totales.')
html = html.replace('Tus UTM viajan hasta el destino.', 'Copiá un enlace UTM válido. Esta demo no registra las visitas a ese enlace.')
sim='''<section class="panel simulator"><div class="section-head"><div><p class="eyebrow">UN EVENTO, UNA CONVERSIÓN</p><h2>Probá el flujo, sin un servidor</h2></div><span class="badge">Simulación local</span></div><div class="sim-fields"><label>Campaña<select id="sim-campaign"></select></label><label>Ingresos de prueba (USD)<input id="sim-amount" type="number" min="0" max="1000000" step="0.01" value="49"></label></div><div class="sim-actions"><button id="sim-click">1. Simular clic</button><button id="sim-convert" disabled>2. Registrar conversión</button><button id="sim-retry" class="quiet" disabled>3. Reenviar mismo evento</button></div><p id="sim-result" role="status" aria-live="polite">Seleccioná «Simular clic» para comenzar.</p><p class="footnote">Podés registrar más de una conversión por clic. Reenviar el mismo evento no suma ingresos. Los códigos 201/200 son ilustrativos; no se envían solicitudes HTTP.</p></section>'''
html = html.replace('<section id="method"', sim+'<section id="method"')
html = html.replace('</body>', '<dialog id="reset-modal"><h2>¿Reiniciar la demo?</h2><p>Se eliminarán únicamente tus campañas y eventos de prueba guardados en este navegador. Volverán los datos ficticios iniciales.</p><div class="actions"><button id="reset-cancel" class="quiet">Cancelar</button><button id="reset-confirm">Sí, reiniciar</button></div></dialog></body>')
(out / "index.html").write_text(html, encoding="utf-8")
css = (root / "web/style.css").read_text(encoding="utf-8")
css += '''\n.repo-link{color:#315746;letter-spacing:0;font-size:12px;white-space:nowrap}.demo-banner{background:#e6efd9;border:1px solid #cbdcbc;border-radius:10px;padding:20px 24px;font-size:14px}.demo-banner p{font-size:12px;line-height:1.7;margin:8px 0 0}.simulator{margin-top:28px}.sim-fields{display:grid;grid-template-columns:2fr 1fr;gap:20px;padding:0 24px}select{width:100%;padding:12px;border:1px solid #becabd;border-radius:6px;background:#fbfcfa;color:#173d30;margin:8px 0 16px;font:inherit}.sim-actions{display:flex;gap:10px;flex-wrap:wrap;padding:0 24px}.simulator #sim-result{padding:8px 24px;font-size:13px;line-height:1.7;color:#315746}.simulator .footnote{padding:0 24px 12px}#storage-note{color:#506849}#reset-modal p{line-height:1.8;font-size:14px}@media(max-width:650px){.sim-fields{grid-template-columns:1fr;gap:0}.sim-actions{flex-direction:column}header{flex-wrap:wrap;padding:12px 0}header .badge{margin-left:0}.demo-banner{padding:18px}.sim-actions button{font-size:12px}}\n'''
(out / "style.css").write_text(css, encoding="utf-8")
(out / "404.html").write_text('<!doctype html><html lang="es"><meta charset="utf-8"><title>CampaignLab · Página no encontrada</title><h1>Página no encontrada</h1><a href="/">Volver a la demo de CampaignLab</a></html>', encoding="utf-8")
print('Static demo built. No backend, credentials or external assets included.')
