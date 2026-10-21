/* Nord-Norge dashboard — applikasjons-JS (ekstrakt fra index.html) */


/* === methodBadge() — kobler hver figur til en kilde og forklarer metoden ====
   Brukes som <inline-element> i kort-overskrifter eller hint-bokser:
   methodBadge('SSB_MONITOR') → <span class="methodbadge">…</span>
   Hover/klikk gir tooltip med metric_type, ekskluderinger, geografi. */
function methodBadge(sourceId){
  const s=SOURCES[sourceId];
  if(!s) return '';
  const metric = ({
    kohort_retensjon:'Kohortbevaring',
    stock_snapshot:'Bestandstall',
    akkumulert_nettoflytting:'Akkumulert nettoflytting',
    raadata:'Rådata'
  })[s.metric_type]||s.metric_type;
  const flags=[];
  flags.push(s.excludes_emigration?'ekskl. utvandring':'inkl. utvandring');
  if(s.ukraine_included===false) flags.push('ekskl. Ukraina');
  flags.push('per '+s.geo_level);
  const tip = (s.short?s.short+' ':'') + (s.caveat||'');
  return '<span class="methodbadge" data-src="'+sourceId+'" tabindex="0" title="'+tip.replace(/"/g,'&quot;')+'">'+
    '<span class="mb-tag">'+metric+'</span>'+
    '<span class="mb-pub">'+s.publisher+'</span>'+
    '<span class="mb-flags">'+flags.join(' · ')+'</span>'+
  '</span>';
}
const K = Object.entries(DATA.kommuner).map(([nr,o])=>{
  const a = DATA.innv[nr]||{bc:0,ves:0,ive:0,innv:0,norskf:0,land:[]};
  const sy = (DATA.syss&&DATA.syss[nr])||null;
  const pop = o.alder.reduce((s,x)=>s+x,0);
  const kreg = (typeof KREGION!=='undefined') ? (KREGION[nr]||null) : null;
  return {nr:+nr,navn:o.navn,fylke:o.fylke,alder:o.alder,pop,
    bc:a.bc,ves:a.ves,ive:a.ive,innv:a.innv,norskf:a.norskf,land:a.land,syss:sy,
    hist:o.hist||null, region:kreg,
    andel: pop? a.bc/pop*100 : 0};
});
const SM = DATA.syss_meta||{grupper:{}};
const SGROUPS=[['tot','Hele befolkningen'],['abc','Befolkningen ekskl. innvandrere'],
  ['zzz','Alle innvandrere'],['ddd','Innvandrere · vestlig'],['eee','Innvandrere · ikke-vestlig']];
const AGES = DATA.age_labels; // 0..105+
let state={fylke:'Alle',q:'',sort:'folketall',sel:K.slice().sort((a,b)=>b.pop-a.pop)[0].nr,
  ageMode:'5', topN:12, csearch:'', compare:[], sysSex:'rate', natSex:'begge', natMetric:'rate', natHidden:{}, projMode:'tot', ukr:0, ukrbase:'mvp', sens:0, mw:'kons', showMVP:false, robekSort:'risk', robekFylke:'Alle', kView:'history'};
// URL-param-overstyringer for flersides oppsett:
//   kommune.html?k=1804&view=people  ·  fylke.html?f=Nordland  ·  sammenlign.html?k=1804,5401,1860
(function applyUrlParams(){
  try{
    const p = new URLSearchParams(window.location.search);
    const kRaw = p.get('k') || '';
    if(kRaw.includes(',')){
      const ks = kRaw.split(',').map(x=>parseInt(x,10)).filter(n => K.some(y => y.nr === n)).slice(0,4);
      if(ks.length >= 2){ state.compare = ks; state.sel = ks[0]; }
    } else {
      const k = parseInt(kRaw, 10);
      if(k && K.some(x => x.nr === k)) state.sel = k;
    }
    const f = p.get('f');
    if(f && ['Alle','Nordland','Troms','Finnmark'].includes(f)) state.fylke = f;
    const view = p.get('view');
    if(view && ['history','people','burden'].includes(view)) state.kView = view;
  }catch(_){}
})();
const FYNR={Alle:-1,Nordland:-18,Troms:-55,Finnmark:-56};
const AGG={};
(function buildAggregates(){
  if(!DATA.proj||!DATA.proj.kommuner) return;
  const GR=['tot','abc','zzz','ddd','eee'];
  const PA=['main','low','high','a019','a2064','a65','a80','tfattr','tfattr_a019','tfattr_a2064','tfattr_a65','ukra50','ukra75','ukra100'];
  const MWF=['pop','nat','mig','a019','a2064','a65','a80','a15','a615','a67','u50','u75','u100','s75','s125'], WINS=['kons','sentral','opt'];
  function build(list,nr,navn,fy){
    const n106=new Array(106).fill(0);
    let bc=0,ves=0,ive=0,innv=0,norskf=0,pop=0; const lm={}; const histAgg={};
    list.forEach(k=>{ pop+=k.pop; bc+=k.bc||0; ves+=k.ves||0; ive+=k.ive||0; innv+=k.innv||0; norskf+=k.norskf||0;
      for(let i=0;i<106;i++) n106[i]+=(k.alder[i]||0);
      (k.land||[]).forEach(p=>{lm[p[0]]=(lm[p[0]]||0)+p[1];});
      if(k.hist){ Object.keys(k.hist).forEach(y=>{histAgg[y]=(histAgg[y]||0)+k.hist[y];}); } });
    const land=Object.keys(lm).map(nm=>[nm,lm[nm]]).sort((a,b)=>b[1]-a[1]);
    function aggSyss(){
      const out={rate:{},rateM:{},rateK:{},cnt:{}};
      GR.forEach(g=>{ let sumC=0,hasC=false,sumBase=0,nM=0,dM=0,nK=0,dK=0;
        list.forEach(k=>{ const s=k.syss; if(!s) return;
          const r=s.rate?s.rate[g]:null, c=s.cnt?s.cnt[g]:null;
          if(c!=null){sumC+=c;hasC=true;}
          if(r!=null&&c!=null&&r>0){ const base=c/(r/100); sumBase+=base;
            if(s.rateM&&s.rateM[g]!=null){nM+=s.rateM[g]*base;dM+=base;}
            if(s.rateK&&s.rateK[g]!=null){nK+=s.rateK[g]*base;dK+=base;} } });
        out.cnt[g]=hasC?Math.round(sumC):null;
        out.rate[g]=sumBase>0?+(100*sumC/sumBase).toFixed(1).replace('.',','):null;
        out.rateM[g]=dM>0?+(nM/dM).toFixed(1).replace('.',','):null;
        out.rateK[g]=dK>0?+(nK/dK).toFixed(1).replace('.',','):null; });
      return out;
    }
    const anyP=list.find(k=>DATA.proj.kommuner[k.nr]);
    if(anyP){ const ref=DATA.proj.kommuner[anyP.nr], yl=(ref.main||[]).length, ap={};
      PA.forEach(f=>{ap[f]=new Array(yl).fill(0);}); let ukr=0;
      list.forEach(k=>{ const o=DATA.proj.kommuner[k.nr]; if(!o) return;
        PA.forEach(f=>{ const arr=o[f]; if(arr) for(let i=0;i<yl;i++) ap[f][i]+=(arr[i]||0); });
        ukr+=(o.ukr||0); });
      ap.mw={}; WINS.forEach(w=>{ ap.mw[w]={}; MWF.forEach(f=>ap.mw[w][f]=new Array(yl).fill(0)); });
      list.forEach(k=>{ const o=DATA.proj.kommuner[k.nr]; if(!o||!o.mw) return;
        WINS.forEach(w=>{ const ow=o.mw[w]; if(!ow) return;
          MWF.forEach(f=>{ const arr=ow[f]; if(arr) for(let i=0;i<yl;i++) ap.mw[w][f][i]+=(arr[i]||0); }); }); });
      ap.ukr=Math.round(ukr); ap.tfmvp_flag=false;
      DATA.proj.kommuner[String(nr)]=ap; }
    return {nr:nr,navn:navn,fylke:fy,isAgg:true,naggk:list.length,
      alder:n106,pop:pop,bc:bc,ves:ves,ive:ive,innv:innv,norskf:norskf,
      land:land,syss:aggSyss(),andel:pop?bc/pop*100:0,
      hist:Object.keys(histAgg).length?histAgg:null};
  }
  AGG[-18]=build(K.filter(k=>k.fylke==='Nordland'),-18,'Nordland \u2014 hele fylket','Nordland');
  AGG[-55]=build(K.filter(k=>k.fylke==='Troms'),-55,'Troms \u2014 hele fylket','Troms');
  AGG[-56]=build(K.filter(k=>k.fylke==='Finnmark'),-56,'Finnmark \u2014 hele fylket','Finnmark');
  AGG[-1]=build(K.slice(),-1,'Nord-Norge \u2014 hele landsdelen','Alle');
  // Regioner (S\u00d8A 13-regioninndeling). Negative nr -101 .. -113 for aggregat-oppslag.
  if(typeof REGIONS !== 'undefined'){
    REGIONS.forEach((r,i)=>{
      const list = K.filter(k=>k.region===r.id);
      if(list.length) AGG[-(101+i)] = build(list, -(101+i), r.navn, r.fylke);
    });
  }
})();
function resolveSel(){ return K.find(x=>x.nr===state.sel) || AGG[state.sel] || null; }
// Returnerer aggregat for valgt fylke (eller landsdel hvis state.fylke = 'Alle').
// Brukes av render-funksjoner som ellers hardkodet AGG[-1].
function currentAgg(){
  return (state.fylke && state.fylke !== 'Alle' && AGG[FYNR[state.fylke]]) || AGG[-1];
}
// Returnerer kommune-array filtrert til valgt fylke (eller alle hvis 'Alle')
function currentK(){
  return state.fylke === 'Alle' ? K : K.filter(x => x.fylke === state.fylke);
}
function MW(o){ return (o&&o.mw)?o.mw[state.mw]:null; }
function LMW(){ const L=DATA.proj&&DATA.proj.landsdel; return (L&&L.mw)?L.mw[state.mw]:{}; }
// Ferskeste kvartalsvise folketall (SSB 01222, BEFK_DATA). Modellene er
// forankret i 1.1-tallene; dette er kun visning av siste maaling.
function aprilPop(k){
  if(typeof BEFK_DATA==='undefined'||!BEFK_DATA||!k) return null;
  if(k.isAgg) return k.fylke==='Alle'?BEFK_DATA.landsdel:(BEFK_DATA.fylker[k.fylke]||null);
  return BEFK_DATA.kommuner[k.nr]||null;
}
function popKpi(k, ekstraSub){
  const apr=aprilPop(k);
  if(!apr) return '<div class="kpi"><div class="v">'+fmt(k.pop)+'</div><div class="l">Folketall</div><div class="s">'+(ekstraSub||'')+'per 1.1.2026</div></div>';
  const d=apr-k.pop;
  return '<div class="kpi"><div class="v">'+fmt(apr)+'</div><div class="l">Folketall</div><div class="s">'+(ekstraSub||'')+'per '+BEFK_DATA.dato_norsk+' ('+(d>=0?'+':'−')+fmt(Math.abs(d))+' siden 1.1)</div></div>';
}

const elList=document.getElementById('klist'), elDet=document.getElementById('detail');

function filtered(){
  const q=(state.q||'').toLowerCase().trim();
  const KW={'robek':k=>kommuneStatus(k).robek!=='ok',
            'vekst':k=>kommuneStatus(k).growth==='up',
            'krymper':k=>kommuneStatus(k).growth==='down',
            'krymp':k=>kommuneStatus(k).growth==='down',
            'nedgang':k=>kommuneStatus(k).growth==='down',
            'stabil':k=>kommuneStatus(k).growth==='flat',
            'aldring':k=>kommuneStatus(k).aging==='old',
            'aldrende':k=>kommuneStatus(k).aging==='old',
            'ung':k=>kommuneStatus(k).aging==='young'};
  const kwTest = KW[q];
  let r=K.filter(k=>(state.fylke==='Alle'||k.fylke===state.fylke)&&
    (kwTest? kwTest(k) : k.navn.toLowerCase().includes(q)));
  const s=state.sort;
  r.sort((a,b)=> s==='navn'? a.navn.localeCompare(b.navn,'nb')
              : s==='andel'? b.andel-a.andel
              : s==='syss'? ((b.syss&&b.syss.rate.zzz)||-1)-((a.syss&&a.syss.rate.zzz)||-1)
              : b.pop-a.pop);
  return r;
}
function renderList(){if(!elList) return;
  const r=filtered();
  var _cnt=document.getElementById('cnt'); if(_cnt) _cnt.textContent=r.length+' kommuner';
  elList.innerHTML=r.map(k=>{
    const s=kommuneStatus(k);
    const grTitle=s.growth==='up'?'Vekst mot 2050':s.growth==='down'?'Nedgang mot 2050':'Stabil mot 2050';
    const grDot='<span class="kstat-dot s-'+s.growth+'" title="'+grTitle+'"></span>';
    const rbDot=s.robek==='in'?'<span class="kstat-dot s-robek" title="I ROBEK"></span>':s.robek==='pending'?'<span class="kstat-dot s-robek-pend" title="ROBEK under behandling"></span>':'';
    const sel = k.nr===state.sel;
    return '<div class="kchip" role="option" tabindex="0" aria-selected="'+sel+'" data-nr="'+k.nr+'" title="'+k.navn+' · '+k.fylke+' · '+fmt(k.pop)+' innb.">'+
      '<div class="kchip-head">'+
        '<span class="fdot" style="background:'+FY[k.fylke]+'"></span>'+
        '<span class="knm">'+k.navn+'</span>'+
      '</div>'+
      '<div class="kchip-bot">'+
        '<span class="kpop">'+fmt(k.pop)+'</span>'+
        '<div class="kchip-stats">'+grDot+rbDot+'</div>'+
        '<button class="cmpadd '+(state.compare.includes(k.nr)?'on':'')+'" data-cmp="'+k.nr+'" title="Legg til i sammenligning">'+(state.compare.includes(k.nr)?'●':'+')+'</button>'+
      '</div>'+
    '</div>';
  }).join('');
  // Scroll til valgt kommune
  setTimeout(()=>{
    const selEl = elList.querySelector('[aria-selected=true]');
    if(selEl) selEl.scrollIntoView({inline:'center', behavior:'smooth', block:'nearest'});
  }, 50);
  // Wire strip-arrows
  document.querySelectorAll('[data-knav="stripPrev"],[data-knav="stripNext"]').forEach(b=>{
    b.onclick=()=>{
      const dir = b.dataset.knav==='stripNext'?1:-1;
      elList.scrollBy({left:dir*400, behavior:'smooth'});
    };
  });
}
function ageGroups(arr,mode){
  if(mode==='1') return AGES.map((l,i)=>({l:l.replace(' år',''),v:arr[i]}));
  // Siste gruppe må ta med indeks 105 («105 år eller eldre»), ellers faller de
  // eldste ut av 5-årsvisningen (4 personer i landsdelen per 1.1.2026).
  if(mode==='5'){const g=[];for(let s=0;s<105;s+=5){const sisteGruppe=s+5>=105;
    g.push({l:sisteGruppe?'100+':`${s}–${s+4}`,v:arr.slice(s,sisteGruppe?106:s+5).reduce((a,b)=>a+b,0)});}return g;}
  // livsfaser
  const cut=[[0,5,'Barn 0–5'],[6,12,'Barn 6–12'],[13,17,'Ungdom 13–17'],[18,29,'Unge voksne 18–29'],
    [30,44,'Voksne 30–44'],[45,66,'Voksne 45–66'],[67,79,'Eldre 67–79'],[80,105,'Eldre 80+']];
  return cut.map(([s,e,l])=>({l,v:arr.slice(s,e+1).reduce((a,b)=>a+b,0)}));
}
function medianAge(arr){let t=arr.reduce((a,b)=>a+b,0),c=0;for(let i=0;i<arr.length;i++){c+=arr[i];if(c>=t/2)return i;}return 0;}
function barChart(rows,color,unit){
  const n=rows.length, rh=n>40?15:n>20?20:27;
  return NN.placeholder('hstolper',{grupper:[{rader:rows.map(r=>({l:String(r.l),v:r.v}))}],farge:color,format:'tall'},n*rh+20);
}
function rateBars(rows){ // rows:[{l,v(0-100 eller null),c}]
  return NN.placeholder('hstolper',{grupper:[{rader:rows.map(r=>({l:r.l,v:r.v,farge:r.c}))}],format:'pst',maks:100},rows.length*27+20);
}
function sysCard(sj){
  const obj=sj[state.sysSex]||{};
  const colors={tot:'var(--ink)',abc:'var(--nl)',zzz:'var(--syss)',ddd:'var(--tr)',eee:'var(--amber)'};
  const rows=SGROUPS.map(p=>{const v=obj[p[0]];return {l:p[1],v:(v==null?null:v),c:colors[p[0]]};});
  const R=sj.rate; let foot;
  if(R.zzz!=null && R.tot!=null){
    foot='Innvandrere ligger <b>'+Math.abs(R.tot-R.zzz).toFixed(1).replace('.',',')+' prosentpoeng</b> '+(R.tot-R.zzz>=0?'under':'over')+' hele befolkningen her';
    if(R.ddd!=null && R.eee!=null)
      foot+=', og vestlige innvandrere ligger <b>'+Math.abs(R.ddd-R.eee).toFixed(1).replace('.',',')+' prosentpoeng</b> '+(R.ddd-R.eee>=0?'over':'under')+' ikke-vestlige ('+R.ddd.toFixed(1).replace('.',',')+' % mot '+R.eee.toFixed(1).replace('.',',')+' %)';
    foot+='.';
  } else { foot='Antall sysselsatte innvandrere: '+(sj.cnt&&sj.cnt.zzz!=null?fmt(sj.cnt.zzz):'\u2013')+'.'; }
  const sel=x=>state.sysSex===x?'true':'false';
  return '<div class="card"><div class="ch"><h3 class="serif">Sysselsetting</h3>'+
    '<div class="minseg" id="sxs">'+
    '<button data-x="rate" aria-selected="'+sel('rate')+'">Begge</button>'+
    '<button data-x="rateM" aria-selected="'+sel('rateM')+'">Menn</button>'+
    '<button data-x="rateK" aria-selected="'+sel('rateK')+'">Kvinner</button></div></div>'+
    '<p class="hint">Andel sysselsatte, 20\u201366 \u00e5r (tabell 11607, 4. kv. 2025). Egen kilde og \u00e5rgang \u2014 sammenlign med folketallene over med varsomhet.</p>'+
    rateBars(rows)+'<p class="hint" style="margin:14px 0 0">'+foot+'</p></div>';
}
function projChart(k,mode){
  // Tegnes av den nye diagrammotoren (src/charts/proj.js). Her settes bare en plassholder inn.
  const o=DATA.proj&&DATA.proj.kommuner[k.nr]; if(!o||!window.NN) return '';
  return NN.placeholder('proj',{nr:k.nr,mode:mode,u:state.ukr,b:state.ukrbase,m:state.showMVP?1:0,s:state.sens,w:state.mw},mode==='fb'?470:340);
}
function projCard(k){
  const P=DATA.proj; const o=P&&P.kommuner[k.nr]; if(!o) return '';
  const yrs=P.years, n=yrs.length;
  const m0=o.main[0], m1=o.main[n-1], chg=((m1/m0-1)*100);
  const g65_0=o.a65[0], g65_1=o.a65[n-1];
  const tot0=o.a019[0]+o.a2064[0]+o.a65[0], tot1=o.a019[n-1]+o.a2064[n-1]+o.a65[n-1];
  const sh0=(g65_0/tot0*100), sh1=(g65_1/tot1*100);
  const sel=x=>state.projMode===x?'true':'false';
  const mw=MW(o), LM=LMW();
  const ubn=(state.ukrbase==='attr'?'TF-ATTR':'TF-MVP');
  const ubaseTraj=(state.ukrbase==='attr')?o.tfattr:(mw?mw.pop:null);
  const us=state.ukr?((state.ukrbase==='attr')?(o['ukra'+state.ukr]||null):((mw&&mw['u'+state.ukr])||null)):null;
  const ubLDbase=(state.ukrbase==='attr')?(P.landsdel&&P.landsdel.tfattr||[]):(LM.pop||[]);
  const ubLDscen=state.ukr?((state.ukrbase==='attr')?((P.landsdel&&P.landsdel['ukra'+state.ukr])||[]):(LM['u'+state.ukr]||[])):[];
  const LD=P.landsdel||{}; const usel=x=>state.ukr===x?'true':'false'; const usel2=x=>state.ukrbase===x?'true':'false';
  const fbA6=o.a65, fbA2=o.a2064;   // SSB MMMM — hovedbane
  const oad0=fbA2[0]?fbA6[0]/fbA2[0]*100:0, oad1=fbA2[n-1]?fbA6[n-1]/fbA2[n-1]*100:0;
  const sup0=fbA6[0]?fbA2[0]/fbA6[0]:0, sup1=fbA6[n-1]?fbA2[n-1]/fbA6[n-1]:0;
  const g65p=fbA6[0]?(fbA6[n-1]/fbA6[0]-1)*100:0, g20p=fbA2[0]?(fbA2[n-1]/fbA2[0]-1)*100:0;
  const dnat=mw?mw.nat[n-1]:0, dmig=mw?mw.mig[n-1]:0;
  const dtot=(mw?mw.pop[n-1]-mw.pop[0]:m1-m0);
  const mwsel=x=>state.mw===x?'true':'false';
  const RN=(P.reg_nm||{}), WN=(P.win_note||{});
  const drv=(dnat<0&&dmig>=-dnat)?'Innflytting mer enn oppveier f\u00f8dselsunderskuddet \u2014 derfor vekst.'
    :(dnat<0&&dmig>0)?'Netto innflytting demper, men oppveier ikke at det f\u00f8des f\u00e6rre enn det d\u00f8r.'
    :(dnat<0&&dmig<0)?'B\u00e5de f\u00f8dselsunderskudd og netto utflytting trekker folketallet ned.'
    :(dnat>=0&&dmig>=0)?'B\u00e5de naturlig endring og flytting bidrar positivt.'
    :'Naturlig tilvekst, men netto utflytting trekker ned.';
  const ssel=x=>state.sens===x?'true':'false';
  return '<div class="card" data-helpfor="<b>Slik leser du framskrivingen.</b> SSB MMMM (offisiell) og strukturmodellen fra Telemarksforskning (vår tilleggsbane) vises sammen. Yttergrense-modeller vises som et spenn av ytterpunkter. Skru på Ukraina-scenario eller flyttefølsomhet for å se hvor sårbart utfallet er for forutsetningene."><div class="ch"><h3 class="serif">Hva skjer i '+k.navn+' mot 2050?</h3>'+
    '<div class="minseg" id="pjm">'+
    '<button data-p="tot" aria-selected="'+sel('tot')+'">Folketall</button>'+
    '<button data-p="dec" aria-selected="'+sel('dec')+'">Drivkrefter</button>'+
    '<button data-p="fb" aria-selected="'+sel('fb')+'">Forsørgerbrøk</button>'+
    '<button data-p="age" aria-selected="'+sel('age')+'">Aldring</button></div></div>'+
    '<p class="hint">SSBs regionale framskriving (tabell 14746, 2026-basert). '+
    (state.projMode==='tot'
      ? 'Den m\u00f8rke linja viser <b>faktisk folketall 1.1.2000\u20132025</b> (SSB tabell 07459, kommuner 2024-sammensl\u00e5tte tidsserier). Den vertikale streken markerer <b>i dag</b>. F.o.m. 2026 starter framskrivingen: SSB MMMM som heltrukken aurora-linje med <i>lav\u2013h\u00f8y</i>-b\u00e5nd, samt strukturmodellen (vår tilleggsbane). Yttergrense-modellene vises i detaljvisningen. Den lange trenden gir kontekst \u2014 har kommunen vokst eller blitt mindre de siste 25 \u00e5rene, og hvordan ser banen mot 2050 ut sammenlignet med det?'
      : state.projMode==='dec'
      ? 'Drivkrefter: endringen 2026\u20132050 splittet i naturlig endring (f\u00f8dsler \u2212 d\u00f8dsfall) og netto flytting. <b>Dekomponeringen finnes bare for TF-MVP</b> \u2014 yttergrense-modellen med valgt flyttevindu, ikke SSB MMMM eller TF-ATTR. Sluttfolketallet her avviker derfor fra Folketall-fanen; bytt flyttevindu nederst for \u00e5 se hvor f\u00f8lsom fordelingen er.'
      : state.projMode==='fb'
      ? 'Forsørgerbrøk: antall eldre (65+) per 100 i alderen 20–64, 2026\u20132050 \u2014 og hvorfor den stiger. Regnes p\u00e5 SSB MMMM (hovedbanen) og er uavhengig av flyttevindu.'
      : 'Antall i tre aldersgrupper, hovedalternativet (MMMM).')+'</p>'+
    projChart(k,state.projMode)+
    (state.projMode==='tot'?(
      '<div class="minseg" id="sens" style="margin:10px 0 0"><button data-s="0" aria-selected="'+ssel(0)+'">F\u00f8lsomhet av</button><button data-s="1" aria-selected="'+ssel(1)+'">Flytting \u00b125 %</button></div>'+
      (state.sens?'<p class="hint" style="margin:6px 0 0;opacity:.75;font-size:11px">B\u00e5nd = TF-MVP med netto flytting \u00d70,75 og \u00d71,25. Flytting er det mest usikre leddet; dette viser hvor mye banen avhenger av nettopp den forutsetningen \u2014 en f\u00f8lsomhet, ikke et prognoseintervall.</p>':'')
    ):'')+
    (state.projMode==='dec'?(
      '<p class="hint" style="margin:14px 0 0">Av en samlet endring p\u00e5 <b>'+(dtot>=0?'+':'\u2212')+fmt(Math.abs(dtot))+'</b> til 2050 kommer <b>'+(dnat>=0?'+':'\u2212')+fmt(Math.abs(dnat))+'</b> fra naturlig endring (f\u00f8dsler \u2212 d\u00f8dsfall) og <b>'+(dmig>=0?'+':'\u2212')+fmt(Math.abs(dmig))+'</b> fra netto flytting. '+drv+'</p>'
    ):state.projMode==='fb'?(
      '<p class="hint" style="margin:14px 0 0">Fors\u00f8rgerbr\u00f8ken '+(oad1>=oad0?'stiger':'faller')+' fra <b>'+oad0.toFixed(0).replace('.',',')+'</b> til <b>'+oad1.toFixed(0).replace('.',',')+'</b> eldre per 100 i alderen 20\u201364 \u2014 fra <b>~'+sup0.toFixed(1).replace('.',',')+'</b> til <b>~'+sup1.toFixed(1).replace('.',',')+'</b> i alderen 20\u201364 bak hver person 65+. Drivkraften er forskyvningen mellom gruppene: <b>65+ '+(g65p>=0?'+':'\u2212')+Math.abs(g65p).toFixed(0).replace('.',',')+' %</b> mens <b>20\u201364 '+(g20p>=0?'+':'\u2212')+Math.abs(g20p).toFixed(0).replace('.',',')+' %</b> (SSB MMMM). '+
      ((g20p<0&&g65p>0)?'Begge effektene virker samtidig \u2014 flere eldre og f\u00e6rre i arbeidsf\u00f8r alder.'
       :(g65p>0&&g20p>=0)?'Det er f\u00f8rst og fremst flere eldre, ikke f\u00e6rre i arbeidsf\u00f8r alder, som driver økningen.'
       :'Gruppen i arbeidsf\u00f8r alder faller mer enn de eldre \u00f8ker.')+' Tallene f\u00f8lger SSB MMMM og endres ikke av flyttevinduet.</p>'
    ):(
      '<p class="hint" style="margin:14px 0 0">Hovedalternativet: <b>'+fmt(m0)+'</b> (2026) \u2192 <b>'+fmt(m1)+'</b> (2050), '+
      (chg>=0?'+':'')+chg.toFixed(1).replace('.',',')+' %. Andel 65+ \u00f8ker fra '+sh0.toFixed(1).replace('.',',')+' % til <b>'+sh1.toFixed(1).replace('.',',')+' %</b> ('+fmt(g65_0)+' \u2192 '+fmt(g65_1)+' personer).</p>'
    ))+
    (state.projMode==='fb'?'':'<p class="hint" style="margin:6px 0 0">Fors\u00f8rgerbr\u00f8k 65+/20\u201364: <b>'+oad0.toFixed(0).replace('.',',')+'</b> \u2192 <b>'+oad1.toFixed(0).replace('.',',')+'</b> eldre per 100 i alderen 20\u201364 (2026\u20132050, SSB MMMM). <span style="opacity:.7">Se «Forsørgerbrøk»-fanen for hvorfor.</span></p>')+
    '<details style="margin:8px 0 0"><summary style="cursor:pointer;font-size:12px;color:var(--ink2);font-weight:600">Slik regnes dette \u2014 kohort-komponent p\u00e5 \u00e9n setning</summary><p class="hint" style="margin:6px 0 0;font-size:11.5px">Hvert \u00e5r flyttes alle ett \u00e5r opp i alderspyramiden, en aldersavhengig andel d\u00f8r, kvinner i fertil alder gir et antall f\u00f8dte (skalert til lokalt fruktbarhetsniv\u00e5), og et netto flyttetall fordeles p\u00e5 alder. Eksempel: 100 stk. 40-\u00e5ringer i \u00e5r \u2192 ~99,9 lever som 41-\u00e5ringer neste \u00e5r, justert for inn-/utflytting i den aldersgruppen. Gjentas 24 ganger (2026\u20132050). TF-MVP og TF-ATTR bruker samme maskineri; forskjellen er bare hvordan flytteleddet ansl\u00e5s.</p></details>'+
    (((state.projMode==='tot'||state.projMode==='dec'||state.projMode==='fb')&&mw)?(
      '<div class="ch" style="margin-top:12px;padding-top:10px;border-top:1px solid var(--line2)"><h3 class="serif" style="font-size:15px">Flyttevindu (TF-MVP)</h3>'+
      '<div class="minseg" id="mw"><button data-w="kons" aria-selected="'+mwsel('kons')+'">Smalt 2017\u201321</button><button data-w="sentral" aria-selected="'+mwsel('sentral')+'">Median 2017–25</button><button data-w="opt" aria-selected="'+mwsel('opt')+'">Snitt 2017\u201325</button></div></div>'+
      '<p class="hint" style="margin:8px 0 0">'+(WN[state.mw]||'')+'. Regionen samlet: <b>'+((RN[state.mw]||0)>=0?'+':'\u2212')+fmt(Math.abs(RN[state.mw]||0))+'</b> netto innflytting per \u00e5r. Standard er <b>Smalt 2017\u20132021</b> fordi median og snitt for 2017\u20132025 fortsatt gir den unormale 2022\u20132023-innvandringen stor vekt i 24 \u00e5r. Alle vinduene inkluderer 2024 og 2025. <b>TF-ATTR p\u00e5virkes ikke</b> \u2014 den bruker strukturell regresjon, ikke historisk snitt. <b>NB:</b> vindusnavnene er beskrivelser av <i>tidsperioden</i>, ikke normative anslag \u2014 et \u00absmalt\u00bb vindu kan godt v\u00e6re pessimistisk hvis den perioden tilfeldigvis var kommunens svakeste.</p>'
    ):'')+
    (state.projMode==='tot'&&mw?(
      (function(){
        // Sanity-flagg: hvis TF-MVP avviker mer enn 15 pp fra SSB MMMM ved 2050, varsle eksplisitt.
        var ssb2050=o.main[n-1], mvp2050=mw.pop[n-1];
        var ppDiff = ssb2050 ? (mvp2050/ssb2050-1)*100 : 0;
        var winLabel = ({kons:'Smalt 2017\u20132021',sentral:'Median 2017\u20132025',opt:'Snitt 2017\u20132025'})[state.mw];
        var warn='';
        if(Math.abs(ppDiff) >= 15){
          var dir = ppDiff < 0 ? 'mer pessimistisk' : 'mer optimistisk';
          warn = '<div style="margin:10px 0 0;padding:10px 12px;background:color-mix(in srgb, var(--warn) 10%, transparent);border:1px solid color-mix(in srgb, var(--warn) 32%, transparent);border-left:4px solid var(--amber);border-radius:0;font-size:12.5px;color:var(--ink)"><b>Stort avvik mot SSB:</b> TF-MVP med vinduet \u00ab'+winLabel+'\u00bb er <b>'+Math.abs(ppDiff).toFixed(0).replace('.',',')+' %</b> '+dir+' enn SSB MMMM ved 2050. Det skyldes at flyttetallene i det valgte vinduet var '+(ppDiff<0?'spesielt svake':'spesielt sterke')+' for denne kommunen; modellen forutsetter at det gjentar seg i 24 \u00e5r. Pr\u00f8v et annet vindu eller bytt til <b>TF-ATTR</b> for en strukturbasert kontroll.</div>';
        }
        return warn;
      })()+
      '<p class="hint" style="margin:8px 0 0">Yttergrense-modell, vindu '+({kons:'Smalt 2017\u20132021',sentral:'Median 2017\u20132025',opt:'Snitt 2017\u20132025'})[state.mw]+': <b>'+fmt(mw.pop[0])+'</b> \u2192 <b>'+fmt(mw.pop[n-1])+'</b> (2050), avvik fra SSB <b>'+((mw.pop[n-1]-o.main[n-1])>=0?'+':'\u2212')+fmt(Math.abs(mw.pop[n-1]-o.main[n-1]))+'</b>'+(o.tfmvp_flag?' \u00b7 <b>tynt grunnlag</b>':'')+'. '+
      (o.tfattr?'Strukturmodell (tilleggsbane): <b>'+fmt(o.tfattr[0])+'</b> \u2192 <b>'+fmt(o.tfattr[n-1])+'</b> (2050), avvik fra SSB <b>'+((o.tfattr[n-1]-o.main[n-1])>=0?'+':'\u2212')+fmt(Math.abs(o.tfattr[n-1]-o.main[n-1]))+'</b>.':'')+'</p>'+
      '<p class="hint" style="margin:6px 0 0;opacity:.7;font-size:11px">Telemarksforskning-modellene er reprodusert, ikke validert. Hovedbanen i dashbordet er alltid SSB MMMM; strukturmodellen er en tilleggsbane til SSB MMMM (slo SSB i de minst sentrale kommunene i etterpr\u00f8vingen for 2020\u20132024, kort horisont). Yttergrense-modellene viser et spenn av ytterpunkter.</p>'+
      '<div class="ch" style="margin-top:12px;padding-top:10px;border-top:1px solid var(--line2)"><h3 class="serif" style="font-size:15px">Scenario: ukrainske flyktninger forlater landsdelen</h3>'+
      '<div class="minseg" id="ukr"><button data-u="0" aria-selected="'+usel(0)+'">Av</button><button data-u="50" aria-selected="'+usel(50)+'">50 %</button><button data-u="75" aria-selected="'+usel(75)+'">75 %</button><button data-u="100" aria-selected="'+usel(100)+'">100 %</button></div></div>'+
      (us?(
        '<div class="minseg" id="ukrb" style="margin:10px 0 2px"><button data-b="mvp" aria-selected="'+usel2('mvp')+'">Basis: TF-MVP</button><button data-b="attr" aria-selected="'+usel2('attr')+'">Basis: TF-ATTR</button></div>'+
        '<p class="hint" style="margin:8px 0 0">Kommunen har <b>'+fmt(o.ukr)+'</b> registrerte ukrainske innvandrere. Hvis <b>'+state.ukr+' %</b> forlater landsdelen i l\u00f8pet av ett \u00e5r (2027), lagt p\u00e5 <b>'+ubn+'</b>-banen'+(state.ukrbase==='attr'?'':' ('+({kons:'Smalt 2017\u20132021',sentral:'Median 2017\u20132025',opt:'Snitt 2017\u20132025'})[state.mw]+')')+': folketall 2050 <b>'+fmt((ubaseTraj||[])[n-1]||0)+'</b> \u2192 <b>'+fmt(us[n-1])+'</b> ('+((us[n-1]-((ubaseTraj||[])[n-1]||0))>=0?'+':'\u2212')+fmt(Math.abs(us[n-1]-((ubaseTraj||[])[n-1]||0)))+'). '+
        'Hele landsdelen: <b>'+fmt(Math.round((state.ukr/100)*(LD.ukr_total||0)))+'</b> personer drar (av '+fmt(LD.ukr_total||0)+'); regionalt folketall 2050 <b>'+fmt((ubLDbase||[])[n-1]||0)+'</b> \u2192 <b>'+fmt((ubLDscen||[])[n-1]||0)+'</b>.</p>'+
        '<p class="hint" style="margin:6px 0 0;opacity:.7;font-size:11px">Forutsetning: engangsutflytting i 2027 oppe p\u00e5 '+ubn+'-banen, fordelt p\u00e5 en kvinne/barn-tung flyktningprofil (dokumentert, ikke kalibrert). En f\u00f8lsomhetsberegning, ikke en prognose.</p>'
      ):'')
    ):'')+
    '</div>';
}
function kostraCard(k){
  const P=DATA.proj; if(!P||(!P.kostra&&!P.kostra_bench)) return '';
  const isA=k.isAgg;
  const ks=isA?((P.kostra_bench||{})[k.fylke]||(P.kostra_bench||{})['Alle']):((P.kostra||{})[k.nr]);
  if(!ks) return '';
  const B=(P.kostra_bench||{})['Alle']||{};
  const FYB=isA?B:((P.kostra_bench||{})[k.fylke]||B);
  const yr=ks.yr||B.yr||'';
  const o=P.kommuner&&P.kommuner[k.nr]; const mw=MW(o); const n=(P.years||[]).length;
  const num=v=>(v==null?null:+v);
  const sgn=v=>v==null?'\u2013':(v>=0?'':'\u2212')+Math.abs(v).toFixed(1).replace('.',',');
  function bar(val,dmin,dmax,col,refs){
    const span=(dmax-dmin)||1;
    const pc=v=>(Math.max(dmin,Math.min(dmax,v))-dmin)/span*100;
    const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
    const neg=dmin<0&&dmax>0, z=neg?pc(0):0;
    let s='<div style="position:relative;height:36px;margin:8px 0 0">';
    // reference labels (own row above the track) + ticks
    (refs||[]).forEach((rf,i)=>{ if(rf[0]==null) return; const x=pc(rf[0]);
      s+='<div style="position:absolute;top:'+(i?13:0)+'px;left:'+clamp(x,7,93)+'%;transform:translateX(-50%);font-size:9px;font-weight:700;color:'+rf[2]+';white-space:nowrap;line-height:1">'+rf[1]+'</div>';
      s+='<div style="position:absolute;top:24px;height:18px;width:2px;left:'+x+'%;transform:translateX(-50%);background:'+rf[2]+';opacity:'+(rf[3]?'.55':'1')+'"></div>'; });
    // track
    s+='<div style="position:absolute;left:0;right:0;top:27px;height:9px;border-radius:0;background:color-mix(in srgb, var(--ink) 9%, transparent)"></div>';
    // value fill
    if(val!=null){ const xv=pc(val); const a=Math.min(z,xv), w=Math.abs(xv-z);
      s+='<div style="position:absolute;top:27px;height:9px;border-radius:0;left:'+a+'%;width:'+Math.max(w,0.8)+'%;background:'+col+'"></div>'; }
    // zero marker for signed scales
    if(neg) s+='<div style="position:absolute;top:24px;height:15px;width:1px;left:'+z+'%;background:var(--ink3)"></div>';
    return s+'</div>';
  }
  function row(label,val,unit,col,verdict,refs,dmin,dmax,explain){
    return '<div style="margin:0 0 16px">'+
      '<div style="display:flex;align-items:baseline;justify-content:space-between;gap:8px">'+
      '<span style="font-weight:600;color:var(--ink)">'+label+'</span>'+
      '<span><b style="font-family:var(--font-mono);font-size:17px;color:'+col+'">'+(val==null?'\u2013':(unit==='%'?sgn(val):fmt(Math.round(val))))+'</b>'+
      '<span style="font-size:11px;color:var(--ink3)"> '+unit+'</span> '+
      '<span style="font-size:10px;font-weight:700;color:'+col+';background:'+col+'1f;padding:2px 7px;border-radius:0">'+verdict+'</span></span></div>'+
      bar(val,dmin,dmax,col,refs)+
      '<p class="hint" style="margin:5px 0 0;font-size:11.5px">'+explain+'</p></div>';
  }
  const GRN='var(--pos)',AMB='var(--amber)',RED='var(--neg)';
  const ndr=num(ks.ndr),fond=num(ks.fond),gjeld=num(ks.gjeld);
  const vNdr=ndr==null?AMB:(ndr>=1.75?GRN:ndr>=0?AMB:RED);
  const vFond=fond==null?AMB:(fond>=10?GRN:fond>=4?AMB:RED);
  const vGjeld=gjeld==null?AMB:(gjeld<=EXT_NORMS.ksGjeld?GRN:gjeld<=100?AMB:RED);
  const refMed=v=>[v,'median','var(--ink2)','2 2'];
  let body='';
  body+=row('Netto driftsresultat',ndr,'%',vNdr,
    ndr==null?'\u2013':(ndr>=1.75?'sunn':ndr>=0?'svak':'underskudd'),
    [[1.75,'TBU 1,75','var(--aurora)',''],refMed(FYB.ndr)],-6,6,
    'Hva er igjen etter driften, i % av inntektene. Teknisk beregningsutvalg (TBU) anbefaler \u2248 +1,75 % over tid for \u00e5 t\u00e5le svingninger og kunne sette av. '+(isA?'Vist som median for '+(k.fylke==='Alle'?'landsdelen':k.fylke)+'.':'Landsdelsmedian: '+sgn(B.ndr)+' %.'));
  body+=row('Disposisjonsfond',fond,'%',vFond,
    fond==null?'\u2013':(fond>=10?'solid buffer':fond>=5?'moderat':fond>=3?'tynn':'kritisk lav'),
    [refMed(FYB.fond)],0,Math.max(25,fond||0,FYB.fond||0),
    'Oppsparte, fritt disponible reserver i % av inntektene \u2014 st\u00f8tputen mot uforutsette utgifter og inntektssvikt. Veiledende: under ~4 % regnes som tynt. Landsdelsmedian: '+sgn(B.fond)+' %.');
  body+=row('Netto l\u00e5negjeld',gjeld,'%',vGjeld,
    gjeld==null?'\u2013':(gjeld<=EXT_NORMS.ksGjeld?'moderat':gjeld<=100?'h\u00f8y':'sv\u00e6rt h\u00f8y'),
    [[EXT_NORMS.ksGjeld,'KS '+EXT_NORMS.ksGjeld,'var(--aurora)',''],refMed(FYB.gjeld)],0,Math.max(160,gjeld||0),
    'Rentb\u00e6rende gjeld fratrukket utl\u00e5n og ubundne midler, i % av inntektene. H\u00f8yere = mer s\u00e5rbar for renteoppgang. Landsdelsmedian: '+sgn(B.gjeld)+' %.');
  // ---- sektormiks (rikere) ----
  // McHalvard kategoripalett i fast rekkefølge (blå, blekk, cyan, skifer, gull, oransje)
  const SEC=[['omsorg_pct','Pleie og omsorg','a67','var(--cat-1)'],
             ['skole_pct','Grunnskole','a615','var(--cat-2)'],
             ['bhg_pct','Barnehage','a15','var(--cat-3)'],
             ['khelse_pct','Kommunehelse',null,'var(--cat-4)'],
             ['kultur_pct','Kultur',null,'var(--cat-5)'],
             ['kirke_pct','Kirke',null,'var(--cat-6)']];
  const sv=f=>num(ks[f]);
  let summed=0; SEC.forEach(s=>{const x=sv(s[0]); if(x!=null)summed+=x;});
  const annet=Math.max(0,100-summed);
  let mix='';
  {
    const parts=SEC.map(s=>[s[1],sv(s[0])||0,s[3]]).concat([['Annet (adm., sosial, barnevern, vei, VAR m.m.)',annet,'color-mix(in srgb, var(--ink) 18%, transparent)']]);
    const seg=parts.map(p=>p[1]>0?'<div style="width:'+p[1]+'%;background:'+p[2]+'" title="'+p[0]+' '+p[1].toFixed(1).replace('.',',')+' %"></div>':'').join('');
    const leg=parts.map(p=>'<span><i style="background:'+p[2]+'"></i>'+p[0].split(' (')[0]+' '+p[1].toFixed(0).replace('.',',')+' %</span>').join('');
    mix='<div style="margin:6px 0 0"><div style="font-weight:600;color:var(--ink);margin:0 0 6px">Hvor pengene g\u00e5r \u2014 andel av netto driftsutgifter</div>'+
      '<div style="display:flex;height:26px;border-radius:0;overflow:hidden;font-size:0">'+seg+'</div>'+
      '<div class="legend" style="margin-top:7px">'+leg+'</div>'+
      (ks.omsorg_pi!=null?'<p class="hint" style="margin:6px 0 0;font-size:11.5px">Helse og omsorg koster <b>'+fmt(Math.round(ks.omsorg_pi))+' kr</b> per innbygger \u2014 den st\u00f8rste og mest aldersf\u00f8lsomme posten.</p>':'')+'</div>';
  }
  // ---- tidsserie-tilgang ----
  const TS=P.kostra_ts||{}; const tyr=TS.years||[];
  const tsK=isA?((TS.bench||{})[k.fylke]||(TS.bench||{})['Alle']||{}):((TS.kommuner||{})[k.nr]||{});
  const tsB=(TS.bench||{})['Alle']||{};
  // ---- gjenbrukbart linjediagram ----
  function lineChart(o){
    // o: {title,col,unit,signed, hx,hv,bench, px,pv, ref} — tegnes av diagrammotoren (src/charts/mini.js)
    const har=(o.hv||[]).some(v=>v!=null)||(o.pv||[]).some(v=>v!=null);
    if(!har) return '';
    return '<div style="min-width:240px">'+NN.placeholder('mini',{tittel:o.title,sub:o.sub,hx:o.hx,hv:o.hv,bench:o.bench,px:o.px||null,pv:o.pv||null,
      ref:(o.ref&&o.ref.val!=null)?{val:o.ref.val,label:o.ref.label}:null,signed:!!o.signed,unit:o.unit,farge:o.col},190)+'</div>';
  }
  const GRID='display:grid;grid-template-columns:repeat(auto-fit,minmax(248px,1fr));gap:14px 18px;margin:8px 0 0';
  // ---- 1) \u00d8konomi over tid (faktisk) ----
  let econ='';
  if(tyr.length>1){
    const E=[['ndr','Netto driftsresultat','var(--amber)',1,{val:1.75,label:'TBU 1,75'}],
             ['bdr','Brutto driftsresultat','var(--gold)',1,null],
             ['fond','Disposisjonsfond','var(--aurora)',0,null],
             ['gjeld','Netto l\u00e5negjeld','var(--nl)',0,null]];
    econ='<div style="margin:8px 0 2px;padding-top:12px;border-top:1px solid var(--line2)">'+
      '<div style="font-weight:600;color:var(--ink)">\u00d8konomi \u2014 faktisk utvikling '+tyr[0]+'\u2013'+tyr[tyr.length-1]+'</div>'+
      '<p class="hint" style="margin:2px 0 0;font-size:11.5px">Heltrukket = '+(isA?'median':k.navn)+', stiplet = landsdelsmedian. <b>Ikke framskrevet</b> \u2014 driftsresultat/gjeld styres av politikk og inntekter, ikke demografi.</p>'+
      '<div style="'+GRID+'">'+
      E.map(e=>lineChart({title:e[1],sub:'% av brutto driftsinntekter',col:e[2],unit:'pct',signed:!!e[3],
        hx:tyr,hv:tsK[e[0]]||[],bench:tsB[e[0]]||[],ref:e[4]})).join('')+'</div></div>';
  }
  // ---- 2) Sektorandeler: faktisk \u2192 demografidrevet (til 2050) ----
  let sec='', stacked='';
  if(mw&&mw.a67&&mw.pop&&n>1){
    const drv={a67:mw.a67,a615:mw.a615,a15:mw.a15,pop:mw.pop};
    const SX=SEC.map(s=>({nm:s[1],f:s[0],d:s[2],c:s[3]})).concat([{nm:'Annet',f:null,d:null,c:'color-mix(in srgb, var(--ink) 30%, transparent)'}]);
    function renorm(raw){let su=0;raw.forEach(x=>su+=x||0);const an=Math.max(0,100-su);
      const arr=raw.map(x=>x||0).concat([an]);let t2=0;arr.forEach(x=>t2+=x);return arr.map(x=>t2?x/t2*100:0);}
    const HY=[],HS=[],HB=[];
    tyr.forEach((Y0,i)=>{  const om=tsK.omsorg_pct&&tsK.omsorg_pct[i]; if(om==null) return;
      HY.push(Y0); HS.push(renorm(SEC.map(s=>tsK[s[0]]?tsK[s[0]][i]:0)));
      HB.push(renorm(SEC.map(s=>tsB[s[0]]?tsB[s[0]][i]:0))); });
    const base=HS.length?HS[HS.length-1]:renorm(SEC.map(s=>sv(s[0])));
    const PY=[],PS=[];
    for(let i=0;i<n;i++){ let tot=0; const w=SX.map((s,si)=>{const dv=s.d?drv[s.d]:drv.pop;const f=(dv&&dv[0])?dv[i]/dv[0]:1;const ww=base[si]*f;tot+=ww;return ww;});
      PY.push((P.years||[])[i]); PS.push(w.map(x=>tot?x/tot*100:0)); }
    const joinY=HY.length?HY[HY.length-1]:(P.years||[])[0];
    const wlab=({kons:'smalt vindu 2017–2021',sentral:'median 2017–2025',opt:'snitt 2017–2025'})[state.mw]||state.mw;
    const SHOW=[0,1,2,3,4]; // omsorg, skole, barnehage, kommunehelse, kultur
    sec='<div style="margin:14px 0 2px;padding-top:12px;border-top:1px solid var(--line2)">'+
      '<div style="font-weight:600;color:var(--ink)">Sektorandel \u2014 faktisk \u2192 demografidrevet, til 2050 <span style="font-size:10px;font-weight:700;color:var(--amber);background:color-mix(in srgb, var(--amber) 12%, transparent);padding:2px 7px;border-radius:0">illustrasjon</span></div>'+
      '<p class="hint" style="margin:2px 0 0;font-size:11.5px">Heltrukket venstre for «i dag» = faktiske KOSTRA-andeler. Stiplet f\u00f8r «i dag» = landsdel. Stiplet etter «i dag» = demografidrevet (flyttebane: '+wlab+', alt annet likt). Andel av netto driftsutgifter.</p>'+
      '<div style="'+GRID+'">'+
      SHOW.map(si=>lineChart({title:SX[si].nm,sub:'% av netto driftsutgifter',col:SX[si].c,unit:'pct',signed:false,
        hx:HY,hv:HS.map(v=>v[si]),bench:HB.map(v=>v[si]),
        px:PY,pv:PS.map(v=>v[si])})).join('')+'</div>'+
      '<p class="hint" style="margin:8px 0 0;font-size:11px;opacity:.8">Stiplet linje etter «i dag» = <b>kun demografieffekt</b>: konstant enhetskostnad/dekningsgrad, ingen produktivitet, politikk eller omstilling. Bytt flyttebane over for f\u00f8lsomhet.</p></div>';
    // stablet helhetsbilde (kollapsbart)
    const XY=HY.concat(PY.filter(y=>y>joinY)), ST=[];
    HY.forEach((y,idx)=>ST.push(HS[idx])); PY.forEach((y,idx)=>{ if(y>joinY||(!HY.length&&idx===0)) ST.push(PS[idx]); });
    if(XY.length>1){
      const sy0=XY[0];
      const g=NN.placeholder('stablet',{x:XY,serier:SX.map((sx,si)=>({navn:sx.nm,data:ST.map(r=>Math.round(r[si]*10)/10),farge:sx.c})),iDag:joinY},290);
      stacked='<details style="margin:12px 0 0"><summary style="cursor:pointer;font-weight:600;color:var(--ink2);font-size:12.5px">Samlet sammensetning (alle sektorer stablet, '+(HY.length?HY[0]:sy0)+'\u20132050)</summary><p class="hint" style="margin:6px 0 6px;font-size:11px">Samme tall som over, men stablet til 100 % \u2014 se hvordan hele kaka vris.</p>'+g+'</details>';
    }
  }
  // ---- 80+ omsorgspress (kort) ----
  let bridge='';
  if(o&&o.a80&&o.a80.length>1&&sv('omsorg_pct')!=null){
    const a0=o.a80[0],a1=o.a80[n-1],r=a0?a1/a0:1,gp=(r-1)*100,om=sv('omsorg_pct');
    bridge='<p class="hint" style="margin:12px 0 0;font-size:11.5px;padding-top:10px;border-top:1px solid var(--line2)">Spissere: innbyggere <b>80+</b> g\u00e5r fra <b>'+fmt(a0)+'</b> til <b>'+fmt(a1)+'</b> ('+(gp>=0?'+':'\u2212')+Math.abs(gp).toFixed(0).replace('.',',')+' %). Med konstant kostnad per 80+ ville pleie og omsorg alene tilsvart <b>~'+(om*r).toFixed(0).replace('.',',')+' %</b> av et budsjett p\u00e5 dagens niv\u00e5 (mot '+om.toFixed(0).replace('.',',')+' % i dag).</p>';
  }
  // ---- full KOSTRA-tabell (siste verdi mot landsdel) ----
  const F=(v,kind)=> v==null?'\u2013' : kind==='pct'? sgn(v)+' %' : kind==='kr'? fmt(Math.round(v))+' kr' : (''+v);
  const GRP=[
   ['\u00d8konomi (% av brutto driftsinntekter, kr)',[
     ['ndr','Netto driftsresultat','pct'],['bdr','Brutto driftsresultat','pct'],
     ['fond','Disposisjonsfond','pct'],['gjeld','Netto l\u00e5negjeld','pct'],
     ['lgjeld','Langsiktig gjeld','pct'],['finutg','Netto finansutgifter','pct'],
     ['akap','Arbeidskapital','pct'],['frieink','Frie inntekter / innbygger','kr']]],
   ['Sektorandel (% av netto driftsutgifter)',[
     ['omsorg_pct','Pleie og omsorg','pct'],['khelse_pct','Kommunehelse','pct'],
     ['skole_pct','Grunnskole','pct'],['bhg_pct','Barnehage','pct'],
     ['kultur_pct','Kultur','pct'],['kirke_pct','Kirke','pct'],
     ['eiendom_pct','Eiendomsforvaltning','pct']]],
   ['Per innbygger (kr)',[
     ['omsorg_pi','Helse og omsorg / innb.','kr'],['skole_pi','Grunnskole / innb. 6\u201315','kr'],
     ['bhg_pi','Barnehage / innb. 1\u20135','kr'],['kultur_pi','Kultur / innb.','kr'],
     ['vei_pi','Kommunale veier / innb.','kr'],['bvern_pi','Barnevern / innb. 0\u201317','kr'],
     ['eiendom_pi','Eiendomsforvaltning / innb.','kr']]]];
  let tbl='';
  GRP.forEach(grp=>{
    tbl+='<div style="font-weight:700;color:var(--ink);font-size:11.5px;margin:12px 0 4px">'+grp[0]+'</div>'+
      '<table style="width:100%;border-collapse:collapse;font-size:11.5px">'+
      '<tr style="color:var(--ink3)"><td style="text-align:left;padding:2px 0">N\u00f8kkeltall</td><td style="text-align:right">Siste ('+(yr||tyr[tyr.length-1])+')</td><td style="text-align:right;padding-left:14px">Landsdel</td></tr>';
    grp[1].forEach(r=>{ tbl+='<tr style="border-top:1px solid var(--line2)">'+
      '<td style="text-align:left;padding:3px 0;color:var(--ink2)">'+r[1]+'</td>'+
      '<td style="text-align:right;font-family:var(--font-mono);color:var(--ink)">'+F(num(ks[r[0]]),r[2])+'</td>'+
      '<td style="text-align:right;padding-left:14px;font-family:var(--font-mono);color:var(--ink3)">'+F(num(B[r[0]]),r[2])+'</td></tr>'; });
    tbl+='</table>';
  });
  const full='<details style="margin:14px 0 0;padding-top:10px;border-top:1px solid var(--line2)"><summary style="cursor:pointer;font-weight:600;color:var(--ink2);font-size:12.5px">Alle KOSTRA-n\u00f8kkeltall \u2014 siste verdi mot landsdelsmedian</summary><p class="hint" style="margin:6px 0 8px;font-size:11px">Utviklingen over tid vises i grafene over. Tabellen er sisteverdi-oppslaget.</p>'+tbl+'</details>';
  const deep=(econ||sec)?'<details style="margin:14px 0 0;padding-top:10px;border-top:1px solid var(--line2)"><summary style="cursor:pointer;font-weight:600;color:var(--ink2);font-size:12.5px">G\u00e5 dypere \u2014 utvikling per n\u00f8kkeltall over tid (\u00f8konomi + sektorandeler 2015\u20132050)</summary>'+econ+sec+'</details>':'';
  return '<div class="card">'+
    '<p class="hint" style="margin-top:0">'+(isA?'Median for '+(k.fylke==='Alle'?'de 80 kommunene i landsdelen':k.fylke)+' (forholdstall summeres ikke). ':'SSB KOSTRA-konserntall'+(yr?' ('+yr+')':'')+'. ')+
    'Tre tall sier mest om \u00f8konomisk handlingsrom: resultat, buffer og gjeld. Fargene er veiledende \u2014 ikke offisielle grenseverdier; se ogs\u00e5 utviklingsgrafene under.</p>'+
    body+mix+deep+stacked+bridge+full+
    '<details style="margin:12px 0 0"><summary style="cursor:pointer;font-size:12px;color:var(--ink2);font-weight:600">Kilder og forbehold</summary><p class="hint" style="margin:6px 0 0;font-size:11px">SSB KOSTRA-konserntall: tab. 12143 (finansielle n\u00f8kkeltall, % av brutto driftsinntekter), 12209 (helse/omsorg), 12255 (grunnskole), 13502 (barnehage), 13135 (kultur), 12025 (kirke), 11816 (samferdsel), 12279 (barnevern), 12051 (eiendom), 12134 (frie inntekter). Tidsserie 2015\u20132025; 2025 er endelige tall (publisert 15. juni 2026). Nye kommunenummer fra 2024 mangler ofte tidligere \u00e5r. Sektorframskrivingen bruker aldersgruppene fra kohortmodellen for valgt flyttevindu og er en ren demografivekting, ikke en \u00f8konomiprognose.</p></details></div>';
}
function diagnoseCard(k){
  const P=DATA.proj; if(!P) return '';
  const o=P.kommuner&&P.kommuner[k.nr]; const n=(P.years||[]).length;
  if(!o||n<2) return '';
  const f=v=>fmt(Math.round(v));
  const pct=(a,b)=>b?((a/b-1)*100):0;
  // SSB MMMM er hovedbane overalt; strukturmodellen (TF-ATTR) er tilleggsbane.
  // pop0 er faktisk folketall per 1.1.2026 (k.pop).
  const pop0=k.pop;
  const pop1_ssb=o.main[n-1], pp_ssb=pct(pop1_ssb,pop0);
  const pop1_attr=o.tfattr?o.tfattr[n-1]:null;
  const pp_attr=pop1_attr!=null?pct(pop1_attr,pop0):null;
  // Forsørgerbyrde og 80+ fra SSB MMMM (o.a65/a2064 er SSB-tall, ikke vindu-spesifikke)
  const a6=o.a65, a2=o.a2064;
  const oad0=a6&&a2&&a2[0]?100*a6[0]/a2[0]:null, oad1=a6&&a2&&a2[n-1]?100*a6[n-1]/a2[n-1]:null;
  const a8=o.a80;   // SSB MMMM — hovedbane
  const g80=a8&&a8[0]?pct(a8[n-1],a8[0]):null;
  const isA=k.isAgg;
  const ks=isA?((P.kostra_bench||{})[k.fylke]||(P.kostra_bench||{})['Alle']):((P.kostra||{})[k.nr]);
  const num=v=>v==null?null:+v;
  const ndr=ks?num(ks.ndr):null, fond=ks?num(ks.fond):null, gj=ks?num(ks.gjeld):null, yr=ks&&ks.yr;
  let neg=0,pos=0;
  if(ndr!=null){ if(ndr>=1.75)pos++; else if(ndr<0)neg++; }
  if(fond!=null){ if(fond>=10)pos++; else if(fond<5)neg++; }
  if(gj!=null){ if(gj<=85)pos++; else if(gj>110)neg++; }
  const verdict=(neg>=2)?'svakt':((pos>=2&&neg===0)?'solid':'blandet');
  const vc=(verdict==='svakt')?'var(--neg)':(verdict==='solid'?'var(--pos)':'var(--amber)');
  const sgn1=v=>(v>=0?'+':'−')+Math.abs(v).toFixed(0).replace('.',',');
  // Yttergrense-spennvidde: smalt 2017-21-vindu som outlier-merknad
  let spread='';
  if(o.mw&&o.mw.kons){
    const mvp_smalt=o.mw.kons.pop[n-1];
    spread=' Yttergrense-modellen (smalt 2017–2021-vindu, TF-MVP) sier <b>'+f(mvp_smalt)+'</b> — det er hva som skjer hvis flyttetrenden 2017–2021 vedvarer i 24 år.';
  }
  let s='';
  s+='<b>'+k.navn+'</b> har <b>'+f(pop0)+'</b> innbyggere (per 1.1.2026'+(aprilPop(k)?'; '+BEFK_DATA.dato_norsk+': '+f(aprilPop(k)):'')+'). ';
  s+='SSBs offisielle bane (MMMM) peker mot <b>'+f(pop1_ssb)+'</b> i 2050 (<b>'+sgn1(pp_ssb)+' %</b>)';
  if(pop1_attr!=null){
    s+='. Strukturmodellen fra Telemarksforskning — vår tilleggsbane, som slo SSB i de minst sentrale kommunene i etterpr\u00f8vingen for 2020\u20132024 — sier <b>'+f(pop1_attr)+'</b> (<b>'+sgn1(pp_attr)+' %</b>)';
  }
  s+='. ';
  if(oad0!=null&&oad1!=null) s+=(oad1>=oad0?'Aldringen er kjernen: forsørgerbrøken stiger':'Forsørgerbrøken er høy i dag, men faller')+' fra <b>'+oad0.toFixed(0).replace('.',',')+'</b> til <b>'+oad1.toFixed(0).replace('.',',')+'</b> eldre per 100 i alderen 20–64'+(g80!=null?', og innbyggere 80+ '+(g80>=0?'øker':'går ned')+' <b>'+sgn1(g80)+' %</b>':'')+'. ';
  if(ks&&(ndr!=null||fond!=null||gj!=null)) s+='Det økonomiske utgangspunktet er <b style="color:'+vc+'">'+verdict+'</b>'+(yr?' ('+yr+')':'')+': netto driftsresultat <b>'+(ndr==null?'–':(ndr>=0?'':'−')+Math.abs(ndr).toFixed(1).replace('.',','))+' %</b> (TBU-norm +1,75), disposisjonsfond <b>'+(fond==null?'–':fond.toFixed(1).replace('.',','))+' %</b>, netto lånegjeld <b>'+(gj==null?'–':gj.toFixed(1).replace('.',','))+' %</b>. ';
  s+='Holdes alt annet likt, vrir demografien driftsbudsjettet mot pleie og omsorg — vist i grafene under.'+spread;
  return '<div class="card" style="border-left:4px solid var(--amber);border-radius:0">'+
    '<div class="ch" style="margin-bottom:6px"><h3 class="serif">Kortversjon — demografi møter økonomi</h3>'+
    '<span style="font-size:10px;font-weight:700;color:var(--aurora);background:color-mix(in srgb, var(--accent) 15%, transparent);padding:2px 8px;border-radius:0">SSB MMMM · hovedbane</span></div>'+
    '<p style="margin:0;font-size:13.5px;line-height:1.65;color:var(--ink)">'+s+'</p>'+
    '<p class="hint" style="margin:8px 0 0;font-size:11px;opacity:.75">SSB MMMM er hovedbanen; strukturmodellen (TF-ATTR) er vår tilleggsbane. Yttergrense-modeller vises som ytterpunkter til sammenligning. KOSTRA: siste tilgjengelige år.</p></div>';
}
function robekProxy(nr){
  const P=DATA.proj, ks=(P.kostra||{})[nr], TS=P.kostra_ts||{}, tsK=(TS.kommuner||{})[nr]||{};
  const N=v=>v==null?null:+v;
  const ndr=ks?N(ks.ndr):null, fond=ks?N(ks.fond):null, gj=ks?N(ks.gjeld):null, bdr=ks?N(ks.bdr):null, yr=ks&&ks.yr;
  const ndrs=(tsK.ndr||[]).filter(v=>v!=null), neg=ndrs.filter(v=>v<0).length;
  let pts=0;
  // Disposisjonsfond dominerer \u2014 direkte utl\u00f8sende for oppsamlet merforbruk (\u00a728-1 d)
  if(fond!=null){ if(fond<1)pts+=4; else if(fond<3)pts+=3; else if(fond<5)pts+=1; }
  // Driftsresultat
  if(ndr!=null){ if(ndr<-2)pts+=3; else if(ndr<0)pts+=2; else if(ndr<1.75)pts+=0.5; }
  // Kronisk svakhet
  if(neg>=5)pts+=3; else if(neg>=3)pts+=2; else if(neg>=2)pts+=1;
  if(bdr!=null&&bdr<0)pts+=1;
  // L\u00e5negjeld bare som svak forsterker (ikke et ROBEK-vilk\u00e5r i seg selv)
  if(gj!=null&&gj>=160)pts+=1;
  const lvl=pts>=6?3:pts>=4?2:pts>=2?1:0;
  return {pts:pts,lvl:lvl,ndr:ndr,fond:fond,gj:gj,bdr:bdr,neg:neg,yr:yr,nser:ndrs.length};
}
function robekOverviewHTML(fylke){
  const P=DATA.proj, RB=P.robek||{kommuner:{}}; if(!P||!P.robek) return '';
  const LV=['Lav','Moderat','Forh\u00f8yet','H\u00f8y'], LC=['var(--pos)','var(--cat-5)','var(--amber)','var(--neg)'];
  const scope=fylke==='Alle'?'Nord-Norge':fylke;
  const sf=(f)=>'Statsforvalteren i '+(f==='Alle'?'fylket':(f==='Troms'||f==='Finnmark')?'Troms og Finnmark':f);
  const inF=K.filter(x=>fylke==='Alle'?true:x.fylke===fylke);
  const reg=inF.filter(x=>RB.kommuner[x.nr]);
  const pendF=inF.filter(x=>(RB.pending||{})[x.nr]);
  const pctv=inF.length?(reg.length/inF.length*100):0;
  const dist=[0,0,0,0];
  const recs=inF.map(x=>{ const pr=robekProxy(x.nr); dist[pr.lvl]++;
    const st=RB.kommuner[x.nr]?2:((RB.pending||{})[x.nr]?1:0);
    return {nr:x.nr,navn:x.navn,fylke:x.fylke,pr:pr,st:st,let:RB.kommuner[x.nr]||((RB.pending||{})[x.nr]?'d':'')}; });
  const so=state.robekSort||'risk';
  recs.sort((a,b)=> so==='navn'? a.navn.localeCompare(b.navn,'no')
    : so==='fylke'? (a.fylke===b.fylke? b.pr.pts-a.pr.pts : a.fylke.localeCompare(b.fylke,'no'))
    : so==='status'? (b.st-a.st || b.pr.pts-a.pr.pts || a.navn.localeCompare(b.navn,'no'))
    : (b.pr.pts-a.pr.pts || b.st-a.st || a.navn.localeCompare(b.navn,'no')) );
  const seg=(v,t)=>'<button data-s="'+v+'" aria-selected="'+(so===v?'true':'false')+'">'+t+'</button>';
  const stCell=r=> r.st===2
    ? '<span style="color:var(--neg);font-weight:600">I ROBEK</span> <span style="color:var(--ink3);font-size:10px">\u00a728-1 '+r['let']+'</span>'
    : r.st===1 ? '<span style="color:var(--amber);font-weight:600">Over grensen</span> <span style="color:var(--ink3);font-size:10px">(d, behandles)</span>'
    : '<span style="color:var(--ink3)">\u2013</span>';
  const pill=l=>'<span style="display:inline-block;padding:1px 8px;border-radius:0;font-size:10.5px;font-weight:700;color:#fff;background:'+LC[l]+'">'+LV[l]+'</span>';
  const fmtp=(v,unit)=> v==null?'\u2013':(v<0?'\u2212':'')+Math.abs(v).toFixed(unit==='0'?0:1).replace('.',',')+(unit==='%'?'\u2009%':'');
  const showFylke=fylke==='Alle';
  const headerTitle = fylke === 'Alle' ? 'ROBEK — landsdelsoversikt (Nord-Norge)' : 'ROBEK — fylkesoversikt (' + fylke + ')';
  const scopeText = fylke === 'Alle' ? 'Nord-Norge' : fylke;
  const totalReg = K.filter(x => RB.kommuner[x.nr]).length;
  const totalPnd = K.filter(x => (RB.pending||{})[x.nr]).length;
  const totalAffected = totalReg + totalPnd;
  const head='<tr style="color:var(--ink3);font-size:10.5px;text-align:left">'+
    '<td style="padding:3px 0">Kommune</td>'+(showFylke?'<td>Fylke</td>':'')+
    '<td>Status</td><td>Risiko</td>'+
    '<td style="text-align:right">NDR</td><td style="text-align:right;padding-left:8px">Fond</td>'+
    '<td style="text-align:right;padding-left:8px">Gjeld</td><td style="text-align:right;padding-left:8px">Neg.\u00e5r</td></tr>';
  const body=recs.map(r=>'<tr style="border-top:1px solid var(--line2)">'+
    '<td style="padding:4px 0;color:var(--ink);font-weight:'+(r.st?'600':'400')+'">'+r.navn+'</td>'+
    (showFylke?'<td style="color:var(--ink3);font-size:11px">'+r.fylke+'</td>':'')+
    '<td style="font-size:11px">'+stCell(r)+'</td>'+
    '<td>'+pill(r.pr.lvl)+'</td>'+
    '<td style="text-align:right;font-family:var(--font-mono);color:'+(r.pr.ndr!=null&&r.pr.ndr<0?'var(--neg)':'var(--ink2)')+'">'+fmtp(r.pr.ndr,'%')+'</td>'+
    '<td style="text-align:right;padding-left:8px;font-family:var(--font-mono);color:'+(r.pr.fond!=null&&r.pr.fond<3?'var(--neg)':'var(--ink2)')+'">'+fmtp(r.pr.fond,'%')+'</td>'+
    '<td style="text-align:right;padding-left:8px;font-family:var(--font-mono);color:'+(r.pr.gj!=null&&r.pr.gj>=110?'var(--amber)':'var(--ink2)')+'">'+fmtp(r.pr.gj,'0')+'\u2009%</td>'+
    '<td style="text-align:right;padding-left:8px;font-family:var(--font-mono);color:var(--ink3)">'+r.pr.neg+'/'+r.pr.nser+'</td></tr>').join('');
  const crit='<details style="margin:12px 0 0;padding-top:10px;border-top:1px solid var(--line2)">'+
    '<summary style="cursor:pointer;font-weight:600;color:var(--ink2);font-size:12.5px">Hva utl\u00f8ser ROBEK? (kommuneloven \u00a728-1)</summary>'+
    '<p class="hint" style="margin:6px 0 0;font-size:11.5px">Minst ett objektivt vilkår m\u00e5 ha inntruffet: '+
    '<b>a)</b> driftsbudsjett vedtatt med merforbruk \u00b7 <b>b)</b> \u00f8konomiplanens driftsdel vedtatt med merforbruk \u00b7 '+
    '<b>c)</b> merforbruk som dekkes inn over mer enn to \u00e5r \u00b7 <b>d)</b> oppsamlet merforbruk &gt; <b>3 % av driftsinntektene</b> \u00b7 '+
    '<b>e/f)</b> plan/budsjett/regnskap ikke vedtatt innen frist. Nasjonale kriterier; '+sf(fylke)+' f\u00f8rer kontrollen p\u00e5 vegne av KDD.</p></details>';
  return '<div class="card"><div class="ch"><h3 class="serif">'+headerTitle+'</h3></div>'+
    '<p class="hint">Faktisk registerstatus per <b>'+RB.oppdatert+'</b> (kilde: '+RB.kilde+'), satt mot den kalibrerte risikoindikatoren p\u00e5 KOSTRA-fundamentene for alle '+inF.length+' kommuner i '+scopeText+'.</p>'+
    '<div style="display:flex;flex-wrap:wrap;gap:18px;align-items:baseline;margin:8px 0 4px">'+
    '<div><span style="font-family:var(--font-display);font-size:28px;font-weight:600;color:'+(reg.length?'var(--neg)':'var(--pos)')+'">'+reg.length+'</span> <span style="color:var(--ink2);font-size:12.5px">i ROBEK ('+pctv.toFixed(0).replace('.',',')+' %)</span></div>'+
    (pendF.length?'<div><span style="font-family:var(--font-display);font-size:28px;font-weight:600;color:var(--amber)">'+pendF.length+'</span> <span style="color:var(--ink2);font-size:12.5px">over grensen (behandles)</span></div>':'')+
    '<div style="font-size:11.5px;color:var(--ink2)">Indikator: <b style="color:'+LC[3]+'">'+dist[3]+'</b> H\u00f8y \u00b7 <b style="color:'+LC[2]+'">'+dist[2]+'</b> Forh\u00f8yet \u00b7 <b style="color:'+LC[1]+'">'+dist[1]+'</b> Moderat \u00b7 <b style="color:'+LC[0]+'">'+dist[0]+'</b> Lav</div></div>'+
    '<div class="minseg" id="rbk" style="margin:6px 0 4px">'+seg('risk','Risiko')+seg('status','Status')+seg('navn','Navn')+(showFylke?seg('fylke','Fylke'):'')+'</div>'+
    '<div style="max-height:460px;overflow:auto;border:1px solid var(--line2);border-radius:0;padding:2px 10px"><table style="width:100%;border-collapse:collapse;font-size:11.5px"><thead style="position:sticky;top:0;background:var(--paper2)">'+head+'</thead><tbody>'+body+'</tbody></table></div>'+
    '<p class="hint" style="margin:6px 0 0;font-size:11px">Sorter med knappene over. <b>Risiko</b> = kalibrert indikator: disposisjonsfond (tyngst vektet \u2014 direkte utl\u00f8sende for bokstav d), driftsresultat, kronisk svakhet, l\u00e5negjeld kun som svak forsterker. Ikke de juridiske vilkårene.</p>'+
    crit+
    '<p class="hint" style="margin:10px 0 0;font-size:11px;opacity:.75">Kalibrert mot fasiten: '+recs.filter(r=>r.st>0&&r.pr.lvl>=2).length+' av '+recs.filter(r=>r.st>0).length+' kommuner i/over ROBEK i '+scopeText+' fanges (Forh\u00f8yet/H\u00f8y). Indikatoren overvarsler fortsatt bevisst \u2014 mange kommuner har reelt svake fundamenter, men unng\u00e5r registeret ved \u00e5 saldere budsjettet (vilkår a\u2013c er vedtak, ikke n\u00f8kkeltall). Registerstatus er et \u00f8yeblikksbilde og endres l\u00f8pende.</p></div>';
}
function robekCard(k){
  const P=DATA.proj; if(!P||!P.robek) return '';
  const RB=P.robek, isA=k.isAgg;
  const sf=(f)=>'Statsforvalteren i '+(f==='Alle'?'fylket':(f==='Troms'||f==='Finnmark')?'Troms og Finnmark':f);
  const crit='<details style="margin:12px 0 0;padding-top:10px;border-top:1px solid var(--line2)">'+
    '<summary style="cursor:pointer;font-weight:600;color:var(--ink2);font-size:12.5px">Hva utl\u00f8ser ROBEK? (kommuneloven \u00a728-1)</summary>'+
    '<p class="hint" style="margin:6px 0 0;font-size:11.5px">Registrering er <b>ikke skj\u00f8nn</b> \u2014 minst ett objektivt vilkår m\u00e5 ha inntruffet: '+
    '<b>a)</b> driftsbudsjettet vedtatt med merforbruk \u00b7 <b>b)</b> driftsdelen i \u00f8konomiplanen vedtatt med merforbruk \u00b7 '+
    '<b>c)</b> merforbruk som skal dekkes inn over mer enn to \u00e5r \u00b7 <b>d)</b> oppsamlet merforbruk &gt; <b>3 % av driftsinntektene</b> \u00b7 '+
    '<b>e/f)</b> \u00f8konomiplan/budsjett/regnskap ikke vedtatt innen frist. Kriteriene er nasjonale (samme i alle fylker); '+sf(isA?k.fylke:k.fylke)+' f\u00f8rer kontrollen p\u00e5 vegne av Kommunal- og distriktsdepartementet. '+
    'Konsekvens: l\u00e5neopptak, budsjett og lange leieavtaler m\u00e5 godkjennes.</p></details>';

  if(isA){ return robekOverviewHTML(k.fylke); }

  const letters=RB.kommuner[k.nr];
  const pr=robekProxy(k.nr);
  const ndr=pr.ndr, fond=pr.fond, gj=pr.gj, bdr=pr.bdr, yr=pr.yr, neg=pr.neg;
  const ndrs={length:pr.nser};
  const pts=pr.pts, lvl=pr.lvl;
  const LV=['Lav','Moderat','Forh\u00f8yet','H\u00f8y'], LC=['var(--pos)','var(--cat-5)','var(--amber)','var(--neg)'];
  const gauge='<div style="display:flex;gap:4px;margin:8px 0 2px">'+LV.map((t,i)=>
    '<div style="flex:1;text-align:center"><div style="height:8px;border-radius:0;background:'+(i<=lvl?LC[lvl]:'var(--line2)')+'"></div>'+
    '<div style="font-size:10.5px;margin-top:3px;font-weight:'+(i===lvl?'700':'400')+';color:'+(i===lvl?LC[lvl]:'var(--ink3)')+'">'+t+'</div></div>').join('')+'</div>';
  const tag=(v,bad,warn,fmtv)=> v==null?'<span style="color:var(--ink3)">\u2013</span>':
    '<b>'+fmtv+'</b> <span style="color:'+(bad?'var(--neg)':warn?'var(--amber)':'var(--pos)')+';font-size:11px">'+(bad?'\u25cf':warn?'\u25cf':'\u25cf')+'</span>';
  const rows=[
    ['Netto driftsresultat'+(yr?' ('+yr+')':''), tag(ndr,ndr!=null&&ndr<0,ndr!=null&&ndr<1.75,(ndr==null?'':(ndr<0?'\u2212':'')+Math.abs(ndr).toFixed(1).replace('.',',')+'\u2009%')), 'TBU-norm +1,75 %'],
    ['\u00c5r med negativt resultat', '<b>'+neg+'</b> av '+ndrs.length+' siste \u00e5r', '\u22655 \u00e5r = kronisk (tungt vektet)'],
    ['Disposisjonsfond', tag(fond,fond!=null&&fond<3,fond!=null&&fond<5,(fond==null?'':fond.toFixed(1).replace('.',',')+'\u2009%')), 'buffer mot merforbruk \u2014 &lt;3 % kritisk (bokstav d)'],
    ['Netto l\u00e5negjeld', tag(gj,gj!=null&&gj>=160,gj!=null&&gj>=110,(gj==null?'':gj.toFixed(1).replace('.',',')+'\u2009%')), 'kun svak forsterker (ikke ROBEK-vilkår)'],
    ['Brutto driftsresultat', tag(bdr,bdr!=null&&bdr<0,false,(bdr==null?'':(bdr<0?'\u2212':'')+Math.abs(bdr).toFixed(1).replace('.',',')+'\u2009%')), 'drift uten finansposter']
  ];
  const tbl='<table style="width:100%;border-collapse:collapse;font-size:12px;margin:8px 0 0">'+rows.map(r=>
    '<tr style="border-top:1px solid var(--line2)"><td style="text-align:left;padding:4px 0;color:var(--ink2)">'+r[0]+'</td>'+
    '<td style="text-align:right;font-family:var(--font-mono)">'+r[1]+'</td>'+
    '<td style="text-align:right;padding-left:12px;color:var(--ink3);font-size:10.5px">'+r[2]+'</td></tr>').join('')+'</table>';
  const pend=(RB.pending||{})[k.nr];
  const badge=letters
    ? '<div style="background:color-mix(in srgb, var(--neg) 7%, transparent);border:1px solid color-mix(in srgb, var(--neg) 33%, transparent);border-radius:0;padding:9px 12px;margin:6px 0 4px"><b style="color:var(--neg)">Registrert i ROBEK</b> \u2014 kommuneloven \u00a728-1 bokstav <b>'+letters+'</b>. '+sf(k.fylke)+' f\u00f8rer kontroll med budsjett, l\u00e5neopptak og lange leieavtaler. Status per '+RB.oppdatert+'.</div>'
    : pend
    ? '<div style="background:color-mix(in srgb, var(--amber) 8%, transparent);border:1px solid color-mix(in srgb, var(--amber) 40%, transparent);border-radius:0;padding:9px 12px;margin:6px 0 4px"><b style="color:var(--amber)">Over ROBEK-grensen \u2014 innmelding under behandling</b> (\u00a728-1 bokstav <b>'+pend.par+'</b>). '+pend.note+' <span style="color:var(--ink3)">Kilde: '+pend.kilde+', '+pend.oppdatert+'. Ikke f\u00f8rt inn i det offisielle registeret per '+RB.oppdatert+'.</span></div>'
    : '<div style="background:color-mix(in srgb, var(--pos) 7%, transparent);border:1px solid color-mix(in srgb, var(--pos) 33%, transparent);border-radius:0;padding:9px 12px;margin:6px 0 4px"><b style="color:var(--pos)">Ikke registrert i ROBEK</b> per '+RB.oppdatert+' (kilde: '+RB.kilde+').</div>';
  const read='Fundamentene gir <b style="color:'+LC[lvl]+'">'+LV[lvl]+'</b> risiko. '+
    (letters?'Kommunen er faktisk i registeret \u2014 her bekrefter indikatoren den juridiske statusen.'
            :pend?'Kommunen er over den kvantitative grensen (bokstav d) \u2014 indikatoren fanget presset f\u00f8r registeret rakk \u00e5 vise det.'
            :(lvl>=2?'Kommunen er ikke i registeret i dag, men fundamentene viser \u00f8kende press.':'Kommunen er ikke i registeret, og fundamentene st\u00f8tter det.'));
  return '<div class="card"><div class="ch"><h3 class="serif">ROBEK \u2014 status og \u00f8konomisk risiko</h3></div>'+
    badge+
    '<p class="hint" style="margin:12px 0 0;font-size:12px">Under: risikoindikator basert p\u00e5 KOSTRA-fundamentene \u2014 tidligvarsel p\u00e5 det som <i>g\u00e5r forut for</i> ROBEK, ikke de juridiske vilkårene.</p>'+
    gauge+tbl+
    '<p style="margin:8px 0 0;font-size:12.5px;color:var(--ink)">'+read+'</p>'+
    crit+
    '<p class="hint" style="margin:10px 0 0;font-size:11px;opacity:.78">Risikonivået er en <b>gjennomsiktig indikator</b> p\u00e5 KOSTRA-fundamentene, ikke en sannsynlighet og ikke de juridiske vilkårene. Faktisk innmelding utl\u00f8ses av budsjett-/\u00f8konomiplanvedtak (a, b) og akkumulert merforbruk (c, d) som ikke kan leses ut av disse n\u00f8kkeltallene. Bokstav d \u2014 oppsamlet merforbruk &gt; 3 % av driftsinntektene \u2014 er det eneste kvantitative vilkåret; indikatoren fanger presset som leder dit (svakt driftsresultat som t\u00e6rer p\u00e5 fondet). Registerstatus er et \u00f8yeblikksbilde per '+RB.oppdatert+' og endres l\u00f8pende.</p></div>';
}
/* === status helper for badges + list === */
function kommuneStatus(k){
  const P=DATA.proj, o=P&&P.kommuner&&P.kommuner[k.nr];
  let growth='flat', growthPct=0;
  if(o&&o.main&&o.main.length){
    const a=o.main[0], b=o.main[o.main.length-1];
    growthPct=a? (b-a)/a*100 : 0;
    growth = growthPct>2 ? 'up' : growthPct<-2 ? 'down' : 'flat';
  }
  const RB=P&&P.robek;
  let robek='ok';
  if(RB){
    if(RB.kommuner&&RB.kommuner[k.nr]) robek='in';
    else if(RB.pending&&RB.pending[k.nr]) robek='pending';
  }
  const med=medianAge(k.alder);
  const aging = med<38 ? 'young' : med<43 ? 'mid' : 'old';
  return {growth, growthPct, robek, aging, med};
}
function statusBadges(k,s){
  if(k.isAgg) return '';
  const gtxt = s.growth==='up' ? '↑ vekst '+(s.growthPct>0?'+':'')+s.growthPct.toFixed(0).replace('.',',')+' %' :
               s.growth==='down' ? '↓ nedgang '+Math.abs(s.growthPct).toFixed(0).replace('.',',')+' %' :
               '→ stabilt '+(s.growthPct>0?'+':'')+s.growthPct.toFixed(0).replace('.',',')+' %';
  const rtxt = s.robek==='in' ? '● i ROBEK' :
               s.robek==='pending' ? '● ROBEK under behandling' :
               '● ikke i ROBEK';
  const atxt = s.aging==='young' ? '⬇ ung profil (median '+s.med+')' :
               s.aging==='mid' ? '● middels aldersprofil (median '+s.med+')' :
               '⬆ aldrende (median '+s.med+')';
  return '<div class="status-badges">'+
    '<span class="badge b-'+s.growth+'" title="SSB MMMM 2026\u20132050">'+gtxt+'</span>'+
    '<span class="badge b-robek-'+(s.robek==='in'?'in':s.robek==='pending'?'pend':'ok')+'" title="ROBEK-status">'+rtxt+'</span>'+
    '<span class="badge b-age-'+s.aging+'" title="Medianalder i dag">'+atxt+'</span>'+
  '</div>';
}
/* Pre-beregner rang i landsdelen for median husholdningsinntekt */
let _inntektRangCache=null;
function inntektRang(nr){
  if(!_inntektRangCache && typeof LEVEKAR_DATA!=='undefined'){
    const arr=[];
    Object.entries(LEVEKAR_DATA.kommuner).forEach(([n,r])=>{
      if(r.medianInntektEtterSkatt) arr.push({nr:n, m:r.medianInntektEtterSkatt});
    });
    arr.sort((a,b)=>b.m-a.m);
    _inntektRangCache={};
    arr.forEach((x,i)=>{ _inntektRangCache[x.nr] = {rang:i+1, total:arr.length}; });
  }
  return _inntektRangCache ? (_inntektRangCache[String(nr)]||null) : null;
}

function levekarKommuneCard(k){
  if(typeof LEVEKAR_DATA==='undefined') return '';
  const r = LEVEKAR_DATA.kommuner[String(k.nr)];
  if(!r) return '';
  const fmt0 = n => n==null ? '–' : (n>=1e6?(n/1e6).toFixed(2).replace('.',',')+' mill':(n>=1000?Math.round(n).toLocaleString('nb-NO'):Math.round(n)));
  const rang = inntektRang(k.nr);
  // Landsdelens vektede median for sammenligning
  let sumW=0, sumMW=0;
  Object.values(LEVEKAR_DATA.kommuner).forEach(x=>{
    if(x.medianInntektEtterSkatt && x.hush_total){ sumMW += x.medianInntektEtterSkatt * x.hush_total; sumW += x.hush_total; }
  });
  const landsdelMed = sumW ? sumMW/sumW : null;
  const NORGE_MED = 676100; // SSB 06944, hele landet, alle husholdninger, inntekt etter skatt, median 2024
  const diffLandsdel = (r.medianInntektEtterSkatt && landsdelMed) ? (r.medianInntektEtterSkatt/landsdelMed-1)*100 : null;
  const diffNorge = r.medianInntektEtterSkatt ? (r.medianInntektEtterSkatt/NORGE_MED-1)*100 : null;
  // Personinntekt-sammensetning
  const totL=r.totalLonn_mill||0, totP=r.totalPensjon_mill||0, totU=r.totalUfore_mill||0;
  const sumK = totL+totP+totU;
  const pctL = sumK?totL/sumK*100:0, pctP = sumK?totP/sumK*100:0, pctU = sumK?totU/sumK*100:0;
  // Boliger
  const bolTot = r.boliger_total||0;
  const eneP = bolTot ? r.boliger_enebolig/bolTot*100 : 0;
  const blokkP = bolTot ? r.boliger_boligblokk/bolTot*100 : 0;
  return '<div class="card">'+
    '<div class="ch"><h3 class="serif">Levekår og inntekt</h3></div>'+
    '<p class="hint">Hva tjener husholdningene i '+k.navn+', hvor kommer pengene fra, hvordan bor de? Kilder: SSB 06944 (inntekt 2024), 14780 (personinntekt 2025), 14891 (eierstatus 2025), 06265 (boliger 2026).</p>'+
    '<div class="kpis" style="margin-top:14px">'+
      '<div class="kpi"><div class="v">'+(r.medianInntektEtterSkatt?fmt(Math.round(r.medianInntektEtterSkatt/1000))+' 000':'–')+'</div><div class="l">Median hush.-inntekt</div><div class="s">etter skatt'+(diffLandsdel!=null?' · '+(diffLandsdel>=0?'+':'−')+Math.abs(diffLandsdel).toFixed(0).replace('.',',')+' % mot landsdelen':'')+'</div></div>'+
      '<div class="kpi"><div class="v">'+fmt0(r.hush_total)+'</div><div class="l">Husholdninger</div><div class="s">'+(r.pct_selveier!=null?r.pct_selveier.toFixed(0).replace('.',',')+' % selveiere':'')+'</div></div>'+
      '<div class="kpi"><div class="v">'+fmt0(bolTot)+'</div><div class="l">Boliger</div><div class="s">'+eneP.toFixed(0).replace('.',',')+' % enebolig · '+blokkP.toFixed(0).replace('.',',')+' % blokk</div></div>'+
      (rang?'<div class="kpi"><div class="v">'+rang.rang+'</div><div class="l">Rang i Nord-Norge</div><div class="s">av '+rang.total+' kommuner, høyest inntekt = 1</div></div>':'')+
    '</div>'+
    (sumK?
      '<div class="origin-section">'+
        '<h3 class="serif" style="font-size:15px;font-weight:600;margin-bottom:6px">Hvor kommer personinntekten fra?</h3>'+
        '<p class="hint" style="font-size:12px">Lønn, pensjon og uføretrygd som andel av samlet personinntekt for bosatte 17+ år. Totalt '+(sumK>1000?(sumK/1000).toFixed(1).replace('.',',')+' milliarder kroner':sumK.toFixed(0).replace('.',',')+' millioner kroner')+'.</p>'+
        '<div class="split" style="margin:8px 0">'+
          '<div style="width:'+pctL.toFixed(1)+'%;background:var(--aurora);color:#fff;font-weight:700;font-size:12px;display:flex;align-items:center;justify-content:center">'+(pctL>=8?pctL.toFixed(0).replace('.',',')+' %':'')+'</div>'+
          '<div style="width:'+pctP.toFixed(1)+'%;background:var(--nl);color:#fff;font-weight:700;font-size:12px;display:flex;align-items:center;justify-content:center">'+(pctP>=8?pctP.toFixed(0).replace('.',',')+' %':'')+'</div>'+
          '<div style="width:'+pctU.toFixed(1)+'%;background:var(--amber);color:#fff;font-weight:700;font-size:12px;display:flex;align-items:center;justify-content:center">'+(pctU>=8?pctU.toFixed(0).replace('.',',')+' %':'')+'</div>'+
        '</div>'+
        '<div class="legend">'+
          '<span><i style="background:var(--aurora)"></i>Lønn '+pctL.toFixed(0).replace('.',',')+' %</span>'+
          '<span><i style="background:var(--nl)"></i>Pensjon '+pctP.toFixed(0).replace('.',',')+' %</span>'+
          '<span><i style="background:var(--amber)"></i>Uføretrygd '+pctU.toFixed(0).replace('.',',')+' %</span>'+
        '</div>'+
      '</div>'
    :'')+
  '</div>';
}

function originCard(k,vesP,iveP,lands,shown){
  return '<div class="card">'+
    '<h3 class="serif">Opprinnelse — vestlig/ikke-vestlig og land</h3>'+
    '<p class="hint">Av '+fmt(k.bc)+' med innvandrerbakgrunn (innvandrere + norskfødte med innvandrerforeldre).</p>'+
    '<div class="split">'+
      '<div class="v" style="width:'+vesP+'%">'+(vesP>8?vesP+' %':'')+'</div>'+
      '<div class="i" style="width:'+iveP+'%">'+(iveP>8?iveP+' %':'')+'</div></div>'+
    '<div class="legend"><span><i style="background:var(--nl)"></i>Vestlig · '+fmt(k.ves)+'</span>'+
      '<span><i style="background:var(--amber)"></i>Ikke-vestlig · '+fmt(k.ive)+'</span></div>'+
    '<div class="origin-section">'+
      '<div class="ch" style="margin-bottom:4px"><h3 class="serif" style="font-size:16px">Opprinnelsesland</h3>'+
        '<input class="csearch" id="cs" placeholder="søk land …" value="'+state.csearch+'"></div>'+
      '<p class="hint">Enkeltland, sortert. Tabell 09817. '+lands.length+' land med registrerte personer.</p>'+
      (!state.csearch?'<div class="cslider"><span>Vis topp</span>'+
        '<input id="tn" type="range" min="5" max="'+Math.max(5,Math.min(40,k.land.filter(l=>l[1]>0).length))+'" value="'+state.topN+'">'+
        '<span class="mono" id="tnv">'+state.topN+'</span></div><div style="height:10px"></div>':'')+
      (shown.length?barChart(shown.map(l=>({l:l[0],v:l[1]})),'var(--amber)'):'<p class="hint">Ingen treff.</p>')+
    '</div>'+
  '</div>';
}
/* === klartekst-banner per linse === */
function tldrBanner(k, view){
  const P=DATA.proj, o=P&&P.kommuner&&P.kommuner[k.nr];
  const fmt0=v=>v==null?'–':fmt(Math.round(v));
  const pctF=v=>(v>=0?'+':'−')+Math.abs(v).toFixed(0).replace('.',',')+' %';
  if(view==='history'){
    const hist=k.hist||{};
    const histKeys=Object.keys(hist).map(Number).sort((a,b)=>a-b);
    const firstY=histKeys.length?histKeys[0]:null;
    const firstV=firstY?hist[firstY]:null;
    const lastY=histKeys.length?histKeys[histKeys.length-1]:null;
    const lastV=lastY?hist[lastY]:null;
    const pastPct=(firstV&&lastV)?((lastV/firstV-1)*100):null;
    let projHi=null, projLo=null, projMain=null, projYear=null;
    if(o&&o.main&&o.main.length){
      const n=o.main.length;
      projMain=o.main[n-1];
      // Spennet skal dekke alle banene i begge ender — tidligere manglet to av
      // de tre TF-MVP-vinduene, slik at gulvet ble oppgitt for høyt.
      const baner=[o.main[n-1]];
      ['kons','sentral','opt'].forEach(w=>{ if(o.mw&&o.mw[w]&&o.mw[w].pop) baner.push(o.mw[w].pop[n-1]); });
      if(o.tfattr) baner.push(o.tfattr[n-1]);
      if(o.high) baner.push(o.high[n-1]);
      if(o.low) baner.push(o.low[n-1]);
      projHi=Math.max.apply(null,baner); projLo=Math.min.apply(null,baner);
      projYear=(P.years||[])[n-1]||2050;
    }
    const futurePct=(k.pop&&projMain)?((projMain/k.pop-1)*100):null;
    let text='';
    if(firstY&&lastY&&pastPct!=null){
      text+='<b>'+k.navn+'</b> '+(pastPct>=0?'vokste':'gikk ned')+' fra <b>'+fmt0(firstV)+'</b> ('+firstY+') til <b>'+fmt0(lastV)+'</b> ('+lastY+') — <b>'+pctF(pastPct)+'</b> på '+((+lastY)-(+firstY))+' år. ';
    } else {
      text+='<b>'+k.navn+'</b> har <b>'+fmt0(k.pop)+'</b> innbyggere i dag. ';
    }
    if(projMain){
      text+='SSB MMMM peker mot <b>'+fmt0(projMain)+'</b> i '+projYear+' ('+pctF(futurePct)+' fra i dag). ';
      if(projLo&&projHi&&projHi-projLo>50) text+='Banene spriker fra <b>'+fmt0(projLo)+'</b> til <b>'+fmt0(projHi)+'</b> avhengig av flytteforutsetning. ';
    }
    text+='<i>Det er flyttingen som skiller tilleggsbanene fra SSBs hovedalternativ; fødsler og dødsfall regnes likt i dem.</i>';
    const nums=[];
    if(firstV&&lastV) nums.push({nv:pctF(pastPct),cls:pastPct>=0?'up':'down',nl:'siden '+firstY,nh:firstY+' → '+lastY});
    nums.push({nv:fmt0(k.pop),cls:'',nl:'i dag',nh:'1.1.2026'});
    if(projMain&&futurePct!=null) nums.push({nv:pctF(futurePct),cls:futurePct>=0?'up':'down',nl:'mot '+projYear,nh:'SSB MMMM'});
    return '<div class="tldr">'+
      '<div class="tldr-tag">Seksjon 1 · Befolkning 2000–2050</div>'+
      '<h3>Hva har skjedd — og hva kan komme?</h3>'+
      '<p class="tldr-text">'+text+'</p>'+
      '<div class="tldr-nums">'+nums.map(n=>'<div class="tldr-num"><div class="nv '+n.cls+'">'+n.nv+'</div><div class="nl">'+n.nl+'</div><div class="nh">'+n.nh+'</div></div>').join('')+'</div>'+
    '</div>';
  }
  if(view==='people'){
    const med=medianAge(k.alder);
    const barn=k.alder.slice(0,18).reduce((a,b)=>a+b,0);
    const eldre=k.alder.slice(67).reduce((a,b)=>a+b,0);
    const pctBarn=k.pop?100*barn/k.pop:0;
    const pctEldre=k.pop?100*eldre/k.pop:0;
    const pctInnv=k.andel||0;
    const ageWord = med<38?'ung':med<43?'moderat':'aldrende';
    let text='Medianalderen er <b>'+med+' år</b> — en '+ageWord+' kommune. <b>'+pctBarn.toFixed(0).replace('.',',')+' %</b> er under 18 år, mens <b>'+pctEldre.toFixed(0).replace('.',',')+' %</b> har passert 67. ';
    text+='<b>'+pctInnv.toFixed(1).replace('.',',')+' %</b> har innvandrerbakgrunn (vestlig + ikke-vestlig). ';
    text+='<i>Aldringen i dag er forhåndsvarselet for press på omsorg og bemanning de neste tjue årene.</i>';
    return '<div class="tldr t-people">'+
      '<div class="tldr-tag">Seksjon 2 · Sammensetning</div>'+
      '<h3>Hvem bor her nå?</h3>'+
      '<p class="tldr-text">'+text+'</p>'+
      '<div class="tldr-nums">'+
        '<div class="tldr-num"><div class="nv">'+med+'</div><div class="nl">Medianalder</div><div class="nh">år</div></div>'+
        '<div class="tldr-num"><div class="nv '+(pctBarn>22?'up':pctBarn<18?'down':'')+'">'+pctBarn.toFixed(0).replace('.',',')+' %</div><div class="nl">0–17 år</div><div class="nh">'+fmt(barn)+' personer</div></div>'+
        '<div class="tldr-num"><div class="nv '+(pctEldre>20?'warn':pctEldre>17?'':'up')+'">'+pctEldre.toFixed(0).replace('.',',')+' %</div><div class="nl">67+ år</div><div class="nh">'+fmt(eldre)+' personer</div></div>'+
        '<div class="tldr-num"><div class="nv">'+pctInnv.toFixed(1).replace('.',',')+' %</div><div class="nl">Innvandrerbakgrunn</div><div class="nh">'+fmt(k.bc)+' personer</div></div>'+
      '</div>'+
    '</div>';
  }
  if(view==='burden'){
    const a6=o?o.a65:null, a2=o?o.a2064:null;   // SSB MMMM — hovedbane
    const n=(P.years||[]).length;
    const oad0=(a6&&a2&&a2[0])?100*a6[0]/a2[0]:null;
    const oad1=(a6&&a2&&a2[n-1])?100*a6[n-1]/a2[n-1]:null;
    const isA=k.isAgg;
    const ks=isA?((P.kostra_bench||{})[k.fylke]||(P.kostra_bench||{})['Alle']):((P.kostra||{})[k.nr]);
    const num=v=>v==null?null:+v;
    const ndr=ks?num(ks.ndr):null, fond=ks?num(ks.fond):null, gj=ks?num(ks.gjeld):null;
    const RB=P.robek||{kommuner:{}}; const inRobek=!isA&&RB.kommuner&&RB.kommuner[k.nr];
    const pending=!isA&&(RB.pending||{})[k.nr];
    const robekTxt=inRobek?'I ROBEK (bokstav '+inRobek+')':pending?'over grensen — under behandling':'ikke i ROBEK';
    let text='';
    if(oad0!=null&&oad1!=null){
      text+='I dag er det <b>'+oad0.toFixed(0).replace('.',',')+'</b> innbyggere 65 år og eldre per 100 i alderen 20–64. I 2050 er tallet <b>'+oad1.toFixed(0).replace('.',',')+'</b> ('+(oad1>=oad0?'opp':'ned')+' fra '+oad0.toFixed(0).replace('.',',')+') — '+(oad1>oad0?'en tyngre bør':'fortsatt bærbart')+'. ';
    }
    if(fond!=null){
      const fondGrade=fond<3?'<b style="color:var(--neg)">kritisk lav</b>':fond<5?'<b style="color:var(--amber)">tynn</b>':fond<10?'akseptabel':'<b style="color:var(--aurora)">solid</b>';
      text+='Disposisjonsfondet er '+fondGrade+' på <b>'+fond.toFixed(1).replace('.',',')+' %</b> av driftsinntektene. ';
    }
    if(ndr!=null){
      text+='Netto driftsresultat: <b>'+(ndr>=0?'+':'−')+Math.abs(ndr).toFixed(1).replace('.',',')+' %</b> (TBU-norm +1,75). ';
    }
    text+='ROBEK-status: <b'+(inRobek?' style="color:var(--neg)"':pending?' style="color:var(--amber)"':' style="color:var(--aurora)"')+'>'+robekTxt+'</b>. ';
    text+='<i>Hvor tungt blir aldringen å bære for kommunens budsjett?</i>';
    return '<div class="tldr t-burden">'+
      '<div class="tldr-tag">Seksjon 3 · Arbeid og forsørgerbyrde</div>'+
      '<h3>Hva betyr demografien for kommuneøkonomien?</h3>'+
      '<p class="tldr-text">'+text+'</p>'+
      '<div class="tldr-nums">'+
        (oad1!=null?'<div class="tldr-num"><div class="nv '+(oad1>40?'warn':'')+'">'+oad1.toFixed(0).replace('.',',')+'</div><div class="nl">Forsørgerbrøk 2050</div><div class="nh">65+ per 100 i alderen 20–64</div></div>':'')+
        (fond!=null?'<div class="tldr-num"><div class="nv '+(fond<3?'down':fond<5?'warn':'up')+'">'+fond.toFixed(1).replace('.',',')+' %</div><div class="nl">Disposisjonsfond</div><div class="nh">av driftsinntekter</div></div>':'')+
        (ndr!=null?'<div class="tldr-num"><div class="nv '+(ndr<0?'down':ndr<1.75?'warn':'up')+'">'+(ndr>=0?'+':'−')+Math.abs(ndr).toFixed(1).replace('.',',')+' %</div><div class="nl">Netto driftsresultat</div><div class="nh">TBU-norm +1,75</div></div>':'')+
        '<div class="tldr-num"><div class="nv '+(inRobek?'down':pending?'warn':'up')+'">'+(inRobek?'I':pending?'●':'●')+'</div><div class="nl">ROBEK-status</div><div class="nh">'+robekTxt+'</div></div>'+
      '</div>'+
    '</div>';
  }
  return '';
}
function detail(){
  if(!elDet) return;
  const k=resolveSel();
  if(!k){elDet.innerHTML='<div class="empty"><div class="big serif">Ingen treff</div>Juster søk eller fylke.</div>';return;}
  const med=medianAge(k.alder);
  const barn=k.alder.slice(0,18).reduce((a,b)=>a+b,0);
  const eldre=k.alder.slice(67).reduce((a,b)=>a+b,0);
  const vesP=k.bc?Math.round(k.ves/k.bc*100):0, iveP=100-vesP;
  let lands=k.land.filter(l=>l[1]>0);
  if(state.csearch) lands=lands.filter(l=>l[0].toLowerCase().includes(state.csearch.toLowerCase()));
  const shown=lands.slice(0,state.csearch?lands.length:state.topN);
  const sj=k.syss, sjr=sj?sj.rate:null;
  const sjVal=sjr&&sjr.zzz!=null?sjr.zzz.toFixed(1).replace('.',',')+' %':'–';
  const sjGap=(sjr&&sjr.zzz!=null&&sjr.tot!=null)?(sjr.tot-sjr.zzz).toFixed(1).replace('.',','):null;
  const st=kommuneStatus(k);
  const flist=filtered(); const fi=flist.findIndex(x=>x.nr===k.nr);
  const hasPrev=fi>0, hasNext=fi>=0&&fi<flist.length-1;
  const view=state.kView||'history';
  const inCmp=state.compare.includes(k.nr);

  const heroHTML='<div class="khero">'+
    '<div class="khero-row">'+
      '<button class="khero-nav" data-knav="prev" '+(hasPrev?'':'disabled')+' title="Forrige kommune">←</button>'+
      '<div class="khero-id"><h2>'+k.navn+'</h2>'+
      '<span class="fy" style="background:transparent;color:'+(FY[k.fylke]||'var(--ink2)')+';border:1px solid '+(FY[k.fylke]||'var(--ink2)')+'44;padding:3px 10px">'+(k.isAgg?k.naggk+' kommuner':k.fylke)+'</span></div>'+
      '<div class="khero-actions">'+(k.isAgg?'':'<button class="khero-cmp '+(inCmp?'on':'')+'" data-knav="cmp" title="Sammenlign">'+(inCmp?'● i sammenligning':'+ sammenlign')+'</button>')+'</div>'+
      '<button class="khero-nav" data-knav="next" '+(hasNext?'':'disabled')+' title="Neste kommune">→</button>'+
    '</div>'+
    statusBadges(k,st)+
    (k.isAgg?'<p class="hint" style="margin:-2px 0 12px">Aggregerte tall for '+(k.fylke==='Alle'?'hele landsdelen':k.fylke)+' — klikk en kommune i listen for kommunetall.</p>':'')+
    '<div class="kpis">'+
      popKpi(k, k.isAgg?k.naggk+' kommuner · ':'')+
      '<div class="kpi"><div class="v">'+k.andel.toFixed(1).replace('.',',')+' %</div><div class="l">Innvandrerbakgrunn</div><div class="s">'+fmt(k.bc)+' personer</div></div>'+
      '<div class="kpi"><div class="v">'+med+'</div><div class="l">Medianalder</div><div class="s">år</div></div>'+
      '<div class="kpi"><div class="v">'+(barn/k.pop*100).toFixed(0).replace('.',',')+'/'+(eldre/k.pop*100).toFixed(0).replace('.',',')+'</div><div class="l">0–17 / 67+ %</div><div class="s">'+fmt(barn)+' / '+fmt(eldre)+'</div></div>'+
      '<div class="kpi"><div class="v" style="color:var(--syss)">'+sjVal+'</div><div class="l">Sysselsatt · innv.</div><div class="s">'+(sjGap!=null?(sjGap.charAt(0)==='-'?sjGap.slice(1)+' prosentpoeng over hele bef.':sjGap+' prosentpoeng under hele bef.'):'20–66 år, 2025')+'</div></div>'+
    '</div>'+
  '</div>';

  const subnavHTML='<nav class="ksubtabs" role="tablist">'+
    '<button role="tab" data-kview="history" aria-selected="'+(view==='history')+'"><span class="ksn">01</span>Reisen 2000\u20132050</button>'+
    '<button role="tab" data-kview="people" aria-selected="'+(view==='people')+'"><span class="ksn">02</span>Folket i dag</button>'+
    '<button role="tab" data-kview="burden" aria-selected="'+(view==='burden')+'"><span class="ksn">03</span>Hva må kommunen bære?</button>'+
  '</nav>';

  let viewHTML='';
  if(view==='history'){
    // Seksjon 1: befolkningen over tid + framskriving + drivkrefter
    const savedMode=state.projMode;
    state.projMode='tot';
    const histChart=projCard(k);
    state.projMode=savedMode;
    viewHTML=tldrBanner(k,'history')+
      '<div class="hero-chart">'+histChart+'</div>'+
      diagnoseCard(k);
  } else if(view==='people'){
    // Seksjon 2: alder + opprinnelse + sysselsetting
    viewHTML=tldrBanner(k,'people')+
      '<div class="card">'+
        '<div class="ch"><h3 class="serif">Aldersstruktur i dag</h3>'+
          '<div class="minseg" id="agm">'+
            '<button data-m="1" aria-selected="'+(state.ageMode==='1')+'">Ettårig</button>'+
            '<button data-m="5" aria-selected="'+(state.ageMode==='5')+'">5-årig</button>'+
            '<button data-m="L" aria-selected="'+(state.ageMode==='L')+'">Livsfaser</button>'+
          '</div></div>'+
        '<p class="hint">Folketall 1.1.2026 etter alder (SSB tabell 07459). Medianalder '+med+' år. Aldersfordeling publiseres bare per 1. januar — derfor 1.1.2026 her, mens folketallet ellers vises per '+(typeof BEFK_DATA!=='undefined'?BEFK_DATA.dato_norsk:'1. juli 2026')+'.</p>'+
        barChart(ageGroups(k.alder,state.ageMode==='1'?'1':state.ageMode==='5'?'5':'L'),'var(--aurora)')+
      '</div>'+
      originCard(k,vesP,iveP,lands,shown)+
      (sj? sysCard(sj) : '')+
      levekarKommuneCard(k);
  } else if(view==='burden'){
    // Seksjon 3: bærekrafts-sammenstilling → forsørgerbyrde → KOSTRA → ROBEK
    const savedMode=state.projMode;
    state.projMode='fb';
    const fbChart=projCard(k);
    state.projMode=savedMode;
    viewHTML=tldrBanner(k,'burden')+
      sustKommuneCard(k)+
      '<div class="hero-chart">'+fbChart+'</div>'+
      kostraCard(k)+
      robekCard(k);
  }

  elDet.innerHTML = heroHTML + subnavHTML + '<div class="kview">'+viewHTML+'</div>';
  bindDetail();
}
function _oldDetailUnused(){
  const k=resolveSel();
  if(!k){elDet.innerHTML='<div class="empty"><div class="big serif">Ingen treff</div>Juster søk eller fylke.</div>';return;}
  const med=medianAge(k.alder), barn=k.alder.slice(0,18).reduce((a,b)=>a+b,0),
    eldre=k.alder.slice(67).reduce((a,b)=>a+b,0);
  const vesP=k.bc?Math.round(k.ves/k.bc*100):0, iveP=100-vesP;
  let lands=k.land.filter(l=>l[1]>0);
  if(state.csearch) lands=lands.filter(l=>l[0].toLowerCase().includes(state.csearch.toLowerCase()));
  const shown=lands.slice(0,state.csearch?lands.length:state.topN);
  const sj=k.syss, sjr=sj?sj.rate:null;
  const sjVal=sjr&&sjr.zzz!=null?sjr.zzz.toFixed(1).replace('.',',')+' %':'–';
  const sjGap=(sjr&&sjr.zzz!=null&&sjr.tot!=null)?(sjr.tot-sjr.zzz).toFixed(1).replace('.',','):null;
  const st=kommuneStatus(k);
  const flist=filtered(); const fi=flist.findIndex(x=>x.nr===k.nr);
  const hasPrev=fi>0, hasNext=fi>=0&&fi<flist.length-1;
  const view=state.kView||'history';
  const inCmp=state.compare.includes(k.nr);
  const heroNav='<div class="khero-row">'+
    '<button class="khero-nav" data-knav="prev" '+(hasPrev?'':'disabled')+' title="Forrige kommune">\u2190</button>'+
    '<div class="khero-id"><h2>'+k.navn+'</h2>'+
    '<span class="fy" style="background:'+(FY[k.fylke]||'var(--ink2)')+'">'+(k.isAgg?k.naggk+' kommuner':k.fylke)+'</span></div>'+
    '<div class="khero-actions">'+(k.isAgg?'':'<button class="khero-cmp '+(inCmp?'on':'')+'" data-knav="cmp" title="Sammenlign">'+(inCmp?'\u2713 i sammenligning':'+ sammenlign')+'</button>')+'</div>'+
    '<button class="khero-nav" data-knav="next" '+(hasNext?'':'disabled')+' title="Neste kommune">\u2192</button>'+
  '</div>';
  elDet.innerHTML='<div class="khero">'+heroNav+statusBadges(k,st)+
  (k.isAgg?'<p class="hint" style="margin:-2px 0 12px">Aggregerte tall for '+(k.fylke==='Alle'?'hele landsdelen':k.fylke)+' \u2014 klikk en kommune i listen for kommunetall. Folketall/alder/innvandring/framskriving er summer; andeler og sysselsettingsrater er folkemengde-vektede.</p>':'')
  +`
  <div class="kpis">
    ${popKpi(k, k.isAgg?k.naggk+' kommuner \u00b7 ':'')}
    <div class="kpi"><div class="v">${k.andel.toFixed(1).replace('.',',')}%</div><div class="l">Innvandrerbakgrunn</div><div class="s">${fmt(k.bc)} personer</div></div>
    <div class="kpi"><div class="v">${med}</div><div class="l">Medianalder</div><div class="s">år</div></div>
    <div class="kpi"><div class="v">${(barn/k.pop*100).toFixed(0).replace('.',',')}/${(eldre/k.pop*100).toFixed(0).replace('.',',')}</div><div class="l">0-17 / 67+ %</div><div class="s">${fmt(barn)} / ${fmt(eldre)}</div></div>
    <div class="kpi"><div class="v" style="color:var(--syss)">${sjVal}</div><div class="l">Sysselsatt · innv.</div><div class="s">${sjGap!=null?(sjGap.charAt(0)==='-'?sjGap.slice(1)+' prosentpoeng over hele bef.':sjGap+' prosentpoeng under hele bef.'):'20–66 år, 2025'}</div></div>
  </div>

  ${diagnoseCard(k)}

  <div class="card">
    <div class="ch"><h3 class="serif">Aldersstruktur</h3>
      <div class="minseg" id="agm">
        <button data-m="1" aria-selected="${state.ageMode==='1'}">Ettårig</button>
        <button data-m="5" aria-selected="${state.ageMode==='5'}">5-årig</button>
        <button data-m="L" aria-selected="${state.ageMode==='L'}">Livsfaser</button>
      </div></div>
    <p class="hint">Hele befolkningen (tabell 07459). Medianalder ${med} år.</p>
    ${barChart(ageGroups(k.alder,state.ageMode==='1'?'1':state.ageMode==='5'?'5':'L'),'var(--aurora)')}
  </div>

  ${projCard(k)}

  ${kostraCard(k)}

  ${robekCard(k)}

  <div class="card">
    <h3 class="serif">Vestlig vs. ikke-vestlig bakgrunn</h3>
    <p class="hint">Av ${fmt(k.bc)} med innvandrerbakgrunn (innvandrere + norskfødte med innvandrerforeldre).</p>
    <div class="split">
      <div class="v" style="width:${vesP}%">${vesP>8?vesP+' %':''}</div>
      <div class="i" style="width:${iveP}%">${iveP>8?iveP+' %':''}</div></div>
    <div class="legend"><span><i style="background:var(--nl)"></i>Vestlig · ${fmt(k.ves)}</span>
      <span><i style="background:var(--amber)"></i>Ikke-vestlig · ${fmt(k.ive)}</span></div>
  </div>

  ${sj? sysCard(sj) : ''}

  <div class="card">
    <div class="ch"><h3 class="serif">Opprinnelsesland</h3>
      <input class="csearch" id="cs" placeholder="søk land …" value="${state.csearch}"></div>
    <p class="hint">Enkeltland, sortert. Tabell 09817. ${lands.length} land med registrerte personer.</p>
    ${!state.csearch?`<div class="cslider"><span>Vis topp</span>
      <input id="tn" type="range" min="5" max="${Math.max(5,Math.min(40,k.land.filter(l=>l[1]>0).length))}" value="${state.topN}">
      <span class="mono" id="tnv">${state.topN}</span></div><div style="height:10px"></div>`:''}
    ${shown.length?barChart(shown.map(l=>({l:l[0],v:l[1]})),'var(--amber)'):'<p class="hint">Ingen treff.</p>'}
  </div>`;
  bindDetail();
}
function bindDetail(){
  elDet.querySelectorAll('.ksubtabs button').forEach(b=>b.onclick=()=>{state.kView=b.dataset.kview;detail();});
  elDet.querySelectorAll('[data-knav]').forEach(b=>b.onclick=()=>{
    const act=b.dataset.knav;
    if(act==='cmp'){
      const i=state.compare.indexOf(state.sel);
      if(i>=0) state.compare.splice(i,1);
      else if(state.compare.length<4) state.compare.push(state.sel);
      render(); return;
    }
    const fl=filtered(); const i=fl.findIndex(x=>x.nr===state.sel);
    if(act==='prev' && i>0){state.sel=fl[i-1].nr;render();}
    else if(act==='next' && i>=0 && i<fl.length-1){state.sel=fl[i+1].nr;render();}
  });
  elDet.querySelectorAll('#agm button').forEach(b=>b.onclick=()=>{state.ageMode=b.dataset.m;detail();});
  elDet.querySelectorAll('#sxs button').forEach(b=>b.onclick=()=>{state.sysSex=b.dataset.x;detail();});
  elDet.querySelectorAll('#pjm button').forEach(b=>b.onclick=()=>{state.projMode=b.dataset.p;detail();});
  elDet.querySelectorAll('#ukr button').forEach(b=>b.onclick=()=>{state.ukr=+b.dataset.u;detail();});
  elDet.querySelectorAll('#ukrb button').forEach(b=>b.onclick=()=>{state.ukrbase=b.dataset.b;detail();});
  elDet.querySelectorAll('#sens button').forEach(b=>b.onclick=()=>{state.sens=+b.dataset.s;detail();});
  elDet.querySelectorAll('#mw button').forEach(b=>b.onclick=()=>{state.mw=b.dataset.w;detail();});
  elDet.querySelectorAll('#rbk button').forEach(b=>b.onclick=()=>{state.robekSort=b.dataset.s;detail();});
  const tn=document.getElementById('tn'); if(tn)tn.oninput=()=>{state.topN=+tn.value;
    var _tnv=document.getElementById('tnv'); if(_tnv) _tnv.textContent=tn.value;detail();};
  const cs=document.getElementById('cs'); if(cs)cs.oninput=()=>{state.csearch=cs.value;detail();
    const e=document.getElementById('cs');e.focus();e.setSelectionRange(e.value.length,e.value.length);};
}
// Pensjonstall i sammenligningskolonnen (PENSJON_DATA, fetch_pensjon.py)
function pensjonCmp(k){
  if(typeof PENSJON_DATA==='undefined') return '';
  const P=PENSJON_DATA, d=P.kommuner[String(k.nr)]; if(!d) return '';
  const i30=P.aar.indexOf(2030), i50=P.aar.indexOf(2050);
  const p=v=>pensjonTall(v)+' %';
  const tall=(v,l,farge)=>`<div><div style="font-size:18px;font-weight:600${farge?';color:'+farge:''}" class="mono">${v}</div><div style="font-size:11px;color:var(--ink3)">${l}</div></div>`;
  return `<div style="margin-top:14px;padding-top:12px;border-top:1px solid var(--line2)">
    <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink3);margin-bottom:8px">Pensjon · % av driftsinntektene</div>
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin-bottom:8px">
      ${tall(p(d.pa),'premieavvik 2025',d.pa>P.meta.landet_pa?'var(--neg)':null)}
      ${tall(p(d.df),'disposisjonsfond',d.pa>d.df?'var(--warn)':null)}
    </div>
    <div style="display:flex;gap:14px;flex-wrap:wrap">
      ${tall(p(d.R.basis[i30]),'kostnad 2030')}
      ${tall(p(d.R.basis[i50]),'kostnad 2050')}
    </div>
    <div style="font-size:11.5px;color:var(--ink3);margin-top:6px">2050: spenn ${pensjonTall(d.R.lav[i50])}–${p(d.R.hoy[i50])} · ${d.lev==='KLP'?'KLP':d.lev} · amortisering ${d.amort} år${d.grunnlag==='note'?'':' · bare KOSTRA'}</div>
  </div>`;
}
function renderCompare(){
  if(state.compare.length<2) return false;
  const ks=state.compare.map(nr=>K.find(k=>k.nr===nr));
  elDet.innerHTML=`<div class="dhead"><h2 class="serif">Sammenligning</h2>
    <span style="font-size:13px;color:var(--ink3)">${ks.length} kommuner — trykk ● i lista for å fjerne</span></div>
    <div class="cmpgrid" style="grid-template-columns:repeat(${ks.length},1fr)">
    ${ks.map(k=>{const med=medianAge(k.alder);const g=ageGroups(k.alder,'L');const mx=Math.max(...g.map(x=>x.v));
      return `<div class="cmpcol"><h4 class="serif">${k.navn}</h4>
      <div class="cfy" style="color:${FY[k.fylke]}">${k.fylke}</div>
      <div style="font-family:var(--font-display);font-size:24px;font-weight:600">${fmt(k.pop)}</div>
      <div style="font-size:12px;color:var(--ink3);margin-bottom:10px">folketall</div>
      <div style="display:flex;gap:14px;margin-bottom:12px">
        <div><div style="font-size:18px;font-weight:600" class="mono">${k.andel.toFixed(1).replace('.',',')} %</div><div style="font-size:11px;color:var(--ink3)">innv.bakgr.</div></div>
        <div><div style="font-size:18px;font-weight:600" class="mono">${med}</div><div style="font-size:11px;color:var(--ink3)">medianalder</div></div>
        <div><div style="font-size:18px;font-weight:600;color:var(--syss)" class="mono">${(k.syss&&k.syss.rate.zzz!=null)?k.syss.rate.zzz.toFixed(1).replace('.',',')+' %':'–'}</div><div style="font-size:11px;color:var(--ink3)">syss. innv.</div></div>
      </div>
      ${NN.placeholder('stolper',{kategorier:g.map(x=>x.l),serier:[{navn:'Personer',data:g.map(x=>x.v),farge:FY[k.fylke]}],ingenAkse:true,ingenY:true,hoyde:80},80)}
      <div style="font-size:11px;color:var(--ink3);margin-top:4px">aldersfordeling (livsfaser)</div>
      <div style="margin-top:12px;font-size:12.5px;color:var(--ink2)"><b>Største opprinnelse:</b><br>
        ${k.land.filter(l=>l[1]>0).slice(0,3).map(l=>l[0]+' ('+fmt(l[1])+')').join('<br>')||'–'}</div>
      ${pensjonCmp(k)}
      ${forsorgCmp(k)}
      </div>`;}).join('')}</div>`;
  return true;
}
const NATCOL=['var(--cat-3)','var(--cat-5)','var(--cat-6)','var(--cat-2)','var(--pos)','var(--neg)','var(--warn)','var(--cat-4)'];
function natColor(navn,i){
  if(navn==='Hele befolkningen')return 'var(--ink)';
  if(navn==='Befolkningen ekskl. innvandrere')return 'var(--cat-4)';
  if(navn==='Innvandrere i alt')return 'var(--accent)';
  return NATCOL[i%NATCOL.length];
}
function natBars(N,met,sx){
  const idxOf={}; N.rows.forEach((r,i)=>idxOf[r.navn]=i);
  const SUMN=['Hele befolkningen','Befolkningen ekskl. innvandrere','Innvandrere i alt'];
  const valOf=r=> (met==='rate'? r.rate[sx] : r.cnt[sx]);
  const summary=SUMN.map(nm=>N.rows[idxOf[nm]]).filter(Boolean);
  const regions=N.rows.filter(r=>SUMN.indexOf(r.navn)<0)
      .slice().sort((a,b)=>(valOf(b)==null?-1:valOf(b))-(valOf(a)==null?-1:valOf(a)));
  const natAvg = met==='rate' ? N.rows[idxOf['Hele befolkningen']].rate[sx] : null;
  const sumFarge={'Hele befolkningen':'ink','Befolkningen ekskl. innvandrere':'cat-4','Innvandrere i alt':'accent'};
  const note=v=> (met==='rate'&&natAvg!=null&&v!=null) ? ((v-natAvg)>=0?'+':'−')+Math.abs(v-natAvg).toFixed(1).replace('.',',')+' p.e. mot snitt' : '';
  return NN.placeholder('hstolper',{
    format:met==='rate'?'pst':'tall', maks:met==='rate'?100:undefined,
    grupper:[
      {tittel:'Sammendrag', rader:summary.map(r=>({l:r.navn,v:valOf(r),farge:sumFarge[r.navn],uthev:r.navn==='Innvandrere i alt'}))},
      {tittel:met==='rate'?'Verdensregioner, rangert etter andel':'Verdensregioner, rangert etter antall',
       ref:natAvg!=null?{v:natAvg,tekst:'Nasjonalt snitt '+natAvg.toFixed(1).replace('.',',')+' %'}:null,
       rader:regions.map(r=>({l:r.navn,v:valOf(r),note:note(valOf(r))}))}
    ]}, (summary.length+regions.length)*27+90);
}
function renderNat(){
  const N=DATA.nat_syss; if(!N) return;
  const el=document.getElementById('natbars'); if(!el) return;
  el.innerHTML=natBars(N,state.natMetric,state.natSex);
}
function renderNatTS(){
  const T=DATA.nat_ts; if(!T) return;
  const host=document.getElementById('natts'); if(!host) return;
  const yrs=T.years, n=yrs.length, met=state.natMetric, sx=state.natSex;
  if(!state.natHidden) state.natHidden={};
  const SUMN=['Hele befolkningen','Befolkningen ekskl. innvandrere','Innvandrere i alt'];
  const series=T.rows.map((r,i)=>({navn:r.navn,i,c:natColor(r.navn,i),
    sum:SUMN.indexOf(r.navn)>-1,
    vals:(r[met][sx]||[]).map(v=>v==null?null:v),
    on:!state.natHidden[r.navn]}));
  const byName=nm=>series.find(s=>s.navn===nm);
  const vis=series.filter(s=>s.on);
  let lo=Infinity,hi=-Infinity;
  vis.forEach(s=>s.vals.forEach(v=>{if(v!=null){lo=Math.min(lo,v);hi=Math.max(hi,v);}}));
  const legHTML=()=>{
    let g1='',g2='';
    series.forEach(se=>{
      const b=`<button data-leg="${se.navn}" data-on="${se.on?1:0}"><span class="dot" style="background:${se.c}"></span>${se.navn}</button>`;
      if(se.sum)g1+=b; else g2+=b;});
    return `<div class="nleg" style="margin-top:14px"><span class="ncap">Sammendrag</span>${g1}`
      +`<span class="ncap" style="margin-left:8px">Verdensregioner</span>${g2}</div>`;
  };
  if(!isFinite(lo)){host.innerHTML='<p class="hint" style="margin:8px 0 0">Ingen serier valgt.</p>'+legHTML();return;}
  const A=byName('Befolkningen ekskl. innvandrere'), Bn=byName('Innvandrere i alt');
  const harBand=A&&Bn&&A.on&&Bn.on;
  let gapTxt='';
  if(harBand){ let li=n-1; while(li>=0&&(A.vals[li]==null||Bn.vals[li]==null))li--;
    if(li>=0){const gap=A.vals[li]-Bn.vals[li]; gapTxt=' Skravert felt = forskjellen mellom befolkningen ekskl. innvandrere og innvandrere i alt: '+(met==='rate'?gap.toFixed(1).replace('.',',')+' prosentenheter':fmt(gap))+' i '+yrs[li]+'.';} }
  const spec={x:yrs, format:met==='rate'?'pst1':'tall', xTicks:yrs.filter((y,i)=>i%2===0||i===n-1), hoyde:360,
    serier:vis.map(se=>({navn:se.navn, kort:se.navn.length>22?se.navn.slice(0,21)+'…':se.navn, data:se.vals, farge:se.c,
      uthev:se.navn==='Hele befolkningen'||se.navn==='Innvandrere i alt', svak:!se.sum, etikett:se.sum})),
    band:harBand?{x:yrs, lo:Bn.vals, hi:A.vals, farge:'warn'}:null,
    yTittel:(met==='rate'?'Andel sysselsatte, 20–66 år.':'Antall sysselsatte, 20–66 år.')+' Verdensregionene er tonet ned; trykk på navnene under for å slå serier av og på.'+gapTxt};
  host.innerHTML=NN.placeholder('linjer',spec,380)+legHTML();
}
function renderModelEval(){
  const B=DATA.proj&&DATA.proj.backtest; if(!B) return;
  const hosts=[document.getElementById('bteval'),document.getElementById('bteval_intro'),document.getElementById('bteval_metode')].filter(Boolean);
  if(!hosts.length) return;
  [document.getElementById('btcav'),document.getElementById('btcav_intro'),document.getElementById('btcav_metode')].filter(Boolean).forEach(el=>{el.textContent=B.caveat||'';});
  const groups=B.classes.map(c=>({lab:c.name,sub:'klasse '+c.cls+' · n='+c.n,
      v:[c.ssb,c.mvp,c.attr],hl:(c.cls===5||c.cls===6)}))
    .concat([{lab:'Alle 80',sub:'n='+B.all.n,v:[B.all.ssb,B.all.mvp,B.all.attr],hl:false,div:true},
             {lab:'Mindre og minst sentrale',sub:'klasse 5+6 · n='+B.least.n,v:[B.least.ssb,B.least.mvp,B.least.attr],hl:true}]);
  const series=[['SSB-2020','var(--accent)'],['TF-MVP','var(--cat-5)'],['TF-ATTR','var(--cat-3)']];
  const html=NN.placeholder('backtest',{grupper:groups.map(g=>({lab:g.lab,sub:g.sub,v:g.v,uthev:g.hl})),serier:series},groups.length*54+80);
  hosts.forEach(h=>{h.innerHTML=html;});
}
function renderBigPicture(){
  const host=document.getElementById('bigPicGraph');
  const tldrHost=document.getElementById('bigPicTldr');
  if(!host&&!tldrHost) return;
  const agg=currentAgg(); // valgt fylke eller hele landsdelen
  if(!agg) return;
  // Tegn projChart for hele landsdelen i 'tot'-modus
  if(host){
    const savedMode=state.projMode; state.projMode='tot';
    host.innerHTML = projChart(agg,'tot');
    state.projMode=savedMode;
  }
  // Klartekst-banner
  if(tldrHost){
    const P=DATA.proj, o=P&&P.kommuner&&P.kommuner[agg.nr];
    const hist=agg.hist||{};
    const histYrs=Object.keys(hist).map(Number).sort((a,b)=>a-b);
    const firstY=histYrs.length?histYrs[0]:null, lastY=histYrs.length?histYrs[histYrs.length-1]:null;
    const firstV=firstY?hist[firstY]:null, lastV=lastY?hist[lastY]:null;
    const pastPct=(firstV&&lastV)?((lastV/firstV-1)*100):null;
    let projSSB=null, projLo=null, projHi=null, projYear=null;
    if(o&&o.main&&o.main.length){
      const n=o.main.length;
      projSSB=o.main[n-1]; projYear=(P.years||[])[n-1]||2050;
      const ext=[o.main[n-1],(o.mw&&o.mw.kons?o.mw.kons.pop[n-1]:projSSB),(o.tfattr?o.tfattr[n-1]:projSSB)];
      projLo=Math.min.apply(null,ext); projHi=Math.max.apply(null,ext);
    }
    const futurePct=(agg.pop&&projSSB)?((projSSB/agg.pop-1)*100):null;
    const fmt0=v=>v==null?'–':fmt(Math.round(v));
    const pctF=v=>(v>=0?'+':'−')+Math.abs(v).toFixed(Math.abs(v)<1?1:0).replace('.',',')+' %';
    let text='';
    const _bparea_cap = (state.fylke && state.fylke !== 'Alle') ? state.fylke : 'Nord-Norge';
    if(firstY&&lastY&&pastPct!=null){
      text+=_bparea_cap+' hadde <b>'+fmt0(firstV)+'</b> innbyggere i '+firstY+' og <b>'+fmt0(lastV)+'</b> i '+lastY+' — '+pctF(pastPct)+' over 25 år. ';
    }
    if(projSSB) text+='SSBs offisielle bane peker mot <b>'+fmt0(projSSB)+'</b> i '+projYear+' ('+pctF(futurePct)+' fra i dag). ';
    if(projLo&&projHi&&projHi-projLo>500) text+='Våre alternative flyttebaner ligger mellom <b>'+fmt0(projLo)+'</b> og <b>'+fmt0(projHi)+'</b>. ';
    const _bptot = (typeof currentK==='function') ? currentK().length : 80;
    const _bparea = (state.fylke && state.fylke !== 'Alle') ? state.fylke : 'landsdelen';
    text+='<i>Bak '+(/s$/.test(_bparea)?_bparea+"'":_bparea+'s')+' samlede linje ligger '+_bptot+' kommuner med svært ulike skjebner.</i>';
    const nums=[];
    if(pastPct!=null) nums.push({nv:pctF(pastPct),cls:pastPct>=0?'up':'down',nl:'25 år bak oss',nh:firstY+'–'+lastY});
    nums.push({nv:fmt0(agg.pop),cls:'',nl:'i dag',nh:'1.1.2026'});
    if(futurePct!=null) nums.push({nv:pctF(futurePct),cls:futurePct>=0?'up':'down',nl:'mot '+projYear,nh:'SSB MMMM'});
    tldrHost.className='tldr';
    tldrHost.innerHTML='<div class="tldr-tag">Akt 1 · Hva skjer · '+(state.fylke&&state.fylke!=='Alle'?state.fylke+' samlet':'Landsdelen samlet')+'</div>'+
      '<h3>Sett under ett: går folketallet i Nord-Norge ned?</h3>'+
      '<p class="tldr-text">'+text+'</p>'+
      '<div class="tldr-nums">'+nums.map(n=>'<div class="tldr-num"><div class="nv '+n.cls+'">'+n.nv+'</div><div class="nl">'+n.nl+'</div><div class="nh">'+n.nh+'</div></div>').join('')+'</div>';
  }
}
function renderComposition(){
  const agg=currentAgg(); if(!agg) return;
  // Klartekst
  const tldrHost=document.getElementById('compTldr');
  if(tldrHost){
    const med=medianAge(agg.alder);
    const barn=agg.alder.slice(0,18).reduce((a,b)=>a+b,0);
    const eldre=agg.alder.slice(67).reduce((a,b)=>a+b,0);
    const eldre80=agg.alder.slice(80).reduce((a,b)=>a+b,0);
    const pBarn=agg.pop?100*barn/agg.pop:0;
    const pEldre=agg.pop?100*eldre/agg.pop:0;
    const pEldre80=agg.pop?100*eldre80/agg.pop:0;
    const pInnv=agg.andel||0;
    const _scope = (state.fylke && state.fylke !== 'Alle') ? state.fylke : 'Nord-Norge';
    let text=_scope+' har <b>'+fmt(agg.pop)+'</b> innbyggere. Medianalderen er <b>'+med+' år</b>. ';
    text+='<b>'+pBarn.toFixed(0).replace('.',',')+' %</b> er under 18 (<i>'+fmt(barn)+'</i>), <b>'+pEldre.toFixed(0).replace('.',',')+' %</b> har passert 67 (<i>'+fmt(eldre)+'</i>) og <b>'+pEldre80.toFixed(1).replace('.',',')+' %</b> er 80 år eller eldre. ';
    text+='<b>'+pInnv.toFixed(1).replace('.',',')+' %</b> har innvandrerbakgrunn — i alt <b>'+fmt(agg.bc)+'</b> personer fordelt på <b>'+(agg.land||[]).filter(l=>l[1]>0).length+'</b> opprinnelsesland. ';
    text+='<i>Aldersgruppen som vokser raskest mot 2050, er 80+ — det er den som driver mest av framtidens omsorgsbehov.</i>';
    tldrHost.className='tldr t-people';
    tldrHost.innerHTML='<div class="tldr-tag">Akt 2 · Hvem blir igjen · '+(state.fylke&&state.fylke!=='Alle'?state.fylke+' samlet':'Landsdelen samlet')+'</div>'+
      '<h3>Hvem bor i '+_scope+' i dag?</h3>'+
      '<p class="tldr-text">'+text+'</p>'+
      '<div class="tldr-nums">'+
        '<div class="tldr-num"><div class="nv">'+med+'</div><div class="nl">Medianalder</div><div class="nh">år</div></div>'+
        '<div class="tldr-num"><div class="nv">'+pBarn.toFixed(0).replace('.',',')+' %</div><div class="nl">0–17 år</div><div class="nh">'+fmt(barn)+' personer</div></div>'+
        '<div class="tldr-num"><div class="nv '+(pEldre>=20?'warn':'')+'">'+pEldre.toFixed(0).replace('.',',')+' %</div><div class="nl">67+ år</div><div class="nh">'+fmt(eldre)+' personer</div></div>'+
        '<div class="tldr-num"><div class="nv">'+pInnv.toFixed(1).replace('.',',')+' %</div><div class="nl">Innvandrerbakgrunn</div><div class="nh">'+fmt(agg.bc)+' personer</div></div>'+
      '</div>';
  }
  // Aldersstruktur
  const ageHost=document.getElementById('compAgeGraph');
  if(ageHost){
    const mode=state.compAgeMode||'5';
    ageHost.innerHTML=barChart(ageGroups(agg.alder,mode==='1'?'1':mode==='5'?'5':'L'),'var(--aurora)');
    document.querySelectorAll('#cAgm button').forEach(b=>{
      b.setAttribute('aria-pressed', b.dataset.m===mode?'true':'false');
      b.onclick=()=>{state.compAgeMode=b.dataset.m;renderComposition();};
    });
  }
  // Landbakgrunn
  const origHost=document.getElementById('compOriginGraph');
  if(origHost){
    const vesP=agg.bc?Math.round(agg.ves/agg.bc*100):0, iveP=100-vesP;
    const lands=agg.land.filter(l=>l[1]>0).slice(0,15);
    origHost.innerHTML=
      '<div class="split" style="margin-bottom:10px">'+
        '<div class="v" style="width:'+vesP+'%">'+(vesP>8?vesP+' %':'')+'</div>'+
        '<div class="i" style="width:'+iveP+'%">'+(iveP>8?iveP+' %':'')+'</div></div>'+
      '<div class="legend"><span><i style="background:var(--nl)"></i>Vestlig · '+fmt(agg.ves)+'</span>'+
        '<span><i style="background:var(--amber)"></i>Ikke-vestlig · '+fmt(agg.ive)+'</span></div>'+
      '<h4 class="serif" style="font-size:14px;font-weight:600;margin:18px 0 6px">Topp 15 opprinnelsesland</h4>'+
      barChart(lands.map(l=>({l:l[0],v:l[1]})),'var(--amber)');
  }
  // Bofasthet (gjenbruker eksisterende renderBofastChart)
  const bfHost=document.getElementById('compBofastGraph');
  if(bfHost && typeof bofastChartHTML==='function'){
    bfHost.innerHTML='<div class="bofast-chart">'+bofastChartHTML()+'</div>';
  }
}

/* === Akt 2.3 Levekår og inntekt — render-funksjoner ========================== */
function renderLevekar(){
  if(typeof LEVEKAR_DATA==='undefined') return;
  // Aggregér landsdelen (vektet etter antall husholdninger / personer der relevant)
  const _kFylkeNr = state.fylke==='Alle' ? null : new Set(K.filter(x=>x.fylke===state.fylke).map(x=>String(x.nr)));
  const ks = Object.entries(LEVEKAR_DATA.kommuner).filter(([n,r])=>!_kFylkeNr||_kFylkeNr.has(n));
  // ---- A. Husholdningsinntekt ----
  // Median = vektet snitt av kommune-medianene, vektet med antall husholdninger
  let medSum=0, medW=0, totalHush=0;
  const kommuneMedianer = [];
  ks.forEach(([nr,r])=>{
    if(r.medianInntektEtterSkatt && r.hush_total){
      medSum += r.medianInntektEtterSkatt * r.hush_total;
      medW += r.hush_total;
      kommuneMedianer.push(r.medianInntektEtterSkatt);
    }
    if(r.hush_total) totalHush += r.hush_total;
  });
  const landsdelMedian = medW ? medSum/medW : null;
  kommuneMedianer.sort((a,b)=>a-b);
  const lavKommune = kommuneMedianer[0] || null;
  const hoyKommune = kommuneMedianer[kommuneMedianer.length-1] || null;
  // ---- B. Personinntekt-komponenter (sum total beløp i mill kr) ----
  let totLonn=0, totPensjon=0, totUfore=0, antBos=0;
  let medLonnSum=0, medLonnW=0, medPensjonSum=0, medPensjonW=0, medUforeSum=0, medUforeW=0;
  ks.forEach(([nr,r])=>{
    if(r.totalLonn_mill) totLonn += r.totalLonn_mill;
    if(r.totalPensjon_mill) totPensjon += r.totalPensjon_mill;
    if(r.totalUfore_mill) totUfore += r.totalUfore_mill;
    if(r.personBosatte17plus) antBos += r.personBosatte17plus;
    if(r.personLonn_median && r.personLonn_antall){
      medLonnSum += r.personLonn_median * r.personLonn_antall; medLonnW += r.personLonn_antall;
    }
    if(r.personPensjon_median && r.personPensjon_antall){
      medPensjonSum += r.personPensjon_median * r.personPensjon_antall; medPensjonW += r.personPensjon_antall;
    }
    if(r.personUfore_median && r.personUfore_antall){
      medUforeSum += r.personUfore_median * r.personUfore_antall; medUforeW += r.personUfore_antall;
    }
  });
  const sumKomponenter = totLonn + totPensjon + totUfore;
  const andelLonn = sumKomponenter ? totLonn/sumKomponenter*100 : 0;
  const andelPensjon = sumKomponenter ? totPensjon/sumKomponenter*100 : 0;
  const andelUfore = sumKomponenter ? totUfore/sumKomponenter*100 : 0;
  const medLonn = medLonnW ? medLonnSum/medLonnW : null;
  const medPensjon = medPensjonW ? medPensjonSum/medPensjonW : null;
  const medUfore = medUforeW ? medUforeSum/medUforeW : null;
  // ---- C. Eierstatus ----
  let hushTot=0, hushSelv=0, hushAndels=0, hushLeier=0;
  ks.forEach(([nr,r])=>{
    if(r.hush_total) hushTot += r.hush_total;
    if(r.hush_selveier) hushSelv += r.hush_selveier;
    if(r.hush_andels) hushAndels += r.hush_andels;
    if(r.hush_leier) hushLeier += r.hush_leier;
  });
  const pctSelv = hushTot ? hushSelv/hushTot*100 : 0;
  const pctAndels = hushTot ? hushAndels/hushTot*100 : 0;
  const pctLeier = hushTot ? hushLeier/hushTot*100 : 0;
  // ---- D. Boliger ----
  let bolTot=0, bolEne=0, bolTo=0, bolRekke=0, bolBlokk=0, bolBofell=0, bolAndre=0;
  ks.forEach(([nr,r])=>{
    if(r.boliger_total) bolTot += r.boliger_total;
    if(r.boliger_enebolig) bolEne += r.boliger_enebolig;
    if(r.boliger_tomannsbolig) bolTo += r.boliger_tomannsbolig;
    if(r.boliger_rekkehus) bolRekke += r.boliger_rekkehus;
    if(r.boliger_boligblokk) bolBlokk += r.boliger_boligblokk;
    if(r.boliger_bofellesskap) bolBofell += r.boliger_bofellesskap;
    if(r.boliger_andre) bolAndre += r.boliger_andre;
  });
  // Norgessnitt for kontekst (omtrent fra SSB)
  const NORGE_MED_INNT = 676100; // SSB 06944, hele landet, alle husholdninger, inntekt etter skatt, median 2024
  // ---- Klartekst ----
  const tldrHost=document.getElementById('levekarTldr');
  const fmtKr = n => n==null?'–':(n>=1e6?(n/1e6).toFixed(2).replace('.',',')+' mill kr':(n>=1000?Math.round(n).toLocaleString('nb-NO').replace(/ /g,' ')+' kr':Math.round(n)+' kr'));
  const fmtMrd = n => (n/1000).toFixed(1).replace('.',',')+' mrd kr';
  const fmtMrdTekst = n => (n/1000).toFixed(1).replace('.',',')+' milliarder kroner';
  if(tldrHost){
    const diffNorge = landsdelMedian ? ((landsdelMedian/NORGE_MED_INNT - 1)*100) : null;
    const _scope2 = (state.fylke && state.fylke !== 'Alle') ? state.fylke : 'Nord-Norge';
    let text='Median husholdningsinntekt etter skatt i '+_scope2+' er <b>'+fmtKr(landsdelMedian)+'</b> per husholdning (2024). ';
    if(diffNorge!=null) text+='Det er '+(diffNorge>=0?'<b>'+diffNorge.toFixed(0).replace('.',',')+' %</b> over':'<b>'+Math.abs(diffNorge).toFixed(0).replace('.',',')+' %</b> under')+' nasjonal median på '+NORGE_MED_INNT.toLocaleString('nb-NO').replace(/ /g,' ')+' kr. ';
    if(lavKommune && hoyKommune) text+='Mellom de '+kommuneMedianer.length+' kommunene varierer median husholdningsinntekt fra <b>'+fmtKr(lavKommune)+'</b> til <b>'+fmtKr(hoyKommune)+'</b> — en forskjell på <b>'+(hoyKommune/lavKommune).toFixed(2).replace('.',',')+'×</b>. ';
    text+='Av den samlede personinntekten i '+_scope2+' på <b>'+fmtMrdTekst(sumKomponenter)+'</b> kommer <b>'+andelLonn.toFixed(0).replace('.',',')+' %</b> fra lønn, <b>'+andelPensjon.toFixed(0).replace('.',',')+' %</b> fra pensjon og <b>'+andelUfore.toFixed(0).replace('.',',')+' %</b> fra uføretrygd. ';
    text+='<b>'+pctSelv.toFixed(0).replace('.',',')+' %</b> av husholdningene eier boligen selv. ';
    text+='<i>Pensjon og uføretrygd utgjør til sammen en stor del av inntektene, så inntektsbasen er følsom for endringer i statlige stønader.</i>';
    tldrHost.className='tldr t-people';
    tldrHost.innerHTML='<div class="tldr-tag">Akt 2 · Hvem blir igjen · Levekår</div>'+
      '<h3>Hva tjener folk i '+_scope2+' — og hvor kommer pengene fra?</h3>'+
      '<p class="tldr-text">'+text+'</p>'+
      '<div class="tldr-nums">'+
        (landsdelMedian?'<div class="tldr-num"><div class="nv">'+(Math.round(landsdelMedian/1000)*1000).toLocaleString('nb-NO').replace(/ /g,' ')+' kr</div><div class="nl">Median hush.-inntekt</div><div class="nh">etter skatt, 2024</div></div>':'')+
        '<div class="tldr-num"><div class="nv">'+fmt(hushTot)+'</div><div class="nl">Antall husholdninger</div><div class="nh">SSB 14891, 2025</div></div>'+
        '<div class="tldr-num"><div class="nv '+(andelUfore>=12?'down':andelUfore>=8?'warn':'')+'">'+andelUfore.toFixed(0).replace('.',',')+' %</div><div class="nl">Andel uføretrygd</div><div class="nh">av total personinntekt</div></div>'+
        '<div class="tldr-num"><div class="nv">'+fmt(bolTot)+'</div><div class="nl">Antall boliger</div><div class="nh">SSB 06265, 2026</div></div>'+
      '</div>';
  }
  // ---- Graf A: Husholdningsinntekt — kommune-spennvidde + median + nasjonalt snitt ----
  const inntektHost=document.getElementById('levekarInntektGraph');
  if(inntektHost && landsdelMedian){
    const max = Math.max(hoyKommune||1, NORGE_MED_INNT*1.2);
    const w = v => v/max*100;
    inntektHost.innerHTML =
      NN.placeholder('hstolper',{format:'kr',grupper:[{rader:[
        {l:'Lavest kommune',v:lavKommune||null},
        {l:'Landsdelsmedian',v:Math.round(landsdelMedian),uthev:true},
        {l:'Norge',v:NORGE_MED_INNT,farge:'cat-4'},
        {l:'Høyest kommune',v:hoyKommune||null}]}]},140)+
      '<p class="hint" style="font-size:11px;margin-top:8px;font-style:italic">Median per kommune (SSB tabell 06944, 2024). Landsdelsmedianen er vektet snitt med antall husholdninger. Nasjonal median 2024: 676 100 kr (SSB 06944).</p>';
  }
  // ---- Graf B: Personinntekt-komponenter ----
  const kompHost=document.getElementById('levekarKomponentGraph');
  if(kompHost){
    const pct = (v) => (v/sumKomponenter*100);
    kompHost.innerHTML =
      '<div class="split" style="margin:10px 0">'+
        '<div style="width:'+pct(totLonn).toFixed(1)+'%;background:var(--aurora);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:12px">'+(pct(totLonn)>=8?andelLonn.toFixed(0).replace('.',',')+' %':'')+'</div>'+
        '<div style="width:'+pct(totPensjon).toFixed(1)+'%;background:var(--nl);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:12px">'+(pct(totPensjon)>=8?andelPensjon.toFixed(0).replace('.',',')+' %':'')+'</div>'+
        '<div style="width:'+pct(totUfore).toFixed(1)+'%;background:var(--amber);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:12px">'+(pct(totUfore)>=8?andelUfore.toFixed(0).replace('.',',')+' %':'')+'</div>'+
      '</div>'+
      '<div class="legend"><span><i style="background:var(--aurora)"></i>Lønn '+fmtMrd(totLonn)+'</span>'+
        '<span><i style="background:var(--nl)"></i>Pensjon '+fmtMrd(totPensjon)+'</span>'+
        '<span><i style="background:var(--amber)"></i>Uføretrygd '+fmtMrd(totUfore)+'</span></div>'+
      '<table class="sust-table" style="width:100%;margin-top:14px;font-size:12.5px">'+
        '<thead><tr><th>Inntektskomponent</th><th class="r">Median per person</th><th class="r">Andel av total</th></tr></thead>'+
        '<tbody>'+
          '<tr><td><b>Lønn</b></td><td class="r">'+(medLonn?Math.round(medLonn/1000)+' 000 kr':'–')+'</td><td class="r">'+andelLonn.toFixed(1).replace('.',',')+' %</td></tr>'+
          '<tr><td><b>Pensjon</b></td><td class="r">'+(medPensjon?Math.round(medPensjon/1000)+' 000 kr':'–')+'</td><td class="r">'+andelPensjon.toFixed(1).replace('.',',')+' %</td></tr>'+
          '<tr><td><b>Uføretrygd</b></td><td class="r">'+(medUfore?Math.round(medUfore/1000)+' 000 kr':'–')+'</td><td class="r">'+andelUfore.toFixed(1).replace('.',',')+' %</td></tr>'+
        '</tbody></table>';
  }
  // ---- Graf C: Eierstatus ----
  const eierHost=document.getElementById('levekarEierGraph');
  if(eierHost){
    eierHost.innerHTML =
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:10px">'+
        '<div>'+
          '<div style="font-family:var(--font-mono);font-size:28px;font-weight:600;color:var(--ink)">'+fmt(hushTot)+'</div>'+
          '<div style="font-size:12px;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em">Totalt antall husholdninger</div>'+
        '</div>'+
        '<div>'+
          '<div style="font-family:var(--font-mono);font-size:28px;font-weight:600;color:var(--aurora)">'+pctSelv.toFixed(0).replace('.',',')+' %</div>'+
          '<div style="font-size:12px;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em">Selveiere</div>'+
        '</div>'+
      '</div>'+
      '<div class="split" style="margin-top:14px">'+
        '<div style="width:'+pctSelv.toFixed(1)+'%;background:var(--aurora);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:12px">'+(pctSelv>=10?pctSelv.toFixed(0).replace('.',',')+' %':'')+'</div>'+
        '<div style="width:'+pctAndels.toFixed(1)+'%;background:var(--nl);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:12px">'+(pctAndels>=8?pctAndels.toFixed(0).replace('.',',')+' %':'')+'</div>'+
        '<div style="width:'+pctLeier.toFixed(1)+'%;background:var(--amber);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:12px">'+(pctLeier>=8?pctLeier.toFixed(0).replace('.',',')+' %':'')+'</div>'+
      '</div>'+
      '<div class="legend"><span><i style="background:var(--aurora)"></i>Selveier '+fmt(hushSelv)+'</span>'+
        '<span><i style="background:var(--nl)"></i>Andels-/aksjeeier '+fmt(hushAndels)+'</span>'+
        '<span><i style="background:var(--amber)"></i>Leier '+fmt(hushLeier)+'</span></div>'+
      '<p class="hint" style="margin-top:10px;font-size:11.5px;font-style:italic">Til sammen eier om lag '+Math.round(pctSelv+pctAndels)+' % av husholdningene i '+((state.fylke&&state.fylke!=='Alle')?state.fylke:'Nord-Norge')+' boligen selv, enten som selveiere eller andelseiere, men andelen varierer kraftig mellom kommuner. Sentrale kommuner (Bodø, Tromsø, Hammerfest) har mer leie og borettslag enn distriktskommuner.</p>';
  }
  // ---- Graf D: Boliger ----
  const boligHost=document.getElementById('levekarBoligGraph');
  if(boligHost && bolTot){
    const bP = v => bolTot ? v/bolTot*100 : 0;
    const rows = [
      ['Enebolig', bolEne, 'var(--aurora)'],
      ['Tomannsbolig', bolTo, 'var(--nl)'],
      ['Rekkehus / kjedehus / småhus', bolRekke, 'var(--tr)'],
      ['Boligblokk', bolBlokk, 'var(--amber)'],
      ['Bofellesskap', bolBofell, 'var(--fi)'],
      ['Andre', bolAndre, 'var(--ink3)']
    ];
    const rowsH = NN.placeholder('hstolper',{format:'tall',grupper:[{rader:rows.map((r,i)=>({l:r[0],v:r[1],uthev:i===0,farge:i===0?'accent':'muted',note:bP(r[1]).toFixed(0)+' %'}))}]},rows.length*27+20);
    boligHost.innerHTML =
      '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin:10px 0 16px">'+
        '<div><div style="font-family:var(--font-mono);font-size:24px;font-weight:600;color:var(--ink)">'+fmt(bolTot)+'</div>'+
          '<div style="font-size:11.5px;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em">Boliger totalt</div></div>'+
        '<div><div style="font-family:var(--font-mono);font-size:24px;font-weight:600;color:var(--aurora)">'+bP(bolEne).toFixed(0).replace('.',',')+' %</div>'+
          '<div style="font-size:11.5px;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em">Eneboliger</div></div>'+
        '<div><div style="font-family:var(--font-mono);font-size:24px;font-weight:600;color:var(--amber)">'+bP(bolBlokk).toFixed(0).replace('.',',')+' %</div>'+
          '<div style="font-size:11.5px;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em">Blokkleiligheter</div></div>'+
      '</div>'+
      rowsH +
      '<p class="hint" style="margin-top:10px;font-size:11.5px;font-style:italic">Eneboliger dominerer, særlig i distriktskommunene. Andelen boligblokker er størst i Bodø og Tromsø.</p>';
  }
  // ---- Graf E: Inntektsspennvidde mellom kommuner ----
  const spennHost=document.getElementById('levekarSpennGraph');
  if(spennHost){
    // Bygg liste av kommuner med median inntekt, sortert
    const items = [];
    ks.forEach(([nr,r])=>{
      if(r.medianInntektEtterSkatt){
        const k = K.find(x=>x.nr===+nr);
        items.push({nr, navn:k?k.navn:nr, fylke:k?k.fylke:'', med:r.medianInntektEtterSkatt, hush:r.hush_total});
      }
    });
    items.sort((a,b)=>a.med-b.med); // laveste først → høyeste til høyre
    const n = items.length;
    const svg = NN.placeholder('rang',{format:'kr',
      rader:items.map(it=>({nr:+it.nr,navn:it.navn,fylke:it.fylke,v:it.med,
        note:landsdelMedian?(((it.med-landsdelMedian)/landsdelMedian*100)>=0?'+':'−')+Math.abs((it.med-landsdelMedian)/landsdelMedian*100).toFixed(1).replace('.',',')+' % mot landsdelen':''})),
      ref:[landsdelMedian?{y:Math.round(landsdelMedian),tekst:'Landsdel '+fmt(Math.round(landsdelMedian))}:null,{y:NORGE_MED_INNT,tekst:'Norge '+fmt(NORGE_MED_INNT),farge:'var(--accent-text)'}].filter(Boolean)},320);
    // Statistikk under
    const lo3 = items.slice(0,3).map(x=>x.navn).join(', ');
    const hi3 = items.slice(-3).reverse().map(x=>x.navn).join(', ');
    const spread = items[n-1].med - items[0].med;
    const ratio = items[n-1].med / items[0].med;
    spennHost.innerHTML = svg +
      '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-top:14px">'+
        '<div><div style="font-family:var(--font-mono);font-size:18px;font-weight:600;color:var(--ink)">'+fmt(Math.round(items[0].med/1000)*1000)+' → '+fmt(Math.round(items[n-1].med/1000)*1000)+'</div><div style="font-size:11px;color:var(--ink3);text-transform:uppercase;letter-spacing:.06em">Spennvidde</div></div>'+
        '<div><div style="font-family:var(--font-mono);font-size:18px;font-weight:600;color:var(--amber)">'+ratio.toFixed(2).replace('.',',')+'×</div><div style="font-size:11px;color:var(--ink3);text-transform:uppercase;letter-spacing:.06em">Høyest / lavest</div></div>'+
        '<div><div style="font-size:13px;color:var(--ink)">'+hi3+'</div><div style="font-size:11px;color:var(--ink3);text-transform:uppercase;letter-spacing:.06em">Topp 3</div></div>'+
        '<div><div style="font-size:13px;color:var(--ink)">'+lo3+'</div><div style="font-size:11px;color:var(--ink3);text-transform:uppercase;letter-spacing:.06em">Bunn 3</div></div>'+
      '</div>'+
      '<p class="hint" style="margin-top:12px;font-size:11.5px;font-style:italic">Spennvidden mellom høyeste og laveste kommune i '+(state.fylke&&state.fylke!=='Alle'?state.fylke:'Nord-Norge')+' er '+fmt(Math.round(spread/1000)*1000)+' kr. Hovedforklaringen er fordelingen mellom lønn og pensjon — kommuner med mange yrkesaktive husholdninger (sentre, oljerelaterte) ligger over snittet; aldrende distriktskommuner med høy pensjons- og uføretrygdandel ligger under.</p>';
  }
  attachMethodBadges();
}

function renderBurden(){
  const agg=currentAgg(); if(!agg) return;
  const P=DATA.proj, o=P&&P.kommuner&&P.kommuner[agg.nr];
  const tldrHost=document.getElementById('burdenTldr');
  const graphHost=document.getElementById('burdenGraph');
  if(!o||!o.a65||!o.a2064) return;
  const n=(P.years||[]).length;
  // Standard demografisk forsørgerbyrde (65+/20-64) — SSB MMMM (hovedbane)
  const oad0=o.a2064[0]?100*o.a65[0]/o.a2064[0]:null;
  const oad1=o.a2064[n-1]?100*o.a65[n-1]/o.a2064[n-1]:null;
  // Scope (fylke eller landsdel)
  const _scopeKey = (state.fylke && state.fylke !== 'Alle') ? state.fylke : 'Alle';
  const _scopeTxt = _scopeKey === 'Alle' ? 'landsdelen samlet' : state.fylke;
  const a80_0=o.a80?o.a80[0]:null, a80_1=o.a80?o.a80[n-1]:null;
  const projYear=(P.years||[])[n-1]||2050;
  // Faktisk arbeid: ikke-sysselsatte per 100 sysselsatte (FORSORG_DATA, fetch_forsorg.py)
  const fKey=_scopeKey==='Alle'?'nn':_scopeKey, fNavn=_scopeKey==='Alle'?'Nord-Norge':_scopeKey;
  const FR=(typeof FORSORG_DATA!=='undefined')?FORSORG_DATA.regioner[fKey]:null, FL=FR?FORSORG_DATA.regioner.landet:null;
  const t1=v=>v==null?'–':v.toFixed(1).replace('.',',');
  if(tldrHost){
    let text='Forsørgerbrøken i '+_scopeTxt+' går fra <b>'+t1(oad0)+'</b> til <b>'+t1(oad1)+'</b> innbyggere 65 år og eldre per 100 i alderen 20–64 fram mot '+projYear+'. ';
    let fNums='';
    if(FR){
      const ok0=fbOkonIDag(FR), okL=fbOkonIDag(FL), m=FR.okon.length-1, dS=(FR.syss[m]/FR.syss[0]-1)*100, dSL=(FL.syss[m]/FL.syss[0]-1)*100;
      text+='Aldersmålet teller ikke hvem som er i arbeid. Teller man alle som ikke er sysselsatt — barn, studenter, pensjonister, uføre og ledige — er det <b>'+t1(ok0)+'</b> per 100 sysselsatte i dag, mot '+t1(okL)+' i landet. ';
      text+=(Math.abs(ok0-okL)<2?'Målt mot faktisk arbeid er byrden altså omtrent som i landet. ':ok0>okL?'Målt mot faktisk arbeid er byrden høyere enn i landet. ':'Målt mot faktisk arbeid er byrden lavere enn i landet. ');
      text+='Holdes sysselsettingen i hver aldersgruppe som i dag, '+(dS>=0?'øker':'faller')+' antallet sysselsatte med <b>'+t1(Math.abs(dS))+' %</b> mot '+projYear+' (landet '+(dSL>=0?'+':'−')+t1(Math.abs(dSL))+' %). ';
      fNums='<div class="tldr-num"><div class="nv">'+t1(ok0)+'</div><div class="nl">Per 100 sysselsatte i dag</div><div class="nh">ikke-sysselsatte, alle aldre · landet '+t1(okL)+'</div></div>'+
        '<div class="tldr-num"><div class="nv '+(FR.okon[m]>FL.okon[m]+2?'warn':'')+'">'+t1(FR.okon[m])+'</div><div class="nl">Per 100 sysselsatte '+projYear+'</div><div class="nh">alt annet likt · landet '+t1(FL.okon[m])+'</div></div>'+
        '<div class="tldr-num"><div class="nv '+(dS<-5?'down':'')+'">'+(dS>=0?'+':'−')+t1(Math.abs(dS))+' %</div><div class="nl">Sysselsatte 2026–'+projYear+'</div><div class="nh">alt annet likt</div></div>';
    }
    if(a80_0&&a80_1){
      const pct80=(a80_1/a80_0-1)*100;
      text+='Antallet 80+ <b>'+(pct80>=0?'vokser med '+pct80.toFixed(0).replace('.',',')+' %':'går ned med '+Math.abs(pct80).toFixed(0).replace('.',',')+' %')+'</b> (fra '+fmt(a80_0)+' til '+fmt(a80_1)+'). ';
    }
    text+='<i>Det er denne forskyvningen — flere eldre og færre i arbeid — som setter kommuneøkonomien på prøve i Akt 3.</i>';
    tldrHost.className='tldr t-burden';
    tldrHost.innerHTML='<div class="tldr-tag">Akt 2 · Hvem blir igjen · Bæreevne</div>'+
      '<h3>Hvor tungt blir aldringen å bære?</h3>'+
      '<p class="tldr-text">'+text+'</p>'+
      '<div class="tldr-nums">'+
        (oad0!=null?'<div class="tldr-num"><div class="nv">'+t1(oad0)+' → '+t1(oad1)+'</div><div class="nl">Forsørgerbrøk 2026–'+projYear+'</div><div class="nh">65+ per 100 i alderen 20–64</div></div>':'')+
        fNums+
      '</div>';
  }
  const fbHost=document.getElementById('forsorgKort');
  if(fbHost && typeof forsorgCard==='function') fbHost.innerHTML=forsorgCard(fKey, fNavn);
  // Hero-graf: projChart i 'fb'-modus for landsdelen
  if(graphHost){
    const savedMode=state.projMode;
    state.projMode='fb';
    graphHost.innerHTML=projChart(agg,'fb');
    state.projMode=savedMode;
  }
}
function renderEconomy(){
  const agg=currentAgg(); if(!agg) return;
  const P=DATA.proj, B=(P&&P.kostra_bench&&(P.kostra_bench[state.fylke&&state.fylke!=='Alle'?state.fylke:'Alle']||P.kostra_bench['Alle']))||{};
  const num=v=>v==null?null:+v;
  const ndr=num(B.ndr), fond=num(B.fond), gj=num(B.gjeld), yr=B.yr||'';
  const RB=P&&P.robek; let inR=0, pend=0;
  // Filtrer ROBEK-status til valgt scope (fylke eller landsdel)
  const scopeK = currentK();
  const scopeTot = scopeK.length;
  const scopeOmrade = (state.fylke && state.fylke !== 'Alle') ? state.fylke : 'Nord-Norge';
  if(RB&&RB.kommuner){
    inR = scopeK.filter(x => RB.kommuner[x.nr]).length;
    pend = scopeK.filter(x => (RB.pending||{})[x.nr]).length;
  }
  const tldrHost=document.getElementById('econTldr');
  if(tldrHost){
    let text='Median<b> netto driftsresultat</b> er '+(ndr==null?'–':(ndr>=0?'+':'−')+Math.abs(ndr).toFixed(1).replace('.',',')+' %')+' av brutto driftsinntekter ('+yr+'). ';
    text+='<b>Disposisjonsfondet</b> ligger på '+(fond==null?'–':fond.toFixed(1).replace('.',',')+' %')+'. ';
    text+='<b>Netto lånegjeld</b> er '+(gj==null?'–':gj.toFixed(1).replace('.',',')+' %')+'. ';
    text+='Av '+scopeTot+' kommuner i '+scopeOmrade+' er <b>'+inR+'</b> registrert i ROBEK i dag, og <b>'+pend+'</b> over grensen under behandling. ';
    text+='<i>Disse tre tallene — resultat, buffer, gjeld — bestemmer hvor mye handlingsrom kommunene har når aldringskostnaden kommer.</i>';
    tldrHost.className='tldr t-burden';
    tldrHost.innerHTML='<div class="tldr-tag">Akt 3 · Kan vi bære det? · Økonomien i dag</div>'+
      '<h3>Hvor solid står kommuneøkonomien?</h3>'+
      '<p class="tldr-text">'+text+'</p>'+
      '<div class="tldr-nums">'+
        (ndr!=null?'<div class="tldr-num"><div class="nv '+(ndr<0?'down':ndr<1.75?'warn':'up')+'">'+(ndr>=0?'+':'−')+Math.abs(ndr).toFixed(1).replace('.',',')+' %</div><div class="nl">Netto driftsresultat</div><div class="nh">TBU-norm +1,75</div></div>':'')+
        (fond!=null?'<div class="tldr-num"><div class="nv '+(fond<3?'down':fond<5?'warn':'up')+'">'+fond.toFixed(1).replace('.',',')+' %</div><div class="nl">Disposisjonsfond</div><div class="nh">av driftsinntekter</div></div>':'')+
        '<div class="tldr-num"><div class="nv down">'+inR+'</div><div class="nl">I ROBEK</div><div class="nh">av '+scopeTot+' kommuner</div></div>'+
        (pend>0?'<div class="tldr-num"><div class="nv warn">'+pend+'</div><div class="nl">Over grensen</div><div class="nh">under behandling</div></div>':'')+
      '</div>';
  }
  renderRente();
  renderGjeld();
  renderPensjon();
}
function renderRente(){
  const host=document.getElementById('renteContent');
  if(!host || typeof RENTE_DATA==='undefined') return;
  if(state.renteCur==null) state.renteCur = 5.4;
  if(state.renteNew==null) state.renteNew = 4.0;
  // Aggregér til valgt scope (fylke eller landsdel)
  const _scopeNr = new Set(currentK().map(k => String(k.nr)));
  let sumNdrKr=0, sumRxpKr=0, validKom=0, proxyKom=0;
  Object.entries(RENTE_DATA.kommuner).forEach(([nr,r])=>{
    if(!_scopeNr.has(nr)) return;
    if(r.ndr_kr!=null){ sumNdrKr+=r.ndr_kr; validKom++; }
    if(r.rxp_kr!=null){ sumRxpKr+=r.rxp_kr; if(r.proxy) proxyKom++; }
  });
  const aggPop=currentAgg()?currentAgg().pop:0;
  const perPpKr = sumRxpKr * 0.01 * 1000;
  const ppPerInnb = aggPop?perPpKr/aggPop:0;
  const dRate = state.renteCur - state.renteNew;
  const savingsKr = sumRxpKr * (dRate/100) * 1000;
  const savingsPerInnb = aggPop?savingsKr/aggPop:0;
  const ndrTotal = sumNdrKr * 1000;
  const ndrPerInnb = aggPop?ndrTotal/aggPop:0;
  const isSaving = dRate >= 0;
  const fmtMrd = n => (n/1e9).toFixed(2).replace('.',',')+' mrd kr';
  const fmtMill = n => (n/1e6).toFixed(1).replace('.',',')+' mill kr';
  const fmtKrInnb = n => Math.round(n).toLocaleString('nb-NO')+' kr';
  let html='';
  // Slidere
  html+='<div class="sust-sliders" style="margin-bottom:14px">'+
    '<div class="sust-slider">'+
      '<div class="ssl-lab"><span>Antatt dagens flytende rente</span><span class="ssl-val">'+state.renteCur.toFixed(2).replace('.',',')+' %</span></div>'+
      '<input type="range" min="2" max="8" step="0.05" value="'+state.renteCur+'" id="rcur">'+
      '<div class="ssl-hint">3 mnd NIBOR + KBN-margin. Norges Banks styringsrente 4,50 % (fra 25. september 2026).</div>'+
    '</div>'+
    '<div class="sust-slider">'+
      '<div class="ssl-lab"><span>Ønsket/ny rente</span><span class="ssl-val">'+state.renteNew.toFixed(2).replace('.',',')+' %</span></div>'+
      '<input type="range" min="2" max="8" step="0.05" value="'+state.renteNew+'" id="rnew">'+
      '<div class="ssl-hint">Sett over dagens for å se merkostnad.</div>'+
    '</div>'+
  '</div>';
  // KPI-kort
  html+='<div class="sust-fylkebars">'+
    '<div class="sfb">'+
      '<h4>Faktisk netto rentekostnad</h4>'+
      '<div style="font-family:var(--font-mono);font-size:22px;font-weight:600;color:var(--ink2);margin:6px 0 2px">'+fmtMrd(ndrTotal)+'/år</div>'+
      '<div style="font-size:11.5px;color:var(--ink3)">'+fmtKrInnb(ndrPerInnb)+' per innbygger · regnskap (KOSTRA AGD97)</div>'+
    '</div>'+
    '<div class="sfb">'+
      '<h4>Renteeksponert gjeld</h4>'+
      '<div style="font-family:var(--font-mono);font-size:22px;font-weight:600;color:var(--ink2);margin:6px 0 2px">'+fmtMrd(sumRxpKr*1000)+'</div>'+
      '<div style="font-size:11.5px;color:var(--ink3)">1 prosentpoeng lavere rente = '+(perPpKr/1e6).toFixed(0).replace('.',',')+' mill kr/år · '+fmtKrInnb(ppPerInnb)+'/innb'+(proxyKom>0?' († '+proxyKom+(proxyKom===1?' kommune bruker':' kommuner bruker')+' netto lånegjeld i stedet)':'')+'</div>'+
    '</div>'+
    '<div class="sfb" style="background:'+(isSaving?'color-mix(in srgb, var(--pos) 6%, transparent)':'color-mix(in srgb, var(--neg) 6%, transparent)')+';border-color:'+(isSaving?'color-mix(in srgb, var(--pos) 25%, transparent)':'color-mix(in srgb, var(--neg) 25%, transparent)')+'">'+
      '<h4 style="color:'+(isSaving?'var(--pos)':'var(--neg)')+'">'+(isSaving?'Innsparing':'Merkostnad')+' ved ny rente</h4>'+
      '<div style="font-family:var(--font-mono);font-size:22px;font-weight:600;color:'+(isSaving?'var(--pos)':'var(--neg)')+';margin:6px 0 2px">'+(isSaving?'−':'+')+fmtMrd(Math.abs(savingsKr))+'/år</div>'+
      '<div style="font-size:11.5px;color:var(--ink3)">'+(isSaving?'−':'+')+fmtKrInnb(Math.abs(savingsPerInnb))+'/innb · '+Math.abs(dRate).toFixed(2).replace('.',',')+' pp endring</div>'+
    '</div>'+
  '</div>';
  // Per kommune
  const rows=[];
  Object.entries(RENTE_DATA.kommuner).forEach(([nr,r])=>{
    if(r.rxp_kr==null||r.ndr_kr==null) return;
    const k=K.find(x=>x.nr===+nr); if(!k) return;
    const savKr = r.rxp_kr * (dRate/100) * 1000;
    rows.push({navn:k.navn,fylke:k.fylke,ndr:r.ndr_kr*1000,rxp:r.rxp_kr*1000,
      proxy:r.proxy,savKr,savPi:k.pop?savKr/k.pop:0,pop:k.pop});
  });
  rows.sort((a,b)=>Math.abs(b.savPi)-Math.abs(a.savPi));
  let trs='';
  rows.forEach(r=>{
    trs+='<tr>'+
      '<td><div class="sname">'+r.navn+(r.proxy?' †':'')+'</div><div class="sfylke">'+r.fylke+'</div></td>'+
      '<td class="r">'+(r.ndr/1e6).toFixed(1).replace('.',',')+' mill</td>'+
      '<td class="r">'+Math.round(r.ndr/r.pop).toLocaleString('nb-NO')+' kr</td>'+
      '<td class="r">'+(r.rxp/1e6).toFixed(0).replace('.',',')+' mill</td>'+
      '<td class="r" style="color:'+(isSaving?'var(--pos)':'var(--neg)')+'">'+(isSaving?'−':'+')+(Math.abs(r.savKr)/1e6).toFixed(1).replace('.',',')+' mill</td>'+
      '<td class="r" style="color:'+(isSaving?'var(--pos)':'var(--neg)')+'">'+(isSaving?'−':'+')+Math.round(Math.abs(r.savPi)).toLocaleString('nb-NO')+' kr</td>'+
    '</tr>';
  });
  html+='<div class="sust-table-wrap" style="margin-top:14px"><table class="sust-table">'+
    '<thead><tr><th>Kommune</th>'+
      '<th class="r">Netto renter</th><th class="r">kr/innb</th>'+
      '<th class="r">Renteeksp.<br>gjeld</th>'+
      '<th class="r">'+(isSaving?'Innsparing':'Merkostnad')+'<br>'+Math.abs(dRate).toFixed(1).replace('.',',')+' pp</th>'+
      '<th class="r">kr/innb</th>'+
    '</tr></thead><tbody>'+trs+'</tbody></table></div>'+
    '<p class="hint" style="margin-top:8px;font-size:11px;opacity:.75">Per-prosentpoeng-effekten er det robuste tallet — den skalerer lineært. «Dagens rente» er din egen valgbare forutsetning. Renteutslag tar tid: KBNs flytende lån justeres kvartalsvis, fastrentelån forfaller gradvis over flere år. Tallene er øvre grense for et rent KBN-rentekutt — også KLP/sertifikater/obligasjoner finnes. † = renteeksponert gjeld manglet i KOSTRA, netto lånegjeld brukt i stedet.</p>'+
    '<div style="margin-top:12px" data-methodbadge="SSB_STATBANK"></div>';
  host.innerHTML=html;
  const rc=document.getElementById('rcur'), rn=document.getElementById('rnew');
  if(rc) rc.oninput=e=>{state.renteCur=parseFloat(e.target.value); renderRente();};
  if(rn) rn.oninput=e=>{state.renteNew=parseFloat(e.target.value); renderRente();};
  attachMethodBadges();
}

/* === Gjeldsbildet — utvidet drill-down med KS/TBU/KBN-bakteppe =============== */
function renderGjeld(){
  if(typeof GJELD_DATA === 'undefined') return;
  const host = document.getElementById('gjeldContent');
  if(!host) return;
  // Velg scope: aktivt fylke eller hele landsdelen
  const scope = (state.fylke && state.fylke !== 'Alle') ? state.fylke : 'landsdel';
  const data = scope === 'landsdel' ? GJELD_DATA.landsdel : (GJELD_DATA.fylker[state.fylke] || GJELD_DATA.landsdel);
  const scopeNavn = scope === 'landsdel' ? 'Nord-Norge' : state.fylke;
  const bakteppe = GJELD_DATA.bakteppe || {};
  const sektor = bakteppe.sektor || {};
  const lanekilder = bakteppe.lanekilder || [];
  const rb = bakteppe.rentebinding || {};

  // Tall: konverter 1000 kr → mrd kr for store tall
  const mrd = v => v != null ? (v/1e6).toFixed(1).replace('.',',') : '–';
  const mill = v => v != null ? (v/1e3).toFixed(0).replace('.',',') : '–';
  // Samme avrunding som stolpediagrammet, så tekst og figur viser samme tall
  const pct = v => v != null ? (Math.round(v * 10) / 10).toFixed(1).replace('.',',') + ' %' : '–';

  // Per-innbygger: trenger befolkning fra K
  const scopePop = (function(){
    if(scope === 'landsdel') return K.reduce((s,k)=>s+(k.pop||0), 0);
    return K.filter(k => k.fylke === state.fylke).reduce((s,k)=>s+(k.pop||0), 0);
  })();
  const krPerInnb = v => v != null && scopePop ? Math.round(v*1000/scopePop).toLocaleString('nb-NO') : '–';

  // ─── KPI-rad ───
  // Total gjeld (langsiktig), årlige renter, årlige avdrag, samlet gjeldsbetjening
  const ksNorm = EXT_NORMS.ksGjeld; // samme grense som indikatortellingen
  const nlanColor = data.nlan_pct > ksNorm ? 'var(--neg)' : (data.nlan_pct > ksNorm*0.9 ? 'var(--amber)' : 'var(--pos)');
  const kpiHTML =
    '<div class="kpi-rad" style="margin:8px 0 14px">' +
      '<div class="kpi"><div class="v">' + mrd(data.lan_kr) + ' mrd</div><div class="l">Langsiktig gjeld</div><div class="nh">' + pct(data.lan_pct) + ' av brutto driftsinntekter</div></div>' +
      '<div class="kpi"><div class="v" style="color:' + nlanColor + '">' + pct(data.nlan_pct) + '</div><div class="l">Netto lånegjeld</div><div class="nh">Anbefalt øvre grense ' + ksNorm + ' %</div></div>' +
      '<div class="kpi"><div class="v down">' + mill(data.gjb_kr) + ' mill</div><div class="l">Renter + avdrag/år</div><div class="nh">' + pct(data.gjb_pct) + ' av inntektene</div></div>' +
      '<div class="kpi"><div class="v">' + krPerInnb(data.gjb_kr) + ' kr</div><div class="l">Per innbygger</div><div class="nh">gjeldsbetjening 2025</div></div>' +
    '</div>';

  // ─── "Hva binder kommunekassen?" — sammenlign gjeldsbetjening med sektorutgifter ───
  // Sektorandeler hentes fra DATA.proj.kostra_bench (vektet snitt for scopet)
  const KB = (DATA.proj && DATA.proj.kostra_bench) || {};
  const bench = KB[scope === 'landsdel' ? 'Alle' : state.fylke] || KB['Alle'] || {};
  // bench har sektor i % — gjeldsbetjening er i % av BDI; sektor er i % av netto driftsutgifter
  // Begge bruker driftstall, så vi viser dem som sammenlignbare for å gi STØRRELSE-følelse
  const sektorRader = [
    {navn:'Pleie og omsorg',    pct: bench.omsorg_pct,  col:'var(--amber)',  type:'sektor'},
    {navn:'Grunnskole',         pct: bench.skole_pct,   col:'var(--nl)',     type:'sektor'},
    {navn:'Barnehage',          pct: bench.bhg_pct,     col:'var(--aurora)', type:'sektor'},
    {navn:'Renter + avdrag',    pct: data.gjb_pct,      col:'var(--neg)',       type:'gjeld'},
    {navn:'Kommunehelse',       pct: bench.khelse_pct,  col:'var(--cat-3)',       type:'sektor'},
    {navn:'Kultur',             pct: bench.kultur_pct,  col:'var(--gold)',   type:'sektor'},
  ].filter(r => r.pct != null);
  sektorRader.sort((a,b) => b.pct - a.pct);
  const compareHTML =
    '<div class="ch" style="margin-top:18px"><h3 class="serif" style="font-size:16px">Hva binder kommunekassen?</h3></div>' +
    '<p class="hint" style="font-size:12.5px;margin-bottom:8px">Gjeldsbetjening (renter + avdrag) i ' + scopeNavn + ' er <b>' + pct(data.gjb_pct) + '</b> av driftsinntektene — sammenlignet med de største sektorenes andel av driftsutgiftene. Gjeldsbetjening kommer på linje med en mellomstor utgiftspost, men er <b>låst</b> og kan ikke kuttes slik tjenester kan.</p>' +
    NN.placeholder('hstolper', {format:'pst', grupper:[{rader: sektorRader.map(r => ({
      l: r.navn + (r.type === 'gjeld' ? ' †' : ''), v: Math.round(r.pct * 10) / 10, farge: r.col, uthev: r.type === 'gjeld',
      note: r.type === 'gjeld' ? 'av inntekter' : 'av utgifter'
    }))}]}, sektorRader.length * 34 + 30) +
    '<p class="hint" style="font-size:11.5px;margin-top:8px;opacity:.75;font-style:italic">† = gjeldsbetjening. Tallet er regnet av brutto driftsinntekter; sektorene er regnet av netto driftsutgifter. Sammenligningen viser <i>relativ størrelse</i>, ikke samme nevner.</p>';

  // ─── Lånekilder — nasjonalt bakteppe (SSB K2, tabell 06718) ───
  const lkMeta = bakteppe.lanekilder_meta || {};
  const f1l = v => (Math.round(v * 10) / 10).toFixed(1).replace('.', ',');
  const lkMax = Math.max.apply(null, lanekilder.map(l => l.andel_pct));
  const stolpe = (navn, andel, sub, farge, inn) =>
    '<div style="display:grid;grid-template-columns:minmax(150px,240px) 1fr;gap:10px;align-items:center' + (inn ? ';margin-top:-2px' : '') + '">' +
      '<div style="font-size:' + (inn ? '11.5px' : '12.5px') + ';color:' + (inn ? 'var(--ink2)' : 'var(--ink)') + ';font-weight:' + (inn ? 400 : 500) + ';text-align:right">' + (inn ? 'herav ' : '') + navn + '</div>' +
      '<div style="display:flex;align-items:center;gap:8px"><div style="height:' + (inn ? 10 : 16) + 'px;width:' + (andel / lkMax * 80).toFixed(1) + '%;background:' + farge + '"></div>' +
      '<span style="font-family:var(--font-mono);font-size:11.5px;color:var(--ink)">' + f1l(andel) + ' %</span>' + (sub ? '<span style="font-size:11px;color:var(--ink3)">' + sub + '</span>' : '') + '</div>' +
    '</div>';
  const lanekildeHTML =
    '<div class="ch" style="margin-top:24px"><h3 class="serif" style="font-size:16px">Hvor lånes pengene fra? <span style="font-size:11px;color:var(--ink3);font-weight:400">— kommunesektoren i hele landet</span></h3></div>' +
    '<p class="hint" style="font-size:12.5px;margin-bottom:8px">Kommunesektoren skyldte <b>' + (lkMeta.total_mrd ? f1l(lkMeta.total_mrd) : '–') + ' milliarder kroner</b> til norske långivere i ' + (lkMeta.periode_navn || lkMeta.periode || '') + '. Banker og kredittforetak — i praksis Kommunalbanken — står for nesten halvparten, og nær en tredjedel er tatt opp direkte i obligasjons- og sertifikatmarkedet. Tallene gjelder sektoren samlet; sammensetningen varierer mellom kommunene.</p>' +
    '<div style="display:flex;flex-direction:column;gap:6px;margin-top:6px">' +
    lanekilder.map((l, i) =>
      stolpe(l.navn, l.andel_pct, l.belop_mrd != null ? f1l(l.belop_mrd) + ' mrd kr' : '', i === 0 ? 'var(--accent)' : 'var(--muted-mark)', false) +
      (l.herav || []).map(h => stolpe(h.navn, h.andel_pct, h.note, 'color-mix(in srgb, var(--accent) 55%, transparent)', true)).join('')
    ).join('') +
    '</div>' +
    '<p class="hint" style="font-size:11px;opacity:.8;margin-top:6px">Kilde: ' + (lkMeta.kilde || 'SSB 06718') + '. Kommunalbankens andel er avledet: bankens egen markedsandel (' + (lanekilder[0] && lanekilder[0].herav && lanekilder[0].herav[0].markedsandel ? f1l(lanekilder[0].herav[0].markedsandel.verdi) + ' % i ' + lanekilder[0].herav[0].markedsandel.periode : '') + ') regnes uten Husbanken i nevneren og er omregnet til andel av all gjeld. Gjeld til utenlandske långivere er ikke med.</p>';

  // ─── Rentebinding (SSB tabell 10648: lån fra banker og kredittforetak) ───
  const rbFl = rb.flytende_pct, rbKort = rb.kort_pct, rbLang = rb.lang_pct;
  const rbTrend = rb.flytende_trend ? Object.keys(rb.flytende_trend).sort() : [];
  const rbFoerste = rbTrend.length ? rbTrend[0] : null;
  const segment = (andel, farge, tekst) => andel > 0 ? '<div style="width:' + andel + '%;background:' + farge + ';display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:11.5px;white-space:nowrap;overflow:hidden">' + tekst + '</div>' : '';
  const rentebindingHTML = rbFl == null ? '' :
    '<div class="ch" style="margin-top:24px"><h3 class="serif" style="font-size:16px">Fastrente eller flytende?</h3></div>' +
    '<p class="hint" style="font-size:12.5px;margin-bottom:8px">Av kommunesektorens lån i banker og kredittforetak (' + f1l(rb.grunnlag_mrd) + ' milliarder kroner, ' + f1l(rb.andel_av_gjelden_pct) + ' % av gjelden) hadde <b>' + f1l(rbFl) + ' %</b> flytende rente ved utgangen av ' + (rb.periode_navn || rb.periode) + '. ' +
      (rbFoerste && rbFoerste !== rb.periode ? 'Andelen har falt fra ' + f1l(rb.flytende_trend[rbFoerste]) + ' % i ' + ((rb.trend_navn && rb.trend_navn[rbFoerste]) || rbFoerste) + ' — sektoren har bundet mer av renten. ' : '') +
      'Når renten endres, slår det raskest ut på den flytende delen.</p>' +
    '<div style="display:flex;height:30px;border-radius:0;overflow:hidden;border:1px solid var(--line2);margin:8px 0">' +
      segment(rbFl, 'var(--amber)', 'Flytende ' + f1l(rbFl) + ' %') +
      segment(rbKort, 'color-mix(in srgb, var(--cat-3) 60%, var(--amber))', f1l(rbKort) + ' %') +
      segment(rbLang, 'var(--cat-3)', 'Bundet over 1 år ' + f1l(rbLang) + ' %') +
    '</div>' +
    '<div style="display:flex;gap:14px;flex-wrap:wrap;font-size:11px;color:var(--ink2)"><span><i style="display:inline-block;width:10px;height:10px;background:var(--amber);margin-right:4px"></i>Inntil 3 måneder (flytende)</span><span><i style="display:inline-block;width:10px;height:10px;background:color-mix(in srgb, var(--cat-3) 60%, var(--amber));margin-right:4px"></i>3–12 måneder</span><span><i style="display:inline-block;width:10px;height:10px;background:var(--cat-3);margin-right:4px"></i>Over 1 år</span></div>' +
    '<p class="hint" style="font-size:11.5px;margin-top:8px">For resten av gjelden finnes ingen samlet statistikk. Sertifikatlånene har høyst tolv måneders løpetid. Kommunalbanken hadde fastrente på ' + f1l(rb.kbn_fastrente.verdi) + ' % av utlånene (' + rb.kbn_fastrente.periode + '), og ' + rb.klpkk_flytende.verdi + ' % av KLP Kommunekreditts utlån har flytende rente (' + rb.klpkk_flytende.periode + '). Gjennomsnittlig avdragstid i sektoren er ' + ((bakteppe.lopetid && bakteppe.lopetid.tekst) || '25–30 år') + ' (' + ((bakteppe.lopetid && bakteppe.lopetid.kilde) || 'TBU') + ').</p>' +
    '<p class="hint" style="font-size:11px;opacity:.8">Kilde: ' + rb.kilde + '; ' + rb.kbn_fastrente.kilde + '; ' + rb.klpkk_flytende.kilde + '.</p>';

  // ─── Sektornivå-konklusjon (KOSTRA, kommunekonsern, fra SSB 12143) ───
  const KO = bakteppe.kostra || null;
  const sAar = sektor.aar || (KO && KO.aar) || 2025;
  const sForrige = (KO && KO.forrige_aar) || sAar - 1;
  const sv = k => sektor[k];
  const kort = (verdi, farge, tittel, under) =>
    '<div style="padding:12px 14px;background:var(--paper2);border:1px solid var(--line2);border-radius:0"><div style="font-family:var(--font-mono);font-size:18px;font-weight:700;color:' + farge + '">' + verdi + '</div><div style="font-size:11.5px;color:var(--ink2)">' + tittel + '</div><div style="font-size:10.5px;color:var(--ink3);margin-top:2px">' + under + '</div></div>';
  const ndrS = sv('netto_driftsresultat_' + sAar + '_pct'), fondS = sv('disposisjonsfond_' + sAar + '_pct');
  const nlanS = sv('netto_lanegjeld_' + sAar + '_pct'), finS = sv('finansutgifter_endring_' + sForrige + '_' + sAar + '_pct');
  const f1 = v => Math.abs(v).toFixed(1).replace('.', ',');
  const fmtSgn = v => v == null ? '–' : (v >= 0 ? '+' : '−') + f1(v) + ' %';
  const sektorKort =
    (ndrS != null ? kort(fmtSgn(ndrS), ndrS >= sektor.ks_norm_ndr_kommune_pct ? 'var(--pos)' : 'var(--amber)', 'Netto driftsresultat ' + sAar, 'TBU-norm: ' + fmt(sektor.ks_norm_ndr_kommune_pct) + ' % · ' + sForrige + ': ' + fmtSgn(sv('netto_driftsresultat_' + sForrige + '_pct'))) : '') +
    (fondS != null ? kort(f1(fondS) + ' %', fondS >= sektor.ks_norm_disposisjonsfond_pct ? 'var(--pos)' : 'var(--amber)', 'Disposisjonsfond ' + sAar, 'KS: om lag ' + fmt(sektor.ks_norm_disposisjonsfond_pct) + ' % i snitt') : '') +
    (nlanS != null ? kort(f1(nlanS) + ' %', nlanS > ksNorm ? 'var(--neg)' : 'var(--pos)', 'Netto lånegjeld ' + sAar, (nlanS > ksNorm ? 'Over' : 'Under') + ' KS-grensen (' + fmt(ksNorm) + ' %) · ' + sForrige + ': ' + fmt(sv('netto_lanegjeld_' + sForrige + '_pct')) + ' %') : '') +
    (finS != null ? kort(fmtSgn(finS), finS > 0 ? 'var(--neg)' : 'var(--pos)', 'Netto finansutgifter, endring i kroner', sForrige + '–' + sAar + ' · renter ' + fmtSgn(sv('rente_endring_' + sForrige + '_' + sAar + '_pct'))) : '');
  // Sammenligning: landet og de tre nordnorske fylkene (summert for kommunene i området)
  let sektorTabell = '';
  if (KO && KO.omrader) {
    const rekke = ['Landet', 'Landet uten Oslo', 'Nordland', 'Troms', 'Finnmark'].filter(n => KO.omrader[n]);
    const aktivt = (state.fylke && state.fylke !== 'Alle') ? state.fylke : null;
    const celle = (v, bra) => '<td style="text-align:right;font-family:var(--font-mono);padding:5px 8px;color:' + (v == null ? 'var(--ink3)' : bra ? 'var(--ink)' : 'var(--neg)') + '">' + (v == null ? '–' : (v < 0 ? '−' : '') + f1(v) + ' %') + '</td>';
    sektorTabell =
      '<div style="overflow-x:auto;margin-top:12px"><table style="width:100%;border-collapse:collapse;font-size:12px">' +
      '<thead><tr style="color:var(--ink3);font-size:10.5px;text-transform:uppercase;letter-spacing:.06em"><th style="text-align:left;padding:5px 8px">' + sAar + ', % av brutto driftsinntekter</th><th style="text-align:right;padding:5px 8px">Netto driftsresultat</th><th style="text-align:right;padding:5px 8px">Disposisjonsfond</th><th style="text-align:right;padding:5px 8px">Netto lånegjeld</th><th style="text-align:right;padding:5px 8px">Renter og avdrag</th></tr></thead><tbody>' +
      rekke.map(n => { const o = KO.omrader[n]; const uth = n === aktivt || (!aktivt && n === 'Landet');
        return '<tr style="border-top:1px solid var(--line2)' + (uth ? ';background:color-mix(in srgb, var(--accent) 8%, transparent)' : '') + '"><td style="padding:5px 8px;' + (uth ? 'font-weight:600' : '') + '">' + n + '</td>' +
          celle(o.ndr, o.ndr != null && o.ndr >= sektor.ks_norm_ndr_kommune_pct) + celle(o.fond, o.fond != null && o.fond >= sektor.ks_norm_disposisjonsfond_pct) + celle(o.nlan, o.nlan != null && o.nlan <= ksNorm) + celle(o.gjeldsbetjening, true) + '</tr>'; }).join('') +
      '</tbody></table></div>' +
      '<p class="hint" style="font-size:11px;margin-top:6px">Kommunene i området summert (kommunekonsern), ikke median. Rødt = svakere enn normen (TBU 1,75 % netto driftsresultat, KS om lag 5 % disposisjonsfond, KS 85 % netto lånegjeld). Kilde: ' + KO.kilde + '.</p>';
  }
  const sektorHTML =
    '<div class="ch" style="margin-top:24px"><h3 class="serif" style="font-size:16px">Sektorbildet ' + sAar + ' — kommunene i landet</h3></div>' +
    '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:8px">' + sektorKort + '</div>' +
    sektorTabell +
    '<p class="hint" style="font-size:12px;margin-top:10px;font-style:italic">Normer: ' + sektor.tbu_kilde + ' og ' + sektor.ks_kilde + '. KS-anbefalingen er at bufferne skal tåle <b>' + sektor.ks_buffer_test + '</b>.</p>';

  // ─── Avslutning + kilde ───
  const overHer = data.nlan_pct != null && data.nlan_pct > ksNorm, overLand = nlanS != null && nlanS > ksNorm;
  const normSetning = 'KS-grensen på ' + ksNorm + ' % netto lånegjeld er ' +
    (overHer && overLand ? 'overskredet både her (' + pct(data.nlan_pct) + ') og for kommunene i landet samlet (' + fmt(nlanS) + ' %).'
      : overHer ? 'overskredet her (' + pct(data.nlan_pct) + '), men ikke for landet samlet (' + fmt(nlanS) + ' %).'
      : overLand ? 'ikke overskredet her (' + pct(data.nlan_pct) + '), men for kommunene i landet samlet (' + fmt(nlanS) + ' %).'
      : 'ikke overskredet her (' + pct(data.nlan_pct) + ').');
  const closingHTML =
    '<p class="sub" style="margin-top:18px;padding:14px 16px;background:color-mix(in srgb, var(--neg) 6%, transparent);border-left:4px solid var(--neg);border-radius:0">' +
      '<b>Gjeld er ikke et problem fordi tallet er stort. Det er fordi det er låst.</b> Av ' + (/s$/.test(scopeNavn) ? scopeNavn + "'" : scopeNavn + 's') + ' driftsinntekter går <b>' + pct(data.gjb_pct) + '</b> til renter og avdrag — på linje med en mellomstor sektor som ' + (sektorRader.find(r => Math.abs(r.pct - data.gjb_pct) < 2 && r.type === 'sektor')?.navn || 'kommunehelse').toLowerCase() + '. Forskjellen: gjeldsbetjening kan ikke kuttes når aldring presser tjenestebehovet de neste 25 årene. ' + normSetning +
    '</p>' +
    '<p class="hint" style="font-size:11px;margin-top:10px;opacity:.75">Kilder: SSB KOSTRA tab. 12143 (kommuner og sektortall); ' + bakteppe.kilde + '. Sist oppdatert: ' + bakteppe.sist_oppdatert + '. Sektortallene hentes fra SSB ved hver kjøring av fetch_gjeld.py; lånekilder og rentebinding oppdateres manuelt.</p>';

  host.innerHTML = kpiHTML + compareHTML + lanekildeHTML + rentebindingHTML + sektorHTML + closingHTML;
}

/* === Pensjon: premieavvik og fremskrevet pensjonskostnad (PENSJON_DATA, fetch_pensjon.py) ===
   renderPensjon() fyller #pensjonContent på landsdels- og fylkessiden for valgt scope.
   pensjonFigur(o, hoyde) gir viftediagrammet (basis med lav–høy-bånd) for et kommune-, fylkes- eller landsdelsobjekt. */
function pensjonFigur(o, hoyde){
  const P = PENSJON_DATA;
  return NN.placeholder('linjer', {
    x: P.aar,
    serier: [
      {navn:'Høyt scenario', kort:'Høy', data:o.R.hoy, farge:'muted', stil:'stiplet'},
      {navn:'Basis', kort:'Basis', data:o.R.basis, farge:'accent', uthev:true},
      {navn:'Lavt scenario', kort:'Lav', data:o.R.lav, farge:'muted', stil:'stiplet'}
    ],
    band: {x:P.aar, lo:o.R.lav, hi:o.R.hoy, farge:'accent'},
    markor: [{x:2027}, {x:2033}],
    format:'pst1', null:true, xTicks:[2025,2030,2040,2050], hoyde: hoyde || 280,
    kilde:'Regnskapsført pensjonskostnad inkl. arbeidsgiveravgift, % av brutto driftsinntekter. Egne beregninger på grunnlag av pensjonsnotene 2025, KOSTRA (SSB 13202, 12364, 12367) og KDDs beregningsforutsetninger.'
  }, (hoyde || 280) + 20);
}
function pensjonTall(v, d){
  if(v == null) return '–';
  const f = Math.pow(10, d == null ? 1 : d), r = Math.round(Math.abs(v) * f) / f;
  return (v < 0 && r ? '−' : '') + r.toFixed(d == null ? 1 : d).replace('.', ',');
}
function renderPensjon(){
  if(typeof PENSJON_DATA === 'undefined') return;
  const host = document.getElementById('pensjonContent');
  if(!host) return;
  const P = PENSJON_DATA, M = P.meta;
  const fy = (state.fylke && state.fylke !== 'Alle') ? state.fylke : null;
  const o = fy ? P.fylker[fy] : P.landsdel;
  const scopeNavn = fy || 'Nord-Norge';
  const p1 = v => pensjonTall(v) + ' %';
  const i30 = P.aar.indexOf(2030), i50 = P.aar.indexOf(2050);
  const ks = currentK().filter(k => P.kommuner[k.nr]);
  const kn = k => (k.navn.split(' - ').find(d => !/[áčđŋšŧžÁČĐŊŠŦŽäÄ]/.test(d)) || k.navn);

  const kpiHTML =
    '<div class="kpi-rad" style="margin:8px 0 14px">' +
      '<div class="kpi"><div class="v' + (o.pa > M.landet_pa ? ' down' : '') + '">' + p1(o.pa) + '</div><div class="l">Akkumulert premieavvik</div><div class="nh">' + pensjonTall(o.pa_kr / 1e6) + ' mrd kr · landet ' + p1(M.landet_pa) + '</div></div>' +
      '<div class="kpi"><div class="v">' + p1(o.df) + '</div><div class="l">Disposisjonsfond</div><div class="nh">premieavviket er større i ' + o.pa_over_df + ' av ' + o.n + ' kommuner</div></div>' +
      '<div class="kpi"><div class="v">' + p1(o.R.basis[i30]) + '</div><div class="l">Pensjonskostnad 2030</div><div class="nh">basis · ' + p1(o.R.basis[0]) + ' i 2025 · spenn ' + pensjonTall(o.R.lav[i30]) + '–' + p1(o.R.hoy[i30]) + '</div></div>' +
      '<div class="kpi"><div class="v">' + p1(o.R.basis[i50]) + '</div><div class="l">Pensjonskostnad 2050</div><div class="nh">basis · spenn ' + pensjonTall(o.R.lav[i50]) + '–' + p1(o.R.hoy[i50]) + '</div></div>' +
    '</div>';

  const leadHTML =
    '<p class="hint" style="font-size:12.5px;margin-bottom:8px">Kommunene i ' + scopeNavn + ' har betalt ' + pensjonTall(o.pa_kr / 1e6) + ' milliarder kroner mer i pensjonspremie enn de har ført som kostnad — <b>' + p1(o.pa) + '</b> av driftsinntektene (' + p1(o.pa24) + ' året før). ' +
    'Beløpet utgiftsføres som hovedregel over de neste sju årene. Pensjonsordningene er fullt finansiert; risikoen ligger i at etterslepet skal utgiftsføres, og i at premien i dag holdes nede av KLPs overskudd på premiefondet.</p>';

  const figHTML =
    '<div class="ch" style="margin-top:16px"><h3 class="serif" style="font-size:16px">Pensjonskostnaden i ' + scopeNavn + ' fram mot 2050</h3></div>' +
    pensjonFigur(o, 280) +
    '<p class="hint" style="font-size:11.5px;margin-top:6px">Basis er uthevet; feltet viser spennet mellom lavt og høyt scenario. Stiplede linjer: 2027, når forholdstallet senkes til 0,75, og 2033, når dagens etterslep er utgiftsført. Årene 2026–2027 er kalibrert mot kommunebudsjetter og er usikre. I høyt scenario dekker premiefondet bare en firedel av 2025-nivået, og premien kommunene betaler stiger fra ' + p1(o.P25) + ' til ' + p1(o.P30.hoy) + ' av driftsinntektene i 2030.</p>';

  const rader = ks.map(k => { const d = P.kommuner[k.nr]; return {l:kn(k), v:Math.round(d.pa * 10) / 10, farge: d.pa > d.df ? 'warn' : 'muted', note:'fond ' + pensjonTall(d.df) + ' %'}; })
    .sort((a, b) => b.v - a.v);
  const listeHTML =
    '<div class="ch" style="margin-top:22px"><h3 class="serif" style="font-size:16px">Premieavvik per kommune, 2025</h3></div>' +
    '<p class="hint" style="font-size:12px;margin-bottom:6px">Akkumulert premieavvik i % av driftsinntektene. Oransje: premieavviket er større enn disposisjonsfondet (vist til høyre). Det er ikke en norm, men viser om kommunen har oppspart buffer som kan bære amortiseringen.</p>' +
    NN.placeholder('hstolper', {format:'pst', grupper:[{rader:rader, ref:{v:M.landet_pa, tekst:'Landet ' + p1(M.landet_pa)}}],
      kilde:'Kilde: SSB 13202 og 12364 (KOSTRA 2025, kommunekonsern). Premieavvik netto, inkl. arbeidsgiveravgift.'}, rader.length * (rader.length > 40 ? 17 : 27) + 60);

  const kasser = M.org.kasser.filter(x => !fy || ks.some(k => String(k.nr) === x.nr));
  const orgHTML =
    '<p class="hint" style="font-size:12.5px;margin-top:14px"><b>Hvem bærer risikoen?</b> ' +
    (kasser.length ? kasser.map(x => x.navn + ' (solvenskapitaldekning ' + x.solvens_pct + ' %)').join(', ') + (kasser.length > 1 ? ' er egne kommunale kasser' : ' er en egen kommunal kasse') + '; de øvrige kommunene har fellesordningen i KLP (' + M.org.klp_solvens_pct + ' %). '
      : 'Alle kommunene i ' + scopeNavn + ' har fellesordningen i KLP (solvenskapitaldekning ' + M.org.klp_solvens_pct + ' %). ') +
    'Lærerne er i Statens pensjonskasse. Hele bildet: <a href="tema-pensjon.html">Pensjonsetterslepet</a> · <a href="metode.html#pensjon">metode</a>.</p>' +
    '<p class="hint" style="font-size:11px;opacity:.75">Kilder: ' + M.kilde + '. Sist oppdatert: ' + M.sist_oppdatert + '.</p>';

  host.innerHTML = kpiHTML + leadHTML + figHTML + listeHTML + orgHTML;
}
// Pensjonsblokk på kommunesiden (fanen Pensjon)
function pensjonKommuneCard(k){
  if(typeof PENSJON_DATA === 'undefined') return '';
  const P = PENSJON_DATA, M = P.meta, d = P.kommuner[String(k.nr)];
  if(!d) return '';
  const p1 = v => pensjonTall(v) + ' %';
  const i30 = P.aar.indexOf(2030), i50 = P.aar.indexOf(2050);
  const navn = (k.navn.split(' - ').find(x => !/[áčđŋšŧžÁČĐŊŠŦŽäÄ]/.test(x)) || k.navn);
  const overDf = d.pa > d.df;
  const egen = d.lev !== 'KLP';
  const dR = d.R.basis[i50] - d.R.basis[0];
  const belop = d.pa_kr >= 1e6 ? pensjonTall(d.pa_kr / 1e6) + ' milliarder' : Math.round(d.pa_kr / 1000).toLocaleString('nb-NO') + ' millioner';
  let tekst = '<b>' + navn + '</b> har ' + belop + ' kroner i premieavvik som ennå ikke er utgiftsført — <b>' + p1(d.pa) + '</b> av driftsinntektene, mot ' + p1(M.landet_pa) + ' for landet. ';
  tekst += overDf ? 'Det er mer enn disposisjonsfondet (' + p1(d.df) + '), så kommunen har ikke oppspart buffer som dekker etterslepet. ' : 'Disposisjonsfondet (' + p1(d.df) + ') er større enn etterslepet. ';
  tekst += d.amort === 1 ? 'Kommunen utgiftsfører premieavviket året etter, så etterslepet bygges ikke opp. ' : 'Beløpet utgiftsføres som hovedregel over de neste sju årene. ';
  tekst += 'Regnskapsført pensjonskostnad er ' + p1(d.R.basis[0]) + ' av driftsinntektene i 2025 og ' + p1(d.R.basis[i50]) + ' i 2050 i basisscenariet' +
    (d.amort !== 1 && Math.abs(dR) >= 0.5 ? ' — ' + (dR > 0 ? 'en økning' : 'en nedgang') + ' på ' + pensjonTall(Math.abs(dR)) + ' prosentpoeng' : '') + '. ' +
    (d.amort === 1 ? 'Med ettårig amortisering føres hele fjorårets avvik i ett år, så kostnaden svinger mer fra år til år enn kurven viser. ' : '');
  const grunnlag = d.grunnlag === 'note' ? 'Pensjonsnoten i årsregnskapet 2025' : 'Bare KOSTRA — kostnaden er anslått';
  // Innbetalinger 2025 fra pensjonsnoten; for byene med egen pensjonskasse (Bodø, Tromsø, Harstad) også tall fra kassens årsrapport
  let innbetHTML = '';
  const b = d.innbet;
  if(b){
    const m = v => v == null ? 'ikke oppgitt' : pensjonTall(v);
    const rad = (t, v, sterk) => '<tr' + (sterk ? ' style="font-weight:600"' : '') + '><td style="padding:5px 8px;text-align:left">' + t + '</td><td style="padding:5px 8px;text-align:right;font-family:var(--font-mono);font-variant-numeric:tabular-nums">' + v + '</td></tr>';
    innbetHTML =
      '<h4 class="serif" style="font-size:14.5px;margin:18px 0 4px">Innbetalinger 2025</h4>' +
      '<p class="hint" style="font-size:12px;margin:0 0 6px">Fra pensjonsnoten i årsregnskapet, millioner kroner. Gjelder alle ordningene samlet: ' + (egen ? d.lev + ', KLP for sykepleierne' : 'KLP') + ' og Statens pensjonskasse for lærerne. Kostnaden er premie minus premieavvik, inkludert administrasjon.</p>' +
      '<div style="overflow-x:auto"><table style="width:100%;max-width:560px;border-collapse:collapse;font-size:12.5px"><tbody>' +
        (b.pf_bruk != null || egen ? rad('Premie før bruk av premiefond' + (b.premie_for_pf_beregnet ? ' (beregnet)' : ''), m(b.premie_for_pf)) +
          rad('Bruk av premiefond', b.pf_bruk == null ? 'ikke oppgitt' : '−' + pensjonTall(b.pf_bruk)) : '') +
        '<tr style="border-top:2px solid var(--ink);font-weight:600"><td style="padding:5px 8px">Innbetalt premie</td><td style="padding:5px 8px;text-align:right;font-family:var(--font-mono);font-variant-numeric:tabular-nums">' + pensjonTall(b.premie) + '</td></tr>' +
        rad('Beregnet pensjonskostnad', pensjonTall(b.kostnad)) +
        rad('Årets premieavvik', pensjonTall(b.avvik)) +
        (b.ek_2025.length ? b.ek_2025.map(e => rad('Egenkapitalinnskudd til ' + e[0], pensjonTall(e[1], e[1] < 1 ? 2 : 1))).join('') : (egen ? rad('Egenkapitalinnskudd', 'ingen årlige') : '')) +
      '</tbody></table></div>' +
      (b.kasse_premie == null ? (b.pf_bruk == null ? '<p class="hint" style="font-size:11.5px;margin-top:6px">Noten oppgir ikke bruk av premiefond.</p>' : '') : '<p class="hint" style="font-size:11.5px;margin-top:6px">Fra kassens årsrapport for 2025 (alle medlemsforetak): ' +
        (b.sats_2025 != null ? b.sats_tekst.charAt(0).toUpperCase() + b.sats_tekst.slice(1) + ' ' + pensjonTall(b.sats_2025, 2) + ' % av pensjonsgrunnlaget (' + pensjonTall(b.sats_2024, 2) + ' % i 2024). ' : 'Premiesats i prosent av lønn er ikke oppgitt. ') +
        (b.reg_2025 != null ? 'Reguleringspremie ' + pensjonTall(b.reg_2025) + ' mill. kr (' + pensjonTall(b.reg_2024) + ' i 2024). ' : '') +
        'Kassens ' + b.kasse_premie_tekst + ' ' + pensjonTall(b.kasse_premie) + ' mill. kr. Innskutt egenkapital fra kommunen i alt ' + pensjonTall(b.ek_innskutt_mill) + ' mill. kr. ' + b.note +
        ' <a href="' + b.kilde + '" target="_blank" rel="noopener">Kassens årsrapport</a></p>');
  }
  const tagCol = d.grunnlag === 'note' && !d.svak ? 'var(--ink2)' : 'var(--warn)';
  return '<div class="ch" style="margin-top:18px">' +
      '<div class="h-row" style="display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap"><h3 class="serif" style="font-size:16px">Pensjon — etterslepet og kostnaden fram mot 2050</h3>' +
      '<span class="tag" style="font-size:11px;color:' + tagCol + '">' + grunnlag + '</span></div>' +
      '<div class="kpi-rad" style="margin:10px 0 12px">' +
        '<div class="kpi"><div class="v' + (d.pa > M.landet_pa ? ' down' : '') + '">' + p1(d.pa) + '</div><div class="l">Akkumulert premieavvik</div><div class="nh">av driftsinntektene · landet ' + p1(M.landet_pa) + '</div></div>' +
        '<div class="kpi"><div class="v">' + p1(d.df) + '</div><div class="l">Disposisjonsfond</div><div class="nh">' + (overDf ? 'mindre enn premieavviket' : 'større enn premieavviket') + '</div></div>' +
        '<div class="kpi"><div class="v">' + p1(d.R.basis[i30]) + '</div><div class="l">Pensjonskostnad 2030</div><div class="nh">basis · ' + p1(d.R.basis[0]) + ' i 2025 · spenn ' + pensjonTall(d.R.lav[i30]) + '–' + p1(d.R.hoy[i30]) + '</div></div>' +
        '<div class="kpi"><div class="v">' + p1(d.R.basis[i50]) + '</div><div class="l">Pensjonskostnad 2050</div><div class="nh">basis · spenn ' + pensjonTall(d.R.lav[i50]) + '–' + p1(d.R.hoy[i50]) + '</div></div>' +
      '</div>' +
      '<p class="hint" style="font-size:12.5px;margin-bottom:8px">' + tekst + '</p>' +
      pensjonFigur(d, 240) +
      innbetHTML +
      '<p class="hint" style="font-size:11.5px;margin-top:6px">' +
        (egen ? 'Fellesordningen ligger i ' + d.lev + ', en egen kommunal pensjonskasse; kommunen bærer selv risikoen for avkastning, uførhet og levealder. ' : 'Fellesordningen ligger i KLP, der risikoen deles med om lag 330 kommuner. ') +
        'Lærerne er i Statens pensjonskasse. Amortiseringstid: ' + d.amort + ' år. Stiplede linjer: 2027 (forholdstall 0,75) og 2033 (dagens etterslep utgiftsført). Årene 2026–2027 er kalibrert mot kommunebudsjetter og er usikre. ' +
        (d.svak ? '<b>Forbehold:</b> ' + d.svak + ' ' : '') +
        (d.url ? '<a href="' + d.url + '" target="_blank" rel="noopener">Årsregnskapet 2025</a> · ' : '') +
        '<a href="tema-pensjon.html?k=' + k.nr + '#framover">Pensjonsetterslepet</a> · <a href="metode.html#pensjon">metode</a></p>' +
    '</div>';
}

/* === Husholdninger × type × inntekt — SSB 06944 =============================== */
/* renderHusholdninger(hostId, scope) — scope: 'kommune-NR', 'fylke-NAVN', 'landsdel'
   Rendrer en utvidbar seksjon med:
   - KPI-rad (andel aleneboende, par med barn, inntektsspennvidde)
   - Stolpegraf inntekt per husholdningstype
   - Stolpegraf antall (sammensetning)
   - Klartekst-tolkning
   - Nivå 2 (utvidbar <details>): tidsserie 2005-2024 */
function renderHusholdninger(hostId, scope){
  if(typeof HUSH_DATA === 'undefined') return;
  const host = document.getElementById(hostId);
  if(!host) return;

  // Hent data for scope
  let data, scopeNavn;
  if(scope.startsWith('kommune-')){
    const nr = scope.slice(8);
    data = HUSH_DATA.kommuner[nr];
    const k = (typeof K !== 'undefined') ? K.find(x => String(x.nr) === nr) : null;
    scopeNavn = k ? k.navn : nr;
  } else if(scope.startsWith('fylke-')){
    const f = scope.slice(6);
    data = HUSH_DATA.fylker[f];
    scopeNavn = f;
  } else {
    data = HUSH_DATA.landsdel;
    scopeNavn = 'Nord-Norge';
  }
  if(!data || !data.latest) return;

  const latest = data.latest;
  const alle = latest.alle || {};
  const alle_n = alle.n;
  const alle_med = alle.median;
  if(!alle_n || !alle_med) { host.innerHTML = '<p class="hint">Husholdningsdata ikke tilgjengelig for denne kommunen.</p>'; return; }

  const fmtKr = n => n != null ? fmt(Math.round(n/1000)*1000)+'' : '–';
  const fmtN = n => n != null ? n.toLocaleString('nb-NO') : '–';
  const fmtPct = (a, b) => b ? ((a/b)*100).toFixed(0).replace('.',',') + ' %' : '–';
  const sgn = v => (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(0).replace('.',',');

  // Type-rekkefølge med farger
  const TYPES = [
    {key:'aleneboende',     label:'Aleneboende',                col:'var(--neg)'},
    {key:'par_uten_barn',   label:'Par uten barn',              col:'var(--amber)'},
    {key:'par_med_barn',    label:'Par med barn 0–17',          col:'var(--pos)'},
    {key:'enslig_forelder', label:'Enslig forelder',            col:'var(--fi)'},
    {key:'andre',           label:'Andre/flerfamilie',          col:'var(--ink3)'},
  ];

  // KPI-rad
  const aleneN = (latest.aleneboende || {}).n || 0;
  const aleneMed = (latest.aleneboende || {}).median;
  const parMedBarnN = (latest.par_med_barn || {}).n || 0;
  const parMedBarnMed = (latest.par_med_barn || {}).median;
  const enslig = (latest.enslig_forelder || {}).n || 0;
  const enkligMed = (latest.enslig_forelder || {}).median;
  const aleneVsMed = aleneMed && alle_med ? ((aleneMed/alle_med - 1) * 100) : null;
  const parVsMed = parMedBarnMed && alle_med ? ((parMedBarnMed/alle_med - 1) * 100) : null;
  const spennMin = aleneMed;
  const spennMax = parMedBarnMed;
  const spennX = spennMin && spennMax ? (spennMax / spennMin) : null;

  const kpiHTML =
    '<div class="kpi-rad" style="margin:8px 0 14px">' +
      '<div class="kpi"><div class="v">' + fmtPct(aleneN, alle_n) + '</div><div class="l">Aleneboende</div><div class="nh">' + fmtN(aleneN) + ' husholdninger</div></div>' +
      '<div class="kpi"><div class="v">' + fmtPct(parMedBarnN, alle_n) + '</div><div class="l">Par med barn</div><div class="nh">' + fmtN(parMedBarnN) + ' husholdninger</div></div>' +
      '<div class="kpi"><div class="v down">' + fmtKr(aleneMed) + '</div><div class="l">Aleneboende median</div><div class="nh">' + (aleneVsMed != null ? sgn(aleneVsMed) + ' % mot kommunemedianen' : 'inntekt etter skatt') + '</div></div>' +
      '<div class="kpi"><div class="v up">' + fmtKr(parMedBarnMed) + '</div><div class="l">Par med barn median</div><div class="nh">' + (parVsMed != null ? sgn(parVsMed) + ' % mot kommunemedianen' : 'inntekt etter skatt') + '</div></div>' +
    '</div>';

  // Inntekt per type — sortert
  const innRader = TYPES
    .map(t => ({...t, n: (latest[t.key] || {}).n, median: (latest[t.key] || {}).median}))
    .filter(r => r.median != null);
  innRader.sort((a, b) => b.median - a.median);
  const inntektsGrafHTML =
    '<div style="font-family:var(--font-display);font-size:14px;font-weight:600;margin:8px 0 6px;color:var(--ink)">Median inntekt etter skatt — per husholdningstype</div>' +
    NN.placeholder('hstolper', {format:'kr', grupper:[{rader: innRader.map(r => ({
      l: r.label, v: Math.round(r.median), farge: r.col, note: sgn((r.median / alle_med - 1) * 100) + ' % mot medianen'
    }))}]}, innRader.length * 34 + 30);

  // Sammensetning — stablet 100 %-stolpe
  const sammensetningRader = TYPES
    .map(t => ({...t, n: (latest[t.key] || {}).n || 0}))
    .filter(r => r.n > 0);
  const sumN = sammensetningRader.reduce((s, r) => s + r.n, 0);
  const segHTML = sammensetningRader.map(r => {
    const pct = (r.n / sumN * 100);
    if(pct < 0.5) return '';
    return '<div style="width:' + pct.toFixed(1) + '%;background:' + r.col + ';display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:12px" title="' + r.label + ' ' + r.n.toLocaleString('nb-NO') + '">' + (pct >= 7 ? pct.toFixed(0).replace('.',',') + ' %' : '') + '</div>';
  }).join('');
  const legendHTML = sammensetningRader.map(r =>
    '<span style="display:inline-flex;align-items:center;gap:5px;font-size:11.5px;color:var(--ink2)"><i style="display:inline-block;width:10px;height:10px;background:' + r.col + ';border-radius:0"></i>' + r.label + ' (' + fmtN(r.n) + ')</span>'
  ).join(' ');
  const sammensetningHTML =
    '<div style="margin-top:18px"><div style="font-family:var(--font-display);font-size:14px;font-weight:600;margin-bottom:6px;color:var(--ink)">Sammensetning — ' + fmtN(sumN) + ' husholdninger i ' + scopeNavn + '</div>' +
    '<div style="display:flex;height:30px;border-radius:0;overflow:hidden;font-size:0">' + segHTML + '</div>' +
    '<div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:8px">' + legendHTML + '</div></div>';

  // Klartekst-tolkning
  const tolkningHTML =
    '<p class="sub" style="margin-top:16px;padding:14px 16px;background:color-mix(in srgb, var(--neg) 6%, transparent);border-left:4px solid var(--neg);border-radius:0;line-height:1.6;font-size:13.5px">' +
    '<b>Medianen forteller ikke alt.</b> ' + (/s$/.test(scopeNavn) ? scopeNavn + "'" : scopeNavn + 's') + ' kommunemedian er <b>' + fmtKr(alle_med) + ' kr</b>, men det skjuler stor variasjon: ' +
    '<b>' + fmtPct(aleneN, alle_n) + '</b> er aleneboende med median <b>' + fmtKr(aleneMed) + ' kr</b> ' + (aleneVsMed != null ? '(' + Math.abs(aleneVsMed).toFixed(0).replace('.',',') + ' % under)' : '') + ', ' +
    'mens par med barn (kun ' + fmtPct(parMedBarnN, alle_n) + ' av husholdningene) har <b>' + fmtKr(parMedBarnMed) + ' kr</b> ' + (parVsMed != null ? '(' + Math.abs(parVsMed).toFixed(0).replace('.',',') + ' % over)' : '') + '. ' +
    (spennX ? 'Forskjellen mellom rikeste og fattigste husholdningstype er <b>' + spennX.toFixed(1).replace('.',',') + ' ganger</b>. ' : '') +
    (enkligMed == null || !enslig ? 'Tall for enslige forsørgere er skjermet av SSB.' : 'Enslige forsørgere er <b>' + fmtPct(enslig, alle_n) + '</b> av husholdningene med median <b>' + fmtKr(enkligMed) + ' kr</b> — en gruppe med høyt forsørgeransvar' + (alle_med && enkligMed < alle_med * 0.9 ? ' og lav inntekt' : '') + '.') + '</p>';

  // Nivå 2: tidsserie (utvidbar)
  let tidsserieHTML = '';
  if(data.tidsserie){
    const years = HUSH_DATA.years;
    // Beregn andel aleneboende og median inntekt per type per år
    const seriesAlene = []; // andel aleneboende
    const seriesMedAlle = []; // median alle
    const seriesMedAlene = [];
    const seriesMedPar = [];
    years.forEach(yr => {
      const yd = data.tidsserie[yr] || {};
      const all_y = (yd.alle || {}).n;
      const al_y = (yd.aleneboende || {}).n;
      seriesAlene.push(all_y ? al_y/all_y*100 : null);
      seriesMedAlle.push((yd.alle || {}).median);
      seriesMedAlene.push((yd.aleneboende || {}).median);
      seriesMedPar.push((yd.par_med_barn || {}).median);
    });
    // Y-akse-helper: gir nice ticks som garantert dekker [min, max] uten å klippe
    function niceTickRange(min, max, unit){
      const span = Math.max(0, max - min);
      let step;
      if(unit === 'kr'){
        step = span <= 400000 ? 100000 : span <= 800000 ? 200000 : span <= 2000000 ? 250000 : 500000;
      } else {
        step = span <= 4 ? 1 : span <= 8 ? 2 : span <= 20 ? 5 : span <= 40 ? 10 : 20;
      }
      let lo = Math.floor(min / step) * step;
      let hi = Math.ceil(max / step) * step;
      // Hvis lo===hi (flat kurve eller verdi treffer kant nøyaktig), gi luft på begge sider
      if(hi - lo < step){ lo -= step; hi += step; }
      return {lo: lo, hi: hi, step: step};
    }
    // Andel-graf
    const valsA = seriesAlene.filter(v => v != null);
    const aRange = niceTickRange(Math.min.apply(null, valsA), Math.max.apply(null, valsA), '%');
    const aLo = aRange.lo, aHi = aRange.hi, aStep = aRange.step;
    const xT=[years[0], years[Math.floor(years.length/2)], years[years.length-1]];
    function lineChart(values, color, yLo, yHi, yStep, unit, yLabel){
      return NN.placeholder('linjer',{x:years, serier:[{navn:unit==='%'?'Andel aleneboende':'Verdi', kort:unit==='%'?'Aleneboende':'', data:values, farge:'accent', uthev:true}],
        format:unit==='%'?'pst1':'kr1000', xTicks:xT, hoyde:220},230);
    }
    function multiLineChart(linesData){
      return NN.placeholder('linjer',{x:HUSH_DATA.years, serier:linesData.map(l=>({navn:l.label, kort:l.label, data:l.values, farge:l.color, uthev:l.label==='aleneboende'})),
        format:'kr1000', xTicks:xT, hoyde:260},270);
    }
    tidsserieHTML =
      '<details style="margin-top:18px"><summary style="cursor:pointer;font-family:var(--font-display);font-size:14px;font-weight:600;color:var(--ink);padding:6px 0;list-style:none">▾ Tidsserie 2005\u20132024 — strukturelle endringer</summary>' +
      '<div style="margin-top:12px">' +
      '<div style="font-family:var(--font-display);font-size:13px;font-weight:600;margin:8px 0 2px;color:var(--ink)">Andel aleneboende (%) — utvikling 2005\u20132024</div>' +
      '<p class="hint" style="font-size:11.5px;margin:0 0 6px;opacity:.85">Andelen av alle husholdninger som er aleneboende. Stigende kurve = flere bor alene, noe som vanligvis trekker inntekten per husholdning ned.</p>' +
      lineChart(seriesAlene, 'var(--neg)', aLo, aHi, aStep, '%') +
      '<div style="font-family:var(--font-display);font-size:13px;font-weight:600;margin:18px 0 2px;color:var(--ink)">Median inntekt etter skatt — tre husholdningstyper</div>' +
      '<p class="hint" style="font-size:11.5px;margin:0 0 6px;opacity:.85"><b>NB:</b> Tallene er <b>nominelle kroner</b> (ikke inflasjonsjustert). Bruk forholdet mellom linjene og kurveformen, ikke absolutte beløp.</p>' +
      multiLineChart([
        {values: seriesMedAlene, color:'accent', label:'aleneboende'},
        {values: seriesMedAlle, color:'ink', label:'alle'},
        {values: seriesMedPar, color:'cat-4', label:'par med barn'},
      ]) +
      '<p class="hint" style="font-size:11px;margin-top:8px;opacity:.75;font-style:italic">Tall ved endepunktene viser median i siste år (kroner). Endring i forholdet mellom linjene over tid viser strukturell ulikhet. Forholdet påvirkes ikke av prisveksten, men avstanden i kroner gjør det.</p>' +
      '</div></details>';
  }

  // Avsluttende kilde-rad
  const kildeHTML = '<p class="hint" style="font-size:11.5px;margin-top:14px;opacity:.75;font-style:italic">Kilde: SSB tabell 06944, ' + HUSH_DATA.year_latest + '. ' + (scope.startsWith('kommune-') ? 'Per-kommune-data.' : 'Aggregat: antall summert, median = vektet snitt av kommunemedianer (vekt = antall husholdninger).') + ' «Andre»-kategorien er flerfamiliehushold og enfamiliehusholdninger med voksne hjemmeboende barn.</p>';

  host.innerHTML = kpiHTML + inntektsGrafHTML + sammensetningHTML + tolkningHTML + tidsserieHTML + kildeHTML;
}

/* === Arbeids-helpers fra ARBEID_DATA ======================================== */
function getSysselsRate(nr){
  if(typeof ARBEID_DATA==='undefined') return null;
  const r=ARBEID_DATA.kommuner[String(nr)];
  return r&&r.sysselsRate!=null ? r.sysselsRate/100 : null;
}
function getUforePct(nr){
  if(typeof ARBEID_DATA==='undefined') return null;
  const r=ARBEID_DATA.kommuner[String(nr)];
  return r ? r.uforePct18_67 : null;
}
function getSysselsAbs(nr){
  if(typeof ARBEID_DATA==='undefined') return null;
  const r=ARBEID_DATA.kommuner[String(nr)];
  return r ? r.sysselsatte20_66 : null;
}
let _landsdelSyssRate=null;
function landsdelSysselsRate(){
  if(_landsdelSyssRate!=null) return _landsdelSyssRate;
  if(typeof ARBEID_DATA==='undefined') return 0.7;
  let sumSyss=0, sumTot=0;
  Object.values(ARBEID_DATA.kommuner).forEach(r=>{
    if(r.sysselsatte20_66!=null) sumSyss+=r.sysselsatte20_66;
    if(r.tot20_66!=null) sumTot+=r.tot20_66;
  });
  _landsdelSyssRate = sumTot ? sumSyss/sumTot : 0.7;
  return _landsdelSyssRate;
}

/* === Bærekraftsindikatorer 2050 — eksterne kilder + normer ================== */
/* Ingen interne terskler. Hver indikator vurderes mot sin autoritative norm:
   - OECD SCIRN (årlig befolkningsendring)
   - OECD-standard forsørgerbyrde (65+/20–64)
   - TBU-norm netto driftsresultat (+1,75 %)
   - KS-rapport mai 2025 (disposisjonsfond om lag 5 %, korrigert netto lånegjeld ≤ 85 %)
   - Kommuneloven §28-1 (ROBEK)
   - SSB-snitt for sysselsetting og uføreandel (referansenivå) */
const EXT_NORMS = {
  scirnAnnual: -0.15,     // OECD SCIRN: ≥0,15 %/år nedgang = "shrinking"
  oecd2050: 52,           // OECD-snitt forsørgerbyrde 65+/20-64 i 2050
  nasjSyss: 76.7,         // SSB 13563, 2025: 2 629 263 sysselsatte av 3 428 369 i alderen 20–66
  nasjUfor: 10.7,         // SSB 11715, 2025: 10,7 % uføretrygdede 18–67
  tbuNDR: 1.75,           // TBU-norm netto driftsresultat
  ksFond: 5.0,            // KS FoU mai 2025 anbefalt minimum
  ksGjeld: 85.0,          // KS 2025: korrigert netto lånegjeld ≤ 85 % (75 % var Riksrevisjonens analysegrense i 2015)
};
function evaluateKommune(k){
  // Alle indikatorer måles mot SSB MMMM (tabell 14746) — dashbordets hovedbane.
  // Våre egne baner (TF-ATTR, TF-MVP) vises som alternativer, aldri som grunnlag
  // for vurderingen mot de eksterne normene.
  const P=DATA.proj, o=P&&P.kommuner&&P.kommuner[k.nr];
  if(!o||!o.main) return null;
  const pop=o.main;
  const n=pop.length;
  const popFall = pop[0]?(1 - pop[n-1]/pop[0])*100:null;
  const a2 = o.a2064, a6 = o.a65;
  const workFall = (a2&&a2[0])?(1 - a2[n-1]/a2[0])*100:null;
  // OECD-standard forsørgerbyrde (65+/20-64)
  const oad2050 = (a2&&a2[n-1])?100*a6[n-1]/a2[n-1]:null;
  // Årlig endring 2026\u20132050 (geometrisk) — for SCIRN
  const annualPct = (pop[0]&&pop[n-1]>0)?(Math.pow(pop[n-1]/pop[0], 1/(n-1)) - 1)*100:null;
  const syssR = getSysselsRate(k.nr);
  const uforePct = getUforePct(k.nr);
  const FR = (typeof FORSORG_DATA!=='undefined') ? FORSORG_DATA.regioner[String(k.nr)] : null;
  const okon = FR ? fbOkonIDag(FR) : null;
  const RB = P.robek||{kommuner:{}};
  const inROBEK = !!(RB.kommuner && RB.kommuner[k.nr]);
  const pendingROBEK = !!(RB.pending && RB.pending[k.nr]);
  const prox = (typeof robekProxy==='function')?robekProxy(k.nr):null;
  const fond = prox?prox.fond:null;
  const ndr = prox?prox.ndr:null;
  const gj = prox?prox.gj:null;
  const bdr = prox?prox.bdr:null;
  const negYrs = prox?prox.neg:null;
  const yr = prox?prox.yr:null;
  return {
    nr:k.nr, navn:k.navn, fylke:k.fylke,
    popFall, workFall, oad2050, annualPct,
    syssRate: syssR!=null?syssR*100:null,
    uforePct, okon,
    ndr, fond, gj, bdr, negYrs, yr,
    inROBEK, pendingROBEK,
  };
}
/* Per-kommune indikatorkort — viser hver indikator mot sin eksterne norm. Ingen aggregert dom. */
function sustKommuneCard(k){
  if(k.isAgg) return '';
  const e = evaluateKommune(k);
  if(!e) return '';
  const N = EXT_NORMS;
  const sgn = v => (v>=0?'+':'−')+Math.abs(v).toFixed(0).replace('.',',');
  const fmt1 = v => (v==null?'–':(v<0?'−':'')+Math.abs(v).toFixed(1).replace('.',','));
  const fmt0 = v => (v==null?'–':Math.round(v).toString());
  // Status helper: returns color + label
  const stat = (val, ok) => {
    if(val==null) return {col:'var(--ink3)', lab:'–'};
    return ok ? {col:'var(--pos)', lab:''} : {col:'var(--neg)', lab:''};
  };
  const row = (lab, valHtml, statusInfo, source) =>
    '<tr style="border-top:1px solid var(--line2)">'+
      '<td style="padding:6px 0;color:var(--ink2)">'+lab+'</td>'+
      '<td style="text-align:right;font-family:var(--font-mono);font-weight:600;color:'+(statusInfo&&statusInfo.col||'var(--ink2)')+'">'+valHtml+'</td>'+
      '<td style="text-align:right;color:var(--ink3);font-size:10.5px;padding-left:12px">'+source+'</td>'+
    '</tr>';
  const sectionHeader = (txt) =>
    '<tr><td colspan="3" style="padding:10px 0 2px;font-size:11px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--ink3)">'+txt+'</td></tr>';
  // Vurder mot eksterne normer
  const popOK = e.annualPct!=null ? e.annualPct > N.scirnAnnual : null;
  const oadOK = e.oad2050!=null ? e.oad2050 <= N.oecd2050 : null;
  const sysOK = e.syssRate!=null ? e.syssRate >= N.nasjSyss : null;
  const ufoOK = e.uforePct!=null ? e.uforePct <= N.nasjUfor : null;
  const okonL = (typeof FORSORG_DATA!=='undefined') ? fbOkonIDag(FORSORG_DATA.regioner.landet) : null;
  const okonOK = (e.okon!=null && okonL!=null) ? e.okon <= okonL : null;
  const ndrOK = e.ndr!=null ? e.ndr >= N.tbuNDR : null;
  const fondOK = e.fond!=null ? e.fond >= N.ksFond : null;
  const gjeldOK = e.gj!=null ? e.gj <= N.ksGjeld : null;
  const robekOK = !e.inROBEK && !e.pendingROBEK;
  const tbl='<table style="width:100%;border-collapse:collapse;font-size:12.5px;margin:6px 0 0">'+
    sectionHeader('Demografi mot 2050 (framskrevet)')+
    row('Befolkningsendring 2026\u20132050', e.popFall!=null?sgn(-e.popFall)+' %':'–', stat(e.popFall, popOK), 'OECD SCIRN · nedgang ≥ 0,15 %/år')+
    row('Årlig endring (geometrisk)', e.annualPct!=null?(e.annualPct>=0?'+':'−')+Math.abs(e.annualPct).toFixed(2).replace('.',',')+' %':'–', stat(e.annualPct, popOK), 'OECD SCIRN-terskel: −0,15 %/år')+
    row('Forsørgerbrøk 2050 (65+/20–64)', fmt0(e.oad2050), stat(e.oad2050, oadOK), 'OECD-standard · OECD-snitt 2050 ≈ 52')+
    sectionHeader('Arbeidsmarked og helse ('+(typeof ARBEID_DATA!=='undefined'?ARBEID_DATA.year:'2025')+')')+
    row('Sysselsettingsrate 20–66', e.syssRate!=null?fmt0(e.syssRate)+' %':'–', stat(e.syssRate, sysOK), 'SSB 13563 · nasjonalt snitt 76,7 %')+
    row('Uføretrygdede 18–67', e.uforePct!=null?fmt1(e.uforePct)+' %':'–', stat(e.uforePct, ufoOK), 'SSB 11715 · nasjonalt snitt 10,7 %')+
    row('Ikke-sysselsatte per 100 sysselsatte', e.okon!=null?fmt1(e.okon):'–', stat(e.okon, okonOK), 'SSB 13563 · landet '+(okonL!=null?fmt1(okonL):'–')+' · alle aldre')+
    sectionHeader('Kommuneøkonomi'+(e.yr?' ('+e.yr+')':''))+
    row('Netto driftsresultat', e.ndr!=null?fmt1(e.ndr)+' %':'–', stat(e.ndr, ndrOK), 'TBU-norm · +1¾ % av brutto driftsinntekter')+
    row('Disposisjonsfond', e.fond!=null?fmt1(e.fond)+' %':'–', stat(e.fond, fondOK), 'KS-rapport mai 2025 · om lag 5 % i snitt')+
    row('Netto lånegjeld', e.gj!=null?fmt0(e.gj)+' %':'–', stat(e.gj, gjeldOK), 'KS 2025 · ≤85 % av driftsinntekter')+
    row('ROBEK-status', e.inROBEK?'I ROBEK':(e.pendingROBEK?'Behandles':'Ikke i ROBEK'), stat(1, robekOK), 'Kommuneloven §28-1')+
    '</table>';
  return '<div class="card">'+
    '<div class="ch" style="margin-bottom:4px">'+
      '<h3 class="serif">Bærekraftsindikatorer 2050</h3>'+
    '</div>'+
    '<p class="hint" style="margin:0 0 2px">Indikatorer vurdert mot etablerte eksterne normer. Grønt = innen norm, rødt = utenfor. Ingen samlet dom — hver indikator står på egne ben med kilden bak.</p>'+
    tbl+
  '</div>';
}
function renderSustainability(){
  const N = EXT_NORMS;
  // Vurder alle kommuner mot eksterne normer
  // Fylke-filter: bruk valgt fylke når state.fylke != 'Alle', ellers hele landsdelen
  const results = currentK().map(evaluateKommune).filter(Boolean);
  const total = results.length;
  const pct = (n,t)=>t?Math.round(100*n/t):0;
  // Per-indikator tellinger mot ekstern norm
  const counts = {
    popDecl:  results.filter(r=>r.annualPct!=null && r.annualPct <= N.scirnAnnual).length,
    oadOver:  results.filter(r=>r.oad2050!=null && r.oad2050 > N.oecd2050).length,
    sysUnder: results.filter(r=>r.syssRate!=null && r.syssRate < N.nasjSyss).length,
    ufoOver:  results.filter(r=>r.uforePct!=null && r.uforePct > N.nasjUfor).length,
    ndrUnder: results.filter(r=>r.ndr!=null && r.ndr < N.tbuNDR).length,
    fondUnder:results.filter(r=>r.fond!=null && r.fond < N.ksFond).length,
    gjeldOver:results.filter(r=>r.gj!=null && r.gj > N.ksGjeld).length,
    robekIn:  results.filter(r=>r.inROBEK).length,
    robekPnd: results.filter(r=>r.pendingROBEK).length,
  };
  // Klartekst — observasjoner, ingen samlet dom
  const tldrHost=document.getElementById('sustTldr');
  if(tldrHost){
    let text='Hver indikator vurderes mot sin <b>eksterne autoritative norm</b> — ikke mot en samlet bærekraftsdom. Av '+total+' kommuner i '+((state.fylke&&state.fylke!=='Alle')?state.fylke:'Nord-Norge')+': ';
    text+='<b>'+counts.popDecl+'</b> har befolkningsnedgang ≥ 0,15 %/år (OECD SCIRN-definisjonen av befolkningsnedgang); ';
    text+='<b>'+counts.oadOver+'</b> har forsørgerbrøk 2050 over OECD-snittet (52 eldre per 100, Pensions at a Glance 2025); ';
    text+='<b>'+counts.ndrUnder+'</b> ligger under TBU-normen for netto driftsresultat (+1¾ %); ';
    text+='<b>'+counts.fondUnder+'</b> har disposisjonsfond under KS-snittet på om lag 5 %;';
    text+='<b>'+(counts.robekIn+counts.robekPnd)+'</b> er i ROBEK eller har innmelding under behandling. ';
    text+='Hvert tall er en <i>observasjon</i> mot en konkret etablert standard.';
    tldrHost.className='tldr';
    tldrHost.innerHTML='<div class="tldr-tag">Akt 3 · Kan vi bære det? · Indikatoroversikt</div>'+
      '<h3>Kommunene mot etablerte normer</h3>'+
      '<p class="tldr-text">'+text+'</p>'+
      '<div class="tldr-nums">'+
        '<div class="tldr-num"><div class="nv down">'+counts.popDecl+'</div><div class="nl">Befolkningsnedgang</div><div class="nh">OECD SCIRN ≥ 0,15 %/år</div></div>'+
        '<div class="tldr-num"><div class="nv">'+counts.oadOver+'</div><div class="nl">Over OECD-snitt</div><div class="nh">forsørgerbrøk 2050 > 52</div></div>'+
        '<div class="tldr-num"><div class="nv">'+counts.ndrUnder+'</div><div class="nl">Under TBU-norm</div><div class="nh">NDR < +1¾ %</div></div>'+
        '<div class="tldr-num"><div class="nv down">'+(counts.robekIn+counts.robekPnd)+'</div><div class="nl">ROBEK</div><div class="nh">§28-1 registrert/behandles</div></div>'+
      '</div>';
  }
  // Per-fylke: distribusjon over hver indikator
  const fylkeHost=document.getElementById('sustFylkeBars');
  if(fylkeHost){
    // Fylke-filter: hvis state.fylke er satt, vis bare det valgte fylket
    const fylker = (state.fylke && state.fylke !== 'Alle') ? [state.fylke] : ['Nordland','Troms','Finnmark'];
    const indicators = [
      {key:'popDecl', lab:'Befolkningsnedgang (OECD SCIRN)', test:r=>r.annualPct!=null && r.annualPct <= N.scirnAnnual},
      {key:'oadOver', lab:'Forsørgerbrøk 2050 over OECD-snitt', test:r=>r.oad2050!=null && r.oad2050 > N.oecd2050},
      {key:'sysUnder', lab:'Sysselsetting under nasjonalt snitt', test:r=>r.syssRate!=null && r.syssRate < N.nasjSyss},
      {key:'ufoOver', lab:'Uføreandel over nasjonalt snitt', test:r=>r.uforePct!=null && r.uforePct > N.nasjUfor},
      {key:'ndrUnder', lab:'NDR under TBU-norm', test:r=>r.ndr!=null && r.ndr < N.tbuNDR},
      {key:'fondUnder', lab:'Disposisjonsfond under KS-anbefaling', test:r=>r.fond!=null && r.fond < N.ksFond},
      {key:'gjeldOver', lab:'Lånegjeld over KS-grense', test:r=>r.gj!=null && r.gj > N.ksGjeld},
      {key:'robek', lab:'I ROBEK eller behandles', test:r=>r.inROBEK || r.pendingROBEK},
    ];
    let h='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px">';
    fylker.forEach(fy=>{
      const sub = results.filter(r=>r.fylke===fy);
      const t = sub.length;
      let rows='';
      indicators.forEach(ind=>{
        const n = sub.filter(ind.test).length;
        const p = t?(100*n/t):0;
        const col = p>=60?'var(--neg)' : p>=30?'var(--cat-5)' : 'var(--pos)';
        rows+='<div style="margin-bottom:8px">'+
          '<div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:2px"><span style="color:var(--ink2)">'+ind.lab+'</span><span style="font-family:var(--font-mono);color:'+col+';font-weight:600">'+n+' / '+t+'</span></div>'+
          '<div style="height:6px;background:var(--line2);border-radius:0;overflow:hidden"><div style="height:100%;width:'+p+'%;background:'+col+'"></div></div>'+
        '</div>';
      });
      h+='<div class="card" style="padding:14px 16px;margin:0">'+
        '<h4 style="margin:0 0 10px;font-family:var(--font-display);font-weight:600">'+fy+' <span style="color:var(--ink3);font-weight:400;font-size:12px">· '+t+' kommuner</span></h4>'+
        rows+
      '</div>';
    });
    h+='</div>';
    fylkeHost.innerHTML=h;
  }
}
function render(){renderList(); if(!renderCompare())detail();
  var _cmpi=document.getElementById('cmpinfo'); if(_cmpi) _cmpi.textContent=state.compare.length?`${state.compare.length} valgt — sammenligner`:'+ for å sammenligne';
  renderNat(); renderNatTS(); renderModelEval(); renderRobek(); renderBigPicture(); renderComposition(); renderBurden(); renderLevekar(); renderEconomy(); renderSustainability();
  if(typeof attachHelpPops==='function')attachHelpPops();}
function renderRobek(){
  const host=document.getElementById('robekview'); if(!host) return;
  // Synkroniser med valgt fylke: når brukeren er på fylke.html, vis bare det fylkets kommuner
  const f = (state.fylke && state.fylke !== 'Alle') ? state.fylke : (state.robekFylke || 'Alle');
  host.innerHTML=robekOverviewHTML(f);
  host.querySelectorAll('#rbk button').forEach(b=>b.onclick=()=>{state.robekSort=b.dataset.s;renderRobek();});
  const fb=document.getElementById('rbkf');
  if(fb) fb.querySelectorAll('button').forEach(b=>b.onclick=()=>{
    fb.querySelectorAll('button').forEach(x=>x.setAttribute('aria-selected',x===b?'true':'false'));
    state.robekFylke=b.dataset.f; renderRobek();});
}

document.querySelectorAll('#fylke button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('#fylke button').forEach(x=>x.setAttribute('aria-selected',x===b));
  state.fylke=b.dataset.f; state.sel=FYNR[state.fylke]; const f=filtered(); render();});
var _q=document.getElementById('q'); if(_q) _q.oninput=e=>{state.q=e.target.value;const f=filtered();
  if(f.length)state.sel=f[0].nr; render();};
document.querySelectorAll('.searchhint .shchip').forEach(b=>b.onclick=()=>{
  const v=b.dataset.shq; const qi=document.getElementById('q');
  state.q = state.q.toLowerCase().trim()===v.toLowerCase() ? '' : v;
  qi.value=state.q;
  const f=filtered(); if(f.length)state.sel=f[0].nr; render();
});
document.querySelectorAll('.sortbar button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('.sortbar button').forEach(x=>x.setAttribute('aria-pressed',x===b));
  state.sort=b.dataset.s; render();});
