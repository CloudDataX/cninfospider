# -*- coding:utf-8 -*-
from scrapy.spider import Spider  
from scrapy.selector import Selector
from scrapyspider.items import CninfoItem
import scrapy
from scrapy.http import Request
#from scrapy.http import FormRequest 
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.by import By
import urllib2
import json
import datetime
import time
import os
import urllib
import re
import codecs
import platform


class CninfoSpider(Spider):  
    name = "cninfo"  
    allowed_domains = ["cninfo.com.cn"]  
    start_urls = ["http://www.cninfo.com.cn/cninfo-new/disclosure/szse_main"]
    allstockjson_url = "http://www.cninfo.com.cn/cninfo-new/js/data/szse_stock.json"
    stockNumsInAllStockJson = 0
    homePage = r"http://www.cninfo.com.cn"  
    financialFolder = ''
    savedInfoFile = ''
    savedStockSumNum = 0
    
    def GetJsonStockIndex(self,response):
        if('jsonStockIndex='==response.body[0:len('jsonStockIndex=')]):
            print '==============GetJsonStockIndex:',response.body, response.body[len('jsonStockIndex='):len(response.body)]
            return int(response.body[len('jsonStockIndex='):len(response.body)])        
        else:
            return -1  
        
    def generateUrl(self,url,stock,pageNum,jsonStockIndex):
        return url+'?stock='+stock+'&pageNum='+str(pageNum)+'&jsonStockIndex='+str(jsonStockIndex)
    
    def parse(self, response):
        self.createFinancialDataFolder() 
        allStockJsonPath = self.downloadAllStockJson()
        queryUrl='http://www.cninfo.com.cn/cninfo-new/announcement/query'
        jsonStockIndex = self.GetJsonStockIndex(response)
        print "start get stock data,jsonStockIndex=",jsonStockIndex,'self.stockNumsInAllStockJson:',self.stockNumsInAllStockJson
        
        jsonSzse_stocks=json.loads(open(allStockJsonPath, 'rb').read())
        if self.stockNumsInAllStockJson == 0:
            for jsonSzse_stock in jsonSzse_stocks['stockList']:
                self.stockNumsInAllStockJson=self.stockNumsInAllStockJson+1
                    
        if(0<=jsonStockIndex and jsonStockIndex<self.stockNumsInAllStockJson):      
              
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
            savedInfo = {"secCode": " ","secName": " ","announcementTitle": " ","adjunctUrl": " ","pdfPath": " ","announcementTime": " "}
            if(0==jsonAnnouncements['totalRecordNum']%pageSize):
                pageSumNums=jsonAnnouncements['totalRecordNum']/pageSize
            else:
                pageSumNums=(jsonAnnouncements['totalRecordNum']/pageSize+1)
            print 'totalRecordNum and current pageNum:',pageSumNums,pageNum
            for announcement in jsonAnnouncements['announcements']:
                code=announcement['secCode']
                orgId=announcement['orgId']
                stock=code+'%2C'+orgId
                
                #Skip not needed pdf
                if not self.isNeededAnnouncementTitle(announcement['announcementTitle']):
                    continue
                
                #Download pdf
                companyFolder = self.createCompanyFolder(announcement['secCode'])
                if announcement["secName"] == None or announcement['announcementTitle'] == None:
                    pdfname = announcement['announcementTitle']
                else:
                    pdfname = announcement["secName"]+announcement['announcementTitle']
                pdfPath = self.downloadPDF(companyFolder, pdfname,announcement['adjunctUrl'])
                
                #save info in Json
                savedInfo['secCode'] = announcement['secCode']
                savedInfo['secName'] = announcement['secName']
                savedInfo['announcementTitle'] = announcement['announcementTitle']
                savedInfo['adjunctUrl'] = announcement['adjunctUrl']
                savedInfo['pdfPath'] = pdfPath
                savedInfo['announcementTime'] = announcement['announcementTime']
                #savedInfo['announcementTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(announcement['announcementTime']))
                if not self.isInfoInJson(savedInfo):
                    try:
                        savedInfofileread = codecs.open(self.savedInfoFile,'rb','utf-8')
                        readdata = savedInfofileread.read()[:-2]
                        if(20<len(readdata)):
                            readdata=readdata+','
                        writedata = json.dumps(savedInfo,ensure_ascii=False,indent=2)
                        writedata = readdata+writedata+']}'
                        savedInfofilewrite = codecs.open(self.savedInfoFile,'w','utf-8')
                        savedInfofilewrite.write(writedata)
                    finally:
                        savedInfofilewrite.close()
            
            print "parseDetail: ########################################################"
            if(pageSumNums>pageNum):#go to read next page of current stock code
                pageNum=pageNum+1
                print "parseDetail: get next page:",str(pageNum),"pageSumNums:",str(pageSumNums)
                yield Request(self.generateUrl(queryUrl,stock,pageNum,jsonStockIndex), callback=self.parseDetail,meta={'code':code,'orgId':orgId,'pageNum':pageNum,'jsonStockIndex':jsonStockIndex}) 
            else:#go to read next stock code
                yield Request(self.generateUrl(startUrl, '', 1, jsonStockIndex+1), callback=self.parse, meta={'jsonStockIndex':jsonStockIndex+1}) 
        else:#fail to get current stock data, go to read next stock code
            
            yield Request(self.generateUrl(startUrl, '', 1, jsonStockIndex), callback=self.parse, meta={'jsonStockIndex':jsonStockIndex}) 

    def createCompanyFolder(self, secCode):
        if "Windows" == platform.system():
            companyFolder = self.financialFolder + '\\' + secCode
        else:
            companyFolder = self.financialFolder + '/' + secCode
        if not os.path.exists(companyFolder):
            os.mkdir(companyFolder)
        return companyFolder
            
    def downloadPDF(self, companyFolder, reportName, downloadURL):
        if "Windows" == platform.system():
            pdfPath = companyFolder + '\\' + reportName + '.pdf'
        else:
            pdfPath = companyFolder + '/' + reportName + '.pdf'
        
        realURL = self.homePage + "/" + downloadURL
        print "Download PDF. pdfPath:", pdfPath, ' realURL:',realURL
        try:
            if not os.path.exists(pdfPath):
                urllib.urlretrieve(realURL, pdfPath)
            else:
                print 'WRN: ', reportName, '.pdf is already exists'
                return pdfPath
        except IOError:
            print "ERROR: save pdf fail"
            return None
        return pdfPath

    def isInfoInJson(self, announcement):
        try:
            savedInfofile=json.loads(codecs.open(self.savedInfoFile,'r','utf-8').read())
            
            if 5 > len(savedInfofile["stockList"]):
                return False
            else:
                for jsonSzse_stock in savedInfofile['stockList']:
                    self.savedStockSumNum=self.savedStockSumNum+1
                print "-------------",len(savedInfofile['stockList'])
                for index in range(self.savedStockSumNum):
                    if savedInfofile["stockList"][index]['secCode'] == announcement['secCode'] and savedInfofile["stockList"][index]['announcementTitle'] == announcement['announcementTitle']:
                        print "WRN stock report already exist", announcement['secCode'],announcement['announcementTitle']
                        return True
        except Exception,e:
            print e
            
        return False
    
    def isNeededAnnouncementTitle(self, announcementTitle):
        print "isNeedAnnouncementTitle:", announcementTitle
        filter1 = announcementTitle.find(u"摘要") 
        filter2 = announcementTitle.find(u"英文版")
        filter3 = announcementTitle.find(u"正文")
        if filter1 != -1 or filter2 != -1 or filter3 != -1:
            print "isNeedAnnouncementTitle: False"
            return False
        else:
            print "isNeedAnnouncementTitle: True"
            return True
        
    def createFinancialDataFolder(self):
        sysstr = platform.system()
        if(sysstr =="Windows"):
            print "!!!Windows"
            self.financialFolder = r'D:\financialdata'
            self.savedInfoFile = self.financialFolder + '\\' + 'stockreportlist.json'
            failReportPath = self.financialFolder + '\\' + 'szse_stock_failList.json'
        elif(sysstr == "Linux"):
            print "!!Linux"
            self.financialFolder = r'/home/xproject/financialdata' 
            self.savedInfoFile = self.financialFolder + '/' + 'stockreportlist.json'       
            failReportPath = self.financialFolder + '/' + 'szse_stock_failList' + '.json'                       
        else:
            print "Other System tasks"
        
        if (False == os.path.exists(self.financialFolder)):
            os.makedirs(self.financialFolder)
        
        if (False == os.path.exists(self.savedInfoFile)):
            f= codecs.open(self.savedInfoFile,'w','utf-8')
            writeData = '{"stockList":[]}'
            f.write(writeData)
            f.close()
            
        if (False == os.path.exists(failReportPath)):
            f= codecs.open(failReportPath,'w','utf-8')
            writeData = '{"stockList":[]}'
            f.write(writeData)
            f.close()
            
            
    def downloadAllStockJson(self):
        if "Windows" == platform.system():
            allStockJsonPath = self.financialFolder + '\\' + 'szse_stock.json'
            
        else:
            allStockJsonPath = self.financialFolder + '/' + 'szse_stock.json'

        print "!!!!!!allStockJsonPath:",allStockJsonPath 
        try:
            urllib.urlretrieve(self.allstockjson_url, allStockJsonPath)
            return allStockJsonPath
        except IOError:
            print "DownLoad AllStockJson fail"
            return None