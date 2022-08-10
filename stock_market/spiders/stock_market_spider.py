"""
To run script without Zyte change 7 occurrences of

 meta={'item': item_loader.item,
       "zyte_api": {"browserHtml": True,
                    "httpResponseBody": False, }})
for

 meta={'item': item_loader.item})
"""

import re
import json

import scrapy
import openpyxl
import chompjs

from datetime import datetime, timedelta
from pathlib import Path

from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst

from stock_market.items import StockMarketItem


class StockMarketSpider(scrapy.Spider):
    name = "stock_market"
    companies = []
    custom_settings = {
        'FEED_EXPORTERS': {
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

        for row in sheet.iter_rows(min_row=2, max_col=2, values_only=True):
            if row[0] is None:
                break
            # Create an item
            stock_market_item = StockMarketItem()
            # Get 'Ticker' field
            ticker = row[0]
            stock_market_item['Ticker'] = ticker
            # Get 'Exchange' field
            exchange = row[1]
            stock_market_item['Exchange'] = exchange
            # Get 'URL' field
            uri = f'https://www.marketbeat.com/stocks/{exchange}/{ticker}/'
            stock_market_item['URL'] = uri
            # Get 'Name' field
            company = self.companies.get(row[0], None)
            if company is not None and company['uri'] == uri:
                stock_market_item['Name'] = company['name']
                # Scrap dividends
                dividend_uri = uri + 'dividend/'
                yield scrapy.Request(
                    url=dividend_uri,
                    callback=self.get_dividend,
                    dont_filter=True,
                    meta={
                        'item': stock_market_item,
                    }
                )
            else:
                # Scrap company name
                url_request_uri = f'https://www.marketbeat.com/scripts/' \
                                  f'AutoComplete.ashx?searchquery={ticker}'
                yield scrapy.Request(
                    url=url_request_uri,
                    callback=self.get_company_url,
                    meta={
                        'item': stock_market_item,
                    }
                )

    def get_company_url(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)

        ticker = item_loader.item['Ticker']
        exchange = item_loader.item['Exchange']
        # Get 'URL' field
        data = json.loads(response.text)

        for data_piece in data:
            parsed_url = data_piece['data'].strip('/').split('/')
            company = parsed_url[-1]
            stocks = parsed_url[-2]
            if (data_piece['category'] == 'Companies' and
                    company == ticker and stocks == exchange):
                item_loader.add_value(
                    'Name',
                    data_piece['label']
                )
                break
        else:
            item_loader.add_value('Name', ticker)
            
        item_loader.load_item()
        # Scrap dividends
        dividend_uri = item_loader.item['URL'] + 'dividend/'
        return scrapy.Request(
            url=dividend_uri,
            callback=self.get_dividend,
            dont_filter=True,
            meta={
                'item': item_loader.item,
            }
        )

    def get_dividend(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        # Get 'Dividend (Amt)' field
        item_loader.add_css(
            'Dividend (Amt)',
            'div.d-flex.stat-summary-wrapper.justify-content-center.'
            'align-items-center.text-center.align-content-center.flex-wrap.'
            'shadow.mb-3.dividend-wrapper.py-1:nth-child(2) dd.'
            'stat-summary-heading.mt-2'
        )
        item_loader.load_item()
        # Scrap earnings
        earnings_uri = item_loader.item['URL'] + 'earnings/'
        return scrapy.Request(
            url=earnings_uri,
            callback=self.get_earnings,
            dont_filter=True,
            meta={
                'item': item_loader.item,
            }
        )

    def get_earnings(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        # Get 'Nxt Earning dt' field
        item_loader.add_css(
            'Nxt Earning dt',
            'table#earnings-history > tbody > tr:nth-child(1) > '
            'td:nth-child(1)'
        )
        item_loader.load_item()
        # Scrap revenue chart
        name = '-'.join(
            [word for word in re.split(
                ' |-',
                item_loader.item['Name'].lower()
            ) if word.isalnum()]
        )
        revenue_uri = f"https://www.macrotrends.net/stocks/charts/" \
                      f"{item_loader.item['Ticker']}/" \
                      f"{name}/revenue"
        return scrapy.Request(
            url=revenue_uri,
            callback=self.get_revenue_chart,
            meta={
                'item': item_loader.item,
            }
        )

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
        eps_link = response.url.replace(
            'revenue', 'eps-earnings-per-share-diluted'
        )
        item_loader.add_value('MacroTrend EPS Link', eps_link)

        # Get 'MacroTrend Mkt Cap Link' field
        cap_link = response.url.replace('revenue', 'market-cap')
        item_loader.add_value('MacroTrend Mkt Cap Link', cap_link)

        item_loader.load_item()

        # Scrap revenue data
        revenue_chart_uri = f"https://www.macrotrends.net/assets/php/" \
                            f"fundamental_iframe.php?t=" \
                            f"{item_loader.item['Ticker']}&type=revenue&" \
                            f"statement=income-statement&freq=Q"

        return scrapy.Request(
            url=revenue_chart_uri,
            callback=self.get_revenue_data,
            meta={
                'item': item_loader.item,
            }
        )

    def get_revenue_data(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        try:
            data_javascript = response.css('body > script::text').get()
            data = chompjs.parse_js_object(data_javascript)
    
            # Get '12 mo Revenue' field
            if self.null_checker(data[-1]['v1']):
                revenue_12_months = data[-1]['v1']
                item_loader.add_value('12 mo Revenue',
                                      revenue_12_months * 1000000000)
            else:
                revenue_12_months = None
         
            # Get '10yr Rev High / Low' and '10 Yr Rev High /Low  Dt' fields
            revenue_10_year_high = revenue_10_year_low = revenue_12_months
            revenue_10_year_high_date = revenue_10_year_low_date = data[-1][
                'date']
            for data_piece in data[-40:]:
                try:
                    value = data_piece['v1']
                    if (self.null_checker(value)
                            and revenue_10_year_high is None):
                        revenue_10_year_high = revenue_10_year_low = value
                    if (self.null_checker(value)
                            and value >= revenue_10_year_high):
                        revenue_10_year_high = value
                        revenue_10_year_high_date = data_piece['date']
                    if (self.null_checker(value)
                            and value <= revenue_10_year_low):
                        revenue_10_year_low = value
                        revenue_10_year_low_date = data_piece['date']
                except TypeError:
                    continue
            
            if revenue_10_year_high is not None:
                item_loader.add_value('10yr Rev High',
                                      revenue_10_year_high * 1000000000)
                item_loader.add_value('10 Yr Rev High Dt',
                                      revenue_10_year_high_date)
            if revenue_10_year_low is not None:
                item_loader.add_value('10yr Rev Low',
                                      revenue_10_year_low * 1000000000)
                item_loader.add_value('10 Yr Rev Low Dt',
                                      revenue_10_year_low_date)
    
            # Get '12mo Rev Growth' field
            for data_piece in data[-5:]:
                try:
                    revenue_previous_12_months = data_piece['v1']
                    if revenue_12_months > revenue_previous_12_months:
                        revenue_12_growth = (revenue_12_months
                                             / revenue_previous_12_months
                                             - 1) * 1
                    else:
                        revenue_12_growth = (revenue_previous_12_months
                                             / revenue_12_months - 1) * -1

                    item_loader.add_value('12mo Rev Growth', revenue_12_growth)
                    break
                except TypeError:
                    continue
    
            # Get 'YoY Quarterly Rev Growth' field
            try:
                revenue_yoy_quarterly_growth = data[-1]['v3']/100
                item_loader.add_value(
                    'YoY Quarterly Rev Growth', revenue_yoy_quarterly_growth
                )
            except TypeError:
                pass
                
            # Get 'Q/Q Rev Growth' field
            try:
                revenue_q_q_growth = (data[-1]['v2'] / data[-2]['v2'] - 1) * 1
                item_loader.add_value('Q/Q Rev Growth', revenue_q_q_growth)
            except TypeError:
                pass
            
            item_loader.load_item()
        except:
            pass

        # Scrap net income data
        net_income_chart_uri = f"https://www.macrotrends.net/assets/php/" \
                               f"fundamental_iframe.php?t=" \
                               f"{item_loader.item['Ticker']}&type=" \
                               f"net-income&statement=income-statement&freq=Q"

        return scrapy.Request(
            url=net_income_chart_uri,
            callback=self.get_net_income_data,
            meta={
                'item': item_loader.item,
            }
        )

    def get_net_income_data(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        try:
            data_javascript = response.css('body > script::text').get()
            data = chompjs.parse_js_object(data_javascript)
    
            # Get '12 mo Net Income' field
            if self.null_checker(data[-1]['v1']):
                net_income_12_months = data[-1]['v1']
                item_loader.add_value('12 mo Net Income',
                                      net_income_12_months * 1000000000)
            else:
                net_income_12_months = None

            # Get '10yr NI High / Low' and '10 Yr NI High /Low  Dt' fields
            net_income_10_year_high = net_income_10_year_low = \
                net_income_12_months
            net_income_10_year_high_date = net_income_10_year_low_date = \
                data[-1]['date']
            for data_piece in data[-40:]:
                try:
                    value = data_piece['v1']
                    if (self.null_checker(value)
                            and net_income_10_year_high is None):
                        net_income_10_year_high = net_income_10_year_low = \
                            value
                    if (self.null_checker(value)
                            and value >= net_income_10_year_high):
                        net_income_10_year_high = value
                        net_income_10_year_high_date = data_piece['date']
                    if (self.null_checker(value)
                            and value <= net_income_10_year_low):
                        net_income_10_year_low = value
                        net_income_10_year_low_date = data_piece['date']
                except TypeError:
                    continue

            if net_income_10_year_high is not None:
                item_loader.add_value('10yr NI High',
                                      net_income_10_year_high * 1000000000)
                item_loader.add_value('10 Yr NI High Dt',
                                      net_income_10_year_high_date)
            if net_income_10_year_low is not None:
                item_loader.add_value('10yr NI Low',
                                      net_income_10_year_low * 1000000000)
                item_loader.add_value('10 Yr NI Low Dt',
                                      net_income_10_year_low_date)
    
            # Get '12 mo NI Growth' field
            for data_piece in data[-5:]:
                try:
                    net_income_previous_12_months = data_piece['v1']
                    net_income_12_growth = (net_income_12_months - net_income_previous_12_months) / abs(net_income_previous_12_months)
                    item_loader.add_value('12 mo NI Growth',
                                          net_income_12_growth)
                    # net_income_previous_12_months = data_piece['v1']
                    # if net_income_12_months > net_income_previous_12_months:
                    #     net_income_12_growth = (net_income_12_months
                    #                             / net_income_previous_12_months
                    #                             - 1) * 1
                    # else:
                    #     net_income_12_growth = (net_income_previous_12_months
                    #                             / net_income_12_months
                    #                             - 1) * -1
                    # item_loader.add_value('12 mo NI Growth',
                    #                       net_income_12_growth)
                    break
                except TypeError:
                    continue

            # Get 'YoY Quarterly NI Growth' field
            net_income_yoy_quarterly_growth = None
            try:
                net_income_yoy_quarterly_growth = data[-1]['v3']/100
            except TypeError:
                net_income_current_q = data[-1]['v2'] * 1000000000
    
                for data_piece in data[-5:]:
                    try:
                        net_income_previous_4_q = data_piece['v2'] * 1000000000
                        if net_income_current_q > net_income_previous_4_q:
                            net_income_yoy_quarterly_growth = abs(
                                (net_income_current_q / net_income_previous_4_q
                                 - 1))
                        else:
                            net_income_yoy_quarterly_growth = -abs(
                                (net_income_current_q / net_income_previous_4_q
                                 - 1))
                        break
                    except TypeError:
                        continue
            if net_income_yoy_quarterly_growth is not None:
                item_loader.add_value('YoY Quarterly NI Growth',
                                      net_income_yoy_quarterly_growth)
    
            # Get 'Q/Q NI Growth' field
            try:
                net_income_q_q_growth = (data[-1]['v2'] / data[-2]['v2']
                                         - 1) * 1
                item_loader.add_value('Q/Q NI Growth', net_income_q_q_growth)
            except TypeError:
                pass
            
            item_loader.load_item()
        except:
            pass

        # Scrap eps data
        esp_chart_uri = f"https://www.macrotrends.net/assets/php/" \
                        f"fundamental_iframe.php?t=" \
                        f"{item_loader.item['Ticker']}&type=" \
                        f"eps-earnings-per-share-diluted&statement=" \
                        f"income-statement&freq=Q"

        return scrapy.Request(
            url=esp_chart_uri,
            callback=self.get_eps_data,
            meta={
                'item': item_loader.item,
            }
        )

    def get_eps_data(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        try:
            data_javascript = response.css('body > script::text').get()
            data = chompjs.parse_js_object(data_javascript)
    
            # Get '12 mo EPS' field
            if self.null_checker(data[-1]['v1']):
                esp_12_months = data[-1]['v1']
                item_loader.add_value('12 mo EPS', esp_12_months)
            else:
                esp_12_months = None
    
            # Get '10yr EPS High / Low' and '10 Yr EPS High /Low  Dt' fields
            esp_10_year_high = esp_10_year_low = esp_12_months
            esp_10_year_high_date = esp_10_year_low_date = data[-1]['date']
            for data_piece in data[-40:]:
                try:
                    value = data_piece['v1']
                    if self.null_checker(value) and esp_10_year_high is None:
                        esp_10_year_high = esp_10_year_low = value
                    if self.null_checker(value) and value >= esp_10_year_high:
                        esp_10_year_high = value
                        esp_10_year_high_date = data_piece['date']
                    if self.null_checker(value) and value <= esp_10_year_low:
                        esp_10_year_low = value
                        esp_10_year_low_date = data_piece['date']
                except TypeError:
                    continue

            if esp_10_year_high is not None:
                item_loader.add_value('10yr EPS High', esp_10_year_high)
                item_loader.add_value('10 Yr EPS High Dt',
                                      esp_10_year_high_date)
            if esp_10_year_low is not None:
                item_loader.add_value('10yr EPS Low', esp_10_year_low)
                item_loader.add_value('10 Yr EPS Low Dt', esp_10_year_low_date)
    
            # Get '12 mo EPS Growth' field
            for data_piece in data[-5:]:
                try:
                    esp_previous_12_months = data_piece['v1']
                    esp_12_growth = (esp_12_months - esp_previous_12_months) / abs(esp_previous_12_months)
                    item_loader.add_value('12 mo EPS Growth', esp_12_growth)
                    # esp_previous_12_months = data_piece['v1']
                    # if esp_12_months > esp_previous_12_months:
                    #     esp_12_growth = (esp_12_months / esp_previous_12_months
                    #                      - 1) * 1
                    # else:
                    #     esp_12_growth = (esp_previous_12_months / esp_12_months
                    #                      - 1) * -1
                    # item_loader.add_value('12 mo EPS Growth', esp_12_growth)
                    break
                except TypeError:
                    continue

            # Get 'YoY Quarterly EPS Growth' field
            esp_yoy_quarterly_growth = None
            try:
                esp_yoy_quarterly_growth = data[-1]['v3']/100
            except TypeError:
                esp_current_q = data[-1]['v2'] * 1000000000
    
                for data_piece in data[-5:]:
                    try:
                        esp_previous_4_q = data_piece['v2'] * 1000000000
                        if esp_current_q > esp_previous_4_q:
                            esp_yoy_quarterly_growth = abs(
                                (esp_current_q / esp_previous_4_q - 1))
                        else:
                            esp_yoy_quarterly_growth = -abs(
                                (esp_current_q / esp_previous_4_q - 1))
                        break
                    except TypeError:
                        continue
            if esp_yoy_quarterly_growth is not None:
                item_loader.add_value('YoY Quarterly EPS Growth',
                                      esp_yoy_quarterly_growth)
    
            # Get 'Q/Q EPS Growth' field
            try:
                esp_q_q_growth = (data[-1]['v2'] / data[-2]['v2'] - 1) * 1
                item_loader.add_value('Q/Q EPS Growth', esp_q_q_growth)
            except TypeError:
                pass
    
            item_loader.load_item()
        except:
            pass
        
        # Scrap price sales data
        price_sales_chart_uri = f"https://www.macrotrends.net/assets/php/" \
                                f"fundamental_iframe.php?t=" \
                                f"{item_loader.item['Ticker']}&type=" \
                                f"price-sales&statement=price-ratios&freq=Q"

        return scrapy.Request(
            url=price_sales_chart_uri,
            callback=self.get_price_sales_data,
            meta={
                'item': item_loader.item,
            }
        )

    def get_price_sales_data(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        try:
            data_javascript = response.css('body > script::text').get()
            data = chompjs.parse_js_object(data_javascript)
    
            # Get '10 Yr High / Low P/S' fields
            # try:
            #     price_sales_10_year_high = price_sales_10_year_low = \
            #         data[-40]['v3']
            # except IndexError:
            #     price_sales_10_year_high = price_sales_10_year_low = \
            #         data[0]['v3']

            price_sales_10_year_high = price_sales_10_year_low = None
            
            for data_piece in data[-40:]:
                try:
                    value = data_piece['v3']
                    if (self.null_checker(value)
                            and price_sales_10_year_high is None):
                        price_sales_10_year_high = price_sales_10_year_low = \
                            value
                    if (self.null_checker(value)
                            and value >= price_sales_10_year_high):
                        price_sales_10_year_high = value
                    if (self.null_checker(value)
                            and value <= price_sales_10_year_low):
                        price_sales_10_year_low = value
                except TypeError:
                    continue
            
            if price_sales_10_year_high is not None:
                item_loader.add_value('10 Yr High P/S',
                                      price_sales_10_year_high)
            if price_sales_10_year_low is not None:
                item_loader.add_value('10 Yr Low P/S',
                                      price_sales_10_year_low)

            item_loader.load_item()
        except:
            pass

        # Scrap pe ratio data
        pe_ratio_chart_uri = f"https://www.macrotrends.net/assets/php/" \
                             f"fundamental_iframe.php?t=" \
                             f"{item_loader.item['Ticker']}&type=pe-ratio&" \
                             f"statement=price-ratios&freq=Q"

        return scrapy.Request(
            url=pe_ratio_chart_uri,
            callback=self.get_pe_ratio_data,
            meta={
                'item': item_loader.item,
            }
        )

    def get_pe_ratio_data(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        try:
            data_javascript = response.css('body > script::text').get()
            data = chompjs.parse_js_object(data_javascript)
    
            # Get '10 Yr High / Low P/E' fields
            # try:
            #     pe_ratio_10_year_high = pe_ratio_10_year_low = data[-40]['v3']
            # except IndexError:
            #     pe_ratio_10_year_high = pe_ratio_10_year_low = data[0]['v3']

            pe_ratio_10_year_high = pe_ratio_10_year_low = None

            for data_piece in data[-40:]:
                try:
                    value = data_piece['v3']
                    if self.null_checker(
                            value) and pe_ratio_10_year_high is None:
                        pe_ratio_10_year_high = pe_ratio_10_year_low =\
                            value
                    if self.null_checker(
                            value) and value >= pe_ratio_10_year_high:
                        pe_ratio_10_year_high = value
                    if self.null_checker(
                            value) and value <= pe_ratio_10_year_low:
                        pe_ratio_10_year_low = value
                except TypeError:
                    continue

            if pe_ratio_10_year_high is not None:
                item_loader.add_value('10 Yr High P/E',
                                      pe_ratio_10_year_high)
            if pe_ratio_10_year_low is not None:
                item_loader.add_value('10 Yr Low P/E', pe_ratio_10_year_low)

            item_loader.load_item()
        except:
            pass

        # Scrap market cap data
        market_cap_chart_uri = f"https://www.macrotrends.net/assets/php/" \
                               f"market_cap.php?t={item_loader.item['Ticker']}"

        return scrapy.Request(
            url=market_cap_chart_uri,
            callback=self.get_market_cap_data,
            meta={
                'item': item_loader.item,
            }
        )

    def get_market_cap_data(self, response):
        item_loader = ItemLoader(item=response.request.meta['item'],
                                 default_output_processor=TakeFirst(),
                                 selector=response)
        try:
            data_javascript = response.css('body > script::text').get()
            data = chompjs.parse_js_object(data_javascript)
    
            latest_chart_date = data[-1]['date']
            latest_chart_date_time_obj = datetime.strptime(latest_chart_date,
                                                           '%Y-%m-%d')
            # Get '10yr Mkt Cap High / Low' and '10 Yr High / Low  Dt' fields
            i = 0
            for data_piece in data:
                chart_date = data_piece['date']
                chart_date_time_obj = datetime.strptime(chart_date, '%Y-%m-%d')
    
                if (latest_chart_date_time_obj - chart_date_time_obj >
                        timedelta(days=10 * 365)):
                    i += 1
                    continue
                elif self.null_checker(data_piece['v1']):
                    market_cap_10_year_high = market_cap_10_year_low = \
                        data_piece['v1']
                    market_cap_10_year_high_date = \
                        market_cap_10_year_low_date = data_piece['date']
                    i += 1
                    break
                else:
                    i += 1
                    continue
            else:
                market_cap_10_year_high = market_cap_10_year_low = None
                market_cap_10_year_high_date = market_cap_10_year_low_date = \
                    None
                
            for data_piece in data[i:]:
                try:
                    value = data_piece['v1']
                    if (self.null_checker(value)
                            and market_cap_10_year_high is None):
                        market_cap_10_year_high = market_cap_10_year_low = \
                            value
                    if (self.null_checker(value)
                            and value >= market_cap_10_year_high):
                        market_cap_10_year_high = value
                        market_cap_10_year_high_date = data_piece['date']
                    if (self.null_checker(value)
                            and value <= market_cap_10_year_low):
                        market_cap_10_year_low = value
                        market_cap_10_year_low_date = data_piece['date']
                except TypeError:
                    continue
            
            if market_cap_10_year_high is not None:
                item_loader.add_value('10yr Mkt Cap High',
                                      market_cap_10_year_high * 1000000000)
                item_loader.add_value('10Yr High Dt',
                                      market_cap_10_year_high_date)
            if market_cap_10_year_low is not None:
                item_loader.add_value('10yr Mkt Cap Low',
                                      market_cap_10_year_low * 1000000000)
                item_loader.add_value('10Yr Low Dt',
                                      market_cap_10_year_low_date)

        except:
            pass

        return item_loader.load_item()
    
    @staticmethod
    def null_checker(value):
        if value == 'NULL' or value is None:
            return False
        else:
            return True
