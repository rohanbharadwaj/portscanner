from pymongo import MongoClient
import json
from ReqResObjects import *

ip = 'localhost'
port = 27017

# DB = 'secaffe'
# CONNECTTABLE = 'connect_scan'
# ISUPTABLE = 'is_up_scan'
# FINTABLE = 'tcp_fin_scan'
# SYNTABLE = 'tcp_syn_scan'

def preprocess(jsondata):
    data2 = {}
    data1 = []
    data = {}
    #SYN FYN
    numres= len(jsondata["report"])
    print numres
    for i in xrange(numres):
        data2 = {}
        print i
        data2["reqId"] = jsondata["reqId"]
        data2["scannedports"] = str(min(jsondata["ports"]))+"-"+str(max(jsondata["ports"]))
        data2["ip"] = jsondata["report"][i][0]
        data2["openports"] = ','.join(map(str,jsondata["report"][i][1]))
        data2["IPs"] = ','.join(map(str,jsondata["IPs"][i][1]))
        print data2
        data1.append(data2)
    print json.dumps(data1)
    #openportstr = jsondata["report"][0][0]



def setup():
    return MongoClient(ip, port)

def insertdata(client, json_data, scanType):
    # client = MongoClient(ip,port)
    db = client.secaffe

    if(scanType==CONNECT_SCAN):
        records = db.connect_scan
    elif(scanType==IS_UP_BULK):
        records = db.is_up_scan
    elif(scanType==TCP_FIN_SCAN):
        records = db.tcp_fin_scan
    elif(scanType==TCP_SYN_SCAN):
        records = db.tcp_syn_scan

    jsond= json.loads(json_data)
    print type(jsond)
    print jsond
    print "**************************INSERTING RECORD**************************************************"
    print records.insert(jsond)
    print "End"


def getdata(client):
    db = client.DB
    table = db.is_up_scan
    for e in table.find():
        print e


if __name__ == '__main__':
    client = setup()
    ip = []
    for i in xrange(10):
        ip.append('127.0.0.' + str(i))
    print ip
    getdata(client)
    # insertdata(client,[{"reqId":"1242525","ip":"[134.214.13.131,233.112.22.1,12.34.234.34]"}])
    # print a
    #insertdata(client,a)
