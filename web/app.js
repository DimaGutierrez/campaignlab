let key = '';
const $ = (id) => document.getElementById(id);
const money = (cents) => new Intl.NumberFormat('es-AR', {style:'currency', currency:'USD', maximumFractionDigits:2}).format(cents / 100);
const status = (message) => { $('status').textContent = message; };
async function request(path, options = {}) {
  const response = await fetch(path, {...options, headers:{'X-Admin-Key':key, ...options.headers}});
  if (!response.ok) {
    if (response.status === 401) disconnect();
    const data = await response.json().catch(() => ({}));
    throw new Error(typeof data.detail === 'string' ? data.detail : 'Revisá los campos y volvé a intentar.');
  }
  return response;
}
function disconnect() { key=''; $('dashboard').hidden=true; $('connection').hidden=false; $('disconnect').hidden=true; $('rows').replaceChildren(); }
async function load() {
  const {campaigns} = await (await request('/api/campaigns')).json();
  let demoNote=document.getElementById('demo-note');
  if (!demoNote) { demoNote=document.createElement('p');demoNote.id='demo-note';demoNote.className='footnote';$('dashboard').prepend(demoNote); }
  demoNote.textContent=campaigns.some(c=>c.id.startsWith('demo-')) ? 'DEMO · Este workspace contiene datos ficticios. No representan resultados comerciales.' : '';
  const sum = (field) => campaigns.reduce((total,c) => total+c[field],0);
  $('clicks').textContent=sum('clicks').toLocaleString('es-AR');
  $('conversions').textContent=sum('conversions').toLocaleString('es-AR');
  $('revenue').textContent=money(sum('revenue_cents'));
  $('roas').textContent=sum('spend_cents') ? (sum('revenue_cents')/sum('spend_cents')).toFixed(2)+'×' : '—';
  $('rows').replaceChildren();
  for (const c of campaigns) {
    const tr=document.createElement('tr');
    const cells=[c.name, c.source+' / '+c.medium, c.clicks, c.conversions, c.conversion_rate === null ? '—' : (c.conversion_rate*100).toFixed(1)+'%', money(c.revenue_cents), c.roas === null ? '—' : c.roas.toFixed(2)+'×'];
    for (const value of cells) { const td=document.createElement('td');td.textContent=value;tr.append(td); }
    const td=document.createElement('td'), button=document.createElement('button');
    button.className='copy';button.textContent='Copiar ↗';button.setAttribute('aria-label','Copiar enlace de '+c.name);
    button.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(c.tracking_url);status('Enlace copiado: '+c.tracking_url);}catch{status('Copiá este enlace: '+c.tracking_url);}});
    td.append(button);tr.append(td);$('rows').append(tr);
  }
  $('empty').hidden=campaigns.length>0;$('dashboard').hidden=false;$('connection').hidden=true;$('disconnect').hidden=false;
}
$('login').addEventListener('submit',async(e)=>{e.preventDefault();key=$('key').value;$('key').value='';try{await load();status('Workspace conectado. Los valores corresponden a todo el historial.');}catch(error){status(error.message);}});
$('disconnect').addEventListener('click',()=>{disconnect();status('Sesión local desconectada.');});
$('refresh').addEventListener('click',async()=>{try{await load();status('Datos actualizados.');}catch(error){status(error.message);}});
$('new').addEventListener('click',()=>{$('form-error').textContent='';$('modal').showModal();});
$('close').addEventListener('click',()=>$('modal').close());
$('create').addEventListener('submit',async(e)=>{e.preventDefault();$('save').disabled=true;const fields=Object.fromEntries(new FormData(e.target));fields.spend_cents=Math.round(Number(fields.spend)*100);delete fields.spend;try{const data=await(await request('/api/campaigns',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(fields)})).json();$('modal').close();e.target.reset();await load();status('Campaña creada: '+data.tracking_url);}catch(error){$('form-error').textContent=error.message;}finally{$('save').disabled=false;}});
$('export').addEventListener('click',async()=>{try{const blob=await(await request('/api/export.csv')).blob();const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='campaignlab.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(error){status(error.message);}});
