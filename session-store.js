// In-memory sessions are intentionally short-lived; production multi-instance deployments need Redis.
const sessions=new Map();
const TTL=30*60*1000,MAX=1000;
export function session(id){
 const now=Date.now();for(const [k,v] of sessions)if(now-v.updated>TTL)sessions.delete(k);
 if(sessions.size>MAX)sessions.delete(sessions.keys().next().value);
 const s=sessions.get(id)||{history:[],updated:now};s.updated=now;sessions.set(id,s);return s;
}
export function clearSession(id){sessions.delete(id)}
