__author__ = 'rami'

from datetime import datetime
from time import sleep
import errno
from collections import OrderedDict
import threading
import requests
import web
import logging

import jsonpickle

from config import *
from ReqResObjects import *


logging.getLogger("scapy.runtime").setLevel(logging.ERROR)  # Disable the annoying No Route found warning !
from scapy.all import *

# CONSTANTS
SERVICE_ = URL + '/'
job_queue = OrderedDict()
new_job_id = 0
# ---------------------------SCANNER---------------------------------------------------------
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
    icmp = IP(dst=ips) / ICMP(seq=RandShort())
    resp, unresp = sr(icmp, timeout=30)
    catched = []

    oldstdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    resp.summary(lambda (s, r): catcher(r.sprintf("%IP.src%"), catched),
                 lfilter=lambda (s, r): r.sprintf("%ICMP.type%") in ICMP_REACHABLE_TYPE)
    sys.stdout = oldstdout
    return catched


def connect_scan(ips, ports):
    ret = []

    for ip in ips:
        port_banners = []
        sock = []

        """ Prepare all sockets for select """
        for port in ports:
            tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tmp_sock.setblocking(0)
            tmp_sock.connect_ex((ip, port))
            sock.append(tmp_sock)

        cur_time = time.time()
        timeout = 10
        fin_time = cur_time + timeout
        open_socks = []

        while ((fin_time - cur_time) > 0) and len(sock):
            ready_to_read, ready_to_write, in_error = select([], sock, [], fin_time - cur_time)
            cur_time = time.time()
            for elem in ready_to_write:
                sock.remove(elem)  #Remove from the select descriptor list
                err_code = elem.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                #If in error, the port is closed, cleanup our socket
                if err_code:
                    print(elem, errno.errorcode[err_code])
                    elem.close()
                # The connection is established, add to open_socks
                else:
                    elem.setblocking(1)
                    open_socks.append(elem)

        #Close any sockets with no response
        for elem in sock:
            print('Unresponsive sock: ', elem.getpeername())
            elem.close()

        #Send something to grab the banner
        for elem in open_socks:
            print('Open sock: ', elem.getpeername())
            elem.send('hi')

        cur_time = time.time()
        timeout = 10
        fin_time = cur_time + timeout

        #Wait on Select for replies
        while ((fin_time - cur_time) > 0) and len(open_socks):
            print 'Opens socks are: ', open_socks
            ready_to_read, ready_to_write, in_error = select(open_socks, [], [], fin_time - cur_time)
            cur_time = time.time()
            for elem in ready_to_read:
                open_socks.remove(elem)  #Remove from the select descriptor list
                remote = elem.getpeername()
                err_code = elem.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)

                #If in error, the port is closed, cleanup our socket
                if err_code:
                    print(remote, errno.errorcode[err_code])
                    elem.close()
                    port_banners.append([remote[1], "No Banner"])
                # There is something to read
                else:
                    port_banners.append([remote[1], elem.recv(128)])
                    elem.close()

        #Close any sockets with no response
        for elem in open_socks:
            remote = elem.getpeername()
            port_banners.append([remote[1], "No Banner"])
            elem.close()

    ret.append([ip, port_banners])

    print 'IP-Banners: ', ret
    return ret


def tcpFINScan(ips, ports):
    conf.verb = 0  # Disable verbose in sr(), sr1() methods
    start_time = time.time()
    #upIPs = get_up(ips)
    upIPs = ips
    ret = []
    if upIPs:
        print "Host %s is up, start scanning" % upIPs
        for ip in upIPs:
            src_port = RandShort()  # Getting a random port as source port
            p = IP(dst=ip) / TCP(sport=src_port, dport=ports, flags='F')  # Forging SYN packet
            resp, unresp = sr(p, timeout=2)  # Sending packet
            active_ports = []
            inactive_ports = []

            # resp.summary()
            oldstdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            resp.summary(prn=lambda (s, r): catcher(
                TCP_SERVICES[r.sprintf("%TCP.sport%")] if r.sprintf("%TCP.sport%") in TCP_SERVICES else r.sprintf(
                    "%TCP.sport%"), inactive_ports), lfilter=lambda (s, r): r.sprintf("%TCP.flags%") == "RA")
            unresp.summary(prn=lambda (s): catcher(
                TCP_SERVICES[s.sprintf("%TCP.dport%")] if s.sprintf("%TCP.dport%") in TCP_SERVICES else s.sprintf(
                    "%TCP.dport%"), active_ports))
            sys.stdout = oldstdout

            sr(IP(dst=ip) / TCP(sport=src_port, dport=active_ports, flags='RA'), timeout=1)
            for pop in active_ports: print "%d open" % pop
            print "%d closed ports in %d total port scanned" % (len(inactive_ports), len(ports))

            ret.append([ip, active_ports])

    print "Down host(s) %s are: " % list(set(ips).difference(set(upIPs)))

    duration = time.time() - start_time
    print "%s Scan Completed in %fs" % (ips, duration)
    return ret

