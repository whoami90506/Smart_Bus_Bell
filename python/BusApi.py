# -*- coding: utf-8 -*-
import gzip
import urllib
import json, requests, sys, pprint, re, os

# (1)附屬路線與路線對應資訊/每小時
_1url = 'http://data.taipei/bus/PathDetail'
urllib.urlretrieve(_1url, "_1data.gz")
_1f = gzip.open("_1data.gz", 'r')
_1data = _1f.read()
_1f.close()
_1data = json.loads(_1data)
os.chdir('/mnt/d/Dropbox/Workspace/Project/MySmartBus/Data')
_1file=open('PathDetail.txt','w')
_1file.write(str(_1data))
_1file.close()
    

# (2)車輛基本資訊/每小時
_2url = 'http://data.taipei/bus/CarInfo'
urllib.urlretrieve(_2url, "_2data.gz")
_2f = gzip.open("_2data.gz", 'r')
_2data = _2f.read()
_2f.close()
_2data = json.loads(_2data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_2file=open('CarInfo.txt','w')
_2file.write(str(_2data))
_2file.close()
    

# (3)路線、營業站對應/每小時
_3url = 'http://data.taipei/bus/OrgPathAttribute'
urllib.urlretrieve(_3url, "_3data.gz")
_3f = gzip.open("_3data.gz", 'r')
_3data = _3f.read()
_3f.close()
_3data = json.loads(_3data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_3file=open('OrgPathAttribute.txt','w')
_3file.write(str(_3data))
_3file.close()
    

# (4)業者營運基本資料/每小時
_4url = 'http://data.taipei/bus/PROVIDER'
urllib.urlretrieve(_4url, "_4data.gz")
_4f = gzip.open("_4data.gz", 'r')
_4data = _4f.read()
_4f.close()
_4data = json.loads(_4data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_4file=open('PROVIDER.txt','w')
_4file.write(str(_4data))
_4file.close()
    

# (5)路線/每小時
_5url = 'http://data.taipei/bus/ROUTE'
urllib.urlretrieve(_5url, "_5data.gz")
_5f = gzip.open("_5data.gz", 'r')
_5data = _5f.read()
_5f.close()
_5data = json.loads(_5data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_5file=open('ROUTE.txt','w')
_5file.write(str(_5data))
_5file.close()
    

# (6)公車路線線型開放格式/每小時
_6url = 'http://data.taipei/bus/ROUTEGeom'
urllib.urlretrieve(_6url, "_6data.gz")
_6f = gzip.open("_6data.gz", 'r')
_6data = _6f.read()
_6f.close()
_6data = json.loads(_6data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_6file=open('ROUTEGeom.txt','w')
_6file.write(str(_6data))
_6file.close()
    


    

# (8)預定班表資訊/每小時
_8url = 'http://data.taipei/bus/TimeTable'
urllib.urlretrieve(_8url, "_8data.gz")
_8f = gzip.open("_8data.gz", 'r')
_8data = _8f.read()
_8f.close()
_8data = json.loads(_8data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_8file=open('TimeTable.txt','w')
_8file.write(str(_8data))
_8file.close()
    

# (9)機動班次時刻表/每分鐘
_9url = 'http://data.taipei/bus/SemiTimeTable'
urllib.urlretrieve(_9url, "_9data.gz")
_9f = gzip.open("_9data.gz", 'r')
_9data = _9f.read()
_9f.close()
_9data = json.loads(_9data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_9file=open('SemiTimeTable.txt','w')
_9file.write(str(_9data))
_9file.close()
    

# (10)定時車機資訊/每分鐘
_10url = 'http://data.taipei/bus/BUSDATA'
urllib.urlretrieve(_10url, "_10data.gz")
_10f = gzip.open("_10data.gz", 'r')
_10data = _10f.read()
_10f.close()
_10data = json.loads(_10data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_10file=open('BUSDATA.txt','w')
_10file.write(str(_10data))
_10file.close()
    

# (11)定點車機資訊/每分鐘
_11url = 'http://data.taipei/bus/BUSEVENT'
urllib.urlretrieve(_11url, "_11data.gz")
_11f = gzip.open("_11data.gz", 'r')
_11data = _11f.read()
_11f.close()
_11data = json.loads(_11data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_11file=open('BUSEVENT.txt','w')
_11file.write(str(_11data))
_11file.close()
    

# (12)智慧型站牌所屬路線/每分鐘
_12url = 'http://data.taipei/bus/IStopPath'
urllib.urlretrieve(_12url, "_12data.gz")
_12f = gzip.open("_12data.gz", 'r')
_12data = _12f.read()
_12f.close()
_12data = json.loads(_12data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_12file=open('IStopPath.txt','w')
_12file.write(str(_12data))
_12file.close()
    

# (13)智慧型站牌/每分鐘
_13url = 'http://data.taipei/bus/IStop'
urllib.urlretrieve(_13url, "_13data.gz")
_13f = gzip.open("_13data.gz", 'r')
_13data = _13f.read()
_13f.close()
_13data = json.loads(_13data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_13file=open('IStop.txt','w')
_13file.write(str(_13data))
_13file.close()
    

# (14)站牌/每分鐘
_14url = 'http://data.taipei/bus/Stop'
urllib.urlretrieve(_14url, "_14data.gz")
_14f = gzip.open("_14data.gz", 'r')
_14data = _14f.read()
_14f.close()
_14data = json.loads(_14data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_14file=open('Stop.txt','w')
_14file.write(str(_14data))
_14file.close()
    

# (15)車機異常資訊/每分鐘
_15url = 'http://data.taipei/bus/CarUnusual'
urllib.urlretrieve(_15url, "_15data.gz")
_15f = gzip.open("_15data.gz", 'r')
_15data = _15f.read()
_15f.close()
_15data = json.loads(_15data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_15file=open('CarUnusual.txt','w')
_15file.write(str(_15data))
_15file.close()
    

# (16)站位資訊/每分鐘
_16url = 'http://data.taipei/bus/StopLocation'
urllib.urlretrieve(_16url, "_16data.gz")
_16f = gzip.open("_16data.gz", 'r')
_16data = _16f.read()
_16f.close()
_16data = json.loads(_16data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_16file=open('StopLocation.txt','w')
_16file.write(str(_16data))
_16file.close()
    

# (17)預估到站時間/每分鐘
_17url = 'http://data.taipei/bus/EstimateTime'
urllib.urlretrieve(_17url, "_17data.gz")
_17f = gzip.open("_17data.gz", 'r')
_17data = _17f.read()
_17f.close()
_17data = json.loads(_17data)
#os.chdir('D:\Dropbox\Workspace\Project\MySmartBus\Data')
_17file=open('EstimateTime.txt','w')
_17file.write(str(_17data))
_17file.close()
