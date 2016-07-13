#! -*- coding:utf-8 -*-
# encoding: utf-8
from scrapy.http import HtmlResponse
import logging
import time
import urllib
import urllib2
import httplib
import cookielib
from urllib import urlencode
from urllib import unquote
import json
import os
logger = logging.getLogger('CninfoGetAnnouncementMiddleware')
class CninfoGetAnnouncementMiddleware(object):
    def __init__(self, options, max_sum):
        self.options = options
        self.max_sum = max_sum
        
        #filename = 'result\szse_stock_failList.json'
        #remove result files at begiin
        #if (os.path.isfile(filename)):
        #    os.remove(filename)
        #    outputResult = open(filename, 'wb')
        #    outputResult.write('{"stockList":[]}')
        #    outputResult.close()
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            options=crawler.settings.get('PHANTOMJS_OPTIONS', {}),
            max_sum=crawler.settings.get('PHANTOMJS_MAXSUM', 2)
        )
    def process_request(self, request, spider):
        service_args = ['--load-image=false', '--disk-cache=true']
        url ='http://www.cninfo.com.cn/cninfo-new/announcement/query'
        startUrl ='http://www.cninfo.com.cn/cninfo-new/disclosure/szse_main'
        pageSize=30
        pageNum=1
        heads = { 'Accept':'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding':'gzip,deflate,sdch',
                'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Content-Length':'363',
                'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                'Cookie':'JSESSIONID=DD8456AB003255DA41290DAF981A2C30',
                'Host':'www.cninfo.com.cn',
                'Origin':'http://www.cninfo.com.cn',
                'Referer':'http://www.cninfo.com.cn/cninfo-new/announcement/show',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest' } 
        try:
            
            if(startUrl==request.url[0:len(startUrl)]):
                if(None==request.meta.get('jsonStockIndex', None)):
                    jsonStockIndex=0
                else:
                    jsonStockIndex =request.meta['jsonStockIndex']
                content='jsonStockIndex='+str(jsonStockIndex)
                return HtmlResponse(url, encoding='utf-8', status=200, body=content)
            elif (''!=request.meta['code'] and ''!=request.meta['orgId'] and 0!=request.meta['pageNum'] and 50>request.meta['pageNum']):
                pageNum=request.meta['pageNum']
                stock=request.meta['code']+'%2C'+request.meta['orgId']
                postdata='stock='+stock+'%3B&searchkey=&plate=&category=category_ndbg_szsh%3Bcategory_bndbg_szsh%3Bcategory_yjdbg_szsh%3Bcategory_sjdbg_szsh%3B&trade=&column=szse_gem&columnTitle=%E5%8E%86%E5%8F%B2%E5%85%AC%E5%91%8A%E6%9F%A5%E8%AF%A2&pageNum='+str(pageNum)+'&pageSize=30&tabName=fulltext&sortName=&sortType=&limit=&showTitle=&seDate=%E8%AF%B7%E9%80%89%E6%8B%A9%E6%97%A5%E6%9C%9F'   
                print '************',postdata
                
                newRequest = urllib2.Request(url,postdata,heads)
                response = urllib2.urlopen(newRequest,None, 10)
                content = response.read()
                #set_cookie = response.info()['Set-Cookie']
                response = HtmlResponse(url, encoding='utf-8', status=200, body=content)
                
                #get Json data,Insert pageNum
                jsonAnnouncements = json.loads(response.body)      
                #get page sum number
                
                jsonAnnouncements['pageNum']=pageNum
                jsonAnnouncements['jsonStockIndex']=request.meta['jsonStockIndex']
                content=json.dumps(jsonAnnouncements,ensure_ascii=False,indent=2)
                
                print '*****pageSumNums',jsonAnnouncements['pageNum']
                return HtmlResponse(url, encoding='utf-8', status=200, body=content)
            else:
                print '*****error!!! jsonStockIndex:',request.meta['jsonStockIndex'],'pageNum:',request.meta['pageNum']
                
        except Exception, e:
            logger.warning(e)
            logger.info('******process_request fail : 504')
            filename = '/home/xproject/financialdata/szse_stock_failList.json'
            srcStockfilename='/home/xproject/financialdata/szse_stock.json'
            outputResultFile=open(filename)
            outputResult=outputResultFile.read()
            outputFile=open(filename,'w')         
            try:                
                outputResult=outputResult[:-2] #delete last two char
                if(20<len(outputResult)):
                    outputResult=outputResult+','
                if(None!=request.meta.get('jsonStockIndex', None)):                    
                    jsonSzse_stocks=json.loads(open(srcStockfilename, 'rb').read())
                    errorStockStr=json.dumps(jsonSzse_stocks['stockList'][request.meta['jsonStockIndex']])
                    outputResult=outputResult+errorStockStr+']}'
                else:
                    jsonSzse_stocks=json.loads(open(srcStockfilename, 'rb').read())
                    errorStockStr=json.dumps(jsonSzse_stocks['stockList'][0])
                    outputResult=outputResult+errorStockStr+']}'
                outputFile.write(outputResult)
            finally:  
                outputFile.close()
                outputResultFile.close()
            if(None==request.meta.get('jsonStockIndex', None)):
                jsonStockIndex=1
            else:
                jsonStockIndex =request.meta['jsonStockIndex']+1
            content='jsonStockIndex='+str(jsonStockIndex)
            
            #if return 503 error, it will ignore handler parse, so change error code to 200
            #return HtmlResponse(request.url, encoding='utf-8', status=503, body=content) 
            return HtmlResponse(request.url, encoding='utf-8', status=200, body=content)