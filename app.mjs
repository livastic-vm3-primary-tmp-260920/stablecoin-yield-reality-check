/** Public metadata screener. No third-party network calls, keys, cookies, analytics or wallet. */
export function finite(v){return typeof v==='number' && Number.isFinite(v)?v:null;}
export function illustrative(principal,days,costs,baseApyPct,headlineApyPct){
 const v=[principal,days,costs,baseApyPct,headlineApyPct].map(finite);
 if(v.some(x=>x===null))return null;
 const [p,d,c,b,t]=v;
 if(p<0||p>100000000||d<1||d>365||c<0||c>1000000||b<0||b>100||t<0||t>100)return null;
 const grossBase=p*b/100*d/365, grossHeadline=p*t/100*d/365;
 return {grossBase,grossHeadline,netBase:grossBase-c,netHeadline:grossHeadline-c,
         daysToBreakEven:p*b>0?c*36500/(p*b):null};
}
export function ageHours(iso,now=Date.now()){
 const timestamp=Date.parse(iso);
 return Number.isFinite(timestamp)?Math.max(0,(now-timestamp)/3600000):Infinity;
}
export function visibleRows(rows,{asset='USDC',chain='all',sort='base',quality='all'}={}){
 const filtered=rows.filter(p=>{
  if(!p||typeof p!=='object')return false;
  if(asset!=='all'&&p.asset!==asset)return false;
  if(chain!=='all'&&p.chain!==chain)return false;
  const flags=Array.isArray(p.flags)?p.flags:[];
  if(quality==='rewards'&&!flags.includes('incentive_heavy'))return false;
  if(quality==='volatile'&&!flags.includes('rate_change_large'))return false;
  if(quality==='unknown'&&!flags.some(f=>['reward_split_unknown','history_unavailable','week_change_unavailable'].includes(f)))return false;
  return true;
 });
 const metric=sort==='total'?'apy_pct':sort==='tvl'?'tvl_usd':'base_pct';
 filtered.sort((a,b)=>{
  if(sort==='rewards'){
   const ratio=p=>p.rewards_pct===null||!p.apy_pct?-1:p.rewards_pct/p.apy_pct;
   return ratio(b)-ratio(a);
  }
  return (b[metric]??0)-(a[metric]??0);
 });
 return filtered;
}
/** Compose only a buyer-initiated draft using already-public, bounded provider metadata.
 * Never serialize wallet/portfolio/principal inputs; never send an email automatically. */
export function buyerInquiryHref(row){
 if(!row || typeof row!=='object')return null;
 const {id,protocol,chain,asset}=row;
 if(typeof id!=='string'|| !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(id))return null;
 if(typeof protocol!=='string'|| !/^[a-z0-9-]{2,48}$/.test(protocol))return null;
 if(typeof chain!=='string'|| !/^[A-Za-z0-9 -]{2,32}$/.test(chain))return null;
 if(typeof asset!=='string'|| !/^[A-Z0-9]{2,12}$/.test(asset))return null;
 const subject='Public yield data QA scope — '+protocol+' '+chain+' '+asset;
 const message=[
  'Hello, I selected one PUBLIC DeFi pool in the free yield comparison:',
  'Provider: DefiLlama Yields; protocol: '+protocol+'; chain: '+chain+'; token: '+asset,
  'Public pool ID: '+id,
  '',
  'Concrete source-data discrepancy I need reviewed:',
  'Public supporting URL or reported field:',
  'Is a paid technical QA report worth a fixed scoped quote? (yes/no):',
  '',
  'Please confirm exact deliverables, timeline, privacy, acceptance, cancellation/refunds,',
  'recipient control, Base native Circle USDC token and fixed price before any payment.',
  'I have NOT attached wallet keys, balances, portfolio data, private files or real trades.',
  'This is a manual email draft only; no data has been transmitted by the website.'
 ].join('\n');
 return 'mailto:onecursor1@gmail.com?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(message);
}

