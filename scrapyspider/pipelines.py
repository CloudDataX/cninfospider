# -*- coding:utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import urllib
import os
import re

class ScrapyspiderPipeline(object):
    
    financialfolder = r'E:\financialdata'
    
    def process_item(self, item, spider):
        
        self.creatfinancialfolder()
        
        #get info from item
        companyinfo = self.processcompanyinfo(item)
        
        companyname = u'中国船舶' 
        companyinfo = u'600111 中国船舶报告' 
        companydir = self.savecompanyinfo(companyname, companyinfo)
        
        pdfpath = companydir + '\\' + companyname + '.pdf'
        
        downloadlink = u'http://www.cninfo.com.cn' + "".join(item['downloadhref'])
        print "Real download URL =", downloadlink
        print 'Down load pdf path:', pdfpath

        try:
            if not os.path.exists(pdfpath):
                urllib.urlretrieve(downloadlink, pdfpath)
            else:
                print 'WRN: ', companyname, 'already exists'
        except IOError:
            print "ERROR: I/O ERROR save pdf fail"

        return item
    
    def processcompanyinfo(self, item):
        
        for index in range(len(item['companyinfo'])):
            item['companyinfo'][index] = item['companyinfo'][index] .strip()    
        companyname = "".join(item['companyinfo'])
        companyinfo = companyname.split(' ')
        
        print companyinfo[1]
        #pos = re.match(r'^\d+', companyinfo[1])
        #print pos.groups()
        
        reportdate = ''.join(item['reportyear']) + u'月' + ''.join(item['reportday'])
        
        companyinfo.append(reportdate)
        
        for value in companyinfo:
            print 'companyinfo is:', value
        
        return companyinfo
            
    def creatfinancialfolder(self):
        
        if not os.path.exists(self.financialfolder):
            os.mkdir(self.financialfolder)
        return
    
    def savecompanyinfo(self, companyname, companyinfo):
              
        companylist = self.financialfolder + '\\' + 'companylist.txt'
        companydir = self.financialfolder + '\\' + companyname
        print companylist
        print companydir
    
        self.createcompanyfolder(companydir)
        self.saveinfoinlistfile(companylist, companyinfo)
        
        return companydir
    
    def createcompanyfolder(self, companydir):
    
        if not os.path.exists(companydir):
            os.mkdir(companydir)
        return

    def saveinfoinlistfile(self, companylist, companyinfo):

        companyfile = open(companylist, 'a')
        companyfile.write(companyinfo.encode('utf-8'))
        companyfile.write('\n')
        companyfile.close()
        return


