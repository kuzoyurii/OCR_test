import requests
import datetime
import time

server_ipv4 = '127.0.0.1'
# Test all fields SB Event ##


def test_log(text):
    print(text)
    with open('test_sb.log', 'a+') as file:
        file.write(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S: " + text + '\n'))



def init():
    URL = "http://" + server_ipv4 + ":5000/init"
    PARAMS = {
        "scoreboard_id": "basketball",
        "shotclock": True,
        "debug": False,
        "listen_port": 5503
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str(datetime.datetime.now()) + ' init')


def set_qarter(qarter):
    URL = "http://" + server_ipv4 + ":5000/setPeriod"
    PARAMS = {
        "period": qarter
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} setPeriod {}'.format(str(datetime.datetime.now()),str(qarter))))
    time.sleep(5)


def startShotClock(maxtime=24):
    global shotclock
    URL = "http://" + server_ipv4 + ":5000/startShotClock"
    PARAMS = {
        "seconds": maxtime
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} startShotClock {}'.format(str(datetime.datetime.now()),str(maxtime))))
    shotclock = maxtime
    time.sleep(4.5)


def startClock(total_sec):
    min = int(total_sec / 240)
    URL = "http://" + server_ipv4 + ":5000/startClock"
    PARAMS = {
       "minutes": min,
       "seconds": 0,
       "direction": "down"
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} startClock {}:0'.format(str(datetime.datetime.now()),str(min))))
    time.sleep(4.5)


def setClock(min, sec):
    URL = "http://" + server_ipv4 + ":5000/startClock"
    PARAMS = {
       "minutes": min,
       "seconds": sec,
       "direction": "down"
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} setClock {}:{}'.format(str(datetime.datetime.now()),str(min),str(sec))))
    time.sleep(5)


def on():
    URL = "http://" + server_ipv4 + ":5000/commands/on"
    r = requests.post(url=URL)
    test_log(str(datetime.datetime.now()) + ' on')


def quit_sb():
    URL = "http://" + server_ipv4 + ":5000/commands/quit"
    r = requests.post(url=URL)
    test_log(str(datetime.datetime.now()) + ' QUIT')
    time.sleep(5)


def pause_clock(sec=5):
    URL = "http://" + server_ipv4 + ":5000/stopClock"
    r = requests.post(url=URL)
    test_log(str('{} pause Clock'.format(str(datetime.datetime.now()))))
    time.sleep(sec)


def resume_shotclock():
    URL = "http://" + server_ipv4 + ":5000/startShotClock"
    r = requests.post(url=URL)
    test_log(str('{} resume ShotClock'.format(str(datetime.datetime.now()))))
    time.sleep(5)


def resume_clock():
    URL = "http://" + server_ipv4 + ":5000/startClock"
    PARAMS = {
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} resume Clock'.format(str(datetime.datetime.now()))))
    time.sleep(4.5)


def setfoul(hf,gf):
    URL = "http://" + server_ipv4 + ":5000/setFouls"
    PARAMS = {
        "homeFouls": hf,
        "awayFouls": gf
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} setFouls {}-{}'.format(str(datetime.datetime.now()),str(hf),str(gf))))
    time.sleep(5)


def setscore(hs,gs):
    URL = "http://" + server_ipv4 + ":5000/setTeamScore"
    PARAMS = {
        "homeScore": hs,
        "awayScore": gs
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} setTeamScore {}-{}'.format(str(datetime.datetime.now()), str(hs), str(gs))))
    time.sleep(5)


def test_fouls():
    global hf, gf
    for t in range(9):
        hf +=1
        setfoul(hf, gf)
        gf += 1
        setfoul(hf, gf)


def test_pausing():
    pause_clock()
    resume_clock()
    resume_shotclock()


def test_score():
    global hs, gs
    hs += 1
    setscore(hs, gs)
    gs += 1
    setscore(hs, gs)
    for t in range(8):
        hs += 11
        setscore(hs, gs)
        gs += 11
        setscore(hs, gs)
    setscore(99, 99)


def test_quarters(quarters):
    global qrt
    for q in range(quarters):
        qrt += 1
        set_qarter(qrt)


def test_clocks():
    mn = 99
    sc = 59
    setClock(mn, sc)
    mn -= 1
    for c in range(9):
        setClock(mn, sc)
        mn -= 11
        sc -= 5
        pause_clock(2)
    startShotClock(24)
    time.sleep(30)
    pause_clock()
    time.sleep(10)


def run_main_loop():
    global shotclock, hs, hf, gs, gf, qrt
    hs = 0
    gs = 0
    hf = 0
    gf = 0
    qrt = 1
    total_time = 1500
    set_qarter(qrt)
    startClock(total_time)
    startShotClock()
    test_fouls()
    test_pausing()
    test_score()
    test_quarters(4)
    test_clocks()


def run_player():
    URL = "http://" + server_ipv4 + ":5000/commands/player"
    PARAMS = {
       "zoom": 3,
       "top": False,
       "shotclock": True
    }
    r = requests.post(url=URL, json=PARAMS)
    test_log(str('{} start Player'.format(str(datetime.datetime.now()))))


if __name__ == '__main__':
    init()
    time.sleep(5)
    run_player()
    on()
    time.sleep(120)
    run_main_loop()
    quit_sb()
    quit()

