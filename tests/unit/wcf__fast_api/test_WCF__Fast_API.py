from unittest import TestCase

from osbot_fast_api_serverless.fast_api.routes.Routes__Info         import ROUTES_PATHS__INFO
from mgraph_ai_web_content_filtering.wcf__fast_api.WCF__Fast_API    import WCF__Fast_API
from mgraph_ai_web_content_filtering.wcf__fast_api.routes.Routes__Html_Graphs import ROUTES_PATHS__HTML_GRAPHS
from tests.unit.wcf__objs_for_tests                                 import setup_local_stack, wcf_tests__setup_fast_api


class test_WCF__Fast_API(TestCase):
    @classmethod
    def setUpClass(cls):
        setup_local_stack()
        cls.wcf_test_data = wcf_tests__setup_fast_api()
        cls.wcf_fast_api = cls.wcf_test_data.wcf__fast_api

    def test_setUpClass(self):
        with self.wcf_fast_api as _:
            assert type(_) is WCF__Fast_API

    def test__config_fast_api_routes(self):
        assert self.wcf_fast_api.routes_paths() == sorted(ROUTES_PATHS__INFO +
                                                          ROUTES_PATHS__HTML_GRAPHS)