if(elList) elList.onclick=e=>{
  const c=e.target.closest('[data-cmp]');
  if(c){const nr=+c.dataset.cmp; const i=state.compare.indexOf(nr);
    if(i>=0)state.compare.splice(i,1); else if(state.compare.length<4)state.compare.push(nr);
    render(); e.stopPropagation(); return;}
  const row=e.target.closest('[data-nr]'); if(row){state.sel=+row.dataset.nr;
    if(state.compare.length<2)render(); else {state.compare=[];render();}}};
document.querySelectorAll('#nxs button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('#nxs button').forEach(x=>x.setAttribute('aria-selected',x===b));
  state.natSex=b.dataset.x; renderNat(); renderNatTS();});
document.querySelectorAll('#nmt button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('#nmt button').forEach(x=>x.setAttribute('aria-selected',x===b));
  state.natMetric=b.dataset.m; renderNat(); renderNatTS();});
var _natts=document.getElementById('natts'); if(_natts) _natts.addEventListener('click',e=>{
  const b=e.target.closest('[data-leg]'); if(!b)return;
  const k=b.dataset.leg; state.natHidden[k]=!state.natHidden[k]; renderNatTS();});
function setTab(t){
  document.querySelectorAll('#journey button').forEach(x=>x.setAttribute('aria-current',x.dataset.tab===t?'true':'false'));
  document.querySelectorAll('.tab').forEach(p=>p.classList.toggle('active',p.dataset.tab===t));
  window.scrollTo({top:0,behavior:'smooth'});
}
document.querySelectorAll('#journey button').forEach(b=>b.onclick=()=>setTab(b.dataset.tab));
document.querySelectorAll('.nextstep').forEach(b=>b.onclick=()=>setTab(b.dataset.next));
document.querySelectorAll('.insight .src').forEach(b=>b.onclick=()=>setTab(b.dataset.goto));

