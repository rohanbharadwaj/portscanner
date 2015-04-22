import pymongo
from pymongo import MongoClient


ip = 'localhost'
port = 27017

DB = 'secaffe'
CONNECTTABLE =  'connect_scan'
ISUPTABLE = 'is_up_scan'
FINTABLE = 'tcp_fin_scan'
SYNTABLE = 'tcp_syn_scan'

def setup():
   return MongoClient(ip,port)
   
def insertdata(client,json_data):
    #client = MongoClient(ip,port) 
    db = client.DB
    records = db.is_up_scan
    print records.insert(json_data)
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
        ip.append('127.0.0.'+str(i))
    print ip
    getdata(client)
    #insertdata(client,[{"reqId":"1242525","ip":"[134.214.13.131,233.112.22.1,12.34.234.34]"}])
    #print a
    #insertdata(client,a)
