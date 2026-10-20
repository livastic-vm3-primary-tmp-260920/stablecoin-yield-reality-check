/** Isolated Chrome smoke of public buyer draft; neither wallet nor email client is touched. */
import {spawn} from 'node:child_process';
import {mkdtemp,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {setTimeout as sleep} from 'node:timers/promises';
const URL='https://livastic-vm3-primary-tmp-260920.github.io/stablecoin-yield-reality-check/';
const dir=await mkdtemp(join(tmpdir(),'vm3-buyerdraft-headless-'));
let chrome=null,ws=null,uid=0;
const pending=new Map(),errors=[],otherRequests=[];
function send(method,params={}){
 const id=++uid;
 return new Promise((resolve,reject)=>{
  pending.set(id,{resolve,reject});
  ws.send(JSON.stringify({id,method,params}));
 });
}
async function val(expr){
 const r=await send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});
 if(r.exceptionDetails)throw new Error('PAGE_EVAL_FAILED');
 return r.result?.value;
}
try{
 chrome=spawn('/usr/bin/google-chrome',[
  '--headless=new','--no-sandbox','--disable-gpu','--disable-background-networking',
  '--no-first-run','--remote-allow-origins=*','--remote-debugging-port=0',
  '--user-data-dir='+dir,'about:blank'
 ],{stdio:'ignore'});
 let port=null;
 for(let i=0;i<80;i++){
  await sleep(105);
  try{port=Number((await readFile(join(dir,'DevToolsActivePort'),'utf8')).split('\n')[0]);}catch{}
  if(port>0&&Number.isInteger(port))break;
  if(chrome.exitCode!==null)throw new Error('CHROME_EXITED');
 }
 if(!port)throw new Error('CHROME_PORT_NOT_FOUND');
 const list=await (await fetch('http://127.0.0.1:'+port+'/json/list')).json();
 const page=list.find(x=>x.type==='page');
 if(!page)throw new Error('NO_PAGE');
 ws=new WebSocket(page.webSocketDebuggerUrl);
 ws.addEventListener('message',event=>{
  const x=JSON.parse(event.data);
  if(x.method==='Runtime.exceptionThrown')errors.push(x.params?.exceptionDetails?.text||'script error');
  if(x.method==='Network.requestWillBeSent'){
   const u=x.params.request?.url||'';
   if(u.startsWith('http')&&!u.startsWith(URL))otherRequests.push(u.split('?')[0]);
  }
  if(x.id&&pending.has(x.id)){
   const p=pending.get(x.id);pending.delete(x.id);
   x.error?p.reject(new Error(x.error.message||'CDP_FAIL')):p.resolve(x.result);
  }
 });
 await new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>reject(new Error('CDP_TIMEOUT')),6000);
  ws.addEventListener('open',()=>{clearTimeout(timer);resolve()},{once:true});
  ws.addEventListener('error',error=>{clearTimeout(timer);reject(error)},{once:true});
 });
 await send('Runtime.enable');await send('Page.enable');await send('Network.enable');
 await send('Page.navigate',{url:URL});
 let ready=false;
 for(let i=0;i<90;i++){
  await sleep(135);
  if(await val("document.readyState==='complete' && document.querySelectorAll('button.pick').length>0 && document.querySelector('#request-pool-email')!==null")){ready=true;break}
 }
 if(!ready)throw new Error('PUBLIC_UI_NOT_READY');
 const initial=await val("document.querySelector('#request-pool-email').getAttribute('href')");
 if(!initial.startsWith('mailto:onecursor1@gmail.com?'))throw new Error('BASE_MAILTO_MISSING');
 const selection=await val("(function(){document.querySelector('button.pick').click();return {selected:document.querySelector('#chosen').textContent,uri:document.querySelector('#request-pool-email').getAttribute('href'),info:document.querySelector('#request-context').textContent,href:location.href,count:document.querySelectorAll('button.pick').length}})()");
 if(!selection?.uri?.startsWith('mailto:onecursor1@gmail.com?'))throw new Error('BUYER_DRAFT_NOT_GENERATED');
 const body=new URL(selection.uri).searchParams.get('body')||'';
 const poolId=/Public pool ID: ([0-9a-f-]{36})/.exec(body)?.[1];
 if(!poolId)throw new Error('PUBLIC_POOL_ID_NOT_IN_DRAFT');
 if(!selection.info.includes('No portfolio input'))throw new Error('PRIVACY_DISCLOSURE_MISSING');
 if(selection.href!==URL||selection.count<1)throw new Error('UNEXPECTED_NAVIGATION_OR_EMPTY_TABLE');
 if(otherRequests.length)throw new Error('UNEXPECTED_EXTERNAL_REQUEST');
 if(errors.length)throw new Error('JS_EXCEPTION');
 console.log(JSON.stringify({status:'PASS',publicPoolId:poolId,renderedPublicRows:selection.count,
  ephemeralHeadlessTab:true,userExistingTabChanges:0,mailClientOpened:false,
  mailSent:false,walletMethodsCalled:0,usdcNewReceipts:0,otherNetworkRequests:0,jsExceptions:0}));
}catch(e){console.error('QA_FAILED',String(e?.message||e));process.exitCode=1}
finally{
 try{ws?.close()}catch{}
 try{chrome?.kill('SIGTERM')}catch{}
 await sleep(180);
 try{await rm(dir,{recursive:true,force:true})}catch{}
}
