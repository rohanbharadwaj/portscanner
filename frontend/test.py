jsondata = [{"scannedports": "9010.0-10010.0", "ip": "130.245.124.254", "reqId": "128bca28-ea3a-11e4-a9c1-bc773780be52", "openports": ""}, {"ip": "130.245.124.254", "reqId": "128bca28-ea3a-11e4-a9c1-bc773780be52", "scannedports": "8009.0-9009.0", "openports": "[8081.0, u''],[8080.0, u'HTTP/1.1 400 Bad Request\\r\\n']"}, {"ip": "130.245.124.254", "reqId": "128bca28-ea3a-11e4-a9c1-bc773780be52", "scannedports": "7008.0-8008.0", "openports": "[7890.0, u'No Banner']"}, {"ip": "130.245.124.254", "reqId": "128bca28-ea3a-11e4-a9c1-bc773780be52", "scannedports": "6007.0-7007.0", "openports": "[6125.0, u''],[6444.0, u'No Banner']"}, {"ip": "130.245.124.254", "reqId": "128bca28-ea3a-11e4-a9c1-bc773780be52", "scannedports": "4005.0-5005.0", "openports": ""}, {"ip": "130.245.124.254", "reqId": "128bca28-ea3a-11e4-a9c1-bc773780be52", "scannedports": "3004.0-4004.0", "openports": "[3306.0, {u'py/bytes': u\"X=00=00=00=FFj=04Host 'ha192-200.resnet.stonybrook.edu' is not allowed to c=\\nonnect to this MySQL server\"}],[4000.0, u'No Banner'],[4002.0, u'No Banner'],[4003.0, u'No Banner'],[4001.0, u'No Banner']"}, {"ip": "130.245.124.254", "reqId": "128bca28-ea3a-11e4-a9c1-bc773780be52", "scannedports": "2003.0-3003.0", "openports": "[2049.0, u'No Banner']"}, {"ip": "130.245.124.254", "reqId": "128bca28-ea3a-11e4-a9c1-bc773780be52", "scannedports": "1002.0-2002.0", "openports": ""}]

print len(jsondata)

num = len(jsondata)
 
data ={}
for i in xrange(num):
    if not data[jsondata[i]["ip"]]:
    	data[jsondata[i]["ip"]] = data[jsondata[i]["openports"]
    else: 	
    	data[jsondata[i]["ip"]]+ = data[jsondata[i]["openports"]