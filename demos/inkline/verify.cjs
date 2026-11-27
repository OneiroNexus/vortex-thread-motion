'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync(__dirname+'/index.html','utf8');
const blocks=[...html.matchAll(/<script id="[^"]+">([\s\S]*?)<\/script>/g)].map(m=>m[1]);
assert.equal(blocks.length,2);
assert.equal(/<(script|link|img)[^>]+(?:src|href)\s*=/i.test(html),false);
class El{constructor(value=''){this.value=value;this.attrs={};this.children=[];this.events={};}setAttribute(k,v){this.attrs[k]=String(v);}append(e){this.children.push(e);}addEventListener(k,f){this.events[k]=f;}get valueAsNumber(){return this.value===''?NaN:+this.value;}}
const elems=Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(m=>[m[1],new El()]));
Object.assign(elems.time,{value:'1.25'});Object.assign(elems.visc,{value:'.12'});elems.sx.value='1.06';elems.sy.value='1.20';
Object.assign(elems.chart,{getScreenCTM:()=>({inverse:()=>0}),createSVGPoint:()=>({matrixTransform(){return this;}})});
let id=0;const jobs=new Map(),doc=new El();
doc.getElementById=id=>elems[id];doc.createElementNS=()=>new El();
const sandbox={document:doc,requestAnimationFrame:f=>{jobs.set(++id,f);return id;},cancelAnimationFrame:i=>jobs.delete(i)};
const ctx=vm.createContext(sandbox);
vm.runInContext(blocks.join('\n'),ctx);
const {velocity,kinematicPressure,pathline,projection,arrow}=vm.runInContext('({velocity,kinematicPressure,pathline,projection,arrow})',ctx);
const d=(f,h)=> (f(h)-f(-h))/(2*h), d2=(f,h)=>(f(h)+f(-h)-2*f(0))/(h*h);
let div=0,residual=0;
for(const x of [.31,1.71,3.15,5.21])for(const y of [.51,2,3.52,5.61])for(const t of [0,.4,2.])for(const n of [0,.12,.45]){
 const [u,v]=velocity(x,y,t,n);
 const grad=c=>[d(e=>velocity(x+e,y,t,n)[c],1e-5),d(e=>velocity(x,y+e,t,n)[c],1e-5)];
 const gu=grad(0),gv=grad(1);
 div=Math.max(div,Math.abs(gu[0]+gv[1]));
 for(let c=0;c<2;c++){
  const g=c?gv:gu;
  const f=e=>velocity(x+e,y,t,n)[c],j=e=>velocity(x,y+e,t,n)[c];
  const px=d(e=>kinematicPressure(x+(c?0:e),y+(c?e:0),t,n),1e-5);
  const rt=d(e=>velocity(x,y,t+e,n)[c],1e-5)+u*g[0]+v*g[1]+px-n*(d2(f,.001)+d2(j,.001));
  residual=Math.max(residual,Math.abs(rt));
 }
}
assert.ok(div<1e-9);assert.ok(residual<1e-6);
const near=(a,b,tol=1e-7)=>assert.ok(Math.abs(a-b)<tol,`${a} vs ${b}`);
near(velocity(0,Math.PI/2,0,.12)[0],1);
near(velocity(0,Math.PI/2,1,.12)[0],Math.exp(-.24));
near(velocity(Math.PI/2,0,0,.12)[1],-1);
near(projection(0,0)[1],438);near(projection(0,Math.PI*2)[1],10);
assert.match(arrow(5,5,0,1,23),/^M5.00 5.00L5.00 -18.00/);
for(const t of [0,1.25,8]){
 const a=pathline(1.06,1.2,t,.12).at(-1),b=pathline(1.06,1.2,t,.12,.005).at(-1);
 near(a[0],b[0]);near(a[1],b[1]);
 near(Math.cos(a[0])*Math.cos(a[1]),Math.cos(1.06)*Math.cos(1.2));
}
assert.equal(elems.field.children.length,225);
const old=elems.field.children.map(e=>e.attrs.d);
elems.time.value='4';elems.time.events.input();assert.equal(elems.tVal.textContent,'4.000');
assert.notDeepEqual(elems.field.children.map(e=>e.attrs.d),old);
elems.visc.value='.45';elems.visc.events.input();assert.match(elems.numbers.textContent,/Field scale  0.027/);
elems.chart.events.click({clientX:155,clientY:117});
near(+elems.sx.value,Math.PI/2,1e-6);near(+elems.sy.value,3*Math.PI/2,1e-6);
elems.sx.value='3';elems.sx.events.change();near(+elems.sx.value,3);
elems.play.events.click();assert.equal(elems.play.textContent,'Pause');
const next=ms=>{const [k,cb]=jobs.entries().next().value;jobs.delete(k);cb(ms);};
next(0);next(50);assert.equal(+elems.time.value,4.05);
doc.hidden=true;doc.events.visibilitychange();assert.equal(jobs.size,0);
elems.reset.events.click();assert.equal(+elems.time.value,0);assert.ok(!elems.trail.attrs.d.includes('L'));
elems.time.value='8';elems.time.events.input();elems.play.events.click();assert.equal(+elems.time.value,0);
console.log({arrows:225,modelCases:144,maximumDivergence:div,maximumMomentumResidual:residual,probeAndUi:'pass'});
