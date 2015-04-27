import pymongo
from pymongo import MongoClient
import json


ip = 'localhost'
port = 27017

DB = 'secaffe'
IS_UP_BULK = "IS_UP_BULK"
TCP_SYN_SCAN = "TCP_SYN_SCAN"
CONNECT_SCAN = "CONNECT_SCAN"
TCP_FIN_SCAN = "TCP_FIN_SCAN"

#test_json = "[{"py/object": "ReqResObjects.Res", "scanType": "CONNECT_SCAN", "IPPorts": [["172.24.20.1", 20, 30], ["172.24.20.2", 20, 30], ["172.24.20.3", 20, 30], ["172.24.20.4", 20, 30], ["172.24.20.5", 20, 30], ["172.24.20.6", 20, 30], ["172.24.20.7", 20, 30], ["172.24.20.8", 20, 30], ["172.24.20.9", 20, 30], ["172.24.20.10", 20, 30], ["172.24.20.11", 20, 30], ["172.24.20.12", 20, 30], ["172.24.20.13", 20, 30], ["172.24.20.14", 20, 30], ["172.24.20.15", 20, 30], ["172.24.20.16", 20, 30], ["172.24.20.17", 20, 30], ["172.24.20.18", 20, 30], ["172.24.20.19", 20, 30], ["172.24.20.20", 20, 30], ["172.24.20.21", 20, 30], ["172.24.20.22", 20, 30], ["172.24.20.23", 20, 30], ["172.24.20.24", 20, 30], ["172.24.20.25", 20, 30], ["172.24.20.26", 20, 30], ["172.24.20.27", 20, 30], ["172.24.20.28", 20, 30], ["172.24.20.29", 20, 30], ["172.24.20.30", 20, 30], ["172.24.20.31", 20, 30], ["172.24.20.32", 20, 30], ["172.24.20.33", 20, 30], ["172.24.20.34", 20, 30], ["172.24.20.35", 20, 30], ["172.24.20.36", 20, 30], ["172.24.20.37", 20, 30], ["172.24.20.38", 20, 30], ["172.24.20.39", 20, 30], ["172.24.20.40", 20, 30], ["172.24.20.41", 20, 30], ["172.24.20.42", 20, 30], ["172.24.20.43", 20, 30], ["172.24.20.44", 20, 30], ["172.24.20.45", 20, 30], ["172.24.20.46", 20, 30], ["172.24.20.47", 20, 30], ["172.24.20.48", 20, 30], ["172.24.20.49", 20, 30], ["172.24.20.50", 20, 30], ["172.24.20.51", 20, 30], ["172.24.20.52", 20, 30], ["172.24.20.53", 20, 30], ["172.24.20.54", 20, 30], ["172.24.20.55", 20, 30], ["172.24.20.56", 20, 30], ["172.24.20.57", 20, 30], ["172.24.20.58", 20, 30], ["172.24.20.59", 20, 30], ["172.24.20.60", 20, 30], ["172.24.20.61", 20, 30], ["172.24.20.62", 20, 30]], "timestamp": "2015-04-26 14:46:11.761931", "jobId": "81f8f708-ec44-11e4-a9c1-bc773780be52", "reqId": "81f89088-ec44-11e4-a9c1-bc773780be52", "scanSequentially": "False", "workerIP_Port": "172.24.31.108:8080", "report": [["172.24.20.23", []], ["172.24.20.29", []], ["172.24.20.27", [[22, "SSH-2.0-OpenSSH_6.6.1p1 Ubuntu-2ubuntu2\r\n"]]], ["172.24.20.24", [[22, "SSH-2.0-OpenSSH_6.6.1p1 Ubuntu-2ubuntu2\r\n"]]], ["172.24.20.35", []], ["172.24.20.46", []], ["172.24.20.6", []], ["172.24.20.16", []], ["172.24.20.1", []], ["172.24.20.2", []], ["172.24.20.4", []], ["172.24.20.7", []], ["172.24.20.5", []], ["172.24.20.10", []], ["172.24.20.8", []], ["172.24.20.11", []], ["172.24.20.9", []], ["172.24.20.3", []], ["172.24.20.14", []], ["172.24.20.13", []], ["172.24.20.12", []], ["172.24.20.18", []], ["172.24.20.22", []], ["172.24.20.20", []], ["172.24.20.19", []], ["172.24.20.17", []], ["172.24.20.25", []], ["172.24.20.21", []], ["172.24.20.28", []], ["172.24.20.32", []], ["172.24.20.31", []], ["172.24.20.26", []], ["172.24.20.30", []], ["172.24.20.33", []], ["172.24.20.34", []], ["172.24.20.36", []], ["172.24.20.38", []], ["172.24.20.37", []], ["172.24.20.41", []], ["172.24.20.44", []], ["172.24.20.42", []], ["172.24.20.43", []], ["172.24.20.47", []], ["172.24.20.50", []], ["172.24.20.51", []], ["172.24.20.55", []], ["172.24.20.54", []], ["172.24.20.49", []], ["172.24.20.52", []], ["172.24.20.48", []], ["172.24.20.57", []], ["172.24.20.59", []], ["172.24.20.62", []], ["172.24.20.58", []], ["172.24.20.61", []], ["172.24.20.40", []], ["172.24.20.15", []], ["172.24.20.39", []], ["172.24.20.45", []], ["172.24.20.53", []], ["172.24.20.60", []], ["172.24.20.56", [[21, "No Banner"]]]]}]"
iptest = "127.0.0.1"

def restructjson(test_json):
    data = {}


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
    # print "After getRawData"
    # print jsondata
    return json.dumps(jsondata)
    #return preprocess(jsondata)


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
    #data2 = {}
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
    reqid = "2e591188-eb7b-11e4-a9c1-bc773780be52"
    #collection = setup(CONNECT_SCAN)
    print fetchProcessedData(reqid,CONNECT_SCAN)
    #print fetchProcessedData(reqid,CONNECT_SCAN)
    # print getCount(reqid)
    # getRawData(collection,reqid)  
    #jsondata = getRawData(collection,reqid)    
    # preprocess(jsondata)

def getReportData(searchip, scanType):
    a = searchip.split(".")
    collectionsFin = setup(TCP_FIN_SCAN)
    collectionConn = setup(CONNECT_SCAN)
    collectionSyn = setup(TCP_SYN_SCAN)
    collectionIP = setup(IS_UP_BULK)

    querystr = '/^'+a[0]+'\.'+a[1]+'\.'+a[2]+'\.'+a[3]+'*/.test(this.report)'
    #querystr = '/^127\.0\.0\.1*/.test(this.report)'
    print querystr
    result = []
    print collectionConn.find( { '$where': querystr } ).count()
    for e in collectionConn.find({ '$where': querystr},{'_id':0}):
        result.append(e)
    for e in collectionsFin.find({ '$where': querystr},{'_id':0}):
        result.append(e)
    for e in collectionSyn.find({ '$where': querystr},{'_id':0}):
        result.append(e)
    for e in collectionIP.find({ '$where': querystr},{'_id':0}):
        result.append(e)
    return result


if __name__ == '__main__':
    #Test()

    print getReportData("127.0.0.1", CONNECT_SCAN)

    print getReportData("130.245.124.254", CONNECT_SCAN)

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
