__author__ = 'rami'

from datetime import datetime
from time import sleep
from collections import OrderedDict
import os
import threading
import jsonpickle
import requests
import web
from config import *
from ReqResObjects import *

# CONSTANTS
SERVICE_ = service + '/'
db = OrderedDict()
nextid = 0

class RestAPIServer:

    app = None

    def GET(self, id=None):
        global db
        if(len(id) == 0):
            return jsonpickle.encode(db)
        elif(int(id) in db):
            return jsonpickle.encode(db[int(id)])
        else:
            return web.notfound()

    def POST(self, id=None):
        global db, nextid
        db[nextid] = jsonpickle.decode(web.data())
        nextid += 1
        print 'ID is Now %d' % nextid, self, db
        return jsonpickle.encode({'created': nextid - 1})

    def DELETE(self, id):
        global db
        if(int(id) in db):
            db.pop(int(id))
            return jsonpickle.encode({'deleted': int(id)})
        else:
            return web.notfound()

    def PUT(self, id):
        global db
        if(int(id) in db):
            db[int(id)] = jsonpickle.decode(web.data())
            return jsonpickle.encode({'updated': int(id)})
        else:
            return web.notfound()

    def process(self):
        currID = -1
        while True:
            print 'Current Job ID = %d' % currID
            if len(self.app.fvars['db']) != 0 and currID < self.app.fvars['nextid']:
                if currID in self.app.fvars['db']:
                    job = self.app.fvars['db'][currID]
                    print "Processing %s..." % jsonpickle.encode(job)
                    # DO SOMETHING
                    self.app.fvars['db'][currID] = 'Processed @ %s' % str(datetime.now())
                currID += 1
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
        print "Creating the message..."
        data = jsonpickle.encode("Test ID = %s" % datetime.now())
        r = requests.post(service, data=data)
        created = r.json()['created']
        print "Message ID: " + str(created)

        print "Showing the message..."
        r = requests.get(SERVICE_ + str(created))
        print "Service returned: " + str(r.json())

        print "Updating the message..."
        data = jsonpickle.encode("Test ID = %s [UPDATED]" % datetime.now())
        r = requests.put(SERVICE_ + str(created), data=data)
        print "Service returned: " + str(r.json())

        print "Showing the message again..."
        r = requests.get(SERVICE_ + str(created))
        print "Service returned: " + str(r.json())

        print "Deleting the message..."
        r = requests.delete(SERVICE_ + str(created))
        print "Service returned: " + str(r.json())

        if test_die:
            os._exit(0)

        return True
#-----------------------------------------------------------------------
# RUN PROGRAM - DO NOT CHANGE
#-----------------------------------------------------------------------

def sendAndReceiveObjects(req):
    r = requests.post(service, data=jsonpickle.encode(req))
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
    if run_basic_test:
        sendAndReceiveObjects(Req("IP_BULK", ["10.10.2.31", "10.10.2.29"]))
        sendAndReceiveObjects(Req("IP_BULK", ["10.9.2.31"]))
        sendAndReceiveObjects(Req("IP_BULK", ["10.7.7.31", "10.7.7.29"]))
    # END OF EXAMPLE

    while server_alive_for != 0:
        server_alive_for -= 1
        sleep(1)

    print 'Server shutting down...'
    os._exit(0)