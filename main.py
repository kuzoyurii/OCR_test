import image_generator as IG
from image_generator import scoreboard_image as SI
from multiprocessing.connection import Listener
import os
import sys
import time
import threading
import glob
import json
from server_settings import *
import requests
import subprocess
import psutil


MAXIMUM_FRAMES = 999999999
python_path = str(sys.executable)
forced_list = ['HomeScoreHundreds', 'AwayScoreHundreds', 'HomeScoreOnes', 'HomeScoreTens', 'AwayScoreOnes',
               'AwayScoreTens', 'Period', 'MinutesTens', 'MinutesOnes', 'SecondsOnes', 'SecondsTens', 'HomeFouls',
               'AwayFouls', 'ShotClockTens', 'ShotClockOnes']


def set_clock(seconds=None, minutes=None, direction=None):
    global change_list, my_scoreboard, timer
    timer = 0
    if str(seconds):
        seconds = int(seconds)
        if seconds % 10 != my_scoreboard.areas['SecondsOnes'][0]:
            my_scoreboard.set_value('SecondsOnes', seconds % 10)
            change_list.append('SecondsOnes')
        if seconds // 10 != my_scoreboard.areas['SecondsTens'][0]:
            my_scoreboard.set_value('SecondsTens', seconds // 10)
            change_list.append('SecondsTens')
    if str(minutes):
        minutes = int(minutes)
        if minutes % 10 != my_scoreboard.areas['MinutesOnes'][0]:
            my_scoreboard.set_value('MinutesOnes', minutes % 10)
            change_list.append('MinutesOnes')
        if minutes // 10 != my_scoreboard.areas['MinutesTens'][0]:
            my_scoreboard.set_value('MinutesTens', minutes // 10)
            change_list.append('MinutesTens')
    if str(direction):
        my_scoreboard.clock_direction(direction)


def set_shotclock(seconds=None):
    global change_list, my_scoreboard, shotclock_timer
    if shotclock_enabled:
        shotclock_timer = 0
        if str(seconds):
            seconds = int(seconds)
            if seconds % 10 != my_scoreboard.areas['ShotClockOnes'][0]:
                my_scoreboard.set_value('ShotClockOnes', seconds % 10)
                change_list.append('ShotClockOnes')
            if seconds // 10 != my_scoreboard.areas['ShotClockTens'][0]:
                my_scoreboard.set_value('ShotClockTens', seconds // 10)
                change_list.append('ShotClockTens')


def shot_clock_tic():
    global my_scoreboard
    changed = []
    if shotclock_enabled:
        int_sec = (my_scoreboard.areas['ShotClockTens'][0] * 10) + my_scoreboard.areas['ShotClockOnes'][0]
        if int_sec == 0:
            reset_shotclock()
            return changed
        new_int_sec = int_sec - 1
        my_scoreboard.set_value('ShotClockOnes', new_int_sec % 10)
        changed.append('ShotClockOnes')
        if new_int_sec // 10 != my_scoreboard.areas['ShotClockTens'][0]:
            my_scoreboard.set_value('ShotClockTens', new_int_sec // 10)
            changed.append('ShotClockTens')
    return changed


def tic():
    global my_scoreboard
    changed = []
    int_sec = (my_scoreboard.areas['SecondsTens'][0] * 10) + my_scoreboard.areas['SecondsOnes'][0]
    int_min = (my_scoreboard.areas['MinutesTens'][0] * 10) + my_scoreboard.areas['MinutesOnes'][0]
    new_int_sec = int_sec + my_scoreboard.time_change
    new_int_min = int_min
    if new_int_sec > 59:
        new_int_sec = 0
        new_int_min = int_min + 1
    if new_int_sec < 0:
        new_int_min = int_min - 1
        new_int_sec = 59
    if (new_int_min > 99) or (new_int_min < 0):
        reset_clock()
        return changed
    my_scoreboard.set_value('SecondsOnes', new_int_sec % 10)
    changed.append('SecondsOnes')
    if new_int_sec // 10 != my_scoreboard.areas['SecondsTens'][0]:
        my_scoreboard.set_value('SecondsTens', new_int_sec // 10)
        changed.append('SecondsTens')
    else:
        return changed
    if new_int_min % 10 != my_scoreboard.areas['MinutesOnes'][0]:
        my_scoreboard.set_value('MinutesOnes', new_int_min % 10)
        changed.append('MinutesOnes')
    else:
        return changed
    if new_int_min // 10 != my_scoreboard.areas['MinutesTens'][0]:
        my_scoreboard.set_value('MinutesTens', new_int_min // 10)
        changed.append('MinutesTens')
    return changed


def run_render():
    global my_scoreboard, change_list, turn_off
    if my_scoreboard.debug:
        my_scoreboard.log('Change list: ' + str(change_list))
    rendered, log_list = SI.changes_in_image(my_scoreboard, change_list, cwd, frames)
    if rendered:
        change_list = []
        my_scoreboard.old_frame = my_scoreboard.frame
        my_scoreboard.frame = frames
    else:
        print('ERROR! Error in render!')
        my_scoreboard.log('ERROR! Error in render!')
    if my_scoreboard.debug:
        if log_list:
            my_scoreboard.log('scoreboard_image: ' + str(log_list))
        else:
            my_scoreboard.log('scoreboard_image: log is EMPTY')
    if turn_off:
        my_scoreboard.status = False
        turn_off = False


def send_quit_to_server():
    global listener
    try:
        URL = "http://" + server_ip + ":" + f_port_hardcoded + "/commands/quit"
        PARAMS = {
            "secret": SERVER_SECRET
        }
        r = requests.post(url=URL)
    except:
        print('error sending quit command to server')
    try:
        listener.close()
    except:
        print('error closing conn')


def get_frame_number():
    if 'my_scoreboard' in globals():
        try:
            return my_scoreboard.frame
        except:
            return -1
    return -1


def sb_is_active():
    if 'my_scoreboard' in globals():
        if my_scoreboard is not None:
            return True
    return False


def updater():
    global timer, shotclock_timer, frames, change_list
    frames = 0
    timer = 0
    shotclock_timer = 0
    while running_main:
        frames += 1
        if frames > max_frames:
            print('frame number exceeded max frames for event, exiting...')
            quitting()
            send_quit_to_server()
        time_start = time.time()
        if my_scoreboard.ticking and timer == 1:
            ticker()
            timer = 0
        if my_scoreboard.shotclock_ticking and shotclock_timer == 1:
            shotclock_ticker()
            shotclock_timer = 0
        change_list.extend(forced_list)
        if change_list: # and my_scoreboard.status:
            run_render()
        time_sec = time.time()
        if time_sec-time_start < refresh_time:
            time.sleep(refresh_time - (time_sec-time_start))
            if my_scoreboard.debug:
                my_scoreboard.log('slept ' + str(refresh_time-(time_sec-time_start)))
        else:
            if my_scoreboard.debug:
                my_scoreboard.log('! INSOMNIA !')
        if my_scoreboard.ticking:
            timer += refresh_time
        if my_scoreboard.shotclock_ticking:
            shotclock_timer += refresh_time


def ticker():
    global my_scoreboard, change_list
    if my_scoreboard.ticking:
        change_list.extend(tic())


def shotclock_ticker():
    global my_scoreboard, change_list
    if my_scoreboard.shotclock_ticking:
        change_list.extend(shot_clock_tic())


def init_scoreboard(id, font=0, debug=False, period=0, up=True):
    global my_scoreboard, max_frames, forced_list
    max_frames = MAXIMUM_FRAMES
    if debug:
        max_frames = MAXIMUM_FRAMES * 2
    forced_list = ['HomeScoreHundreds', 'AwayScoreHundreds', 'HomeScoreOnes', 'HomeScoreTens', 'AwayScoreOnes',
                   'AwayScoreTens', 'Period', 'MinutesTens', 'MinutesOnes', 'SecondsOnes', 'SecondsTens', 'HomeFouls',
                   'AwayFouls', 'ShotClockTens', 'ShotClockOnes']
    try:
        my_scoreboard = IG.Scoreboard(id, debug)
        my_scoreboard.init_scoreboard(cwd)
        print('!!!')
        my_scoreboard.period = int(period)
        if up:
            my_scoreboard.clock_direction('up')
        else:
            my_scoreboard.clock_direction('down')
        SI.create_assets(my_scoreboard, cwd, font)
    except Exception as e:
        print(str(e))
        print('SI ERROR, Check the init scoreboard_id and fonts exists. exiting...')
        quitting()
        send_quit_to_server()
        return None

    return my_scoreboard


def create_folders(folders):
    for folder in folders:
        try:
            if not os.path.exists(folder):
                os.makedirs(folder)
        except:
            print('unable to locate or create necessary folder(s), exiting... ')
            sys.exit(-1)


def remove_files(folder_list):
    for folder in folder_list:
        files = glob.glob('{}/*'.format(folder))
        for file in files:
            if os.path.isfile(file):
                try:
                    os.remove(file)
                except:
                    print('Error removing file...')


def setup_workplace():
    create_folders(['output', 'assets'])
    remove_files(['output', 'assets'])


def set_debug(sb_id):
    create_folders(['output/debug', 'output/debug/' + sb_id])
    remove_files(['output/debug/' + sb_id])


def on_off(state='on'):
    global my_scoreboard, change_list, turn_off
    if state.lower() == 'on':
        turn_off = False
        change_list = my_scoreboard.on()
        my_scoreboard.status = True
    else:
        change_list = my_scoreboard.off()
        turn_off = True


def start_clock():
    global my_scoreboard, timer
    my_scoreboard.ticking = True
    if shotclock_enabled:
        my_scoreboard.shotclock_ticking = True


def stop_clock():
    global my_scoreboard
    my_scoreboard.ticking = False
    if shotclock_enabled:
        my_scoreboard.shotclock_ticking = False


def reset_clock():
    global my_scoreboard
    print('reset_clock')
    print(my_scoreboard.period)
    if int(my_scoreboard.period) > 0:
        print('should reset period')
        reset_period()
    my_scoreboard.ticking = False
    if shotclock_enabled:
        set_shotclock(shot_clock)
        my_scoreboard.shotclock_ticking = False


def reset_period():
    global my_scoreboard, change_list
    my_scoreboard.set_value('Period', my_scoreboard.areas['Period'][0] + 1)
    print(my_scoreboard.areas['Period'][0])
    change_list.append('Period')
    set_clock(seconds='0', minutes=str(my_scoreboard.period), direction='')


def start_shotclock():
    global my_scoreboard, shotclock_timer
    my_scoreboard.shotclock_ticking = True


def stop_shotclock():
    global my_scoreboard
    my_scoreboard.shotclock_ticking = False


def reset_shotclock():
    global my_scoreboard
    set_shotclock(shot_clock)
    my_scoreboard.shotclock_ticking = False

def player_already_running():
    for p in psutil.process_iter():
        try:
            if 'python3' in str(p):
                return True
        except:
            continue
    return False


def start_player(zoom=1, top=True, debug_path='false'):
    #import subprocess
    if player_already_running():
        quitting(before_run=True)
    debug = player_setup['debug'] if 'debug' in player_setup else my_scoreboard.debug
    if debug:
        debug_path = player_setup['debug_path'] if 'debug_path' in player_setup else my_scoreboard.id
    frame = player_setup['frame'] if 'frame' in player_setup else 0 - my_scoreboard.frame
    zoom = player_setup['zoom'] if 'zoom' in player_setup else zoom
    top = player_setup['top'] if 'top' in player_setup else top
    player_path = os.getcwd() + '/player.py'
    #player_path = 'player.py'
    #player_path = 'player.exe'
    #print(str(frame))
    #player_path = r'C:\Users\udia.PIXELLOT\PycharmProjects\ocr_simulator\venv\Scripts\dist\player.exe'
    subprocess.Popen(['python3', str(player_path),str(frame),str(zoom),str(top),str(debug),str(refresh_time),str(debug_path)])
    # os.system('"{}" {} {} {} {} {} {} {}'.format(python_path, player_path, frame, zoom, top, debug, refresh_time, debug_path))


def setClock(command):
    direction = command['setClock']['direction'] if 'direction' in command['setClock'] else ''
    seconds = command['setClock']['seconds'] if 'seconds' in command['setClock'] else ''
    minutes = command['setClock']['minutes'] if 'minutes' in command['setClock'] else ''
    set_clock(seconds, minutes, direction)


def startClocks(command):
    direction = command['startClock']['direction'] if 'direction' in command['startClocks'] else ''
    seconds = command['startClock']['seconds'] if 'seconds' in command['startClocks'] else ''
    minutes = command['startClock']['minutes'] if 'minutes' in command['startClocks'] else ''
    scv = command['startClock']['shotclock'] if 'shotclock' in command['startClocks'] else ''
    if direction or seconds or minutes:
        set_clock(seconds, minutes, direction)
    start_clock()
    if scv:
        set_shotclock(scv)
        start_shotclock()


def startClock(command):
    direction = command['startClock']['direction'] if 'direction' in command['startClock'] else ''
    seconds = command['startClock']['seconds'] if 'seconds' in command['startClock'] else ''
    minutes = command['startClock']['minutes'] if 'minutes' in command['startClock'] else ''
    if direction or seconds or minutes:
        set_clock(seconds, minutes, direction)
    start_clock()


def setShotClock(command):
    seconds = command['setShotClock']['seconds'] if 'seconds' in command['setShotClock'] else ''
    set_shotclock(seconds)


def startShotClock(command):
    seconds = command['startShotClock']['seconds'] if 'seconds' in command['startShotClock'] else ''
    set_shotclock(seconds)
    start_shotclock()


def setTeamScore(command):
    global my_scoreboard, change_list
    homeScore = command['setTeamScore']['homeScore'] if 'homeScore' in command['setTeamScore'] else ''
    awayScore = command['setTeamScore']['awayScore'] if 'awayScore' in command['setTeamScore'] else ''
    if str(homeScore):
        change_list.extend(my_scoreboard.set_score('home', int(homeScore)))
    if str(awayScore):
        change_list.extend(my_scoreboard.set_score('away', int(awayScore)))


def setFouls(command):
    global my_scoreboard, change_list
    homeFouls = command['setFouls']['homeFouls'] if 'homeFouls' in command['setFouls'] else ""
    awayFouls = command['setFouls']['awayFouls'] if 'awayFouls' in command['setFouls'] else ""
    if str(homeFouls):
        if int(homeFouls) != my_scoreboard.areas['HomeFouls'][0]:
            my_scoreboard.set_value('HomeFouls', command['setFouls']['homeFouls'])
            change_list.append('HomeFouls')
    if str(awayFouls):
        if int(awayFouls) != my_scoreboard.areas['AwayFouls'][0]:
            my_scoreboard.set_value('AwayFouls', command['setFouls']['awayFouls'])
            change_list.append('AwayFouls')


def setPeriod(command):
    global my_scoreboard, change_list
    if command['setPeriod']['period'] != my_scoreboard.areas['Period'][0]:
        my_scoreboard.set_value('Period', command['setPeriod']['period'])
        change_list.append('Period')


def quitting(before_run=False):
    global to_run_player, running_main
    print('quitting player...')
    if before_run:
        with open(r'output/quit.command', 'w') as f:
            f.write('quit player')
        time.sleep(2)
        try:
            os.remove(r'output/quit.command')
        except:
            pass
        return 0
    try:
        if my_scoreboard.debug:
            print('writing scoreboard log to debug.txt ...')
            with open('debug.txt', 'w') as f:
                for item in my_scoreboard.log_file:
                    f.write("%s\n" % item)
    except:
        pass
    with open(r'output/quit.command', 'w') as f:
        f.write('quit player')
    to_run_player = False
    running_main = False
    time.sleep(2)
    return 0


def sendData():
    text_file = open("sb_data.txt", "w+")
    sb_data = json.dumps(my_scoreboard.areas)
    my_sb_data = my_scoreboard.get_data()
    print(my_sb_data)
    text_file.write(str(my_sb_data) + '\n' + str(sb_data))
    text_file.close()


def command_parser(message):
    global to_run_player, player_setup
    command = message
    if 'command' in command.keys():
        print('parse_special_command')
        for keys in command.values():
            for k in keys:
                if str(k).lower() == 'scoreboard':
                    on_off(command['command'][k])
                    break
                if str(k).lower() == 'player':
                    to_run_player = True
                    player_setup = command['command']['player']
                    break
                if str(k).lower() == 'quit':
                    quitting()
        return '200'
    else:
        print('parse_regular_command')
        if 'setClock' in command.keys():
            setClock(command)
        if 'startClock' in command.keys():
            startClock(command)
        if 'startClocks' in command.keys():
            startClocks(command)
        if 'stopClock' in command.keys():
            stop_clock()
        if 'setShotClock' in command.keys():
            setShotClock(command)
        if 'startShotClock' in command.keys():
            startShotClock(command)
        if 'stopShotClock' in command.keys():
            stop_shotclock()
        if 'setTeamScore' in command.keys():
            setTeamScore(command)
        if 'setFouls' in command.keys():
            setFouls(command)
        if 'setPeriod' in command.keys():
            setPeriod(command)
        if 'getData' in command.keys():
            sendData()
        return '200'


def start_listener(listen_port=5500):
    global my_scoreboard, server_ip, conn, listener
    server_ip = ''
    print('start listening')
    # try:
    #     address = ('localhost', int(listen_port))  # family is deduced to be 'AF_INET'
    #     listener = Listener(address, authkey=bytes(str('secret password').encode()))
    #     listener.close()
    # except:
    #     print('error closing socket')
    try:
        address = ('localhost', int(listen_port))  # family is deduced to be 'AF_INET'
        listener = Listener(address, authkey=bytes(str('secret password').encode()))
        conn = listener.accept()
        print('log: connection accepted from', listener.last_accepted)
        server_ip = listener.last_accepted[0]
        my_scoreboard.log(('log: connection accepted from ' + str(listener.last_accepted)))
    except Exception as e:
        print('failed to listen')
        try:
            listener.close()
            print('closing listener')
        except:
            print('error closing listener')
        print(str(e))
        try:
            quitting()
        except:
            pass
        return
    while running_main:
        api_message = conn.recv()
        print('Got API MESSAGE: ' + str(api_message))
        my_scoreboard.log('Got API MESSAGE: ' + str(api_message))
        command_parser(api_message)
    try:
        listener.close()
    except Exception as e:
        print(str(e) + '\nerror closing listener')


def init(scoreboard_id='basketball',debug=False, listen_port=5500, shotclock=True, period=0, up=True, font=0):
    global cwd, my_scoreboard, change_list, to_run_player, player_setup, running_main, refresh_time, shot_clock, \
        shotclock_enabled, turn_off, forced_list, listener
    turn_off = False
    running_main = True
    cwd = os.getcwd()
    to_run_player = False
    player_setup = {}
    setup_workplace()
    if debug:
        set_debug(scoreboard_id)
    shotclock_enabled = shotclock
    if shotclock_enabled:
        refresh_time = 0.5
    else:
        refresh_time = 1
    shot_clock = 24
    change_list = []
    try:
        my_scoreboard = init_scoreboard(scoreboard_id, font, debug, period, up)
    except:
        print('error init sb from main.py')
        my_scoreboard = None
        del globals()['my_scoreboard']
        return
    if my_scoreboard is not None:
        try:
            running_listener = threading.Thread(target=start_listener, args=(listen_port,))
            running_listener.start()
        except:
            print('error running listener from main.py')
            my_scoreboard = None
            del globals()['my_scoreboard']
            return
        try:
            running_updater = threading.Thread(target=updater)
            running_updater.start()
        except:
            print('error running updater from main.py')
            running_main = False
            my_scoreboard = None
            del globals()['my_scoreboard']
            return
        forced_list = my_scoreboard.get_forced()

    while running_main:
        time.sleep(1)
        if to_run_player:
            running_player = threading.Thread(target=start_player)
            running_player.start()
            to_run_player = False
    print('Exit main.py - Scoreboard Event is Over...')
    try:
        listener.close()
    except Exception as e:
        print(str(e) + '\nerror closing listener')
    time.sleep(2)
    try:
        del globals()['my_scoreboard']
        print('my_scoreboard var deleted')
    except:
        print('error removing my_scoreboard var')
    return 0


if __name__ == '__main__':
    #init()
    pass
