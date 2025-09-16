import gzip

import pytest
from unittest                                                                                   import TestCase
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.config.consts__Semantic_Text   import CACHE_SERVICE_URL, ENV_VAR__API_KEY__SERVICE__CACHE__KEY_NAME
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.services.Cache__Client         import Cache__Client
from osbot_utils.testing.__                                                                     import __, __SKIP__
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid                           import Random_Guid
from osbot_utils.utils.Misc                                                                     import is_guid
from osbot_utils.utils.Objects                                                                  import base_classes, obj
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Key                import Safe_Str__Key
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                        import Safe_Str__Url
from osbot_utils.utils.Env                                                                      import get_env, load_dotenv


class test_Cache__Client(TestCase):

    @classmethod
    def setUpClass(cls):                                                              # ONE-TIME expensive setup
        load_dotenv()                                                                 # Load environment variables
        if not get_env(ENV_VAR__API_KEY__SERVICE__CACHE__KEY_NAME):
            pytest.skip("Tests requite service cache API key and value")
        cls.cache_client = Cache__Client()                                            # Create client once
        cls.test_data    = {'test_key': 'test_value', 'answer': 42}                   # Reusable test data

    def test__init__(self):                                                           # Test client initialization with v0.5.30 defaults
        with Cache__Client() as _:
            assert type(_)         is Cache__Client
            assert base_classes(_) == [Type_Safe, object]

            # Verify type safety of attributes
            assert type(_.base_url)  is Safe_Str__Url
            assert type(_.namespace) is Safe_Str__Key
            assert type(_.headers()) is dict

            # Verify v0.5.30 defaults
            assert _.base_url  == CACHE_SERVICE_URL
            assert _.namespace == "semantic-html"                                    # Single namespace for semantic HTML

            # Verify auth headers are set
            assert len(_.headers()) > 0                                                 # Headers should be populated

    def test__safe_path_key(self):                                                      # Test path truncation strategy
        with self.cache_client as _:
            short_path = "sites/example.com/pages/index"                                # Short path - should remain unchanged
            assert _._safe_path_key(short_path) == short_path

            # Long path - should truncate and add hash
            long_path = "a" * 250                                                       # Exceeds S3 key limits
            result = _._safe_path_key(long_path, max_length=200)

            assert len(result)                  <= 201                                  # Within limit # todo: see why it is 201 and not 200
            assert "__"                         in result                               # Contains separator
            assert result.startswith("a" * 167) is True                                 # Truncated portion
            assert len(result.split("__")[1])   == 32                                   # Hash portion

    def test__safe_path_key__consistency(self):                                         # Test deterministic hashing
        with self.cache_client as _:
            long_path = "sites/very-long-domain-name.com/pages/" + "x" * 200

            result1 = _._safe_path_key(long_path)                                       # Same path should produce same result
            result2 = _._safe_path_key(long_path)

            assert result1 == result2                                                   # Deterministic

            different_path = long_path + "y"                                            # Different path should produce different result
            result3 = _._safe_path_key(different_path)

            assert result3 != result1                                                   # Different hash for different path

    def test_store_json__semantic_file(self):                                           # Test JSON storage with semantic_file strategy
        with self.cache_client as _:
            cache_key = "sites/test.com/page-abc"
            file_id   = "manifest"

            result__store = _.store_json(data      = self.test_data ,
                                         cache_key = cache_key      ,
                                         file_id   = file_id        ,
                                         strategy  = "semantic_file")
            cache_id = result__store.get("cache_id")
            # Verify response structure for v0.5.30
            assert 'cache_id'                 in result__store
            assert 'hash'                     in result__store
            assert 'namespace'                in result__store
            assert 'paths'                    in result__store
            assert 'size'                     in result__store
            assert result__store['namespace'] == "semantic-html"
            result__delete = _.delete_by_id(cache_id=cache_id)
            assert result__delete.get('deleted_count') == 9


    def test_store_json__with_long_path(self):                                       # Test storage with path truncation
        with self.cache_client as _:

            # Create a very long cache key
            long_key = "sites/example.com/pages/" + "very_long_page_path_" * 20

            result = _.store_json(data      = self.test_data,
                                  cache_key = long_key,
                                  file_id   = "data",
                                  strategy  = "semantic_file")

            assert 'cache_id' in result                                              # Should succeed despite long path
            assert _.delete_by_id(cache_id=result.get('cache_id')).get('deleted_count') == 9

    def test_store_string__semantic_file(self):                                      # Test string storage with semantic path
        with self.cache_client as _:
            test_string = "This is test content for semantic storage"
            cache_key   = "sites/example.com/pages/article_123/content"

            result = _.store_string(data      = test_string     ,
                                    cache_key = cache_key       ,
                                    file_id   = "text"          ,
                                    strategy  = "semantic_file" )

            assert 'cache_id' in result
            assert 'paths'    in result
            assert _.delete_by_id(cache_id=result.get('cache_id')).get('deleted_count') == 9
    
    def test_store_binary__with_compression(self):                                   # Test binary storage with compression
        with self.cache_client as _:

            test_data   = b"Binary test data that will be compressed"
            compressed  = gzip.compress(test_data)
            cache_key   = "sites/example.com/bloom"

            result = _.store_binary(data             = compressed       ,
                                    cache_key        = cache_key        ,
                                    file_id          = "filter"         ,
                                    strategy         = "semantic_file"  ,
                                    content_encoding = "gzip"           )

            assert 'cache_id' in result
            assert 'size'     in result
            assert _.delete_by_id(cache_id=result.get('cache_id')).get('deleted_count') == 9

    def test_store_json__fallback_strategies(self):                                  # Test other strategies still work
        with self.cache_client as _:
            strategies = ["direct", "temporal", "temporal_latest"]

            for strategy in strategies:
                result = _.store_json(data     = self.test_data,
                                      strategy = strategy             )              # No cache_key for non-semantic strategies

                assert 'cache_id' in result
                assert 'hash'     in result
                assert _.delete_by_id(cache_id=result.get('cache_id')).get('deleted_count') > 8

    def test_retrieve_by_id(self):                                                   # Test retrieval by cache ID
        with self.cache_client as _:

            # First store something
            store_result = _.store_json(data      = self.test_data  ,
                                        cache_key = "test/retrieval",
                                        file_id   = "test_id"       ,
                                        strategy  = "semantic_file" )
            cache_id = store_result['cache_id']

            # Then retrieve it
            retrieved = _.retrieve_by_id(cache_id=cache_id)

            assert retrieved is not None
            assert 'data'     in retrieved
            assert 'metadata' in retrieved
            assert _.delete_by_id(cache_id=cache_id).get('deleted_count') > 8
            assert obj(retrieved) == __(data             = __( test_key         = 'test_value'      ,
                                                               answer           = 42                ),
                                        metadata         = __( cache_hash       = 'de28049828f02d82',
                                                               cache_key        = 'test/retrieval'  ,
                                                               cache_id         = cache_id          ,
                                                               content_encoding = None              ,
                                                               stored_at        = __SKIP__          ,
                                                               strategy         ='semantic_file'    ,
                                                               namespace        ='semantic-html'    ,
                                                               file_type        = 'json'            ),
                                        data_type         = 'json'                                   ,
                                        content_encoding = None                                      )

    def test_retrieve_json_by_id(self):                                              # Test JSON-specific retrieval
        with self.cache_client as _:
            if not get_env('FAST_API__AUTH__API_KEY__VALUE'):
                pytest.skip("Cache service API key required")

            store_result = _.store_json(data      = self.test_data  ,                # Store JSON data
                                        cache_key = "test/json"     ,
                                        file_id   = "json_test"     ,
                                        strategy  = "semantic_file" )
            cache_id = store_result['cache_id']

            retrieved = _.retrieve_json_by_id(cache_id=cache_id)                     # Retrieve as JSON

            assert retrieved == self.test_data                                       # Should match original data
            assert _.delete_by_id(cache_id=cache_id).get('deleted_count') > 8

    def test_retrieve_by_hash(self):                                                 # Test retrieval by hash
        with self.cache_client as _:

            # Store data with direct strategy (hash-based)
            store_result = _.store_json(data     = self.test_data,
                                        strategy = "direct"      )                  # Hash-based strategy
            hash_value = store_result['hash']

            # Retrieve by hash
            retrieved = _.retrieve_by_hash(cache_hash=hash_value)

            assert retrieved is not None
            assert 'data' in retrieved
            assert _.delete_by_id(cache_id=store_result.get('cache_id')).get('deleted_count') > 8

    def test_retrieve__not_found(self):                                              # Test retrieval of non-existent data
        with self.cache_client as _:

            result = _.retrieve_by_id(cache_id=Random_Guid())
            assert result  == {'message': 'Cache entry not found', 'status': 'not_found'}

            result = _.retrieve_by_hash(cache_hash="1f76dabaf4aaaaaa")
            assert result == {'message': 'Cache entry not found', 'status': 'not_found'}

    def test_exists(self):                                                           # Test existence check
        with self.cache_client as _:
            store_result = _.store_json(data     = self.test_data,                   # Store data using direct strategy
                                        strategy = "direct"  )
            hash_value = store_result['hash']

            assert _.exists(cache_hash=hash_value)                                            is True   # Check existence
            assert _.exists(cache_hash="1f76dabaf4aaaaaa")                                    is False
            assert _.delete_by_id(cache_id=store_result.get('cache_id')).get('deleted_count') > 8

    def test_delete_by_id(self):                                                     # Test deletion by ID
        with self.cache_client as _:
            if not get_env('FAST_API__AUTH__API_KEY__VALUE'):
                pytest.skip("Cache service API key required")

            # Store data
            store_result = _.store_json(data      = {'to_delete': True},
                                        cache_key = "test/delete",
                                        file_id   = "delete_me",
                                        strategy  = "semantic_file")
            cache_id = store_result['cache_id']

            delete_result = _.delete_by_id(cache_id=cache_id)                       # Delete it

            assert 'deleted' in delete_result or 'status' in delete_result

            # Verify it's gone
            retrieved = _.retrieve_by_id(cache_id=cache_id)
            assert retrieved == {'message': 'Cache entry not found', 'status': 'not_found'}

    def test_get_stats(self):                                                        # Test namespace statistics
        with self.cache_client as _:

            stats = _.get_stats()

            # Verify v0.5.30 stats structure
            assert 'namespace'        in stats
            assert 's3_bucket'        in stats
            assert 's3_prefix'        in stats
            assert 'total_files'      in stats or 'direct_files' in stats

    def test_list_file_ids(self):                                                    # Test listing file IDs
        with self.cache_client as _:
            result = _.list_file_ids()
            assert type(result) is list


    def test_list_file_hashes(self):                                                 # Test listing file hashes
        with self.cache_client as _:

            result = _.list_file_hashes()

            assert type(result) is list

    def test_type_safety__namespace(self):                                           # Test namespace type safety
        with self.cache_client as _:
            _.namespace = "test$namespace$123"                                       # Safe_Str__Key should sanitize special characters
            assert _.namespace == "test_namespace_123"                               # Special chars replaced

            # Test with raw string assignment
            _.namespace = 123
            assert type(_.namespace) is Safe_Str__Key                               # Auto-converted
            assert _.namespace == "123"

    def test_integration__semantic_storage_flow(self):                               # Test complete semantic storage flow
        with self.cache_client as _:

            domain = "test.example.com"

            manifest_data = { 'domain'              : domain,                       # Store site manifest
                              'total_unique_hashes' : 100   ,
                              'pages_processed'     : 5     }

            manifest_result = _.store_json( data      = manifest_data               ,
                                            cache_key = f"sites/{domain}/manifest"  ,
                                            file_id   = "manifest"                  ,
                                            strategy  = "semantic_file"             )

            page_data = { 'url'             : f"https://{domain}/page"  ,           # Store page data
                          'total_elements'  : 50                        ,
                          'classifications' : {}                        }

            page_result = _.store_json( data      = page_data                           ,
                                        cache_key = f"sites/{domain}/pages/index/data"  ,
                                        file_id   = "data"                              ,
                                        strategy  = "semantic_file"                     )

            common_data = { 'domain': domain,                                       # Store common elements
                            'common_hashes': ["hash1", "hash2"] }

            common_result = _.store_json(data      = common_data             ,
                                         cache_key = f"sites/{domain}/common",
                                         file_id   = "common"                ,
                                         strategy  = "semantic_file"         )

            cache_id__manifest_result   = manifest_result['cache_id']
            cache_id__common_result     = common_result  ['cache_id']
            cache_id__page_result       = page_result    ['cache_id']

            assert is_guid(cache_id__manifest_result)                                               # Verify all stored successfully
            assert is_guid(cache_id__common_result  )                                               #    where we received valid guids for each one
            assert is_guid(cache_id__page_result    )

            assert _.delete_by_id(cache_id=cache_id__manifest_result).get('deleted_count') > 8      # delete all 3 files
            assert _.delete_by_id(cache_id=cache_id__common_result  ).get('deleted_count') > 8
            assert _.delete_by_id(cache_id=cache_id__page_result    ).get('deleted_count') > 8