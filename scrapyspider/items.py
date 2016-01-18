# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class ScrapyspiderItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass

class CninfoItem(Item):
    companyname = Field()
    #stockcode = Field()
    reportyear = Field()
    reportday = Field()
    downloadhref = Field()
	
