import test from 'node:test';
import assert from 'node:assert/strict';
import {buyerInquiryHref} from '../app.mjs';
import {readFileSync} from 'node:fs';

const sample=Object.freeze({
 id:'7372edda-f07f-4598-a347-90b5099b31cb',
 protocol:'fluid-lending',
 chain:'Base',
 asset:'USDC',
 base_pct:4.99,
 apy_pct:8.19,
 arbitraryWalletAddress:'0xDONOTLEAK',
 principal:'SECRET PRINCIPAL',
 actualUserPortfolio:'PRIVATE_PII'
});

test('creates a safe manual email draft with the selected actual public pool',()=>{
 const href=buyerInquiryHref(sample);
 assert.ok(href.startsWith('mailto:onecursor1@gmail.com?subject='));
 const u=new URL(href);
 assert.match(u.searchParams.get('subject'),/fluid-lending Base USDC/);
 assert.match(u.searchParams.get('body'),/Public pool ID: 7372edda-f07f-4598-a347-90b5099b31cb/);
 assert.match(u.searchParams.get('body'),/before any payment/);
 assert.match(u.searchParams.get('body'),/manual email draft only/);
 assert.ok(href.length<2200,'bounded mailto URI');
});

test('never puts hypothetical principal, private rows, wallet or user data in generated inquiry',()=>{
 const href=buyerInquiryHref(sample);
 for(const secret of ['0xDONOTLEAK','SECRET PRINCIPAL','PRIVATE_PII','4.99','8.19'])
  assert.ok(!href.includes(secret),secret+' must not leak');
});

test('invalid or adversarial provider metadata cannot enter a mailto URL',()=>{
 const overrides=[
  {id:'not-a-public-uuid'},
  {id:'7372edda-f07f-4598-a347-90b5099b31cb\nBCC:intruder@example.com'},
  {protocol:'bad@example.com?bcc=evil'},
  {chain:'Base&body=pwned'},
  {asset:'USDC%0D%0A'},
  {asset:{toString(){throw new Error('should not invoke')}}},
  {protocol:'h'.repeat(4096)},
  {asset:''}
 ];
 for(const o of overrides) assert.equal(buyerInquiryHref({...sample,...o}),null,JSON.stringify(o));
 for(const obj of [null,undefined,false,42,'btc',[]])assert.equal(buyerInquiryHref(obj),null);
});

test('public data only: no sending or network APIs in helper implementation',()=>{
 const href=buyerInquiryHref(sample);
 assert.equal(typeof href,'string');
 assert.ok(!href.startsWith('https://'));
 assert.ok(!href.includes('0xDONOTLEAK'));
 assert.ok(!href.includes('fetch('));
});

test('all currently published real pool IDs yield a privacy-scoped buyer draft',()=>{
 const data=JSON.parse(readFileSync(new URL('../data/pools.json',import.meta.url),'utf8'));
 assert.ok(data.pools.length>=1);
 for(const pool of data.pools){
  const link=buyerInquiryHref(pool);
  assert.ok(link?.startsWith('mailto:onecursor1@gmail.com?'),pool.id);
  const body=new URL(link).searchParams.get('body');
  assert.ok(body?.includes(pool.id));
  assert.ok(!body?.includes('0xDONOTLEAK'));
 }
});
