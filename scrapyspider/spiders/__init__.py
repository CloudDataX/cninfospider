# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import os

financialFolder = r'E:\financialdata'
jsonFile = financialFolder + '\\' + 'stockreportlist.json'
        
if not os.path.exists(financialFolder):
    os.mkdir(financialFolder)
if not os.path.exists(jsonFile):
    openfile = open(jsonFile, 'w')
    openfile.close()