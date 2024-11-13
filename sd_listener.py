import requests
import time
import os


server_ipv4 = '127.0.0.1'
#os.system('mode con: cols=15 lines=10')


def init():
    URL = "http://" + server_ipv4 + ":5000/init"
    PARAMS = {
        "scoreboard_id": "basketball",
        "shotclock": True,
        "debug": False,
        "listen_port": 5503
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


if __name__ == '__main__':
    init()
    time.sleep(3)
    run_player()
    time.sleep(5)
    os.startfile(f"{os.getcwd()}"+'\\stream_deck.exe')
    quit()

