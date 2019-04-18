# -*- coding: utf-8 -*-
import gzip
import urllib
import googlemaps
import math
from datetime import datetime
import json, requests, sys, pprint, re, os
from flask import Flask, jsonify
from flask import make_response
from flask import request
from flask import abort

app = Flask(__name__)

def quicksort(a, attr):
    if len(a) <= 1:
        return a  # 如果a為一位數則直接傳回a

    l = [x for x in a[1:] if x[attr] <= a[0][attr]]  # 輸出排序後的比a[0]小的數列
    r = [x for x in a[1:] if x[attr] > a[0][attr]]  # 輸出排序後的比a[0]大的數列
    return quicksort(l, attr) + [a[0]] + quicksort(r, attr)


def single_quicksort(a):
    if len(a) <= 1:
        return a

    l = [x for x in a[1:] if x <= a[0]]
    r = [x for x in a[1:] if x > a[0]]
    return single_quicksort(l) + [a[0]] + single_quicksort(r)


def estquicksort(a, attr):
    print 'estquicksort'
    if len(a) <= 1:
        return a  # 如果a為一位數則直接傳回a
    w = []
    f = []
    for q in a:
        if q[attr][-4:] == ' min':
            q['tem'] = float(q[attr][:-4])
            f.append(q)
        else:
            w.append(q)
            continue

    if len(f) == 0:
        return a
    l = [x for x in f[1:] if x['tem'] <= f[0]['tem']]  # 輸出排序後的比a[0]小的數列
    r = [x for x in f[1:] if x['tem'] > f[0]['tem']]  # 輸出排序後的比a[0]大的數列
    m = quicksort(l, 'tem')
    n = quicksort(r, 'tem')
    for p in a:
        if 'tem' in p.keys():
            del p['tem']
    return m + [f[0]] + n + w


def findbus(rd, seq, bus, pathdata, rod):
    busdict = {'0': u'一般公車', '1': u'低底盤', \
               '2': u'大復康巴士', '3': u'圓仔公車'}
    if seq == -1:
        return [u"無資訊", u"無資訊"]
    for b in bus:
        if seq in range(len(pathdata[rd]['path'])):
            if str(pathdata[rd]['path'][seq]['Id']) == str(b['StopID']):
                if str(b['CarOnStop']) == '0':
                    return [b['BusID'], busdict[b['CarType']]]
                elif str(b['CarOnStop']) == '1' and rod > 0:
                    return [b['BusID'], busdict[b['CarType']]]
                elif seq == 0:
                    return [u"未發車", u"未發車"]
                elif rd not in pathdata.keys():
                    return [u"查無此路線", u"查無此路線"]
    # print 'recursive'
    return findbus(rd, seq - 1, bus, pathdata, rod + 1)


def tab(x, n):
    return x.ljust(n - x.encode('raw_unicode_escape').count('\u'))


def Howard_generator():
    if True:
        print 'Grabbing data ...'
        # (14)站牌/每分鐘
        if not os.path.exists('./_14data.gz'):
            _14url = 'http://data.taipei/bus/Stop'
            urllib.urlretrieve(_14url, "_14data.gz")
        _14f = gzip.open("_14data.gz", 'r')
        _14data = _14f.read()
        _14f.close()
        _14data = json.loads(_14data)
        print 'Stop.json loaded'

        # (5)路線/每小時
        if not os.path.exists('./_5data.gz'):
            _5url = 'http://data.taipei/bus/ROUTE'
            urllib.urlretrieve(_5url, "_5data.gz")
        _5f = gzip.open("_5data.gz", 'r')
        _5data = _5f.read()
        _5f.close()
        _5data = json.loads(_5data)
        print 'ROUTE.json loaded'

        js5 = _5data
        route = js5['BusInfo']

        js14 = _14data
        real = js14['BusInfo']

        print 'Building belldata ...'
        belldata = {}
        recorded = []
        for i in real:
            if i['routeId'] in recorded:
                stopdict = {'latitude': i['latitude'], \
                            'longitude': i['longitude'], \
                            'stopId': i['Id'], \
                            'name': i['nameZh'], \
                            'seqNo': i['seqNo']}
                belldata[i['routeId']]['path'].append(stopdict)
            else:
                for j in route:
                    if j['Id'] == i['routeId']:
                        stopdict = {'latitude': i['latitude'], \
                                    'longitude': i['longitude'], \
                                    'stopId': i['Id'], \
                                    'name': i['nameZh'], \
                                    'seqNo': i['seqNo']}
                        dictn = {'routeId': j['Id'], \
                                 'name': j['nameZh'], \
                                 "path": [stopdict]}
                        recorded.append(j['Id'])
                        belldata[j['Id']] = dictn
                        break

        for i in belldata.values():
            i['path'] = quicksort(i['path'], 'seqNo')
        newdata = []

    with open('Howard.json', 'w') as file1:
        json.dump(belldata, file1)
    file1.close()
    print 'Howard.json built with 389 paths in it!'


