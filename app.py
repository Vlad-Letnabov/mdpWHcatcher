from flask import Flask
import subprocess
import xml.etree.cElementTree as ET
import os
import logging

app = Flask(__name__)
#format = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
strfmt = '%(asctime)s %(thread)d %(clientip)s %(user)s %(name)s [%(levelname)s] %(funcName)s: %(message)s'
# строка формата времени
datefmt = '%Y-%m-%d %H:%M:%S'
# создаем форматтер
formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)


def readconfig():
    config=dict(host='localhost',user='noboby',path='/tmp',fromuser='')
    path =  os.path.abspath("config.xml") #'config.xml'
    logging.info(path)
    tree = ET.parse(path)
    root = tree.getroot()
    for key,value in config.items():
        try:
            node = root.find(f'./{key}')
            if node.text:
                config[key] = node.text
        except BaseException as exp:
            logging.error(str(exp))
            logging.error('check config')
    return config

config = readconfig()
logging.info(config)
@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/catchwh/<string:script>', methods=['GET'])
def catchwh(script):
    logging.info(script)
    call_arr = ['sudo', 'ssh', f"{config['user']}@{config['host']}", f"{config['path']}{script}"]
    if config['fromuser'] and config['fromuser']!='':
        call_arr = ['sudo', 'ssh', '-u', f"{config['fromuser']}", f"{config['user']}@{config['host']}", f"{config['path']}{script}"]
    logging.info(call_arr)
    result = subprocess.call(call_arr)
    return {'result':result}

if __name__ == '__main__':
    logging.info('run app on 0.0.0.0:5000')
    app.run(host='0.0.0.0')
