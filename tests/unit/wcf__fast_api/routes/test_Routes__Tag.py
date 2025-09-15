from unittest import TestCase

from mgraph_ai_web_content_filtering.wcf__fast_api.routes.Routes__Url import Routes__Url
from osbot_utils.utils.Dev import pprint
from tests.unit.wcf__objs_for_tests import wcf_tests__setup_fast_api


class test_Routes__Tag(TestCase):

    @classmethod
    def setUpClass(cls):
        local_objs = wcf_tests__setup_fast_api()
        cls.routes_url = Routes__Url()

    def test_to__hashes(self):
        with self.routes_url as _:
            url_hashes = _.to__hashes()
            assert url_hashes['1e314df0e1'] == {'original_text': '\n   BBC - 404: Not Found\n    ',
                                                'tag'          : 'title'                          }
