from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor

from stock_market.spiders.companies_spider import CompaniesSpider


if __name__ == "__main__":

    configure_logging()
    #settings = get_project_settings()

    #install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    process = CrawlerProcess()#settings=settings)
    process.crawl(CompaniesSpider)
    process.start()

