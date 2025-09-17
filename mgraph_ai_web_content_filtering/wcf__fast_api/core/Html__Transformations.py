import requests
from typing                                                                                     import Dict, Optional
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.services.Html__Cache__Manager  import Html__Cache__Manager
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                        import Safe_Str__Url
from osbot_utils.helpers.html.transformers.Html__To__Html_Document                              import Html__To__Html_Document
from osbot_utils.helpers.html.transformers.Html_Dict__To__Html                                  import Html_Dict__To__Html
from osbot_utils.helpers.html.transformers.Html__To__Html_Dict                                  import Html__To__Html_Dict


WEBSITE_URL__DEFAULT_SITE = "https://www.bbc.co.uk/404"

class Html__Transformations(Type_Safe):                                         # HTML processing with cache service integration
    cache_manager  : Html__Cache__Manager                                       # Manages caching via cache.dev.mgraph.ai
    use_cache      : bool                   = True                               # Enable/disable caching (for testing)
    force_reload   : bool                   = False                              # Force refresh from source

    def default_headers(self):                                                  # Standard browser headers for requests
        headers = { 'User-Agent'               : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                    'Accept'                   : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Connection'               : 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'         }
        return headers

    def url__to__html(self, url: Safe_Str__Url, reload: bool = False) -> str:  # Fetch HTML with caching
        if self.use_cache and not (reload or self.force_reload):
            # Try to get from cache first
            cached_html = self.cache_manager.retrieve_html(url)
            if cached_html:
                return cached_html

        # Fetch from source
        response = requests.get(str(url), headers=self.default_headers())
        html     = response.text

        # Store in cache if enabled
        if self.use_cache:
            self.cache_manager.store_html(url, html)

        return html

    def url__to__html_dict(self, url: Safe_Str__Url, reload: bool = False) -> Dict:  # Convert URL to HTML dict representation
        if self.use_cache and not (reload or self.force_reload):
            # Try to get cached dict first
            cached_dict = self.cache_manager.retrieve_html_dict(url)
            if cached_dict:
                return cached_dict

        # Generate HTML dict
        html      = self.url__to__html(url, reload=reload)
        html_dict = Html__To__Html_Dict(html=html).convert()

        # Store in cache if enabled
        if self.use_cache:
            self.cache_manager.store_html_dict(url, html_dict)

        return html_dict

    def url__to__html_dict__to__html(self, url: Safe_Str__Url) -> str:         # Round-trip URL → dict → HTML
        html_dict      = self.url__to__html_dict(url=url)
        html_roundtrip = Html_Dict__To__Html(root=html_dict).convert()
        return html_roundtrip

    def url__to__html_dict__to__lines(self, url: Safe_Str__Url) -> str:        # Convert URL to printable lines
        html_dict = self.url__to__html_dict(url=url)
        html_converter = Html__To__Html_Dict(html='')  # Create instance for printing
        html_converter.root = html_dict
        lines = "\n".join(html_converter.print(just_return_lines=True))
        return lines

    def url__to__html_document(self, url: Safe_Str__Url) -> Dict:              # Convert URL to HTML document structure
        html          = self.url__to__html(url)
        html_document = Html__To__Html_Document(html=html).convert()
        return html_document

    def clear_cache_for_url(self, url: Safe_Str__Url):                         # Clear all cached data for a URL
        # In future, could add delete methods to cache service
        # For now, just set force_reload flag
        self.force_reload = True