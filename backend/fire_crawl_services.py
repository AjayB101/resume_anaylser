import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp, ScrapeOptions
from sqlalchemy import over
# from langchain_community.tools import TavilySearchResults


class FireCrawlService:
    def __init__(self):
        load_dotenv(override=True)
        self.app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    def search(self, query: str, n_res: int = 2):
        crawl_result = self.app.search(
            query=query,
            limit=n_res,
            scrape_options=ScrapeOptions(formats=['markdown']),
        )
        return crawl_result

    def scrape(self, url: str):
        scrape_result = self.app.scrape_url(
            url, formats=['markdown'])
        return scrape_result
