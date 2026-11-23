/* YouBiff — outils, guide interactif, lexique, menu */
(function(){
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const eur=(n,d=0)=>(isFinite(n)?n:0).toLocaleString('fr-FR',{minimumFractionDigits:d,maximumFractionDigits:d})+' €';
const num=v=>{const x=parseFloat(String(v).replace(/\s/g,'').replace(',','.'));return isFinite(x)?x:0};
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pct=x=>String(x).replace('.',',');
function toast(t){let e=$('#toast');if(!e){e=document.createElement('div');e.id='toast';e.className='toast';e.setAttribute('role','status');document.body.appendChild(e)}e.textContent=t;e.classList.add('show');clearTimeout(e._t);e._t=setTimeout(()=>e.classList.remove('show'),2600)}
const store={get(k,d){try{const v=localStorage.getItem('yb_'+k);return v?JSON.parse(v):d}catch(e){return d}},set(k,v){try{v==null?localStorage.removeItem('yb_'+k):localStorage.setItem('yb_'+k,JSON.stringify(v))}catch(e){}}};

/* menu mobile */
const bg=$('.burger'),mn=$('.menu');
if(bg&&mn)bg.addEventListener('click',()=>{const o=mn.classList.toggle('open');bg.setAttribute('aria-expanded',o)});

/* boutons à choix */
function bindChoice(root,cb){$$('.choice',root).forEach(s=>$$('button',s).forEach(b=>b.addEventListener('click',()=>{$$('button',s).forEach(x=>x.setAttribute('aria-pressed',x===b));cb&&cb(s,b)})))}
const val=id=>{const b=$('#'+id+' button[aria-pressed="true"]');return b?b.dataset.v:null};

/* ===== OUTILS ===== */
const f=(id,label,v,unit='€',hint='')=>`<div class="field"><label for="${id}">${label}</label><div class="inp"><input id="${id}" inputmode="decimal" autocomplete="off" value="${v}"><span>${unit}</span></div>${hint?'<small>'+hint+'</small>':''}</div>`;
const ch=(id,label,opts,def)=>`<div class="field"><span class="lb" id="${id}-l">${label}</span><div class="choice full" id="${id}" role="group" aria-labelledby="${id}-l">${opts.map(o=>`<button type="button" data-v="${o[0]}" aria-pressed="${o[0]==def}">${o[1]}</button>`).join('')}</div></div>`;
const mot=(w,d)=>`<div class="mot"><span class="k">Mot nouveau</span><span><b>${w}</b> : ${d}</span></div>`;
function out(total,sub,lines,extra=''){$('#r-tot').textContent=total;$('#r-sub').innerHTML=sub;$('#r-lines').innerHTML=lines.map(r=>`<div><span>${r[0]}</span><span>${r[1]}</span></div>`).join('');$('#r-extra').innerHTML=extra}

const T={
budget:{eyebrow:'Il te reste à la fin du mois',form:f('b-rev','Ce qui rentre par mois','1100','€','Bourse, APL, job, aide des parents')+f('b-fix','Dépenses fixes','620','€','Loyer, forfait, transport, abonnements')+f('b-var','Courses et sorties','350')+f('b-ep','Épargne visée','80'),
 calc(){const r=num($('#b-rev').value),x=num($('#b-fix').value),v=num($('#b-var').value),e=num($('#b-ep').value),left=r-x-v-e,p=a=>r?Math.round(a/r*100):0;
 out(eur(left),left>=0?'après tes dépenses et ton épargne.':'<b style="color:#B3261E">Tu dépenses plus que ce qui rentre.</b>',[['Besoins (repère 50 %)',eur(x)+' · '+p(x)+' %'],['Envies (repère 30 %)',eur(v)+' · '+p(v)+' %'],['Épargne (repère 20 %)',eur(e)+' · '+p(e)+' %'],['Ton épargne sur 1 an',eur(e*12)]],mot('Charges fixes','les dépenses qui reviennent tous les mois au même montant.'))}},
fractionne:{eyebrow:'Coût total',form:f('p-px','Prix de l’achat','400')+ch('p-n','Nombre de fois',[[3,'3 fois'],[4,'4 fois']],4)+f('p-fee','Frais annoncés','2,5','%','Regarde les conditions : souvent entre 0 et 4 % du prix'),
 calc(){const p=num($('#p-px').value),n=+val('p-n'),fe=p*num($('#p-fee').value)/100,t=p+fe;
 out(eur(t,2),'soit '+eur(fe,2)+' de frais en plus.',[['Chaque paiement',eur(t/n,2)],['Premier paiement','aujourd’hui'],['Dernier paiement','dans '+(n-1)+' mois'],['Frais',eur(fe,2)]],mot('Crédit','depuis le 20 novembre 2026, le paiement fractionné est encadré comme un crédit à la consommation.'))}},
abonnements:{eyebrow:'Tes abonnements te coûtent',form:'<div class="field"><span class="lb">Tes abonnements</span><div class="rows" id="subs"></div><button type="button" class="add" id="addsub">+ Ajouter un abonnement</button></div>',
 init(){const def=store.get('subs',[['Musique',11.99],['Vidéo',8.99],['Forfait mobile',9.99],['Salle de sport',29.99]]);const box=$('#subs');
  const row=(n,p)=>{const d=document.createElement('div');d.className='r';d.innerHTML=`<div class="inp"><input aria-label="Nom" value="${esc(n)}"></div><div class="inp"><input aria-label="Prix par mois" inputmode="decimal" value="${pct(p)}"><span>€</span></div><button type="button" class="x" aria-label="Supprimer">×</button>`;$('.x',d).onclick=()=>{d.remove();T.abonnements.calc()};$$('input',d).forEach(i=>i.oninput=()=>T.abonnements.calc());box.appendChild(d)};
  def.forEach(s=>row(s[0],s[1]));$('#addsub').onclick=()=>{row('Nouveau',5);T.abonnements.calc()}},
 calc(){const rows=$$('#subs .r').map(r=>{const i=$$('input',r);return[i[0].value,num(i[1].value)]});store.set('subs',rows);const m=rows.reduce((a,b)=>a+b[1],0);const top=rows.slice().sort((a,b)=>b[1]-a[1])[0];
 out(eur(m*12),'par an, soit '+eur(m,2)+' par mois.',[['Sur 5 ans',eur(m*60)],['Le plus cher',top?esc(top[0]):'–'],['Couper un abonnement à 10 €/mois','+ '+eur(120)+' par an']],'<p class="small" style="margin:8px 0 0">Beaucoup de plateformes ont une offre étudiante : vérifie avant de payer plein tarif.</p>')}},
voiture:{eyebrow:'Ta voiture te coûte',form:f('v-cr','Mensualité du crédit ou de la location','0','€/mois','0 si tu l’as payée comptant')+f('v-as','Assurance','80','€/mois','Un jeune conducteur paie souvent plus cher')+f('v-km','Kilomètres par mois','600','km')+f('v-co','Consommation','6','L/100 km')+f('v-pr','Prix du litre','1,75','€')+f('v-en','Entretien, pneus, contrôle technique','600','€/an')+f('v-pk','Parking et péages','20','€/mois'),
 calc(){const km=num($('#v-km').value),g=km*num($('#v-co').value)/100*num($('#v-pr').value),en=num($('#v-en').value)/12,as=num($('#v-as').value),t=num($('#v-cr').value)+as+g+en+num($('#v-pk').value);
 out(eur(t)+' / mois','soit '+eur(t*12)+' par an.',[['Carburant',eur(g)+' / mois'],['Assurance',eur(as)+' / mois'],['Entretien',eur(en)+' / mois'],['Coût du kilomètre',eur(km?t/km:0,2)]],'<p class="small" style="margin:8px 0 0">N’oublie pas que la voiture perd un peu de valeur chaque année.</p>')}},
appart:{eyebrow:'À payer avant d’avoir les clés',form:f('a-l','Loyer hors charges','520','€/mois')+f('a-c','Charges','60','€/mois')+ch('a-t','Type de logement',[['vide','Vide'],['meuble','Meublé']],'meuble')+ch('a-ag','Passé par une agence ?',[['oui','Oui'],['non','Non']],'oui')+f('a-m2','Surface','22','m²')+ch('a-z','Ta ville',[['12','Paris et proche banlieue'],['10','Grande ville'],['8','Ailleurs']],'10')+f('a-as','Assurance habitation, 1re année','90')+f('a-dm','Déménagement','150','€','Utilitaire, cartons…'),
 calc(){const l=num($('#a-l').value),c=num($('#a-c').value),dep=l*(val('a-t')==='meuble'?2:1),m2=num($('#a-m2').value),ag=val('a-ag')==='oui'?m2*(+val('a-z')+3):0,as=num($('#a-as').value),dm=num($('#a-dm').value),t=dep+ag+l+c+as+dm;
 out(eur(t),'à prévoir pour entrer dans ton logement.',[['Dépôt de garantie',eur(dep)],['Frais d’agence (maximum légal)',eur(ag)],['Premier loyer charges comprises',eur(l+c)],['Assurance habitation',eur(as)],['Déménagement',eur(dm)]],mot('Dépôt de garantie','rendu à ta sortie si le logement est en bon état. 1 mois de loyer hors charges pour un vide, 2 mois maximum pour un meublé.')+'<p class="small" style="margin:8px 0 0">Pense aux APL : demande-les sur le site de la CAF dès la signature du bail.</p>')}},
coloc:{eyebrow:'À partager chaque mois',form:f('c-l','Loyer total charges comprises','1200','€/mois')+f('c-f','Factures partagées','90','€/mois','Électricité, internet…')+ch('c-m','Partage du loyer',[['egal','Parts égales'],['surface','Selon la chambre']],'surface')+'<div class="field"><span class="lb">Les colocs et la surface de leur chambre</span><div class="rows" id="cols"></div><button type="button" class="add" id="addcol">+ Ajouter un coloc</button></div>',
 init(){const box=$('#cols');const row=(n,s)=>{const d=document.createElement('div');d.className='r';d.innerHTML=`<div class="inp"><input aria-label="Prénom" value="${esc(n)}"></div><div class="inp"><input aria-label="Surface" inputmode="decimal" value="${s}"><span>m²</span></div><button type="button" class="x" aria-label="Supprimer">×</button>`;$('.x',d).onclick=()=>{if($$('#cols .r').length>2){d.remove();T.coloc.calc()}else toast('Il faut au moins 2 colocs.')};$$('input',d).forEach(i=>i.oninput=()=>T.coloc.calc());box.appendChild(d)};
  [['Sam',14],['Inès',11],['Yanis',9]].forEach(x=>row(x[0],x[1]));$('#addcol').onclick=()=>{row('Coloc '+($$('#cols .r').length+1),10);T.coloc.calc()}},
 calc(){const l=num($('#c-l').value),fa=num($('#c-f').value),pp=$$('#cols .r').map(r=>{const i=$$('input',r);return[i[0].value,num(i[1].value)]}),n=pp.length||1,S=pp.reduce((a,b)=>a+b[1],0)||1,eq=val('c-m')==='egal',sh=p=>eq?l/n:(l/2)/n+(l/2)*p[1]/S;
 out(eur(l+fa),'loyer et factures. Ce que paie chacun :',pp.map(p=>[esc(p[0]),eur(sh(p)+fa/n)]),'<p class="small" style="margin:8px 0 0">'+(eq?'Loyer et factures divisés à parts égales.':'La moitié du loyer paie les pièces communes (parts égales), l’autre moitié suit la taille des chambres. Factures à parts égales.')+'</p>')}},
salaire:{eyebrow:'Tu touches environ',form:f('s-b','Salaire brut','1800','€/mois')+ch('s-st','Ton contrat',[['nc','Salarié'],['c','Cadre'],['stage','Stage'],['alt','Alternance']],'nc'),
 calc(){const b=num($('#s-b').value),st=val('s-st');let r,lab;
 if(st==='nc'){r=.22;lab='environ 22 % de cotisations'}else if(st==='c'){r=.25;lab='environ 25 % de cotisations'}else if(st==='stage'){r=b<=700?0:.22*(b-700)/b;lab='gratification exonérée jusqu’au minimum légal (environ 700 €/mois)'}else{r=b<=900?0:.22*(b-900)/b;lab='peu ou pas de cotisations sur le bas du salaire'}
 const n=b*(1-r);out(eur(n)+' / mois','net avant impôt, soit '+eur(n*12)+' par an.',[['Brut',eur(b)],['Cotisations',eur(b-n)],['Pourquoi',lab]],mot('Net avant impôt','ce que tu touches avant le prélèvement à la source. Étudiant de moins de 26 ans : souvent pas d’impôt sur tes salaires jusqu’à un plafond.'))}},
interets:{eyebrow:'Tu aurais au bout',form:f('i-c','Ce que tu as au départ','500')+f('i-m','Ce que tu ajoutes chaque mois','50')+f('i-t','Taux par an','3','%','Livret A : 1,7 % en 2026. Bourse : non garanti, peut être négatif.')+f('i-d','Durée','10','ans'),
 calc(){const c=num($('#i-c').value),m=num($('#i-m').value),t=num($('#i-t').value)/100,d=Math.min(60,Math.max(1,Math.round(num($('#i-d').value))));let v=c,pts=[];
 for(let y=1;y<=d;y++){for(let k=0;k<12;k++)v=v*(1+t/12)+m;pts.push([c+m*12*y,v])}
 const put=c+m*12*d,mx=Math.max(...pts.map(p=>p[1]),1);
 const bars='<div class="chart" aria-hidden="true">'+pts.map(p=>`<div style="height:${Math.max(1,p[1]/mx*100)}%"><i style="height:${p[1]>0?Math.min(100,p[0]/p[1]*100):100}%"></i></div>`).join('')+'</div><div class="legend"><span><i style="background:#0B7F58"></i>Intérêts gagnés</span><span><i style="background:#9CC9B5"></i>Ce que tu as mis</span></div>';
 out(eur(v),'en '+d+' an'+(d>1?'s':'')+', à '+pct(num($('#i-t').value))+' % par an.',[['Ce que tu as mis',eur(put)],['Intérêts gagnés',eur(v-put)]],bars+mot('Intérêts composés','tes intérêts rapportent eux aussi des intérêts. Plus tu commences tôt, plus l’effet est fort.'))}},
livrets:{eyebrow:'Le mieux pour toi',form:f('l-m','Somme à placer','3000')+f('l-d','Durée','12','mois')+ch('l-lep','Tes revenus permettent le LEP ?',[['oui','Oui'],['non','Non ou je ne sais pas']],'non')+ch('l-age','Tu as entre 12 et 25 ans ?',[['oui','Oui'],['non','Non']],'oui'),
 calc(){const m=num($('#l-m').value),d=num($('#l-d').value);const L=[['LEP',2.5,10000,val('l-lep')==='oui'],['Livret A',1.7,22950,true],['LDDS',1.7,12000,true],['Livret jeune (minimum)',1.7,1600,val('l-age')==='oui']];
 const rows=L.map(x=>{const put=Math.min(m,x[2]);return{n:x[0],t:x[1],cap:x[2],ok:x[3],g:put*x[1]/100*d/12,capped:put<m}});const best=rows.filter(r=>r.ok).sort((a,b)=>b.g-a.g)[0];
 out(best.n,'environ '+eur(best.g,2)+' d’intérêts en '+d+' mois'+(best.capped?' (plafond de '+eur(best.cap)+' atteint)':'')+'.',rows.map(r=>[r.n+' · '+pct(r.t)+' %',r.ok?eur(r.g,2)+(r.capped?' (plafonné)':''):'non accessible']),mot('Plafond','la somme maximum que tu peux verser sur un livret.'))}},
micro:{eyebrow:'Il te reste par mois',form:f('m-ca','Ce que tu encaisses par mois','1500','€','Ton chiffre d’affaires')+ch('m-act','Ton activité',[['v','Vente'],['bic','Service artisanal ou commercial'],['bnc','Service libéral']],'bnc')+ch('m-vl','Versement libératoire de l’impôt ?',[['non','Non'],['oui','Oui']],'non')+f('m-fr','Tes frais','100','€/mois','Logiciels, matériel, déplacements'),
 calc(){const ca=num($('#m-ca').value),R={v:[12.3,.1,1],bic:[21.2,.3,1.7],bnc:[25.6,.2,2.2]}[val('m-act')],co=ca*R[0]/100,cf=ca*R[1]/100,vl=val('m-vl')==='oui'?ca*R[2]/100:0,fr=num($('#m-fr').value),left=ca-co-cf-vl-fr;
 out(eur(left),'après cotisations'+(vl?', impôt':'')+' et frais.',[['Cotisations sociales ('+pct(R[0])+' %)',eur(co)],['Formation professionnelle',eur(cf)],['Impôt (versement libératoire)',vl?eur(vl):'non choisi'],['Tes frais',eur(fr)],['Sur 1 an',eur(left*12)]],mot('Chiffre d’affaires','tout l’argent encaissé, avant de payer quoi que ce soit. Les cotisations se calculent dessus.'))}}
};
const tool=$('[data-tool]');
if(tool){const id=tool.dataset.tool,t=T[id];
 $('#tf').innerHTML=t.form;$('#r-eye').textContent=t.eyebrow;
 if(t.init)t.init();
 $$('#tf input').forEach(i=>i.addEventListener('input',()=>t.calc()));bindChoice($('#tf'),()=>t.calc());t.calc();
 $('#copy').addEventListener('click',async()=>{const txt=document.title.split(' –')[0]+' : '+$('#r-tot').textContent+' '+$('#r-sub').textContent+'\n'+$$('#r-lines div').map(d=>d.children[0].textContent+' : '+d.children[1].textContent).join('\n')+'\nCalculé sur youbiff.fr';
  try{await navigator.clipboard.writeText(txt);toast('Résultat copié.')}catch(e){toast('La copie n’est pas possible ici.')}});
 $('#reset').addEventListener('click',()=>{store.set('subs',null);location.reload()});
}

/* ===== GUIDE 1 000 € ===== */
const g=$('#guide1000');
if(g){const ans=[null,null,null];
 $$('.yn .choice',g).forEach((s,i)=>$$('button',s).forEach(b=>b.addEventListener('click',()=>{$$('button',s).forEach(x=>x.setAttribute('aria-pressed',x===b));ans[i]=+b.dataset.v;
  const n=ans.filter(a=>a!==null).length,y=ans.filter(a=>a===1).length;let t;
  if(n<3)t='Encore '+(3-n)+' question'+(3-n>1?'s':'')+' pour voir où tu en es.';
  else if(y===3)t='3 oui sur 3 : tu as les bases pour passer à l’étape suivante.';
  else if(ans[0]===0)t='D’abord ton épargne de secours : mets 3 mois de dépenses de côté sur un livret avant d’investir.';
  else if(ans[1]===0)t='D’abord rembourser tes crédits : un crédit coûte souvent plus que ce que la Bourse peut rapporter.';
  else t=y+' oui sur 3 : tu as les bases. Sur moins de 5 ans, garde surtout en tête le risque de l’étape 4.';
  $('#verdict').textContent=t})));
 let dur=8;
 const draw=()=>{const m=num($('#g-mt').value),liv=m*Math.pow(1.017,dur),act=m*Math.pow(1.06,dur),lo={2:.75,5:.8,8:.8}[dur],hi={2:1.3,5:1.6,8:2.15}[dur];
  const W=[['Tout sur un livret',liv,liv,liv,0],['Moitié livret, moitié actions monde',(liv+act)/2,(liv+m*lo)/2,(liv+m*hi)/2,1],['Tout en actions monde',act,m*lo,m*hi,0]];
  const min=m*.6,max=m*Math.max(2.3,hi+.1),pos=v=>Math.max(0,Math.min(100,(v-min)/(max-min)*100));
  const r=v=>'≈ '+eur(Math.round(v/10)*10);
  $('#ways').innerHTML=W.map((w,i)=>`<div class="way${w[4]?' on':''}"><div class="top"><b>${w[0]}</b><b>${i?r(w[1]):eur(w[1])}</b></div><span class="bar"><i style="left:${pos(w[2])}%;right:${100-pos(w[3])-(i?0:1.5)}%"></i></span><div class="rg"><span>Mauvaise période : ${i?r(w[2]):eur(w[2])}</span><span>Bonne période : ${i?r(w[3]):eur(w[3])}</span></div></div>`).join('');
  $('#g-txt').textContent=eur(m)+' en '+dur+' ans';};
 $('#g-mt').addEventListener('input',draw);
 bindChoice($('#g-dur').parentNode,(s,b)=>{dur=+b.dataset.v;draw()});
 draw();
 const links=$$('.toc a');if('IntersectionObserver' in window&&links.length){const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)links.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+e.target.id))}),{rootMargin:'-30% 0px -60% 0px'});$$('.art h2[id]').forEach(h=>io.observe(h))}
}

/* ===== LEXIQUE ===== */
const lq=$('#lexq');
if(lq){const norm=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');const words=$$('.word');
 lq.addEventListener('input',()=>{const q=norm(lq.value.trim());let any=false;words.forEach(w=>{const ok=norm(w.textContent).includes(q);w.hidden=!ok;any=any||ok});$$('.letter').forEach(l=>{let n=l.nextElementSibling,vis=false;while(n&&n.classList.contains('word')){if(!n.hidden)vis=true;n=n.nextElementSibling}l.hidden=!vis});$('#lexnone').hidden=any})}

/* ===== FILTRES OUTILS ===== */
const chips=$$('.chip[data-cat]');
chips.forEach(c=>c.addEventListener('click',()=>{chips.forEach(x=>x.setAttribute('aria-pressed',x===c));const k=c.dataset.cat;$$('[data-cats]').forEach(t=>t.hidden=!(k==='tous'||t.dataset.cats===k))}));
})();
