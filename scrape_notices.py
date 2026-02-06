#!/usr/bin/env python
from src.scraper import NoticesScraper
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape University Notices")
    parser.add_argument("--limit", type=int, help="Limit number of downloads")
    args = parser.parse_args()

    scraper = NoticesScraper()
    scraper.scrape(limit=args.limit)
