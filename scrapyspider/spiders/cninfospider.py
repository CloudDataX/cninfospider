from scrapy.spider import Spider  
from scrapy.selector import Selector
from scrapyspider.items import CninfoItem

  
class CninfoSpider(Spider):  
    name = "cninfo"  
    allowed_domains = ["cninfo.com.cn"]  
    start_urls = ["http://www.cninfo.com.cn/cninfo-new/disclosure/sse/bulletin_detail/true/1200932228?announceTime=2015-04-29"]  
  
    def parse(self, response):  
        sel = Selector(response)  

        item = CninfoItem()

        item['companyinfo'] = sel.xpath('//div[@class="bd-top"]/h2/text()').extract()
        item['reportyear'] = sel.xpath('//div[@class="year"]/text()').extract()
        item['reportday'] = sel.xpath('//div[@class="day"]/text()').extract()
        item['downloadhref'] = sel.xpath('//div[@class="btn-blue bd-btn"]/a/@href').extract()

        return item  