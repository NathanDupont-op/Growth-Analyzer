import asyncio
import sys
import argparse
from scraper import get_startup_content

# Force Proactor for standalone execution
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to scrape")
    args = parser.parse_args()
    
    # Run the scraper
    content = await get_startup_content(args.url)
    
    # Print content to stdout (handle encoding)
    sys.stdout.reconfigure(encoding='utf-8')
    print(content)

if __name__ == "__main__":
    asyncio.run(main())
