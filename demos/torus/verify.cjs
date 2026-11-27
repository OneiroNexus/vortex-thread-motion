/* Execute the final HTML's inline script against an in-memory DOM contract. */
const {readFileSync}=require('node:fs'), path=require('node:path');
const {strict:assert}=require('node:assert'), vm=require('node:vm');
const html=readFileSync(path.join(__dirname,'index.html'),'utf8');
const script=html.match(/<script>\n([\s\S]*?)<\/script>/)[1];
const json=html.match(/<script type="application\/json" id="trace">([\s\S]*?)<\/script>/)[1];
const raw=JSON.parse(json);
assert.equal(raw.frames.length,60);
assert.deepEqual(raw.frames.map(f=>f.index).filter((_,i)=>i===0||i===59),[0,239]);
assert.deepEqual(raw,JSON.parse(readFileSync(path.join(__dirname,'trace.json'),'utf8')));
assert(!/<(?:script|img|link) [^>]*(?:src|href)=["']https?:/i.test(html));
class Element {
  constructor(tag,textContent=''){this.tag=tag;this.textContent=textContent;this.attrs={};this.style={};this.children=[];this.events={};}
  append(...els){this.children.push(...els);}
  setAttribute(k,v){this.attrs[k]=v;}
  addEventListener(k,v){this.events[k]=v;}
  fire(k){this.events[k]();}
  tree(){return [this,...this.children.flatMap(c=>c instanceof Element?c.tree():[])];}
  toSVG(){
    const e=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
    const a=Object.entries(this.attrs).map(([k,v])=>` ${k}="${e(v)}"`).join('');
    return `<${this.tag}${a}>${e(this.textContent)}${this.children.map(c=>c instanceof Element?c.toSVG():e(c)).join('')}</${this.tag}>`;
  }
}
function boot(content){
 const nodes={trace:new Element('script',content),error:new Element('p'),side:new Element('g'),end:new Element('g'),legend:new Element('div'),prev:new Element('button'),play:new Element('button'),next:new Element('button'),scrub:new Element('input'),readout:new Element('output')};
 const doc=new Element('document');
 doc.getElementById=id=>nodes[id];
 doc.createElementNS=(_ns,tag)=>new Element(tag);
 doc.createElement=tag=>new Element(tag);
 doc.createTextNode=t=>t;
 let tick=null;
 vm.runInNewContext(script,{document:doc,setInterval:fn=>{tick=fn;return 1;},clearInterval:()=>{tick=null;}});
 return {nodes,doc,get tick(){return tick;}};
}
const test=boot(json),{nodes}=test;
assert.equal(nodes.legend.children.length,3);
function curves(id){return nodes[id].tree().filter(e=>'data-thread'in e.attrs);}
assert(curves('side').length===3&&curves('end').length===3);
let bound=0;for(const f of raw.frames)for(const t of f.tracks)for(const p of t)bound=Math.max(bound,...p.map(Math.abs));
const scale=143/bound;
function check(pos) {
 const f=raw.frames[pos];
 assert.equal(Number(nodes.scrub.value),pos);
 assert.match(nodes.readout.textContent,new RegExp('Frame '+f.index+' ·'));
 for(const [plate,axis] of [['side',2],['end',1]]) {
  for(const [thread,curve] of curves(plate).entries()) {
   assert.equal(curve.attrs.d,f.tracks[thread].map((p,i)=>`${i?'L':'M'}${(260+p[0]*scale).toFixed(3)} ${(175-p[axis]*scale).toFixed(3)}`).join(' '));
  }
 }
 assert(curves('side')[0].attrs.d!==curves('end')[0].attrs.d);
}
check(47);
nodes.scrub.value='0';nodes.scrub.fire('input');check(0);
assert(nodes.prev.disabled);
nodes.next.fire('click');check(1);
nodes.play.fire('click');test.tick();check(2);
nodes.scrub.value='59';nodes.scrub.fire('input');check(59);
assert.equal(test.tick,null);
assert(nodes.next.disabled);
nodes.play.fire('click');check(0);
for(let n=1;n<=59;n++)test.tick();
check(59);assert.equal(test.tick,null);
assert(!boot('invalid JSON').nodes.side.children.length);
assert(boot('{}').nodes.play.disabled);
nodes.scrub.value='47';nodes.scrub.fire('input');check(47);
const preview=`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="595" viewBox="0 0 1200 595">
<rect width="1200" height="595" fill="#ece5ce"/><path d="M50 29H1150" stroke="#20271e" stroke-width="5"/>
<text x="50" y="56" font-family="monospace" font-weight="bold" font-size="15" letter-spacing="2" fill="#36513a">FIELD SHEET 01 / VORTEX THREADS</text>
<text x="47" y="124" font-family="serif" font-weight="bold" font-size="70" fill="#20271e">Juicy <tspan font-style="italic" fill="#a43729">Donut</tspan> Lab</text>
<rect x="861" y="81" width="289" height="45" fill="#36513a"/><text x="1005" y="109" text-anchor="middle" font-family="monospace" font-size="16" fill="#fffaf0">SCRIPTED GEOMETRY</text>
<rect x="50" y="149" width="1100" height="394" fill="#f7f0d9" stroke="#20271e"/><path d="M600 149V543" stroke="#20271e"/>
<g font-family="serif" font-size="25" font-weight="bold" fill="#20271e"><text x="80" y="185">Side · x/z</text><text x="630" y="185">End-on · x/y</text></g>
<g transform="translate(65 194)">${nodes.side.toSVG()}</g><g transform="translate(615 194)">${nodes.end.toSVG()}</g>
<text x="50" y="573" font-family="monospace" font-size="15" fill="#495142">Frame ${raw.frames[47].index} · Same recorded frame and scale · Dimensionless · Not a fluid simulation</text></svg>`;
assert(preview.startsWith('<svg ')); // Generated preview stays in memory; this verifier writes no files.
console.log('Verified data equality, both axis projections on asymmetric real geometry, all three thread paths, scrub/step, play to end, boundary controls, and malformed-data rejection.');
