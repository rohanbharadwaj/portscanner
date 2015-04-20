from flask import Flask
from flask import render_template

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

if __name__ == '__main__':
    app.run(debug=True)
