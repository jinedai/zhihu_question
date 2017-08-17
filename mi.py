# -*- coding:utf-8 -*-
import os,urllib,urllib2,re
import socket
import json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

header = {
'Device-Id': 'ffffffff-c690-520f-47dc-5a4708a11582',
'Cookie': 'serviceToken=/6/yH6az6Q+PoVKMg/dgFNpNn7N+lkfTVp5UM2bI4w1FYcN/knthmSzazqvKyM42Boog2oOBhgoa0ldZ53DYfFFn/WBT4O258HPOI+VHLTd7GPi9BDxcfcLiSafmp5tuEiVHqkQP4RlhFPeyqEk4NCjgi1orAonKAH9fF32gsng=',
'Network-Stat': 'wifi',
'Mishop-Client-Id': '180100031052',
'Screen-width-px': '1080',
'Mishop-Client-VersionName': '4.2.7.0801.r1',
'Accept-Encoding': 'gzip',
'Mishop-Client-VersionCode': '20170801',
'Mishop-Auth': 'f672ff74f1877343;734336530',
'Mishop-Model': 'MI 5s',
'Uuid': '5d60fbc2-372a-f65e-310b-d201f2d3c564',
'Screen-DensityDpi': '480',
'Mishop-Is-Pad': '0',
'device': '5rqXkVAmt5lWh975gaRttg==',
'Android-Ver': '23',
'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
'Host': 'api.m.mi.com',
'Connection': 'Keep-Alive',
'User-Agent': 'okhttp/3.4.1'
}


##====================以下为方法========================##
def getContent():
    url = 'http://api.m.mi.com/v1/hisearch/se_home'
    data = {
            'input_word' : '小爱同学',
            'query' : '小爱同学',
            'page_index' : '1',
            'checkbox' : '0',
            'page_size' : 20
    }
    data = urllib.urlencode(data)
    req = urllib2.Request(url, data, headers = header) 
    try:
        currentPage=json.loads(urllib2.urlopen(req, timeout=10).read())
        return currentPage['data']['red_session']
    except urllib2.URLError:
        print 'url error'
        return None
    except socket.error:
        print 'socket result'
        return None
    except Exception,e:
        print 'other error'
        return None

def getResult(session_id):
    url = 'http://api.m.mi.com/v1/misearch/roll'
    data = {
            'session_id' : session_id,
            'query' : '小爱同学',
    }
    data = urllib.urlencode(data)
    try:
        req = urllib2.Request(url, data, headers = header) 
        currentPage= urllib2.urlopen(req, timeout=10).read()
        print session_id
    except urllib2.URLError:
        print 'url error'
    except socket.error:
        print 'socket result'
    except Exception,e:
        print 'other error'

if __name__ == '__main__':
    i = 1
    while (1):
        print i
        red_session = getContent()
        if not red_session is None:
            result = getResult(red_session)
        i = i + 1
        
