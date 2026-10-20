import test from 'node:test';
import assert from 'node:assert/strict';
import { TIP_DETAILS, validatePublicTipDetails, copyPublicReceiver } from '../tip.mjs';
test('public payee and exact canonical native Base USDC are pinned', () => {
  assert.equal(TIP_DETAILS.chainId,8453);
  assert.equal(TIP_DETAILS.network,'Base mainnet');
  assert.equal(TIP_DETAILS.assetAddress.toLowerCase(),'0x833589fcd6edb6e08f4c7c32d4f71b54bda02913');
  assert.equal(TIP_DETAILS.publicPayTo.toLowerCase(),'0x6b01efa0705e91a7aca54271510bf9e594717f34');
  assert.equal(TIP_DETAILS.voluntaryExampleUsdc,'1');
  assert.equal(TIP_DETAILS.paymentCreatesOrder,false);
  assert.equal(TIP_DETAILS.browserAutoTransfers,false);
});
test('click copies only public receive address without any network/wallet hooks', async () => {
  const writes=[];
  const fakeClipboard={writeText:async value => {writes.push(value);}};
  assert.equal(await copyPublicReceiver(fakeClipboard),true);
  assert.deepEqual(writes,[TIP_DETAILS.publicPayTo]);
});
test('missing clipboard permission leaves manual selectable address', async () => {
  assert.equal(await copyPublicReceiver(null),false);
  assert.equal(await copyPublicReceiver({}),false);
  assert.equal(await copyPublicReceiver({writeText:async()=>{throw new Error('not permitted');}}),false);
});
test('safely refuse unrecognized asset, chain, recipient or paid-order fiction', async () => {
  for (const changed of [
    {chainId:1},{network:'Ethereum mainnet'},{assetAddress:'0x0000000000000000000000000000000000000000'},
    {publicPayTo:'0x0000000000000000000000000000000000000000'},{paymentCreatesOrder:true},{browserAutoTransfers:true}
  ]){
    const bad={...TIP_DETAILS,...changed};
    assert.throws(()=>validatePublicTipDetails(bad),TypeError);
    const writes=[];
    await assert.rejects(copyPublicReceiver({writeText:async value => writes.push(value)},bad),TypeError);
    assert.equal(writes.length,0);
  }
});
