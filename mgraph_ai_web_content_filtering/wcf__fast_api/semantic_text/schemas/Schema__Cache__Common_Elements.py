from memory_fs.schemas.Safe_Str__Cache_Hash                                                     import Safe_Str__Cache_Hash
from osbot_utils.type_safe.primitives.domains.numerical.safe_float.Safe_Float__Percentage_Exact import Safe_Float__Percentage_Exact
from osbot_utils.type_safe.primitives.core.Safe_UInt                                            import Safe_UInt
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Display_Name       import Safe_Str__Display_Name
from osbot_utils.type_safe.primitives.domains.identifiers.Timestamp_Now                         import Timestamp_Now
from typing                                                                                     import Dict, Set, Any

class Schema__Cache__Common_Elements(Type_Safe):                                # Common elements shared across pages in a domain
    domain            : Safe_Str__Display_Name                                  # Website domain
    threshold_percent : Safe_Float__Percentage_Exact          = 30.0            # Minimum % of pages to be considered common
    total_pages       : int                                                     # Total pages analyzed
    last_updated      : Timestamp_Now                                           # Auto-generates timestamp
    common_hashes     : Set[Safe_Str__Cache_Hash]                               # Hashes appearing above threshold
    hash_frequencies  : Dict[Safe_Str__Cache_Hash, Safe_UInt]                   # Hash -> occurrence count
    classifications   : Dict[Safe_Str__Cache_Hash, Dict[str, Any]]              # Hash -> classification data

    # todo: remove this logic from this schema file
    def is_common(self, hash_value: str) -> bool:                               # Check if hash is considered common
        if self.total_pages == 0:
            return False
        frequency = self.hash_frequencies.get(hash_value, 0)
        percentage = (frequency / self.total_pages) * 100
        return percentage >= self.threshold_percent

    def update_frequency(self, hash_value: str) -> 'Schema__Cache__Common_Elements':  # Increment frequency for a hash
        current_count = self.hash_frequencies.get(hash_value, 0)
        self.hash_frequencies[hash_value] = current_count + 1

        if self.is_common(hash_value):                                           # Add to common set if above threshold
            self.common_hashes.add(hash_value)

        self.last_updated = Timestamp_Now()
        return self

    def add_page_hashes(self, page_hashes: Set[str]) -> 'Schema__Cache__Common_Elements':  # Process hashes from a new page
        self.total_pages += 1
        for hash_value in page_hashes:
            self.update_frequency(hash_value)
        return self