import hashlib
from typing                                                                                                 import Dict, List, Optional, Any
from urllib.parse                                                                                           import urlparse
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.schemas.Schema__Cache__Common_Elements     import Schema__Cache__Common_Elements
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.schemas.Schema__Cache__Page_Data           import Schema__Cache__Page_Data
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.schemas.Schema__Cache__Site_Manifest       import Schema__Cache__Site_Manifest
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                                    import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Display_Name                   import Safe_Str__Display_Name
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Extract_Text_Nodes                            import Html__Extract_Text_Nodes
from mgraph_ai_web_content_filtering.wcf__fast_api.core.Html__Transformations                               import Html__Transformations
from mgraph_ai_web_content_filtering.wcf__fast_api.semantic_text.services.Cache__Client                     import Cache__Client
from osbot_utils.utils.Dev import pprint


class Semantic__Cache__Service(Type_Safe):                                       # Orchestrates cache operations with semantic_file strategy
    cache_client         : Cache__Client                                         # Updated client for v0.5.30
    html_transformations : Html__Transformations                                 # HTML processing utilities

    def calculate_page_hash(self, url: str) -> str:                              # Generate deterministic hash for page identification (using hash from full URL including query params)
        parsed = urlparse(url)

        # Build cache key from URL components
        cache_key_parts = [ parsed.scheme,                                                          # http or https
                            parsed.netloc,                                                          # domain
                            parsed.path  ,                                                          # /wiki/September_15
                            parsed.query ]                                                          # all query parameters

        cache_key = "|".join(cache_key_parts)
        page_hash = hashlib.sha256(cache_key.encode()).hexdigest()[:16]                             # 16 char hash

        return page_hash

    # todo: replace str below with Safe_Str*
    def create_page_path(self, url: str) -> str:                                 # Create semantic path from URL (handling long paths)
        parsed = urlparse(url)

        path = parsed.path.strip('/').replace('/', '_')                         # Remove leading/trailing slashes and replace remaining with underscores

        if parsed.query:                                                        # Add query string hash if present
            query_hash = hashlib.sha256(parsed.query.encode()).hexdigest()[:8]
            path = f"{path}_q{query_hash}"

        if not path:                                                            # Handle empty paths
            path = "index"


        max_path_length = 100                                                    # Conservative limit for page paths # todo: move value to const
        if len(path) > max_path_length:                                          # Handle long paths using truncation + hash strategy
            path_hash = hashlib.sha256(path.encode()).hexdigest()[:32]
            path      = f"{path[:max_path_length-33]}__{path_hash}"

        return path

    def extract_domain(self, url: str) -> Safe_Str__Display_Name:               # Extract domain from URL
        parsed = urlparse(url)
        return Safe_Str__Display_Name(parsed.netloc)

    def get_site_manifest(self, domain: Safe_Str__Display_Name                   # Retrieve or create site manifest
                           ) -> Schema__Cache__Site_Manifest:
        cache_key  = f"sites/{domain}/manifest"
        cache_hash = hashlib.sha256(cache_key.encode('utf-8')).hexdigest()[:16]                             # Calculate hash from cache_key (same as cache service does)

        result = self.cache_client.retrieve_json_by_hash(cache_hash = cache_hash                 ,          # Try to retrieve by hash
                                                         namespace  = self.cache_client.namespace)
        if result.get('status') != 'not_found':                                                             # todo: find a better way to check if we got a valid result
            return Schema__Cache__Site_Manifest.from_json(result)

        return Schema__Cache__Site_Manifest(domain=domain)                                                  # Create new manifest if not found

    def save_site_manifest(self, manifest: Schema__Cache__Site_Manifest              # Save site manifest to cache
                            ):
        cache_key = f"sites/{manifest.domain}/manifest"                              # todo: refactor out the logic to create this path (i.e. it shouldn't be here)
        result    = self.cache_client.store_json(data      = manifest.json()   ,     # Store using semantic_file strategy
                                                 cache_key = cache_key         ,
                                                 file_id   = "manifest"        ,     # Consistent file ID
                                                 strategy  = "semantic_file"   )

        return result

    # todo: replace url with Safe_Str_*
    def get_page_data(self, url: Safe_Str__Url) -> Optional[Schema__Cache__Page_Data]:                    # Retrieve cached page data

        domain    = self.extract_domain(url)
        page_path = self.create_page_path(url)
        cache_key = f"sites/{domain}/pages/{page_path}/data"                                            # todo: refactor out this path creation logic

        cache_hash = hashlib.sha256(cache_key.encode('utf-8')).hexdigest()[:16]                         # Calculate hash from cache_key   # todo: move the 16 (hash value) to a const

        result = self.cache_client.retrieve_json_by_hash(cache_hash = cache_hash                 ,      # Try to retrieve by hash
                                                         namespace  = self.cache_client.namespace)

        if result.get('status') != 'not_found':                                                         # todo: find a better way to check if we got a valid result
            return Schema__Cache__Page_Data.from_json(result)

        return None                                                                                     # todo: see if we shouldn't be creating the page object here

    # todo: refactor the return str with a Safe_* class
    def save_page_data(self, page_data: Schema__Cache__Page_Data) -> dict:       # Save page data to cache
        domain    = self.extract_domain(page_data.url)
        page_path = self.create_page_path(page_data.url)

        cache_key = f"sites/{domain}/pages/{page_path}/data"                    # Store under site's pages folder

        result = self.cache_client.store_json(data      = page_data.json(),
                                              cache_key = cache_key       ,
                                              file_id   = "data"          ,
                                              strategy  = "semantic_file" )

        return result

    def get_common_elements(self, domain: Safe_Str__Display_Name                 # Retrieve common elements for a domain
                       ) -> Optional[Schema__Cache__Common_Elements]:

        cache_key = f"sites/{domain}/common"                                    # todo: refactor out this path creation

        # Calculate hash from cache_key
        cache_hash = hashlib.sha256(cache_key.encode('utf-8')).hexdigest()[:16]     # todo: refactor out this path hash creation

        # Try to retrieve by hash
        result = self.cache_client.retrieve_json_by_hash(cache_hash = cache_hash                 ,
                                                         namespace  = self.cache_client.namespace)

        if result.get('status') != 'not_found':                                                             # todo: find a better way to check if we got a valid result
            return Schema__Cache__Common_Elements.from_json(result)

        return None

    def save_common_elements(self, common: Schema__Cache__Common_Elements) -> Dict: # Save common elements
        cache_key = f"sites/{common.domain}/common"

        result = self.cache_client.store_json(data      = common.json()  ,
                                              cache_key = cache_key      ,
                                              file_id   = "common"       ,
                                              strategy  = "semantic_file")

        return result

    def process_url_with_cache(self, url: Safe_Str__Url) -> Dict[str, Any]:                                 # Main entry point for cached processing
        domain    = self.extract_domain     (url)                                                           # Step 1: Extract domain and page info
        page_path = self.create_page_path   (url)
        page_hash = self.calculate_page_hash(url)                                                           # Still useful for quick lookups

        page_data = self.get_page_data(url)                                                                 # Step 2: Check if we have this exact page cached

        if page_data and page_data.cache_completeness == 100.0:
            return { 'status'        : 'cache_hit'                      ,                                   # todo: return a Type_Safe class
                     'cache_hit_rate': 100.0                            ,
                     'page_hash'     : page_hash                        ,
                     'page_path'     : page_path                        ,
                     'domain'        : domain                           ,
                     'classifications': page_data.hash_classifications  ,
                     'total_elements': page_data.total_elements         }

        html_extract    = Html__Extract_Text_Nodes(url                  = url                      ,        # Step 3: Extract text nodes from page
                                                   html_transformations = self.html_transformations)
        try:
            text_elements   = html_extract.extract()
        except Exception as error:
            return { 'status' : 'error' , 'message' : f'in process_url_with_cache, we got error: {error.args[0]}' }     # todo: find a better way to handle these error (which should be returned on Type_Safe class

        site_manifest   = self.get_site_manifest(domain)                                                    # Step 4: Get site manifest and common elements
        common_elements = self.get_common_elements(domain)

        cached_classifications = {}                                                                         # Step 5: Check cache for each hash
        uncached_hashes        = []

        if common_elements and common_elements.classifications:                                             # Check common elements first
            for hash_value in text_elements.keys():
                if hash_value in common_elements.classifications:
                    cached_classifications[hash_value] = common_elements.classifications[hash_value]

        for hash_value in text_elements.keys():                                                             # Check individual hash cache for remaining elements
            if hash_value not in cached_classifications:
                if self.cache_client.exists(hash_value):                                                    # Store individual classifications using direct strategy
                    cached_data = self.cache_client.retrieve_json_by_hash(hash_value)
                    if cached_data:
                        cached_classifications[hash_value] = cached_data
                else:
                    uncached_hashes.append(hash_value)

        total_hashes   = len(text_elements)                                                                 # Calculate cache hit rate
        cached_count   = len(cached_classifications)
        cache_hit_rate = (cached_count / total_hashes * 100) if total_hashes > 0 else 0

        if not page_data:                                                                                   # Step 6: Create or update page data
            page_data = Schema__Cache__Page_Data(url       = url      ,
                                                 page_hash = page_hash)

        page_data.total_elements       = total_hashes
        page_data.unique_hashes        = list(text_elements.keys())
        page_data.hash_classifications = cached_classifications
        page_data.calculate_completeness()

        self.save_page_data(page_data)                                                                      # Save page data

        site_manifest.increment_pages()                                                                     # Update site manifest
        site_manifest.update_hashes(total_hashes)
        self.save_site_manifest(site_manifest)

        if not common_elements:                                                                             # Update common elements if we have new hashes
            common_elements = Schema__Cache__Common_Elements(domain=domain)

        common_elements.add_page_hashes(set(text_elements.keys()))
        self.save_common_elements(common_elements)

        return { 'status'         : 'partial_cache' if cached_count > 0 else 'cache_miss',                  # todo: refactor to Type_Safe class
                 'cache_hit_rate' : cache_hit_rate          ,
                 'page_hash'      : page_hash               ,
                 'page_path'      : page_path               ,
                 'domain'         : domain                  ,
                 'total_elements' : total_hashes            ,
                 'cached_elements': cached_count            ,
                 'uncached_hashes': uncached_hashes         ,
                 'text_elements'  : text_elements           ,
                 'classifications': cached_classifications  }

    def store_classifications(self, classifications: Dict[str, Dict[str, Any]]   # Store classification results
                             ) -> List[str]:
        stored_ids = []
        # todo: review this use of direct strategy, since it might be better to keep these files under the site or pages path/folder
        for hash_value, classification in classifications.items():
            result = self.cache_client.store_json(data     = classification,                # Store individual classifications using direct strategy (hash-based)
                                                  strategy = "direct",                      # Direct for individual hashes
                                                  namespace= self.cache_client.namespace   )
            cache_id = result.get('cache_id')
            if cache_id:
                stored_ids.append(cache_id)

        return stored_ids

    def get_cache_structure(self, domain: Safe_Str__Display_Name) -> Dict[str, Any]:   # Helper method to visualize cache structure for a domain
        return { 'domain'       : domain,
                 'structure'    : { 'manifest'       : f"sites/{domain}/manifest/manifest.json"             ,           # todo: replace with Type_Safe class
                                    'common_elements': f"sites/{domain}/common/common.json"                 ,
                                    'bloom_filter'   : f"sites/{domain}/bloom/filter.b64"                   ,
                                    'pages'          : f"sites/{domain}/pages/{{page_path}}/data/data.json" },
                 'description'  : 'All page data is organized under the site folder for better organization'}