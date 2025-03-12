"""
Crawls the specified domain using a breadh first strategy
"""

import asyncio

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, FilterChain, DomainFilter
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

from crawl4ai import RateLimiter, MemoryAdaptiveDispatcher
from crawl4ai import CrawlerMonitor, DisplayMode

from settings import settings
from utils import save_json


# Set crawl parameters
CRAWL_DEPTH = 3  # 1, 2, 3, 4
CRAWL_INFO = {
    "url": "https://flare.network",
    "output_file": f"data/crawled_data/flare-network_depth{CRAWL_DEPTH}.json"
}


async def crawler():
    """Crawl multiple URLs in parallel with a concurrency limit."""
    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
        extra_args=["--disable-gpu",
                    "--disable-dev-shm-usage", "--no-sandbox"],
    )
    # crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Create a chain of filters
    filter_chain = FilterChain([
        # Only crawl specific domains
        DomainFilter(
            # blocked_domains=["https://flare-explorer.flare.network/*", "https://songbird-explorer.flare.network/*",
            #                  "https://coston2-explorer.flare.network/*", "https://coston-explorer.flare.network/*", "https://dev.flare.network/*", "https://docs.flare.network/*"]

            blocked_domains=["flare-explorer.flare.network", "songbird-explorer.flare.network",
                             "coston2-explorer.flare.network", "coston-explorer.flare.network"]
        ),
    ])

    # Configure a 2-level deep crawl
    crawler_config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=CRAWL_DEPTH,
            include_external=False,
            filter_chain=filter_chain
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
        cache_mode=CacheMode.BYPASS,
        stream=True,  # Enable streaming mode
    )

    # Create a RateLimiter with custom settings
    rate_limiter = RateLimiter(
        base_delay=(2.0, 4.0),  # Random delay between 2-4 seconds
        max_delay=60.0,         # Cap delay at 30 seconds
        max_retries=5,          # Retry up to 5 times on rate-limiting errors
        rate_limit_codes=[429, 503]  # Handle these HTTP status codes
    )

    # Provides real-time visibility into crawling operations
    monitor = CrawlerMonitor(
        # Maximum rows in live display
        max_visible_rows=15,

        # DETAILED or AGGREGATED view
        display_mode=DisplayMode.AGGREGATED
    )

    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=10,
        rate_limiter=rate_limiter,
        monitor=monitor,

    )

    file = []  # stores {url: str, file: str}; file -> markdown file

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Process results as they become available
        async for result in await crawler.arun(
            url=CRAWL_INFO["url"],
            config=crawler_config,
            # rate_limiter=rate_limiter,
            # monitor=monitor
            dispatcher=dispatcher
        ):
            if result.success:
                # Process each result immediately

                # print(result.url)
                # await process_and_store_document(result.url, result.markdown.raw_markdown)

                # Store in dict
                # file.append(
                #     {"url": result.url, "page_title": result.metadata["title"], "page_description": result.metadata["description"], "internal_links": result.links.get("internal", []), "external_links": result.links.get("external", []), "file": result.markdown.raw_markdown})

                file.append(
                    {"url": result.url, "page_title": result.metadata["title"], "page_description": result.metadata["description"],  "file": result.markdown.raw_markdown})

            else:
                print(f"Failed to crawl {result.url}: {result.error_message}")

    # Save to json
    save_json(file, settings.input_path / CRAWL_INFO["output_file"])


async def crawler_main():
    await crawler()

if __name__ == "__main__":
    asyncio.run(crawler_main())
