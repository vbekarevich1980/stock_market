# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import json
from urllib.parse import quote

import scrapy
from itemadapter import ItemAdapter
from scrapy.utils.defer import maybe_deferred_to_future


class StockMarketPipeline:

    def open_spider(self, spider):
        if spider.name == 'companies':
            self.tickers = {}
            # self.file = open('companies.json', 'w')
            # self.file.write('{')

    def close_spider(self, spider):
        if spider.name == 'companies':
            with open('companies.json', 'w') as file:
                file.write(json.dumps(self.tickers))

    def process_item(self, item, spider):
        if spider.name == 'companies':
            self.tickers[ItemAdapter(item).asdict()['ticker']] = {}
            self.tickers[ItemAdapter(item).asdict()['ticker']]['name'] = ItemAdapter(item).asdict()['name']
            self.tickers[ItemAdapter(item).asdict()['ticker']]['uri'] = ItemAdapter(item).asdict()['uri']
            #line = f"{ItemAdapter(item).asdict()['ticker']}: {ItemAdapter(item).asdict().items()}" + "\n"

            #self.file.write(line)
        return item


class ScreenshotPipeline:
    """Pipeline that uses Splash to render screenshot of
    every Scrapy item."""

    SPLASH_URL = "http://localhost:8050/render.png?url={}"

    async def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        charts = {
            "revenue":
                f"https://www.macrotrends.net/assets/php/fundamental_iframe."
                f"php?t={adapter['Ticker']}&type=revenue&statement=income-"
                f"statement&freq=Q",
            "net_income":
                f"https://www.macrotrends.net/assets/php/fundamental_iframe."
                f"php?t={adapter['Ticker']}&type=net-income&statement=income-"
                f"statement&freq=Q",
            "esp":
                f"https://www.macrotrends.net/assets/php/fundamental_iframe."
                f"php?t={adapter['Ticker']}&type=eps-earnings-per-share-"
                f"diluted&statement=income-statement&freq=Q",
            "price_sales":
                f"https://www.macrotrends.net/assets/php/fundamental_iframe."
                f"php?t={adapter['Ticker']}&type=price-sales&statement=price-"
                f"ratios&freq=Q",
            "pe_ratio":
                f"https://www.macrotrends.net/assets/php/fundamental_iframe."
                f"php?t={adapter['Ticker']}&type=pe-ratio&statement=price-"
                f"ratios&freq=Q",
            "price_book":
                f"https://www.macrotrends.net/assets/php/fundamental_iframe."
                f"php?t={adapter['Ticker']}&type=price-book&statement=price-"
                f"ratios&freq=Q",
            "market_cap":
                f"https://www.macrotrends.net/assets/php/market_cap."
                f"php?t={adapter['Ticker']}",
        }
        for name, uri in charts.items():
            encoded_item_url = quote(uri)
            screenshot_url = self.SPLASH_URL.format(encoded_item_url)
            request = scrapy.Request(screenshot_url)
            response = await maybe_deferred_to_future(spider.crawler.engine.download(request, spider))

            if response.status != 200:
                # Error happened, return item.
                continue

            # Save screenshot to file
            screenshot_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
            if not os.path.exists(screenshot_dir):
                os.mkdir(screenshot_dir)
            filename = os.path.join(screenshot_dir, f"{adapter['Ticker']}_{name}.png")
            with open(filename, "wb") as f:
                f.write(response.body)

        return item
