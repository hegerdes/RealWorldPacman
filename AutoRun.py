import time
from subprocess import Popen, PIPE, call


if __name__ == "__main__":
    for i in range(10):
        serv_start = 'python3 Server.py localhost:25565 os-base os-rand'
        pac_start = 'python3 PacmanPyGame.py 25565'
        pserv = Popen([serv_start], stdin=PIPE, shell=True)
        time.sleep(3)
        pclient = Popen([pac_start], stdin=PIPE, shell=True)
        time.sleep(3)
        pserv.communicate(input=b'start\n')
        time.sleep(20)