def tcpSYNScan(ips, ports):
    conf.verb = 0  # Disable verbose in sr(), sr1() methods
    start_time = time.time()
    #upIPs = get_up(ips)
    upIPs = get_up(ips)
    ret = []
    if upIPs:
        print "Host %s is up, start scanning" % upIPs
        for ip in upIPs:
            src_port = RandShort()  # Getting a random port as source port
            p = IP(dst=ip) / TCP(sport=src_port, dport=ports, flags='S')  # Forging SYN packet
            resp, unresp = sr(p, timeout=2)  # Sending packet
            active_ports = []
            inactive_ports = []

            # resp.summary()
            oldstdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            resp.summary(prn=lambda (s, r): catcher(
                TCP_SERVICES[r.sprintf("%TCP.sport%")] if r.sprintf("%TCP.sport%") in TCP_SERVICES else r.sprintf(
                    "%TCP.sport%"), active_ports), lfilter=lambda (s, r): r.sprintf("%TCP.flags%") == "SA")
            resp.summary(prn=lambda (s, r): catcher(
                TCP_SERVICES[r.sprintf("%TCP.sport%")] if r.sprintf("%TCP.sport%") in TCP_SERVICES else r.sprintf(
                    "%TCP.sport%"), inactive_ports), lfilter=lambda (s, r): r.sprintf("%TCP.flags%") == "RA")
            unresp.summary(prn=lambda (s): catcher(
                TCP_SERVICES[s.sprintf("%TCP.dport%")] if s.sprintf("%TCP.dport%") in TCP_SERVICES else s.sprintf(
                    "%TCP.dport%"), inactive_ports))
            sys.stdout = oldstdout

            sr(IP(dst=ip) / TCP(sport=src_port, dport=active_ports, flags='RA'), timeout=1)
            for pop in active_ports: print "%d open" % pop
            print "%d closed ports in %d total port scanned" % (len(inactive_ports), len(ports))

            ret.append([ip, active_ports])

    print "Down host(s) %s are: " % list(set(ips).difference(set(upIPs)))

    duration = time.time() - start_time
    print "%s Scan Completed in %fs" % (ips, duration)
    return ret


#----------------------END OF SCANNER LOGIC-----------------------------------------------

