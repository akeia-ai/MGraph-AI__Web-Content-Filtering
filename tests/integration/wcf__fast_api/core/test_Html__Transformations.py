from unittest import TestCase

from osbot_utils.utils.Dev import pprint

from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations import Html__Transformations

WEBSITE_URL__BBC__SPORT = "https://www.bbc.co.uk/sport"

class test_Html__Transformations(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_transformations = Html__Transformations().setup()

    def test__init__(self):
        with self.html_transformations as _:
            assert type(_) is Html__Transformations

    def test_html__get(self):
        with self.html_transformations as _:
            html = _.html__get(WEBSITE_URL__BBC__SPORT)
            pprint(html)
