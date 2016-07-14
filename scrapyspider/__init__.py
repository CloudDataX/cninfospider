import os
import platform
import codecs
print "srapysider.init start"

SysStr = platform.system()
StockStartIndex = 0
StockEndIndex = 9999
FinancialFolder = ''
SavedInfoFile = ''
FailReportPath = ''
ProcessIndex = 1
DownloadPdfFailLists = ''
SzseStockFile = ''

if(SysStr =="Windows"):
    FinancialFolder = r'D:\financialdata' + '\\'
elif(SysStr == "Linux"):
    FinancialFolder = r'/home/xproject/financialdata/'               
else:
    print "Other Platform"
    os._exit()


   
# Use 1.txt 2.txt 3.txt ... to distribute different process


while (ProcessIndex < 5):
    ProcessFile = FinancialFolder + str(ProcessIndex) + '.txt'
    if ( False == os.path.exists(ProcessFile)):
        f= codecs.open(ProcessFile,'w','utf-8')
        writeData = '{}'
        f.write(writeData)
        f.close()
        break
    else:
        ProcessIndex += 1
        
SavedInfoFile = FinancialFolder + 'stockreportlist' + str(ProcessIndex) + '.json'       
FailReportPath = FinancialFolder + 'szse_stock_failList' + str(ProcessIndex) + '.json'
DownloadPdfFailLists = FinancialFolder + 'downloadPdfFailLists' + str(ProcessIndex) + '.txt' 
SzseStockFile = FinancialFolder + 'szse_stock.json'

if (False == os.path.exists(FinancialFolder)):
    os.makedirs(FinancialFolder)

if (False == os.path.exists(SavedInfoFile)):
    f= codecs.open(SavedInfoFile,'w','utf-8')
    writeData = '{"stockList":[]}'
    f.write(writeData)
    f.close()
    
if (False == os.path.exists(FailReportPath)):
    f= codecs.open(FailReportPath,'w','utf-8')
    writeData = '{"stockList":[]}'
    f.write(writeData)
    f.close()
    
if (False==os.path.exists(DownloadPdfFailLists)):
    f= codecs.open(DownloadPdfFailLists,'w','utf-8')
    writeData = 'downloadPdfFailLists:'
    f.write(writeData)
    f.close()
    
if ProcessIndex == 1:
    StockStartIndex = 0
    StockEndIndex = 800
elif ProcessIndex == 2:
    StockStartIndex = 800
    StockEndIndex = 1600
elif ProcessIndex == 3:
    StockStartIndex = 1600
    StockEndIndex = 2400
elif ProcessIndex == 4:
    StockStartIndex = 2400
    StockEndIndex = 3200



    