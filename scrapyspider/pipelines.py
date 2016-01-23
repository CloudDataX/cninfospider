# -*- coding:utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import urllib
import os
import re

class ScrapyspiderPipeline(object):
    
    financialFolder = r'E:\financialdata'
    companyInfoTxt = financialFolder + '\\' + 'companyinfolist.txt'
    
    def process_item(self, item, spider):
        
        self.createFileandFolder()
        
        #Process item get the following info
        returnlist = self.processItemInfo(item)
        
        #stockcode = returnlist[0]
        companyname = returnlist[1]
        reportname = returnlist[2]
        #reportdate = returnlist[3]
        
        #Create company folder
        companyFolder = self.financialFolder + '\\' + companyname
        if not os.path.exists(companyFolder):
            os.mkdir(companyFolder)
        else:
            print 'WRN: ', companyFolder, 'is already exists'
        
        #Download pdf to the created folder
        pdfpath = companyFolder + '\\' + reportname + '.pdf'
        returnlist.append(pdfpath)
        downloadlink = u'http://www.cninfo.com.cn' + "".join(item['downloadhref'])
        try:
            if not os.path.exists(pdfpath):
                urllib.urlretrieve(downloadlink, pdfpath)
            else:
                print 'WRN: ', reportname, '.pdf is already exists'
        except IOError:
            print "ERROR: I/O ERROR save pdf fail"

        #save company info to txt
        tempinfo = " ".join(returnlist[:3])
        txtinfo = tempinfo.strip()
        
        if not self.isInfoInTxt(txtinfo):
            self.saveInfoInTxt(returnlist)

        return item
    
    def processItemInfo(self, item):
        
        #retrunlist[0-3]: stock code, company name, report name, report date
        returnlist = []
        
        #Connect item to a str
        for index in range(len(item['companyinfo'])):
            item['companyinfo'][index] = item['companyinfo'][index].strip()
            item['companyinfo'][index] = re.sub(u' ', '', item['companyinfo'][index])
            item['companyinfo'][index] = re.sub(u'：', '', item['companyinfo'][index])   
        infostr = "".join(item['companyinfo'])
        
        #Get the stock code
        splitdate1 = infostr[0:6]
        returnlist.append(splitdate1)
        
        #Split company name and report name
        splitdate2 = infostr[6:]
        pdfinfo = re.match(r'[^u4e00-u9fa5]+', splitdate2)
        if pdfinfo:
            returnlist.append(pdfinfo.group(0))
            returnlist.append(splitdate2[pdfinfo.end(0):])
        else:
            print "processcompanyinfo: not matched"
        
        #Get report date
        reportdate = ''.join(item['reportyear']) + u'月' + ''.join(item['reportday'])
        returnlist.append(reportdate)
        
        return returnlist
            
    def createFileandFolder(self):
        
        if not os.path.exists(self.financialFolder):
            os.mkdir(self.financialFolder)
        if not os.path.exists(self.companyInfoTxt):
            openfile = open(self.companyInfoTxt, 'w')
            openfile.close()
        return

    def saveInfoInTxt(self, returnlist):
        
        openfile = open(self.companyInfoTxt, 'a')
        
        for value in returnlist:
            openfile.write(value.encode('utf-8'))
            openfile.write(' ')
        openfile.write('\n')
        openfile.close()
        return

    def isInfoInTxt(self, txtinfo):
        try:
            lines=open(self.companyInfoTxt,'r').readlines()
            flen=len(lines)
            for i in range(flen):
                if re.match(txtinfo.encode('utf-8'),lines[i-1]):
                    print 'WRN: ', txtinfo, 'is already in txt'
                    return True
         
        except Exception,e:
            print e
        
        return False
    