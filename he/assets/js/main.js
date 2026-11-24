(function(){
var b=document.body,r=document.documentElement;
function get(k){try{return localStorage.getItem(k)}catch(e){return null}}
function set(k,v){try{localStorage.setItem(k,v)}catch(e){}}
if(get('hc')==='1')b.classList.add('hc');
var fs=parseInt(get('fs')||'17',10);r.style.setProperty('--fs',fs+'px');
document.addEventListener('click',function(e){
 var t=e.target.closest('[data-act]');if(!t)return;var a=t.dataset.act;
 if(a==='hc'){b.classList.toggle('hc');set('hc',b.classList.contains('hc')?'1':'0')}
 if(a==='fp'||a==='fm'){fs=Math.max(14,Math.min(24,fs+(a==='fp'?1:-1)));r.style.setProperty('--fs',fs+'px');set('fs',fs)}
 if(a==='menu'){var n=document.getElementById('nav');var o=n.classList.toggle('open');t.setAttribute('aria-expanded',o)}
});
var f=document.getElementById('elegivel');
if(f)f.addEventListener('submit',function(e){e.preventDefault();var o=document.getElementById('res');o.classList.add('on');o.textContent='Situação simulada: título regular, apto(a) a votar nas próximas eleições do Roleplay.'});
var of=document.getElementById('ouv');
if(of)of.addEventListener('submit',function(e){e.preventDefault();var p='RP-'+new Date().getFullYear()+'-'+Math.floor(Math.random()*900000+100000);var o=document.getElementById('res');o.classList.add('on');o.textContent='Manifestação registrada (simulação). Protocolo: '+p});
var sr=document.getElementById('sres');
if(sr&&window.SITE_INDEX){
 var q=(new URLSearchParams(location.search).get('q')||'').trim();
 var inp=document.getElementById('bq');if(inp)inp.value=q;
 var n=function(s){return s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()};
 var qq=n(q).split(/\s+/).filter(Boolean);
 var hits=window.SITE_INDEX.filter(function(p){var h=n(p.t+' '+p.d);return qq.every(function(w){return h.indexOf(w)>-1})});
 var c=document.getElementById('scount');
 if(!q){c.textContent='Digite algo para pesquisar nas páginas do portal.'}
 else{c.textContent=hits.length?hits.length+' resultado(s) para "'+q+'".':'Nenhum resultado para "'+q+'". Tente outra palavra ou veja o mapa do site.'}
 if(q)hits.forEach(function(p){var li=document.createElement('li');var a=document.createElement('a');a.href=p.u;a.textContent=p.t;var d=document.createElement('div');d.textContent=p.d;li.appendChild(a);li.appendChild(d);sr.appendChild(li)});
}
})();
