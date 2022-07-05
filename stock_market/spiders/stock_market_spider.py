import re

import scrapy
import openpyxl
import json
from pathlib import Path
from scrapy.loader import ItemLoader
from stock_market.items import StockMarketItem
from itemloaders.processors import Join, MapCompose, TakeFirst
import chompjs


class StockMarketSpider(scrapy.Spider):
    name = "stock_market"
    companies = []
    custom_settings = {
         'FEED_EXPORTERS': {
    #         'json': 'scrapy.exporters.JsonItemExporter',
             'xlsx': 'scrapy_xlsx.XlsxItemExporter',
         },
        'FEEDS': {
            "stock.xlsx": {"format": "xlsx"},
            "stock.csv": {"format": "csv"},
        },
        'ITEM_PIPELINES': {'stock_market.pipelines.ScreenshotPipeline': 300}
    }

    def start_requests(self):

        # Get the companies list
        companies_file = Path('companies.json')
        with open(companies_file) as file:
            self.companies = json.load(file)

        # Extract the tickers from the first column
        xlsx_file = Path('Stock Market.xlsx')
        wb_obj = openpyxl.load_workbook(xlsx_file)
        sheet = wb_obj.active

        for row in sheet.iter_rows(min_row=2, max_row=5, max_col=1, values_only=True):
            # Create an item
            stock_market_item = StockMarketItem()
            # Get 'Ticker' field
            stock_market_item['Ticker'] = row[0]
            # Scrap dividends
            dividend_uri = self.companies[row[0]]['uri'] + 'dividend/'
            yield scrapy.Request(url=dividend_uri, callback=self.get_dividend,
                                 meta={'item': stock_market_item})
            # Scrap earnings
            # earnings_uri = self.companies[row[0]]['uri']
            # yield scrapy.Request(url=earnings_uri, callback=self.get_earnings, meta={'item': stock_market_item})

            # Scrap revenue chart
            # name = '-'.join([word for word in re.split(' |-', self.companies[row[0]]['name'].lower()) if word.isalnum()])
            # revenue_uri = f"https://www.macrotrends.net/stocks/charts/{row[0]}/{name}/revenue"
            # yield scrapy.Request(url=revenue_uri, callback=self.get_revenue_chart,
            #                      meta={'item': stock_market_item})

    def get_dividend(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        # Get 'Dividend (Amt)' field
        item_loader.add_css(
            'Dividend (Amt)',
            'div.d-flex.stat-summary-wrapper.justify-content-center.align-items-center.text-center.align-content-center.flex-wrap.shadow.mb-3.dividend-wrapper.py-1:nth-child(2) dd.stat-summary-heading.mt-2'
        )
        item_loader.load_item()
        # Scrap earnings
        earnings_uri = self.companies[item_loader.item['Ticker']]['uri']
        yield scrapy.Request(url=earnings_uri, callback=self.get_earnings,
                             meta={'item': item_loader.item})

    def get_earnings(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        # Get 'Nxt Earning dt' field
        item_loader.add_css(
            'Nxt Earning dt',
            'div.mt-3.mb-1.p-1.gradient-green.c-white + dl div.price-data:nth-child(6) dd.m-0'
        )
        item_loader.load_item()
        # Scrap revenue chart
        name = '-'.join([word for word in re.split(' |-', self.companies[item_loader.item['Ticker']]['name'].lower()) if
                         word.isalnum()])
        revenue_uri = f"https://www.macrotrends.net/stocks/charts/{item_loader.item['Ticker']}/" \
                      f"{name}/revenue"
        yield scrapy.Request(url=revenue_uri, callback=self.get_revenue_chart,
                             meta={'item': item_loader.item})

    def get_revenue_chart(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        # Get 'MacroTrend Revenue Link' field
        item_loader.add_value(
            'MacroTrend Revenue Link',
            response.url
        )
        # Get 'MacroTrend Net Income Link' field
        net_income_link = response.url.replace('revenue', 'net-income')
        item_loader.add_value('MacroTrend Net Income Link', net_income_link)

        # Get 'MacroTrend EPS Link' field
        eps_link = response.url.replace('revenue', 'eps-earnings-per-share-diluted')
        item_loader.add_value('MacroTrend EPS Link', eps_link)

        # Get 'MacroTrend Mkt Cap Link' field
        cap_link = response.url.replace('revenue', 'market-cap')
        item_loader.add_value('MacroTrend Mkt Cap Link', cap_link)

        # Get '12mo Rev Growth' field
        # revenue_12_growth = response.css('div#main_content div:nth-child(2) li:nth-child(2)')
        # if 'revenue for the twelve months' in revenue_12_growth.get():
        #     item_loader.add_css('12mo Rev Growth', 'div#main_content div:nth-child(2) li:nth-child(2) strong')


        # Scrap revenue data
        revenue_chart_uri = response.css('iframe#chart_iframe::attr(src)').get()
        item_loader.add_value(
            'Revenue',
            revenue_chart_uri
        )
        item_loader.load_item()


        yield scrapy.Request(url=revenue_chart_uri,
                             callback=self.get_revenue_data,
                             meta={'item': item_loader.item})


    def get_revenue_data(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        data_javascript = response.css('body > script::text').get()
        data = chompjs.parse_js_object(data_javascript)

        # Get '12 mo Revenue' field
        revenue_12_months = data[-1]['v1'] * 1000000000
        item_loader.add_value('12 mo Revenue', revenue_12_months)

        # Get '10yr Rev High / Low' and '10 Yr Rev High /Low  Dt' fields
        revenue_10_year_high = revenue_10_year_low = revenue_12_months
        revenue_10_year_high_date = revenue_10_year_low_date = data[-1]['date']
        for data_piece in data[-40:]:
            value = data_piece['v1'] * 1000000000
            if value >= revenue_10_year_high:
                revenue_10_year_high = value
                revenue_10_year_high_date = data_piece['date']
            if value <= revenue_10_year_low:
                revenue_10_year_low = value
                revenue_10_year_low_date = data_piece['date']
        item_loader.add_value('10yr Rev High', revenue_10_year_high)
        item_loader.add_value('10yr Rev Low', revenue_10_year_low)
        item_loader.add_value('10 Yr Rev High Dt', revenue_10_year_high_date)
        item_loader.add_value('10 Yr Rev Low Dt', revenue_10_year_low_date)

        # Get '12mo Rev Growth' field
        revenue_previous_12_months = data[-5]['v1'] * 1000000000
        if revenue_12_months > revenue_previous_12_months:
            revenue_12_growth = (revenue_12_months / revenue_previous_12_months - 1) * 100
        else:
            revenue_12_growth = (revenue_previous_12_months / revenue_12_months - 1) * -100

        item_loader.add_value('12mo Rev Growth', revenue_12_growth)

        # Get 'YoY Quarterly Rev Growth' field
        revenue_yoy_quarterly_growth = data[-1]['v3']
        item_loader.add_value('YoY Quarterly Rev Growth', revenue_yoy_quarterly_growth)

        # Get 'Q/Q Rev Growth' field
        revenue_q_q_growth = (data[-1]['v2'] / data[-2]['v2'] - 1) * 100
        item_loader.add_value('Q/Q Rev Growth', revenue_q_q_growth)

        item_loader.load_item()

        # Scrap net income data
        net_income_chart_uri = f"https://www.macrotrends.net/assets/php/fundamental_iframe.php?t={item_loader.item['Ticker']}&type=net-income&statement=income-statement&freq=Q"

        yield scrapy.Request(url=net_income_chart_uri,
                             callback=self.get_net_income_data,
                             meta={'item': item_loader.item})

    def get_net_income_data(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        data_javascript = response.css('body > script::text').get()
        data = chompjs.parse_js_object(data_javascript)

        # Get '12 mo Net Income' field
        net_income_12_months = data[-1]['v1'] * 1000000000
        item_loader.add_value('12 mo Net Income', net_income_12_months)

        # Get '10yr NI High / Low' and '10 Yr NI High /Low  Dt' fields
        net_income_10_year_high = net_income_10_year_low = net_income_12_months
        net_income_10_year_high_date = net_income_10_year_low_date = data[-1]['date']
        for data_piece in data[-40:]:
            value = data_piece['v1'] * 1000000000
            if value >= net_income_10_year_high:
                net_income_10_year_high = value
                net_income_10_year_high_date = data_piece['date']
            if value <= net_income_10_year_low:
                net_income_10_year_low = value
                net_income_10_year_low_date = data_piece['date']
        item_loader.add_value('10yr NI High', net_income_10_year_high)
        item_loader.add_value('10yr NI Low', net_income_10_year_low)
        item_loader.add_value('10 Yr NI High Dt', net_income_10_year_high_date)
        item_loader.add_value('10 Yr NI Low Dt', net_income_10_year_low_date)

        # Get '12 mo NI Growth' field
        net_income_previous_12_months = data[-5]['v1'] * 1000000000
        if net_income_12_months > net_income_previous_12_months:
            net_income_12_growth = (net_income_12_months / net_income_previous_12_months - 1) * 100
        else:
            net_income_12_growth = (net_income_previous_12_months / net_income_12_months - 1) * -100

        item_loader.add_value('12 mo NI Growth', net_income_12_growth)

        # Get 'YoY Quarterly NI Growth' field
        net_income_yoy_quarterly_growth = data[-1]['v3']
        item_loader.add_value('YoY Quarterly NI Growth', net_income_yoy_quarterly_growth)

        # Get 'Q/Q NI Growth' field
        net_income_q_q_growth = (data[-1]['v2'] / data[-2]['v2'] - 1) * 100
        item_loader.add_value('Q/Q NI Growth', net_income_q_q_growth)

        item_loader.load_item()

        # Scrap eps data
        esp_chart_uri = f"https://www.macrotrends.net/assets/php/fundamental_iframe.php?t={item_loader.item['Ticker']}&type=eps-earnings-per-share-diluted&statement=income-statement&freq=Q"

        yield scrapy.Request(url=esp_chart_uri,
                             callback=self.get_eps_data,
                             meta={'item': item_loader.item})


    def get_eps_data(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        data_javascript = response.css('body > script::text').get()
        data = chompjs.parse_js_object(data_javascript)

        # Get '12 mo EPS' field
        esp_12_months = data[-1]['v1']
        item_loader.add_value('12 mo EPS', esp_12_months)

        # Get '10yr EPS High / Low' and '10 Yr EPS High /Low  Dt' fields
        esp_10_year_high = esp_10_year_low = esp_12_months
        esp_10_year_high_date = esp_10_year_low_date = data[-1]['date']
        for data_piece in data[-40:]:
            value = data_piece['v1']
            if value >= esp_10_year_high:
                esp_10_year_high = value
                esp_10_year_high_date = data_piece['date']
            if value <= esp_10_year_low:
                esp_10_year_low = value
                esp_10_year_low_date = data_piece['date']
        item_loader.add_value('10yr EPS High', esp_10_year_high)
        item_loader.add_value('10yr EPS Low', esp_10_year_low)
        item_loader.add_value('10 Yr EPS High Dt', esp_10_year_high_date)
        item_loader.add_value('10 Yr EPS Low Dt', esp_10_year_low_date)

        # Get '12 mo EPS Growth' field
        esp_previous_12_months = data[-5]['v1']
        if esp_12_months > esp_previous_12_months:
            esp_12_growth = (esp_12_months / esp_previous_12_months - 1) * 100
        else:
            esp_12_growth = (esp_previous_12_months / esp_12_months - 1) * -100

        item_loader.add_value('12 mo EPS Growth', esp_12_growth)

        # Get 'YoY Quarterly EPS Growth' field
        esp_yoy_quarterly_growth = data[-1]['v3']
        item_loader.add_value('YoY Quarterly EPS Growth', esp_yoy_quarterly_growth)

        # Get 'Q/Q EPS Growth' field
        esp_q_q_growth = (data[-1]['v2'] / data[-2]['v2'] - 1) * 100
        item_loader.add_value('Q/Q EPS Growth', esp_q_q_growth)


        yield item_loader.load_item()

