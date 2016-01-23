from scrapy.spider import Spider  
from scrapy.selector import Selector
from scrapyspider.items import CninfoItem
import scrapy
from scrapy.http import Request
#from scrapy.http import FormRequest 
from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.by import By
import urllib2
import json
import datetime
import time
import os
  
class CninfoSpider(Spider):  
    name = "cninfo"  
    allowed_domains = ["cninfo.com.cn"]  
    start_urls = ["http://www.cninfo.com.cn/cninfo-new/announcement/show"]  
  
    def parse(self, response): 
        queryUrl='http://www.cninfo.com.cn/cninfo-new/announcement/query'
        if(queryUrl==response.url and 'start'==response.body): 
            print "start get stock data!!!!!"
            filename='szse_stock.json'
            jsonSzse_stocks=json.loads(open(filename, 'rb').read())
            for JsonStock in jsonSzse_stocks['stockList']:
                stock=JsonStock['code']+'%2C'+JsonStock['orgId']
                pageNum=1
                print stock,pageNum
                queryUrl = queryUrl+'?time='+str(time.time())
                yield Request(queryUrl, callback=self.parseDetail,meta={'stock':stock,'pageNum':pageNum}) 
            
        else:
            print response.url,response.body
            print "current dir:",os.getcwd()
    
    def parseDetail(self, response): 
        queryUrl='http://www.cninfo.com.cn/cninfo-new/announcement/query'
        print "********* enter parseDetail",response.url
        #filename = response.url.split("/")[-2]
        #open(filename, 'wb').write(response.body)
        
        if(''!=response.body): 
            jsonAnnouncements = json.loads(response.body_as_unicode()) 
            pageNum=jsonAnnouncements['pageNum']
            pageSumNums=0
            pageSize=30
            if(0==jsonAnnouncements['totalRecordNum']%pageSize):
                pageSumNums=jsonAnnouncements['totalRecordNum']/pageSize
            else:
                pageSumNums=(jsonAnnouncements['totalRecordNum']/pageSize+1)
            print jsonAnnouncements['totalRecordNum'],pageSumNums,pageNum
            print "parseDetail: ======================================================="
            for announcement in jsonAnnouncements['announcements']:
                stock=announcement['secCode']+'%2C'+announcement['orgId']
                
                #todo: download pdf
                
                print announcement['secCode'],announcement['secName'],announcement['announcementTitle'],announcement['adjunctUrl'],datetime.datetime.fromtimestamp(announcement['announcementTime']/1000).strftime("%Y-%m-%d")
            print "parseDetail: ########################################################"
            if(pageSumNums>pageNum):
                print "parseDetail: get next page:",str(pageNum),"pageSumNums:",str(pageSumNums)
                queryUrl = queryUrl+'?time='+str(time.time())               
                yield Request(queryUrl, callback=self.parseDetail,meta={'stock':stock,'pageNum':pageNum+1}) 

