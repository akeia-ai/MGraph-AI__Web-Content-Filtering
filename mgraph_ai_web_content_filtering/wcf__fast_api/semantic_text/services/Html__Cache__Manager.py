import hashlib
from typing                                                                                     import Dict, Optional

from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path

from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.config.consts__Semantic_Text import CACHE_PREFIX__SITES, FILE_ID__HTML__RAW__CONTENT, FILE_ID__HTML__RAW__DICT, \
    FILE_ID__HTML__TEXT_NODES, FILE_ID__HTML__TEXT_RATINGS
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                        import Safe_Str__Url
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.services.Cache__Client         import Cache__Client
from osbot_utils.utils.Http import url_join_safe


class Html__Cache__Manager(Type_Safe):                                          # Manages HTML caching via cache.dev.mgraph.ai
    cache_client : Cache__Client                                                # REST client for cache service    
    
    def namespace(self):
        return self.cache_client.namespace
    
    def _cache_key_for_url(self, url    : Safe_Str__Url,
                                 prefix : Safe_Str__File__Path = '',
                                 suffix : Safe_Str__File__Path = '',
                           ) -> str: # Generate semantic cache key from URL
        url_str = str(url)
        if url_str.startswith('https://'):
            url_str = url_str[8:]
        elif url_str.startswith('http://'):
            url_str = url_str[7:]
        
        if url_str.startswith('www.'):
            url_str = url_str[4:]
        cache_key = url_str
        if prefix:
            cache_key = url_join_safe(prefix, url_str)
        if suffix:
            cache_key = url_join_safe(cache_key, suffix)
        return cache_key.rstrip('/')
    
    def _hash_for_cache_key(self, cache_key: str) -> str:                      # Calculate hash from cache_key (same as cache service does)
        return hashlib.sha256(cache_key.encode('utf-8')).hexdigest()[:16]      # 16 char hash matching cache service
    
    def store_html(self, url: Safe_Str__Url, html: str) -> Dict:               # Store raw HTML for a URL
        cache_key = self._cache_key_for_url(url, prefix=CACHE_PREFIX__SITES)
        file_id   = FILE_ID__HTML__RAW__CONTENT
        result    = self.cache_client.store_string(data      = html            ,
                                                   file_id   = file_id         ,
                                                   cache_key = cache_key       ,
                                                   strategy  = "semantic_file" ,
                                                   namespace = self.namespace())
        return result
    
    def retrieve_html(self, url: Safe_Str__Url) -> Optional[str]:              # Retrieve raw HTML for a URL
        cache_key  = self._cache_key_for_url(url,CACHE_PREFIX__SITES )
        cache_hash = self._hash_for_cache_key(cache_key)                        # Calculate hash from cache_key
        
        cached_entry = self.cache_client.retrieve_by_hash(cache_hash, namespace=self.namespace())

        if cached_entry and cached_entry.get('status') != 'not_found':         # Check for valid result
            return cached_entry.get('data')
        return None
    
    def store_html_dict(self, url: Safe_Str__Url, html_dict: Dict) -> Dict:    # Store HTML dict representation
        cache_key = self._cache_key_for_url(url, CACHE_PREFIX__SITES)
        file_id   = FILE_ID__HTML__RAW__DICT
        result    = self.cache_client.store_json(data      = html_dict   ,
                                                 cache_key = cache_key   ,
                                                 file_id   = file_id     ,
                                                 strategy  = "semantic_file",
                                                 namespace = self.namespace())
        return result
    
    def retrieve_html_dict(self, url: Safe_Str__Url) -> Optional[Dict]:        # Retrieve HTML dict for a URL
        cache_key  = self._cache_key_for_url(url, CACHE_PREFIX__SITES)
        cache_hash = self._hash_for_cache_key(cache_key)
        
        cached_entry = self.cache_client.retrieve_json_by_hash(cache_hash, namespace=self.namespace())
        
        if cached_entry and cached_entry.get('status') != 'not_found':
            return cached_entry
        return None
    
    def store_text_nodes(self, url: Safe_Str__Url, text_nodes: Dict) -> Dict:  # Store extracted text nodes
        cache_key = self._cache_key_for_url(url, CACHE_PREFIX__SITES)
        file_id   = FILE_ID__HTML__TEXT_NODES
        result    = self.cache_client.store_json(data      = text_nodes ,
                                                 cache_key = cache_key  ,
                                                 file_id   = file_id    ,
                                                 strategy  = "semantic_file",
                                                 namespace = self.namespace())
        return result
    
    def retrieve_text_nodes(self, url: Safe_Str__Url) -> Optional[Dict]:       # Retrieve text nodes for a URL
        cache_key  = self._cache_key_for_url(url, CACHE_PREFIX__SITES)
        cache_hash = self._hash_for_cache_key(cache_key)
        
        cached_entry = self.cache_client.retrieve_json_by_hash(cache_hash, namespace=self.namespace())
        
        if cached_entry and cached_entry.get('status') != 'not_found':
            return cached_entry
        return None
    
    def store_ratings(self, url          : Safe_Str__Url ,                     # Store LLM ratings for text nodes
                            model       : str             ,
                            ratings     : Dict
                      ) -> Dict:
        cache_key = self._cache_key_for_url(url, prefix=CACHE_PREFIX__SITES, suffix=f'ratings/{model}')
        file_id   = FILE_ID__HTML__TEXT_RATINGS
        result    = self.cache_client.store_json(data      = ratings        ,
                                                 cache_key = cache_key      ,
                                                 file_id   = file_id        ,
                                                 strategy  = "semantic_file",
                                                 namespace = self.namespace())
        return result

    # todo: fix the logic in this workflow (since this is not currently capturing the file, since we used file file id)
    #       what we need to do is to centrallise the creation of these paths
    def retrieve_ratings(self, url: Safe_Str__Url, model: str) -> Optional[Dict]:  # Retrieve ratings for URL and model
        cache_key  = self._cache_key_for_url(url, prefix=CACHE_PREFIX__SITES, suffix=f'ratings/{model}')
        cache_hash = self._hash_for_cache_key(cache_key)
        
        cached_entry = self.cache_client.retrieve_json_by_hash(cache_hash, namespace=self.namespace())
        
        if cached_entry and cached_entry.get('status') != 'not_found':
            return cached_entry
        return None
    
    def has_cached_html(self, url: Safe_Str__Url) -> bool:                     # Check if HTML is cached for URL
        cache_key  = self._cache_key_for_url(url, CACHE_PREFIX__SITES)
        cache_hash = self._hash_for_cache_key(cache_key)
        return self.cache_client.exists(cache_hash, namespace=self.namespace())
    
    def has_cached_html_dict(self, url: Safe_Str__Url) -> bool:                # Check if HTML dict is cached
        cache_key  = self._cache_key_for_url(url, CACHE_PREFIX__SITES)
        cache_hash = self._hash_for_cache_key(cache_key)
        return self.cache_client.exists(cache_hash, namespace=self.namespace())
    
    def has_cached_text_nodes(self, url: Safe_Str__Url) -> bool:               # Check if text nodes are cached
        cache_key  = self._cache_key_for_url(url, CACHE_PREFIX__SITES)
        cache_hash = self._hash_for_cache_key(cache_key)
        return self.cache_client.exists(cache_hash, namespace=self.namespace())
    
    def has_cached_ratings(self, url: Safe_Str__Url, model: str) -> bool:      # Check if ratings are cached
        cache_key  = self._cache_key_for_url(url, prefix=CACHE_PREFIX__SITES, suffix=f'ratings/{model}')
        cache_hash = self._hash_for_cache_key(cache_key)
        return self.cache_client.exists(cache_hash, namespace=self.namespace())