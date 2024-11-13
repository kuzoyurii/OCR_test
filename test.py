import requests
import datetime
import time
import subprocess
import random


def WakeOnLan(ethernet_address):
    import struct, socket
    broadcast = '10.0.0.255'
    wol_port = 9
    ethernet_address = str(ethernet_address).replace('-',':')
    add_oct = ethernet_address.split(':')
    hwa = struct.pack('BBBBBB', int(add_oct[0], 16),
                      int(add_oct[1], 16),
                      int(add_oct[2], 16),
                      int(add_oct[3], 16),
                      int(add_oct[4], 16),
                      int(add_oct[5], 16))
    msg = bytes(str('\xff').encode()*6 + str(hwa).encode()*16)
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    soc.sendto(msg, (broadcast, wol_port))
    soc.close()
    time.sleep(180)


def test_log(text):
    print(text)
    with open('test.log', 'a+') as file:
        file.write(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S: " + text + '\n'))

def get_server_ipv4(server_pc_name):
    global subprocess
    subprocess = subprocess.Popen("ping -4 {}".format(server_pc_name), shell=True, stdout=subprocess.PIPE)
    subprocess_return = str(subprocess.stdout.read())
    print(subprocess_return)
    server_ipv4 = ''
    if 'unreachable' not in subprocess_return:
        server_ipv4 = str(subprocess_return.split(']')[0].split('[')[1])
        test_log(str('Found IPv4 address for {}: {}'.format(server_pc_name,server_ipv4)))
    print('server ipv4',server_ipv4)
    return server_ipv4


def get_ipv4(server_pc_name):
    server_ipv4 = ''
    try:
        server_ipv4 = get_server_ipv4(server_pc_name)
    except:
        server_ipv4 = ''
    if server_ipv4 != '':
        return server_ipv4
    print('no response from ' + str(server_ipv4 + ', trying to wake it up...'))
    WakeOnLan(servers_mac[server_pc_name])
    try:
        server_ipv4 = get_server_ipv4(server_pc_name)
    except:
        server_ipv4 = ''
    return server_ipv4


def init():
    URL = "http://" + server_ipv4 + ":5000/init"
    PARAMS = {
        "scoreboard_id": "basketball",
        "shotclock": True,
        "debug": True,
        "secret": "test_random_event",
        "listen_port": 5503
    }
    test_log(str(datetime.datetime.now()) + ' init')
    r = requests.post(url=URL, json=PARAMS)
    time.sleep(5)

def set_qarter(qarter, break_duration):
    if qarter > 1:
        time.sleep(break_duration)
    URL = "http://" + server_ipv4 + ":5000/setPeriod"
    PARAMS = {
        "period": qarter,
        "secret": "test_random_event"
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} setPeriod {}'.format(str(datetime.datetime.now()),str(qarter))))

def startShotClock(maxtime=24):
    global shotclock
    URL = "http://" + server_ipv4 + ":5000/startShotClock"
    PARAMS = {
        "seconds": maxtime,
        "secret": "test_random_event",
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} startShotClock'.format(str(datetime.datetime.now()))))
    shotclock = maxtime


def startClock(total_sec):
    min = int(total_sec / 240)
    URL = "http://" + server_ipv4 + ":5000/startClock"
    PARAMS = {
       "minutes": min,
       "seconds": 0,
       "secret": "test_random_event",
       "direction": "down"
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} startClock'.format(str(datetime.datetime.now()))))


def on():
    URL = "http://" + server_ipv4 + ":5000/commands/on"
    test_log(str(datetime.datetime.now()) + ' on')
    PARAMS = {
       "secret": "test_random_event"
    }
    r = requests.get(url=URL, json=PARAMS)
    time.sleep(5)

def quit_sb():
    URL = "http://" + server_ipv4 + ":5000/commands/quit"
    PARAMS = {
       "secret": "test_random_event"
    }
    r = requests.get(url=URL, json=PARAMS)
    test_log(str(datetime.datetime.now()) + ' QUIT')

def pause_clock():
    URL = "http://" + server_ipv4 + ":5000/stopClock"
    r = requests.get(url=URL)
    test_log(str('{} pause Clock'.format(str(datetime.datetime.now()))))

def resume_shotclock():
    URL = "http://" + server_ipv4 + ":5000/startShotClock"
    PARAMS = {
        "secret": "test_random_event"
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} resume ShotClock'.format(str(datetime.datetime.now()))))


def resume_clock():
    URL = "http://" + server_ipv4 + ":5000/startClock"
    PARAMS = {
        "secret": "test_random_event"
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} resume Clock'.format(str(datetime.datetime.now()))))


def shotclock_timed_out():
    global shotclock
    pause_clock()
    time.sleep(random.randint(3, 6))
    resume_clock()
    startShotClock()

def avera(hf,gf):
    ## AVERA ##
    pause_clock()
    time.sleep(random.randint(3, 6))

    URL = "http://" + server_ipv4 + ":5000/setFouls"
    PARAMS = {
        "secret": "test_random_event",
        "homeFouls": hf,
        "awayFouls": gf
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} setFouls {}-{}'.format(str(datetime.datetime.now()),str(hf),str(gf))))

    resume_clock()
    resume_shotclock()



def run_main_loop():
    global shotclock
    shoclock=24
    half_sec = False
    full_sec = False
    hs = 0
    gs = 0
    hf = 0
    gf = 0
    qrt = 1
    total_time = 1200
    total_time_left = 1200
    qrt_time = int(total_time / 4)
    qrt_time_left = int(total_time / 4)
    set_qarter(qrt, 0)
    for q in range(4):
        set_qarter(q+1, 0)
        startClock(total_time)
        startShotClock()
        for sec in range(qrt_time):
            time.sleep(1)
            shotclock -= 1
            qrt_time_left -= 1
            total_time_left -= 1
            if total_time_left == 0:
                return
            if qrt_time_left == 0:
                break
            if shotclock == 0:
                shotclock_timed_out()
                continue
            rand_chance = random.randint(0, shotclock+1)
            if rand_chance != 0:
                continue
            rand_chance = random.randint(0, 25)
            if 0 <= rand_chance <= 5:
                print('avera')
                team_foul = random.choice(['hf', 'gf'])
                if team_foul == 'hf':
                    hf += 1
                else:
                    gf += 1
                avera(hf,gf)
                continue
            if 5 <= rand_chance <= 15:
                print('hatifa')
                shotclock = 24
                startShotClock()
                continue
            if 15 <= rand_chance <= 25:
                print('sal')
                ## SAL ##
                team_scored = random.choice(['hs', 'gs'])
                scored = random.randint(1, 3)
                if team_scored == 'hs':
                    hs += scored
                else:
                    gs += scored
                URL = "http://" + server_ipv4 + ":5000/setTeamScore"
                PARAMS = {
                    "secret": "test_random_event",
                    "homeScore": hs,
                    "awayScore": gs
                }
                test_log(str('{} setTeamScore {}-{}'.format(str(datetime.datetime.now()), str(hs), str(gs))))
                r = requests.post(url=URL, json=PARAMS)
                pause_clock()
                time.sleep(random.randint(3,6))
                resume_clock()
                startShotClock()



if __name__ == '__main__':
    servers_mac = {}
    server_pc_name = 'PXL-LOT1'
    servers_mac[server_pc_name]='AA-BB-CC-DD-EE-FF'

    server_ipv4 = get_ipv4(server_pc_name)

    if server_ipv4 == '':
        print('can not find server ' + server_pc_name + ' ipv4 or server is still down, aborting...')
        quit()
    try:
        init()
    except:
        print('Found IP, but Server might be down, exiting...')
        quit()
    on()
    run_main_loop()
    set_qarter(5,30)
    quit_sb()
    quit()

