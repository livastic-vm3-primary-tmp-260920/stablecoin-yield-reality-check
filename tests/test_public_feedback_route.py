import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
class FeedbackRouteTest(unittest.TestCase):
    def test_one_free_public_issue_route_and_plain_language_disclosure(self):
        page=(ROOT/'index.html').read_text()
        template='issues/new?template=public-yield-data-error.yml'
        self.assertEqual(page.count(template),1)
        self.assertIn('GitHub login required',page)
        self.assertIn('no paid buyer, order, delivery or revenue',page)
        self.assertIn('https://dev.to/livasticvm3primarytmp260920/why-6-stablecoin-apy-can-lose-to-a-12-round-trip-3ooi',page)
    def test_issue_template_requires_only_public_non_sensitive_data(self):
        f=(ROOT/'.github/ISSUE_TEMPLATE/public-yield-data-error.yml').read_text()
        for term in ('public pool','NEVER','reproduce','required: true','wallet addresses'):
            self.assertIn(term.casefold(),f.casefold())
if __name__=='__main__':unittest.main()
