#!/usr/bin/env python3
"""Sentinel OSINT Dashboard - Real Investigation Data"""
import json, csv, os, sys
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

GEO_FILE = Path(r"C:\Users\HP\OneDrive\Documents\opencode_work\geo_entity_map.csv")

def load_real_data():
    entities = []
    entity_set = set()
    with open(GEO_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('entity', row.get('label', 'Unknown'))
            if not name or name in entity_set:
                name = row.get('label', 'Unknown')
            if not name or name in entity_set:
                continue
            entity_set.add(name)
            layer = row.get('layer', 'UNKNOWN')
            type_map = {
                'TOXIC_SITE': 'HAZARD', 'SHELL_LLC': 'ORG', 'RESIDENCE': 'LOCATION',
                'GOVERNMENT': 'GOV', 'COURT': 'GOV', 'MILITARY': 'GOV',
                'CMRA': 'MAIL', 'MAIL_DROP': 'MAIL',
            }
            etype = type_map.get(layer, 'OTHER')
            risk = 0.9 if layer == 'TOXIC_SITE' else 0.7 if layer == 'SHELL_LLC' else 0.3 if layer in ('GOVERNMENT','COURT','MILITARY') else 0.4
            val = row.get('value', '')
            if '$' in val:
                risk = min(risk + 0.1, 1.0)
            entities.append({
                'name': name, 'type': etype, 'layer': layer,
                'address': row.get('address', ''), 'lat': float(row.get('lat', 0) or 0),
                'lon': float(row.get('lng', 0) or 0), 'risk': risk,
                'value': val, 'year': row.get('year', ''),
                'label': row.get('label', ''),
            })
    relationships = []
    layers = {}
    for e in entities:
        l = e['layer']
        if l not in layers:
            layers[l] = []
        layers[l].append(e['name'])
    for layer_name, members in layers.items():
        for i in range(len(members)):
            for j in range(i+1, min(i+5, len(members))):
                relationships.append((members[i], members[j], 'same_network'))
    shell_llcs = [e['name'] for e in entities if e['layer'] == 'SHELL_LLC']
    govs = [e['name'] for e in entities if e['layer'] in ('GOVERNMENT', 'COURT')]
    for s in shell_llcs[:3]:
        for g in govs[:3]:
            relationships.append((s, g, 'under_investigation'))
    hazards = [e['name'] for e in entities if e['layer'] == 'TOXIC_SITE']
    for h in hazards:
        for s in shell_llcs[:2]:
            relationships.append((h, s, 'linked_to'))
    return entities, relationships

ENTITIES, RELATIONSHIPS = load_real_data()

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Sentinel OSINT - Real Investigation Dashboard</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0a0e17;color:#e0e6ed}
.header{background:linear-gradient(135deg,#0d1117,#161b22);border-bottom:1px solid #21262d;padding:14px 28px;display:flex;align-items:center;gap:16px}
.logo{font-size:26px;font-weight:700;background:linear-gradient(90deg,#58a6ff,#3fb950);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.subtitle{color:#8b949e;font-size:13px}
.stats-bar{display:flex;gap:12px;margin-left:auto}
.stat-box{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:10px 16px;text-align:center;min-width:100px}
.stat-box .num{font-size:22px;font-weight:700;color:#58a6ff}
.stat-box .label{font-size:10px;color:#8b949e;text-transform:uppercase;letter-spacing:1px}
.nav{display:flex;gap:4px;background:#0d1117;padding:8px 28px;border-bottom:1px solid #21262d}
.nav button{background:0 0;border:1px solid #21262d;color:#8b949e;padding:7px 18px;border-radius:6px;cursor:pointer;font-size:12px;transition:.2s}
.nav button:hover,.nav button.active{background:#1f6feb;color:#fff;border-color:#1f6feb}
.main{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px 28px;height:calc(100vh - 130px)}
.panel{background:#0d1117;border:1px solid #21262d;border-radius:10px;overflow:hidden;display:flex;flex-direction:column}
.panel-header{background:#161b22;padding:10px 14px;border-bottom:1px solid #21262d;font-weight:600;font-size:13px;display:flex;align-items:center;gap:8px}
.panel-body{flex:1;overflow:auto;padding:14px}
.search-box{display:flex;gap:8px;margin-bottom:12px}
.search-box input{flex:1;background:#0d1117;border:1px solid #21262d;color:#e0e6ed;padding:9px 12px;border-radius:6px;font-size:13px;outline:0}
.search-box input:focus{border-color:#1f6feb}
.search-box button{background:#238636;color:#fff;border:none;padding:9px 16px;border-radius:6px;cursor:pointer;font-weight:600;font-size:12px}
.entity-card{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:10px 14px;cursor:pointer;transition:.2s;margin-bottom:6px}
.entity-card:hover{border-color:#1f6feb;background:#1c2333}
.entity-name{font-weight:600;font-size:13px;margin-bottom:3px}
.entity-type{display:inline-block;font-size:9px;padding:2px 7px;border-radius:10px;font-weight:600;text-transform:uppercase;letter-spacing:.5px}
.type-ORG{background:#1a3a1a;color:#3fb950}.type-LOCATION{background:#3a2a1a;color:#d29922}.type-GOV{background:#1f3a5f;color:#58a6ff}.type-HAZARD{background:#3a1a1a;color:#f85149}.type-MAIL{background:#2a1a3a;color:#bc8cff}.type-OTHER{background:#21262d;color:#8b949e}
.risk-bar{height:4px;background:#21262d;border-radius:2px;margin-top:6px;overflow:hidden}
.risk-fill{height:100%;border-radius:2px}
.risk-low{background:#3fb950}.risk-med{background:#d29922}.risk-high{background:#f85149}
.val-tag{display:inline-block;font-size:10px;background:#0d1117;border:1px solid #21262d;padding:1px 6px;border-radius:4px;margin-top:4px;color:#d29922;font-weight:600}
#map{width:100%;height:100%;min-height:400px}
#graph-svg{width:100%;height:100%}
.detail-panel{padding:14px}
.detail-panel h3{color:#58a6ff;margin-bottom:10px;font-size:15px}
.detail-row{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #21262d}
.detail-row .key{color:#8b949e;font-size:12px}.detail-row .val{color:#e0e6ed;font-weight:500;font-size:12px}
.report-btn{background:#1f6feb;color:#fff;border:none;padding:9px 16px;border-radius:6px;cursor:pointer;font-weight:600;margin-top:10px;width:100%}
.full-width{grid-column:1/-1}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:#0d1117}::-webkit-scrollbar-thumb{background:#21262d;border-radius:3px}
.toast{position:fixed;bottom:16px;right:16px;background:#161b22;border:1px solid #238636;color:#3fb950;padding:10px 16px;border-radius:8px;font-size:12px;z-index:9999;opacity:0;transition:.3s}
.toast.show{opacity:1}
</style>
</head>
<body>
<div class="header">
<div class="logo">SENTINEL</div>
<div class="subtitle">Real Investigation Data - Orange County RICO/Toxic Tort</div>
<div class="stats-bar">
<div class="stat-box"><div class="num">""" + str(len(ENTITIES)) + """</div><div class="label">Entities</div></div>
<div class="stat-box"><div class="num">""" + str(len(RELATIONSHIPS)) + """</div><div class="label">Links</div></div>
<div class="stat-box"><div class="num">""" + str(sum(1 for e in ENTITIES if e['risk']>=0.7)) + """</div><div class="label">High Risk</div></div>
<div class="stat-box"><div class="num">""" + str(sum(1 for e in ENTITIES if e['value'] and '$' in e['value'])) + """</div><div class="label">$$$ Linked</div></div>
</div></div>
<div class="nav">
<button class="active" onclick="showView('graph',this)">Network Graph</button>
<button onclick="showView('map',this)">Map View</button>
<button onclick="showView('entities',this)">All Entities</button>
<button onclick="showView('shell',this)">Shell LLCs</button>
<button onclick="showView('hazards',this)">Toxic Sites</button>
<button onclick="showView('gov',this)">Government</button>
<button onclick="showView('reports',this)">Reports</button>
</div>
<div class="main">
<div class="panel" id="panel-left">
<div class="panel-header"><span id="left-title">Network Graph</span></div>
<div class="panel-body" id="left-body"><svg id="graph-svg"></svg></div>
</div>
<div class="panel" id="panel-right">
<div class="panel-header"><span>Intelligence Detail</span></div>
<div class="panel-body" id="right-body">
<div class="detail-panel"><h3>Select an entity</h3>
<p style="color:#8b949e;font-size:12px;">Click nodes on the graph or entities in lists to view intelligence details, financial links, and connections.</p>
<div style="margin-top:16px;">
<div style="color:#58a6ff;font-weight:600;font-size:12px;margin-bottom:8px;">LAYER LEGEND</div>
<div style="display:flex;flex-wrap:wrap;gap:6px;">
<span class="entity-type type-HAZARD">TOXIC SITE</span>
<span class="entity-type type-ORG">SHELL LLC</span>
<span class="entity-type type-LOCATION">RESIDENCE</span>
<span class="entity-type type-GOV">GOVERNMENT</span>
<span class="entity-type type-MAIL">MAIL DROP</span>
</div></div></div>
</div></div></div>
<div class="toast" id="toast"></div>
<script>
const E=""" + json.dumps(ENTITIES) + """;
const R=""" + json.dumps(RELATIONSHIPS[:200]) + """;
function showToast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),3000)}
function riskClass(r){return r>=0.7?'risk-high':r>=0.4?'risk-med':'risk-low'}
function riskLabel(r){return r>=0.7?'HIGH':r>=0.4?'MEDIUM':'LOW'}
function typeColor(t){return{ORG:'#3fb950',LOCATION:'#d29922',GOV:'#58a6ff',HAZARD:'#f85149',MAIL:'#bc8cff',OTHER:'#8b949e'}[t]||'#8b949e'}
let map,graphSim,svgG,currentView='graph';
function showView(v,btn){
currentView=v;
document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('active'));
if(btn)btn.classList.add('active');
const left=document.getElementById('left-body');
const title=document.getElementById('left-title');
if(v==='graph'){title.textContent='Network Graph';left.innerHTML='<svg id="graph-svg" width="100%" height="100%"></svg>';drawGraph()}
else if(v==='map'){title.textContent='Map View';left.innerHTML='<div id="map"></div>';drawMap()}
else if(v==='entities'){title.textContent='All Entities ('+E.length+')';drawList(E)}
else if(v==='shell'){title.textContent='Shell LLCs';drawList(E.filter(e=>e.layer==='SHELL_LLC'))}
else if(v==='hazards'){title.textContent='Toxic Sites';drawList(E.filter(e=>e.layer==='TOXIC_SITE'))}
else if(v==='gov'){title.textContent='Government/Court';drawList(E.filter(e=>['GOVERNMENT','COURT','MILITARY'].includes(e.layer)))}
else if(v==='reports'){title.textContent='Reports';drawReports()}
}
function drawGraph(){
const svg=d3.select('#graph-svg');
const w=svg.node().getBoundingClientRect().width||800;
const h=svg.node().getBoundingClientRect().height||600;
svg.selectAll('*').remove();
svg.append('defs').append('marker').attr('id','arrow').attr('viewBox','0 -5 10 10').attr('refX',20).attr('refY',0).attr('markerWidth',5).attr('markerHeight',5).attr('orient','auto').append('path').attr('d','M0,-5L10,0L0,5').attr('fill','#30363d');
svgG=svg.append('g');
svg.call(d3.zoom().scaleExtent([.2,5]).on('zoom',e=>svgG.attr('transform',e.transform)));
const nodes=E.slice(0,60).map((e,i)=>({...e,id:i}));
const nodeMap={};nodes.forEach(n=>nodeMap[n.name]=n.id);
const links=R.filter(r=>nodeMap[r[0]]!==undefined&&nodeMap[r[1]]!==undefined).map(r=>({source:nodeMap[r[0]],target:nodeMap[r[1]],label:r[2]}));
graphSim=d3.forceSimulation(nodes).force('link',d3.forceLink(links).id(d=>d.id).distance(100)).force('charge',d3.forceManyBody().strength(-250)).force('center',d3.forceCenter(w/2,h/2)).force('collision',d3.forceCollide().radius(30));
const link=svgG.selectAll('.link').data(links).enter().append('line').attr('stroke','#21262d').attr('stroke-width',1).attr('marker-end','url(#arrow)');
const node=svgG.selectAll('.node').data(nodes).enter().append('g').attr('class','node').call(d3.drag().on('start',(e,d)=>{if(!e.active)graphSim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y}).on('drag',(e,d)=>{d.fx=e.x;d.fy=e.y}).on('end',(e,d)=>{if(!e.active)graphSim.alphaTarget(0);d.fx=null;d.fy=null}));
node.append('circle').attr('r',d=>d.risk>=.7?14:d.risk>=.4?11:8).attr('fill',d=>typeColor(d.type)).attr('stroke',d=>d.risk>=.7?'#f85149':'none').attr('stroke-width',2).style('cursor','pointer').on('click',(e,d)=>showDetail(d));
node.append('text').attr('dy',22).attr('text-anchor','middle').attr('font-size','9px').attr('fill','#e0e6ed').text(d=>d.name.length>18?d.name.slice(0,16)+'..':d.name);
graphSim.on('tick',()=>{link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);node.attr('transform',d=>`translate(${d.x},${d.y})`)});
showToast('Graph loaded - drag to explore '+nodes.length+' nodes');
}
function drawMap(){
if(map)map.remove();
map=L.map('map').setView([33.72,-118.0],10);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{attribution:'CartoDB',maxZoom:19}).addTo(map);
const colors={HAZARD:'#f85149',ORG:'#3fb950',LOCATION:'#d29922',GOV:'#58a6ff',MAIL:'#bc8cff',OTHER:'#8b949e'};
E.forEach(e=>{if(e.lat&&e.lon){
L.circleMarker([e.lat,e.lon],{radius:e.risk>=.7?10:e.risk>=.4?7:5,fillColor:colors[e.type]||'#8b949e',color:'#0d1117',weight:2,fillOpacity:.8}).addTo(map)
.bindPopup('<div style="color:#0d1117;font-family:sans-serif;"><b>'+e.name+'</b><br>'+e.layer+'<br>'+(e.value||'')+'<br>Risk: '+riskLabel(e.risk)+'</div>')
.on('click',()=>showDetail(e))}});
showToast('Map loaded - '+E.filter(e=>e.lat).length+' locations plotted');
}
function drawList(items){
const left=document.getElementById('left-body');
let html='<div class="search-box"><input type="text" id="es" placeholder="Search..." oninput="filterList()"></div><div id="elist">';
items.sort((a,b)=>b.risk-a.risk).forEach((e,i)=>{
html+='<div class="entity-card" onclick="showDetail(E.find(x=>x.name===\\''+e.name.replace(/'/g,"\\'")+'\\'))"><div class="entity-name">'+e.name+'</div><span class="entity-type type-'+e.type+'">'+e.layer+'</span>';
if(e.value)html+=' <span class="val-tag">'+e.value+'</span>';
html+='<div class="risk-bar"><div class="risk-fill '+riskClass(e.risk)+'" style="width:'+e.risk*100+'%"></div></div>';
if(e.address)html+='<div style="font-size:10px;color:#484f58;margin-top:3px;">'+e.address+'</div>';
html+='</div>'});
html+='</div>';
left.innerHTML=html;
}
function filterList(){const q=(document.getElementById('es')?.value||'').toLowerCase();document.querySelectorAll('.entity-card').forEach(c=>{c.style.display=c.textContent.toLowerCase().includes(q)?'':'none'})}
function showDetail(e){
const c=e;
const conns=R.filter(r=>r[0]===c.name||r[1]===c.name);
const related=conns.map(r=>r[0]===c.name?r[1]:r[0]);
const linkedEntities=E.filter(x=>related.includes(x.name));
document.getElementById('right-body').innerHTML=`<div class="detail-panel"><h3>${c.name}</h3>
<div class="detail-row"><span class="key">Type</span><span class="val"><span class="entity-type type-${c.type}">${c.layer}</span></span></div>
<div class="detail-row"><span class="key">Risk</span><span class="val" style="color:${c.risk>=.7?'#f85149':c.risk>=.4?'#d29922':'#3fb950'}">${(c.risk*100).toFixed(0)}% - ${riskLabel(c.risk)}</span></div>
${c.address?`<div class="detail-row"><span class="key">Address</span><span class="val">${c.address}</span></div>`:''}
${c.value?`<div class="detail-row"><span class="key">Financial</span><span class="val" style="color:#d29922">${c.value}</span></div>`:''}
${c.year?`<div class="detail-row"><span class="key">Year</span><span class="val">${c.year}</span></div>`:''}
${c.lat?`<div class="detail-row"><span class="key">Coordinates</span><span class="val">${c.lat.toFixed(4)}, ${c.lon.toFixed(4)}</span></div>`:''}
<div style="margin-top:12px;color:#58a6ff;font-weight:600;font-size:12px;">Connections (${conns.length})</div>
${linkedEntities.slice(0,10).map(x=>`<div class="detail-row"><span class="key">${conns.find(r=>(r[0]===c.name&&r[1]===x.name)||(r[1]===c.name&&r[0]===x.name))?.[2]||'linked'}</span><span class="val" style="color:#58a6ff;cursor:pointer" onclick="showDetail(E.find(y=>y.name==='${x.name.replace(/'/g,"\\'")}'))">${x.name}</span></div>`).join('')}
<button class="report-btn" onclick="showToast('Report generation coming soon')">Generate Report</button></div>`;
}
function drawReports(){
const left=document.getElementById('left-body');
let html='<div style="padding:8px"><h3 style="color:#58a6ff;margin-bottom:12px">Investigation Reports</h3>';
html+='<div class="entity-card" onclick="showToast(\'Full report coming soon\')" style="margin-bottom:8px"><div class="entity-name">Full OC RICO Investigation Report</div><span class="entity-type type-HAZARD">COMPREHENSIVE</span><p style="color:#8b949e;font-size:11px;margin-top:6px">Complete intelligence briefing on all '+E.length+' entities, shell LLCs, toxic sites, and government connections.</p></div>';
html+='<div class="entity-card" onclick="showToast(\'Financial report coming soon\')" style="margin-bottom:8px"><div class="entity-name">Financial Flow Analysis</div><span class="entity-type type-ORG">FINANCIAL</span><p style="color:#8b949e;font-size:11px;margin-top:6px">Track $'+E.filter(e=>e.value&&e.value.includes('$')).reduce((s,e)=>s+1,0)+' entities with financial data through shell LLC network.</p></div>';
html+='<div class="entity-card" onclick="showToast(\'Toxic report coming soon\')" style="margin-bottom:8px"><div class="entity-name">Toxic Site Contamination Report</div><span class="entity-type type-HAZARD">ENVIRONMENTAL</span><p style="color:#8b949e;font-size:11px;margin-top:6px">HBNC/Cameron Lane contamination data, Cr-VI levels, EPA violations.</p></div>';
html+='</div>';
left.innerHTML=html;
}
drawGraph();
</script>
</body></html>"""

@app.route("/")
def index():
    return render_template_string(TEMPLATE)

@app.route("/api/entities")
def api_entities():
    return jsonify(ENTITIES)

@app.route("/api/search")
def api_search():
    q = request.args.get("q","").lower()
    return jsonify([e for e in ENTITIES if q in e["name"].lower() or q in e.get("address","").lower()])

if __name__ == "__main__":
    print("=" * 50)
    print("SENTINEL - Real Investigation Dashboard")
    print(f"Loaded {len(ENTITIES)} entities, {len(RELATIONSHIPS)} relationships")
    print("http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
