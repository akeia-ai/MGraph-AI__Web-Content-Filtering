from unittest                                                                                   import TestCase

import pytest
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.config.consts__Semantic_Text   import ENV_VAR__API_KEY__SERVICE__CACHE__KEY_NAME
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.services.Html__Cache__Manager  import Html__Cache__Manager
from osbot_utils.helpers.html.schemas.Schema__Html_Document                                     import Schema__Html_Document
from osbot_utils.utils.Env                                                                      import get_env
from osbot_utils.utils.Misc                                                                     import list_set
from osbot_utils.utils.Objects                                                                  import base_classes
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                        import Safe_Str__Url
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations                   import Html__Transformations, WEBSITE_URL__DEFAULT_SITE
from tests.unit.wcf__objs_for_tests                                                             import setup_local_stack

class test_Html__Transformations(TestCase):

    @classmethod
    def setUpClass(cls):                                                        # ONE-TIME expensive setup
        if not get_env(ENV_VAR__API_KEY__SERVICE__CACHE__KEY_NAME):
            pytest.skip("Tests requite service cache API key and value")
        setup_local_stack()                                                     # LocalStack setup (2-3s)
        cls.html_transformations = Html__Transformations()                      # Initialize once with cache
        cls.test_url = Safe_Str__Url(WEBSITE_URL__DEFAULT_SITE)                 # Use default test URL

    def test__init__(self):                                                     # Test auto-initialization
        with Html__Transformations() as _:
            assert type(_)         is Html__Transformations
            assert base_classes(_) == [Type_Safe, object]
            assert type(_.cache_manager) is Html__Cache__Manager                # Auto-initialized
            assert _.use_cache     is True                                      # Caching enabled by default
            assert _.force_reload  is False                                     # No forced reload by default

    def test_url_to_html(self):                                                 # Test HTML fetching with cache
        with self.html_transformations as _:
            # First call - fetches and caches
            html1 = _.url__to__html(self.test_url)
            assert len(html1) > 10000                                           # BBC 404 page is substantial
            assert '<title>' in html1                                           # Valid HTML

            # Second call - should use cache (faster)
            html2 = _.url__to__html(self.test_url)
            assert html2 == html1                                               # Same content from cache

            # Force reload
            html3 = _.url__to__html(self.test_url, reload=True)
            assert html3 == html1                                               # Content should be same (stable page)


    def test_url_to_html_dict(self):                                            # Test dict conversion with cache
        with self.html_transformations as _:
            # First call - generates and caches
            html_dict1 = _.url__to__html_dict(self.test_url)
            assert type(html_dict1) is dict
            assert list_set(html_dict1) == ['attrs', 'nodes', 'tag']            # Expected structure

            # Second call - from cache
            html_dict2 = _.url__to__html_dict(self.test_url)
            assert html_dict2 == html_dict1                                     # Same from cache

    def test_url_to_html_dict__force_reload(self):                              # Test force reload behavior
        with Html__Transformations() as _:
            _.force_reload = True                                               # Force all reloads

            # Should bypass cache even if exists
            html_dict = _.url__to__html_dict(self.test_url)
            assert type(html_dict) is dict
            # Note: Can't easily verify it didn't use cache, but force_reload ensures it

    def test_url__to__html_dict__to__html(self):                                # Test round-trip conversion
        with self.html_transformations as _:
            html_roundtrip = _.url__to__html_dict__to__html(self.test_url)
            assert '<html' in html_roundtrip                                    # Valid HTML
            assert '</html>' in html_roundtrip
            # Round-trip should preserve structure
            assert len(html_roundtrip) > 1000

    def test_url__to__html_dict__to__lines(self):                               # Test lines output
        with self.html_transformations as _:
            lines = _.url__to__html_dict__to__lines(self.test_url)
            assert '└── TEXT: BBC - 404: Not Found' in lines                    # Expected text in tree view
            assert type(lines) is str
            assert '\n' in lines                                                # Multi-line output

    def test_url__to__html_document(self):                                      # Test document structure
        with self.html_transformations as _:
            doc = _.url__to__html_document(self.test_url)
            assert type(doc) is Schema__Html_Document                           # Returns Schema__Html_Document

    def test_cache_integration(self):                                           # Test full cache integration
        with Html__Transformations() as transformer1:

            # First transformer caches content
            html1 = transformer1.url__to__html(self.test_url)
            dict1 = transformer1.url__to__html_dict(self.test_url)

        # Different instance should get cached content
        with Html__Transformations() as transformer2:

            # Should get from cache (no network call)
            html2 = transformer2.url__to__html(self.test_url)
            dict2 = transformer2.url__to__html_dict(self.test_url)

            assert html2 == html1                                               # Same cached HTML
            assert dict2 == dict1                                               # Same cached dict