/* help-pop overlays */
function attachHelpPops(){
  document.querySelectorAll('[data-helpfor]').forEach(host=>{
    if(host.querySelector('.helpbtn'))return;
    const btn=document.createElement('button');
    btn.className='helpbtn'; btn.type='button'; btn.textContent='i';
    btn.setAttribute('aria-label','Hva betyr denne grafen?');
    btn.setAttribute('aria-expanded','false');
    const pop=document.createElement('div');
    pop.className='helppop'; pop.innerHTML=host.dataset.helpfor;
    host.style.position=host.style.position||'relative';
    host.appendChild(btn); host.appendChild(pop);
    btn.onclick=e=>{
      e.stopPropagation();
      document.querySelectorAll('.helppop.open').forEach(p=>{if(p!==pop){p.classList.remove('open');p.previousSibling&&p.previousSibling.setAttribute&&p.previousSibling.setAttribute('aria-expanded','false');}});
      const isOpen=pop.classList.toggle('open');
      btn.setAttribute('aria-expanded',isOpen?'true':'false');
      if(isOpen){
        const r=btn.getBoundingClientRect();
        pop.style.top=(btn.offsetTop+btn.offsetHeight+10)+'px';
        pop.style.left=Math.max(8,btn.offsetLeft-8)+'px';
      }
    };
  });
}
document.addEventListener('click',e=>{
  if(!e.target.closest('.helppop')&&!e.target.classList.contains('helpbtn')){
    document.querySelectorAll('.helppop.open').forEach(p=>{
      p.classList.remove('open');
      const b=p.parentElement&&p.parentElement.querySelector('.helpbtn');
      if(b)b.setAttribute('aria-expanded','false');
    });
  }
});

