__author__ = 'rami'

from optparse import OptionParser
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
import traceback

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)  # Disable the annoying No Route found warning !
from scapy.all import *

# CONSTANTS
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((SERVER_IP, SERVER_PORT))
LOCAL_IP = s.getsockname()[0]
s.close()

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


def get_up(ips, catched=[]):
    try:
        """ Tests if host is up """
        #print "ips= ", ips
        icmp = IP(dst=ips) / ICMP(seq=RandShort())
        resp, unresp = sr(icmp, timeout=1, verbose=0)
        #print "Send/Receive Done"
        oldstdout = sys.stdout
        #sys.stdout = open(os.devnull, 'w')
        resp.summary(lambda (s, r): catcher(r.sprintf("%IP.src%"), catched),lfilter=lambda (s, r): r.sprintf("%ICMP.type%") in ICMP_REACHABLE_TYPE)
        sys.stdout = oldstdout
    except Exception as e:
        traceback.print_exc()
    return catched


def connect_scan(ips, ports, ret=[]):
    start_time = time.time()
    try:
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
                    sock.remove(elem)  # Remove from the select descriptor list
                    err_code = elem.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                    # If in error, the port is closed, cleanup our socket
                    if err_code:
                        print(elem, errno.errorcode[err_code])
                        elem.close()
                    # The connection is established, add to open_socks
                    else:
                        elem.setblocking(1)
                        open_socks.append(elem)

            # Close any sockets with no response
            for elem in sock:
                print('Unresponsive sock: ', elem.getpeername())
                elem.close()

            # Send something to grab the banner
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
    except:
        traceback.print_exc()
    duration = time.time() - start_time
    print "%s Scan Completed in %fs" % (ips, duration)
    return ret


def tcpFINScan(ips, ports, ret=[]):

    conf.verb = 0  # Disable verbose in sr(), sr1() methods
    start_time = time.time()
    # upIPs = get_up(ips)
    upIPs = ips
    try:
        if upIPs:
            print "Host %s is up, start scanning" % upIPs
            for ip in upIPs:
                src_port = RandShort()  # Getting a random port as source port
                p = IP(dst=ip) / TCP(sport=src_port, dport=ports, flags='F')  # Forging SYN packet
                resp, unresp = sr(p, timeout=1)  # Sending packet
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

            #print "Down host(s) %s are: " % list(set(ips).difference(set(upIPs)))
    except:
        traceback.print_exc()
    duration = time.time() - start_time
    print "%s Scan Completed in %fs" % (ips, duration)
    return ret


def tcpSYNScan(ips, ports, ret=[]):
    conf.verb = 0  # Disable verbose in sr(), sr1() methods
    start_time = time.time()
    # upIPs = get_up(ips)
    upIPs = ips
    try:
        if upIPs:
            print "Host {0} is up, start scanning".format(upIPs)
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

    except:
        traceback.print_exc()
    duration = time.time() - start_time
    print "%s Scan Completed in %fs" % (ips, duration)
    return ret


# ----------------------END OF SCANNER LOGIC-----------------------------------------------
class RestAPIServer(object):
    app = None

    def GET(self, id=None):
        global job_queue
        try:
            if (len(id) == 0 or int(id) < 0):
                return jsonpickle.encode(job_queue)
            elif (int(id) in job_queue):
                return jsonpickle.encode(job_queue[int(id)])
        except ValueError as ve:
            pass  # forget about int() conversion
        return web.notfound()

    def POST(self, id=None):
        global job_queue, new_job_id
        job_queue[new_job_id] = jsonpickle.decode(web.data())
        new_job_id += 1
        # print 'ID is Now %d' % new_job_id, self, job_queue
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
        pass

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
                    res = self.doJob(job)
                    print 'REQ[{0}] processed with RESPONSE[{1}]'.format(jsonpickle.encode(job), jsonpickle.encode(res))
                    # DONE SOMETHING
                    # self.app.fvars['job_queue'][processingID] = 'Processed @ %s' % str(datetime.now())
                processingID += 1
            else:
                # print "Nothing to process!"
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


# -----------------------------------------------------------------------
# RUN PROGRAM - DO NOT CHANGE
#-----------------------------------------------------------------------

