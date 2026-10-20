from pathlib import Path
import unittest
from html.parser import HTMLParser
class Parser(HTMLParser):pass
P=Path(__file__).resolve().parent.parent
class FeedbackTests(unittest.TestCase):
 def test_one_real_verified_public_optional_form_url(self):
  s=(P/'index.html').read_text()
  u='https://docs.google.com/forms/d/e/1FAIpQLSdQgzl-FctFmpdOlPj0KVM4wrOXm_VeuYTOP3ry5qsZv-MaTw/viewform'
  self.assertEqual(s.count('href="'+u+'"'),1)
  self.assertIn('hypothetically',s)
  self.assertIn('Email collection and the one-response Google sign-in restriction were disabled',s)
  self.assertIn('no verified independent respondents',s)
  self.assertIn('no new USDC receipts',s)
  self.assertIn('id="real-user-feedback"',s)
  self.assertIn('19 native Circle USDC',s)
  Parser().feed(s)
if __name__=='__main__':unittest.main()