/* share-card buttons */
const prntBtn=document.getElementById('prntbtn');
if(prntBtn)prntBtn.onclick=()=>window.print();
const copyBtn=document.getElementById('copybtn');
if(copyBtn)copyBtn.onclick=async()=>{
  try{ await navigator.clipboard.writeText(location.href); copyBtn.textContent='Kopiert';
    setTimeout(()=>copyBtn.textContent='Kopier lenke',1800);
  }catch(_){copyBtn.textContent='Marker URL manuelt';}
};

/* tour-modus */
const TOUR=[
  {sel:'.essence',title:'Kjernebudskapet',body:'Dashbordets hovedfunn i én setning: flere eldre og færre i arbeidsfør alder fram mot 2050, med store forskjeller mellom kommunene.'},
  {sel:'#journey',title:'Reisen i tre akter',body:'Tre tematiske akter à to kapitler, pluss et sammendrag. Akt 1 spør «Hva skjer», Akt 2 «Hvem blir igjen», Akt 3 «Kan vi bære det?». Klikk fritt mellom kapitlene.'},
  {sel:'[data-tab="intro"] #bigPicChart',title:'Akt 1.1 · Det store bildet',body:'Landsdelens samlede befolkning 2000\u20132050 i én graf. Den mørke linjen er faktisk historikk; framover er SSBs MMMM-bane og Telemarksforsknings TF-MVP/TF-ATTR.'},
  {sel:'[data-tab="explore"] .stepcard',title:'Akt 1.2 · Utforsk kommunene',body:'Bak linjen for landsdelen ligger 80 kommuner med ulik utvikling. Filtrér på fylke eller status (ROBEK, vekst, aldring) og gå inn i detaljvisningen for hver kommune.',action:'explore'},
  {sel:'[data-tab="model"] .stepcard',title:'Akt 2.1 · Befolkningssammensetningen',body:'Alder, opprinnelse og bofasthet samlet. Hvem bor her — og hvor lenge blir flyktningene? To ulike mål, samme historie.',action:'model'},
  {sel:'[data-tab="nat"] #burdenChart',title:'Akt 2.2 · Forsørgerbyrden',body:'Forsørgerbrøken, innbyggere 65 år og eldre per 100 i alderen 20–64, stiger fra 38 til 51 i Nord-Norge mot 2050. Teller man bare dem som faktisk er i arbeid, blir bildet et annet; se «Hvem bærer hvem?».',action:'nat'},
  {sel:'[data-tab="refugees"] #econRobekCard',title:'Akt 3.1 · Økonomien i dag',body:'KOSTRA-status og ROBEK-register samlet. Hvor solid står kommunene før aldringskostnaden kommer?',action:'refugees'},
  {sel:'[data-tab="robek"] #sustFylkeCard',title:'Akt 3.2 · Bærekraftsindikatorer 2050',body:'Åtte indikatorer vurdert mot eksterne normer (OECD SCIRN, OECD-standard, TBU, KS, kommuneloven). Per fylke: hvor mange kommuner ligger utenfor hver enkelt norm?',action:'robek'},
  {sel:'[data-tab="summary"] .summary-hero',title:'Sammendrag · Det du nå vet',body:'Fem funn med lenker tilbake til kapitlene. Skriv ut som PDF til møtet.',action:'summary'},
];
let tourIdx=-1;
const tBack=document.createElement('div'); tBack.className='tour-backdrop';
const tSpot=document.createElement('div'); tSpot.className='tour-spot';
const tBub=document.createElement('div'); tBub.className='tour-bubble';
document.body.append(tBack,tSpot,tBub);
function tourPos(el){
  if(!el){tSpot.classList.remove('on');return null;}
  const r=el.getBoundingClientRect();
  const pad=8;
  tSpot.style.top=(r.top-pad)+'px';
  tSpot.style.left=(r.left-pad)+'px';
  tSpot.style.width=(r.width+pad*2)+'px';
  tSpot.style.height=(r.height+pad*2)+'px';
  tSpot.classList.add('on');
  return r;
}
function tourShow(i){
  if(i<0||i>=TOUR.length){tourEnd();return;}
  const step=TOUR[i];
  if(step.action) setTab(step.action);
  setTimeout(()=>{
    const el=document.querySelector(step.sel);
    if(el)el.scrollIntoView({block:'center',behavior:'smooth'});
    setTimeout(()=>{
      const r=tourPos(el);
      tBub.innerHTML=`<div class="tk">Steg ${i+1} av ${TOUR.length}</div>
        <h4>${step.title}</h4><p>${step.body}</p>
        <div class="tnav"><button class="tprev" ${i===0?'disabled':''}>← Forrige</button>
        <span class="tcount">${i+1} / ${TOUR.length}</span>
        <div><button class="tskip">Avslutt</button>
        <button class="tnext">${i===TOUR.length-1?'Ferdig':'Neste →'}</button></div></div>`;
      const top=r?Math.min(window.innerHeight-220,r.bottom+16):120;
      const left=r?Math.max(16,Math.min(window.innerWidth-400,r.left)):Math.max(16,(window.innerWidth-360)/2);
      tBub.style.top=top+'px'; tBub.style.left=left+'px';
      tBub.classList.add('on');
      tBub.querySelector('.tprev').onclick=()=>{tBub.classList.remove('on');setTimeout(()=>tourShow(i-1),120);};
      tBub.querySelector('.tnext').onclick=()=>{tBub.classList.remove('on');setTimeout(()=>tourShow(i+1),120);};
      tBub.querySelector('.tskip').onclick=tourEnd;
    },step.action?300:60);
  },step.action?60:0);
}
function tourStart(){tourIdx=0;tBack.classList.add('on');tourShow(0);
  try{localStorage.setItem('nn_tour_seen','1');}catch(_){}}
