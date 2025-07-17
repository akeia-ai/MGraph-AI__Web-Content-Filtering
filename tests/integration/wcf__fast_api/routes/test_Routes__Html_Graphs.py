from unittest                                                                   import TestCase
from mgraph_ai_web_content_filtering.wcf__fast_api.routes.Routes__Html_Graphs   import ROUTES__TAG__HTML_GRAPHS
from tests.integration.wcf__objs_for_tests                                      import wcf_tests__setup_fast_api

class test_Routes__Html_Graphs(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wcf_test_data = wcf_tests__setup_fast_api()
        cls.client        = cls.wcf_test_data.wcf__fast_api__client

    def test__html_graphs__html_to_html_dict(self):
        url = "https://text.npr.org"
        response = self.client.get(f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html?url={url}')
        assert response.status_code == 200