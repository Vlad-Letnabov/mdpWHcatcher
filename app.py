from flask import Flask, request, make_response
import logging
from logging.handlers import RotatingFileHandler
import paramiko
from config import Config
import requests
import os

BASEPATH = os.path.abspath(os.path.dirname(__file__))
print('BASE', BASEPATH)

def check_dir(dir):
    print('check_dir:', dir)
    if not dir:
        return False
    if isinstance(dir, list):
        print('is list', dir)
        result = False
        for item in dir:
            result = check_dir(item)
            if not result:
                break
        return result
    elif isinstance(dir, str):
        print('is string', dir)
        dir = ''.join([BASEPATH,'/', dir])
        try:
            if not os.path.exists(dir):
                os.mkdir(dir)
        except BaseException as exp:
            print('error create file:', exp)
            return False
        return True
    else:
        return False


dirs = ['config', 'keys', 'logs']
check_dir(dirs)
strfmt = '%(asctime)s %(thread)d %(name)s [%(levelname)s] %(funcName)s: %(message)s'
logging.basicConfig(filename=f'{BASEPATH}/logs/wh.log', level=logging.DEBUG, format=strfmt)
handler = RotatingFileHandler(f'{BASEPATH}/logs/wh.log', maxBytes=10000000, backupCount=1)
handler.setLevel(logging.DEBUG)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())

app = Flask(__name__)
app.logger.addHandler(handler)


def readconfig():
    config = dict(host='localhost', user='noboby', path='/tmp', fromuser='', sudo='/usr/bin/sudo', port='22',
                  sshkey='key')
    config = Config(BASEPATH).get_config()
    if not config['port']:
        config['port'] = 22
    return config


config = readconfig()
app.logger.info(config)
ssh_key = paramiko.RSAKey.from_private_key_file(f"{BASEPATH}/keys/{config['sshkey']}")


@app.route('/')
def hello_world():
    app.logger.info('hello_world page')
    return 'Hello World!'

def create_ticket(data):
    '''
    :param data:
    :return:
    POST /api/v1/tickets

    {
      "title": "Help me!",
      "group": "Users",
      "customer": "email_of_existing_customer@example.com",
      "article": {
        "subject": "some subject",
        "body": "some message",
        "type": "note",
        "internal": false
      },
      "note": "some note",
      ...
    }

    '''
    if data['state'].lower() != 'alerting':
        return False
    query = f"{Config().get_url(config)}api/v1/tickets"

    create_json = {
        "title": data['title'][:40],
        "group": "Users",
        "customer": config['zammad']['customer_email'],
        "state_id": 1,
        "article": {
            "subject": data['title'][:40],
            "body": data['message'],
            "type": "note",
            "internal": False,
            "sender": "Customer",
        },
        "note": data['message']}
    print('URL:', query)
    print(create_json)
    # Authorization: Token token=
    headers = {
        'Authorization': f"Token token={config['zammad']['token']}"
    }
    print(headers)
    exception = False
    try:
        responce = requests.post(query, headers=headers, json=create_json)
        app.logger.info(f'result create ticket: {responce.status_code}')
        '''try:
            print( responce.status_code)
            if responce.status_code == 201:
                if isinstance(responce.json(), dict):
                    ticket = responce.json()
                    print(ticket)
                    return dict(id=ticket['id'],
                                number=ticket['number'],
                                title=ticket['title'],
                                tmplbeeline=ticket['tmpbeeline'],
                                tmplmegafon=ticket['tmplmegafone'])
        except BaseException as exp:
            print('Error create user: ', exp)
            logging.error('Error create user: ' + str(exp))'''
        text = ''
        if responce.status_code >= 400:
            text = f'<h2>{responce.status_code} Error</h2>'
    except ConnectionError as exp:
        app.logger.error(f'Connection error: {exp}')
        return {'message': '502 Server Connection Error', 'code': 502}
    except TimeoutError as exp:
        app.logger.error(f'Timeout error: {exp}')
        return {'message': '408 Request Timeout Error', 'code': 408}
    except request.ro as exp:
        app.logger.error(f'BaseException error: {exp}')
        return {'message': '500 Server  Error', 'code': 500}

    return {'message': text, 'code': responce.status_code}


@app.route('/catchwh/<string:script>', methods=['GET'])
def catchwhget(script):
    app.logger.info(script)
    return call_script(script)


@app.route('/catchwh/', methods=['POST', 'GET'])
def catchwh():
    app.logger.info(f"method: {request.method}")
    result = dict()
    if request.method == 'POST':
        script = None
        data = None
        if request.is_json:
            data = request.get_json()
            app.logger.info(str(data))
            if 'tags' in data:
                if 'script' in data['tags']:
                    script = data['tags']['script']
        else:
            script = request.form.get('script')
            data = request.form.to_dict()
        if script:
            app.logger.info(f"get via POST: {script}")
            result = call_script(script)
        else:
            result = create_ticket(data)

    else:
        script = request.args.get('script')
        app.logger.info(f"args: {request.args}, {script}")
        if script:
            app.logger.info(f"get via GET: {script}")
            result = call_script(script)

    response = make_response(result['message'], int(result['code']))
    response.headers["Content-Type"] = "application/json"
    return response


def check_errors(stdout, stderr):
    out = ''
    error = ''
    error_code = 500
    len_out = 0
    len_err = 0
    if isinstance(stdout, int) or isinstance(stderr, int):
        return dict(result=error_code, error='Exec exception')
    for line in stdout:
        out += line.strip('\n')
        len_out = 1
    for line in stderr:
        error += line.strip('\n')
        len_err = 1
    if len_out > 0:
        app.logger.info(f'OUT: {out}')
        if out.upper().rstrip() == 'OK':
            error_code = 200
            error = 'OK'
    if len_err > 0:
        if 'No such file or directory' in error:
            error = 'Script error'

    return dict(code=error_code, message=error)


def call_script(script):
    app.logger.info(script)
    call_arr = []
    # call_arr = [{config['sudo']}, 'ssh', f"{config['user']}@{config['host']}", f"{config['path']}{script}"]
    # if config['fromuser'] and config['fromuser']!='':
    #    call_arr = ['/usr/bin/sudo', '-u', f"{config['fromuser']}", 'ssh', f"{config['user']}@{config['host']}", f"{config['path']}{script}"]
    app.logger.info(str(call_arr))
    # result = subprocess.call(call_arr)
    stdin, stdout, stderr = (555, 555, 555)
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

    return check_errors(stdout, stderr)  # {'result':stdout, 'error': stderr}


if __name__ == '__main__':
    app.logger.info('run app on 0.0.0.0:5000')
    app.run(host='0.0.0.0')