@app.route('/', methods=['GET'])
def usermanual():
    text = '''
    <!DOCTYPE HTML>
    <title>User Manual</title>
    <h1 align="center">-&emsp;-&emsp;-&emsp;&emsp;使用說明&emsp;&emsp;-&emsp;-&emsp;- </h1>
    <pre>(1) http://mysmartbus.herokuapp.com/                      ---> 查看使用說明</pre>
    <pre>(2) http://mysmartbus.herokuapp.com/path/                 ---> 生成path<->stop資料(不會用到，由其他API使用)</pre>
    <pre>(3) http://mysmartbus.herokuapp.com/mapnet/                 ---> 生成Map Net資料(不會用到，由其他API使用)</pre>
    <pre>(4) http://mysmartbus.herokuapp.com/near/{緯度}/{經度}     ---> 查詢附近站牌</pre>
    <pre>    格式說明:
           {'wrapper':[ ... ,(附近站牌list)
               {
                   "stopLocationId": 站牌位置ID,
                   "length": 與使用者距離,
                   "address": 中文地址,
                   "name": 中文名,
                   "location": {
                       "lat": 緯度,
                       "lng": 經度
                    },
                   "passroute": [ ... ,(經過路線list)
                        {
                            "from": 起點站,
                            "to": 終點站,
                            "seqNo": 於路線中序列,
                            "routeId": 路線ID,
                            "stopId": 站牌ID,
                            "num": 公車編號
                        }, ...
                    ]
               },
           {站牌2},
           {站牌3}, ...]}</pre>
    <pre>(5) http://mysmartbus.herokuapp.com/time/{stopLocationId}  ---> 查看該站牌所有路線之預測時間資料，stopLocationId即站牌位置ID，就是上面那個</pre>
    <pre>    格式說明:
             {
              "stopLocationId": 站牌位置ID,
              "length": 與使用者距離,
              "address": 中文地址,
              "name": 中文名,
              "location": {
                       "lat": 緯度,
                       "lng": 經度
                      },
              "wrapper": [ ... ,(各路線資料list)
                {
                  "EstimateTime": 預測時間 min, 
                  "GoBack": 去程or回程(0去,1回,2未知), 
                  "busId": 車牌號碼(or未發車or無班車or查無此路線), 
                  "cartype": 一般公車or低底盤or大復康巴士or圓仔公車, 
                  "from": 起點站, 
                  "num": 公車編號, 
                  "routeId": 路線ID, 
                  "seqNo": 於路線中序列, 
                  "stopId": 站牌ID, 
                  "to": 終點站
                }, ...]
             { 
             </pre>
    <pre>(6) http://mysmartbus.herokuapp.com/search/{緯度}/{經度}/{以+連接的關鍵字}  ---> 路線規劃</pre>
    <pre>    格式說明:
             兩個wrapper:第一個direct是我用自己的算法算出來的直達路徑
                         第二個是google規劃出來的路線，但跟direct重複的路線會被刪掉，所以只會剩下轉乘的路線
                         
                         google的感覺可以放個小圖案代表是google提供的，然後他需要有多一個按鈕來顯示轉乘指示
                         我覺得應該可以direct的方案排在上面，google的方案排在下面，因為有時候google的都是較
                         沒效率的轉乘法，可是只沒辦法直達的時候就會只剩下google的。
                         
                         google有時候會規畫搭新北市公車(Ex:849,667)，EstimateTime就會只寫資料異動
                         direct的內容有照EstimateTime來排，最快到的排最上面。
               {
                 "direct": [ {...} ,   (這個list放所有直達路徑)
                   {
                     "EstimateTime": "30.45 min", 
                     "busId": "468-FW", 
                     "cartype": "低底盤", 
                     "from": "東園", #起點站(不是上車站喔，是整條路線起點)
                     "len_end": 0.003366417220135753, #目的地位置與下車站距離(單位:經緯度)
                     "len_start": 0.0007796266350022264, #使用者所在位置與上車站距離(單位:經緯度)
                     "number": "藍28", #公車編號
                     "routeId": 10721, 
                     "to": "景明街口", #終點站
                     "seq": 7, 
                     "end": {     (下車站資訊)
                       "Id": 11527, 
                       "goBack": "1", 
                       "latitude": "25.0287", 
                       "longitude": "121.509833", 
                       "nameZh": "三元南海路口", 
                       "routeId": 10721, 
                       "seqNo": 39, 
                       "stopLocationId": 1851
                     }, 
                     "start": {     (上車站資訊)
                       "Id": 11513, 
                       "goBack": "1", 
                       "latitude": "25.02698", 
                       "longitude": "121.496086", 
                       "nameZh": "聚福宮", 
                       "routeId": 10721, 
                       "seqNo": 32, 
                       "stopLocationId": 1001447
                     }
                   }, {...} , {...} ], 
                 "google": [ {...} ,   (這個list放google規劃路徑)
                   {
                     "EstimateTime": "1.65 min", 
                     "busId": "683-FR", 
                     "cartype": "低底盤", 
                     "final_arrival_time": "下午12:43", 
                     "from": "東園",
                     "num": "204", 
                     "num_stops": 6, 
                     "routeId": 11212,
                     "to": "麥帥新城", 
                     "transfer_times": 1 , #轉乘公車次數
                     "instruction": " -> 步行到德昌街口 0.6 公里\\n
                     -> 搭204 東園-麥帥新城 共8分 共6站\\n
                     -> 步行到100台灣台北市中正區南海路56號 0.4 公里\\n",
                     
                     (上面這是轉乘指示，可以做成一個按鈕點進去才會顯示)
                     
                     "start": {
                       "location": {
                         "lat": 25.025728, 
                         "lng": 121.500549
                       }, 
                       "name": "德昌街口", 
                       "seqNo": 3, 
                       "stopId": 18272
                     },  
                     "end": {
                       "location": {
                         "lat": 25.029956, 
                         "lng": 121.509147
                       }, 
                       "name": "三元街口", 
                       "seqNo": 9, 
                       "stopId": 18281
                     } 
                   },
                   {...} , {...} }
                 ]
               }</pre>
    <pre>(7) http://mysmartbus.herokuapp.com/belldata/                              ---> 所有路線按鈴資料生成(APP應該不會用到)</pre>
    <pre>(8) http://mysmartbus.herokuapp.com/seebell/{該路線數字名稱}                ---> 查看單一路線按鈴資料(司機端APP用)</pre>
    <pre>    格式說明:
                    {
                      "departureZh": 起站, 
                      "destinationZh": 迄站, 
                      "name": 起站<->迄站, 
                      "number": 數字名稱,
                      "providerName": u'光華巴士', #業者名稱
                      "routeId": 10932, #路線ID
                      "segmentBufferZh": "中國時報－捷運臺大醫院站", #分段緩衝區
                      "ticketPriceDescriptionZh": "兩段票"
                      "path": [ ... ,    (這條路線所有站牌都收在這，而且有用seqNo排序過了，所以是照順序的)
                        {
                          "Id": 154151, #其實他是stopId才對，因為這是從stop data直接抓的沒改名字
                          "address": "懷德街201巷同向", #地址
                          "bell1": 0, #按鈴與否(他是int，有人按鈴會+1，取消會-1，APP應該要設計成:按鈴的鈕按下去之後變成取消按鈴的鈕，
                          才不會有人把別人按的也取消，或是一個人按兩次，司機端APP只要他不是0就會亮燈)
                          "bell2": 0,
                          "bell3": 0,
                          "bell4": 0,
                          "goBack": "0", #去程or回程
                          "latitude": "25.028775935224", #經緯度
                          "longitude": "121.48060944509", 
                          "nameEn": "Wufu New Village", #英文站名
                          "nameZh": "\u4e94\u798f\u65b0\u6751", #中文站名
                          "pgp": "0", #上車站或下車站或可上可下，用不到，原廠附的懶得刪掉
                          "routeId": 10932, #他也是路線ID
                          "seqNo": 0, #本站牌在這條路線上的序位
                          "showLat": "25.028775935224", #顯示用經緯度，意義不明，有時候好像會比上面那個更貼近真實，有時候沒差
                          "showLon": "121.48060944509", 
                          "stopLocationId": 2565, #站位ID
                          "vector": "999" #據說是站牌相位角，原廠附的懶得刪掉
                          
                          ----新增----
                          "busId": "915-FR", #該站公車車牌
                          "cartype": u"低底盤", #該站車型(低底盤or一般...)
                          "CarOnStop": "0" #進站1或離站0
                          ------------
                          
                        }, {...} , {...} , ... ],
                      }
                        </pre>
    <pre>(9) http://mysmartbus.herokuapp.com/bell/{routeId}/{stopLocationId}                 ---> 按鈴(傳入路線ID及站牌ID)
             格式說明: 其實他會回傳值，會跟樓上產生同樣的資料(按鈴那一條路線的)</pre>
    <pre>(10) http://mysmartbus.herokuapp.com/cancel/{routeId}/{stopLocationId}              ---> 取消按鈴(傳入路線ID及站牌ID)
             格式說明: 其實他會回傳值，會跟樓上上產生同樣的資料</pre>
    <pre>(11) http://mysmartbus.herokuapp.com/reset/{routeId}/{stopLocationId}              ---> 重置按鈴(就是司機已經載完客就傳一個request來重置它)
             格式說明: 其實他會回傳值，會跟樓上上上產生同樣的資料</pre>
    <pre>(12) http://mysmartbus.herokuapp.com/howard/{該路線數字名稱}                        ---> 生成單一路線所有站牌序列
             格式說明:
             {
                 "wrapper": {
                   "name": "262",
                   "routeId":10961,
                   "path": [
                     { ... ,
                       "latitude": "24.97267", 
                       "longitude": "121.458837", 
                       "name": "\u5fb7\u9716\u6280\u8853\u5b78\u9662", 
                       "seqNo": 0, 
                       "stopId": 40495
                     }, ... , ... }
               {






              </pre>
    <p align="center">Copyright  NTUEE. All rights reserved.<br/>
    Howard Chao, ChengDe Lin, Jexus Chuang. No.1, Sec. 4, Roosevelt Road, Taipei, Taiwan 106.</p>'''
    return text


