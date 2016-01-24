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
    stockCodeSumNum = 2
    
    def GetJsonStockIndex(self,response):
        if('jsonStockIndex='==response.body[0:len('jsonStockIndex=')]):
            print '==============GetJsonStockIndex:',response.body, response.body[len('jsonStockIndex='):len(response.body)]
            return int(response.body[len('jsonStockIndex='):len(response.body)])        
        else:
            return -1  
        
    def generateUrl(self,url,stock,pageNum,jsonStockIndex):
        return url+'?stock='+stock+'&pageNum='+str(pageNum)+'&jsonStockIndex='+str(jsonStockIndex)
    
    def parse(self, response): 
        queryUrl='http://www.cninfo.com.cn/cninfo-new/announcement/query'
        jsonStockIndex = self.GetJsonStockIndex(response)
        print "start get stock data,jsonStockIndex=",jsonStockIndex,'self.stockCodeSumNum:',self.stockCodeSumNum
        if(0<=jsonStockIndex and jsonStockIndex<self.stockCodeSumNum):
            filename='szse_stock.json'
            jsonSzse_stocks=json.loads(open(filename, 'rb').read())
            if(2==self.stockCodeSumNum):                
                self.stockCodeSumNum=0
                for jsonSzse_stock in jsonSzse_stocks['stockList']:
                    self.stockCodeSumNum=self.stockCodeSumNum+1

            code=jsonSzse_stocks['stockList'][jsonStockIndex]['code']
            orgId=jsonSzse_stocks['stockList'][jsonStockIndex]['orgId']
            stock=jsonSzse_stocks['stockList'][jsonStockIndex]['code']+'%2C'+jsonSzse_stocks['stockList'][jsonStockIndex]['orgId']
            pageNum=1
            yield Request(self.generateUrl(queryUrl,stock,pageNum,jsonStockIndex), callback=self.parseDetail,meta={'code':code,'orgId':orgId,'pageNum':pageNum,'jsonStockIndex':jsonStockIndex}) 
        elif (jsonStockIndex==self.stockCodeSumNum):
            print '====================================='
            print 'fetch stock data finished,please check if have fail lists in result/szse_stock_failList.json'
            print '====================================='
        else:
            print '====================================='
            print 'fetch stock data fail,exit!!! jsonStockIndex=',jsonStockIndex,response.url,response.body
            print 'please check fail lists in result/szse_stock_failList.json'
            print '====================================='
    
    def parseDetail(self, response): 
        filename = 'result\szse_stock_failList.json'
        queryUrl='http://www.cninfo.com.cn/cninfo-new/announcement/query'
        startUrl='http://www.cninfo.com.cn/cninfo-new/announcement/show'
        print "********* enter parseDetail",response.url
        #filename = response.url.split("/")[-2]
        #open(filename, 'wb').write(response.body)
        jsonStockIndex = self.GetJsonStockIndex(response)
        if(-1==jsonStockIndex):
            #enter here only get data successful 
            jsonAnnouncements = json.loads(response.body_as_unicode()) 
            pageNum=jsonAnnouncements['pageNum']
            jsonStockIndex=jsonAnnouncements['jsonStockIndex']
            pageSumNums=0
            pageSize=30
            if(0==jsonAnnouncements['totalRecordNum']%pageSize):
                pageSumNums=jsonAnnouncements['totalRecordNum']/pageSize
            else:
                pageSumNums=(jsonAnnouncements['totalRecordNum']/pageSize+1)
            print 'totalRecordNum and current pageNum:',pageSumNums,pageNum
            for announcement in jsonAnnouncements['announcements']:
                code=announcement['secCode']
                orgId=announcement['orgId']
                stock=code+'%2C'+orgId
                
                #todo: download pdf
                
                print announcement['secCode'],announcement['secName'],announcement['announcementTitle'],announcement['adjunctUrl'],datetime.datetime.fromtimestamp(announcement['announcementTime']/1000).strftime("%Y-%m-%d")
            print "parseDetail: ########################################################"
            if(pageSumNums>pageNum):#go to read next page of current stock code
                pageNum=pageNum+1
                print "parseDetail: get next page:",str(pageNum),"pageSumNums:",str(pageSumNums)
                yield Request(self.generateUrl(queryUrl,stock,pageNum,jsonStockIndex), callback=self.parseDetail,meta={'code':code,'orgId':orgId,'pageNum':pageNum,'jsonStockIndex':jsonStockIndex}) 
            else:#go to read next stock code
                yield Request(self.generateUrl(startUrl, '', 1, jsonStockIndex+1), callback=self.parse, meta={'jsonStockIndex':jsonStockIndex+1}) 
        else:#fail to get current stock data, go to read next stock code
            
            yield Request(self.generateUrl(startUrl, '', 1, jsonStockIndex), callback=self.parse, meta={'jsonStockIndex':jsonStockIndex}) 

      
