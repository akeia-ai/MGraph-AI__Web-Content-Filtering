from typing                                                                                     import Dict, List, Any

from memory_fs.schemas.Safe_Str__Cache_Hash import Safe_Str__Cache_Hash

from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                            import Safe_UInt
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                        import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.identifiers.Timestamp_Now                         import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id                 import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Percentage_Exact import Safe_Float__Percentage_Exact


class Schema__Cache__Page_Data(Type_Safe):                                       # Complete cache data for a specific page
    url                 : Safe_Str__Url                                          # Original page URL
    page_hash           : Safe_Str__Cache_Hash                                   # Hash of URL for consistent identification
    extraction_timestamp: Timestamp_Now                                          # When content was extracted
    total_elements      : Safe_UInt                                              # Total text elements found
    unique_hashes       : List[Safe_Str__Cache_Hash]                             # List of unique text hashes
    hash_classifications: Dict[Safe_Str__Id, Dict[str, Any]]                     # Hash -> classification mapping           # todo: replace [str, Any] with strongly types
    cache_completeness  : Safe_Float__Percentage_Exact                           # Percentage of elements cached (0-100)

    # todo: remove this logic from this schema file
    def calculate_completeness(self) -> 'Schema__Cache__Page_Data':              # Calculate cache completeness percentage
        if self.total_elements > 0 and self.hash_classifications:
            cached_count = len(self.hash_classifications)
            self.cache_completeness = (cached_count / self.total_elements) * 100    # todo: review this value and see if we need it (i.e. does it add valu)
        return self

    def add_classification(self, hash_value  : str                            ,  # Add classification for a hash
                                 classification: Dict[str, Any]
                          ) -> 'Schema__Cache__Page_Data':
        self.hash_classifications[hash_value] = classification
        self.calculate_completeness()
        return self