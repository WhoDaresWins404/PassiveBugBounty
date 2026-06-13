from typing import List


def get_crawlable_urls(base):
    # For now return a seeded list to simulate crawled targets
    return [f"{base}/login", f"{base}/search?q=123"]
