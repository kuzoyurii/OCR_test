from flask import Flask, request, render_template
from flask_expects_json import expects_json
import main
import os
import sys
import ctypes
from multiprocessing.connection import Client
from multiprocessing import freeze_support
import threading
from schemas import *
from server_settings import *
import datetime
import subprocess
import time
from server_messages import *
import glob
from shutil import copyfile

import multiprocessing
# multiprocessing.freeze_support()
# freeze_support()

SERVER_VER = 'OCRSIM_Beta-0.96'


def server_log(text):
    with open('server.log', 'a+') as file:
        file.write(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S: " + text + '\n'))


shotclock_event = False
server_log('#' * 100 + '\n' + 'Server.py Started')
template_folder = os.getcwd() + '/templates'
static_folder = os.getcwd() + '/static'
ocr_app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)


def ip_to_user(str_ip):
    user_name = str(str_ip)
    try:
        subprocess_var = subprocess.Popen("nslookup {}".format(user_name), shell=True, stdout=subprocess.PIPE)
        subprocess_return = str(subprocess_var.stdout.read())
        if 'Name:' in subprocess_return:
            return_list = subprocess_return.split()
            user_nslookup = return_list[3].split('/r')
            user_name += (' ' + user_nslookup[0])
    except Exception as e:
        server_log(f'Exception: unable to resolve ip address {user_name}')
    return user_name


def validate_secret(req, shutdown=False, quit=False):
    if not secret and not shutdown:
        return True
    if shutdown:
        test_str_secret = SERVER_SECRET
        test_secret = 'str'
    else:
        test_str_secret = str_secret
        test_secret = secret
    if test_secret == 'str':
        try:
            cont = req.json
            if (cont['secret'] == test_str_secret) or (quit and cont['secret'] == SERVER_SECRET):
                return True
        except:
            return False
    if test_secret == 'ip':
        try:
            if (str(request.environ['REMOTE_ADDR']) == test_str_secret) or (quit and cont['secret'] == SERVER_SECRET):
                return True
        except:
            return False
    return False


def shutdown_server(restart_server=False):
    if restart_server:
        subprocess.Popen(['python3', 'server.py'])
    server_log('shutdown_server')
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def main_init(sb_id, debug, listen_port=main_port, shotclock=shotclock_event, font=0, period=0, up=True):
    server_log('main_init, scoreboard={} debug={}, listen_port={}, shotclock={}, font={}, period={}, up={}'.format(str(sb_id),
                                                                                                 str(listen_port),
                                                                                                 str(debug),
                                                                                                 str(shotclock),
                                                                                                 str(up),
                                                                                                 str(period),
                                                                                                 str(font)))
    main.init(scoreboard_id=sb_id, debug=debug, listen_port=listen_port, shotclock=shotclock, font=font,
              period=period, up=up)


@ocr_app.route('/', methods=['GET'])
def home():
    if initialized:
        try:
            cwd = os.getcwd().replace("templates","")
            files_list = glob.glob(f'{cwd}/output/*.png')
            latest_image = max(files_list, key=os.path.getctime)
            copyfile(latest_image, 'static/latest.png')
            print('latest')
            return render_template('isb.html', sb_image = 'static/latest.png?' + str(datetime.datetime.now().timestamp()).split(".")[0])
        except:
            return render_template('isb.html', sb_image='static/sb.png')
    else:
        return render_template('isb.html', sb_image='static/sb.png')


@ocr_app.route('/controller', methods=['GET'])
def controller():
    return render_template('controller.html')


