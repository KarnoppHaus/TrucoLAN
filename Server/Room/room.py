import socket
import os
import threading
import pickle

from TrucoLogic.player import Player
from TrucoLogic.team import Team
from TrucoLogic.turn import Turn

def ready_page(conn : socket, addr) -> int | None:
    global players_ready
    with conn:
        user = conn.recv(64).decode()
        print(f'Conn: {conn} | User: {user}')
        if not user:
            n_players -= 1
            conn.close()
            return 1

        id = None
        while True:
            print(players_ready)
            last_id = id            
            data = pickle.loads(conn.recv(64))
            if not data:
                if id is not None:
                    players_conn[id] = None
                    players_ready[id] = None
                n_players -= 1
                conn.close()
                return 1
            id = int(data['id'])
            ready = int(data['ready'])
            with players_lock:
                if id >= 0 and id < len(players_conn) and players_conn[id] is None:
                    players_conn[int(id)] = conn
                    if ready:
                        players_ready[int(id)] = 1
                    if id != last_id and last_id != None:
                        players_conn[last_id] = None
                        players_ready[last_id] = None
                if not ready:
                    players_ready[int(id)] = 0

            if None in players_ready or 0 in players_ready:
                conn.sendall(b'0')
            else:
                break
        
        conn.sendall(b'1')
        start_game()
        
        

def start_game():
    print(f'GAME STARTING!')

HUB_HOST = ''
HUB_PORT = int(os.environ.get("HUB_PORT"))

HOST = ''
PORT = int(os.environ.get("PORT"))

players_conn = [None] * int(os.environ.get("PLAYERS"))
players_ready = [None] * int(os.environ.get("PLAYERS"))
n_players = 0
room_lock = threading.Lock()
players_lock = threading.Lock()
game_ended = threading.Event()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(0)
    while n_players < int(os.environ.get("PLAYERS")):
        conn, addr = s.accept()
        n_players += 1
        t = threading.Thread(target=ready_page, args=(conn, addr))
        t.daemon = True
        t.start()
    game_ended.wait()
        
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HUB_HOST, HUB_PORT))
    s.sendall(bytes(f'RMV{os.environ.get("ROOM_NAME")}', encoding='utf-8'))

