# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json

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