function tourEnd(){tBack.classList.remove('on');tSpot.classList.remove('on');tBub.classList.remove('on');tourIdx=-1;}
var _ts=document.getElementById('tourstart'); if(_ts) _ts.onclick=tourStart;
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&tourIdx>=0)tourEnd();});

render();
attachHelpPops();

/* === Steg 04½ "Flyktningenes vei" — render-funksjoner ======================== */
function attachMethodBadges(){
  document.querySelectorAll('[data-methodbadge]').forEach(el=>{
    if(el.dataset.mbDone) return;
    el.innerHTML = methodBadge(el.dataset.methodbadge);
    el.dataset.mbDone = '1';
  });
}

function flowChartSVG(state){
  const F=SSB_FLOWS; const yrs=F.years; const n=yrs.length;
  const excl = state==='excl';
  // Innenlands netto er upåvirket av Ukraina; nettoinnvandring minus Ukraina-delta
  const inn = F.nordNorge.nettoInnland.slice();
  const utl = F.nordNorge.nettoInnvandring.map((v,i)=>{
    if(!excl) return v;
    const d = F.nordNorge.ukraineDelta[i];
    return v - (d||0);
  });
  let svg=NN.placeholder('linjer',{x:yrs, null:true, format:'endring', xTicks:yrs.filter((y,i)=>y%5===0||i===n-1), hoyde:300,
    markor:[{x:2022, tekst:'Ukraina-invasjon'}],
    serier:[{navn:'Nettoinnvandring fra utlandet', kort:'Utlandet', data:utl, farge:'accent', uthev:true},
            {navn:'Innenlands nettoflytting', kort:'Innenlands', data:inn, farge:'neg'}]},320);
  svg+='<div class="flow-legend">'+
    '<span><i style="background:var(--accent)"></i>Nettoinnvandring fra utlandet</span>'+
    '<span><i style="background:var(--neg)"></i>Innenlands nettoflytting (ofte negativ — folk drar sør)</span>'+
    (excl?'<span style="color:var(--warn);font-weight:600">Ukraina-effekten er trukket fra (tilnærmet via endring i bestanden)</span>':'')+
  '</div>';
  return svg;
}