@ocr_app.route('/init', methods=['POST'])
@expects_json(schema['init'])
def init_scoreboard(scoreboard_id='basketball', debug=debug_hardcoded, listen_port=main_port, shotclock_def=False,
                    sb_font=0, up=True, period=0):
    global conn, initialized, player_is_on, state, shotclock_event, secret, str_secret
    server_log('init: {}'.format(str(request.json)))
    if not initialized and not main.sb_is_active():
        try:
            content = request.json
            secret = content['secret'] if 'secret' in content.keys() else ''
            if secret:
                if str(secret.lower()) == 'ip':
                    str_secret = str(request.environ['REMOTE_ADDR'])
                    secret = 'ip'
                else:
                    str_secret = str(secret)
                    secret = 'str'
            sb_init['user'] = ip_to_user(str(request.environ['REMOTE_ADDR']))
            sb_init['note'] = content['note'] if 'note' in content.keys() else ''
            sb_init['date'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            scoreboard_id = content['scoreboard_id'] if 'scoreboard_id' in content.keys() else scoreboard_id
            debug = content['debug'] if 'debug' in content.keys() else debug
            listen_port = content['listen_port'] if 'listen_port' in content.keys() else listen_port
            shotclock = content['shotclock'] if 'shotclock' in content.keys() else shotclock_def
            font = content['font'] if 'font' in content.keys() else sb_font
            up = content['up'] if 'up' in content.keys() else up
            period = content['period'] if 'period' in content.keys() else period
            shotclock_event = True if str(shotclock).lower() == 'true' else False
            player_is_on = False
            state = False
            try:
                running_main_init = threading.Thread(target=main_init,
                                                     args=(scoreboard_id, debug, listen_port, shotclock, font,
                                                           period, up))
                running_main_init.start()
            except:
                print('error running_main init')
                initialized = False
                return error_msg['scoreboard']['init']['409']
            try:
                address = ('localhost', listen_port)
                time.sleep(1)
                conn = Client(address, authkey=bytes(str('secret password').encode()))
                time.sleep(5)
                # initialized = True
            except Exception as e:
                print('error open multiprocessing Client')
                print(str(e))
                initialized = False
                return error_msg['scoreboard']['init']['409']
        except:
            initialized = False
            server_log('return: {}'.format(error_msg['scoreboard']['init']['409']))
            return error_msg['scoreboard']['init']['409']
        try:
            time.sleep(5)
            if main.sb_is_active():
                initialized = True
                server_log('return: {}'.format('200 scoreboard initialized'))
                return '200 scoreboard initialized'
            else:
                initialized = False
        except:
            return error_msg['scoreboard']['init']['409']
    if initialized and main.sb_is_active():
        server_log('return: {}'.format(error_msg['scoreboard']['init']['400']))
        return '{}\ndate:{}\nuser:{}\nnote:{}'.format(error_msg['scoreboard']['init']['400'], str(sb_init['date']),
                                                      str(sb_init['user']), str(sb_init['note']))
    return error_msg['scoreboard']['init']['409']


@ocr_app.route('/startClock', methods=['POST'])
@expects_json(schema['startClock'])
def start_clock():
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request):
                return error_msg['secret']['error']
        except:
            server_log(error_msg['secret']['json'])
            return error_msg['secret']['json']
    server_log('startClock: {}'.format(str(request.json)))
    if state != 'on':
        server_log('return: {}'.format(error_msg['scoreboard']['init']['409']))
        return error_msg['scoreboard']['init']['409']
    content = {'startClock': {}} if request.json is None else {'startClock': request.json}
    conn.send(content)
    server_log('return: {}'.format('200 startClock'))
    return '200 startClock'


@ocr_app.route('/startClocks', methods=['POST'])
@expects_json(schema['startClocks'])
def start_clocks():
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request):
                return error_msg['secret']['error']
        except:
            server_log(error_msg['secret']['json'])
            return error_msg['secret']['json']
    server_log('startClocks: {}'.format(str(request.json)))
    if state != 'on':
        server_log('return: {}'.format(error_msg['scoreboard']['init']['409']))
        return error_msg['scoreboard']['init']['409']
    content = {'startClock': {}} if request.json is None else {'startClock': request.json}
    conn.send(content)
    server_log('return: {}'.format('200 startClock'))
    return '200 startClocks'


@ocr_app.route('/setClock', methods=['POST'])
@expects_json(schema['startClock'])
def set_clock():
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request):
                return error_msg['secret']['error']
        except:
            server_log(error_msg['secret']['json'])
            return error_msg['secret']['json']
    server_log('setClock: {}'.format(str(request.json)))
    content = request.json
    conn.send({'setClock': content})
    server_log('return: {}'.format('200 setClock'))
    return '200 setClock'


@ocr_app.route('/stopClock', methods=['POST'])
def stop_clock():
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request):
                return error_msg['secret']['error']
        except:
            server_log(error_msg['secret']['json'])
            return error_msg['secret']['json']
    server_log('stopClock')
    conn.send({'stopClock': {}})
    server_log('return: {}'.format('200 stopClock'))
    return '200 stopClock'


@ocr_app.route('/setTeamScore', methods=['POST'])
@expects_json(schema['setTeamScore'])
def set_score():
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request):
                return error_msg['secret']['error']
        except:
            server_log(error_msg['secret']['json'])
            return error_msg['secret']['json']
    server_log('setTeamScore: {}'.format(str(request.json)))
    content = request.json
    conn.send({'setTeamScore': content})
    server_log('return: {}'.format('200 setTeamScore'))
    return '200 setTeamScore'


