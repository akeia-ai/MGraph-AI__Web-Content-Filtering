from unittest                                                                 import TestCase
from osbot_utils.utils.Misc                                                   import list_set
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations import Html__Transformations, WEBSITE_URL__DEFAULT_SITE


class test_Html__Transformations(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_transformations = Html__Transformations().setup()

    def test__init__(self):
        with self.html_transformations as _:
            assert type(_) is Html__Transformations

    def test_url_to_html(self):
        with self.html_transformations as _:
            html = _.url_to_html(WEBSITE_URL__DEFAULT_SITE)
            assert len(html) > 10000


    def test_url_to_html_dict(self):
        with self.html_transformations as _:
            html_dict = _.url_to_html_dict(WEBSITE_URL__DEFAULT_SITE)
            assert type(html_dict) is dict

            assert list_set(html_dict) == ['attrs', 'nodes', 'tag']

