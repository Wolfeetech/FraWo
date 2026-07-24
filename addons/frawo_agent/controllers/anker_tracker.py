# -*- coding: utf-8 -*-
import logging
from datetime import date
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

KIOSK_HTML = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0c0f14">
<title>Anker Tracker</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/bold/style.css">
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css">
<style>
:root{--bg:#0c0f14;--surface:#13181f;--surface2:#1a2030;--border:rgba(255,255,255,.06);--border-a:rgba(14,165,233,.5);--text:#f1f5f9;--muted:#64748b;--subtle:#334155;--accent:#0ea5e9;--aglow:rgba(14,165,233,.15);--accent2:#8b5cf6;--ok:#10b981;--err:#ef4444;--warn:#f59e0b}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;font-family:'Inter',-apple-system,sans-serif;background:var(--bg);color:var(--text);-webkit-tap-highlight-color:transparent;overscroll-behavior:none}
#app{display:flex;flex-direction:column;height:100dvh;max-width:480px;margin:0 auto;overflow:hidden}
/* HEADER */
.hdr{background:linear-gradient(180deg,rgba(14,165,233,.08),transparent);border-bottom:1px solid var(--border);padding:12px 16px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0;backdrop-filter:blur(20px);position:sticky;top:0;z-index:40}
.hdr-brand{display:flex;align-items:center;gap:10px}
.hdr-icon{width:36px;height:36px;background:linear-gradient(135deg,var(--accent),var(--accent2));border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 4px 16px var(--aglow)}
.hdr-t{font-size:15px;font-weight:800;letter-spacing:-.3px}
.hdr-s{font-size:9px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:var(--accent);opacity:.8}
.status{display:flex;align-items:center;gap:6px;font-size:10px;font-weight:600;color:var(--ok);background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.2);padding:4px 10px;border-radius:20px}
.status span{width:6px;height:6px;border-radius:50%;background:var(--ok);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
/* NAV */
.bnav{display:flex;background:var(--surface);border-top:1px solid var(--border);flex-shrink:0;padding-bottom:env(safe-area-inset-bottom,0)}
.nbtn{flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;padding:10px 0;font-size:9px;font-weight:600;letter-spacing:.5px;text-transform:uppercase;color:var(--muted);background:none;border:none;cursor:pointer;transition:all .2s}
.nbtn i{font-size:22px}
.nbtn.active{color:var(--accent)}
.nbtn.active i{filter:drop-shadow(0 0 8px var(--accent))}
/* MAIN */
.main{flex:1;overflow-y:auto;overflow-x:hidden;padding:16px;display:flex;flex-direction:column;gap:14px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.main::-webkit-scrollbar{display:none}
.view{display:none;flex-direction:column;gap:14px}
.view.active{display:flex}
/* CARD */
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:14px}
.clbl{font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:12px}
/* PERSONS */
.prow{display:flex;gap:10px;overflow-x:auto;padding-bottom:4px;scrollbar-width:none}
.prow::-webkit-scrollbar{display:none}
.pbtn{display:flex;flex-direction:column;align-items:center;gap:5px;flex-shrink:0;background:none;border:none;cursor:pointer}
.pavatar{width:52px;height:52px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;background:var(--surface2);border:2px solid var(--border);transition:all .2s;color:var(--muted)}
.pbtn.active .pavatar{background:var(--aglow);border-color:var(--accent);color:var(--accent);box-shadow:0 0 20px var(--aglow)}
.pname{font-size:10px;font-weight:600;color:var(--muted);max-width:56px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pbtn.active .pname{color:var(--accent);font-weight:700}
/* SECTION */
.sec-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.sec-t{font-size:14px;font-weight:700}
.sec-b{font-size:9px;font-weight:600;color:var(--muted);background:var(--surface);border:1px solid var(--border);padding:3px 8px;border-radius:20px}
/* PRODUCT GRID */
.pgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.pcard{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:14px 10px 10px;display:flex;flex-direction:column;align-items:center;gap:3px;cursor:pointer;transition:all .15s;position:relative;overflow:hidden}
.pcard:active{transform:scale(.94);border-color:var(--accent);background:var(--surface2);box-shadow:0 0 20px var(--aglow)}
.pemoji{font-size:32px;margin-bottom:2px;line-height:1}
.pbrand{font-size:8px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--muted)}
.pname2{font-size:13px;font-weight:700;color:var(--text);text-align:center;line-height:1.2}
.pinfo{font-size:9px;color:var(--muted)}
.pprice{font-size:12px;font-weight:800;color:var(--accent);margin-top:2px}
.pprice-zero{color:var(--subtle)}
.pcard-btns{display:flex;gap:6px;width:100%;margin-top:6px}
.pbtn-bottle,.pbtn-crate{flex:1;display:flex;align-items:center;justify-content:center;gap:4px;padding:6px 4px;border:1px solid var(--border);border-radius:10px;background:var(--surface2);cursor:pointer;font-size:11px;font-weight:700;transition:all .15s;color:var(--text)}
.pbtn-bottle:active{background:var(--accent);color:#fff;transform:scale(.95)}
.pbtn-crate:active{background:#f59e0b;color:#fff;transform:scale(.95)}
.pbtn-crate{border-color:rgba(245,158,11,.3)}
.pentnahme{font-size:10px;font-weight:700;color:var(--accent);margin-top:2px}
.master-crown{font-size:10px;margin-left:2px}
.fav-badge{position:absolute;top:8px;left:8px;font-size:12px;line-height:1;z-index:2}
.tbadge{position:absolute;top:8px;right:8px;font-size:8px;font-weight:700;padding:2px 5px;border-radius:4px;letter-spacing:.5px}
.tbadge.alc{background:rgba(239,68,68,.15);color:#fca5a5}
.tbadge.free{background:rgba(16,185,129,.15);color:#6ee7b7}
/* BILLING */
.bhdr{display:flex;align-items:center;gap:10px;margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid var(--border)}
.bicon{width:36px;height:36px;border-radius:10px;background:var(--aglow);border:1px solid var(--border-a);display:flex;align-items:center;justify-content:center;color:var(--accent);font-size:18px}
.btitle{font-size:14px;font-weight:700}
.bsub{font-size:10px;color:var(--muted)}
.cbk{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:12px;margin-bottom:8px}
.cbk-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.cbk-n{font-size:13px;font-weight:700;display:flex;align-items:center;gap:8px}
.cdot{width:8px;height:8px;border-radius:50%}
.ctbdg{font-size:10px;font-weight:600;background:var(--surface);border:1px solid var(--border);padding:2px 8px;border-radius:20px;color:var(--muted)}
.pglbl{font-size:8px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:5px}
.pglbl.alc{color:#fca5a5}.pglbl.free{color:#6ee7b7}
.prow2{display:flex;justify-content:space-between;align-items:center;padding:7px 10px;background:var(--surface);border-radius:8px;margin-bottom:4px;font-size:11px}
.prn{display:flex;align-items:center;gap:6px;color:var(--text)}
.pra{font-weight:700;color:var(--text);text-align:right}
.chl{color:var(--accent)}
.bill-btn{width:100%;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border:none;border-radius:12px;padding:14px;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:8px;cursor:pointer;transition:all .2s;box-shadow:0 4px 20px var(--aglow);margin-top:14px}
.bill-btn:active{transform:scale(.97)}
/* HISTORY */
.hist-i{display:flex;align-items:center;justify-content:space-between;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:10px 12px;gap:10px}
.hl{display:flex;align-items:center;gap:10px;flex:1;min-width:0}
.hemo{width:38px;height:38px;border-radius:10px;background:var(--surface2);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}
.hname{font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.htime{font-size:10px;color:var(--muted)}
.hr2{display:flex;align-items:center;gap:6px;flex-shrink:0}
.hav{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800}
.hdel{background:none;border:none;color:var(--subtle);font-size:16px;cursor:pointer;padding:4px}
.hdel:hover{color:var(--err)}
/* MANAGE */
.tabs{display:flex;background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:3px;gap:3px}
.tabb{flex:1;padding:8px;font-size:11px;font-weight:700;border:none;border-radius:8px;cursor:pointer;transition:all .2s;background:none;color:var(--muted)}
.tabb.active{background:var(--surface);color:var(--text);box-shadow:0 1px 4px rgba(0,0,0,.3)}
.flbl{font-size:10px;font-weight:600;color:var(--muted);margin-bottom:5px;display:block}
.finp{width:100%;background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:10px 12px;font-size:13px;color:var(--text);font-family:inherit;outline:none;transition:border-color .2s}
.finp:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--aglow)}
.frow{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.frow4{display:grid;grid-template-columns:64px 1fr;gap:8px}
.sbtn{width:100%;background:var(--accent);color:#fff;border:none;border-radius:10px;padding:12px;font-size:12px;font-weight:700;cursor:pointer;transition:all .15s;display:flex;align-items:center;justify-content:center;gap:6px}
.sbtn:active{transform:scale(.97);background:#0284c7}
.mi{display:flex;align-items:center;justify-content:space-between;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:10px 12px}
.mil{display:flex;align-items:center;gap:10px;flex:1;min-width:0}
.mie{font-size:22px}
.min{font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mis{font-size:10px;color:var(--muted)}
.mdel{background:none;border:none;color:var(--subtle);font-size:18px;cursor:pointer;padding:4px 6px}
.mdel:hover{color:var(--err)}
/* MODAL */
.moverlay{position:fixed;inset:0;background:rgba(0,0,0,.8);backdrop-filter:blur(8px);z-index:100;display:none;align-items:flex-end;justify-content:center}
.moverlay.open{display:flex}
.msheet{background:var(--surface);border:1px solid var(--border);border-radius:24px 24px 0 0;padding:24px;width:100%;max-width:480px;animation:slideUp .25s ease;padding-bottom:calc(24px + env(safe-area-inset-bottom,0))}
@keyframes slideUp{from{transform:translateY(100%);opacity:0}to{transform:translateY(0);opacity:1}}
.mhnd{width:36px;height:4px;background:var(--border);border-radius:2px;margin:0 auto 20px}
.mico{width:48px;height:48px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:14px}
.mico.danger{background:rgba(239,68,68,.15);color:var(--err)}
.mico.confirm{background:rgba(16,185,129,.15);color:var(--ok)}
.mtitle{font-size:16px;font-weight:800;margin-bottom:6px}
.mdesc{font-size:12px;color:var(--muted);line-height:1.6;margin-bottom:20px}
.macts{display:flex;gap:10px}
.mcanc{flex:1;padding:12px;border:1px solid var(--border);border-radius:10px;background:none;color:var(--muted);font-size:12px;font-weight:600;cursor:pointer}
.mcfm{flex:1;padding:12px;border:none;border-radius:10px;font-size:12px;font-weight:700;cursor:pointer;transition:all .15s}
.mcfm.danger{background:var(--err);color:#fff}
.mcfm.confirm{background:var(--ok);color:#fff}
.mcfm:active{transform:scale(.97)}
/* TOAST */
#tc{position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:200;display:flex;flex-direction:column;gap:8px;pointer-events:none;width:90%;max-width:400px}
.toast{background:rgba(19,24,31,.95);backdrop-filter:blur(20px);border:1px solid var(--border);border-radius:12px;padding:12px 16px;display:flex;align-items:center;gap:10px;font-size:12px;font-weight:600;animation:tin .3s ease;box-shadow:0 8px 32px rgba(0,0,0,.5)}
.toast i{font-size:18px}
@keyframes tin{from{transform:translateY(-20px);opacity:0}to{transform:translateY(0);opacity:1}}
/* EMPTY */
.empty{text-align:center;padding:32px 16px;background:var(--surface);border:1px dashed var(--border);border-radius:16px;color:var(--muted)}
.empty i{font-size:36px;margin-bottom:8px;opacity:.4;display:block}
.empty p{font-size:12px}
.empty a{color:var(--accent);font-weight:700;text-decoration:none;cursor:pointer}
.skel{background:var(--surface2);border-radius:10px;animation:sk 1.5s ease-in-out infinite}
@keyframes sk{0%,100%{opacity:.5}50%{opacity:1}}
</style>
</head>
<body>
<div id="app">
  <header class="hdr">
    <div class="hdr-brand">
      <div class="hdr-icon">⚓</div>
      <div>
        <div class="hdr-t">Anker Tracker</div>
        <div class="hdr-s">FraWo GbR</div>
      </div>
    </div>
    <div class="status" id="db-status"><span></span> Verbinde...</div>
  </header>

  <main class="main" id="mscroll">
    <!-- TRACKER -->
    <div class="view active" id="view-tracker">
      <div class="card">
        <div class="clbl">Wer trinkt?</div>
        <div class="prow" id="pcarousel">
          <div class="skel" style="width:52px;height:52px;border-radius:14px;flex-shrink:0"></div>
          <div class="skel" style="width:52px;height:52px;border-radius:14px;flex-shrink:0"></div>
          <div class="skel" style="width:52px;height:52px;border-radius:14px;flex-shrink:0"></div>
        </div>
      </div>
      <div>
        <div class="sec-hdr">
          <span class="sec-t">Getraenk buchen</span>
          <span class="sec-b">1 Tap = 1 Flasche</span>
        </div>
        <div class="pgrid" id="pgrid">
          <div class="skel" style="height:140px;border-radius:16px;"></div>
          <div class="skel" style="height:140px;border-radius:16px;"></div>
          <div class="skel" style="height:140px;border-radius:16px;"></div>
          <div class="skel" style="height:140px;border-radius:16px;"></div>
        </div>
      </div>
    </div>

    <!-- HISTORY -->
    <div class="view" id="view-history">
      <div class="card">
        <div class="bhdr">
          <div class="bicon"><i class="ph ph-receipt"></i></div>
          <div>
            <div class="btitle">Abrechnungs-Uebersicht</div>
            <div class="bsub">Nicht abgerechnete Buchungen</div>
          </div>
        </div>
        <div id="bsummary"><p style="font-size:12px;color:var(--muted);text-align:center;padding:16px 0">Keine Daten.</p></div>
        <div id="baction" style="display:none">
          <button class="bill-btn" onclick="triggerBilling()"><i class="ph ph-printer"></i> Abrechnen &amp; Drucken</button>
        </div>
      </div>
      <div>
        <div class="sec-hdr"><span class="sec-t">Letzte Aktivitaeten</span></div>
        <div id="hlist" style="display:flex;flex-direction:column;gap:8px"></div>
      </div>
    </div>

    <!-- MANAGE -->
    <div class="view" id="view-manage">
      <div class="tabs">
        <button class="tabb active" id="tab-products" onclick="switchMTab('products')">Getraenke</button>
        <button class="tabb" id="tab-persons" onclick="switchMTab('persons')">Personen</button>
      </div>
      <div id="sec-products">
        <div class="card" style="margin-bottom:10px">
          <div class="clbl">Neues Getraenk</div>
          <form id="form-product" style="display:flex;flex-direction:column;gap:10px">
            <div class="frow4">
              <div><label class="flbl">Emoji</label><input class="finp" id="pe" type="text" placeholder="&#127866;" style="text-align:center;font-size:20px" required></div>
              <div><label class="flbl">Name</label><input class="finp" id="pn" type="text" placeholder="z.B. Helles" required></div>
            </div>
            <div class="frow">
              <div><label class="flbl">Hersteller</label><input class="finp" id="pm" type="text" placeholder="z.B. Augustiner" required></div>
              <div><label class="flbl">Groesse (L)</label><input class="finp" id="pv" type="number" step="0.01" min="0.1" placeholder="0.5" required></div>
            </div>
            <div class="frow">
              <div><label class="flbl">Kategorie</label>
                <select class="finp" id="pt"><option value="alc">Alkoholisch</option><option value="free">Alkoholfrei</option></select>
              </div>
              <div><label class="flbl">Fl./Kiste</label><input class="finp" id="pc" type="number" min="1" max="100" value="20" required></div>
            </div>
            <div>
              <label class="flbl">Preis/Flasche (€)</label>
              <input class="finp" id="pprice" type="number" step="0.01" min="0" placeholder="0.00">
            </div>
            <button class="sbtn" type="submit"><i class="ph ph-plus-circle"></i> Hinzufuegen</button>
          </form>
        </div>
        <div id="manage-plist" style="display:flex;flex-direction:column;gap:8px"></div>
      </div>
      <div id="sec-persons" style="display:none">
        <div class="card" style="margin-bottom:10px">
          <div class="clbl">Neue Person</div>
          <form id="form-person" style="display:flex;flex-direction:column;gap:10px">
            <div><label class="flbl">Vorname / Name</label><input class="finp" id="newpname" type="text" placeholder="z.B. Christian" required></div>
            <button class="sbtn" type="submit"><i class="ph ph-user-plus"></i> Person anlegen</button>
          </form>
        </div>
        <div id="manage-persons" style="display:flex;flex-direction:column;gap:8px"></div>
      </div>
    </div>
  </main>

  <nav class="bnav">
    <button class="nbtn active" id="nav-tracker" onclick="switchView('tracker')">
      <i class="ph ph-beer-bottle"></i>Tracker
    </button>
    <button class="nbtn" id="nav-history" onclick="switchView('history')">
      <i class="ph ph-chart-bar"></i>Verlauf
    </button>
    <button class="nbtn" id="nav-manage" onclick="switchView('manage')">
      <i class="ph ph-gear-six"></i>Verwaltung
    </button>
  </nav>

  <div id="tc"></div>

  <div class="moverlay" id="modal">
    <div class="msheet">
      <div class="mhnd"></div>
      <div class="mico danger" id="mico"><i id="micoi" class="ph ph-warning-circle"></i></div>
      <div class="mtitle" id="mtitle">Element loeschen?</div>
      <div class="mdesc" id="mdesc">Diese Aktion kann nicht rueckgaengig gemacht werden.</div>
      <div class="macts">
        <button class="mcanc" id="mcanc">Abbrechen</button>
        <button class="mcfm danger" id="mcfm">Loeschen</button>
      </div>
    </div>
  </div>
</div>

<script>
const ST={pid:null,consumers:[],products:[],consumptions:[]};
let pending=null;
const COLORS=[['#fca5a5','#7f1d1d'],['#93c5fd','#1e3a5f'],['#6ee7b7','#064e3b'],['#fcd34d','#78350f'],['#c4b5fd','#3b0764'],['#fb923c','#7c2d12']];
const ac=n=>{let h=0;for(let i=0;i<n.length;i++)h=n.charCodeAt(i)+((h<<5)-h);return COLORS[Math.abs(h)%COLORS.length]};

async function rpc(url,p={}){
  const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',method:'call',params:p})});
  const d=await r.json();if(d.error)throw new Error(d.error.data?.message||d.error.message);return d.result;
}

async function init(){
  try{
    const d=await rpc('/anker_tracker/get_data');
    ST.consumers=d.consumers||[];ST.products=d.products||[];
    ST.consumptions=(d.consumptions||[]).sort((a,b)=>b.timestamp-a.timestamp);
    ST.consumer_counts=d.consumer_counts||{};
    if(!ST.pid&&ST.consumers.length)ST.pid=ST.consumers[0].id;
    renderAll();setStatus(true);
  }catch(e){setStatus(false);toast('Ladefehler: '+e.message,'ph-x-circle','#ef4444')}
}

function setStatus(ok){
  const el=document.getElementById('db-status');
  if(ok)el.innerHTML='<span style="width:6px;height:6px;border-radius:50%;background:#10b981;animation:pulse 2s infinite;display:inline-block"></span> Odoo aktiv';
  else{el.innerHTML='<span style="width:6px;height:6px;border-radius:50%;background:#ef4444;display:inline-block"></span> Offline';el.style.color='#ef4444';el.style.borderColor='rgba(239,68,68,.3)'}
}

function renderAll(){renderP();renderProds();renderStats();renderHist();renderMProds();renderMPersons()}

function renderP(){
  const el=document.getElementById('pcarousel');if(!el)return;el.innerHTML='';
  // Sort: masters first (sequence), then guests
  const sorted=[...ST.consumers].sort((a,b)=>{
    const ra=a.role==='master'?0:1, rb=b.role==='master'?0:1;
    if(ra!==rb) return ra-rb;
    return (a.sequence||10)-(b.sequence||10)||(a.name||'').localeCompare(b.name||'');
  });
  sorted.forEach(p=>{
    const act=p.id===ST.pid;const[bg]=ac(p.name);
    const b=document.createElement('button');b.className='pbtn'+(act?' active':'');
    b.onclick=()=>{ST.pid=p.id;renderP();renderProds()};
    const crown=p.role==='master'?'<span class="master-crown">\u{1f451}</span>':'';
    b.innerHTML=`<div class="pavatar" style="${act?'':`background:${bg}22;color:${bg};border-color:${bg}44`}">${p.name[0].toUpperCase()}</div><div class="pname">${p.name}${crown}</div>`;
    el.appendChild(b);
  });
}

function renderProds(){
  const el=document.getElementById('pgrid');if(!el)return;
  if(!ST.products.length){el.innerHTML='<div class="empty" style="grid-column:span 2"><i class="ph ph-beer-bottle"></i><p>Keine Getraenke. <a onclick="switchView(\'manage\')" style="cursor:pointer">Anlegen</a></p></div>';return}
  el.innerHTML='';

  // Smart sort: personalized favorites first
  const cc=ST.consumer_counts||{};
  const myC=cc[ST.pid]||{};
  const sorted=[...ST.products].sort((a,b)=>{
    const pa=(myC[a.id]||0), pb=(myC[b.id]||0);
    if(pa!==pb) return pb-pa;
    const ga=(a.consumed_bottles||0), gb=(b.consumed_bottles||0);
    if(ga!==gb) return gb-ga;
    return a.name.localeCompare(b.name);
  });
  const myTop3=Object.entries(myC).sort((a,b)=>b[1]-a[1]).slice(0,3).map(e=>parseInt(e[0]));

  sorted.forEach(p=>{
    const card=document.createElement('div');card.className='pcard';
    const priceStr=p.price_per_bottle>0?`${p.price_per_bottle.toFixed(2).replace('.',',')} \u20ac`:'?';
    const cratePrice=p.price_per_bottle>0?`${(p.price_per_bottle*(p.crate_size||20)).toFixed(2).replace('.',',')} \u20ac`:'?';
    const isFav=myTop3.includes(p.id);
    const favBadge=isFav?'<span class="fav-badge">\u2b50</span>':'';

    // Show entnahme counter if any
    const consumed=p.consumed_bottles||0;
    const crates_taken=p.consumed_crates||0;
    let entnahmeHtml='';
    if(consumed>0){
      const crateEq=Math.floor(consumed/(p.crate_size||20));
      const loose=consumed%(p.crate_size||20);
      let parts=[];
      if(crates_taken>0) parts.push(`${crates_taken}\ud83d\udce6`);
      if(loose>0||crates_taken===0) parts.push(`${consumed}\ud83c\udf7e`);
      entnahmeHtml=`<div class="pentnahme">${parts.join(' + ')}</div>`;
    }

    card.innerHTML=`<span class="tbadge ${p.is_alcoholic?'alc':'free'}">${p.is_alcoholic?'ALK':'FREI'}</span>${favBadge}
      <div class="pemoji">${p.emoji||'\ud83e\udd64'}</div>
      <div class="pbrand">${p.manufacturer||''}</div>
      <div class="pname2">${p.name}</div>
      <div class="pinfo">${p.volume?p.volume+'L':''} &middot; ${p.crate_size||20}er</div>
      ${entnahmeHtml}
      <div class="pcard-btns">
        <button class="pbtn-bottle" onclick="book(${p.id},'${p.name.replace(/'/g,"\\'")}')" title="1 Flasche">
          \ud83c\udf7e <span>${priceStr}</span>
        </button>
        <button class="pbtn-crate" onclick="book(${p.id},'${p.name.replace(/'/g,"\\'")}','crate')" title="Ganze Kiste (${p.crate_size||20} Fl.)">
          \ud83d\udce6 <span>${cratePrice}</span>
        </button>
      </div>`;
    el.appendChild(card);
  });
}

async function book(pid,pname,unitType='bottle'){
  if(!ST.pid){toast('Bitte erst eine Person auswaehlen!','ph-warning','#f59e0b');return}
  const p=ST.consumers.find(c=>c.id===ST.pid);
  const prod=ST.products.find(x=>x.id===pid);
  const qty=unitType==='crate'?(prod?.crate_size||20):1;
  const lbl=unitType==='crate'?`1 Kiste (${qty} Fl.)`:'+1';
  try{
    const r=await rpc('/anker_tracker/consume',{consumer_id:ST.pid,product_id:pid,unit_type:unitType});
    if(r.status==='success'){
      ST.consumptions.unshift({id:r.id,consumerId:ST.pid,productId:pid,timestamp:Date.now(),unitType,quantity:r.quantity||qty});
      if(prod){prod.consumed_bottles=(prod.consumed_bottles||0)+(r.quantity||qty);if(unitType==='crate')prod.consumed_crates=(prod.consumed_crates||0)+1}
      renderStats();renderHist();renderProds();
      toast(`${lbl} ${pname} fuer ${p?.name}`,'ph-check-circle','#10b981');
    }
  }catch(e){toast('Buchungsfehler: '+e.message,'ph-x-circle','#ef4444')}
}

function renderStats(){
  const el=document.getElementById('bsummary'),act=document.getElementById('baction');if(!el)return;
  if(!ST.consumptions.length){el.innerHTML='<p style="font-size:12px;color:var(--muted);text-align:center;padding:16px 0">Keine offenen Buchungen.</p>';if(act)act.style.display='none';return}
  const s={};ST.consumers.forEach(c=>{s[c.id]={name:c.name,role:c.role||'guest',products:{}}});
  ST.consumptions.forEach(i=>{
    if(!s[i.consumerId])return;const p=ST.products.find(x=>x.id===i.productId);if(!p)return;
    const qty=i.quantity||1;const ut=i.unitType||'bottle';
    if(!s[i.consumerId].products[p.id])s[i.consumerId].products[p.id]={name:p.name,emoji:p.emoji||'\ud83e\udd64',manufacturer:p.manufacturer||'',volume:p.volume,isAlc:p.is_alcoholic,crate:parseInt(p.crate_size)||1,price:p.price_per_bottle||0,pfandBottle:p.pfand_per_bottle||0.08,pfandCrate:p.pfand_per_crate||1.50,bottles:0,crates:0};
    s[i.consumerId].products[p.id].bottles+=qty;
    if(ut==='crate')s[i.consumerId].products[p.id].crates++;
  });
  let html='';let hasData=false;let grandTotal=0;let grandPfand=0;
  Object.entries(s).forEach(([cid,c])=>{
    const ks=Object.keys(c.products);if(!ks.length)return;hasData=true;
    const[bg]=ac(c.name);
    const roleIcon=c.role==='master'?'\ud83d\udc51':'';
    const total=ks.reduce((a,k)=>a+c.products[k].bottles,0);
    const euros=ks.reduce((a,k)=>a+c.products[k].bottles*c.products[k].price,0);
    const pfand=ks.reduce((a,k)=>{const d=c.products[k];return a+(d.bottles*d.pfandBottle)+(d.crates*d.pfandCrate)},0);
    grandTotal+=euros;grandPfand+=pfand;
    html+=`<div class="cbk"><div class="cbk-hdr"><span class="cbk-n"><span class="cdot" style="background:${bg}"></span>${roleIcon}${c.name}</span><span class="ctbdg">${total} Fl. &bull; <span style="color:var(--accent)">${euros.toFixed(2).replace('.',',')} &euro;</span></span></div>`;
    const grp=(items,lbl,cls)=>{
      if(!items.length)return'';
      let g=`<div class="pglbl ${cls}">${lbl}</div>`;
      items.forEach(p=>{
        const cratesTaken=p.crates;
        const looseBtls=p.bottles-(cratesTaken*p.crate);
        let amt=`<span>${p.bottles} Fl.</span>`;
        if(cratesTaken>0){
          amt=`<span class="chl">${cratesTaken} Kiste${cratesTaken>1?'n':''}</span>`;
          if(looseBtls>0)amt+=` + ${looseBtls} Fl.`;
        }
        const subtotal=p.price>0?` <span style="color:var(--accent);font-weight:700">${(p.bottles*p.price).toFixed(2).replace('.',',')} &euro;</span>`:'';
        const pfandStr=` <span style="color:var(--muted);font-size:10px">+${((p.bottles*p.pfandBottle)+(p.crates*p.pfandCrate)).toFixed(2).replace('.',',')}P</span>`;
        g+=`<div class="prow2"><span class="prn"><span>${p.emoji}</span><span>${p.manufacturer} ${p.name} ${p.volume?p.volume+'L':''}</span></span><span class="pra">${amt}${subtotal}${pfandStr}</span></div>`;
      });return g;
    };
    const alc=ks.filter(k=>c.products[k].isAlc).map(k=>c.products[k]);
    const free=ks.filter(k=>!c.products[k].isAlc).map(k=>c.products[k]);
    html+=grp(alc,'Alkoholisch (19% MwSt)','alc')+grp(free,'Alkoholfrei (7% MwSt)','free')+'</div>';
  });
  if(hasData&&grandTotal>0)html+=`<div style="display:flex;justify-content:space-between;padding:10px 4px 0;border-top:1px solid var(--border);margin-top:4px"><span style="font-size:11px;color:var(--muted)">Pfand: ${grandPfand.toFixed(2).replace('.',',')} &euro;</span><span style="font-size:13px;font-weight:800;color:var(--text)">Gesamt: <span style="color:var(--accent)">${(grandTotal+grandPfand).toFixed(2).replace('.',',')} &euro;</span></span></div>`;
  el.innerHTML=html||'<p style="font-size:12px;color:var(--muted);text-align:center;padding:16px 0">Keine Daten.</p>';
  if(act)act.style.display=hasData?'block':'none';
}

function renderHist(){
  const el=document.getElementById('hlist');if(!el)return;
  if(!ST.consumptions.length){el.innerHTML='<div class="empty"><i class="ph ph-clock-counter-clockwise"></i><p>Keine Aktivitaeten.</p></div>';return}
  el.innerHTML='';
  ST.consumptions.slice(0,60).forEach(item=>{
    const c=ST.consumers.find(x=>x.id===item.consumerId)||{name:'?'};
    const p=ST.products.find(x=>x.id===item.productId)||{name:'Geloescht',emoji:'❓'};
    const[bg]=ac(c.name);const lbl=p.manufacturer?`${p.manufacturer} ${p.name}`:p.name;
    const d=document.createElement('div');d.className='hist-i';
    d.innerHTML=`<div class="hl"><div class="hemo">${p.emoji}</div><div><div class="hname">${lbl}</div><div class="htime">${ft(item.timestamp)}</div></div></div><div class="hr2"><div class="hav" style="background:${bg}33;color:${bg}">${c.name[0].toUpperCase()}</div><button class="hdel" onclick="doDel('consumptions','${item.id}')"><i class="ph ph-trash"></i></button></div>`;
    el.appendChild(d);
  });
}

function renderMProds(){
  const el=document.getElementById('manage-plist');if(!el)return;
  if(!ST.products.length){el.innerHTML='<div class="empty"><i class="ph ph-beer-bottle"></i><p>Keine Getraenke.</p></div>';return}
  el.innerHTML='';
  ST.products.forEach(p=>{
    const d=document.createElement('div');d.className='mi';
    const priceLabel=p.price_per_bottle>0?` &bull; <span style="color:var(--accent);font-weight:700">${p.price_per_bottle.toFixed(2).replace('.',',')} &euro;</span>`:'';
    d.innerHTML=`<div class="mil"><span class="mie">${p.emoji}</span><div><div class="min">${p.name}</div><div class="mis">${p.manufacturer||''} &middot; ${p.volume||''}L &middot; ${p.crate_size}er${priceLabel}</div></div></div><button class="mdel" onclick="doDel('products','${p.id}')"><i class="ph ph-trash"></i></button>`;
    el.appendChild(d);
  });
}

function renderMPersons(){
  const el=document.getElementById('manage-persons');if(!el)return;
  if(!ST.consumers.length){el.innerHTML='<div class="empty"><i class="ph ph-users"></i><p>Keine Personen.</p></div>';return}
  el.innerHTML='';
  ST.consumers.forEach(p=>{
    const[bg]=ac(p.name);const d=document.createElement('div');d.className='mi';
    d.innerHTML=`<div class="mil"><div class="hav" style="background:${bg}33;color:${bg};width:36px;height:36px;border-radius:10px;font-size:14px">${p.name[0].toUpperCase()}</div><div class="min">${p.name}</div></div><button class="mdel" onclick="doDel('consumers','${p.id}')"><i class="ph ph-trash"></i></button>`;
    el.appendChild(d);
  });
}

document.getElementById('form-product').addEventListener('submit',async e=>{
  e.preventDefault();
  const name=document.getElementById('pn').value.trim(),emoji=document.getElementById('pe').value.trim()||'\ud83e\udd64';
  const manufacturer=document.getElementById('pm').value.trim(),volume=parseFloat(document.getElementById('pv').value);
  const is_alcoholic=document.getElementById('pt').value==='alc',crate_size=parseInt(document.getElementById('pc').value);
  const price_per_bottle=parseFloat(document.getElementById('pprice').value)||0;
  if(!name||!manufacturer||!volume)return;
  try{
    const r=await rpc('/anker_tracker/add_product',{name,emoji,manufacturer,volume,is_alcoholic,crate_size,price_per_bottle});
    if(r.status==='success'){ST.products.push({id:r.id,name,emoji,manufacturer,volume,is_alcoholic,crate_size,price_per_bottle});renderProds();renderMProds();e.target.reset();toast(emoji+' '+name+' hinzugefuegt!','ph-check-circle','#10b981')}
  }catch(ex){toast('Fehler: '+ex.message,'ph-x-circle','#ef4444')}
});

document.getElementById('form-person').addEventListener('submit',async e=>{
  e.preventDefault();const name=document.getElementById('newpname').value.trim();if(!name)return;
  try{
    const r=await rpc('/anker_tracker/add_consumer',{name});
    if(r.status==='success'){ST.consumers.push({id:r.id,name});renderP();renderMPersons();e.target.reset();toast(name+' hinzugefuegt!','ph-user-plus','#10b981')}
  }catch(ex){toast('Fehler: '+ex.message,'ph-x-circle','#ef4444')}
});

function doDel(type,id){
  showModal('danger','ph-trash','Loeschen?',
    type==='consumptions'?'Diese Buchung wird entfernt.':'Dieses Element wird archiviert.',
    async()=>{
      const r=await rpc('/anker_tracker/delete_item',{model_type:type,item_id:id});
      if(r.status==='success'){
        const nid=parseInt(id);
        if(type==='consumers'){ST.consumers=ST.consumers.filter(c=>c.id!==nid);if(ST.pid===nid)ST.pid=ST.consumers[0]?.id||null}
        else if(type==='products')ST.products=ST.products.filter(p=>p.id!==nid);
        else ST.consumptions=ST.consumptions.filter(c=>c.id!==nid);
        renderAll();toast('Geloescht!','ph-check','#10b981');
      }
    }
  );
}

window.triggerBilling=function(){
  window.open('/anker-tracker/print','_blank');
  showModal('confirm','ph-printer','Zaehler zuruecksetzen?',
    'Druckansicht geoeffnet. Jetzt alle Buchungen als "abgerechnet" archivieren und Kiosk auf 0 zuruecksetzen?',
    async()=>{
      const r=await rpc('/anker_tracker/bill_now');
      if(r.status==='success'){toast('Abgerechnet! '+r.count+' Buchungen archiviert.','ph-check-circle','#10b981');await init()}
    }
  );
};

function showModal(type,icon,title,desc,onOk){
  document.getElementById('mico').className='mico '+type;
  document.getElementById('micoi').className='ph '+icon;
  document.getElementById('mtitle').textContent=title;
  document.getElementById('mdesc').textContent=desc;
  const btn=document.getElementById('mcfm');btn.className='mcfm '+type;
  btn.textContent=type==='danger'?'Loeschen':'Bestaetigen';
  pending=onOk;document.getElementById('modal').classList.add('open');
}
document.getElementById('mcanc').onclick=()=>{document.getElementById('modal').classList.remove('open');pending=null};
document.getElementById('mcfm').onclick=async()=>{
  document.getElementById('modal').classList.remove('open');
  if(pending){try{await pending()}catch(e){toast('Fehler: '+e.message,'ph-x-circle','#ef4444')}pending=null}
};

window.switchView=function(v){
  ['tracker','history','manage'].forEach(x=>{
    document.getElementById('view-'+x).classList.toggle('active',x===v);
    document.getElementById('nav-'+x).classList.toggle('active',x===v);
  });document.getElementById('mscroll').scrollTop=0;
};
window.switchMTab=function(t){
  document.getElementById('sec-products').style.display=t==='products'?'':'none';
  document.getElementById('sec-persons').style.display=t==='persons'?'':'none';
  document.getElementById('tab-products').classList.toggle('active',t==='products');
  document.getElementById('tab-persons').classList.toggle('active',t==='persons');
};

function toast(msg,ico='ph-info',col='#0ea5e9'){
  const c=document.getElementById('tc'),t=document.createElement('div');
  t.className='toast';t.innerHTML=`<i class="ph ${ico}" style="color:${col}"></i><span>${msg}</span>`;
  c.appendChild(t);setTimeout(()=>{t.style.opacity='0';t.style.transform='translateY(-10px)';t.style.transition='all .3s';setTimeout(()=>t.remove(),300)},3200);
}

function ft(ts){
  const d=new Date(ts),now=new Date();
  const t=d.toLocaleTimeString('de-DE',{hour:'2-digit',minute:'2-digit'});
  return d.toDateString()===now.toDateString()?`Heute, ${t}`:`${d.toLocaleDateString('de-DE',{day:'2-digit',month:'2-digit'})}, ${t}`;
}

window.onload=init;
</script>
</body>
</html>"""


class AnkerTrackerController(http.Controller):

    @http.route(['/anker-tracker', '/anker_tracker'], type='http', auth='user')
    def anker_tracker_view(self, **kwargs):
        """Serves the Anker Tracker HTML kiosk as a direct HTTP response (bypasses QWeb XML escaping)."""
        return request.make_response(
            KIOSK_HTML,
            headers=[('Content-Type', 'text/html; charset=utf-8')]
        )

    @http.route('/anker-tracker/print', type='http', auth='user')
    def anker_tracker_print_view(self, **kwargs):
        """Renders the print-optimized A4 invoice layout for the beverage store."""
        try:
            consumers_model = request.env['anker.tracker.consumer'].sudo()
            products_model = request.env['anker.tracker.product'].sudo()
            consumptions_model = request.env['anker.tracker.consumption'].sudo()

            consumers = consumers_model.search([('active', '=', True)])
            products = products_model.search([('active', '=', True)])

            grand_total_bottles = 0
            product_totals = []
            for product in products:
                count = consumptions_model.search_count([
                    ('product_id', '=', product.id),
                    ('billed', '=', False)
                ])
                if count > 0:
                    grand_total_bottles += count
                    crates = count // (product.crate_size or 1)
                    bottles = count % (product.crate_size or 1)
                    product_totals.append({
                        'product': product,
                        'count': count,
                        'crates': crates,
                        'bottles': bottles,
                    })

            consumer_totals = []
            for consumer in consumers:
                consumer_records = consumptions_model.search([
                    ('consumer_id', '=', consumer.id),
                    ('billed', '=', False)
                ])
                count = len(consumer_records)
                if count > 0:
                    prod_details = {}
                    for rec in consumer_records:
                        p = rec.product_id
                        if p.id not in prod_details:
                            prod_details[p.id] = {
                                'name': p.name,
                                'emoji': p.emoji,
                                'manufacturer': p.manufacturer or '',
                                'volume': p.volume,
                                'count': 0
                            }
                        prod_details[p.id]['count'] += 1
                    consumer_totals.append({
                        'consumer': consumer,
                        'count': count,
                        'details': list(prod_details.values())
                    })

            today_str = date.today().strftime('%d.%m.%Y')
            return request.render('frawo_agent.anker_tracker_print_template', {
                'product_totals': product_totals,
                'consumer_totals': consumer_totals,
                'grand_total_bottles': grand_total_bottles,
                'today_str': today_str,
            })
        except Exception as e:
            _logger.error("Anker Tracker print view error: %s", e)
            return request.make_response(f"Fehler: {str(e)}", status=500)

    @http.route('/anker_tracker/get_data', type='jsonrpc', auth='user', methods=['POST'])
    def get_data(self, **kwargs):
        """Fetches active consumers, products, and recent unbilled consumptions."""
        try:
            consumers_model = request.env['anker.tracker.consumer'].sudo()
            products_model = request.env['anker.tracker.product'].sudo()
            consumptions_model = request.env['anker.tracker.consumption'].sudo()

            consumers = consumers_model.search_read([('active', '=', True)], ['id', 'name', 'role', 'sequence'])
            if not consumers:
                consumers_model.create([{'name': 'Wolfi'}, {'name': 'Franz'}])
                consumers = consumers_model.search_read([('active', '=', True)], ['id', 'name', 'role', 'sequence'])

            products = products_model.search_read(
                [('active', '=', True)],
                ['id', 'name', 'emoji', 'manufacturer', 'volume', 'is_alcoholic', 'crate_size', 'price_per_bottle',
                 'pfand_per_bottle', 'pfand_per_crate']
            )
            if not products:
                products_model.create([
                    {'name': 'Lager Hell', 'emoji': '🍺', 'manufacturer': 'Augustiner', 'volume': 0.5, 'is_alcoholic': True, 'crate_size': 20, 'price_per_bottle': 0.97},
                    {'name': 'Spezi', 'emoji': '🥤', 'manufacturer': 'Paulaner', 'volume': 0.33, 'is_alcoholic': False, 'crate_size': 24, 'price_per_bottle': 0.72},
                    {'name': 'Holderweisse', 'emoji': '🌾', 'manufacturer': 'Schaffler', 'volume': 0.5, 'is_alcoholic': True, 'crate_size': 1, 'price_per_bottle': 2.18},
                    {'name': 'Mineralwasser medium', 'emoji': '💧', 'manufacturer': 'Gerolsteiner', 'volume': 1.0, 'is_alcoholic': False, 'crate_size': 12, 'price_per_bottle': 0.79},
                ])
                products = products_model.search_read(
                    [('active', '=', True)],
                    ['id', 'name', 'emoji', 'manufacturer', 'volume', 'is_alcoholic', 'crate_size', 'price_per_bottle']
                )

            consumptions_records = consumptions_model.search([('billed', '=', False)], limit=500, order='timestamp desc')
            consumptions = []
            for c in consumptions_records:
                timestamp_ms = int(c.timestamp.timestamp() * 1000) if c.timestamp else 0
                consumptions.append({
                    'id': c.id,
                    'consumerId': c.consumer_id.id,
                    'productId': c.product_id.id,
                    'timestamp': timestamp_ms,
                    'unitType': c.unit_type or 'bottle',
                    'quantity': c.quantity or 1,
                })

            # --- Consumption rankings for smart sorting ---
            # Global consumption count per product (by total bottles)
            global_counts = {}  # product_id → total bottles
            global_crates = {}  # product_id → crate count
            for c in consumptions_records:
                pid = c.product_id.id
                qty = c.quantity or 1
                global_counts[pid] = global_counts.get(pid, 0) + qty
                if c.unit_type == 'crate':
                    global_crates[pid] = global_crates.get(pid, 0) + 1

            # Per-consumer counts for personalized ranking
            consumer_counts = {}  # consumer_id → {product_id → total bottles}
            for c in consumptions_records:
                cid = c.consumer_id.id
                pid = c.product_id.id
                qty = c.quantity or 1
                if cid not in consumer_counts:
                    consumer_counts[cid] = {}
                consumer_counts[cid][pid] = consumer_counts[cid].get(pid, 0) + qty

            # Enrich products with entnahme data
            for p in products:
                pid = p['id']
                p['consumed_bottles'] = global_counts.get(pid, 0)
                p['consumed_crates'] = global_crates.get(pid, 0)

            return {
                'consumers': consumers,
                'products': products,
                'consumptions': consumptions,
                'consumer_counts': consumer_counts,
            }
        except Exception as e:
            _logger.error("Anker Tracker get_data error: %s", e)
            return {'error': str(e)}

    @http.route('/anker_tracker/consume', type='jsonrpc', auth='user', methods=['POST'])
    def consume(self, consumer_id, product_id, unit_type='bottle', quantity=1, **kwargs):
        """Records a drink consumption. unit_type: 'bottle' or 'crate'.
        For crate: quantity is auto-set to crate_size."""
        try:
            consumption_model = request.env['anker.tracker.consumption'].sudo()
            product = request.env['anker.tracker.product'].sudo().browse(int(product_id))

            # Auto-set quantity for crate
            if unit_type == 'crate':
                quantity = product.crate_size or 20

            record = consumption_model.create({
                'consumer_id': int(consumer_id),
                'product_id': int(product_id),
                'unit_type': unit_type,
                'quantity': int(quantity),
            })
            _logger.info(
                "Anker Tracker: Consumption ID %s (%s, %s, %s, qty=%s)",
                record.id, consumer_id, product.name, unit_type, quantity
            )

            return {'status': 'success', 'id': record.id, 'quantity': quantity}
        except Exception as e:
            _logger.error("Anker Tracker consume error: %s", e)
            return {'status': 'error', 'message': str(e)}

    @http.route('/anker_tracker/add_consumer', type='jsonrpc', auth='user', methods=['POST'])
    def add_consumer(self, name, **kwargs):
        """Adds a new consumer/person."""
        try:
            record = request.env['anker.tracker.consumer'].sudo().create({'name': name})
            return {'status': 'success', 'id': record.id}
        except Exception as e:
            _logger.error("Anker Tracker add_consumer error: %s", e)
            return {'status': 'error', 'message': str(e)}

    @http.route('/anker_tracker/add_product', type='jsonrpc', auth='user', methods=['POST'])
    def add_product(self, name, emoji, manufacturer, volume, is_alcoholic, crate_size, price_per_bottle=0.0, **kwargs):
        """Adds a new beverage product."""
        try:
            record = request.env['anker.tracker.product'].sudo().create({
                'name': name,
                'emoji': emoji or '🥤',
                'manufacturer': manufacturer,
                'volume': float(volume),
                'is_alcoholic': bool(is_alcoholic),
                'crate_size': int(crate_size),
                'price_per_bottle': float(price_per_bottle or 0),
            })
            return {'status': 'success', 'id': record.id}
        except Exception as e:
            _logger.error("Anker Tracker add_product error: %s", e)
            return {'status': 'error', 'message': str(e)}

    @http.route('/anker_tracker/delete_item', type='jsonrpc', auth='user', methods=['POST'])
    def delete_item(self, model_type, item_id, **kwargs):
        """Archives or deletes an item."""
        try:
            item_id = int(item_id)
            if model_type == 'consumers':
                request.env['anker.tracker.consumer'].sudo().browse(item_id).write({'active': False})
            elif model_type == 'products':
                request.env['anker.tracker.product'].sudo().browse(item_id).write({'active': False})
            elif model_type == 'consumptions':
                request.env['anker.tracker.consumption'].sudo().browse(item_id).unlink()
            else:
                return {'status': 'error', 'message': 'Unknown model type'}
            return {'status': 'success'}
        except Exception as e:
            _logger.error("Anker Tracker delete_item error: %s", e)
            return {'status': 'error', 'message': str(e)}

    @http.route('/anker_tracker/bill_now', type='jsonrpc', auth='user', methods=['POST'])
    def bill_now(self, **kwargs):
        """Marks all unbilled consumption records as billed with purchase summary logging."""
        try:
            result = request.env['anker.tracker.consumption'].sudo().bill_now()
            return result
        except Exception as e:
            _logger.error("Anker Tracker bill_now error: %s", e)
            return {'status': 'error', 'message': str(e)}

    @http.route('/anker_tracker/get_purchase_summary', type='jsonrpc', auth='user', methods=['POST'])
    def get_purchase_summary(self, **kwargs):
        """Returns purchase summary with MwSt breakdown (read-only, does not bill)."""
        try:
            return request.env['anker.tracker.consumption'].sudo().generate_purchase_summary()
        except Exception as e:
            _logger.error("Anker Tracker get_purchase_summary error: %s", e)
            return {'error': str(e)}

    @http.route('/anker_tracker/health', type='http', auth='none', methods=['GET'], csrf=False)
    def health(self, **kwargs):
        """Lightweight health endpoint for Uptime Kuma / external monitoring.
        Returns JSON with status, product count, consumer count, and timestamp.
        No authentication required – read-only aggregate counts only.
        """
        import json
        from datetime import datetime
        try:
            product_count = request.env['anker.tracker.product'].sudo().search_count([('active', '=', True)])
            consumer_count = request.env['anker.tracker.consumer'].sudo().search_count([('active', '=', True)])
            unbilled_count = request.env['anker.tracker.consumption'].sudo().search_count([('billed', '=', False)])
            body = json.dumps({
                'status': 'ok',
                'products': product_count,
                'consumers': consumer_count,
                'unbilled': unbilled_count,
                'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            })
            return request.make_response(body, headers=[
                ('Content-Type', 'application/json'),
                ('Cache-Control', 'no-cache'),
            ])
        except Exception as e:
            _logger.error("Anker Tracker health check error: %s", e)
            body = json.dumps({'status': 'error', 'message': str(e)})
            return request.make_response(body, status=500, headers=[
                ('Content-Type', 'application/json'),
            ])

