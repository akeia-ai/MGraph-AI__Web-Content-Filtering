from unittest                                                                                   import TestCase
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                               import Safe_Id
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.config.consts__Semantic_Text   import CACHE_NAMESPACE__SEMANTIC_HTML
from osbot_utils.utils.Misc                                                                     import is_guid
from osbot_utils.utils.Objects                                                                  import base_classes
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                        import Safe_Str__Url
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.services.Cache__Client         import Cache__Client
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.services.Html__Cache__Manager  import Html__Cache__Manager
from tests.unit.wcf__objs_for_tests                                                             import setup_local_stack
import hashlib

class test_Html__Cache__Manager(TestCase):

    @classmethod
    def setUpClass(cls):                                                        # ONE-TIME expensive setup
        setup_local_stack()                                                     # LocalStack setup (2-3s)
        cls.cache_manager = Html__Cache__Manager()                              # Initialize once
        cls.test_url      = Safe_Str__Url("https://www.example.com/test")       # Shared test URL
        cls.test_html     = "<html><body>Test Content</body></html>"            # Shared test HTML
        cls.test_dict     = {"tag": "html", "nodes": []}                        # Shared test dict

    def test__init__(self):                                                     # Test auto-initialization
        with Html__Cache__Manager() as _:
            assert type(_)              is Html__Cache__Manager
            assert base_classes(_)      == [Type_Safe, object]
            assert type(_.cache_client) is Cache__Client                        # Auto-initialized
            assert _.namespace()        == CACHE_NAMESPACE__SEMANTIC_HTML       # Default namespace

    # todo: add tests for suffix
    def test__cache_key_for_url(self):                                          # Test URL to cache key conversion
        with self.cache_manager as _:
            # HTTPS URL
            url1 = Safe_Str__Url("https://www.bbc.co.uk/news/article")
            key1 = _._cache_key_for_url(url1, 'raw')
            assert key1 == "raw/bbc.co.uk/news/article"                    # www. and https:// removed

            # HTTP URL
            url2 = Safe_Str__Url("http://example.com/page")
            key2 = _._cache_key_for_url(url2, 'dict')
            assert key2 == "dict/example.com/page"                         # http:// removed

            # No suffix
            key3 = _._cache_key_for_url(url1, '')
            assert key3 == "bbc.co.uk/news/article"                        # No double slash

            # Trailing slash removal
            url4 = Safe_Str__Url("https://example.com/")
            key4 = _._cache_key_for_url(url4, 'raw')
            assert key4 == "raw/example.com"                               # Trailing slash removed

    def test__hash_for_cache_key(self):                                         # Test hash calculation
        with self.cache_manager as _:
            cache_key = "html/raw/example.com/test"
            hash1 = _._hash_for_cache_key(cache_key)

            assert len(hash1) == 16                                             # 16 character hash
            assert hash1 == hashlib.sha256(cache_key.encode('utf-8')).hexdigest()[:16]  # Correct calculation

            # Same input produces same hash
            hash2 = _._hash_for_cache_key(cache_key)
            assert hash2 == hash1                                               # Deterministic

    def test_store_and_retrieve_html(self):                                     # Test HTML storage and retrieval
        with self.cache_manager as _:
            unique_url = Safe_Str__Url(f"https://test.com/unique/{Safe_Id()}")

            # Store HTML
            store_result = _.store_html(unique_url, self.test_html)
            cache_id     = store_result.get('cache_id' )
            namespace    = store_result.get('namespace')

            assert is_guid(cache_id)
            assert namespace == 'semantic-html'

            # Retrieve HTML
            retrieved = _.retrieve_html(unique_url)
            assert retrieved == self.test_html                                  # Exact match

            delete_result = _.cache_client.delete_by_id(cache_id)
            assert delete_result.get('deleted_count') == 9


    def test_store_and_retrieve_html_dict(self):                                # Test dict storage and retrieval
        with self.cache_manager as _:
            unique_url = Safe_Str__Url(f"https://test.com/dict/{Safe_Id()}")

            # Store dict
            store_result = _.store_html_dict(unique_url, self.test_dict)
            cache_id    = store_result.get('cache_id' )

            # Retrieve dict
            retrieved = _.retrieve_html_dict(unique_url)

            assert retrieved == self.test_dict                                  # Exact match

            delete_result = _.cache_client.delete_by_id(cache_id)
            assert delete_result.get('deleted_count') == 9


    def test_store_and_retrieve_text_nodes(self):                               # Test text nodes storage
        with self.cache_manager as _:
            unique_url = Safe_Str__Url(f"https://test.com/nodes/{__import__('uuid').uuid4()}")
            text_nodes = {'hash1': {'original_text': 'Hello', 'tag': 'p'},
                         'hash2': {'original_text': 'World', 'tag': 'div'}}

            # Store text nodes
            store_result = _.store_text_nodes(unique_url, text_nodes)
            cache_id     = store_result.get('cache_id' )
            #assert 'cache_id' in store_result

            # Retrieve text nodes
            retrieved     = _.retrieve_text_nodes(unique_url)
            delete_result = _.cache_client.delete_by_id(cache_id)

            assert retrieved                          == text_nodes                    # Exact match
            assert delete_result.get('deleted_count') == 9
            #pprint(delete_result)
            #pprint(_.cache_client.delete_by_id('aa9a929d-41c1-4819-b448-1251e74f9d56'))

    def test_store_and_retrieve_ratings(self):                                  # Test ratings storage with model
        with self.cache_manager as _:
            unique_url = Safe_Str__Url(f"https://test.com/ratings/{Safe_Id()}")
            ratings    = {'data': {'ratings': [{'hash': 'h1', 'positivity': 0.8, 'topic': 'greeting'}]}}
            model      = 'gpt-4'

            store_result = _.store_ratings(unique_url, model, ratings)          # Store ratings
            cache_id     = store_result.get('cache_id' )

            retrieved     = _.retrieve_ratings(unique_url, model)                   # Retrieve ratings
            delete_result = _.cache_client.delete_by_id(cache_id)

            assert retrieved                                         == ratings     # Exact match
            assert _.retrieve_ratings(unique_url, 'different-model') is None        # Different model should return None
            assert delete_result.get('deleted_count')                == 9
            #pprint(delete_result)
            #pprint(_.cache_client.delete_by_id('aa9a929d-41c1-4819-b448-1251e74f9d56'))

    def test_has_cached_methods(self):                                          # Test cache existence checks
        with self.cache_manager as _:
            unique_url = Safe_Str__Url(f"https://test.com/exists/{Safe_Id()}")

            # Initially nothing cached
            assert _.has_cached_html        (unique_url         ) is False
            assert _.has_cached_html_dict   (unique_url         )  is False
            assert _.has_cached_text_nodes  (unique_url         ) is False
            assert _.has_cached_ratings     (unique_url, 'model') is False

            # Store HTML
            store_result = _.store_html(unique_url, "test")
            cache_id     = store_result.get('cache_id' )
            assert _.has_cached_html(unique_url) is True                        # Now cached

            # Others still not cached

            #assert _.has_cached_html_dict(unique_url)                          is False
            #pprint(_.has_cached_html_dict(unique_url))                         # todo: fix the logic in this workflow
            assert  _.cache_client.delete_by_id(cache_id).get('deleted_count') == 9
            assert _.has_cached_html(unique_url) is False                        # Now deleted


    def test_retrieve_nonexistent(self):                                        # Test retrieving non-cached items
        with self.cache_manager as _:
            nonexistent_url = Safe_Str__Url(f"https://never.cached.com/{__import__('uuid').uuid4()}")

            assert _.retrieve_html(nonexistent_url)       is None               # Returns None
            assert _.retrieve_html_dict(nonexistent_url)  is None
            assert _.retrieve_text_nodes(nonexistent_url) is None
            assert _.retrieve_ratings(nonexistent_url, 'model') is None

    def test_cache_key_consistency(self):                                       # Test hash-based retrieval consistency
        with self.cache_manager as _:
            url = Safe_Str__Url("https://www.example.com/test-consistency")

            # Calculate expected hash
            cache_key     = _._cache_key_for_url(url, 'raw')
            expected_hash = _._hash_for_cache_key(cache_key)

            # Verify hash is deterministic
            assert expected_hash == hashlib.sha256(cache_key.encode('utf-8')).hexdigest()[:16]

            # Store and retrieve should work with hash-based lookup
            result   = _.store_html(url, "test content")
            cache_id = result.get('cache_id' )
            retrieved = _.retrieve_html(url)
            assert retrieved == "test content"

            assert  _.cache_client.delete_by_id(cache_id).get('deleted_count') == 9
