from unittest                                                                   import TestCase

from osbot_utils.utils.Dev import pprint

from mgraph_ai_web_content_filtering.wcf__fast_api.routes.Routes__Html_Graphs import ROUTES__TAG__HTML_GRAPHS, \
    Routes__Html_Graphs
from tests.integration.wcf__objs_for_tests                                      import wcf_tests__setup_fast_api

class test_Routes__Html_Graphs(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wcf_test_data      = wcf_tests__setup_fast_api()
        cls.client             = cls.wcf_test_data.wcf__fast_api__client
        cls.routes_html_graphs = Routes__Html_Graphs()

    def test__client__url_to_html(self):
        url = "https://text.npr.org"
        response = self.client.get(f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html?url={url}')
        assert response.status_code == 200

    def test__direct__url_to_text_nodes(self):
        with self.routes_html_graphs as _:
            text_nodes = _.url_to_text_nodes()
            assert text_nodes['1e314df0e1'] == { 'original_text': '\n   BBC - 404: Not Found\n    ',
                                                 'tag'          : 'title' }
