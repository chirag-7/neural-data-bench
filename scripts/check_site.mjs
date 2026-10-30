// Source-level render checks in an in-memory DOM stub, not browser interaction/layout QA.
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const elements=new Map();
const el=s=>{if(!elements.has(s))elements.set(s,{innerHTML:'',value:'',classList:{toggle(){}},dataset:{}});return elements.get(s)};
const sandbox={document:{querySelector:el,querySelectorAll:()=>[]},location:{hash:'#/'},window:{addEventListener(){},scrollTo(){}},console,fetch:async p=>({json:async()=>JSON.parse(fs.readFileSync(path.join(root,'website',p),'utf8')),text:async()=>fs.readFileSync(path.join(root,'website',p),'utf8')})};
vm.createContext(sandbox);vm.runInContext(fs.readFileSync(path.join(root,'website/app.js'),'utf8'),sandbox);await new Promise(resolve=>setImmediate(resolve));
const catalog=JSON.parse(fs.readFileSync(path.join(root,'registry/catalog.json'),'utf8'));
let tested=0;
for(const route of ['','trends','methods',...catalog.families.map(f=>'family/'+f.code),...catalog.entries.flatMap(e=>['overview','results','procedure','sources'].map(t=>'task/'+e.id+'/'+t))]){
 sandbox.location.hash='#/'+route;vm.runInContext('draw()',sandbox);const text=el('#app').innerHTML+el('#task-content').innerHTML;
 if(!text.length||/>undefined</.test(text))throw Error('Render defect: '+route);
 tested++;
}
sandbox.location.hash='#/task/C05/results';vm.runInContext('slice="5";draw()',sandbox);
if(!el('#task-content').innerHTML.includes('GPT-6.1 Sol')||!el('#task-content').innerHTML.includes('<svg'))throw Error('C05 plot missing');
sandbox.location.hash='#/task/M04/results';vm.runInContext('draw()',sandbox);
if(!el('#task-content').innerHTML.includes('Posterior median · audit'))throw Error('Post-hoc reference missing');
for(const tab of ['references','progress','native']){vm.runInContext(`trendTab="${tab}";trends()`,sandbox);if(!el('#trend-content').innerHTML.length)throw Error('Empty trend view:'+tab);}
for(const c of ['conventional_baseline','historical_specialist','synthetic_objective_mismatched','deterministic_correctness'])vm.runInContext(`trendTab="references";referenceClass="${c}";trends()`,sandbox);
const measured=JSON.parse(fs.readFileSync(path.join(root,'analysis/summary.json'),'utf8')).measured_task_ids;
for(const id of measured){vm.runInContext(`trendTab="native";trendTask="${id}";trends()`,sandbox);if(!el('#native-trend').innerHTML.includes('<svg'))throw Error('Native charts missing:'+id);}
vm.runInContext('metric="score";bars([{model:"fixture",score:-.2},{model:"fixture2",score:.3}],"higher")',sandbox);
const checks={type:'in-memory source-render checks; not browser layout or interaction verification',routes:tested,C05_five_slices:'passed',trend_tabs_and_reference_filters:'passed',native_task_charts:measured.length,M04_posterior_audit_display:'passed',javascript_syntax:'passed',browser_layout_interaction:'Unverified: prior local-preview navigation blocked by browser URL policy; source checks do not replace browser QA'};
fs.writeFileSync(path.join(root,'analysis/site-source-checks.json'),JSON.stringify(checks,null,2));console.log(JSON.stringify(checks,null,2));
