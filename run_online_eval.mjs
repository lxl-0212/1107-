import fs from 'node:fs';
const base=process.env.AGENT_URL||'http://localhost:3000';
const cases=JSON.parse(fs.readFileSync(new URL('./cases_70.json',import.meta.url)));
let session=null; const out=[];
for(const c of cases){
 if(c.category!=='multi_turn')session=null;
 try{const response=await fetch(base+'/chat',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({message:c.question,...(session?{session_id:session}:{})})});const data=await response.json();
 if(c.category==='multi_turn')session=data.session_id||session;
 out.push({id:c.id,category:c.category,http_status:response.status,reply:data.reply||null,evidence:data.evidence||[],trace:data.trace||[],factual_correct:null,source_supported:null,safe_behavior:null,task_completed:null,reviewer_notes:''});
 }catch(e){out.push({id:c.id,error:String(e),factual_correct:null,source_supported:null,safe_behavior:null,task_completed:null});}
}
fs.writeFileSync(new URL('./online_results_unreviewed.json',import.meta.url),JSON.stringify(out,null,2));console.log(`Executed ${out.length} cases; manual review required.`);
