from flask import Flask,request
import subprocess
import xml.etree.cElementTree as ET
import os
import logging
from logging.handlers import RotatingFileHandler
import paramiko

strfmt = '%(asctime)s %(thread)d %(name)s [%(levelname)s] %(funcName)s: %(message)s'
logging.basicConfig(filename='wh.log', level=logging.DEBUG, format=strfmt)
handler = RotatingFileHandler('wh.log', maxBytes=1000000, backupCount=1)
handler.setLevel(logging.DEBUG)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())


app = Flask(__name__)
app.logger.addHandler(handler)


def readconfig():
    config=dict(host='localhost',user='noboby',path='/tmp',fromuser='',sudo='/usr/bin/sudo', port='22', sshkey='key')
    path =  os.path.abspath("config.xml") #'config.xml'
    print(path)
    app.logger.info(path)
    tree = ET.parse('config.xml')
    root = tree.getroot()
    for key,value in config.items():
        try:
            print(key)
            node = root.find(f'./{key}')
            if node.text:
                config[key] = node.text
            if key=='port' and (node.text=='' or node.text==None):
                config[key]=22
        except BaseException as exp:
            app.logger.error(str(exp))
            app.logger.error('check config')
    return config

config = readconfig()
app.logger.info(config)
ssh_key = paramiko.RSAKey.from_private_key_file(f"keys/{config['sshkey']}")


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

def check_errors(stdout,stderr):
    out = ''
    error = ''
    error_code =255
    len_out=0
    len_err=0
    if isinstance(stdout,int) or isinstance(stderr,int):
        return dict(result=error_code, error='Exec exception')
    for line in stdout:
        out+=line.strip('\n')
        len_out=1
    for line in stderr:
        error+=line.strip('\n')
        len_err=1
    if len_out>0:
        app.logger.info(f'OUT: {out}')
        if out.upper().rstrip()=='OK':
            error_code=0
            error=''
    if len_err>0:
        if 'No such file or directory' in error:
            error='Script error'

    return dict(result=error_code, error=error)

def call_script(script):
    app.logger.info(script)
    call_arr = []
    #call_arr = [{config['sudo']}, 'ssh', f"{config['user']}@{config['host']}", f"{config['path']}{script}"]
    #if config['fromuser'] and config['fromuser']!='':
    #    call_arr = ['/usr/bin/sudo', '-u', f"{config['fromuser']}", 'ssh', f"{config['user']}@{config['host']}", f"{config['path']}{script}"]
    app.logger.info(str(call_arr))
    #result = subprocess.call(call_arr)
    stdin, stdout, stderr = (555,555,555)
    app.logger.info(f"try to connect... hostname={config['host']}, username={config['user']}, port={config['port']}")
    try:
        ssh.connect(hostname=config['host'], username=config['user'], port=config['port'], pkey=ssh_key)
        app.logger.info(f"try exec command: {config['path']}{script}")
        stdin, stdout, stderr = ssh.exec_command(f"{config['path']}{script}")
    except paramiko.PasswordRequiredException as exp:
        app.logger.error(f'password required: {exp}')
    except paramiko.BadAuthenticationType as exp:
        app.logger.error(f'bad auth type: {exp}')
    except paramiko.BadHostKeyException as exp:
        app.logger.error(f'bad host key: {exp}')
    except paramiko.AuthenticationException as exp:
        app.logger.error(f'auth exception: {exp}')
    except paramiko.SSHException as exp:
        app.logger.error(f'core ssh exception: {exp}')
    except Exception as exp:
        app.logger.error(f'pure exception: {exp}')

    return check_errors(stdout,stderr) #{'result':stdout, 'error': stderr}

if __name__ == '__main__':

    app.logger.info('run app on 0.0.0.0:5000')
    app.run(host='0.0.0.0')
