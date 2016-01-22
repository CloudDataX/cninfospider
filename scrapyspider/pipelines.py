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
    companyinfotxt = financialfolder + '\\' + 'companyinfolist.txt'
    
    def process_item(self, item, spider):
        
        self.creatfileandfolder()
        
        #Process item get the following info
        returnlist = self.processiteminfo(item)
        
        #stockcode = returnlist[0]
        companyname = returnlist[1]
        reportname = returnlist[2]
        #reportdate = returnlist[3]
        
        #Create company folder
        companyfolder = self.financialfolder + '\\' + companyname
        if not os.path.exists(companyfolder):
            os.mkdir(companyfolder)
        else:
            print 'WRN: ', companyfolder, 'is already exists'
        
        #Download pdf to the created folder
        pdfpath = companyfolder + '\\' + reportname + '.pdf'
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
        
        if not self.isinfointxt(txtinfo):
            self.saveinfointxt(returnlist)

        return item
    
    def processiteminfo(self, item):
        
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
            
    def creatfileandfolder(self):
        
        if not os.path.exists(self.financialfolder):
            os.mkdir(self.financialfolder)
        if not os.path.exists(self.companyinfotxt):
            openfile = open(self.companyinfotxt, 'w')
            openfile.close()
        return

    def saveinfointxt(self, returnlist):
        
        openfile = open(self.companyinfotxt, 'a')
        
        for value in returnlist:
            openfile.write(value.encode('utf-8'))
            openfile.write(' ')
        openfile.write('\n')
        openfile.close()
        return

    def isinfointxt(self, txtinfo):
        try:
            lines=open(self.companyinfotxt,'r').readlines()
            flen=len(lines)
            for i in range(flen):
                if re.match(txtinfo.encode('utf-8'),lines[i-1]):
                    print 'WRN: ', txtinfo, 'is already in txt'
                    return True
         
        except Exception,e:
            print e
        
        return False
    