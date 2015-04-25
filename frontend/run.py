from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request,json
from data import fetch
from datautil import *
import sys
sys.path.append('../backend')
from server import *

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/index')
def index():
    srvr = MyRestServer()
    srvr.run_server()
    return render_template('index.html')

@app.route('/auto')
def auto():
    return render_template('auto.html')

@app.route('/connect')
def connect():
    return render_template('connect.html')

@app.route('/fin')
def fin():
    return render_template('fin.html') 

@app.route('/isalive')
def isalive():
    return render_template('isalive.html')
 
@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/syn')
def syn():
    return render_template('syn.html')

@app.route('/fetchdata',methods=["GET", "POST"])
def fetchdata():
	if request.method == "GET":
		return fetch() 

@app.route('/test')
def test():
	return render_template('test.html')

@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

@app.route('/signUpUser', methods=['POST'])
def signUpUser():
    user =  request.form['username'];
    password = request.form['password'];
    return json.dumps({'status':'OK','user':user,'pass':password});
  
@app.route('/senddata')
def senddata():
    return render_template('senddata.html')

@app.route('/receivedata', methods=['POST'])
def receivedata():
    connect_input_ip = request.form['connect_input_ip']
    port_range = request.form['connect_port']
    type_scan = request.form['seqran']
    # user =  request.form['username'];
    # password = request.form['password'];
    #[{"reqid": "a5da0bce-eaed-11e4-9475-000c29683c93", "numjob": 1}]
    return requestReceiver(connect_input_ip, type_scan, port_range, CONNECT_SCAN)
    # print connect_input_ip
    # reqId = "128bca28-ea3a-11e4-a9c1-bc773780be52"
    # numjobs = 11
    # return json.dumps({'connect_input_ip':connect_input_ip,'port_range':port_range,'type_scan':type_scan,
    #                     'reqId':reqId,'numjobs':numjobs});

@app.route('/loaddata')
def loaddata():
    return render_template('angular_view.html')

@app.route('/mongogetdata',methods=['GET'])
def mongogetdata():
    return getdata()

@app.route('/submit',methods=['POST'])
def submit():
    ip = request.form['input_ip']
    return json.dumps([{'reqId':'12345','numjobs':'8'}])
    #return json.dumps([{'ip':ip}])    

@app.route('/getJobStatus',methods=['POST'])
def getJobStatus():
    reqId = request.form['reqId']
    scantype = request.form['scantype']
    count = getCount(reqId,scantype)
    return json.dumps([{'reqId':reqId,'count':count}])

@app.route('/getReports',methods=['POST']) 
def getReports():
    ip = request.form['']   
    # i = 0
    # if(i>8):
    #     return json.dumps([{'name':name,'done':'true','pending':0}])
    # else:
    #     return json.dumps([{'name':name,'done':'false','pending':8}])


@app.route('/fetchResults',methods=['POST','GET'])
def fetchResults():
    if request.method == "POST":
        reqId = request.form['reqId']
        scantype = request.form['scantype']
        return fetchProcessedData(reqId,scantype)
    if request.method == "GET":
        res = fetchProcessedData("2e591188-eb7b-11e4-a9c1-bc773780be52",CONNECT_SCAN)
        print res
        return res    


@app.route('/connect_post',methods=['POST'])
def connect_post():
    connect_input_ip = request.form['connect_input_ip']
    port_range = request.form['port_range']
    type_scan = request.form['optionsRadios']
    # user =  request.form['username'];
    # password = request.form['password'];
    print connect_input_ip
    return json.dumps({'connect_input_ip':connect_input_ip,'port_range':port_range,'type_scan':type_scan});

if __name__ == '__main__':
    app.run(debug=True)
