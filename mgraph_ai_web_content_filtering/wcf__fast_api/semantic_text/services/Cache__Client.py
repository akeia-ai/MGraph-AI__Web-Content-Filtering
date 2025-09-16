import hashlib
import requests
from typing                                                                                             import Dict, Any, Optional
from requests                                                                                           import RequestException
from osbot_utils.decorators.methods.cache_on_self                                                       import cache_on_self
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id                         import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                      import Safe_Str__Hash
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.config.consts__Semantic_Text           import CACHE_SERVICE_URL, CACHE_NAMESPACE_DEFAULT, CACHE_STRATEGY_DEFAULT, ENV_VAR__API_KEY__SERVICE__CACHE__KEY_NAME, ENV_VAR__API_KEY__SERVICE__CACHE__KEY_VALUE
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.schemas.Enum__Cache__Store__Strategy   import Enum__Cache__Store__Strategy
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Key                        import Safe_Str__Key
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                                import Safe_Str__Url
from osbot_utils.utils.Env                                                                              import get_env



class Cache__Client(Type_Safe):                                                 # REST client for cache.dev.mgraph.ai service v0.5.30
    base_url  : Safe_Str__Url = CACHE_SERVICE_URL                                # Base URL for cache service
    namespace : Safe_Str__Key = CACHE_NAMESPACE_DEFAULT                          # Namespace for data isolation    

    @cache_on_self    
    def headers(self):        
        api_key_name  = get_env(ENV_VAR__API_KEY__SERVICE__CACHE__KEY_NAME )
        api_key_value = get_env(ENV_VAR__API_KEY__SERVICE__CACHE__KEY_VALUE)
        if not api_key_name or not api_key_value:
            raise ValueError("in Cache__Client, api_key_name and api_key_value are required")
        return  {api_key_name: api_key_value}
    
    def _safe_path_key(self, path: str, max_length: int = 200) -> str:          # Create safe path key that won't exceed S3 limits
        if len(path) <= max_length:                                             # Handle long paths by truncating and adding hash suffix
            return path
        
        # For long paths: truncate and add hash to ensure uniqueness
        truncate_at = max_length - 33                                            # Leave room for "__" + 32 char hash
        path_hash = hashlib.sha256(path.encode()).hexdigest()[:32]
        return f"{path[:truncate_at]}__{path_hash}"
    
    def store_json(self, data       : Dict[str, Any]                                       ,  # Store JSON data with semantic path
                         cache_key  : Safe_Str__Hash               = None                  ,  # Semantic path for organization
                         file_id    : Safe_Str__Id                 = None                  ,  # Custom file identifier
                         strategy   : Enum__Cache__Store__Strategy = CACHE_STRATEGY_DEFAULT,
                         namespace  : Safe_Str__Key                = None
                    ) -> Dict[str, Any]:

        namespace = namespace or self.namespace
        if strategy == "semantic_file" and cache_key:                                           # Use new path-based endpoint for semantic_file
            safe_key = self._safe_path_key(cache_key)
            url = f"{self.base_url}/{namespace}/{strategy}/store/json/{safe_key}"
        else:
            url = f"{self.base_url}/{namespace}/{strategy}/store/json"                          # Use basic endpoint for other strategies

        params   = {"file_id": file_id} if file_id else {}                                        # Add file_id as query parameter if provided
        response = requests.post(url, json=data, headers=self.headers(), params=params)
        if response.status_code != 200:
            raise Exception(response.text)
            #response.raise_for_status()
        return response.json()
    
    def store_string(self, data       : str                                                  ,     # Store string data with semantic path
                           cache_key  : Safe_Str__Hash               = None                  ,
                           file_id    : Safe_Str__Id                 = None                  ,
                           strategy   : Enum__Cache__Store__Strategy = CACHE_STRATEGY_DEFAULT,
                           namespace  : Safe_Str__Key                = None
                      ) -> Dict[str, Any]:
        namespace = namespace or self.namespace
        
        if strategy == "semantic_file" and cache_key:
            safe_key = self._safe_path_key(cache_key)
            url = f"{self.base_url}/{namespace}/{strategy}/store/string/{safe_key}"
        else:
            url = f"{self.base_url}/{namespace}/{strategy}/store/string"

        params = {"file_id": file_id} if file_id else {}
        req_headers = self.headers().copy()                                                           # Add content-encoding header if specified
        req_headers["Content-Type"] = "text/plain"
        response = requests.post(url, data=data, headers=req_headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def store_binary(self, data            : bytes                                 ,  # Store binary data with semantic path
                           cache_key       : Safe_Str__Hash               = None                    ,
                           file_id         : Safe_Str__Id                 = None                    ,
                           strategy        : Enum__Cache__Store__Strategy = CACHE_STRATEGY_DEFAULT  ,
                           namespace       : Safe_Str__Key                = None                    ,
                           content_encoding: Safe_Str__Id                 = None
                      ) -> Dict[str, Any]:
        namespace = namespace or self.namespace
        
        if strategy == "semantic_file" and cache_key:
            safe_key = self._safe_path_key(cache_key)
            url = f"{self.base_url}/{namespace}/{strategy}/store/binary/{safe_key}"
        else:
            url = f"{self.base_url}/{namespace}/{strategy}/store/binary"
            
        params = {"file_id": file_id} if file_id else {}

        req_headers = self.headers().copy()                                                           # Add content-encoding header if specified
        if content_encoding:
            req_headers["Content-Encoding"] = content_encoding
        req_headers["Content-Type"] = "application/octet-stream"
        
        response = requests.post(url, data=data, headers=req_headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def retrieve_by_hash(self, cache_hash: str                                ,  # Retrieve data by its hash
                               namespace  : Optional[Safe_Str__Key] = None
                          ) -> Optional[Dict[str, Any]]:
        namespace = namespace or self.namespace
        url = f"{self.base_url}/{namespace}/retrieve/hash/{cache_hash}"
        
        try:
            response = requests.get(url, headers=self.headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def retrieve_by_id(self, cache_id  : str                                  ,  # Retrieve data by cache ID
                             namespace : Optional[Safe_Str__Key] = None
                       ) -> Optional[Dict[str, Any]]:
        namespace = namespace or self.namespace
        url = f"{self.base_url}/{namespace}/retrieve/{cache_id}"
        

        response = requests.get(url, headers=self.headers())
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise RequestException(response.text)
        return response.json()
    
    def retrieve_json_by_id(self, cache_id  : str                             ,  # Retrieve JSON data specifically
                                   namespace : Optional[Safe_Str__Key] = None
                            ) -> Optional[Dict[str, Any]]:
        namespace = namespace or self.namespace
        url = f"{self.base_url}/{namespace}/retrieve/{cache_id}/json"
        
        try:
            response = requests.get(url, headers=self.headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def retrieve_json_by_hash(self, cache_hash: str                           ,  # Retrieve JSON data by hash
                                     namespace : Optional[Safe_Str__Key] = None
                              ) -> Optional[Dict[str, Any]]:
        namespace = namespace or self.namespace
        url = f"{self.base_url}/{namespace}/retrieve/hash/{cache_hash}/json"
        
        try:
            response = requests.get(url, headers=self.headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def exists(self, cache_hash: str                                          ,  # Check if hash exists in cache
                     namespace  : Optional[Safe_Str__Key] = None
               ) -> bool:
        namespace = namespace or self.namespace
        url = f"{self.base_url}/{namespace}/exists/hash/{cache_hash}"
        
        try:
            response = requests.get(url, headers=self.headers())
            response.raise_for_status()
            result = response.json()
            return result.get('exists', False)
        except requests.exceptions.HTTPError:
            return False
    
    def delete_by_id(self, cache_id  : str                                    ,  # Delete cache entry by ID
                           namespace : Optional[Safe_Str__Key] = None
                     ) -> Dict[str, Any]:
        namespace = namespace or self.namespace
        url = f"{self.base_url}/{namespace}/delete/{cache_id}"
        
        response = requests.delete(url, headers=self.headers())
        response.raise_for_status()
        return response.json()
    
    def get_stats(self, namespace: Optional[Safe_Str__Key] = None             # Get namespace statistics
                  ) -> Dict[str, Any]:
        namespace = namespace or self.namespace
        url = f"{self.base_url}/{namespace}/stats"
        
        response = requests.get(url, headers=self.headers())
        response.raise_for_status()
        return response.json()
    
    def list_file_ids(self, namespace: Optional[Safe_Str__Key] = None         # List all file IDs in namespace
                      ) -> Dict[str, Any]:
        namespace = namespace or self.namespace
        url = f"{self.base_url}/{namespace}/file-ids"
        
        response = requests.get(url, headers=self.headers())
        response.raise_for_status()
        return response.json()
    
    def list_file_hashes(self, namespace: Optional[Safe_Str__Key] = None      # List all file hashes in namespace
                         ) -> Dict[str, Any]:
        namespace = namespace or self.namespace
        url = f"{self.base_url}/{namespace}/file-hashes"
        
        response = requests.get(url, headers=self.headers())
        response.raise_for_status()
        return response.json()