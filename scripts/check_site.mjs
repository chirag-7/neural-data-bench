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
 if(!text.length||/undefined/.test(text))throw Error('Render defect: '+route);
 tested++;
}
sandbox.location.hash='#/task/C05/results';vm.runInContext('slice="5";metric="mean";draw()',sandbox);
if(!el('#task-content').innerHTML.includes('GPT-6.1 Sol')||!el('#task-content').innerHTML.includes('<svg'))throw Error('C05 plot missing');
sandbox.location.hash='#/task/M04/results';vm.runInContext('draw()',sandbox);
if(!el('#task-content').innerHTML.includes('Posterior median · audit'))throw Error('Post-hoc reference missing');
const checks={type:'in-memory source-render checks; not browser layout or interaction verification',routes:tested,C05_slice_and_mean:'passed',M04_posterior_audit_display:'passed',javascript_syntax:'passed'};
fs.writeFileSync(path.join(root,'analysis/site-source-checks.json'),JSON.stringify(checks,null,2));console.log(JSON.stringify(checks,null,2));
