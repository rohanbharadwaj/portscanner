import uuid;
import json;
import requests;
import json;
import ipcalc;
from pymongo import MongoClient;
from RestAPIServer import RestAPIServer
from ReqResObjects import *

from datetime import datetime
from time import sleep
import errno
from collections import OrderedDict
import threading
import jsonpickle
import requests
import web
from config import *


LIMIT = 1000
FIN_SCAN = TCP_FIN_SCAN
SYN_SCAN = TCP_SYN_SCAN
CON_SCAN = CONNECT_SCAN
ICMP_SCAN = IS_UP_BULK

pendingList = {}
assignedList = {}

workerId = "127.0.0.1:8080"
prefixUrl = 'http://';
pendingJobCnt = 0

ip = 'localhost';
port = 27017;

def insertRecord(json_data):
    def __init__(self, ip, port):
        client = MongoClient(ip, port);
        db = client.test_database
        records = db.records
        record_id = records.insert_one(json_data).inserted_id
        print record_id

def assignWork(jobid, reqid, scanIp, stPort, enPort, scanType):
    for key in assignedList:
        if not assignedList[key]:
            assignedList[workerId] = jobid
            #response = requests.get(url, data=job)
            self, type, IPs, startPort, endPort, jobId=None, reqId=None
            sendAndReceiveObjects(prefixUrl+workerId, Job(scanType ,scanIp, stPort, enPort, jobid, reqid)
            print response;

def createJob(jobid, reqid, scanIp, startPort, endPort, scanType):
    data = {}
    json_data =  json.dumps({})
    data['jobid'] = jobid
    data['reqid'] = reqid
    data['scanIp'] = scanIp
    data['startPort'] = startPort
    data['endPort'] = endPort
    data['scanType'] = scanType
    json_data = json.dumps(data)
    return json_data

def requestReceiver(scanIp, startPort, endPort, scanType):
    reqid = str(uuid.uuid1())
    pendingList[reqid] = [];
    range = endPort-startPort
    global pendingJobCnt

    if(scanType is FIN_SCAN or scanType is SYN_SCAN or scanType is CON_SCAN):
        stPort = startPort
        enPort = 0
        d = range/LIMIT
        for x in xrange(d+1):
            stPort = stPort
            if(x==d):
                enPort=endPort
            else:
                enPort = stPort+LIMIT
            jobid = str(uuid.uuid1());
            job = createJob(jobid, reqid, scanIp, stPort, enPort, scanType)
            if(job):
                pendingList[reqid].append(jobid);
                assignWork(jobid, reqid, scanIp, stPort, enPort, scanType);
                print "job: "+job;
                pendingJobCnt += 1
            stPort = enPort+1
        print "Work Pending for reqid: " + reqid +"::::"+ pendingList[reqid];
    
    elif(scanType is CON_SCAN):
        net = ipcalc.Network(scanIp)
        d = range/LIMIT
        startIp = net.host_first();
        for x in xrange(d+1):
            startIp = startIp
            #if(x==d)
                
def receiveJobReport(report):
    global pendingJobCnt
    jobid = json.load(report)["jobid"]
    reqid = json.load(report)["reqid"]
    workerid = json.load(report)["reqid"]
    if(assignedList[workerid]!=None and assignedList[workerid]==jobid):
        assignedList[workerid]=[];
        print "jobid: "+ jobid +"done by workerid: "+workerid;
        for key in pendingList:
            if(key == reqid):
                pendingList[reqid].remove(jobid)
                pendingJobCnt -= 1
                if not pendingList[reqid]:
                    print "reqid: "+ reqid + "completed";
    return

def registerWorker(ip,port):
    assignedList[ip+":"+str(port)] = [];

class MyRestServer(RestAPIServer):
    def doJob(self, job):
        if type(job) == Register:
            registerWorker(job.IP,job.port)
        print "Doing something..."

def sendAndReceiveObjects(url, req):
    r = requests.post(url, data=jsonpickle.encode(req))
    created = r.json()['created']
    print "Message ID: " + str(created), r.json()
    r = requests.get(url + "/" + str(created))
    print "Service returned: " + str(r.json())
    res = jsonpickle.decode(r.text)
    sleep(3)
    return res

if __name__ == '__main__':
    srvr = MyRestServer()
    srvr.run_server()
    sendAndReceiveObjects(URL, Register("27.0.0.0.1",8080))

    requestReceiver("130.245.124.254", 1, 5500, FIN_SCAN);
    #registerWorker("27.0.0.0.1",8080)
    #print pendingJobCnt;
