from scrapy.spider import Spider  
  
class DmozSpider(Spider):  
    name = "cninfo"  
    allowed_domains = ["cninfo.com.cn"]  
    start_urls = ["http://www.cninfo.com.cn/cninfo-new/index"]  
  
    def parse(self, response):  
        filename = response.url.split("/")[-2]  
        open(filename, 'wb').write(response.body)