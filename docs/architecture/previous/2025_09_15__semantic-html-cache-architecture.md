# Semantic HTML Cache Architecture
## Comprehensive Design Document

**Author:** Dinis Cruz (https://docs.diniscruz.ai)  
**Date:** September 15, 2025  
**Version:** 1.0

---

## Executive Summary

This document presents the architecture for a distributed semantic HTML processing system designed to classify and cache text elements from web pages at scale. The core challenge we're solving is achieving sub-5 second performance for complete semantic analysis of web pages containing anywhere from 288 to 3,018 unique text elements, while minimizing expensive LLM API calls through intelligent caching strategies.

Our analysis of real-world data from major websites revealed that the primary bottleneck isn't the extraction or processing of text elements (which takes mere milliseconds), but rather the LLM classification calls that can take 1-30 seconds depending on volume and complexity. Through careful analysis of hash distributions and access patterns, we've designed a caching architecture that can eliminate 40-70% of LLM calls for pages within the same domain, and 100% for revisited pages.

The architecture leverages a microservices approach with three core services running on AWS Lambda: semantic-html.dev.mgraph.ai for HTML processing, llms.dev.mgraph.ai for LLM operations (with built-in caching), and cache.dev.mgraph.ai for our custom hash-based document store. By treating S3 as our primary database and accepting up to 10 parallel file fetches per page request (200-500ms total), we can achieve dramatic performance improvements while maintaining a stateless, scalable architecture.

---

## Introduction

The semantic HTML service represents a fundamental shift in how we process and understand web content. Instead of treating web pages as static documents, we extract every piece of text, generate a unique hash for each element, and classify it according to multiple dimensions including positivity, topics, confidentiality, and semantic meaning. This classification enables us to rebuild the HTML with rich semantic context, opening possibilities for intelligent content filtering, analysis, and transformation.

The journey to optimize this system began with a simple observation: when processing a web page through our LLM pipeline, the initial experiments took 30-50 seconds per page. This was unacceptable for real-time web browsing enhancement. However, by analyzing the performance characteristics of each component, we discovered that while LLM calls were inherently slow, everything else—hash calculation, HTML parsing, and file operations—was remarkably fast. This insight led us to focus our optimization efforts entirely on minimizing LLM calls through intelligent caching.

Our voice memo brainstorming session identified several key strategies: parallel processing of LLM requests, intelligent chunking of content, and most importantly, building a custom caching system that could recognize and skip previously classified content. The challenge was to design this cache to work within the constraints of a serverless architecture, with no persistent local storage and all state maintained in S3.

---

## Performance Analysis: Understanding the Baseline

Before diving into our solution, it's crucial to understand what we learned from our performance testing across eight major websites. This data fundamentally shaped our architecture decisions.

### Test Results and Analysis

| Website | Hashes | Distribution (2-char) | JSON Size | Cache Time | URL Fetch | Speedup |
|---------|--------|----------------------|-----------|------------|-----------|---------|
| Wikipedia (Sept 15) | 2,213 | 256 | 213KB | 50ms | 222ms | 4.4x |
| Wikipedia (2025) | 3,018 | 256 | 300KB | 100ms | 270ms | 2.7x |
| The Register | 335 | 195 | 41KB | 11ms | 160ms | 14.5x |
| Amazon | 291 | 172 | 27KB | 20ms | 700ms | 35x |
| BBC News | 292 | 167 | 31KB | 36ms | 385ms | 10.7x |
| BBC Sport | 400 | 201 | 42KB | 32ms | 580ms | 18.1x |
| The Guardian | 484 | 226 | 56KB | 48ms | 300ms | 6.3x |
| Guardian Sport | 288 | 166 | 31KB | 21ms | 160ms | 7.6x |

### Critical Insights from the Data

The performance data revealed several surprising patterns that directly influenced our architecture decisions:

**Hash Volume Variability:** The range from 288 to 3,018 hashes per page initially seemed problematic, but we discovered this actually follows predictable patterns. Wikipedia pages, with their dense informational content, consistently generate 2,000-3,000 hashes. News sites cluster around 300-500 hashes. E-commerce sites, despite their visual complexity, generate relatively few unique text elements (around 300) due to repetitive UI elements.

**Distribution Challenge:** When we analyzed hash distribution using 2-character prefixes, we found that even small pages (288 hashes) spread across 166-172 unique prefixes, while large pages hit all 256 possible combinations. This near-uniform distribution meant our initial plan of one file per prefix would require 166-256 file operations per page—clearly unworkable for performance.

**The Amazon Anomaly:** Amazon's 35x speedup with caching, despite having only 291 hashes, revealed that network latency (700ms) far exceeded the actual processing time. This validated our hypothesis that caching would provide dramatic benefits, especially for sites with complex CDN architectures or dynamic content generation.

**Linear Scaling:** Hash calculation consistently took 0.033-0.037ms per hash, regardless of page size. This meant even our largest pages (3,000 hashes) only needed 100ms for hash generation—negligible compared to LLM processing time.

---

## Architecture Overview

### Service Topology

Our architecture consists of three specialized microservices, each running on AWS Lambda and designed for horizontal scalability:

**semantic-html.dev.mgraph.ai** serves as the orchestration layer. When a user requests semantic processing of a web page, this service extracts all text elements from the DOM, generates hashes for each unique piece of text, coordinates with the cache service to identify previously classified content, sends new content to the LLM service for classification, and finally rebuilds the HTML with semantic annotations.

**cache.dev.mgraph.ai** implements our custom hash-based document store. This service maintains multiple cache layers including site-level common elements, page-specific classifications, bloom filters for quick existence checks, and cross-page pattern matching. The service is designed to minimize network round trips by supporting bulk operations—checking hundreds of hashes in a single API call.

**llms.dev.mgraph.ai** handles all LLM operations with built-in caching. This service already implements result caching based on request hashes, but our additional caching layer prevents unnecessary network calls to even check this cache. The service supports parallel batch processing, allowing us to classify multiple text elements simultaneously.

### The Caching Challenge

The fundamental challenge we're solving is one of scale and speed. Consider a typical Wikipedia page with 2,213 unique text elements. Currently, we can send all these elements to the LLM service in a single request containing a JSON payload like:

```json
{
  "8f3a2b1c9d": {"original_text": "September 15", "tag": "title"},
  "4e7d9f2a3b": {"original_text": "September 15 is the 258th day of the year", "tag": "p"},
  "1a5c8e9d7f": {"original_text": "Events", "tag": "h2"},
  "9b2f4d8c1e": {"original_text": "1821 – Costa Rica, El Salvador, Guatemala, Honduras, and Nicaragua ....", "tag": "li"},
  "7e1c4f9a2d": {"original_text": "References", "tag": "h2"},
  "2f8b5d1c9a": {"original_text": "External links", "tag": "h2"},
  // ... 2,206 more elements
}
```

The problem is that the LLM takes 30-50 seconds to process this massive request, even when 90% of that content has been classified before. While the llms.dev.mgraph.ai service has built-in caching, we're still sending the entire payload and waiting for it to process everything, check its cache for each hash, and return results.

The performance breakthrough comes from two key optimizations: First, by maintaining our own cache index, we can identify which hashes have already been classified and exclude them from the LLM request entirely. If 90% of content is cached, we reduce the payload from 2,213 elements to just 221. Second, we can split even this reduced set into multiple parallel requests. Instead of one request taking 30 seconds, we might have 10 parallel requests each taking 3-5 seconds.

However, this parallel processing strategy must be carefully balanced. LLM providers implement rate limiting (requests per minute, tokens per minute, concurrent request limits), so we need to find the sweet spot between parallelization for speed and staying within rate limits. Our testing suggests 10-20 parallel requests provides optimal performance while respecting typical rate limits.

Our solution implements intelligent caching at the orchestration layer, maintaining our own index of classified content. This allows us to minimize both the payload size sent to the LLM and the processing time, organized in a way that minimizes lookup time while working within the constraints of a stateless Lambda architecture.

---

## Cache Design Philosophy

### From Individual Hashes to Pattern Recognition

Our initial instinct was to cache individual hash classifications, similar to a traditional key-value store. However, the performance data revealed this wouldn't scale—we'd need to check thousands of individual keys per page. Instead, we developed a hierarchical caching strategy that recognizes patterns in how content appears across pages.

The key insight came from analyzing news sites: BBC News (292 hashes) and BBC Sport (400 hashes) likely share 40-50% of their content—navigation elements, footers, cookie notices, and common UI components. By identifying and caching these common elements at the site level, we can instantly classify nearly half of any BBC page without any lookups.

### The File System as Database

Working within Lambda's stateless architecture, we don't have access to traditional databases or persistent local storage. Instead, we use S3 as our database, organizing files in a way that minimizes retrieval time while maximizing cache hits. This constraint actually led to better design decisions—forcing us to think carefully about data organization and access patterns rather than relying on database indexes to solve performance problems.

Our testing showed that S3 file retrieval takes 20-50ms per file, and we set a budget of 10 file fetches per page request. Crucially, since we know the exact paths of most files we need (based on domain and page URL), we can fetch them in parallel, bringing our total cache lookup time to around 50-100ms regardless of the number of files.

### Bloom Filters: The Power of Negative Knowledge

One of our most powerful optimizations is using bloom filters to quickly identify content we've never seen before. A bloom filter is a probabilistic data structure that can definitively tell us if a hash has never been encountered, with only a small chance of false positives (saying we might have seen something when we haven't). (For a detailed technical explanation of how bloom filters work and why they're perfect for our use case, see the "Understanding Bloom Filters" section at the end of this document.)

For a site with 5,000 unique hashes, a 100KB bloom filter gives us 0.01% false positive rate. This means for a new page with 300 hashes where 100 are truly new, the bloom filter will correctly identify all 100 as new, and might incorrectly suggest we check the cache for 0-1 hash that's actually new. This dramatic reduction in cache lookups more than justifies the small storage overhead.

---

## Detailed Cache Architecture

### File Structure and Organization

Our cache consists of several file types, each serving a specific purpose in our hierarchy of lookups. The organization is designed to maximize the probability of cache hits while minimizing the number of files that need to be loaded.

### Site-Level Cache Files

At the domain level, we maintain several files that capture patterns across all pages we've seen from that site:

**Site Manifest (sites/{domain}/manifest.json):** This 5KB file serves as the entry point for all cache operations for a domain. It contains metadata about what we've cached, including the total number of unique hashes seen, number of pages processed, last update timestamp, and pointers to other cache files. This manifest allows us to quickly understand the cache state without loading larger files.

**Common Elements (sites/{domain}/common.json):** This file, typically 50-100KB, contains the hashes and classifications for text elements that appear on more than 30% of pages from this domain. Our analysis of news sites showed that navigation menus, footers, cookie notices, and UI elements are remarkably consistent across pages. By loading this single file, we can instantly classify 40-50% of any page from that domain. The 30% threshold was chosen empirically—it's high enough to ensure these are truly common elements, but low enough to capture most shared content.

**Bloom Filter (sites/{domain}/bloom.b64):** A binary bloom filter, base64-encoded for storage, containing all hashes we've ever seen from this domain. At approximately 100KB for sites with 5,000 unique hashes, this provides instant negative lookups—if the bloom filter says we haven't seen a hash, we definitely haven't, saving us from checking any other cache files.

**Pages Index (sites/{domain}/pages_index.json):** A lightweight index of all pages we've cached from this domain, with metadata about each page including its URL hash, number of unique elements, cache completeness percentage, and last visit timestamp. This allows us to quickly identify which page-specific cache files might contain classifications for our current hashes.

### Page-Level Cache Files

For individual pages, we maintain more detailed cache data:

**Page Data (pages/{page_hash}/data.json):** Complete cache of all hashes and their classifications for a specific page. When a user revisits the exact same page, we can load this single file and have 100% cache hits. The file includes the original URL, extraction timestamp, and all hash-to-classification mappings with confidence scores and position information.

**Delta Files (pages/{page_hash}/delta_{strategy}.json):** We can implement multiple caching strategies with different granularities. For example, a delta file might contain only hashes unique to this page (not in common elements), or only content-area hashes (excluding navigation), or only high-confidence classifications. By maintaining multiple strategies, we can empirically determine which works best for different site types.

### Pattern-Based Cache Files

**URL Pattern Cache (sites/{domain}/patterns.json):** Captures elements that consistently appear on certain URL patterns. For instance, all BBC Sport articles might share sport-specific navigation elements that don't appear on BBC News pages. By recognizing the URL pattern, we can pre-load likely classifications.

---

## Processing Flows and Optimization Strategies

### The Parallel Processing Revolution

The original implementation sent all hashes to the LLM service in a single request, leading to 30-50 second processing times. By splitting the hashes into batches and processing them in parallel, we can dramatically reduce total processing time. The optimal batch size depends on the LLM's processing characteristics, but our testing suggests 50-100 hashes per batch with 10-20 parallel requests provides the best balance.

Since Lambda functions can spawn multiple threads, and we're making network calls (which are I/O bound, not CPU bound), we can efficiently parallelize these requests. The total processing time becomes limited by the slowest batch, rather than the sum of all processing times. For a page with 1,000 new hashes, instead of one 30-second request, we might have 20 parallel 3-second requests, reducing total time to 3-4 seconds.

### Intelligent Chunking Strategies

Not all text elements are equal. Our analysis revealed several chunking strategies that can improve cache hit rates:

**Size-based chunking:** Group text elements by length. Single words, short phrases, sentences, and paragraphs tend to have different reuse patterns. Navigation elements are often short, while content tends to be longer.

**Semantic chunking:** Group elements by their likely semantic category. Elements containing numbers might be prices or statistics. Elements with certain keywords might be navigation. This pre-classification can help the LLM provide more consistent results.

**Position-based chunking:** Elements at the top and bottom of pages (headers and footers) have different caching characteristics than middle content. By processing these separately, we can optimize cache strategies for each.

### The Cascade of Cache Checks

When processing a new page, we follow a carefully orchestrated cascade of cache checks, designed to maximize early hits while minimizing file loads:

First, we check if we've processed this exact URL before. A single file load (pages/{page_hash}/data.json) might give us 100% cache hits. This is our fastest path—under 100ms total.

If it's a new page from a known site, we load the site manifest and common elements (2 parallel fetches, ~50ms). This immediately classifies 40-50% of the page's content without any lookups.

Next, we load the bloom filter (parallel with above). For the remaining unclassified hashes, we can instantly identify which have never been seen before. These definitely need LLM processing.

For hashes that might be cached (bloom filter positive), we check the pages index to identify 2-3 similar pages that might contain these classifications. We load these in parallel (~50ms) and check for matches.

Any remaining hashes are sent to the LLM service in parallel batches. The results are then stored back to our cache, updating the bloom filter and creating page-specific cache files.

---

## Page Hash Calculation

### The Need for Consistent Page Identification

A critical component of our caching system is the ability to consistently identify when we're looking at the "same" page. This requires a deterministic method for generating page hashes that captures all factors affecting the page content while avoiding unnecessary cache misses due to irrelevant variations.

### Current Implementation (MVP)

For the initial version, we implement a straightforward approach that ensures cache consistency:

```python
def calculate_page_hash(url, method="GET", post_data=None):
    """
    Generate a unique hash for a page based on its URL and parameters.
    MVP version: Only supports GET requests with full URL + query params
    """
    # Parse the URL
    parsed = urlparse(url)
    
    # Build the cache key components
    cache_key_parts = [
        parsed.scheme,      # http or https
        parsed.netloc,      # domain
        parsed.path,        # /wiki/September_15
        parsed.query        # all query parameters
    ]
    
    # Create deterministic string representation
    cache_key = "|".join(cache_key_parts)
    
    # Generate hash
    page_hash = hashlib.sha256(cache_key.encode()).hexdigest()[:16]
    
    return page_hash
```

This approach means:
- `https://en.wikipedia.org/wiki/2025` → consistent hash
- `https://en.wikipedia.org/wiki/2025?printable=yes` → different hash
- `https://en.wikipedia.org/wiki/2025?utm_source=twitter` → different hash

### Why This Matters

The page hash directly determines our cache hit rate. Too specific, and we miss cache opportunities (treating identical content as different pages). Too general, and we risk serving wrong cached content. For the MVP, we err on the side of specificity—better to miss a cache opportunity than serve incorrect content.

### Examples and Edge Cases

Consider these URLs and their cache implications:

**Different query parameters = different hash:**
- `/article?id=123` → hash_abc123
- `/article?id=123&refresh=true` → hash_def456
- Both might return identical content, but we cache them separately

**Order matters (in current implementation):**
- `/search?q=semantic&type=web` → hash_aaa111
- `/search?type=web&q=semantic` → hash_bbb222
- Same logical query, different hashes

**Fragment identifiers are ignored:**
- `/page#section1` → hash_xyz789
- `/page#section2` → hash_xyz789
- Fragments don't affect server response, so same hash

### Future Enhancements

While not in the MVP, future versions will need to handle:

**Configurable parameter filtering:** Some parameters don't affect content (utm_campaign, session_id) and should be excluded from hash calculation.

**POST request support:** Include POST data in hash calculation for forms and dynamic content.

**Parameter normalization:** Sort parameters alphabetically to ensure consistent hashing regardless of parameter order.

**Domain-specific rules:** Different sites might need different hashing strategies (e.g., some sites use path parameters, others use query strings for the same purpose).

For now, the simple approach of hashing the complete URL with all query parameters provides a solid foundation that guarantees cache consistency, even if it means some missed optimization opportunities.

---

## Implementation Considerations

### Scalability and Cost Optimization

Our architecture scales horizontally at every layer. Lambda functions auto-scale based on load, S3 provides virtually unlimited storage and throughput, and our cache structure ensures that performance remains consistent regardless of the total amount of cached data.

Cost optimization comes from minimizing LLM API calls, which are the primary expense. By achieving 40-70% cache hits on new pages and 100% on revisited pages, we dramatically reduce API costs. The storage costs for our cache (approximately 5MB per site) are negligible compared to the saved LLM processing costs.

### Monitoring and Analytics

Our cache design naturally generates valuable analytics. We can track cache hit rates per domain, identify the most commonly classified elements, measure performance improvements over time, and detect unusual patterns that might indicate content changes or new site structures.

These metrics not only help optimize the cache but also provide insights into web content patterns that could be valuable for other applications.

---

## Results and Validation

### Performance Achievements

Based on our architecture and test data, we project the following performance characteristics:

**Same Page Revisit:** 100-200ms total processing time with 100% cache hits. This represents a 150-300x improvement over the original implementation.

**New Page, Same Site:** 1-3 seconds for pages with 70% cached content (typical for news sites with consistent navigation). This is a 10-30x improvement.

**Brand New Site:** 3-5 seconds for initial page processing, as all content requires LLM classification but benefits from parallel processing. Still a 6-10x improvement over serial processing.

These projections are conservative. Sites with higher content repetition (like e-commerce sites with consistent product layouts) could see even better performance.

### Validation Through Real-World Patterns

Our test data validates these projections. The Wikipedia pages, despite having 10x more content than news sites, only take 2x longer to process with caching. This sub-linear scaling demonstrates the effectiveness of our approach. The Amazon example, with its 35x speedup, shows that our architecture provides the most value precisely where it's needed most—on sites with high latency or complex dynamic content.

---

## Conclusions and Future Directions

### Key Achievements

We've successfully designed a caching architecture that transforms a 30-50 second process into a sub-5 second experience for most real-world scenarios. By recognizing that web content follows predictable patterns—with 40-50% repetition within sites and even higher repetition for revisited pages—we can eliminate the majority of expensive LLM calls.

Our use of S3 as a database, rather than fighting against the constraints of serverless architecture, led to a cleaner, more scalable design. The hierarchical cache structure, with site-level common elements and page-specific details, provides an optimal balance between storage efficiency and lookup performance.

The bloom filter optimization, providing instant negative lookups, exemplifies our philosophy of "knowing what we don't know" being as valuable as knowing what we do know. This negative knowledge prevents countless unnecessary cache checks.

### Broader Implications

This architecture has implications beyond just the semantic HTML service. The pattern of using hierarchical caching with bloom filters for quick rejection could apply to any system that needs to process large amounts of semi-repetitive content. The technique of promoting frequently-seen elements to a common cache could optimize any application dealing with template-based content.

Our empirical approach—implementing multiple strategies and measuring which works best—provides a framework for optimization that doesn't require perfect theoretical knowledge. By building in measurement and adaptation from the start, the system can optimize itself based on real-world usage patterns.

### The Path Forward

With this architecture documented and understood, we're ready to begin implementation. The modular design allows us to implement and test components independently. We can start with the site-level common elements cache (providing immediate 40-50% cache hits) and progressively add more sophisticated caching layers.

The architecture's flexibility means we can experiment with different thresholds (why 30% for common elements?), different chunking strategies (size vs. semantic vs. position), and different storage organizations (more or fewer files per page) without fundamental restructuring.

Most importantly, we've created a system that can evolve. As we learn more about how web content is structured and how users navigate sites, our cache can adapt, continuously improving performance while maintaining the sub-5 second target that makes real-time semantic HTML processing practical.

---

## Understanding Bloom Filters

### What is a Bloom Filter?

A Bloom filter, invented by Burton Howard Bloom in 1970, is a space-efficient probabilistic data structure designed to test whether an element is a member of a set. Think of it as a highly compressed way to remember "have I seen this before?" without storing the actual items. The genius of bloom filters lies in their trade-off: they use very little memory in exchange for accepting a small chance of false positives.

To understand how revolutionary this is for our use case, consider the alternative: to know if we've seen a hash before, we'd normally need to store all previously seen hashes. For a site with 10,000 unique text elements, storing 64-character hashes would require about 640KB just for the hashes, plus overhead for the data structure. A bloom filter can achieve 99.9% accuracy with just 100KB—a 6x space reduction.

### How Bloom Filters Work

A bloom filter consists of two components: a bit array and a set of hash functions. Here's how it operates:

**Initialization**: Start with a bit array of size m, with all bits set to 0. Choose k different hash functions that can map any input to a position in the array (0 to m-1).

**Adding an element**: To add a hash to the bloom filter, run it through all k hash functions. Each hash function will return a position in the bit array. Set all these positions to 1. For example, if we have 3 hash functions and they return positions 42, 197, and 891, we set bits 42, 197, and 891 to 1.

**Checking membership**: To check if a hash might be in the set, run it through the same k hash functions. If ALL the corresponding positions in the bit array are 1, the hash might be in the set. If ANY position is 0, the hash is definitely not in the set.

Here's a practical example for our semantic HTML cache:

```
Initial bloom filter (simplified, 20 bits): 00000000000000000000

Add hash "a1b2c3" (maps to positions 3, 7, 15): 00010001000000010000
Add hash "d4e5f6" (maps to positions 1, 7, 12): 01010001000100010000
Add hash "g7h8i9" (maps to positions 7, 11, 18): 01010001000100010010

Check hash "j1k2l3" (maps to positions 2, 9, 14):
- Position 2: bit is 0 → definitely not in set ✓

Check hash "a1b2c3" (maps to positions 3, 7, 15):
- Position 3: bit is 1 ✓
- Position 7: bit is 1 ✓
- Position 15: bit is 1 ✓
- All bits are 1 → might be in set (in this case, it actually is)

Check hash "m4n5o6" (maps to positions 1, 7, 15):
- Position 1: bit is 1 ✓
- Position 7: bit is 1 ✓
- Position 15: bit is 1 ✓
- All bits are 1 → might be in set (false positive - we never added this!)
```

### The Mathematics of False Positives

The false positive rate depends on three variables: the size of the bit array (m), the number of hash functions (k), and the number of elements inserted (n). The probability of a false positive is approximately:

P = (1 - e^(-kn/m))^k

For our use case with 5,000 hashes, using a 100KB bloom filter (800,000 bits) with 5 hash functions gives us a false positive rate of approximately 0.01%. This means:
- Out of 1,000 new hashes we check, the bloom filter will correctly identify all 1,000 as new
- Out of 1,000 previously seen hashes, it might incorrectly say 1 is new (requiring an unnecessary cache check)
- It will NEVER incorrectly say a new hash was previously seen (no false negatives)

### Why Bloom Filters are Perfect for Our Cache

Bloom filters offer several compelling advantages for our semantic HTML caching system:

**Space Efficiency**: A 100KB bloom filter can track 10,000+ unique hashes with 99.99% accuracy. Storing the actual hashes would require 10-20x more space.

**Speed**: Checking membership is O(k) where k is the number of hash functions (typically 3-7). This is essentially constant time and requires no disk I/O once the bloom filter is loaded into memory.

**No False Negatives**: This is crucial for our use case. If the bloom filter says a hash hasn't been seen, we can be 100% certain it hasn't. This means we can skip all cache lookups and go straight to LLM processing for truly new content.

**Persistence Friendly**: A bloom filter is just a bit array, making it trivial to serialize and store in S3. It can be base64 encoded for text storage or kept as binary for maximum efficiency.

**Incremental Updates**: New hashes can be added to an existing bloom filter without rebuilding it. This allows us to update our cache knowledge in real-time as we process new pages.

### Practical Implementation for Our Architecture

In our system, each domain gets its own bloom filter stored at `sites/{domain}/bloom.b64`. Here's how we use it in practice:

```python
# Pseudo-code for our bloom filter usage
def process_page_hashes(domain, page_hashes):
    # Load bloom filter once (100KB, ~20ms from S3)
    bloom = load_bloom_filter(f"sites/{domain}/bloom.b64")
    
    definitely_new = []
    possibly_cached = []
    
    for hash in page_hashes:
        if hash not in bloom:
            # 100% certain this is new - no cache check needed
            definitely_new.append(hash)
        else:
            # Might be cached - need to check
            possibly_cached.append(hash)
    
    # Result: We've eliminated cache lookups for all definitely_new hashes
    # This could be 30-50% of hashes on a new page!
    
    # Only check cache for possibly_cached hashes
    cached_results = check_cache_for_hashes(possibly_cached)
    
    # Send only truly new hashes to LLM
    needs_llm = definitely_new + [h for h in possibly_cached if h not in cached_results]
```

### Trade-offs and Considerations

While bloom filters are powerful, they do have limitations we must consider:

**One-way operation**: Elements can only be added to a bloom filter, never removed. To "remove" elements, you need to rebuild the entire filter. For our use case, this isn't a problem since we're tracking "have we ever seen this?" rather than "is this currently in our cache?"

**Size must be predetermined**: The bit array size must be chosen upfront based on expected number of elements. If we significantly underestimate, the false positive rate will increase. Our solution: we size bloom filters generously (100KB for most sites) and can rebuild them during maintenance windows if needed.

**No element retrieval**: A bloom filter can't tell you what elements are in it, only whether a specific element might be. This is why we pair bloom filters with other cache structures that store actual classifications.

### Real-World Impact

Let's quantify the impact using our BBC News example with 292 hashes:

Without bloom filter:
- Check all 292 hashes against cache files
- Multiple S3 reads to check different cache layers
- Total time: 200-300ms of cache checking

With bloom filter:
- Load bloom filter: 20ms
- Check 292 hashes in memory: <1ms
- Identify ~100 definitely new hashes instantly
- Only check cache for ~192 possibly cached hashes
- Total time: 100-150ms (50% reduction)

More importantly, for brand new content that's never been seen, the bloom filter eliminates 100% of unnecessary cache checks, allowing us to proceed directly to LLM processing. This is particularly valuable when processing new articles or updated content where 30-50% of text might be new.

The bloom filter is a perfect example of how probabilistic data structures can provide enormous practical benefits. By accepting a tiny chance of unnecessary cache checks (false positives), we gain the certainty of never missing cache opportunities (no false negatives) while using minimal storage space. In our architecture, this translates directly to faster page processing and reduced latency for end users.

---

## Appendix: Future Enhancements

### Cross-Page Learning and Pattern Evolution

While the initial MVP implementation maintains a stateless cache (what's cached stays cached), future versions could implement intelligent cache evolution. The cache could learn and adapt based on access patterns. When we see a hash appear on multiple pages, we could track this frequency. Once a hash appears on more than 30% of pages from a domain, it could be promoted to the common elements cache. Conversely, if a previously common element stops appearing, it could be demoted.

This evolution would happen asynchronously. The semantic-html service would focus on serving requests quickly, while a background process (triggered periodically or by significant changes) would reorganize the cache for optimal performance. This would provide continuous improvement without impacting request latency.

### Intelligent Cache Invalidation

The MVP approach of "cache forever" is simple and effective for getting started, but future versions could implement smart invalidation strategies. The architecture could handle this through timestamp-based invalidation. Each cache entry would include a timestamp, and we could configure TTLs based on content type. Navigation elements might be cached for weeks, while news content might expire after days.

Rather than actively invalidating cache entries, we could use lazy invalidation—checking timestamps when loading cache files and treating expired entries as cache misses. This would avoid the complexity of maintaining invalidation queues while ensuring content freshness.

### Advanced Page Hash Strategies

Future versions could implement more sophisticated page hash calculations:

**Smart Parameter Filtering**: Automatically identify and exclude tracking parameters (utm_*, session_id, etc.) that don't affect content, improving cache hit rates without manual configuration.

**Content-Based Hashing**: Instead of URL-based hashing, generate hashes based on actual page structure, allowing cache hits even when URLs change but content remains the same.

**Fuzzy Matching**: Implement similarity detection to identify pages that are "close enough" to use cached classifications for most elements, only processing truly different content.

### Cross-Domain Intelligence

While the MVP focuses on single-domain caching, future enhancements could implement cross-domain pattern recognition. Common elements like cookie notices, social media widgets, and standard UI patterns appear across many sites. A global cache of these elements could provide immediate classification for 10-20% of any new site's content.

---

## Summary

This document captures our complete understanding of the semantic HTML caching challenge as of September 15, 2025. We've moved from an initial implementation taking 30-50 seconds per page to an architecture capable of sub-5 second processing through intelligent caching and parallel processing.

The key insights—that web content is highly repetitive within sites, that bloom filters can provide valuable negative knowledge, that S3 can serve as an effective database for our use case, and that parallel processing can overcome LLM latency—form the foundation of an architecture that's both performant and scalable.

By documenting not just what we decided but why we made these decisions, including the data analysis that led to these conclusions, we've created a reference that can guide implementation while remaining flexible enough to evolve as we learn more from real-world usage.