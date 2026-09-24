import {initialState,metrics,campaignInput,utmUrl,recordClick,recordConversion,validState,csv} from './model.mjs';
const $=id=>document.getElementById(id), storageKey='campaignlab-public-demo-v1';
const money=c=>new Intl.NumberFormat('es-AR',{style:'currency',currency:'USD'}).format(c/100);
let state=initialState(), lastClick=null,lastEvent=null, persistent=true;
try{const saved=localStorage.getItem(storageKey);if(saved){const parsed=JSON.parse(saved);if(validState(parsed))state=parsed;}}catch{persistent=false;}
function message(text){$('status').textContent=text;}
function save(){try{localStorage.setItem(storageKey,JSON.stringify(state));}catch{persistent=false;} $('storage-note').textContent=persistent?'Tus cambios se guardan solo en este navegador. No se envían a un servidor.':'Este navegador bloquea el guardado. Los cambios durarán hasta recargar la página.';}
function render(){
  const sum=f=>state.campaigns.reduce((n,c)=>n+c[f],0);
  $('clicks').textContent=sum('clicks').toLocaleString('es-AR');$('conversions').textContent=sum('conversions').toLocaleString('es-AR');$('revenue').textContent=money(sum('revenue_cents'));$('roas').textContent=sum('spend_cents')?(sum('revenue_cents')/sum('spend_cents')).toFixed(2)+'×':'—';
  $('rows').replaceChildren();const selected=$('sim-campaign').value;$('sim-campaign').replaceChildren();
  for(const item of state.campaigns){const c=metrics(item),tr=document.createElement('tr');for(const value of [c.name,c.source+' / '+c.medium,c.clicks,c.conversions,c.conversion_rate===null?'—':(c.conversion_rate*100).toFixed(1)+'%',money(c.revenue_cents),c.roas===null?'—':c.roas.toFixed(2)+'×']){const td=document.createElement('td');td.textContent=value;tr.append(td);}
    const td=document.createElement('td'),button=document.createElement('button');button.className='copy';button.textContent='Copiar UTM ↗';button.setAttribute('aria-label','Copiar UTM de '+c.name);button.addEventListener('click',async()=>{const url=utmUrl(c);try{await navigator.clipboard.writeText(url);message('Enlace UTM copiado. Esta demo no registra visitas reales.');}catch{message('Copiá el enlace UTM: '+url);}});td.append(button);tr.append(td);$('rows').append(tr);
    const option=document.createElement('option');option.value=c.id;option.textContent=c.name;$('sim-campaign').append(option);
  }
  if(state.campaigns.some(c=>c.id===selected))$('sim-campaign').value=selected;
  $('empty').hidden=state.campaigns.length>0;$('sim-convert').disabled=!lastClick;$('sim-retry').disabled=!lastEvent;save();
}
$('new').addEventListener('click',()=>{$('form-error').textContent='';$('modal').showModal();});$('close').addEventListener('click',()=>$('modal').close());
$('create').addEventListener('submit',e=>{e.preventDefault();try{if(state.campaigns.length>=100)throw Error('La demo permite hasta 100 campañas. Reiniciá para empezar otra vez.');const v=Object.fromEntries(new FormData(e.target));v.spend_cents=Math.round(Number(v.spend)*100);state.campaigns.unshift(campaignInput(v,crypto.randomUUID()));render();$('modal').close();e.target.reset();message('Campaña creada en tu navegador. Copiá sus UTM o probala en el simulador.');}catch(error){$('form-error').textContent=error.message;}});
$('sim-campaign').addEventListener('change',()=>{lastClick=null;lastEvent=null;render();$('sim-result').textContent='Seleccioná «Simular clic» para comenzar.';});
$('sim-click').addEventListener('click',()=>{try{lastClick=recordClick(state,$('sim-campaign').value,crypto.randomUUID());lastEvent=null;render();$('sim-result').textContent='Clic simulado. Ahora registrá una conversión para este clic.';}catch(e){$('sim-result').textContent=e.message;}});
$('sim-convert').addEventListener('click',()=>{try{const revenue=Math.round(Number($('sim-amount').value)*100);if(!$('sim-amount').value)throw Error('Ingresá el importe de prueba.');const event={id:crypto.randomUUID(),click:lastClick,revenue};recordConversion(state,event.click,event.id,event.revenue);lastEvent=event;render();$('sim-result').textContent='201 simulado · Conversión registrada. Probá reenviar el mismo evento: los ingresos no deberían cambiar.';}catch(e){$('sim-result').textContent=e.message;}});
$('sim-retry').addEventListener('click',()=>{try{if(!lastEvent)return;recordConversion(state,lastEvent.click,lastEvent.id,lastEvent.revenue);render();$('sim-result').textContent='200 simulado · Evento ya registrado. Sin conversiones ni ingresos duplicados.';}catch(e){$('sim-result').textContent=e.message;}});
$('reset').addEventListener('click',()=>{$('reset-modal').showModal();});$('reset-cancel').addEventListener('click',()=>$('reset-modal').close());$('reset-confirm').addEventListener('click',()=>{state=initialState();lastClick=null;lastEvent=null;render();$('reset-modal').close();$('sim-result').textContent='Seleccioná «Simular clic» para comenzar.';message('Datos ficticios iniciales restaurados.');});
$('export').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob(['\ufeff'+csv(state)],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='campaignlab-DEMO.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);message('CSV exportado con datos de demostración.');});
render();message('Demo lista. Explorá las campañas o simulá un evento.');
