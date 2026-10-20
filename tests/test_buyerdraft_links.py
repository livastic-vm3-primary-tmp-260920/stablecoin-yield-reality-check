from html.parser import HTMLParser
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

class BuyerDraftLinkTests(unittest.TestCase):
 def test_single_buyer_mailto_and_seller_path(self):
  h=(ROOT/'index.html').read_text()
  self.assertEqual(h.count('id="request-pool-email"'),1)
  self.assertEqual(h.count('id="request-context"'),1)
  self.assertEqual(h.count('href="https://opentask.ai/profiles/cmvckd5ok00cx08jyc1yh8bvz"'),1)
  self.assertIn('not</strong> an automatically purchasable listing',h)
  self.assertIn('19 native Circle USDC',h)
  self.assertIn('no paid buyer, order, delivery or revenue',h)
  HTMLParser().feed(h)

 def test_only_explicit_click_prepares_draft(self):
  s=(ROOT/'app.mjs').read_text()
  self.assertIn("button.addEventListener('click'",s)
  self.assertIn("const buyerDraft=buyerInquiryHref(p)",s)
  self.assertIn("$('request-pool-email').href=buyerDraft",s)
  self.assertNotIn('location.href=buyerDraft',s)
  self.assertNotIn('window.open(buyerDraft',s)
