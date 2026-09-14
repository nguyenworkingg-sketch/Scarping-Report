import argparse
import asyncio

from dotenv import load_dotenv

from core.utils import cleanup_old_files, ensure_directories
from scrapers.hsc import HSCScraper
from scrapers.vietcap import VietcapScraper


async def run(source: str):
    if source in ("all", "hsc"):
        await HSCScraper().run()
    if source in ("all", "vietcap"):
        await VietcapScraper().run()


def main():
    load_dotenv()
    ensure_directories()

    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["all", "hsc", "vietcap"], default="all")
    args = parser.parse_args()

    cleanup_old_files()
    asyncio.run(run(args.source))
    cleanup_old_files()


if __name__ == "__main__":
    main()
