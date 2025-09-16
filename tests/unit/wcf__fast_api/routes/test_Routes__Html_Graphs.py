from unittest                               import TestCase
from osbot_fast_api.api.Fast_API            import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_utils.utils.Env                  import get_env
from tests.unit.wcf__objs_for_tests         import wcf_tests__setup_fast_api, setup_local_stack


class test_Routes__Html_Graphs(TestCase):
    @classmethod
    def setUpClass(cls):
        setup_local_stack()
        from mgraph_ai_web_content_filtering.wcf__fast_api.routes.Routes__Html_Graphs import Routes__Html_Graphs
        cls.wcf_test_data      = wcf_tests__setup_fast_api()
        cls.client             = cls.wcf_test_data.wcf__fast_api__client
        cls.routes_html_graphs = Routes__Html_Graphs()

    def test__client__url_to_html(self):
        from mgraph_ai_web_content_filtering.wcf__fast_api.routes.Routes__Html_Graphs import ROUTES__TAG__HTML_GRAPHS
        auth_key_name  = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME)
        auth_key_value = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE)
        assert auth_key_name  is not None
        assert auth_key_value is not None
        headers = {auth_key_name: auth_key_value}
        url     = "https://text.npr.org"
        response = self.client.get(f'/{ROUTES__TAG__HTML_GRAPHS}/url-to-html?url={url}', headers=headers)
        assert response.status_code == 200

    def test__direct__url_to_text_nodes(self):
        with self.routes_html_graphs as _:
            text_nodes = _.url_to_text_nodes()
            assert text_nodes['1e314df0e1'] == { 'original_text': '\n   BBC - 404: Not Found\n    ',
                                                 'tag'          : 'title' }
