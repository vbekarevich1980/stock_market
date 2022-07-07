# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst, Compose
from w3lib.html import remove_tags
import datetime


class StockMarketItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    def __init__(self):
        super().__init__()
        self.fields['Ticker'] = scrapy.Field(output_processor=TakeFirst())

        self.fields['Dividend (Amt)'] = scrapy.Field(
            input_processor=MapCompose(remove_tags, lambda x: float(x.strip('$'))),
            output_processor=TakeFirst())
        self.fields['Nxt Earning dt'] = scrapy.Field(
            input_processor=MapCompose(remove_tags, lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').strftime('%d.%m.%Y')),
            output_processor=TakeFirst())

        self.fields['MacroTrend Revenue Link'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['12 mo Revenue'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['10yr Rev High'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['10yr Rev Low'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['10 Yr Rev High Dt'] = scrapy.Field(
            input_processor=MapCompose(
                lambda x:
                datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%d.%m.%Y')
            ),
            output_processor=TakeFirst()
        )
        self.fields['10 Yr Rev Low Dt'] = scrapy.Field(
            input_processor=MapCompose(
                lambda x:
                datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%d.%m.%Y')
            ),
            output_processor=TakeFirst()
        )
        self.fields['12mo Rev Growth'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['YoY Quarterly Rev Growth'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['Q/Q Rev Growth'] = scrapy.Field(output_processor=TakeFirst())

        self.fields['MacroTrend Net Income Link'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['12 mo Net Income'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['10yr NI High'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['10yr NI Low'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['10 Yr NI High Dt'] = scrapy.Field(
            input_processor=MapCompose(
                lambda x:
                datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%d.%m.%Y')
            ),
            output_processor=TakeFirst()
        )
        self.fields['10 Yr NI Low Dt'] = scrapy.Field(
            input_processor=MapCompose(
                lambda x:
                datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%d.%m.%Y')
            ),
            output_processor=TakeFirst()
        )
        self.fields['12 mo NI Growth'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['YoY Quarterly NI Growth'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['Q/Q NI Growth'] = scrapy.Field(
            output_processor=TakeFirst())

        self.fields['MacroTrend EPS Link'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['12 mo EPS'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['10yr EPS High'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['10yr EPS Low'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['10 Yr EPS High Dt'] = scrapy.Field(
            input_processor=MapCompose(
                lambda x:
                datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%d.%m.%Y')
            ),
            output_processor=TakeFirst()
        )
        self.fields['10 Yr EPS Low Dt'] = scrapy.Field(
            input_processor=MapCompose(
                lambda x:
                datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%d.%m.%Y')
            ),
            output_processor=TakeFirst()
        )
        self.fields['12 mo EPS Growth'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['YoY Quarterly EPS Growth'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['Q/Q EPS Growth'] = scrapy.Field(
            output_processor=TakeFirst())

        self.fields['10 Yr High P/S'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['10 Yr Low P/S'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['10 Yr High P/E'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['10 Yr Low P/E'] = scrapy.Field(
            output_processor=TakeFirst())

        self.fields['MacroTrend Mkt Cap Link'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['10yr Mkt Cap High'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['10yr Mkt Cap Low'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['10Yr High Dt'] = scrapy.Field(
            input_processor=MapCompose(
                lambda x:
                datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%d.%m.%Y')
            ),
            output_processor=TakeFirst()
        )
        self.fields['10Yr Low Dt'] = scrapy.Field(
            input_processor=MapCompose(
                lambda x:
                datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%d.%m.%Y')
            ),
            output_processor=TakeFirst()
        )
