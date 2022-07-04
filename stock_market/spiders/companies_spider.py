import scrapy


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    custom_settings = {
        # 'FEED_EXPORTERS': {
        #     'json': 'scrapy.exporters.JsonItemExporter',
        # },
        # 'FEEDS': {
        #     "companies.json": {"format": "json"},
        # },
        'ITEM_PIPELINES': {'stock_market.pipelines.StockMarketPipeline': 300}
    }

    def start_requests(self):
        stocks_urls = [
            'https://www.marketbeat.com/stocks/nyse/',
            'https://www.marketbeat.com/stocks/nasdaq/',
            'https://www.marketbeat.com/stocks/otcmkts/',
            'https://www.marketbeat.com/stocks/tse/',
            'https://www.marketbeat.com/stocks/cve/',
            'https://www.marketbeat.com/stocks/lon/',
        ]
        for url in stocks_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        companies = response.css('tr')
        for company in companies:
            if company.css('td:first-of-type a div.ticker-area::text').get() is not None:
                yield {
                    'ticker': company.css('td:first-of-type a div.ticker-area::text').get(),
                    'name': company.css('td:first-of-type a div.title-area::text').get(),
                    'uri': 'https://www.marketbeat.com' + company.css('td:first-of-type a::attr(href)').get(),
                }