@app.route('/path/', methods=['GET'])
def pathstop_generator():
    print '----------http://mysmartbus.herokuapp.com/path/----------'
    #print 'Grabbing data from web ...'
    # (14)站牌/每分鐘
    if not os.path.exists('./_14data.gz'):
        _14url = 'http://data.taipei/bus/Stop'
        urllib.urlretrieve(_14url, "_14data.gz")
    _14f = gzip.open("_14data.gz", 'r')
    _14data = _14f.read()
    _14f.close()
    _14data = json.loads(_14data)
    #print 'Stop.json loaded'

    # (5)路線/每小時
    if not os.path.exists('./_5data.gz'):
        _5url = 'http://data.taipei/bus/ROUTE'
        urllib.urlretrieve(_5url, "_5data.gz")
    _5f = gzip.open("_5data.gz", 'r')
    _5data = _5f.read()
    _5f.close()
    _5data = json.loads(_5data)
    #print 'ROUTE.json loaded'

    js5 = _5data
    route = js5['BusInfo']

    js14 = _14data
    real = js14['BusInfo']

    real = quicksort(real, 'nameZh')

    if os.path.exists('Path_with_all_stop.json'):
        _1file = open('Path_with_all_stop.json', 'r')
        f1 = _1file.read()
        _1file.close()
        pathdata = json.loads(f1)
        #print 'Path_with_all_stop.json loaded'

    else:
        #print 'Building pathdata ...'
        pathdata = {}
        recorded = []
        for i in range(len(real)):
            if real[i]['routeId'] in recorded:
                pathdata[str(real[i]['routeId'])]['path'].append(real[i])
            else:
                for j in range(len(route)):
                    if route[j]['Id'] == real[i]['routeId']:
                        dictn = {'routeId': route[j]['Id'], \
                                 'name': route[j]['departureZh'] + '<->' + route[j]['destinationZh'], \
                                 'departureZh': route[j]['departureZh'], \
                                 'destinationZh': route[j]['destinationZh'], \
                                 'number': route[j]['nameZh'], \
                                 "path": []}
                        dictn['path'].append(real[i])
                        recorded.append(route[j]['Id'])
                        pathdata[str(route[j]['Id'])] = dictn
                        break

    for i in pathdata.values():
        pathdata[str(i['routeId'])]['path'] = quicksort(i['path'], 'seqNo')

    with open('Path_with_all_stop.json', 'w') as file1:
        json.dump(pathdata, file1)
    file1.close()
    #print 'Path_with_all_stop.json built with ' + str(len(pathdata)) + ' paths in it!'

    return jsonify(pathdata)


@app.route('/mapnet/', methods=['GET'])
def mapnet():
    print '----------http://mysmartbus.herokuapp.com/mapnet/----------'
    # (14)站牌/每分鐘
    if not os.path.exists('./_14data.gz'):
        _14url = 'http://data.taipei/bus/Stop'
        urllib.urlretrieve(_14url, "_14data.gz")
    _14f = gzip.open("_14data.gz", 'r')
    _14data = _14f.read()
    _14f.close()
    _14data = json.loads(_14data)

    js14 = _14data
    real = js14['BusInfo']

    # (5)路線/每小時
    if not os.path.exists('./_5data.gz'):
        _5url = 'http://data.taipei/bus/ROUTE'
        urllib.urlretrieve(_5url, "_5data.gz")
    _5f = gzip.open("_5data.gz", 'r')
    _5data = _5f.read()
    _5f.close()
    _5data = json.loads(_5data)

    js5 = _5data
    route = js5['BusInfo']

    #print 'Generating unified stop data ...'
    quicksort(real, 'stopLocationId')
    mid = {}
    for i in range(len(real)):
        if real[i]['stopLocationId'] in mid.keys():
            fm = 'NNN'
            to = 'NNN'
            dic = {}
            for j in route:
                if real[i]['routeId'] == j['Id']:
                    if real[i]['goBack'] == '0':
                        fm = j['departureZh']
                        to = j['destinationZh']
                    elif real[i]['goBack'] == '1':
                        fm = j['destinationZh']
                        to = j['departureZh']
                    dic = {'num': j['nameZh'], \
                           'routeId': j['Id'], \
                           'stopId': real[i]['Id'], \
                           'seqNo': real[i]['seqNo'], \
                           'from': fm, \
                           'to': to}
                    mid[real[i]['stopLocationId']]['passroute'].append(dic)
                    break

            # print type(mid[real[i]['stopLocationId']]),'if'

            if not real[i]['address'] == ('NNN' or 'None'):
                mid[real[i]['stopLocationId']]['address'] = real[i]['address']
        elif not real[i]['stopLocationId'] in mid.keys():
            maindict = {'name': 'No name', \
                        'location': {'lat': 'no', 'lng': 'no'}, \
                        'address': 'No address', 'passroute': []}
            maindict = {'name': real[i]['nameZh'], \
                        'location': {'lat': real[i]['latitude'], 'lng': real[i]['longitude']}, \
                        'address': real[i]['address'], 'passroute': [], \
                        'stopLocationId': real[i]['stopLocationId']}
            # maindict.setdefault
            mid[real[i]['stopLocationId']] = maindict
            fm = 'NNN'
            to = 'NNN'
            dic = {}
            for j in route:
                if real[i]['routeId'] == j['Id']:
                    if real[i]['goBack'] == '0':
                        fm = j['departureZh']
                        to = j['destinationZh']
                    elif real[i]['goBack'] == '1':
                        fm = j['destinationZh']
                        to = j['departureZh']
                    dic = {'num': j['nameZh'], \
                           'routeId': j['Id'], \
                           'stopId': real[i]['Id'], \
                           'seqNo': real[i]['seqNo'], \
                           'from': fm, \
                           'to': to}
                    mid[real[i]['stopLocationId']]['passroute'].append(dic)
                    break
                    # print type(mid[real[i]['stopLocationId']]),'elif'

    # jizz={'wrapper':list(mid.values())}
    with open('Map_Stop_Path.json', 'w') as file1:
        json.dump(mid, file1)
    file1.close()
    print 'total data', len(list(mid.values()))


