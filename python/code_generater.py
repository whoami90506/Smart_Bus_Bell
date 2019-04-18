# -*- coding: utf8 -*-
import os, re, requests, bs4

web=requests.get('https://taipeicity.github.io/traffic_realtime/')
#text=open(web.text,'r').read()
bss=bs4.BeautifulSoup(web.text,'html.parser')
tbody=bss.select('tbody')
tr=tbody=bss.select('tr')
data=[]
i=0
for r in tr[:18]:
    d=r.select('td')
    if len(d):
        data.append([])
        data[i].append(d[0].getText().decode('utf-8'))#EngName
        data[i].append(d[1].getText())#ChiName
        data[i].append(d[2].getText())#Frequen
        data[i].append(d[3].select('a')[0].get('href'))#Url
        i+=1
k=1
for i in data:
    print '''
# %s
_%surl = '%s'
urllib.urlretrieve(_%surl, "_%sdata.gz")
_%sf = gzip.open("_%sdata.gz", 'r')
_%sdata = _%sf.read()
_%sf.close()
_%sdata = json.loads(_%sdata)
os.chdir('/mnt/d/Dropbox/Workspace/Project/MySmartBus/Data')
_%sfile=open('%s.txt','w')
_%sfile.write(str(_%sdata))
_%sfile.close()
    '''% ('('+str(k)+')'+i[1]+'/'+i[2],k,i[3],k,k,k,k,k,k,k,k,k,k,i[0],k,k,k)
    k+=1

