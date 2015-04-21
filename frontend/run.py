from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request,json
from data import fetch

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/index')
def index():
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
    port_range = request.form['port_range']
    type_scan = request.form['optionsRadios']
    # user =  request.form['username'];
    # password = request.form['password'];
    print connect_input_ip
    return json.dumps({'connect_input_ip':connect_input_ip,'port_range':port_range,'type_scan':type_scan});


if __name__ == '__main__':
    app.run(debug=True)
