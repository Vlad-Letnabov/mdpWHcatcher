from flask import Flask
import subprocess
import xml.etree.cElementTree as ET
import os

app = Flask(__name__)

def readconfig():
    config=dict(host='localhost',user='noboby',path='/tmp',fromuser='')
    path =  os.path.abspath("config.xml") #'config.xml'
    print(path)
    tree = ET.parse(path)
    root = tree.getroot()
    for key,value in config.items():
        try:
            node = root.find(f'./{key}')
            if node.text:
                config[key] = node.text
        except BaseException as exp:
            print('err:', str(exp))
            print('check config')
    return config

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/catchwh/<string:script>', methods=['GET'])
def get_user(script):
    print(script)
    config = readconfig()
    print(config)
    call_arr = ['sudo', 'ssh', f"{config['user']}@{config['host']}", f"{config['path']}{script}"]
    if config['fromuser'] and config['fromuser']!='':
        call_arr = ['sudo', 'ssh', '-u', f"{config['fromuser']}", f"{config['user']}@{config['host']}", f"{config['path']}{script}"]
    print(call_arr)
    result = subprocess.call(call_arr)
    return {'result':result}

if __name__ == '__main__':
    app.run(host='0.0.0.0')
