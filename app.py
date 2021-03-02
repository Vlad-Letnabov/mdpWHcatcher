from flask import Flask
import subprocess
import xml.etree.cElementTree as ET
import os
import logging
from logging.handlers import RotatingFileHandler

strfmt = '%(asctime)s %(thread)d %(name)s [%(levelname)s] %(funcName)s: %(message)s'
logging.basicConfig(filename='wh.log', level=logging.DEBUG, format=strfmt)
handler = RotatingFileHandler('wh.log', maxBytes=10000, backupCount=1)
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
def catchwh(script):
    app.logger.info(script)
    call_arr = ['sudo', 'ssh', f"{config['user']}@{config['host']}", f"{config['path']}{script}"]
    if config['fromuser'] and config['fromuser']!='':
        call_arr = ['sudo', 'ssh', '-u', f"{config['fromuser']}", f"{config['user']}@{config['host']}", f"{config['path']}{script}"]
    app.logger.info(str(call_arr))
    result = subprocess.call(call_arr)
    return {'result':result}

if __name__ == '__main__':

    app.logger.info('run app on 0.0.0.0:5000')
    app.run(host='0.0.0.0')
