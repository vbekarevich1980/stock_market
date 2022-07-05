# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import hashlib
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
            # self.file.write('}')
            # self.file.close()

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
        }
        for name, uri in charts.items():
            encoded_item_url = quote(uri)
            screenshot_url = self.SPLASH_URL.format(encoded_item_url)
            #print(screenshot_url)
            request = scrapy.Request(screenshot_url)
            response = await maybe_deferred_to_future(spider.crawler.engine.download(request, spider))

            if response.status != 200:
                # Error happened, return item.
                continue

            # Save screenshot to file, filename will be hash of url.
            # url = adapter["Revenue"]
            # url_hash = hashlib.md5(url.encode("utf8")).hexdigest()
            # filename = f"{url_hash}.png"
            filename = f"{adapter['Ticker']}_{name}.png"
            with open(filename, "wb") as f:
                f.write(response.body)

        # Store filename in item.
        #adapter["screenshot_filename"] = filename
        return item