@app.route('/near/<string:lat>/<string:lng>', methods=['GET'])
def nearstoppath(lat, lng):
    print '----------http://mysmartbus.herokuapp.com/near/%s/%s/----------' % (lat,lng)
    inpu = {'lat': lat, 'lon': lng}
    # (14)站牌/每分鐘
    if not os.path.exists('./_14data.gz'):
        _14url = 'http://data.taipei/bus/Stop'
        urllib.urlretrieve(_14url, "_14data.gz")
    _14f = gzip.open("_14data.gz", 'r')
    _14data = _14f.read()
    _14f.close()
    _14data = json.loads(_14data)

    # (5)路線/每小時
    if not os.path.exists('./_5data.gz'):
        _5url = 'http://data.taipei/bus/ROUTE'
        urllib.urlretrieve(_5url, "_5data.gz")
    _5f = gzip.open("_5data.gz", 'r')
    _5data = _5f.read()
    _5f.close()
    _5data = json.loads(_5data)

    js2 = _5data
    route = js2['BusInfo']

    js14 = _14data
    real = js14['BusInfo']

    # (0)路網/固定資料
    if not os.path.exists('./Map_Stop_Path.json'):
        mapnet()
        #print 'Generating unified stop data ...'
    _0f = open('Map_Stop_Path.json', 'r')
    _0data = _0f.read()
    _0f.close()
    _0data = json.loads(_0data)

    js0 = _0data
    unistop = list(js0.values())
    unidict = js0

    avastop = []

    for i in unistop:
        length = (math.pow(abs(float(inpu['lat']) - float(i['location']['lat'])), 2) + \
                  math.pow(abs(float(inpu['lon']) - float(i['location']['lng'])), 2))
        if (length <= 0.000001):
            i['length'] = length
            avastop.append(i)

    if len(avastop) == 0:
        print "No Stop Nearby!"
        return jsonify({'result': 'No Stop Nearby'})
    avalible = quicksort(avastop, 'length')

    # print range(len(avalible)),len(avalible)
    print 'Avalible Stops Name and Address:'

    for i in avastop:
        print '\n(' + str(i['stopLocationId']) + ')', i['name'], i['address']
        for j in i['passroute']:
            print '  ', tab(j["num"], 8), tab(j['from'], 12), '->', tab(j['to'], 12)

    result = {'wrapper': avastop}
    return jsonify(result)


@app.route('/time/<string:stopLocId>', methods=['GET'])
def seeEstType(stopLocId):
    print '----------http://mysmartbus.herokuapp.com/time/%s/----------' % (stopLocId)
    # (0)路網/固定資料
    if not os.path.exists('./Map_Stop_Path.json'):
        mapnet()
        #print 'Generating unified stop data ...'
    _0f = open('Map_Stop_Path.json', 'r')
    _0data = _0f.read()
    _0f.close()
    _0data = json.loads(_0data)

    js0 = _0data
    unistop = list(js0.values())
    unidict = js0

    if stopLocId not in unidict:
        print 'out of range'
        return jsonify({'error': 'stopLocId out of range'})
    else:
        # (17)預估到站時間/每分鐘
        _17url = 'https://tcgbusfs.blob.core.windows.net/blobbus/GetEstimateTime.gz'
        urllib.urlretrieve(_17url, "_17data.gz")
        _17f = gzip.open("_17data.gz", 'r')
        _17data = _17f.read()
        _17f.close()
        _17data = json.loads(_17data)
        #print 'EstimateTime.json loaded'

        # (11)定點車機資訊/每分鐘
        _11url = 'https://tcgbusfs.blob.core.windows.net/blobbus/GetBusEvent.gz'
        urllib.urlretrieve(_11url, "_11data.gz")
        _11f = gzip.open("_11data.gz", 'r')
        _11data = _11f.read()
        _11f.close()
        _11data = json.loads(_11data)
        print 'BUSEVENT.json loaded'

        js17 = _17data
        est = js17['BusInfo']

        js11 = _11data
        bus = js11['BusInfo']

        if not os.path.exists('./Path_with_all_stop.json'):
            pathstop_generator()
            print "Running /path/ because file not found!"
        _1file = open('Path_with_all_stop.json', 'r')
        f1 = _1file.read()
        _1file.close()
        pathdata = json.loads(f1)
        #print 'Path_with_all_stop.json loaded'

        estdict = {'-1': u'尚未發車', '-2': u'交管不停靠', \
                   '-3': u'末班車已過', '-4': u'今日未營運'}
        busdict = {'0': u'一般公車', '1': u'低底盤', \
                   '2': u'大復康巴士', '3': u'圓仔公車'}
        print '\n(' + str(stopLocId) + ')', unidict[stopLocId]['name'], unidict[stopLocId]['address']

        for i in unidict[stopLocId]['passroute']:
            for j in est:
                i['EstimateTime'] = 'nnn'
                if i['stopId'] == j['StopID']:
                    if int(j['EstimateTime']) >= 0:
                        i['EstimateTime'] = str(round(float(j['EstimateTime']) / 60, 2)) + ' min'
                    else:
                        i['EstimateTime'] = estdict[str(j['EstimateTime'])]
                    print i['EstimateTime']
                    i['GoBack'] = j['GoBack']
                    break

        for i in unidict[stopLocId]['passroute']:
            temp = findbus(str(i['routeId']), i['seqNo'], bus, pathdata, 0)
            # print temp
            i['busId'] = temp[0]
            i['cartype'] = temp[1]

        result = {"stopLocationId": unidict[stopLocId]["stopLocationId"], \
                  "address": unidict[stopLocId]["address"], \
                  "location": unidict[stopLocId]["location"], \
                  "name": unidict[stopLocId]["name"], \
                  'wrapper': unidict[stopLocId]['passroute']}
        for i in unidict[stopLocId]['passroute']:
            print tab(i['num'], 8), tab(i['from'], 12), '->', tab(i['to'], 12),
            print tab(i['busId'], 8), tab(i['EstimateTime'], 12), tab(i['cartype'], 12)
    return jsonify(result)


