# -*- coding: utf-8 -*-
import gzip
import urllib
import json, requests, sys, pprint, re, os


os.chdir('/mnt/d/Dropbox/Workspace/Project/MySmartBus/Data')
print 'Grabbing data from web ...'
# (14)站牌/每分鐘
_14url = 'http://data.taipei/bus/Stop'
urllib.urlretrieve(_14url, "_14data.gz")
_14f = gzip.open("_14data.gz", 'r')
_14data = _14f.read()
_14f.close()
_14data = json.loads(_14data)
print 'Stop.json loaded'

# (5)路線/每小時

_5url = 'http://data.taipei/bus/ROUTE'
urllib.urlretrieve(_5url, "_5data.gz")
_5f = gzip.open("_5data.gz", 'r')
_5data = _5f.read()
_5f.close()
_5data = json.loads(_5data)
print 'ROUTE.json loaded'

js5=_5data
route=js5['BusInfo']

js14=_14data
real=js14['BusInfo']

def quicksort(a,attr):
     if len(a) <= 1:
         return a  # 如果a為一位數則直接傳回a

     l = [x for x in a[1:] if x[attr] <= a[0][attr]]  # 輸出排序後的比a[0]小的數列
     r = [x for x in a[1:] if x[attr] > a[0][attr]]  # 輸出排序後的比a[0]大的數列
     return quicksort(l,attr) + [a[0]] + quicksort(r,attr)

real=quicksort(real,'nameZh')
print 'Building pathdata ...'
pathdata=[]
recorded=[]
for i in range(len(real)):
    if real[i]['routeId'] in recorded:
        for k in range(len(pathdata)):
            if pathdata[k]['routeId']==real[i]['routeId']:
                if real[i]['goBack']=='0':
                    pathdata[k]['to_path'].append(real[i])
                elif real[i]['goBack']=='1':
                    pathdata[k]['back_path'].append(real[i])
                    break
    else:
        for j in range(len(route)):
            if route[j]['Id']==real[i]['routeId']:
                dictn={'routeId':route[j]['Id'], 'name':route[j]['departureZh']+'<->'+route[j]['destinationZh'],'number':route[j]['nameZh'], "to_path":[], "back_path":[]}
                if real[i]['goBack']=='0':
                    dictn['to_path'].append(real[i])
                elif real[i]['goBack']=='1':
                    dictn['back_path'].append(real[i])
                recorded.append(route[j]['Id'])
                pathdata.append(dictn)
                break
print 'Sorting pathdata ...'
pathdata=quicksort(pathdata,'routeId')

def single_quicksort(a):
     if len(a) <= 1:
         return a  

     l = [x for x in a[1:] if x <= a[0]]  
     r = [x for x in a[1:] if x > a[0]]  
     return single_quicksort(l) + [a[0]] + single_quicksort(r)

for i in pathdata:
    i['to_path']=quicksort(i['to_path'],'seqNo')
    i['back_path']=quicksort(i['back_path'],'seqNo')


pathdata=quicksort(pathdata,'routeId')


_1file=open('Path_with_all_stop.txt','w')
_1file.write(str(pathdata))
_1file.close()
print 'Path_with_all_stop.txt built with '+str(len(pathdata))+' paths in it!'