const flagNames={
 reward_split_unknown:'Rewards breakdown unknown',incentive_heavy:'Incentive-heavy',
 week_change_unavailable:'7d change missing',rate_change_large:'Large weekly change',
 history_unavailable:'30d mean missing',spot_above_month_average:'Spot above month average'
};
const $=id=>document.getElementById(id);
const dollars=v=>'$'+Number(v).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
const number=v=>Number(v).toLocaleString('en-US');
const percent=v=>v===null||v===undefined?'unknown':Number(v).toFixed(2)+'%';
const decimal=v=>v===null||v===undefined?'unknown':Number(v).toFixed(2);
const make=(tag,content,className)=>{const el=document.createElement(tag);el.textContent=content;if(className)el.className=className;return el;};
let data=null,chosen=null;
function calc(){
 if(!chosen){$('result').textContent='Choose a pool row above.';return;}
 const v=['principal','days','cost'].map(id=>Number($(id).value));
 const out=illustrative(v[0],v[1],v[2],chosen.base_pct,chosen.apy_pct);
 if(!out){$('result').textContent='Invalid inputs. Enter a nonnegative principal and estimated fees; days must be 1–365.';return;}
 const breakEven=out.daysToBreakEven===null?'not defined':
  out.daysToBreakEven>365?'>365 days at the reported static base APY':
  Math.ceil(out.daysToBreakEven)+' days at the reported static base APY';
 $('result').textContent='Base-only hypothetical gross '+dollars(out.grossBase)+
  '; base-only after assumed fees '+dollars(out.netBase)+
  '. Headline APY with incentives hypothetical gross '+dollars(out.grossHeadline)+
  '; after assumed fees '+dollars(out.netHeadline)+
  '. Base-only fee break-even '+breakEven+
  '. These hypothetical figures do not account for principal losses, variable rates, taxes or other risk.';
}
function filters(){return {asset:$('asset').value,chain:$('chain').value,sort:$('sort').value,quality:$('quality').value};}
function render(){
 if(!data)return;
 const rows=visibleRows(data.pools,filters()),body=$('body');
 $('row-count').textContent=number(rows.length);
 body.replaceChildren();
 if(!rows.length){
  const tr=document.createElement('tr'),td=make('td','No markets match this filter. Try another token, chain or flag.');
  td.colSpan=9;tr.append(td);body.append(tr);return;
 }
 for(const p of rows){
  const tr=document.createElement('tr');
  tr.setAttribute('aria-selected',String(chosen?.id===p.id));
  const first=make('td',p.protocol,'good');
  const button=make('button','Compare','pick');button.type='button';
  button.setAttribute('aria-label','Calculate hypothetical yield on '+p.protocol+' '+p.chain+' '+p.asset);
  button.addEventListener('click',()=>{
   chosen=p;$('chosen').textContent=p.protocol+' · '+p.chain+' · '+p.asset+' · pool '+p.id.slice(0,8);
   const buyerDraft=buyerInquiryHref(p);
   if(buyerDraft){
    $('request-pool-email').href=buyerDraft;
    $('request-context').textContent='Optional manual email draft now includes public '+p.protocol+' / '+p.chain+' / '+p.asset+' pool ID '+p.id+'. No portfolio input, wallet data or email is sent until you choose to send it.';
   }
   calc();render();
  });first.append(button);tr.append(first);
  tr.append(make('td',p.chain+' / '+p.asset));
  tr.append(make('td','$'+number(p.tvl_usd)));
  tr.append(make('td',percent(p.base_pct),'good'));
  tr.append(make('td',percent(p.rewards_pct),p.rewards_pct===null?'muted':''));
  tr.append(make('td',percent(p.apy_pct)));
  tr.append(make('td',percent(p.mean30_pct)));
  tr.append(make('td',decimal(p.delta7_pctpoints)));
  const flags=(p.flags||[]).filter(f=>f!=='protocol_and_issuer_risk_not_assessed').map(f=>flagNames[f]||'Unspecified data flag');
  tr.append(make('td',flags.length?flags.join('; '):'Risks not assessed','flags'));
  body.append(tr);
 }
}
function csvValue(v){return '"'+String(v??'unknown').replaceAll('"','""')+'"';}
function exportCsv(){
 if(!data)return;
 const rows=visibleRows(data.pools,filters());
 const cols=['id','protocol','chain','asset','tvl_usd','base_pct','rewards_pct','apy_pct','mean30_pct','delta7_pctpoints','flags'];
 const raw=[cols.join(','),...rows.map(p=>cols.map(c=>csvValue(Array.isArray(p[c])?p[c].join('|'):p[c])).join(','))].join('\n')+'\n';
 const objectUrl=URL.createObjectURL(new Blob([raw],{type:'text/csv;charset=utf-8'}));
 const link=document.createElement('a');link.href=objectUrl;
 link.download='stablecoin-yield-public-'+(data.checked_utc||'snapshot').slice(0,10)+'.csv';
 document.body.append(link);link.click();link.remove();
 setTimeout(()=>URL.revokeObjectURL(objectUrl),1000);
}
async function boot(){
 ['asset','chain','sort','quality'].forEach(id=>$(id).addEventListener('change',render));
 ['principal','days','cost'].forEach(id=>$(id).addEventListener('input',calc));
 $('export').addEventListener('click',exportCsv);
 try{
  const response=await fetch('./data/pools.json',{cache:'no-store'});
  if(!response.ok)throw new Error('Public snapshot HTTP '+response.status);
  const doc=await response.json();
  if(doc.schema!==1||!Array.isArray(doc.pools)||!doc.checked_utc||!Number.isInteger(doc.total_pools_inspected))throw new Error('Unexpected snapshot schema');
  data=doc;
  $('all-count').textContent=number(doc.total_pools_inspected);
  $('qualified-count').textContent=number(doc.matched_filters);
  $('shown-count').textContent=number(doc.displayed);
  const age=ageHours(doc.checked_utc),time=new Date(doc.checked_utc).toLocaleString();
  $('status').textContent=age>24
    ?'STALE PUBLIC DATA: '+Math.floor(age)+' hours old (checked '+time+'). Do not use old figures for financial decisions. Feed refresh is offline or delayed.'
    :'Public provider snapshot '+time+' ('+age.toFixed(1)+'h ago). Not a live chain verification; values may change.';
  if(age>24)$('status').className='warning';
  render();
 }catch(e){
  $('status').textContent='Snapshot unavailable: '+(e instanceof Error?e.message:'unknown error')+'. No APY numbers inferred or invented.';
  $('status').className='warning';
  const tr=document.createElement('tr'),td=make('td','No public data available.');td.colSpan=9;tr.append(td);$('body').replaceChildren(tr);
 }
}
if(typeof document!=='undefined')boot();