function renderFlowChart(){
  const host=document.getElementById('flowChart'); if(!host) return;
  const btn=document.querySelector('#flowToggle button[aria-pressed=true]');
  const mode=btn?btn.dataset.ukr:'incl';
  host.innerHTML = flowChartSVG(mode);
}

function bofastChartHTML(){
  // Bofasthet for flyktninger: fem år per kull (direkte, SSB-monitoren) og netto bevaring 5–20 år (SSB 10598).
  if(typeof BOFAST_DATA==='undefined') return '';
  const B=BOFAST_DATA, A=B.kull5, N=B.netto, KM=A.kommune;
  const fy=(state.fylke&&state.fylke!=='Alle')?state.fylke:null;
  const p0=v=>v.toLocaleString('nb-NO',{maximumFractionDigits:0})+' %';
  const serier=[{navn:'Landet',data:KM.Landet,farge:'ink',stil:'stiplet'}].concat(['Nordland','Troms','Finnmark'].map(f=>({
    navn:f, data:KM[f], farge:({Nordland:'nl',Troms:'tr',Finnmark:'fi'})[f], uthev:fy===f, svak:!!fy&&fy!==f
  })));
  let html='<h4 class="serif" style="font-size:15px;font-weight:600;margin:4px 0 6px">Fem år etter bosetting, per bosettingskull</h4>'+
    NN.placeholder('linjer',{x:A.kull, serier, format:'pst0', xTicks:[1998,2002,2006,2010,2015,2019], hoyde:300,
      yTittel:'Andel av kullet som bor i første bosettingskommune fem år etter bosetting.',
      kilde:'SSBs monitor for sekundærflytting 2005–2020 og SSB-artikler 2021 og 2024. Kull 2015 bare for Troms og Finnmark samlet ('+p0(KM['Troms og Finnmark'][A.kull.indexOf(2015)])+'). Kull 1999, 2013, 2014 og 2016–2018 er ikke publisert per fylke.'},340);
  const omr=fy==='Nordland'?'nordland':fy?'tf':'nn';
  const omrNavn=fy==='Nordland'?'Nordland':fy?'Troms og Finnmark':'Nord-Norge';
  const grupper=N.grupper.slice(0,2).map(g=>({tittel:g.navn+' · '+omrNavn+' (landet i merknaden)',
    rader:N.botid.map((b,i)=>({l:'Etter '+b+' år', v:g[omr][i], farge:g===N.grupper[0]?'accent':'muted', uthev:g===N.grupper[0]&&b===20, note:'landet '+p0(g.landet[i])}))}));
  html+='<h4 class="serif" style="font-size:15px;font-weight:600;margin:22px 0 6px">Lengre perioder: netto bevaring i '+omrNavn+'</h4>'+
    NN.placeholder('hstolper',{format:'pst0', maks:100, grupper,
      kilde:N.kilde+'. Innvandrere med k års botid i området, i prosent av antallet med ett års botid da kullet kom. Tilflyttere teller med. Ti flyktningland: '+N.flyktningland+'.'},2*(N.botid.length*34+40));
  return html;
}

