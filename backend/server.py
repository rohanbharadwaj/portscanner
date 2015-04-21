import uuid;
import json;
from time import sleep
import requests

import jsonpickle

import ipcalc;
from pymongo import MongoClient;
from RestAPIServer import RestAPIServer
from ReqResObjects import *


LIMIT = 1000
pendingList = {}
assignedList = {}

workerId = "127.0.0.1:8080"
prefixUrl = 'http://';
pendingJobCnt = 0

ip = 'localhost';
port = 27017;

# Insert a new job record in mongo database
def insertRecord(scanType, json_data):
    print "sendAndReceiveObjects"
    def __init__(self, ip, port):
        client = MongoClient(ip, port);
        db = client.test_database
        records = db.records
        record_id = records.insert_one(json_data).inserted_id
        print record_id

# Send/Receive requests from RstAPI Server
def sendAndReceiveObjects(url, req):
    print "sendAndReceiveObjects"
    r = requests.post(url, data=jsonpickle.encode(req))
    created = r.json()['created']
    print "Message ID: " + str(created), r.json()
    r = requests.get(url + "/" + str(created))
    print "Service returned: " + str(r.json())
    res = jsonpickle.decode(r.text)
    sleep(3)
    return res

# Assign a job to worker
def assignWork(jobObj):
    print "assignWork"
    print "assignedList: "+ assignedList
    print "pendingJobCnt: "+ pendingJobCnt
    global pendingJobCnt
    for worker in assignedList:
        if not assignedList[worker]:
            assignedList[worker] = jobObj.jobId
            #response = requests.get(url, data=job)
            #print prefixUrl+key
            sendAndReceiveObjects(prefixUrl+worker,jobObj)
            print "jobid: " + jobid + " assigned to " + worker
            if(pendingJobCnt>0):
                pendingJobCnt -=1
                return

# Get a pending job from queue
def getPendingWork():
    print "assignWork"

    if(pendingJobCnt<=0):
        print "getPendingWork: no pending work"
    else:
        for req in pendingList:
            jobObj = pendingList[req].pop()
            if(jobObj):
                return jobObj


# Register a new worker and assign him work
def registerWorker(ip,port):
    print "registerWorker"
    assignedList[ip+":"+str(port)] = None;
    print "new worker registered " + ip + ":" + str(port);
    job = getPendingWork()
    assignWork(job)



# Receive request from UI and divide the work into jobs then assign them
def requestReceiver(scanIp, startPort, endPort, scanType):
    print "requestReceiver"
    reqid = str(uuid.uuid1())
    pendingList[reqid] = [];
    range = endPort - startPort
    global pendingJobCnt

    if(scanType is TCP_FIN_SCAN or scanType is TCP_SYN_SCAN or scanType is CONNECT_SCAN):
        print "ICMP_SCAN"
        stPort = startPort
        enPort = 0
        print scanType
        d = range/LIMIT
        for x in xrange(d+1):
            stPort = stPort
            if (x == d):
                enPort = endPort
            else:
                enPort = stPort + LIMIT
            jobid = str(uuid.uuid1());
            jobObj = Job(scanType ,[scanIp], stPort, enPort, jobid, reqid)
            #job = createJob(jobid, reqid, scanIp, stPort, enPort, scanType)
            #if(job):
            #print "job: "+job;
            pendingList[reqid].append(jobObj);
            pendingJobCnt += 1
            stPort = enPort+1

            assignWork(jobObj);
        print "Work Pending for reqid: " + reqid +"::::"+ str(pendingList[reqid]);
    
    elif(scanType is IS_UP_BULK):
        print "IS_UP_BULK"
        net = ipcalc.Network(scanIp)
        d = range / LIMIT
        startIp = net.host_first();
        for x in xrange(d + 1):
            startIp = startIp

            #if(x==d)

def processReport(reqId, jobId, scanType, report):
    print "processReport: " + report
    insertRecord(scanType, report)
    for key in pendingList:
        if(key == reqId):
            pendingList[reqid].remove(jobId)
            if not pendingList[reqid]:
                print "reqid: "+ reqid + "completed"


# Receive job report from worker
def receiveJobReport(res):
    print "receiveJobReport1: assignedList" + assignedList
    print "receiveJobReport1: pendingList" + pendingList

    jobId = res.jobId
    reqId = res.reqId
    workerId = res.workerId
    scanType = res.type
    if(assignedList[workerId]!=None and assignedList[workerId]==jobId):
        assignedList[workerId]= None;
        print "jobid: "+ jobid +"done by workerId: "+workerId;

    processReport(reqId, jobId, scanType, jsonpickle.encode(res))
    job = getPendingWork()
    assignWork(job)
    print "receiveJobReport2: assignedList" + assignedList
    print "receiveJobReport2: pendingList" + pendingList
    return

# Rest Server started
class MyRestServer(RestAPIServer):
    def doJob(self, job):
        if type(job) == Register:
            registerWorker(job.IP,job.port)
        elif type(job) == Res:
            receiveJobReport(res)
        print "Doing something..."



if __name__ == '__main__':
    srvr = MyRestServer()
    srvr.run_server()

    # sleep(15)
    #sendAndReceiveObjects(URL, Register("27.0.0.0.1",8080))
    registerWorker("172.24.31.198",8080)
    sleep(3)
    requestReceiver("130.245.124.254", 1, 1200, TCP_FIN_SCAN);

    #registerWorker("27.0.0.0.1",8080)
    #print pendingJobCnt;


'''
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
'''
