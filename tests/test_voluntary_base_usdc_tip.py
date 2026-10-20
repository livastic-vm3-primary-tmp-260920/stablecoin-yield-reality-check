import unittest
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
class Parser(HTMLParser):pass
class TipTest(unittest.TestCase):
 def test_one_tip_page_with_consistent_pinned_original_payee(self):
  src=(ROOT/'index.html').read_text(encoding='utf8')
  assert src.count('id="optional-support"')==1
  assert src.count('id="public-tip-recipient"')==1
  assert src.count('id="copy-public-tip-recipient"')==1
  assert '0x6b01efA0705E91a7aca54271510bf9e594717f34' in src
  assert '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913' in src
  assert 'Base <strong>mainnet</strong>' in src and 'eip155:8453' in src
  assert 'not</strong> a purchase' in src
  assert 'Do NOT tip this address as an order' in src
  assert '19-USDC indicative QA enquiry' in src
  assert 'No confirmed tips' in src
  assert 'src="./tip.mjs"' in src
  Parser().feed(src)
 def test_do_not_use_ethereum_uri_or_wallet_autoconnect(self):
  html=(ROOT/'index.html').read_text(encoding='utf8')
  script=(ROOT/'tip.mjs').read_text(encoding='utf8')
  for text in ['window.ethereum','eth_sendTransaction','eth_requestAccounts','walletconnect','personal_sign','PAYMENT-SIGNATURE','ethereum:0x','localStorage','fetch(','XMLHttpRequest']:
   with self.subTest(text=text):
    assert text not in html or text in ['fetch('] # original page may mention terms
    assert text not in script
if __name__=='__main__':unittest.main()
