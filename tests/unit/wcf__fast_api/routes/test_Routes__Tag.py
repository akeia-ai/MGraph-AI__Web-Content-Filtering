from unittest                                                           import TestCase

import pytest
from mgraph_ai_web_content_filtering.wcf__fast_api.routes.Routes__Url   import Routes__Url
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.config.consts__Semantic_Text import ENV_VAR__API_KEY__SERVICE__CACHE__KEY_NAME
from osbot_utils.utils.Env import get_env
from tests.unit.wcf__objs_for_tests                                     import wcf_tests__setup_fast_api


class test_Routes__Tag(TestCase):

    @classmethod
    def setUpClass(cls):
        if not get_env(ENV_VAR__API_KEY__SERVICE__CACHE__KEY_NAME):
            pytest.skip("Tests requires service cache API key and value")
        local_objs = wcf_tests__setup_fast_api()
        cls.routes_url = Routes__Url()

    def test_to__hashes(self):
        with self.routes_url as _:
            url_hashes = _.to__hashes()
            assert url_hashes['1e314df0e1'] == {'original_text': '\n   BBC - 404: Not Found\n    ',
                                                'tag'          : 'title'                          }
            assert len(url_hashes)> 20

    # def test_to_hashes__check_distribution(self):
    #                                                           # hashes on page  | distribution (2 chars)  |  json file size   | duration (with cache) | duration (with url featch)
    #     url = 'https://en.wikipedia.org/wiki/September_15'    #      2213       |          256            |      213,154      |     50 ms             |     222 ms
    #     url = 'https://en.wikipedia.org/wiki/2025'            #      3018       |          256            |      300,532      |    100ms              |     270 ms
    #     url = 'https://www.theregister.com/'                  #      335        |          195            |       41,480      |     11 ms             |     160 ms
    #     url = "https://www.amazon.com/"                       #      291        |          172            |        27,073     |     20 ms             |     700 ms
    #     url = 'https://news.bbc.co.uk'                        #      292        |          167            |        31,202     |     36 ms             |     385 ms
    #     url = 'https://news.bbc.co.uk/sport'                  #      400        |          201            |        42,249     |     32 ms             |     580 ms
    #     url = 'https://theguardian.co.uk'                     #      484        |          226            |        55,953     |     48 ms             |     300 ms
    #     url = "https://www.theguardian.com/uk/sport"          #      288 ,      |          166            |        31,216     |     21 ms             |     160 ms
    #
    #     #url = WEBSITE_URL__DEFAULT_SITE
    #     with self.routes_url as _:
    #         with print_duration():
    #             url_hashes = _.to__hashes(url=url, reload=False)
    #         print()
    #         distribution = {}
    #         for url_hash in url_hashes:
    #             key = url_hash[0:2]
    #             if key not in distribution:
    #                 distribution[key] = []
    #             distribution[key].append(url_hash)
    #         print()
    #         print('hash_count        :', len(url_hashes))
    #         print('distribution_count:', len(distribution))
    #         print('json size         :', len(json_to_str(url_hashes)))

