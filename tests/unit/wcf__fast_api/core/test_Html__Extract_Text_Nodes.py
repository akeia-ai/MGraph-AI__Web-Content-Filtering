import pytest
from unittest                                                                       import TestCase
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.config.consts__Semantic_Text import ENV_VAR__API_KEY__SERVICE__CACHE__KEY_NAME
from osbot_utils.utils.Env import get_env
from osbot_utils.utils.Misc                                                         import list_set
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Extract_Text_Nodes    import Html__Extract_Text_Nodes
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations       import WEBSITE_URL__DEFAULT_SITE
from tests.unit.wcf__objs_for_tests                                                 import setup_local_stack


class test_Html__Extract_Text_Nodes(TestCase):

    @classmethod
    def setUpClass(cls):
        if not get_env(ENV_VAR__API_KEY__SERVICE__CACHE__KEY_NAME):
            pytest.skip("Tests requite service cache API key and value")
        setup_local_stack()
        cls.html_extract_text_nodes = Html__Extract_Text_Nodes()

    def test_1__extract(self):
        #url = 'https://www.bbc.com/sport/football/articles/cvg8j1l0751o'
        url = WEBSITE_URL__DEFAULT_SITE
        with self.html_extract_text_nodes as _:
            _.url         = url
            text_elements = _.extract()
            assert text_elements['1e314df0e1'] ==  { 'original_text': '\n   BBC - 404: Not Found\n    ',
                                                      'tag': 'title'}
            assert _.captures == 23

    def test_2__create_html_with_hashes_as_text(self):
        url = WEBSITE_URL__DEFAULT_SITE
        with self.html_extract_text_nodes as _:
            _.url = url
            html_with_hashes = _.create_html_with_hashes_as_text()
            assert "<title>1e314df0e1</title>" in html_with_hashes

    def test_3__create_html_with_xxx_as_text(self):
        url = WEBSITE_URL__DEFAULT_SITE
        with self.html_extract_text_nodes as _:
            _.url = url
            html_with_xxxx = _.create_html_with_xxx_as_text()
            assert "<title>x   xxx x xxxx xxx xxxxxx    </title>" in html_with_xxxx

    def test_4__create_ratings(self):
        url = WEBSITE_URL__DEFAULT_SITE
        with self.html_extract_text_nodes as _:
            _.url = url
            ratings = _.create_ratings()
            assert len(ratings) > 20
            for text_hash, rating in ratings.items():
                assert len(text_hash)   == 10
                assert list_set(rating) == ['hash', 'positivity', 'topic']

    def test_5__create_html_with_ratings(self):
        url = WEBSITE_URL__DEFAULT_SITE
        with self.html_extract_text_nodes as _:
            _.url = url
            html_with_ratings = _.create_html_with_ratings()
            assert "<title>" in html_with_ratings                   # todo: improve this assert

    # def test_6__create_html_with_ratings(self):
    #     url = WEBSITE_URL__DEFAULT_SITE
    #     with self.html_extract_text_nodes as _:
    #         _.url = url
    #         html_with_topics = _.create_html_with_topics()
    #         #pprint(html_with_topics)
    #         assert "<title>" in html_with_topics

    # def test_7__create_html_with_min_ratings(self):
    #     url = WEBSITE_URL__DEFAULT_SITE
    #     with self.html_extract_text_nodes as _:
    #         _.url = url
    #         html_with_min_rating = _.create_html_with_min_ratings()
    #         #pprint(html_with_min_rating)
    #         #assert "<title>404 Error</title>" in html_with_topics