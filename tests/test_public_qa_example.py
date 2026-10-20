"""Reproducibility and truthful financial-unit invariants for free case study."""
from pathlib import Path
import json,sys,unittest
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_qa_sample import html_from_document,model,money
class PublicQADemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'data/public-qa-example-20261021.json').read_text())
        cls.rows=cls.data['pools']
        cls.html=(ROOT/'public-qa-example.html').read_text()
    def test_exact_three_distinct_public_pool_ids(self):
        self.assertEqual(len(self.rows),3)
        self.assertEqual(len({r['id'] for r in self.rows}),3)
        self.assertTrue(all(r['asset']=='USDC' for r in self.rows))
        self.assertEqual(self.data['source'],'https://yields.llama.fi/pools')
        self.assertTrue(self.data['checked_utc'].startswith('2026-10-20T20:'))
        self.assertEqual(len(self.data['source_snapshot_sha256']),64)
    def test_base_case_fees_exceed_illustrative_return(self):
        row=next(r for r in self.rows if r['case']=='No reported reward component')
        v=model(row,1000,30,12)
        self.assertEqual(money(v['base_gross']),'$4.66')
        self.assertEqual(money(v['base_after_fees']),'-$7.34')
        self.assertEqual(v['reward_state'],'reported zero')
    def test_reward_heavy_not_base_rate(self):
        r=next(r for r in self.rows if r['case']=='Reward-heavy headline')
        v=model(r,1000,30,12)
        self.assertEqual(v['reward_state'],'reported nonzero')
        self.assertTrue(v['reward_share']>Decimal('30'))
        self.assertTrue(v['headline_after_fees']>v['base_after_fees'])
        self.assertTrue(v['base_after_fees']<0)
    def test_unknown_rewards_never_zero(self):
        r=next(r for r in self.rows if r['case']=='Missing reward breakdown')
        self.assertIsNone(r['rewards_pct'])
        v=model(r,1000,30,12)
        self.assertIsNone(v['reward_share'])
        self.assertEqual(v['reward_state'],'unknown')
        self.assertIn('unknown (null)',self.html)
    def test_invalid_values_rejected(self):
        for v in (None,True,float('nan'),float('inf'),-1):
            with self.subTest(v=v), self.assertRaises(ValueError):
                model(self.rows[0],v,30,12)
        for d in (0,366):
            with self.assertRaises(ValueError):
                model(self.rows[0],1000,d,12)
    def test_reproducible_html(self):
        self.assertEqual(html_from_document(self.data),self.html)
    def test_source_strings_escaped(self):
        doc=json.loads(json.dumps(self.data))
        doc['pools'][0]['protocol']='<script>alert(1)</script>'
        result=html_from_document(doc)
        self.assertNotIn('<script>alert(1)</script>',result)
        self.assertIn('&lt;script&gt;',result)
    def test_no_payment_or_fabricated_buyer(self):
        self.assertNotIn('<script',self.html)
        self.assertIn('mailto:onecursor1@gmail.com?',self.html)
        self.assertIn('not a customer commission',self.html.lower())
        self.assertIn('No independent buyer',self.html)
        self.assertIn('before any payment',self.html)
    def test_discoverability(self):
        index=(ROOT/'index.html').read_text()
        self.assertEqual(index.count('href="./public-qa-example.html"'),1)
        self.assertEqual((ROOT/'sitemap.xml').read_text().count('/public-qa-example.html'),1)
if __name__=='__main__':unittest.main()