/* === Hvem bærer hvem? Forsørgerbrøk og ikke-sysselsatte per 100 sysselsatte (FORSORG_DATA, fetch_forsorg.py) ===
   rKey: kommunenummer, 'Nordland' | 'Troms' | 'Finnmark', 'nn' eller 'landet'. */
function forsorgRegionKey(k){
  if(k == null) return null;
  if(typeof k === 'string') return k;
  if(k.nr > 0) return String(k.nr);
  return ({'-1':'nn','-18':'Nordland','-55':'Troms','-56':'Finnmark'})[String(k.nr)] || null;
}
// Funksjoner (ikke const): render() kjøres lenger opp i filen enn disse definisjonene.
function fbFarger(){ return {syss:'var(--accent)', aapufo:'var(--cat-6)', pensjon:'var(--cat-4)', utd:'var(--cat-3)', ledig:'var(--cat-5)', tiltak:'var(--cat-5)', andre:'var(--muted-mark)', barn:'var(--cat-2)'}; }
function fbT(v, d){ return v == null ? '–' : v.toLocaleString('nb-NO', {minimumFractionDigits:d||0, maximumFractionDigits:d||0}); }
function fbPst(v, d){ return fbT(v, d == null ? 1 : d) + ' %'; }
// 100 personer i alderen 20–66 som prikker (største rest-avrunding)
function fbPrikker(s2066){
  const FB_FARGE = fbFarger();
  const D = FORSORG_DATA, n = s2066[0], kat = D.status.map((s, i) => ({s, v: s2066[i + 1] / n * 100}));
  const slatt = [{s:'syss', v:kat[0].v}, {s:'aapufo', v:kat[4].v}, {s:'utd', v:kat[3].v}, {s:'ledig', v:kat[1].v + kat[2].v}, {s:'pensjon', v:kat[5].v}, {s:'andre', v:kat[6].v}];
  slatt.forEach(x => { x.n = Math.floor(x.v); x.rest = x.v - x.n; });
  let mangler = 100 - slatt.reduce((a, x) => a + x.n, 0);
  slatt.slice().sort((a, b) => b.rest - a.rest).forEach(x => { if(mangler > 0){ x.n++; mangler--; } });
  let prikker = '';
  slatt.forEach(x => { for(let i = 0; i < x.n; i++) prikker += '<i style="background:' + FB_FARGE[x.s] + '"></i>'; });
  return {html: '<div class="fb-prikker" role="img" aria-label="100 personer i alderen 20–66 etter status">' + prikker + '</div>', slatt};
}
function fbNavn(){ return {syss:'i arbeid', aapufo:'AAP eller uføretrygd', utd:'under utdanning', ledig:'ledige eller på tiltak', pensjon:'AFP eller alderspensjon', andre:'andre utenfor arbeid'}; }
// Per 100 sysselsatte: hvem forsørges? (alle aldre)
function fbPer100(r){
  const s = r.s15, sy = s[1], u15 = r.bef.u15;
  return [
    {k:'barn', l:'Barn 0–14 år', v: u15 / sy * 100},
    {k:'utd', l:'Under utdanning', v: s[4] / sy * 100},
    {k:'aapufo', l:'AAP og uføretrygd', v: s[5] / sy * 100},
    {k:'pensjon', l:'AFP og alderspensjon', v: s[6] / sy * 100},
    {k:'ledig', l:'Ledige og på tiltak', v: (s[2] + s[3]) / sy * 100},
    {k:'andre', l:'Andre utenfor arbeid', v: s[7] / sy * 100},
  ];
}
function fbOkonIDag(r){ return (r.bef.tot - r.s15[1]) / r.s15[1] * 100; }
// Kompakt blokk til sammenligningssiden
function forsorgCmp(k){
  if(typeof FORSORG_DATA === 'undefined') return '';
  const r = FORSORG_DATA.regioner[String(k.nr)], L = FORSORG_DATA.regioner.landet;
  if(!r) return '';
  const blokk = (v, l, h) => '<div style="margin-top:8px"><div class="mono" style="font-size:18px;font-weight:600">' + v + '</div><div style="font-size:11px;color:var(--ink3)">' + l + ' · ' + h + '</div></div>';
  return '<div style="margin-top:14px;padding-top:10px;border-top:1px solid var(--line2)"><div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink3);font-weight:600">Hvem bærer hvem?</div>' +
    blokk(fbT(r.demo[0], 1), 'forsørgerbrøk 65+/20–64', 'landet ' + fbT(L.demo[0], 1)) +
    blokk(fbT(fbOkonIDag(r), 1), 'ikke-sysselsatte per 100 sysselsatte', 'landet ' + fbT(fbOkonIDag(L), 1)) +
    blokk(fbPst(r.s2066[5] / r.s2066[0] * 100), 'AAP eller uføretrygd, 20–66', 'landet ' + fbPst(FORSORG_DATA.landet_aapufo_pct)) +
    '</div>';
}
function forsorgCard(rKey, navn, opts){
  const FB_FARGE = fbFarger(), FB_NAVN = fbNavn();
  if(typeof FORSORG_DATA === 'undefined' || !rKey) return '';
  opts = opts || {};
  const D = FORSORG_DATA, R = D.regioner, r = R[rKey], L = R.landet, NNr = R.nn;
  if(!r) return '';
  const id = 'fb' + String(rKey).replace(/\W/g, '');
  const sammen = [[navn, r]].concat(rKey !== 'nn' && rKey !== 'landet' ? [['Nord-Norge', NNr]] : []).concat(rKey !== 'landet' ? [['Hele landet', L]] : []);
  const okon0 = fbOkonIDag(r), okonL = fbOkonIDag(L), demo0 = r.demo[0], demoL = L.demo[0];
  const aap = r.s2066[5] / r.s2066[0] * 100, aapL = D.landet_aapufo_pct;
  const sy = r.syss, dSy = (sy[sy.length - 1] / sy[0] - 1) * 100, n = D.aar.length - 1;
  const liten = r.bef.tot < 3000;

  // Tekst: observasjon og hypotese
  const tyngreDemo = demo0 > demoL + 0.5, tyngreOkon = okon0 > okonL + 0.5;
  let obs = '<b>Observasjon:</b> I ' + navn + ' er det <b>' + fbT(demo0, 1) + '</b> innbyggere 65 år og eldre per 100 i alderen 20–64 (landet ' + fbT(demoL, 1) + '). ' +
    'Teller man alle som ikke er i arbeid — barn, studenter, pensjonister, uføre og ledige — er det <b>' + fbT(okon0, 1) + '</b> per 100 sysselsatte (landet ' + fbT(okonL, 1) + '). ';
  if(rKey !== 'landet'){
    if(tyngreDemo && !tyngreOkon) obs += 'Aldersmålet får ' + navn + ' til å se tyngre ut enn landet, men målt mot dem som faktisk er i arbeid, er byrden ' + (okon0 < okonL - 0.5 ? 'lavere enn' : 'omtrent som') + ' i landet. ';
    else if(!tyngreDemo && tyngreOkon) obs += 'Aldersmålet ligger ' + (demo0 < demoL - 0.5 ? 'under' : 'nær') + ' landet, men færre er i arbeid, så byrden målt mot faktisk arbeid er høyere enn i landet. ';
    else if(tyngreDemo && tyngreOkon) obs += 'Byrden er høyere enn i landet på begge mål. ';
    else obs += 'Byrden er lavere enn eller lik landet på begge mål. ';
  }
  obs += fbPst(aap) + ' av innbyggerne i alderen 20–66 mottar arbeidsavklaringspenger eller uføretrygd (landet ' + fbPst(aapL) + ')';
  const ekstra = (aap - aapL) / 100 * r.s2066[0];
  obs += aap > aapL + 0.2 && ekstra >= 5 ? '. Med landets andel ville om lag <b>' + fbT(Math.round(ekstra / (ekstra >= 100 ? 10 : 1)) * (ekstra >= 100 ? 10 : 1)) + '</b> færre stått utenfor arbeid av denne grunnen.' : '.';
  const hyp = '<b>Hypotese:</b> Dersom sysselsettingen i hver aldersgruppe holdes som i dag, og befolkningen følger SSBs hovedalternativ, stiger forsørgerbrøken til <b>' + fbT(r.demo[n], 1) + '</b> og antallet ikke-sysselsatte per 100 sysselsatte til <b>' + fbT(r.okon[n], 1) + '</b> i ' + D.aar[n] + ' (landet ' + fbT(L.demo[n], 1) + ' og ' + fbT(L.okon[n], 1) + '). ' +
    'Antallet sysselsatte ' + (dSy >= 0 ? 'øker' : 'faller') + ' med ' + fbPst(Math.abs(dSy)) + ', fra ' + fbT(sy[0]) + ' til ' + fbT(sy[n]) + ' (landet ' + (L.syss[n] >= L.syss[0] ? '+' : '−') + fbPst(Math.abs((L.syss[n] / L.syss[0] - 1) * 100)) + ').';

  // Prikker: kommunen/regionen og landet
  const p1 = fbPrikker(r.s2066), p2 = fbPrikker(L.s2066);
  const forklaring = p => '<div class="fb-legend">' + p.slatt.map(x => '<span><i style="background:' + FB_FARGE[x.s] + '"></i>' + x.n + ' ' + FB_NAVN[x.s] + '</span>').join('') + '</div>';
  const prikkHTML = '<div class="fb-prikk-rad">' +
      '<div><div class="fb-prikk-tittel">' + navn + '</div>' + p1.html + forklaring(p1) + '</div>' +
      (rKey !== 'landet' ? '<div><div class="fb-prikk-tittel">Hele landet</div>' + p2.html + forklaring(p2) + '</div>' : '') +
    '</div>';

  // Stablede stolper per 100 sysselsatte
  const rader = sammen.map(([nv, rr]) => ({nv, deler: fbPer100(rr), tot: fbOkonIDag(rr)}));
  const maks = Math.max(...rader.map(x => x.tot));
  const stolper = rader.map(x => '<div class="fb-stolpe-rad"><div class="fb-stolpe-navn">' + x.nv + '</div><div class="fb-stolpe-spor"><div class="fb-stolpe" style="width:' + (x.tot / maks * 100).toFixed(1) + '%">' +
      x.deler.map(d => '<i style="width:' + (d.v / x.tot * 100).toFixed(2) + '%;background:' + FB_FARGE[d.k] + '" title="' + d.l + ': ' + fbT(d.v, 1) + '"></i>').join('') +
    '</div><b>' + fbT(x.tot, 1) + '</b></div></div>').join('');
  const tabell = '<div class="fb-scroll"><table class="fb-tabell"><thead><tr><th>Per 100 sysselsatte</th>' + rader.map(x => '<th>' + x.nv + '</th>').join('') + '</tr></thead><tbody>' +
    rader[0].deler.map((d, i) => '<tr><td><i style="background:' + FB_FARGE[d.k] + '"></i>' + d.l + '</td>' + rader.map(x => '<td>' + fbT(x.deler[i].v, 1) + '</td>').join('') + '</tr>').join('') +
    '<tr class="sum"><td>I alt</td>' + rader.map(x => '<td>' + fbT(x.tot, 1) + '</td>').join('') + '</tr></tbody></table></div>';

  // Utvikling og scenarioer
  const ix = a => a.map(v => v / a[0] * 100);
  const graf = (window.NN ? NN.placeholder('linjer', {
    x: D.aar,
    serier: [
      {navn:'Forsørgerbrøk, ' + navn, kort:'Alder', data: ix(r.demo), farge:'cat-4'},
      {navn:'Ikke-sysselsatte per 100 sysselsatte, ' + navn, kort:'Arbeid', data: ix(r.okon), farge:'accent', uthev:true}
    ].concat(rKey !== 'landet' ? [
      {navn:'Forsørgerbrøk, landet', kort:'Landet', data: ix(L.demo), farge:'cat-4', stil:'stiplet', svak:true, etikett:false},
      {navn:'Ikke-sysselsatte per 100 sysselsatte, landet', kort:'Landet', data: ix(L.okon), farge:'accent', stil:'stiplet', svak:true, etikett:false}
    ] : []),
    format:'indeks', xTicks:[2026, 2040, 2050], hoyde:260,
    yTittel:'Indeks, 2026 = 100. Alder: forsørgerbrøken. Arbeid: ikke-sysselsatte per 100 sysselsatte. Heltrukket: ' + navn + '; stiplet: landet.',
    kilde:'SSB 14746 (hovedalternativet), 07984 og 13563. Sysselsettingsraten i hver aldersgruppe holdes som i 2024–2025.'
  }, 300) : '');
  const scen = '<div class="fb-scroll"><table class="fb-tabell"><thead><tr><th>' + D.aar[n] + '</th><th>Ikke-sysselsatte per 100 sysselsatte</th><th>Sysselsatte</th></tr></thead><tbody>' +
    '<tr><td>Grunnbane: sysselsetting per aldersgruppe som i dag</td><td>' + fbT(r.okon[n], 1) + '</td><td>' + fbT(sy[n]) + '</td></tr>' +
    '<tr><td>A. AAP og uføretrygd på landsnivå' + (r.okonA[n] === r.okon[n] ? ' (allerede på eller under)' : '') + '</td><td>' + fbT(r.okonA[n], 1) + '</td><td>' + fbT(r.syssA2050) + '</td></tr>' +
    '<tr><td>B. 5 prosentpoeng flere i arbeid i alderen 55–74</td><td>' + fbT(r.okonB[n], 1) + '</td><td>' + fbT(r.syssB2050) + '</td></tr>' +
    '</tbody></table></div>';

  const kpi = '<div class="fb-kpis">' +
    '<div class="k"><div class="v">' + fbT(demo0, 1) + ' → ' + fbT(r.demo[n], 1) + '</div><div class="l">Forsørgerbrøk 2026–' + D.aar[n] + '</div><div class="h">65+ per 100 i alderen 20–64 · landet ' + fbT(demoL, 1) + ' → ' + fbT(L.demo[n], 1) + '</div></div>' +
    '<div class="k"><div class="v">' + fbT(okon0, 1) + ' → ' + fbT(r.okon[n], 1) + '</div><div class="l">Ikke-sysselsatte per 100 sysselsatte</div><div class="h">alle aldre · landet ' + fbT(okonL, 1) + ' → ' + fbT(L.okon[n], 1) + '</div></div>' +
    '<div class="k"><div class="v' + (aap > aapL + 1 ? ' down' : '') + '">' + fbPst(aap) + '</div><div class="l">AAP eller uføretrygd, 20–66 år</div><div class="h">landet ' + fbPst(aapL) + ' · SSB 13563, ' + D.status_aar + '</div></div>' +
    '<div class="k"><div class="v' + (dSy < -5 ? ' down' : '') + '">' + (dSy >= 0 ? '+' : '−') + fbPst(Math.abs(dSy)) + '</div><div class="l">Sysselsatte 2026–' + D.aar[n] + '</div><div class="h">' + fbT(sy[0]) + ' → ' + fbT(sy[n]) + ' · alt annet likt</div></div>' +
    '</div>';

  return '<div class="card fb-kort" id="' + id + '"' + (opts.utenRamme ? ' style="border:0;padding:0;background:none"' : '') + '>' +
    (opts.utenTittel ? '' : '<div class="ch"><h3 class="serif">Hvem bærer hvem?</h3></div>') +
    '<p class="hint">To måter å telle på. <b>Forsørgerbrøken</b> teller alder: innbyggere 65+ per 100 i alderen 20–64, som hos SSB og OECD. <b>Ikke-sysselsatte per 100 sysselsatte</b> teller faktisk arbeid: alle som ikke er i arbeid — også uføre, studenter og barn — per 100 personer i arbeid. Mer på <a href="metode.html#forsorgerbyrde">metodesiden</a>.</p>' +
    kpi +
    '<p class="fb-p">' + obs + '</p>' +
    '<h4 class="fb-h4">100 personer i alderen 20–66 år, etter hva de gjør (4. kvartal ' + D.status_aar + ')</h4>' + prikkHTML +
    '<h4 class="fb-h4">Hvem forsørges per 100 sysselsatte?</h4>' + stolper + tabell +
    '<h4 class="fb-h4">Mot ' + D.aar[n] + ': de to målene beveger seg ulikt</h4>' + graf +
    '<p class="fb-p">' + hyp + '</p>' + scen +
    '<p class="hint" style="margin-top:8px;font-size:11.5px">Kilder: SSB 13563 (arbeidsstyrkestatus, bosted), 07459, 07984 og 14746. AAP og uføretrygd telles samlet av SSB. En sysselsatt har arbeidet minst én time i referanseuka, så en deltidsansatt teller som én sysselsatt. Målet teller et barn, en pensjonist og en uføretrygdet likt, selv om de koster ulikt og finansieres ulikt.' +
    (liten ? ' <b>' + navn + ' er liten, så noen få personer kan endre tallene mye.</b>' : '') + '</p>' +
  '</div>';
}

