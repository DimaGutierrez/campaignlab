// Browser-only educational model. No API calls, credentials or real attribution.
export function initialState() {
  return {version:1, campaigns:[
    {id:'demo-linkedin',name:'Spring launch · LinkedIn',destination:'https://example.com/',source:'linkedin',medium:'paid-social',campaign:'spring-launch',spend_cents:24000,clicks:120,conversions:12,converted_clicks:12,revenue_cents:72000},
    {id:'demo-newsletter',name:'The Friday edit',destination:'https://example.com/',source:'newsletter',medium:'email',campaign:'spring-launch',spend_cents:6000,clicks:80,conversions:16,converted_clicks:16,revenue_cents:96000},
    {id:'demo-search',name:'Intent-first search',destination:'https://example.com/',source:'google',medium:'cpc',campaign:'spring-launch',spend_cents:42000,clicks:200,conversions:10,converted_clicks:10,revenue_cents:50000}
  ], clicks:[],events:[]};
}
export function metrics(c) {
  return {...c,conversion_rate:c.clicks?c.converted_clicks/c.clicks:null,roas:c.spend_cents?c.revenue_cents/c.spend_cents:null};
}
export function campaignInput(values,id) {
  const name=String(values.name||'').trim();
  if(!name || name.length>80)throw Error('Ingresá un nombre de hasta 80 caracteres.');
  let url;try{url=new URL(values.destination);}catch{throw Error('Ingresá un destino HTTPS válido.');}
  if(url.protocol!=='https:' || url.username || url.password || /[\r\n\\]/.test(values.destination))throw Error('Usá HTTPS sin credenciales en la dirección.');
  for(const field of ['source','medium','campaign'])if(!/^[a-z0-9][a-z0-9_-]{0,63}$/.test(values[field]))throw Error('Las etiquetas aceptan minúsculas, números, guiones y guiones bajos.');
  if(!Number.isSafeInteger(values.spend_cents)||values.spend_cents<0||values.spend_cents>100000000)throw Error('La inversión debe estar entre 0 y 1.000.000 USD.');
  return {id,name,destination:url.href,source:values.source,medium:values.medium,campaign:values.campaign,spend_cents:values.spend_cents,clicks:0,conversions:0,converted_clicks:0,revenue_cents:0};
}
export function utmUrl(c) {
  const url=new URL(c.destination);
  url.searchParams.delete('cl_click');
  for(const field of ['source','medium','campaign'])url.searchParams.set('utm_'+field,c[field]);
  return url.href;
}
export function recordClick(state,campaignId,id) {
  if(state.clicks.length>=1000)throw Error('Llegaste al límite de esta demo. Reiniciá los datos para seguir probando.');
  const c=state.campaigns.find(x=>x.id===campaignId);if(!c)throw Error('Seleccioná una campaña.');
  if(state.clicks.some(x=>x.id===id))throw Error('El clic ya existe.');
  state.clicks.push({id,campaignId,converted:false});c.clicks++;
  return id;
}
export function recordConversion(state,clickId,eventId,revenue) {
  if(!Number.isSafeInteger(revenue)||revenue<0||revenue>100000000)throw Error('Ingresos inválidos.');
  const existing=state.events.find(x=>x.id===eventId);
  if(existing){if(existing.clickId!==clickId||existing.revenue!==revenue)throw Error('409 · El ID ya tiene otro contenido.');return {replayed:true};}
  if(state.events.length>=1000)throw Error('Reiniciá la demo para registrar más eventos.');
  const click=state.clicks.find(x=>x.id===clickId);if(!click)throw Error('Primero simulá un clic.');
  const c=state.campaigns.find(x=>x.id===click.campaignId);
  state.events.push({id:eventId,clickId,revenue});c.conversions++;c.revenue_cents+=revenue;
  if(!click.converted){click.converted=true;c.converted_clicks++;}
  return {replayed:false};
}
export function validState(s) {
  if(s?.version!==1||!Array.isArray(s.campaigns)||s.campaigns.length>100||!Array.isArray(s.clicks)||s.clicks.length>1000||!Array.isArray(s.events)||s.events.length>1000)return false;
  try {
    for(const c of s.campaigns){campaignInput(c,c.id);if(typeof c.id!=='string'||c.id.length>100)return false;for(const k of ['clicks','conversions','converted_clicks','revenue_cents'])if(!Number.isSafeInteger(c[k])||c[k]<0)return false;if(c.converted_clicks>c.clicks)return false;}
    if(new Set(s.campaigns.map(c=>c.id)).size!==s.campaigns.length)return false;
    for(const c of s.clicks)if(typeof c.id!=='string'||typeof c.converted!=='boolean'||!s.campaigns.some(x=>x.id===c.campaignId))return false;
    for(const e of s.events)if(typeof e.id!=='string'||!Number.isSafeInteger(e.revenue)||e.revenue<0||!s.clicks.some(c=>c.id===e.clickId))return false;
    return true;
  }catch{return false;}
}
export function csv(state) {
  const fields=['name','source','medium','campaign','clicks','conversions','converted_clicks','spend_cents','revenue_cents','conversion_rate','roas'];
  const cell=value=>{let s=value==null?'':String(value);if(/^\s*[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
  return fields.join(',')+'\r\n'+state.campaigns.map(c=>fields.map(f=>cell(metrics(c)[f])).join(',')).join('\r\n');
}