class RestAPIServer:
    app = None

    def GET(self, id=None):
        global job_queue
        try:
            if (len(id) == 0 or int(id) < 0):
                return jsonpickle.encode(job_queue)
            elif (int(id) in job_queue):
                return jsonpickle.encode(job_queue[int(id)])
        except ValueError as ve:
            pass  #forget about int() conversion
        return web.notfound()

    def POST(self, id=None):
        global job_queue, new_job_id
        job_queue[new_job_id] = jsonpickle.decode(web.data())
        new_job_id += 1
        #print 'ID is Now %d' % new_job_id, self, job_queue
        return jsonpickle.encode({'work_id': new_job_id - 1})

    def DELETE(self, id):
        global job_queue
        if (int(id) in job_queue):
            job_queue.pop(int(id))
            return jsonpickle.encode({'deleted': int(id)})
        else:
            return web.notfound()

    def PUT(self, id):
        global job_queue
        if (int(id) in job_queue):
            job_queue[int(id)] = jsonpickle.decode(web.data())
            return jsonpickle.encode({'updated': int(id)})
        else:
            return web.notfound()

    """
    Override this method to do custom jobs for your derived RestAPIServer.
    """

    def doJob(self, job):

        global sendAndReceiveObjects

        if type(job) != Job:
            print 'Invalid scan-job passed. Ignoring it.'
            return

        try:
            res = Res(job)
            res.workerIP_Port = res.workerIP_Port.format(socket.gethostbyname(socket.getfqdn()), SERVICE_PORT)

            if job.scanType == CONNECT_SCAN:
                res.report = connect_scan(job.IPs, job.ports)
            elif job.scanType == TCP_FIN_SCAN:
                res.report = tcpFINScan({x: "" for x in job.IPs}.keys(), job.ports)
            elif job.scanType == TCP_SYN_SCAN:
                res.report = tcpSYNScan({x: "" for x in job.IPs}.keys(), job.ports)
            elif job.scanType == IS_UP or job.scanType == IS_UP_BULK:
                res.report = get_up({x: "" for x in job.IPs}.keys())
            else:
                print 'Undefined scan-type in job. Ignoring it.'
                return

            #sendAndReceiveObjects(SERVER_URL, res)

        except Exception as e:
            pass

        print 'REQ[{0}] processed with RESPONSE[{1}]'.format(jsonpickle.encode(job), jsonpickle.encode(res))


    def process(self, remove_job_after_processing=True):
        processingID = -1
        while True:
            if len(self.app.fvars['job_queue']) != 0 and processingID < self.app.fvars['new_job_id']:
                if processingID in self.app.fvars['job_queue']:
                    job = None
                    if not remove_job_after_processing:
                        job = self.app.fvars['job_queue'][processingID]
                    else:
                        job = self.app.fvars['job_queue'].pop(processingID)
                    print "Processing Job-ID[{0}] Job[{1}]...".format(processingID, jsonpickle.encode(job))
                    # DO SOMETHING
                    self.doJob(job)
                    # DONE SOMETHING
                    #self.app.fvars['job_queue'][processingID] = 'Processed @ %s' % str(datetime.now())
                processingID += 1
            else:
                #print "Nothing to process!"
                sleep(1)

    def run_server(self):
        global URL_PATTERN_SERVICED
        self.app = web.application(URL_PATTERN_SERVICED, globals())
        webthread = threading.Thread(target=self.app.run)
        processthread = threading.Thread(target=self.process)
        webthread.start()
        sleep(3)
        processthread.start()
        return [webthread, processthread]

    def test_server(self, test_die=True):
        global SERVICE_
        print "Testing server APIs..."
        print "New request..."
        data = jsonpickle.encode("Test ID = %s" % datetime.now())
        response = requests.post(URL, data=data)
        work_id = response.json()['work_id']
        print "Job ID: " + str(work_id)

        print "Get request..."
        response = requests.get(SERVICE_ + str(work_id))
        print "Response: " + str(response.json())

        print "Change request..."
        data = jsonpickle.encode("Test ID = %s [UPDATED]" % datetime.now())
        response = requests.put(SERVICE_ + str(work_id), data=data)
        print "Response: " + str(response.json())

        print "Get request again..."
        response = requests.get(SERVICE_ + str(work_id))
        print "Response: " + str(response.json())

        print "Removing the request..."
        response = requests.delete(SERVICE_ + str(work_id))
        print "Response: " + str(response.json())

        if test_die:
            os._exit(0)

        return True


#-----------------------------------------------------------------------
# RUN PROGRAM - DO NOT CHANGE
#-----------------------------------------------------------------------

def sendAndReceiveObjects(url, req, receive = False):
    try:
        r = requests.post(url, data=jsonpickle.encode(req))
        work_id = r.json()['work_id']
        #print "Message ID: " + str(work_id), r.json()
        if receive:
            sleep(3)
            r = requests.get(url + str(work_id))
            #print "Service returned: " + str(r.json())
            res = jsonpickle.decode(r.text)
            return res
    except Exception as e:
        pass

    return req


if __name__ == "__main__":
    currentServer = RestAPIServer()
    currentServer.run_server()

    if RUN_API_TEST: currentServer.test_server(False)

    # EXAMPLE OF SENDING REQ RES OBJECTS
    if RUN_BASIC_TEST:
        sendAndReceiveObjects(URL, Job(IS_UP, ["172.24.22.114"]))
        sendAndReceiveObjects(URL, Job(IS_UP_BULK, ["172.24.22.114", "130.245.124.254"]))
        sendAndReceiveObjects(URL, Job(TCP_SYN_SCAN, ["172.24.22.114", "130.245.124.254"]))
        sendAndReceiveObjects(URL, Job(TCP_FIN_SCAN, ["172.24.22.114"], 21, 2000))
        sendAndReceiveObjects(URL, Job(CONNECT_SCAN, ["172.24.22.114"], 21, 22))
    # END OF EXAMPLE

    #sendAndReceiveObjects(URL, Job(IS_UP, ["172.24.22.114"]))
    #sendAndReceiveObjects(URL, Job(IS_UP, ["130.245.124.254"]))
    #sendAndReceiveObjects(URL, Job(TCP_SYN_SCAN, ["130.245.124.254"]))
    #sendAndReceiveObjects(SERVER_URL, Register("172.24.31.198", 8080))

    while SERVER_ALIVE_FOR_SECONDS != 0:
        SERVER_ALIVE_FOR_SECONDS -= 1
        sleep(1)
    print 'Server shutting down...'
    os._exit(0)