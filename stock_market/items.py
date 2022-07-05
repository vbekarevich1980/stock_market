# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst, Compose
from w3lib.html import remove_tags


class StockMarketItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    def __init__(self):
        super().__init__()
        self.fields['Ticker'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['Dividend (Amt)'] = scrapy.Field(
            input_processor=MapCompose(remove_tags),
            output_processor=TakeFirst())
        self.fields['Nxt Earning dt'] = scrapy.Field(
            input_processor=MapCompose(remove_tags),
            output_processor=TakeFirst())
        self.fields['MacroTrend Revenue Link'] = scrapy.Field()
        self.fields['12 mo Revenue'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['10yr Rev High'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['10yr Rev Low'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['10 Yr Rev High Dt'] = scrapy.Field(output_processor=TakeFirst())
        self.fields['10 Yr Rev Low Dt'] = scrapy.Field(output_processor=TakeFirst())
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
            output_processor=TakeFirst())
        self.fields['10 Yr NI Low Dt'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['12 mo NI Growth'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['YoY Quarterly NI Growth'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['Q/Q NI Growth'] = scrapy.Field(
            output_processor=TakeFirst())
        self.fields['MacroTrend EPS Link'] = scrapy.Field(output_processor=TakeFirst())




        self.fields['MacroTrend Mkt Cap Link'] = scrapy.Field(output_processor=TakeFirst())




        self.fields['Revenue'] = scrapy.Field(output_processor=TakeFirst())

        # self.fields['SKU'] = scrapy.Field(
        #     input_processor=MapCompose(remove_tags),
        #     output_processor=TakeFirst())
        # self.fields['Category'] = scrapy.Field(
        #     input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        #     output_processor=TakeFirst())
        # self.fields['Subcategory'] = scrapy.Field(
        #     input_processor=MapCompose(remove_tags),
        #     output_processor=TakeFirst())
        # self.fields['Short Description'] = scrapy.Field(
        #     input_processor=MapCompose(remove_tags), output_processor=Join(
        #         ' '))  # Need to fix to have whitespaces and remove
        # # 'Description' word
        # self.fields['Long Description'] = scrapy.Field(
        #     input_processor=MapCompose(remove_tags,
        #                                lambda x: ': '.join(x.split(':'))),
        #     output_processor=Join(', '))
        # self.fields['Featured Image URL'] = scrapy.Field(
        #     output_processor=TakeFirst()
        #
        #     )
        # self.fields['Images URLs'] = scrapy.Field(output_processor=Join(', ')
        #
        #                                           )
        # self.fields['Product URL'] = scrapy.Field(
        #     input_processor=MapCompose(remove_tags),
        #     output_processor=TakeFirst())