@app.route('/search/<string:userlat>/<string:userlng>/<string:words>', methods=['GET'])
def searchpath(userlat, userlng, words):
    print '----------http://mysmartbus.herokuapp.com/search/%s/%s/%s----------' % (userlat, userlng, words)
    gmaps = googlemaps.Client(key='AIzaSyDr3z6Nu2lBSE1bZqg-u-oeENCaF53Xhcs')

    inpu = {'lat': userlat, 'lng': userlng}
    geocode_result = gmaps.geocode(address=words, language='zh-TW')
    if len(geocode_result) == 0:
        print "No Such Place!"
        return jsonify({'error': "No Such Place!"})
    lat = geocode_result[0]['geometry']['location']['lat']
    lng = geocode_result[0]['geometry']['location']['lng']
    print lat, lng

    # (14)站牌/每分鐘
    if not os.path.exists('./_14data.gz'):
        _14url = 'http://data.taipei/bus/Stop'
        urllib.urlretrieve(_14url, "_14data.gz")
    _14f = gzip.open("_14data.gz", 'r')
    _14data = _14f.read()
    _14f.close()
    _14data = json.loads(_14data)

    # (5)路線/每小時
    if not os.path.exists('./_5data.gz'):
        _5url = 'http://data.taipei/bus/ROUTE'
        urllib.urlretrieve(_5url, "_5data.gz")
    _5f = gzip.open("_5data.gz", 'r')
    _5data = _5f.read()
    _5f.close()
    _5data = json.loads(_5data)

    js2 = _5data
    route = js2['BusInfo']

    js14 = _14data
    real = js14['BusInfo']

    def Loc(stopId):
        for i in real:
            if stopId==i['Id']:
                return i['stopLocationId']
        return 4814

    # (0)路網/固定資料
    if not os.path.exists('./Map_Stop_Path.json'):
        mapnet()
        #print 'Generating unified stop data ...'
    _0f = open('Map_Stop_Path.json', 'r')
    _0data = _0f.read()
    _0f.close()
    _0data = json.loads(_0data)

    js0 = _0data
    unistop = list(js0.values())
    unidict = js0

    avastop = []
    for i in unistop:
        length = (math.pow(abs(float(inpu['lat']) - float(i['location']['lat'])), 2) + \
                  math.pow(abs(float(inpu['lng']) - float(i['location']['lng'])), 2))
        if (length < 0.00005):
            i['len_start'] = length
            avastop.append(i)

    if len(avastop) == 0:
        print "No Stop Nearby!"
        return jsonify({'error': "No Stop Nearby!"})

    avalible = quicksort(avastop, 'len_start')

    if not os.path.exists('./Path_with_all_stop.json'):
        pathstop_generator()
        print "Running /path/ because file not found!"
    _1file = open('Path_with_all_stop.json', 'r')
    f1 = _1file.read()
    _1file.close()
    pathdata = json.loads(f1)
    #print 'Path_with_all_stop.json loaded'

    avapath = {}
    for i in avastop:
        for j in i['passroute']:
            if str(j['routeId']) not in pathdata.keys():
                break
            ph = pathdata[str(j['routeId'])]['path']
            for k in range(j['seqNo'] + 1, len(ph)):
                length = (math.pow(abs(float(ph[k]['latitude']) - float(lat)), 2) + \
                          math.pow(abs(float(ph[k]['longitude']) - float(lng)), 2))
                if length <= 0.00002:
                    # print j['num'],j['stopId'],j["seqNo"],':',ph[j["seqNo"]]['seqNo'],pathdata[j['routeId']]['number'],ph[j["seqNo"]]['Id']
                    if not j['stopId'] == ph[j["seqNo"]]['Id']:
                        for h in ph:
                            if j['stopId'] == h['Id']:
                                j["seqNo"] = ph.index(h)

                    dic = {'start': ph[j["seqNo"]], \
                           'end': pathdata[str(j['routeId'])]['path'][k], \
                           'routeId': pathdata[str(j['routeId'])]['routeId'], \
                           'from': pathdata[str(j['routeId'])]['departureZh'], \
                           'to': pathdata[str(j['routeId'])]['destinationZh'], \
                           'number': pathdata[str(j['routeId'])]['number'], \
                           'seq': ph[k]['seqNo'] - j["seqNo"], \
                           'len_start': math.pow(i['len_start'], 0.5), \
                           'len_end': math.pow(length, 0.5) \
                           }
                    if 'vector' in dic['start'].keys():
                        del dic['start']["vector"]
                    if 'pgp' in dic['start'].keys():
                        del dic['start']["pgp"]
                    if 'address' in dic['start'].keys():
                        del dic['start']["address"]
                    if "nameEn" in dic['start'].keys():
                        del dic['start']["nameEn"]

                    if 'vector' in dic['end'].keys():
                        del dic['end']["vector"]
                    if "pgp" in dic['end'].keys():
                        del dic['end']["pgp"]
                    if "nameEn" in dic['end'].keys():
                        del dic['end']["nameEn"]
                    if "address" in dic['end'].keys():
                        del dic['end']["address"]

                    if 'showLat' in dic['start'].keys():
                        dic['start']['latitude'] = dic['start']['showLat']
                        del dic['start']['showLat']
                    if 'showLon' in dic['start'].keys():
                        dic['start']['longitude'] = dic['start']['showLon']
                        del dic['start']['showLon']

                    if 'showLat' in dic['end'].keys():
                        dic['end']['latitude'] = dic['end']['showLat']
                        del dic['end']['showLat']
                    if 'showLon' in dic['end'].keys():
                        dic['end']['longitude'] = dic['end']['showLon']
                        del dic['end']['showLon']

                    if pathdata[str(j['routeId'])]['path'][j["seqNo"]]['goBack'] == '1':
                        dic['from'], dic['to'] = dic['to'], dic['from']
                    if pathdata[str(j['routeId'])]['routeId'] not in avapath.keys():
                        avapath[pathdata[str(j['routeId'])]['routeId']] = dic
                    elif (avapath[pathdata[str(j['routeId'])]['routeId']]['seq'] - dic['seq']) > 4:
                        avapath[pathdata[str(j['routeId'])]['routeId']] = dic
                    elif ((dic['seq'] - avapath[pathdata[str(j['routeId'])]['routeId']]['seq']) < 3 and
                                      (dic['len_start'] + dic['len_end']) <=
                                          (avapath[pathdata[str(j['routeId'])]['routeId']]['len_start'] +
                                                   avapath[pathdata[str(j['routeId'])]['routeId']]['len_end'])):

                        avapath[pathdata[str(j['routeId'])]['routeId']] = dic
                    break
    dirnum = []
    for p in avapath.values():
        dirnum.append(p['number'])

    # (17)預估到站時間/每分鐘
    _17url = 'https://tcgbusfs.blob.core.windows.net/blobbus/GetEstimateTime.gz'
    urllib.urlretrieve(_17url, "_17data.gz")
    _17f = gzip.open("_17data.gz", 'r')
    _17data = _17f.read()
    _17f.close()
    _17data = json.loads(_17data)
    #print 'EstimateTime.json loaded'

    # (11)定點車機資訊/每分鐘
    _11url = 'https://tcgbusfs.blob.core.windows.net/blobbus/GetBusEvent.gz'
    urllib.urlretrieve(_11url, "_11data.gz")
    _11f = gzip.open("_11data.gz", 'r')
    _11data = _11f.read()
    _11f.close()
    _11data = json.loads(_11data)
    #print 'BUSEVENT.json loaded'

    js17 = _17data
    est = js17['BusInfo']

    js11 = _11data
    bus = js11['BusInfo']

    def tab(x, n):
        return x.ljust(n - x.encode('raw_unicode_escape').count('\u'))

    def findbus(rd, seq, bus, pathdata, rod):
        busdict = {'0': u'一般公車', '1': u'低底盤', \
                   '2': u'大復康巴士', '3': u'圓仔公車'}
        if seq == -1:
            return [u"無資訊", u"無資訊"]
        for b in bus:
            if str(pathdata[rd]['path'][seq]['Id']) == str(b['StopID']):
                if str(b['CarOnStop']) == '0':
                    return [b['BusID'], busdict[b['CarType']]]
                elif str(b['CarOnStop']) == '1' and rod > 0:
                    return [b['BusID'], busdict[b['CarType']]]
                elif seq == 0:
                    return [u"未發車", u"未發車"]
                elif rd not in pathdata.keys():
                    return [u"查無此路線", u"查無此路線"]
        # print 'recursive'
        return findbus(rd, seq - 1, bus, pathdata, rod + 1)

    def seeEstType(avapath, est, bus):
        if avapath == {}:
            print "No Path Found"
            return 0

        estdict = {'-1': u'尚未發車', '-2': u'交管不停靠', \
                   '-3': u'末班車已過', '-4': u'今日未營運'}
        busdict = {'0': u'一般公車', '1': u'低底盤', \
                   '2': u'大復康巴士', '3': u'圓仔公車'}
        # print '\n('+str(x)+')',unidict[stopLocId]['name'],unidict[stopLocId]['address']

        for i in avapath.values():
            for j in est:
                i['EstimateTime'] = 'nnn'
                if i['start']['Id'] == j['StopID']:
                    if int(j['EstimateTime']) >= 0:
                        i['EstimateTime'] = str(round(float(j['EstimateTime']) / 60, 2)) + ' min'
                    else:
                        i['EstimateTime'] = estdict[str(j['EstimateTime'])]
                    print i['EstimateTime']
                    break

        for i in avapath.values():
            temp = findbus(str(i['start']['routeId']), i['start']['seqNo'], bus, pathdata, 0)
            # print temp
            i['busId'] = temp[0]
            i['cartype'] = temp[1]

    seeEstType(avapath, est, bus)

    templist = list(avapath.values())
    templist = estquicksort(templist, 'EstimateTime')
    for i in templist:
        print tab(i['number'], 8), tab(i['from'], 12), '->', tab(i['to'], 12),
        print tab(i['start']['nameZh'], 8), '->', tab(i['end']['nameZh'], 8), u'共' + str(i['seq']) + u'站',
        print tab(i['busId'], 8), tab(i['EstimateTime'], 12), tab(i['cartype'], 12)

    now = datetime.now()
    directions_result = gmaps.directions(inpu,  # (25.03822167, 121.5151233),
                                         {'lat': lat, 'lng': lng},  # (25.044879,121.532901),
                                         mode="transit",
                                         transit_mode="bus",
                                         transit_routing_preference="fewer_transfers",
                                         alternatives=True,
                                         departure_time=now, language='zh-TW')

    ansname = []
    for i in directions_result:
        b = 0
        bustimes = 0
        print '\nCase (', directions_result.index(i) + 1, ')---------------------'
        insn = ''
        for j in i['legs'][0]['steps']:
            if j['travel_mode'] == 'WALKING':
                print '->', j['html_instructions'], j['distance']['text']
                insn = ' '.join([insn, '->', j['html_instructions'], j['distance']['text'] + '\n'])
            elif j['transit_details']['line']['vehicle']['type'] == 'BUS':
                bustimes += 1
                if b == 0:
                    b = i['legs'][0]['steps'].index(j)
                print '->', u'搭', \
                    j['transit_details']['line']['short_name'], \
                    j['transit_details']['line']['name'], u'共' + \
                                                          j['duration']['text'], u'共' + \
                                                                                 str(j['transit_details'][
                                                                                         'num_stops']) + u'站'
                insn = ' '.join([insn, '->', u'搭', j['transit_details']['line']['short_name'], \
                                 j['transit_details']['line']['name'], u'共' + \
                                 j['duration']['text'], u'共' + \
                                 str(j['transit_details']['num_stops']) + u'站\n'])
        na = i['legs'][0]['steps'][b]['transit_details']['line']['name']
        fm = 'fm'
        to = 'to'
        for e in range(len(na)):
            if na[e] == '-':
                fm = na[:e]
                to = na[e + 1:]
                break
        print '-------------------------------\n',  # 'Start Location:',i['legs'][0]['start_location']
        # print 'End Location:',i['legs'][0]['end_location']
        # print 'First Step: Take the',i['legs'][0]['steps'][b]['transit_details']['line']['short_name'],
        # print i['legs'][0]['steps'][b]['transit_details']['line']['name'],
        # print i['legs'][0]['steps'][b]['transit_details']['line']['vehicle']['type'],i['fare']['text']
        # print i['legs'][0]['steps'][b]['transit_details']['departure_stop']['location'],'->',
        # print i['legs'][0]['steps'][b]['transit_details']['arrival_stop']['location']
        # print 'Total:',i['legs'][0]['steps'][b]['transit_details']['num_stops'],'stops'
        print 'Arrival time', i['legs'][0]['arrival_time']['text']  # ,i['fare']['text']

        dic = {'num': i['legs'][0]['steps'][b]['transit_details']['line']['short_name'], \
               'start': {'location': i['legs'][0]['steps'][b]['transit_details']['departure_stop']['location'], \
                         'name': i['legs'][0]['steps'][b]['transit_details']['departure_stop']['name']}, \
               'end': {'location': i['legs'][0]['steps'][b]['transit_details']['arrival_stop']['location'], \
                       'name': i['legs'][0]['steps'][b]['transit_details']['arrival_stop']['name']}, \
               'from': fm, \
               'to': to, \
               'num_stops': i['legs'][0]['steps'][b]['transit_details']['num_stops'], \
               'final_arrival_time': i['legs'][0]['arrival_time']['text'], \
               'transfer_times': bustimes, \
               'instruction': insn}
        if dic['num'] not in dirnum:
            ansname.append(dic)
    for i in ansname:
        i["routeId"] = 10291
        i['start']["stopId"] = 57291
        i['start']["seqNo"] = 1
        i['start']['stopLocationId'] = 4814
    for i in ansname:
        for h in pathdata.values():
            if h['number'] == i['num']:
                i["routeId"] = h["routeId"]
                stalength = 1.0e-05
                endlength = 1.0e-05
                print 'path found:', i['num']
                for k in h['path']:
                    length1 = (math.pow(abs(float(float(k['latitude'])) - float(i['start']['location']['lat'])), 2) + \
                               math.pow(abs(float(float(k['longitude'])) - float(i['start']['location']['lng'])), 2))
                    length2 = (math.pow(abs(float(float(k['latitude'])) - float(i['end']['location']['lat'])), 2) + \
                               math.pow(abs(float(float(k['longitude'])) - float(i['end']['location']['lng'])), 2))

                    if length1 < stalength:
                        stalength = length1
                        print 'start stop found:', length1
                        # print k['latitude']+', '+k['longitude'],'==',i['start']['location']
                        i['from'] = pathdata[str(k['routeId'])]['departureZh']
                        i['to'] = pathdata[str(k['routeId'])]['destinationZh']
                        i['start']["stopId"] = k["Id"]
                        i['start']['stopLocationId'] = Loc(k["Id"])
                        i['start']["seqNo"] = k["seqNo"]
                        if k['goBack'] == '1':
                            i['from'], i['to'] = i['to'], i['from']
                    if length2 < endlength:
                        print 'end stop found:', length2
                        endlength = length2
                        # print k['latitude']+', '+k['longitude'],'==',i['end']['location']
                        i['from'] = pathdata[str(k['routeId'])]['departureZh']
                        i['to'] = pathdata[str(k['routeId'])]['destinationZh']
                        i['end']["seqNo"] = k["seqNo"]
                        i['end']["stopId"] = k["Id"]
                        i['end']['stopLocationId'] = Loc(k["Id"])
                        if k['goBack'] == '1':
                            i['from'], i['to'] = i['to'], i['from']

    def Goofindbus(rd, seq, bus, pathdata, rod):
        busdict = {'0': u'一般公車', '1': u'低底盤', \
                   '2': u'大復康巴士', '3': u'圓仔公車'}
        if seq == -1:
            return [u"無資訊", u"無資訊"]
        for b in bus:
            if str(pathdata[rd]['path'][seq]['Id']) == str(b['StopID']):
                if str(b['CarOnStop']) == '0':
                    return [b['BusID'], busdict[b['CarType']]]
                elif str(b['CarOnStop']) == '1' and rod > 0:
                    return [b['BusID'], busdict[b['CarType']]]
                elif seq == 0:
                    return [u"未發車", u"未發車"]
                elif rd not in pathdata.keys():
                    return [u"查無此路線", u"查無此路線"]
        # print 'recursive'
        return findbus(rd, seq - 1, bus, pathdata, rod + 1)

    def GooEstType(ansname, est, bus):
        if ansname == []:
            print "No Path Found"
            return 0

        estdict = {'-1': u'尚未發車', '-2': u'交管不停靠', \
                   '-3': u'末班車已過', '-4': u'今日未營運'}
        busdict = {'0': u'一般公車', '1': u'低底盤', \
                   '2': u'大復康巴士', '3': u'圓仔公車'}
        # print '\n('+str(x)+')',unidict[stopLocId]['name'],unidict[stopLocId]['address']

        for i in ansname:
            if 'routeId' not in i.keys():
                i['EstimateTime'] = u"資料異動"
                continue
            for j in est:
                i['EstimateTime'] = 'nnn'
                if i['start']['stopId'] == j['StopID']:
                    i['EstimateTime'] = 'nnn'
                    if int(j['EstimateTime']) >= 0:
                        i['EstimateTime'] = str(round(float(j['EstimateTime']) / 60, 2)) + ' min'
                    else:
                        i['EstimateTime'] = estdict[str(j['EstimateTime'])]
                    print i['EstimateTime']
                    break

        for i in ansname:
            if 'routeId' not in i.keys():
                i['busId'] = u"資料異動"
                i['cartype'] = u"資料異動"
                continue
            temp = Goofindbus(str(i['routeId']), i['start']['seqNo'], bus, pathdata, 0)
            # print temp
            i['busId'] = temp[0]
            i['cartype'] = temp[1]

        # result={'wrapper':unidict[stopLocId]['passroute']}
        for i in ansname:
            print tab(i['num'], 5), tab(i['from'], 12), '->', tab(i['to'], 12),
            print tab(i['start']['name'], 8), '->', tab(i['end']['name'], 8), u'共' + str(i['num_stops']) + u'站',
            print tab(i['busId'], 8), tab(i['EstimateTime'], 12), tab(i['cartype'], 12)

    GooEstType(ansname, est, bus)

    result = {'direct': templist, 'google': ansname}
    return jsonify(result)


