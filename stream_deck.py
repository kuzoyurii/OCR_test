import json

import requests
import time
import os
import ast

#import pyautogui,time


server_ipv4 = '127.0.0.1'
paused = False
clockstarted = False
quitting = False
hs = 0
gs = 0
hf = 0
gf = 0
qrt = 0
os.system('mode con: cols=15 lines=10')


def alt_tab():
    pyautogui.keyDown('alt')
    time.sleep(.2)
    pyautogui.press('tab')
    time.sleep(.2)
    pyautogui.keyUp('alt')


def init():
    URL = "http://" + server_ipv4 + ":5000/init"
    PARAMS = {
        "scoreboard_id": "basketball",
        "shotclock": True,
        "debug": False,
        "listen_port": 5503
    }
    r = requests.post(url=URL, json=PARAMS)


def set_qarter(qarter):
    URL = "http://" + server_ipv4 + ":5000/setPeriod"
    PARAMS = {
        "period": qarter
    }
    r = requests.post(url=URL, json=PARAMS)


def startShotClock(maxtime=24):
    global shotclock
    URL = "http://" + server_ipv4 + ":5000/startShotClock"
    PARAMS = {
        "seconds": maxtime
    }
    r = requests.post(url=URL, json=PARAMS)


def startClock(minutes):
    global paused, clockstarted
    URL = "http://" + server_ipv4 + ":5000/startClock"
    PARAMS = {
       "minutes": minutes,
       "seconds": 0,
       "direction": "down"
    }
    r = requests.post(url=URL, json=PARAMS)
    paused = False
    clockstarted = True


def setClock(min, sec):
    URL = "http://" + server_ipv4 + ":5000/startClock"
    PARAMS = {
       "minutes": min,
       "seconds": sec,
       "direction": "down"
    }
    r = requests.post(url=URL, json=PARAMS)


def on():
    URL = "http://" + server_ipv4 + ":5000/commands/on"
    r = requests.post(url=URL)


def quit_sb():
    URL = "http://" + server_ipv4 + ":5000/commands/quit"
    r = requests.post(url=URL)


def pause_clock():
    global paused
    URL = "http://" + server_ipv4 + ":5000/stopClock"
    r = requests.post(url=URL)
    paused = True


def resume_shotclock():
    URL = "http://" + server_ipv4 + ":5000/startShotClock"
    r = requests.post(url=URL)


def resume_clock():
    global paused
    URL = "http://" + server_ipv4 + ":5000/startClock"
    PARAMS = {
    }
    r = requests.post(url=URL, json=PARAMS)
    print('resume')
    paused = False


def pause_resume():
    if not clockstarted:
        startClock(5)
        return
    if paused:
        resume_clock()
    else:
        pause_clock()



def setfoul(hf, gf):
    URL = "http://" + server_ipv4 + ":5000/setFouls"
    PARAMS = {
        "homeFouls": hf,
        "awayFouls": gf
    }
    r = requests.post(url=URL, json=PARAMS)


def setscore(hs, gs):
    URL = "http://" + server_ipv4 + ":5000/setTeamScore"
    PARAMS = {
        "homeScore": hs,
        "awayScore": gs
    }
    r = requests.post(url=URL, json=PARAMS)


def run_player():
    URL = "http://" + server_ipv4 + ":5000/commands/player"
    PARAMS = {
       "zoom": 3,
       "top": False,
       "shotclock": True
    }
    r = requests.post(url=URL, json=PARAMS)


def get_sb():
    URL = "http://" + server_ipv4 + ":5000/getData"
    r = requests.get(url=URL)
    dict_str = r.content.decode("UTF-8")
    get_data = ast.literal_eval(dict_str)
    hs = get_data['HomeScoreOnes'][0] + get_data['HomeScoreTens'][0] * 10
    hf = get_data['HomeFouls'][0]
    gs = get_data['AwayScoreOnes'][0] + get_data['AwayScoreTens'][0] * 10
    gf = get_data['AwayFouls'][0]
    qrt = get_data['Period'][0]
    return hs, hf, gs, gf, qrt


def run_main_loop():
    global hs, hf, gs, gf, qrt
    try:
        hs, hf, gs, gf, qrt = get_sb()
    except:
        hs = 0
        gs = 0
        hf = 0
        gf = 0
        qrt = 0


if __name__ == '__main__':
    run_main_loop()
    while not quitting:
        user_choice = input('ACTION:')
        print(user_choice)
        if user_choice.upper() in ['1', '2', '3', '4', '5', '6']:
            if user_choice.upper() in ['1', '2', '3']:
                hs += int(user_choice)
            else:
                gs += int(user_choice) - 3
            setscore(hs, gs)
        if user_choice.upper() in ['H', 'G']:
            if user_choice.upper() == 'H':
                hf += 1
            else:
                gf += 1
            setfoul(hf, gf)
        if user_choice.upper() == 'C':
            pause_resume()
            print(paused)
        if user_choice.upper() == 'R':
            startClock(5)
        if user_choice.upper() == 'S':
            startShotClock()
        if user_choice.upper() == 'O':
            on()
        if user_choice.upper() in ['Q', 'QUIT', 'EXIT']:
            quitting = True
    quit_sb()
    quit()

