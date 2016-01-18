# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import urllib
import os

class ScrapyspiderPipeline(object):

    def creat_financial_folder(self, dir):
        financialdir= dir + "\\financialstatement"
     
        if os.path.exists(financialdir):
		    return None
        else:
            os.mkdir(financialdir)
        return financialdir

    # def write_company_list(self, dir, item):
        # listpath= dir + "\\companylist.txt"
     
        # if os.path.exists(listpath):
		    # listfile = open(listpath,'a')
        # else:
            # listfile = open(listpath,'w')
        # listfile.wirte()
        # listfile.close()
        # return		

    def process_item(self, item, spider):
        
        financialdir = self.creat_financial_folder(os.getcwd())
		
		
		print
        # if financialdir:
            # write_company_list(financialdir)
        # else:
            # print "ERR creat company list fail"
            # return None			

        str = "".join(item['downloadhref'])
        print "my str is:", str
        realURL = u'http://www.cninfo.com.cn' + str
        print "real download URL =", realURL
		
        try:
            urllib.urlretrieve(realURL, 'E:\\pythonproject\\scrapyspider\\1.pdf')
     	except IOError:
            print "ERROR: I/O ERROR save pdf fail"
            		
        return item
		
 		