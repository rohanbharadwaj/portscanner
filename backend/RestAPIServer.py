__author__ = 'rami'

from datetime import datetime
from time import sleep
from collections import OrderedDict
import os
import sys
import threading
import jsonpickle
import requests
import web
from config import *
from ReqResObjects import *

import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR) # Disable the annoying No Route found warning !
from scapy.all import *

# CONSTANTS
SERVICE_ = URL + '/'
job_queue = OrderedDict()
new_job_id = 0
#---------------------------SCANNER---------------------------------------------------------
"""
Dirtiest code i have ever written.
Only used to catch the lambda expression
:param ips:
:return:
"""
def catcher(i, o):
    o.append(i)
    return i

def get_up(ips):
    """ Tests if host is up """
    icmp = IP(dst=ips)/ICMP()
    resp, unresp = sr(icmp, timeout=300)
    catched = []
    oldstdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    resp.summary( lambda(s,r): catcher(r.sprintf("%IP.src%"), catched) )
    sys.stdout = oldstdout
    return catched

def doSomething(ips):
    conf.verb = 0 # Disable verbose in sr(), sr1() methods
    start_time = time.time()
    ports = list(range(1, 100))
    closed = 0
    upIPs = get_up(ips)
    if upIPs:
        print "Host %s is up, start scanning" % upIPs
        for ip in upIPs:
            src_port = RandShort() # Getting a random port as source port
            p = IP(dst=ip)/TCP(sport=src_port, dport=ports, flags='S') # Forging SYN packet
            resp, unresp = sr(p, timeout=2) # Sending packet
            active_ports = []
            inactive_ports = []

            # resp.summary()
            oldstdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            resp.summary( prn=lambda(s,r): catcher(TCP_SERVICES[r.sprintf("%TCP.sport%")] if r.sprintf("%TCP.sport%") in TCP_SERVICES else r.sprintf("%TCP.sport%"), active_ports), lfilter = lambda (s,r): r.sprintf("%TCP.flags%") == "SA" )
            resp.summary( prn=lambda(s,r): catcher(TCP_SERVICES[r.sprintf("%TCP.sport%")] if r.sprintf("%TCP.sport%") in TCP_SERVICES else r.sprintf("%TCP.sport%"), inactive_ports), lfilter = lambda (s,r): r.sprintf("%TCP.flags%") == "RA" )
            unresp.summary( prn=lambda(s): catcher(TCP_SERVICES[s.sprintf("%TCP.sport%")] if s.sprintf("%TCP.sport%") in TCP_SERVICES else s.sprintf("%TCP.sport%"), inactive_ports))
            sys.stdout = oldstdout

            sr(IP(dst=ip)/TCP(sport=src_port, dport=active_ports, flags='RA'), timeout=1)
            for pop in active_ports: print "%d open" % pop
            print "%d closed ports in %d total port scanned" % (len(inactive_ports), len(ports))

    print "Down host(s) %s are: " % list(set(ips).difference(set(upIPs)))

    duration = time.time()-start_time
    print "%s Scan Completed in %fs" % (ips, duration)
#----------------------END OF SCANNER LOGIC-----------------------------------------------

class RestAPIServer:

    app = None

    def GET(self, id=None):
        global job_queue
        if(len(id) == 0 or int(id) < 0):
            return jsonpickle.encode(job_queue)
        elif(int(id) in job_queue):
            return jsonpickle.encode(job_queue[int(id)])
        else:
            return web.notfound()

    def POST(self, id=None):
        global job_queue, new_job_id
        job_queue[new_job_id] = jsonpickle.decode(web.data())
        new_job_id += 1
        print 'ID is Now %d' % new_job_id, self, job_queue
        return jsonpickle.encode({'created': new_job_id - 1})

    def DELETE(self, id):
        global job_queue
        if(int(id) in job_queue):
            job_queue.pop(int(id))
            return jsonpickle.encode({'deleted': int(id)})
        else:
            return web.notfound()

    def PUT(self, id):
        global job_queue
        if(int(id) in job_queue):
            job_queue[int(id)] = jsonpickle.decode(web.data())
            return jsonpickle.encode({'updated': int(id)})
        else:
            return web.notfound()

    def process(self):
        processingID = -1
        while True:
            print 'Current Job ID = %d' % processingID
            if len(self.app.fvars['job_queue']) != 0 and processingID < self.app.fvars['new_job_id']:
                if processingID in self.app.fvars['job_queue']:
                    job = self.app.fvars['job_queue'][processingID]
                    print "Processing %s..." % jsonpickle.encode(job)
                    # DO SOMETHING
                    doSomething({x:"" for x in job.IPs}.keys())
                    # DONE SOMETHING
                    self.app.fvars['job_queue'][processingID] = 'Processed @ %s' % str(datetime.now())
                processingID += 1
            else:
                print "Nothing to process!"
                sleep(5)

    def run_server(self):
        global urls
        self.app = web.application(urls, globals())
        webthread = threading.Thread(target = self.app.run)
        processthread = threading.Thread(target = self.process)
        webthread.start()
        sleep(3)
        processthread.start()
        return [webthread, processthread]

    def test_server(self, test_die = True):
        global SERVICE_
        print "Testing server APIs..."
        print "New request..."
        data = jsonpickle.encode("Test ID = %s" % datetime.now())
        r = requests.post(URL, data=data)
        created = r.json()['created']
        print "Job ID: " + str(created)

        print "Get request..."
        r = requests.get(SERVICE_ + str(created))
        print "Response: " + str(r.json())

        print "Change request..."
        data = jsonpickle.encode("Test ID = %s [UPDATED]" % datetime.now())
        r = requests.put(SERVICE_ + str(created), data=data)
        print "Response: " + str(r.json())

        print "Get request again..."
        r = requests.get(SERVICE_ + str(created))
        print "Response: " + str(r.json())

        print "Removing the request..."
        r = requests.delete(SERVICE_ + str(created))
        print "Response: " + str(r.json())

        if test_die:
            os._exit(0)

        return True
#-----------------------------------------------------------------------
# RUN PROGRAM - DO NOT CHANGE
#-----------------------------------------------------------------------

def sendAndReceiveObjects(req):
    r = requests.post(URL, data=jsonpickle.encode(req))
    created = r.json()['created']
    print "Message ID: " + str(created), r.json()
    r = requests.get(SERVICE_ + str(created))
    print "Service returned: " + str(r.json())
    res = jsonpickle.decode(r.text)
    sleep(3)
    return res

if __name__ == "__main__":
    currentServer = RestAPIServer()
    currentServer.run_server()

    if run_api_test: currentServer.test_server(False)

    # EXAMPLE OF SENDING REQ RES OBJECTS
    """
    if run_basic_test:
        sendAndReceiveObjects(Req("IP_BULK", ["10.10.2.31", "10.10.2.29"]))
        sendAndReceiveObjects(Req("IP_BULK", ["10.9.2.31"]))
        sendAndReceiveObjects(Req("IP_BULK", ["10.7.7.31", "10.7.7.29"]))
    """
    # END OF EXAMPLE
    sendAndReceiveObjects(Req("TCP_SYN_SCAN_PORT", ["172.24.22.114", "130.245.124.254"]))
    while server_alive_for != 0:
        server_alive_for -= 1
        sleep(1)

    print 'Server shutting down...'
    os._exit(0)