function renderBofastChart(){
  const host=document.getElementById('bofastChart'); if(!host) return;
  host.innerHTML = '<div class="bofast-chart">'+bofastChartHTML()+'</div>';
}

function sourceTableHTML(filter){
  const ids=Object.keys(SOURCES);
  const rows=ids.filter(id=>{
    if(!filter||filter==='all') return true;
    const s=SOURCES[id];
    if(filter.startsWith('metric:')) return s.metric_type===filter.slice(7);
    if(filter.startsWith('type:')) return s.publisher_type===filter.slice(5);
    return true;
  }).map(id=>{
    const s=SOURCES[id];
    const metricChip = ({
      kohort_retensjon:'<span class="src-chip">Kohortbevaring</span>',
      stock_snapshot:'<span class="src-chip t-stock">Bestandstall</span>',
      akkumulert_nettoflytting:'<span class="src-chip t-acc">Akkumulert flytting</span>',
      raadata:'<span class="src-chip t-raw">Rådata</span>'
    })[s.metric_type]||'';
    const flags=[];
    flags.push(s.excludes_emigration?'ekskl. utvandring':'inkl. utvandring');
    if(s.ukraine_included===false) flags.push('ekskl. Ukraina');
    flags.push('per '+s.geo_level);
    return '<tr id="src-'+id+'">'+
      '<td><div class="src-title">'+s.title+'</div>'+
        '<div class="src-pub">'+s.publisher+' · '+s.period_start+'–'+s.period_end+'</div>'+
        '<div class="src-meta">'+metricChip+'<span style="color:var(--ink3)">'+flags.join(' · ')+'</span></div>'+
        (s.caveat?'<div class="src-meta" style="margin-top:6px;line-height:1.5"><b>Forbehold:</b> '+s.caveat+'</div>':'')+
      '</td>'+
      '<td style="width:140px;text-align:right"><a class="src-link" href="'+s.url+'" target="_blank" rel="noopener">Åpne kilde →</a></td>'+
    '</tr>';
  }).join('');
  return '<table class="source-table"><thead><tr><th>Kilde</th><th></th></tr></thead><tbody>'+(rows||'<tr><td colspan="2" style="text-align:center;color:var(--ink3);padding:20px">Ingen kilder matcher filteret.</td></tr>')+'</tbody></table>';
}

function renderSourcePanel(){
  const host=document.getElementById('sourcePanel'); if(!host) return;
  const btn=document.querySelector('#sourceFilter button[aria-pressed=true]');
  const f=btn?btn.dataset.sf:'all';
  host.innerHTML = sourceTableHTML(f);
}

function initRefugeesStep(){
  renderFlowChart();
  renderBofastChart();
  renderSourcePanel();
  attachMethodBadges();
  // Wire up flow toggle
  document.querySelectorAll('#flowToggle button').forEach(b=>{
    b.onclick=()=>{
      document.querySelectorAll('#flowToggle button').forEach(x=>x.setAttribute('aria-pressed',x===b?'true':'false'));
      renderFlowChart();
    };
  });
  // Wire up source filter
  document.querySelectorAll('#sourceFilter button').forEach(b=>{
    b.onclick=()=>{
      document.querySelectorAll('#sourceFilter button').forEach(x=>x.setAttribute('aria-pressed',x===b?'true':'false'));
      renderSourcePanel();
    };
  });
}
initRefugeesStep();

/* gentle nudge: pulse tour-button first visit */
try{
  if(!localStorage.getItem('nn_tour_seen')){
    const b=document.getElementById('tourstart');
    b.style.animation='popIn .6s ease both, popIn .9s ease 1.2s both';
  }
}catch(_){}