@ocr_app.route('/setFouls', methods=['POST'])
@expects_json(schema['setFouls'])
def setFouls():
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request):
                return error_msg['secret']['error']
        except:
            server_log(error_msg['secret']['json'])
            return error_msg['secret']['json']
    server_log('setFouls: {}'.format(str(request.json)))
    content = request.json
    conn.send({'setFouls': content})
    server_log('return: {}'.format('200 setFouls'))
    return '200 setFouls'


@ocr_app.route('/setPeriod', methods=['POST'])
@expects_json(schema['setPeriod'])
def set_period():
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request):
                return error_msg['secret']['error']
        except:
            server_log(error_msg['secret']['json'])
            return error_msg['secret']['json']
    server_log('setPeriod: {}'.format(str(request.json)))
    content = request.json
    conn.send({'setPeriod': content})
    server_log('return: {}'.format('200 setPeriod'))
    return '200 setPeriod'


@ocr_app.route('/startShotClock', methods=['POST'])
@expects_json(schema['startShotClock'])
def start_shotclock():
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request):
                return error_msg['secret']['error']
        except:
            server_log(error_msg['secret']['json'])
            return error_msg['secret']['json']
    server_log('startShotClock: {}'.format(str(request.json)))
    if state != 'on':
        server_log('return: {}'.format(error_msg['scoreboard']['init']['409']))
        return error_msg['scoreboard']['init']['409']
    if not shotclock_event:
        server_log('return: {}'.format(error_msg['shotclock']['init']))
        return error_msg['shotclock']['init']
    content = {'startShotClock': {}} if request.json is None else {'startShotClock': request.json}
    conn.send(content)
    server_log('return: {}'.format('200 startShotClock'))
    return '200 startShotClock'


@ocr_app.route('/setShotClock', methods=['POST'])
@expects_json(schema['setShotClock'])
def set_shotclock():
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request):
                return error_msg['secret']['error']
        except:
            server_log(error_msg['secret']['json'])
            return error_msg['secret']['json']
    server_log('setShotClock: {}'.format(str(request.json)))
    if not shotclock_event:
        server_log('return: {}'.format(error_msg['shotclock']['init']))
        return error_msg['shotclock']['init']
    content = request.json
    conn.send({'setShotClock': content})
    server_log('return: {}'.format('200 setShotClock'))
    return '200 setShotClock'


@ocr_app.route('/stopShotClock', methods=['POST'])
def stop_shotclock():
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request):
                return error_msg['secret']['error']
        except:
            server_log(error_msg['secret']['json'])
            return error_msg['secret']['json']
    server_log('stopShotClock')
    if not shotclock_event:
        server_log('return: {}'.format(error_msg['shotclock']['init']))
        return error_msg['shotclock']['init']
    conn.send({'stopShotClock': {}})
    server_log('return: {}'.format('200 stopShotClock'))
    return '200 stopShotClock'


@ocr_app.route('/getData', methods=['GET'])
def getData():
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    conn.send({'getData': {}})
    time.sleep(2)
    try:
        with open('sb_data.txt', 'r') as file:
            sb_data = file.read().replace('\n', '')
        server_log('return: {}'.format(str(sb_data)))
        return str(sb_data)
    except:
        server_log('400 error getting scoreboard data')
        return '400 error getting scoreboard data'


@ocr_app.route('/getStatus', methods=['GET'])
def getStatus():
    return f'Version: {SERVER_VER}\nInit: {str(main.sb_is_active())}\nFrame: {str(main.get_frame_number())}\n' \
           f'Player: {str(main.player_already_running())}'


@ocr_app.route('/commands/on', methods=['POST'])
def update_state_on():
    global state
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request):
                return error_msg['secret']['error']
        except:
            server_log(error_msg['secret']['json'])
            return error_msg['secret']['json']
    try:
        server_log('/commands/on')
        if state == 'on':
            server_log('return: {}'.format('409 scoreboard already on'))
            return '409 scoreboard already on'
        state = 'on'
        content = {'command': {'scoreboard': state}}
        conn.send(content)
        server_log('return: {}'.format('200 scoreboard on'))
        return '200 scoreboard on'
    except:
        server_log('400 init error')
        return '400 init error'


