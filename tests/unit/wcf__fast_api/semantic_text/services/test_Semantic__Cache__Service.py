import pytest
import time
from unittest                                                                                           import TestCase
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.schemas.Schema__Cache__Common_Elements import Schema__Cache__Common_Elements
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.schemas.Schema__Cache__Page_Data       import Schema__Cache__Page_Data
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.schemas.Schema__Cache__Site_Manifest   import Schema__Cache__Site_Manifest
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.services.Cache__Client                 import Cache__Client
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.services.Semantic__Cache__Service      import Semantic__Cache__Service
from osbot_utils.testing.__                                                                             import __, __SKIP__
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.utils.Misc                                                                             import is_guid
from osbot_utils.utils.Objects                                                                          import base_classes
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations                           import Html__Transformations, WEBSITE_URL__DEFAULT_SITE
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Display_Name               import Safe_Str__Display_Name
from osbot_utils.utils.Env                                                                              import get_env, load_dotenv
from osbot_utils.utils.Dev import pprint

class test_Semantic__Cache__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                              # ONE-TIME expensive setup
        pytest.skip("needs testing")
        load_dotenv()
        cls.service  = Semantic__Cache__Service()                                    # Service initialization
        cls.test_url = WEBSITE_URL__DEFAULT_SITE                                     # Default test URL

    def test__init__(self):                                                          # Test service initialization with v2 components
        with self.service as _:
            assert type(_)                      is Semantic__Cache__Service
            assert base_classes(_)              == [Type_Safe, object]
            assert type(_.cache_client)         is Cache__Client
            assert type(_.html_transformations) is Html__Transformations

    def test_calculate_page_hash(self):                                                 # Test page hash calculation (unchanged)
        with self.service as _:
            url1  = "https://example.com/page"                                          # Test basic URL
            hash1 = _.calculate_page_hash(url1)
            hash2 = _.calculate_page_hash(url1)                                         # Same URL should produce same hash
            url3  = "https://example.com/other"                                         # Different URL should produce different hash
            hash3 = _.calculate_page_hash(url3)

            assert type(hash1) is str
            assert len(hash1)  == 16                                                    # 16 char hash
            assert hash1 == hash2                                                       # Deterministic
            assert hash3 != hash1

    def test_create_page_path(self):                                                     # Test semantic page path creation
        with self.service as _:
            url  = "https://example.com/article"                                        # Simple path
            path = _.create_page_path(url)
            assert path == "article"

            url  = "https://example.com/news/tech/ai"                                   # Path with multiple segments
            path = _.create_page_path(url)
            assert path == "news_tech_ai"                                               # Slashes replaced with underscores

            url  = "https://example.com/page?id=123&type=post"                          # Path with query string
            path = _.create_page_path(url)
            assert path.startswith("page_q")                                            # Query hash appended
            assert len(path.split("_q")[1]) == 8                                        # 8 char query hash

            url  = "https://example.com/"                                               # Empty path (homepage)
            path = _.create_page_path(url)
            assert path == "index"

    def test_create_page_path__long_urls(self):                                      # Test handling of very long URLs
        with self.service as _:
            long_path = "category/" * 50 + "article"                                 # Create URL with very long path
            url = f"https://example.com/{long_path}"

            path = _.create_page_path(url)

            assert len(path) <= 133                                                  # Max 100 + 33 for hash
            assert "__" in path                                                      # Contains truncation marker

            path2 = _.create_page_path(url)                                          # Verify deterministic
            assert path == path2

    def test_extract_domain(self):                                                   # Test domain extraction
        with self.service as _:
            assert _.extract_domain("https://example.com/page") == "example.com"     # Test various URL formats
            assert _.extract_domain("http://sub.example.com"  ) == "sub.example.com"
            assert _.extract_domain("https://bbc.co.uk/news"  ) == "bbc.co.uk"

            domain = _.extract_domain("https://test.com")                           # Verify type safety
            assert type(domain) is Safe_Str__Display_Name

    def test_get_site_manifest__new(self):                                           # Test creating new site manifest
        with self.service as _:
            domain   = Safe_Str__Display_Name("test.example.com")
            manifest = _.get_site_manifest(domain)

            assert type(manifest) is Schema__Cache__Site_Manifest                   # Verify new manifest created
            assert manifest.obj() == __(total_unique_hashes  = 0       ,
                                        pages_processed      = 0       ,
                                        common_elements_hash = None    ,
                                        bloom_filter_hash    = None    ,
                                        pages_index_hash     = None    ,
                                        domain               = domain  ,
                                        last_updated         = __SKIP__)


    def test_save_site_manifest(self):                                               # Test saving site manifest with semantic path
        with (self.service as _):
            manifest = Schema__Cache__Site_Manifest(domain              = "test.com",
                                                    total_unique_hashes = 100       ,
                                                    pages_processed     = 5         )

            result__save = _.save_site_manifest(manifest)
            cache_id     = result__save.get('cache_id')
            cache_hash   = result__save.get('hash'    )
            namespace    = result__save.get('namespace' )
            assert is_guid(cache_id) is True
            assert cache_hash        == '1f76dabaf4bffdc8'
            assert namespace         == 'semantic-html'

            result__delete = _.cache_client.delete_by_id(cache_id=cache_id)
            assert result__delete.get('deleted_count') == 9
            assert 'data/semantic-file/sites/test.com/manifest/manifest.json' in result__delete.get('deleted_paths')


    def test_get_page_data__not_found(self):                                         # Test retrieving non-existent page data
        with self.service as _:
            url    = "https://example.com/missing"
            result = _.get_page_data(url)
            assert result is None                                                    # Should return None for not found

    def test_save_page_data(self):                                                   # Test saving page data under site folder
        with self.service as _:
            page_data = Schema__Cache__Page_Data(url            = "https://test.com/article"                 ,
                                                 page_hash      = "aaaaabbbbb"                               ,
                                                 total_elements = 50                                         ,
                                                 unique_hashes  = ["aaaaabbbb1", "aaaaabbbb2", "aaaaabbbb3"] )

            result = _.save_page_data(page_data)
            cache_id = result.get('cache_id')
            assert is_guid(cache_id) is True

            result__delete = _.cache_client.delete_by_id(cache_id=cache_id)
            assert result__delete.get('deleted_count') == 9
            assert 'data/semantic-file/sites/test.com/pages/article/data/data.json' in result__delete.get('deleted_paths')

    def test_get_common_elements__new(self):                                         # Test retrieving non-existent common elements
        with self.service as _:
            domain = Safe_Str__Display_Name("new.example.com")
            result = _.get_common_elements(domain)
            assert result is None                                                    # Should return None if not found

    def test_save_common_elements(self):                                             # Test saving common elements
        with self.service as _:

            common  = Schema__Cache__Common_Elements(domain       = "test.com"                               ,
                                                     common_hashes= {"1aaaabbbb1", "2aaaabbbb2", "3aaaabbbb3"})
            result   = _.save_common_elements(common)
            cache_id = result.get('cache_id')
            assert is_guid(cache_id) is True

            result__delete = _.cache_client.delete_by_id(cache_id=cache_id)
            assert result__delete.get('deleted_count')                    == 9
            assert 'data/semantic-file/sites/test.com/common/common.json' in result__delete.get('deleted_paths')

    def test_process_url_with_a_bad_url(self):                               # Test processing URL with no cache
        with self.service as _:

            # Use a unique URL to ensure cache miss
            unique_url = f"https://test-{int(time.time())}.com/page"

            result = _.process_url_with_cache(unique_url)
            assert result.get('status') == 'error'
            assert 'HTTPSConnectionPool' in result.get('message')

    def test_process_url_with_cache__with_real_url(self):                            # Test with actual URL
        with self.service as _:

            result    = _.process_url_with_cache(WEBSITE_URL__DEFAULT_SITE)
            page_hash = result.get('page_hash')

            pprint(result)

            assert 'text_elements' in result                                        # Verify we got text elements
            assert type(result['text_elements']) is dict

            # Verify page path created
            assert 'page_path' in result
            assert result['page_path'] == "404"                                      # BBC 404 page

            # Verify domain extraction
            assert 'domain' in result
            assert 'bbc.co.uk' in str(result['domain'])

    def test_store_classifications(self):                                            # Test storing classification results
        with self.service as _:
            if not get_env('FAST_API__AUTH__API_KEY__VALUE'):
                pytest.skip("Cache service API key required")

            classifications = {
                "hash1": {"positivity": 0.8, "topic": "news"},
                "hash2": {"positivity": 0.3, "topic": "sports"},
                "hash3": {"positivity": 0.5, "topic": "tech"}
            }

            stored_ids = _.store_classifications(classifications)

            assert type(stored_ids) is list
            assert len(stored_ids) == 3                                              # One ID per classification

            for cache_id in stored_ids:
                assert type(cache_id) is str
                assert len(cache_id) > 0

    def test_get_cache_structure(self):                                              # Test cache structure visualization
        with self.service as _:
            domain = Safe_Str__Display_Name("example.com")

            structure = _.get_cache_structure(domain)

            assert structure['domain'] == domain
            assert 'structure' in structure
            assert 'manifest' in structure['structure']
            assert 'common_elements' in structure['structure']
            assert 'pages' in structure['structure']

            # Verify paths follow new organization
            assert structure['structure']['manifest'] == f"sites/{domain}/manifest/manifest.json"
            assert structure['structure']['common_elements'] == f"sites/{domain}/common/common.json"
            assert "sites/{domain}/pages/" in structure['structure']['pages']

    def test_process_url_with_cache__twice(self):                                    # Test cache improvement on second call
        with self.service as _:
            if not get_env('FAST_API__AUTH__API_KEY__VALUE'):
                pytest.skip("Cache service API key required")

            # Use a consistent URL for both calls
            test_url = "https://cache-test.example.com/article/test"

            # First call - likely cache miss
            result1 = _.process_url_with_cache(test_url)
            page_path = result1['page_path']

            # Store some classifications to populate cache
            if 'text_elements' in result1:
                sample_classifications = {}
                for hash_value in list(result1['text_elements'].keys())[:5]:        # Store first 5
                    sample_classifications[hash_value] = {
                        "positivity": 0.5,
                        "topic": "test"
                    }
                _.store_classifications(sample_classifications)

            # Second call - should have some cache hits
            result2 = _.process_url_with_cache(test_url)

            # Same page path
            assert result2['page_path'] == page_path

            # Should have same or better cache hit rate
            assert result2['cache_hit_rate'] >= result1['cache_hit_rate']

    def test_integration__complete_flow(self):                                       # Test complete processing flow with v2
        with self.service as _:
            if not get_env('FAST_API__AUTH__API_KEY__VALUE'):
                pytest.skip("Cache service API key required")

            # Process a URL
            url = WEBSITE_URL__DEFAULT_SITE
            result = _.process_url_with_cache(url)

            # Extract domain and page info
            domain = result['domain']
            page_path = result['page_path']

            # Verify site manifest was created/updated
            manifest = _.get_site_manifest(domain)
            assert manifest.pages_processed >= 1

            # Verify page data was stored
            page_data = _.get_page_data(url)
            if page_data:                                                            # May be None if storage failed
                assert page_data.url == url

            # Verify common elements were updated
            common = _.get_common_elements(domain)
            if common:
                assert common.total_pages >= 1

    def test_type_safety__url_handling(self):                                        # Test URL type conversion
        with self.service as _:
            # Safe_Str__Url handles various inputs
            result = _.process_url_with_cache("https://test.com")
            assert 'page_hash' in result
            assert 'page_path' in result

            # Very long URLs are handled
            long_url = "https://example.com/" + "path/" * 50 + "page"
            result = _.process_url_with_cache(long_url)
            assert 'page_hash' in result
            assert 'page_path' in result

    def test_semantic_paths__consistency(self):                                      # Test semantic path generation consistency
        with self.service as _:
            # Test various URL patterns produce expected paths
            test_cases = [
                ("https://example.com/", "index"),
                ("https://example.com/about", "about"),
                ("https://example.com/blog/post", "blog_post"),
                ("https://example.com/article?id=123", "article_q"),                 # Query adds hash suffix
                ("https://example.com/very/deep/nested/path", "very_deep_nested_path"),
            ]

            for url, expected_prefix in test_cases:
                path = _.create_page_path(url)
                assert path.startswith(expected_prefix)                              # May have query hash suffix

                # Verify deterministic
                path2 = _.create_page_path(url)
                assert path == path2

    def test_cache_organization(self):                                               # Test that cache is organized correctly
        with self.service as _:
            if not get_env('FAST_API__AUTH__API_KEY__VALUE'):
                pytest.skip("Cache service API key required")

            # Process a specific URL
            test_domain = "organization-test.com"
            test_url = f"https://{test_domain}/products/item"

            result = _.process_url_with_cache(test_url)

            # Verify the organization structure
            assert result['domain'] == test_domain
            assert result['page_path'] == "products_item"

            # Expected cache structure:
            # sites/organization-test.com/
            #   ├── manifest/manifest.json
            #   ├── common/common.json
            #   └── pages/products_item/data/data.json

            structure = _.get_cache_structure(test_domain)
            assert "sites/organization-test.com/manifest" in structure['structure']['manifest']
            assert "sites/organization-test.com/pages" in structure['structure']['pages']