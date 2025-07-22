from unittest import TestCase
from fastapi  import FastAPI

from mgraph_ai_web_content_filtering.lambdas.dev.wcf__5__fast_api__with_router.WCF__5__Fast_API__With_Router import \
    WCF__5__Fast_API__With_Router


class test_WCF__5__Fast_API__With_Router(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fast_api_with_routes = WCF__5__Fast_API__With_Router()

    def test__init__(self):
        with self.fast_api_with_routes as _:
            assert type(_      ) is WCF__5__Fast_API__With_Router
            assert type(_.app()) is FastAPI
            assert _.name        == 'WCF__5__Fast_API__With_Router'