@ocr_app.route('/commands/off', methods=['POST'])
def update_state_off():
    global state
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request):
                return error_msg['secret']['error']
        except:
            server_log(error_msg['secret']['json'])
            return error_msg['secret']['json']
    server_log('/commands/off')
    if state == 'off':
        server_log('return: {}'.format('409 scoreboard already off'))
        return '409 scoreboard already off'
    state = 'off'
    content = {'command': {'scoreboard': state}}
    conn.send(content)
    server_log('return: {}'.format('200 scoreboard off'))
    return '200 scoreboard off'


@ocr_app.route('/commands/player', methods=['POST'])
@expects_json(schema['player'])
def run_ocr_player(frame=0, zoom=2):
    global player_is_on
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    server_log('/commands/player: {}'.format(str(request.json)))
    if initialized:
        content = {} if request.json is None else request.json
        conn.send({'command': {'player': content}})
        player_is_on = True
        server_log('return: {}'.format('200 running player'))
        return '200 running player'
    server_log('return: {}'.format(error_msg['scoreboard']['400']))
    return error_msg['scoreboard']['400']


@ocr_app.route('/commands/export', methods=['POST'])
@expects_json(schema['export'])
def export_video():
    try:
        if not validate_secret(request, shutdown=True):
            return error_msg['secret']['error']
    except:
        return error_msg['secret']['json']
    server_log('/commands/export')
    server_log('return: {}'.format('exporting frames to video...'))
    try:
        if "shotclock" not in request.json:
            fps = 1
        else:
            fps = 2 if request.json['shotclock'] else 1
        subprocess.Popen(['python3', 'scoreboards/sb_to_vid.py', str(request.json['scoreboard_id']), str(fps)])
        return '200 exporting video...'
    except:
        return '400 exporting video failed'



@ocr_app.route('/commands/quit', methods=['POST'])
def quit():
    global initialized, debug, player_is_on, state, secret
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    if secret:
        try:
            if not validate_secret(request, quit=True):
                return error_msg['secret']['error']
        except:
            return error_msg['secret']['json']
    server_log('/commands/quit')
    if initialized and main.sb_is_active():
        content = {}
        conn.send({'command': {'quit': content}})
        initialized = False
        debug = True
        player_is_on = False
        state = False
        secret = ''
        sb_init['user'] = '0.0.0.0'
        sb_init['note'] = ''
        sb_init['date'] = 'unknown'
        server_log('return: {}'.format('200 quit'))
        try:
            if 'my_scoreboard' in globals():
                del globals()['my_scoreboard']
                print('my_scoreboard deleted')
            else:
                print('my_scoreboard not in globals')
        except:
            print('unable to delete my_scoreboard')
        return '200 quit'
    else:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']


@ocr_app.route('/commands/secretoverride', methods=['POST'])
def secretoverride():
    global secret, str_secret
    if not initialized:
        server_log('return: {}'.format(error_msg['scoreboard']['400']))
        return error_msg['scoreboard']['400']
    try:
        if not validate_secret(request):
            if not validate_secret(request, shutdown=True):
                return error_msg['secret']['error']
    except:
        return error_msg['secret']['json']
    server_log('/commands/secretoverride')
    try:
        str_secret = request.json['new_secret']
        secret = 'str'
    except:
        str_secret = ''
        secret = ''
    server_log('return: {}'.format('200 Secret Override...'))
    return 'secret reset'


@ocr_app.route('/commands/shutdown', methods=['POST'])
def shutdown():
    global server_runs
    try:
        if not validate_secret(request, shutdown=True):
            return error_msg['secret']['error']
    except:
        return error_msg['secret']['json']
    server_log('/commands/shutdown')
    shutdown_server()
    server_log('return: {}'.format('200 Server shutting down...'))
    server_runs = False
    return '200 Server shutting down...'


@ocr_app.route('/commands/restartServer', methods=['POST'])
def restartServer():
    global server_runs
    try:
        if not validate_secret(request, shutdown=True):
            return error_msg['secret']['error']
    except:
        return error_msg['secret']['json']
    server_log('/commands/restartServer')
    shutdown_server(restart_server=True)
    server_log('return: {}'.format('200 Server shutting down...'))
    server_runs = False
    return '200 Server shutting down...'


if __name__ == '__main__':
    #ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
    initialized = False
    player_is_on = False
    shotclock_event = False
    sb_init = {}
    sb_init['user'] = '0.0.0.0'
    sb_init['note'] = ''
    sb_init['date'] = 'unknown'
    state = 'off'
    secret = ''
    str_secret = ''
    ocr_app.run(host=f_host_hardcoded, port=f_port_hardcoded, threaded=True)
    server_runs = True
    # set back log out to normal
    # ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
