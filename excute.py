#!/usr/bin/python
#coding=gbk

# -*- coding:utf-8 -*-

import os
import platform
import time
import codecs

runTime = 0
SysStr = platform.system()

if(SysStr =="Windows"):
    FinancialFolder = r'D:\financialdata' + '\\'
elif(SysStr == "Linux"):
    FinancialFolder = r'/home/xproject/financialdata/'               
else:
    print "Other Platform"
    os._exit()

#Step1: remove all the final report file
print "-----Step1: remove all the final report file-----"
FinalSavedInfoFile = FinancialFolder + 'stockreportlist' + '.json'       
FinalFailReportPath = FinancialFolder + 'szse_stock_failList' + '.json'
FinalDownloadPdfFailLists = FinancialFolder + 'downloadPdfFailLists' + '.txt'
try:
    os.remove(FinalSavedInfoFile)
    os.remove(FinalFailReportPath)
    os.remove(FinalSavedInfoFile)
except Exception, e:
    print "ERROR: remove all final report file fail:", e
    continue

#Step2: remove all 1,2,3,4 file
print "-----Step2: remove all 1,2,3,4 file-----"
for index in range(1, 4):
    SavedInfoFile = FinancialFolder + 'stockreportlist' + str(index) + '.json'       
    FailReportPath = FinancialFolder + 'szse_stock_failList' + str(index) + '.json'
    DownloadPdfFailLists = FinancialFolder + 'downloadPdfFailLists' + str(index) + '.txt'
    TxtFile = FinancialFolder + str(index) + '.txt'
    try:
        os.remove(SavedInfoFile)
        os.remove(FailReportPath)
        os.remove(DownloadPdfFailLists)
        os.remove(TxtFile)
    except Exception, e:
        print "ERROR: remove all 1,2,3,4 file fail:", e
        continue
        
#Step3: Start 4 process to scrapy pdf and check 4 process is ok or not.
print "-----Step3: Start 4 process to scrapy pdf and check 4 process is ok or not.-----"
os.system("gnome-terminal --title='test' -e '/bin/bash -c \"scrapy crawl cninfo\"'")
os.system("gnome-terminal --title='test' -e '/bin/bash -c \"scrapy crawl cninfo\"'")
os.system("gnome-terminal --title='test' -e '/bin/bash -c \"scrapy crawl cninfo\"'")
os.system("gnome-terminal --title='test' -e '/bin/bash -c \"scrapy crawl cninfo\"'")

for index in range(1, 4): 
    if (False == os.path.exists(TxtFile)):
        print "Process:", index, "not start normally"
 
#Step4: Every 5mins search 4 process finish or not. If finish break
print "-----Step4: Every 5mins search 4 process finish or not. If finish break-----"
while(True):
    time.sleep(300)
    runTime += 1
    print "INFO: already run:", runTime*5 , "mins" 
    resp = os.popen('ps -ef | grep scrapy').readlines()
    #There 2 default processor used for 'ps -ef | grep scrapy'.
    #If len(resp)==2, it means no scrapy run
    if len(resp) == 6:
        print "INFO: 4 process running"
    elif len(resp) == 5:
        print "INFO: 3 process running"
    elif len(resp) == 4:
        print "INFO: 2 process running"
    elif len(resp) == 3:
        print "INFO: 1 process running"
    if len(resp) == 2:
        print "INFO: 4 processes finished"
        break
    
#Step5: create final file
print "-----Step5: create final file-----"
if (False == os.path.exists(FinalSavedInfoFile)):
    f= codecs.open(FinalSavedInfoFile,'w','utf-8')
    writeData = '{"stockList":[]}'
    f.write(writeData)
    f.close()
    
if (False == os.path.exists(FinalFailReportPath)):
    f= codecs.open(FinalFailReportPath,'w','utf-8')
    writeData = '{"stockList":[]}'
    f.write(writeData)
    f.close()
    
if (False==os.path.exists(FinalDownloadPdfFailLists)):
    f= codecs.open(FinalDownloadPdfFailLists,'w','utf-8')
    writeData = 'downloadPdfFailLists:'
    f.write(writeData)
    f.close()

#Step6: combine all 1,2,3,4 to final file
print "-----Step6: combine all 1,2,3,4 to final file-----"
for index in range(1, 4):
    SavedInfoFile = FinancialFolder + 'stockreportlist' + str(index) + '.json'       
    FailReportPath = FinancialFolder + 'szse_stock_failList' + str(index) + '.json'
    DownloadPdfFailLists = FinancialFolder + 'downloadPdfFailLists' + str(index) + '.txt'
    
    try:
        sourceFileData = codecs.open(SavedInfoFile,'rb','utf-8')
        sourceData = sourceFileData.read()[14:]
        targetFileDate = codecs.open(FinalSavedInfoFile,'w','utf-8')
        targetData = targetFileDate.read()[:-2]
        targetData = targetData + ',' + sourceData
        targetFileDate.write(targetData)
    except Exception, e:
        print "ERROR: combine szse_stock_failList.json 1,2,3,4 to final fail:", e
    finally:
        sourceFileData.close()
        targetFileDate.close()
        
    try:
        sourceFileData = codecs.open(FailReportPath,'rb','utf-8')
        sourceData = sourceFileData.read()[14:]
        targetFileDate = codecs.open(FinalFailReportPath,'w','utf-8')
        targetData = targetFileDate.read()[:-2]
        targetData = targetData + ',' + sourceData
        targetFileDate.write(targetData)
    except Exception, e:
        print "ERROR: combine stockreportlist.json 1,2,3,4 to final fail:", e
    finally:
        sourceFileData.close()
        targetFileDate.close()
        
    try:
        sourceFileData = codecs.open(DownloadPdfFailLists,'rb','utf-8')
        sourceData = sourceFileData.read()[21:]
        targetFileDate = codecs.open(FinalDownloadPdfFailLists,'a','utf-8')
        targetFileDate.write(sourceData)
    except Exception, e:
        print "ERROR: combine downloadPdfFailLists.txt 1,2,3,4 to final fail:", e
    finally:
        sourceFileData.close()
        targetFileDate.close()
        
print "-----All cninfo spider are finish-----"