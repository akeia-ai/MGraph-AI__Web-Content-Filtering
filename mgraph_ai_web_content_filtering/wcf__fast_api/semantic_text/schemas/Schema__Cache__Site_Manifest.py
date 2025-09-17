from memory_fs.schemas.Safe_Str__Cache_Hash                                               import Safe_Str__Cache_Hash
from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Display_Name import Safe_Str__Display_Name
from osbot_utils.type_safe.primitives.domains.identifiers.Timestamp_Now                   import Timestamp_Now

class Schema__Cache__Site_Manifest(Type_Safe):                                    # Metadata for a cached website domain
    domain               : Safe_Str__Display_Name                                 # Website domain (e.g., "bbc.co.uk")
    total_unique_hashes  : int                                                    # Total unique text hashes seen
    pages_processed      : int                                                    # Number of pages processed
    last_updated         : Timestamp_Now                                          # Auto-generates timestamp
    common_elements_hash : Safe_Str__Cache_Hash = None                            # Points to common.json cache entry
    bloom_filter_hash    : Safe_Str__Cache_Hash = None                            # Points to bloom filter cache entry
    pages_index_hash     : Safe_Str__Cache_Hash = None                            # Points to pages index cache entry

    # todo: remove this logic from this schema file
    def increment_pages(self) -> 'Schema__Cache__Site_Manifest':                 # Helper to increment page count
        self.pages_processed += 1
        self.last_updated = Timestamp_Now()                                      # Update timestamp
        return self

    def update_hashes(self, new_hash_count: int) -> 'Schema__Cache__Site_Manifest':  # Update unique hash count
        if new_hash_count > self.total_unique_hashes:
            self.total_unique_hashes = new_hash_count
            self.last_updated = Timestamp_Now()
        return self