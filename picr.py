import subprocess
import requests
import time

server_ipv4 = 'localhost'

def init():
    URL = "http://" + server_ipv4 + ":5000/init"
    PARAMS = {
        "scoreboard_id": "basketball",
        "font": 0,
        "period": 2,
        "up": False,
        "shotclock": True,
        "debug": False,
        "listen_port": 5503
    }
    r = requests.post(url=URL, json=PARAMS)
    time.sleep(5)
    
def player():
    URL = "http://" + server_ipv4 + ":5000/commands/player"
    PARAMS = {
        "debug": False,
        "top": False,
        "zoom": 1
    }
    r = requests.post(url=URL, json=PARAMS)
    time.sleep(5)

if __name__ == '__main__':
    psx = subprocess.getoutput('ps -aux | grep "python3 server" | head -1')
    to_kill=(str(psx.split()[1]))
    time.sleep(5)
    subprocess.Popen(['kill', '-9', to_kill])
    psx = subprocess.getoutput('ps -aux | grep "python3 player" | head -1')
    to_kill=(str(psx.split()[1]))
    time.sleep(5)
    subprocess.Popen(['kill', '-9', to_kill])
    subprocess.Popen(['python3', 'server.py'])
    time.sleep(10)
    init()
    time.sleep(10)
    player()
    
    