@app.route('/belldata/', methods=['GET'])
def belldata_generator():
    print '----------http://mysmartbus.herokuapp.com/belldata----------'

    if os.path.exists('./belldata.json'):
        bellfile = open("belldata.json", 'r')
        _data = bellfile.read()
        bellfile.close()
        result = json.loads(_data)
        return jsonify(result)
    else:
        #print 'Grabbing data ...'
        # (14)站牌/每分鐘
        if not os.path.exists('./_14data.gz'):
            _14url = 'http://data.taipei/bus/Stop'
            urllib.urlretrieve(_14url, "_14data.gz")
        _14f = gzip.open("_14data.gz", 'r')
        _14data = _14f.read()
        _14f.close()
        _14data = json.loads(_14data)
        #print 'Stop.json loaded'

        # (5)路線/每小時
        if not os.path.exists('./_5data.gz'):
            _5url = 'http://data.taipei/bus/ROUTE'
            urllib.urlretrieve(_5url, "_5data.gz")
        _5f = gzip.open("_5data.gz", 'r')
        _5data = _5f.read()
        _5f.close()
        _5data = json.loads(_5data)
        #print 'ROUTE.json loaded'

        js5 = _5data
        route = js5['BusInfo']

        js14 = _14data
        real = js14['BusInfo']

        #print 'Building belldata ...'
        belldata = {}
        recorded = []
        for i in real:
            i['bell1'] = 0
            i['bell2'] = 0
            i['bell3'] = 0
            i['bell4'] = 0
            if i['routeId'] in recorded:
                belldata[i['routeId']]['path'].append(i)
            else:
                for j in route:
                    if j['Id'] == i['routeId']:
                        dictn = {'routeId': j['Id'], \
                                 'name': j['departureZh'] + '<->' + j['destinationZh'], \
                                 'departureZh': j['departureZh'], \
                                 'destinationZh': j['destinationZh'], \
                                 'segmentBufferZh': j['segmentBufferZh'], \
                                 'ticketPriceDescriptionZh': j['ticketPriceDescriptionZh'], \
                                 'providerName': j['providerName'], \
                                 'number': j['nameZh'], \
                                 "path": [i]}
                        recorded.append(j['Id'])
                        belldata[j['Id']] = dictn
                        break

        for i in belldata.values():
            belldata[i['routeId']]['path'] = quicksort(i['path'], 'seqNo')

        with open('belldata.json', 'w') as file1:
            json.dump(belldata, file1)
        file1.close()
        #print 'belldata.json built'
        return jsonify(belldata)


