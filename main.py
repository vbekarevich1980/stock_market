import os
import time

from twisted.internet import defer # reactor,
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from stock_market.spiders.stock_market_spider import StockMarketSpider
from stock_market.spiders.companies_spider import CompaniesSpider


from scrapy.utils.reactor import install_reactor

if __name__ == "__main__":

    #os.system('docker run -d -p 8050:8050 --rm --name splash scrapinghub/splash')
    #time.sleep(10)

    # configure_logging()
    # settings = get_project_settings()
    # runner = CrawlerRunner(settings=settings)
    # runner.crawl(ProxySpider)
    # runner.crawl(BroswaySpider)
    # d = runner.join()
    # d.addBoth(lambda _: reactor.stop())
    #
    # reactor.run()  # the script will block here until all crawling jobs are



    configure_logging()
    settings = get_project_settings()
    # runner = CrawlerRunner(settings)
    #
    # @defer.inlineCallbacks
    # def crawl():
    #     yield runner.crawl(ProxySpider)
    #     #yield runner.crawl(BroswaySpider)
    #     #yield runner.crawl(TedoraSpider)
    #     #yield runner.crawl(BreuningSpider)
    #     yield runner.crawl(BoccadamoSpider)
    #     reactor.stop()
    #
    # crawl()
    # reactor.run()




    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    process = CrawlerProcess(settings=settings)
    #process.crawl(CompaniesSpider)
    process.crawl(StockMarketSpider)
    process.start()

    #os.system('docker stop splash')