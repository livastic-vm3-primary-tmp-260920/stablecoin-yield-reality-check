from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class PublicDiscoveryTests(unittest.TestCase):
    def test_real_public_inbound_cta_and_directory_credit(self):
        index=(ROOT/'index.html').read_text(encoding='utf-8')
        self.assertIn('href="mailto:onecursor1@gmail.com?subject=Stablecoin%20Yield%20QA',index)
        self.assertIn('No%20wallet%20credentials%20or%20private%20portfolio%20data',index)
        self.assertIn('href="https://polymart.app/crypto"',index)
        self.assertIn('rel="nofollow noopener noreferrer"',index)
        self.assertIn('no paid buyer, order, delivery or revenue',index)