class CustomRestScanServer(RestAPIServer):

    def threadFns(self, fn, job, res):
        processed = 0
        while processed < len(job.IPPorts) - 1:
            threads = []
            numThreads = 0
            for ip, pstart, pend in list(job.IPPorts[processed:]):
                portRange = None
                args = None
                if pstart and pend and pstart <= pend:
                    portRange = list(range(pstart, pend))
                    args = tuple([[str(ip)], portRange, res.report])
                    print 'Processing {0}:{1}'.format(ip, (pstart, pend))
                else:
                    args = tuple([[str(ip)], res.report])
                    print 'Processing {0}'.format(ip)
                thread = threading.Thread(target=fn, args=args)
                thread.start()
                threads.append(thread)
                numThreads += 1
                processed += 1
                if numThreads > MAX_THREADS: break
            for t in threads: t.join()

    def doJob(self, job):

        global sendAndReceiveObjects

        if type(job) != Job:
            print 'Invalid scan-job passed. Ignoring it.'
            return

        try:
            res = Res(job)
            res.workerIP_Port = res.workerIP_Port.format(LOCAL_IP, LOCAL_SERVICE_PORT)
            res.timestamp = str(datetime.now())
            res.report = []

            if job.scanType == CONNECT_SCAN:
                self.threadFns(connect_scan, job, res)
            elif job.scanType == TCP_FIN_SCAN:
                self.threadFns(tcpFINScan, job, res)
            elif job.scanType == TCP_SYN_SCAN:
                self.threadFns(tcpSYNScan, job, res)
            elif job.scanType == IS_UP or job.scanType == IS_UP_BULK:
                self.threadFns(get_up, job, res)
            else:
                print 'Undefined scan-type in job. Ignoring it.'
                return

            sendAndReceiveObjects(SERVER_URL, res)
        except Exception as e:
            traceback.print_exc()

        return res

def sendAndReceiveObjects(url, req, receive=False):
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


def startSendingHeartBeats():
    while (True):
        try:
            sleep(TIME_IN_SEC_BETWEEN_HEARTBEATS)
            print 'Sending heartbeat to master {0}:{1} '.format(SERVER_IP, SERVER_PORT)
            sendAndReceiveObjects(SERVER_URL, HeartBeat(LOCAL_IP, LOCAL_SERVICE_PORT))
        except Exception as e:
            pass


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-P", "--serverip", dest="serverip", help="Server IP", default=SERVER_IP)
    parser.add_option("-I", "--serverport", dest="serverport", help="Server Port", default=SERVER_PORT)
    parser.add_option("-p", "--port", dest="port", help="Local Port", default=LOCAL_SERVICE_PORT)
    (options, args) = parser.parse_args()
    print 'USER DEFINED OPTIONS : {0}'.format(options)
    SERVER_IP = options.__dict__['serverip']
    SERVER_PORT = options.__dict__['serverport']
    LOCAL_SERVICE_PORT = options.__dict__['port']

    currentServer = CustomRestScanServer()
    currentServer.run_server()

    if RUN_API_TEST: currentServer.test_server(False)

    # EXAMPLE OF SENDING REQ RES OBJECTS
    if RUN_BASIC_TEST:
        sendAndReceiveObjects(URL, Job(IS_UP, [("172.24.22.114", None, None)]))
        sendAndReceiveObjects(URL, Job(IS_UP_BULK, [("172.24.22.114", None, None), ("130.245.124.254", None, None)]))
        sendAndReceiveObjects(URL, Job(TCP_SYN_SCAN, [("172.24.22.114", 1, 100), ("130.245.124.254", 1, 100)]))
        sendAndReceiveObjects(URL, Job(TCP_FIN_SCAN, [("172.24.22.114", 1, 100)]))
        sendAndReceiveObjects(URL, Job(CONNECT_SCAN, [("172.24.22.114", 1, 100)]))
    # END OF EXAMPLE

    # START SENDING HEARTBEATS TO MASTER SERVER
    threading.Thread(target=startSendingHeartBeats()).start()

    # START SENDING HEART BEAT MESSAGES
    while SERVER_ALIVE_FOR_SECONDS != 0:
        SERVER_ALIVE_FOR_SECONDS -= 1
        sleep(1)
    print 'Server shutting down...'
    os._exit(0)