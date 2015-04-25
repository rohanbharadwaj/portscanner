import pymongo
from pymongo import MongoClient
import json


ip = 'localhost'
port = 27017

DB = 'secaffe'
IS_UP = "IS_UP"
TCP_SYN_SCAN = "TCP_SYN_SCAN"
CONNECT_SCAN = "CONNECT_SCAN"
TCP_FIN_SCAN = "TCP_FIN_SCAN"

def setup(scanType):  # setsup connection and returns collection
    client = MongoClient(ip,port)
    db = client.secaffe
    if(scanType==CONNECT_SCAN):
        collection = db.connect_scan
    elif(scanType==IS_UP_BULK):
        collection = db.is_up_scan
    elif(scanType==TCP_FIN_SCAN):
        collection = db.tcp_fin_scan
    elif(scanType==TCP_SYN_SCAN):
        collection = db.tcp_syn_scan
    return collection

def getCount(reqid,scanType): # get count of documents based on reqId
    # print collection.count()
    collection = setup(scanType)
    #return collection.count()
    return collection.find({'reqId':reqid}).count()

def getRawData(collection,reqid):
    result = []
    for e in collection.find({'reqId':reqid},{'_id':0}):
        result.append(e)
    return result   
    # print collection.find({'reqId':reqid})
    # return collection.find({'reqId':reqid})

def fetchProcessedData(reqid,scanType):
    collection = setup(scanType)
    jsondata = getRawData(collection,reqid)
    # print jsondata
    return preprocess(jsondata)


def getdata():
    data1 = []
    data = {}
    #SYN FYN
    numres= len(jsondata["report"])
    print numres
    for i in xrange(numres):
        print i
        data2 = {}
        data2["reqId"] = jsondata["reqId"]
        data2["scannedports"] = str(min(jsondata["ports"]))+"-"+str(max(jsondata["ports"]))
        data2["ip"] = jsondata["report"][i][0]
        data2["openports"] = ','.join(map(str,jsondata["report"][i][1]))
        data1.append(data2)
    print data1
    #openportstr = jsondata["report"][0][0]

    # data = {}
    # client = MongoClient(ip,port)
    # db = client.DB
    # table = db.is_up_scan
    # for e in table.find({},{"reqId":1,"report":1,"ip":1,"ports":1,"_id":0}):
    #     data.update(e)
    # #print data
    # return json.dumps([data])
    # #return data
def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z

def preprocess(jsondata):
    numobj =  len(jsondata)
    #print jsondata[0]["report"][1][0]
    data2 = {}
    data1 = []
    data = {}
    result = []
    #SYN FYN

    for n in xrange(numobj):
        try:
            numres= len(jsondata[n]["report"])
            for i in xrange(numres):
                data2 = {}
                data2["reqId"] = jsondata[n]["reqId"]
                data2["timestamp"] = jsondata[n]["timestamp"]
                data2["jobId"] = jsondata[n]["jobId"]
                data2["scanSequentially"] = jsondata[n]["scanSequentially"]
                data2["ports"] = ','.join(map(str,jsondata[n]["ports"]))
                data2["workerIP_Port"] = jsondata[n]["workerIP_Port"]
                data2["scannedports"] = str(min(jsondata[n]["ports"]))+"-"+str(max(jsondata[n]["ports"]))
                data2["ip"] = jsondata[n]["report"][i][0]
                data2["openports"] = ','.join(map(str,jsondata[n]["report"][i][1]))
                # data1.append(data2)
                data = merge_two_dicts(data,data2)
            result.append(data)
            #print json.dumps(data)
        except (TypeError):
            print "No reports"
    #print result        
    return json.dumps(result)            



   
# def insertdata(client,json_data):
#     #client = MongoClient(ip,port) 
#     db = client.DB
#     records = db.is_up_scan
#     print records.insert(json_data)
#     print "End"

# def getdata(client):
#     db = client.DB
#     table = db.is_up_scan
#     for e in table.find():
#         print e

def Test():
    reqid = "128bca28-ea3a-11e4-a9c1-bc773780be52"
    #collection = setup(CONNECT_SCAN)
    fetchProcessedData(reqid,CONNECT_SCAN)
    # print getCount(reqid)
    # getRawData(collection,reqid)  
    #jsondata = getRawData(collection,reqid)    
    # preprocess(jsondata)

if __name__ == '__main__':
    Test()
    # getdata()
#     client = setup()
#     ip = []
#     for i in xrange(10):
#         ip.append('127.0.0.'+str(i))
#     print ip
#     getdata(client)
    #insertdata(client,[{"reqId":"1242525","ip":"[134.214.13.131,233.112.22.1,12.34.234.34]"}])
    #print a
    #insertdata(client,a)
