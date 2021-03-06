# Scrapy settings for scrapyspider project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'scrapyspider'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['scrapyspider.spiders']
NEWSPIDER_MODULE = 'scrapyspider.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
RETRY_TIMES=0
DOWNLOADER_MIDDLEWARES = {
    'scrapyspider.middlewares.CninfoGetAnnouncementMiddleware': 543
 }
#ITEM_PIPELINES = {  
 #   'scrapyspider.pipelines.ScrapyspiderPipeline':300  
#}  