@app.route('/seebell/<string:routename>', methods=['GET'])
def seebell(routename):
    print '----------http://mysmartbus.herokuapp.com/seebell/%s----------' % routename
    if not os.path.exists('./belldata.json'):
        belldata_generator()
    bellfile = open("belldata.json", 'r')
    _data = bellfile.read()
    bellfile.close()
    belldata = json.loads(_data)

    #print 'Grabbing data ...'

    # (5)路線/每小時
    if not os.path.exists('./_5data.gz'):
        _5url = 'http://data.taipei/bus/ROUTE'
        urllib.urlretrieve(_5url, "_5data.gz")
    _5f = gzip.open("_5data.gz", 'r')
    _5data = _5f.read()
    _5f.close()
    _5data = json.loads(_5data)
    #print 'ROUTE.json loaded'

    js5 = _5data
    route = js5['BusInfo']
    r = ''
    for i in route:
        if i['nameZh'] == routename:
            r = str(i['Id'])
            break
    if r == '':
        return jsonify({'error': "Please enter the correct bus name."})
    else:
        result = belldata[r]

        # (17)預估到站時間/每分鐘
        _17url = 'https://tcgbusfs.blob.core.windows.net/blobbus/GetEstimateTime.gz'
        urllib.urlretrieve(_17url, "_17data.gz")
        _17f = gzip.open("_17data.gz", 'r')
        _17data = _17f.read()
        _17f.close()
        _17data = json.loads(_17data)
        #print 'EstimateTime.json loaded'

        # (11)定點車機資訊/每分鐘
        _11url = 'https://tcgbusfs.blob.core.windows.net/blobbus/GetBusEvent.gz'
        urllib.urlretrieve(_11url, "_11data.gz")
        _11f = gzip.open("_11data.gz", 'r')
        _11data = _11f.read()
        _11f.close()
        _11data = json.loads(_11data)
        #print 'BUSEVENT.json loaded'

        js17 = _17data
        est = js17['BusInfo']

        js11 = _11data
        bus = js11['BusInfo']

        estdict = {'-1': u'尚未發車', '-2': u'交管不停靠', \
                   '-3': u'末班車已過', '-4': u'今日未營運'}
        busdict = {'0': u'一般公車', '1': u'低底盤', \
                   '2': u'大復康巴士', '3': u'圓仔公車'}

        for i in result['path']:
            for j in est:
                i['EstimateTime'] = 'nnn'
                if str(i['Id']) == str(j['StopID']):
                    if int(j['EstimateTime']) >= 0:
                        i['EstimateTime'] = str(round(float(j['EstimateTime']) / 60, 2)) + ' min'
                    else:
                        i['EstimateTime'] = estdict[str(j['EstimateTime'])]
                    print i['EstimateTime']
                    break
                    # i['GoBack']=j['GoBack']

        for i in result['path']:
            for j in bus:
                if str(i['Id']) == str(j['StopID']):
                    i['busId'] = j['BusID']
                    i['cartype'] = busdict[j['CarType']]
                    i['CarOnStop'] = j['CarOnStop']
            i.setdefault('busId', 'None')
            i.setdefault('cartype', 'None')
            i.setdefault('CarOnStop', 'None')

    return jsonify(result)


