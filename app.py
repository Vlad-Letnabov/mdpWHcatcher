from flask import Flask,request
import subprocess
import xml.etree.cElementTree as ET
import os
import logging
from logging.handlers import RotatingFileHandler

strfmt = '%(asctime)s %(thread)d %(name)s [%(levelname)s] %(funcName)s: %(message)s'
logging.basicConfig(filename='wh.log', level=logging.DEBUG, format=strfmt)
handler = RotatingFileHandler('wh.log', maxBytes=1000000, backupCount=1)
handler.setLevel(logging.DEBUG)

app = Flask(__name__)
app.logger.addHandler(handler)


def readconfig():
    config=dict(host='localhost',user='noboby',path='/tmp',fromuser='')
    path =  os.path.abspath("config.xml") #'config.xml'
    app.logger.info(path)
    tree = ET.parse(path)
    root = tree.getroot()
    for key,value in config.items():
        try:
            node = root.find(f'./{key}')
            if node.text:
                config[key] = node.text
        except BaseException as exp:
            app.logger.error(str(exp))
            app.logger.error('check config')
    return config

config = readconfig()
app.logger.info(config)
@app.route('/')
def hello_world():
    app.logger.info('hello_world page')
    return 'Hello World!'

@app.route('/catchwh/<string:script>', methods=['GET'])
def catchwhget(script):
    app.logger.info(script)
    call_script(script)

@app.route('/catchwh/', methods=['POST','GET'])
def catchwh():
    app.logger.info(f"method: {request.method}")
    if request.method == 'POST':
        script=None
        if request.is_json:
            data = request.get_json()
            app.logger.info(str(data))
            if 'tags' in data:
                if 'script' in data['tags']:
                    script = data['tags']['script']
        else:
            script = request.form.get('script')
        if script:
            app.logger.info(f"get via POST: {script}")
            return call_script(script)
    else:
        script = request.args.get('script')
        app.logger.info(f"args: {request.args}, {script}")
        if script:
            app.logger.info(f"get via GET: {script}")
            return call_script(script)
    return {}

def call_script(script):
    app.logger.info(script)
    call_arr = ['/usr/bin/sudo', 'ssh', f"{config['user']}@{config['host']}", f"{config['path']}{script}"]
    if config['fromuser'] and config['fromuser']!='':
        call_arr = ['/usr/bin/sudo', '-u', f"{config['fromuser']}", 'ssh', f"{config['user']}@{config['host']}", f"{config['path']}{script}"]
    app.logger.info(str(call_arr))
    result = subprocess.call(call_arr)
    return {'result':result}

if __name__ == '__main__':

    app.logger.info('run app on 0.0.0.0:5000')
    app.run(host='0.0.0.0')
