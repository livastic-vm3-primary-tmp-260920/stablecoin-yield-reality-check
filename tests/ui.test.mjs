import test from 'node:test';
import assert from 'node:assert/strict';
import {finite,illustrative,ageHours,visibleRows} from '../app.mjs';
test('fee example is negative after costs with small principal',()=>{
 const x=illustrative(1000,30,12,4,6);
 assert.ok(Math.abs(x.grossBase-3.2876712328)<0.00001);
 assert.ok(x.netBase<0);assert.ok(x.netHeadline<0);assert.ok(x.daysToBreakEven>30);
});
test('no capital generates zero income',()=>{
 const x=illustrative(0,30,0,4,8);
 assert.equal(x.grossBase,0);assert.equal(x.grossHeadline,0);assert.equal(x.daysToBreakEven,null);
});
test('reject invalid financial inputs',()=>{
 for(const values of [[-1,30,1,5,6],[100,0,1,5,6],[100,366,1,5,6],
  [100,30,-1,5,6],[100,30,1,Infinity,6],[100,30,1,5,NaN]])assert.equal(illustrative(...values),null);
 assert.equal(finite('5'),null);
});
test('feed staleness is calculable; invalid timestamp rejected',()=>{
 assert.equal(ageHours('no'),Infinity);
 assert.equal(ageHours('2026-10-20T10:00:00Z',Date.parse('2026-10-20T12:00:00Z')),2);
});
test('filter and sort without mutating source array',()=>{
 const a={id:'a',asset:'USDC',chain:'Base',base_pct:3,tvl_usd:100,apy_pct:5,rewards_pct:2,flags:['incentive_heavy']};
 const b={id:'b',asset:'USDT',chain:'Ethereum',base_pct:6,tvl_usd:900,apy_pct:6,rewards_pct:null,flags:['reward_split_unknown']};
 const arr=[a,b];
 assert.deepEqual(visibleRows(arr,{asset:'USDC'}),[a]);
 assert.deepEqual(visibleRows(arr,{asset:'all',quality:'unknown'}),[b]);
 assert.deepEqual(visibleRows(arr,{asset:'all',sort:'tvl'}),[b,a]);
 assert.deepEqual(arr,[a,b]);
});
test('hidden reward split does not rank ahead of known shares',()=>{
 const a={asset:'USDC',chain:'Base',rewards_pct:null,apy_pct:5,flags:[]};
 const b={asset:'USDC',chain:'Base',rewards_pct:1,apy_pct:5,flags:[]};
 assert.deepEqual(visibleRows([a,b],{sort:'rewards'}),[b,a]);
});