@app.route('/bell/<string:routeId>/<string:stopLocId>/<string:ty>', methods=['GET'])
def pushbell(routeId, stopLocId, ty):
    print '----------http://mysmartbus.herokuapp.com/bell/%s/%s/%s----------' % (routeId, stopLocId, ty)
    if ty not in ['1', '2', '3', '4']:
        return jsonify({'error': 'Please input correct number in 1234'})

    if not os.path.exists('./belldata.json'):
        belldata_generator()
    bellfile = open("belldata.json", 'r')
    _data = bellfile.read()
    bellfile.close()
    belldata = json.loads(_data)

    #print 'Grabbing data ...'

    # (14)站牌/每分鐘
    if not os.path.exists('./_14data.gz'):
        _14url = 'http://data.taipei/bus/Stop'
        urllib.urlretrieve(_14url, "_14data.gz")
    _14f = gzip.open("_14data.gz", 'r')
    _14data = _14f.read()
    _14f.close()
    _14data = json.loads(_14data)
    #print 'Stop.json loaded'
    flag = 0
    for i in belldata[routeId]['path']:
        if str(i['stopLocationId']) == stopLocId:
            print 'PUSH', ty
            typ = 'bell' + ty
            i[typ] += 1
            flag = 1
            break
    if flag == 0:
        return jsonify({'error': 'No such stopLocationId'})

    with open('belldata.json', 'w') as file1:
        json.dump(belldata, file1)
    file1.close()
    #print 'belldata.json updated'
    return jsonify(belldata[routeId])


@app.route('/cancel/<string:routeId>/<string:stopLocId>/<string:ty>', methods=['GET'])
def cancelbell(routeId, stopLocId, ty):
    print '----------http://mysmartbus.herokuapp.com/cancel/%s/%s/%s----------' % (routeId, stopLocId, ty)
    if not os.path.exists('./belldata.json'):
        belldata_generator()
    bellfile = open("belldata.json", 'r')
    _data = bellfile.read()
    bellfile.close()
    belldata = json.loads(_data)

    #print 'Grabbing data ...'

    # (14)站牌/每分鐘
    if not os.path.exists('./_14data.gz'):
        _14url = 'http://data.taipei/bus/Stop'
        urllib.urlretrieve(_14url, "_14data.gz")
    _14f = gzip.open("_14data.gz", 'r')
    _14data = _14f.read()
    _14f.close()
    _14data = json.loads(_14data)
    #print 'Stop.json loaded'
    flag = 0
    for i in belldata[routeId]['path']:
        if str(i['stopLocationId']) == stopLocId:
            print 'CANCEL!'
            i['bell' + ty] -= 1
            flag = 1
            break
    if flag == 0:
        return jsonify({'error': 'No such stopLocationId'})
    with open('belldata.json', 'w') as file1:
        json.dump(belldata, file1)
    file1.close()
    #print 'belldata.json updated'
    return jsonify(belldata[routeId])


@app.route('/reset/<string:routeId>/<string:stopLocId>', methods=['GET'])
def resetbell(routeId, stopLocId):
    print '----------http://mysmartbus.herokuapp.com/reset/%s/%s----------' % (routeId, stopLocId)
    if not os.path.exists('./belldata.json'):
        belldata_generator()
    bellfile = open("belldata.json", 'r')
    _data = bellfile.read()
    bellfile.close()
    belldata = json.loads(_data)

    #print 'Grabbing data ...'

    # (14)站牌/每分鐘
    if not os.path.exists('./_14data.gz'):
        _14url = 'http://data.taipei/bus/Stop'
        urllib.urlretrieve(_14url, "_14data.gz")
    _14f = gzip.open("_14data.gz", 'r')
    _14data = _14f.read()
    _14f.close()
    _14data = json.loads(_14data)
    #print 'Stop.json loaded'
    flag = 0
    for i in belldata[routeId]['path']:
        if str(i['stopLocationId']) == stopLocId:
            print 'RESET!'
            i['bell1'] = 0
            i['bell2'] = 0
            i['bell3'] = 0
            i['bell4'] = 0
            flag = 1
            break
    if flag == 0:
        return jsonify({'error': 'No such stopLocationId'})

    with open('belldata.json', 'w') as file1:
        json.dump(belldata, file1)
    file1.close()
    #print 'belldata.json updated'
    return jsonify(belldata[routeId])


@app.route('/howard/<string:routename>', methods=['GET'])
def howard(routename):
    print '----------http://mysmartbus.herokuapp.com/Howard/%s----------' % routename
    if not os.path.exists('./Howard.json'):
        Howard_generator()
        #print 'Generating Howard ...'
    _0f = open('Howard.json', 'r')
    _0data = _0f.read()
    _0f.close()
    _0data = json.loads(_0data)
    howard = _0data

    # (5)路線/每小時
    if not os.path.exists('./_5data.gz'):
        _5url = 'http://data.taipei/bus/ROUTE'
        urllib.urlretrieve(_5url, "_5data.gz")
    _5f = gzip.open("_5data.gz", 'r')
    _5data = _5f.read()
    _5f.close()
    _5data = json.loads(_5data)
    #print 'ROUTE.json loaded'

    js5 = _5data
    route = js5['BusInfo']
    r = ''
    for i in route:
        if i['nameZh'] == routename:
            r = str(i['Id'])
            break
    if r == '':
        return jsonify({'error': "Please enter the correct bus name."})
    else:
        return jsonify({"wrapper": howard[r]})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
