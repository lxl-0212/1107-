import 'dotenv/config';
import express from 'express';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import fs from 'node:fs';
import {MCPClient} from './mcp-client.js';
import {CampusAgent,newId,sanitizeLog} from './agent.js';
import {session,clearSession} from './session-store.js';
const app=express();
app.disable('x-powered-by');
app.use(express.json({limit:'32kb'}));
const ROOT=path.dirname(fileURLToPath(import.meta.url));
const homepage=path.join(ROOT,'index.html');
app.get('/',(req,res)=>{
 if(!fs.existsSync(homepage))return res.status(503).type('text/plain').send('Homepage missing: expected index.html');
 res.sendFile(homepage);
});
console.log('[HOMEPAGE]',homepage||'MISSING', 'cwd=',process.cwd());
const mcp=new MCPClient();const agent=new CampusAgent(mcp);let mcpError=null;
const traceStore=new Map();const MAX_TRACES=300;
app.get('/healthz',(_,res)=>res.json({ok:true,mcpReady:mcp.ready,mcpTools:mcp.tools.map(t=>t.name),openaiConfigured:!!process.env.OPENAI_API_KEY,mcpError}));
app.post('/chat',async(req,res)=>{
 const id=typeof req.body?.session_id==='string'&&/^[a-zA-Z0-9-]{8,80}$/.test(req.body.session_id)?req.body.session_id:newId();
 const text=String(req.body?.message||req.body?.messages?.filter(x=>x?.role==='user').at(-1)?.content||'').trim();
 if(!text||text.length>1500)return res.status(400).json({error:'message 必須為 1–1500 字'});
 const s=session(id);s.history.push({role:'user',content:text});s.history=s.history.slice(-12);
 const request_id=newId();const trace=[{step:'start',request_id,at:new Date().toISOString()}];const started=Date.now();
 try{
  const out=await agent.run(s.history,trace);
  s.history.push({role:'assistant',content:out.reply});s.history=s.history.slice(-12);
  trace.push({step:'finish',status:out.status,total_ms:Date.now()-started});
  traceStore.set(request_id,trace);if(traceStore.size>MAX_TRACES)traceStore.delete(traceStore.keys().next().value);
  console.log('[AGENT_TRACE]',sanitizeLog(trace));
  res.json({reply:out.reply,session_id:id,request_id,status:out.status,evidence:out.evidence.slice(0,12),trace});
 }catch(err){
  s.history.pop();trace.push({step:'error',status:err.status||500,error:String(err.message).slice(0,120)});
  console.error('[AGENT_ERROR]',sanitizeLog(trace));
  const status=err.status===503?503:502;
  res.status(status).json({error:status===503?'服務尚未就緒，請稍後再試':'上游查詢失敗，請稍後重試',request_id,session_id:id});
 }
});
app.delete('/session/:id',(req,res)=>{clearSession(req.params.id);res.json({ok:true})});
// Trace endpoint disabled by default: logs may contain operational metadata.
if(process.env.ENABLE_TRACE_ENDPOINT==='true'&&process.env.ADMIN_TRACE_TOKEN){
 app.get('/admin/trace/:id',(req,res)=>{if(req.get('x-admin-token')!==process.env.ADMIN_TRACE_TOKEN)return res.sendStatus(403);res.json(traceStore.get(req.params.id)||[])});
}
const port=Number(process.env.PORT||3000);app.listen(port,()=>console.log(`Campus Agent V4 FLAT listening on ${port}`));
async function startMcp(){try{await mcp.connect();mcpError=null}catch(e){mcpError=e.message;console.error('[MCP_STARTUP]',e.message);setTimeout(startMcp,10000).unref()}}
startMcp();
