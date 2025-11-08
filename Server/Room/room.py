import socket
import os
import threading

def start_game():
    for player in players:
        player.sendall(b'1')
    turn = 0
    while True:
        player.recv(1)
        for i, player in enumerate(players):
            if i == turn % 2: player.sendall(b'1') #C: turn % 4
            else: player.sendall(b'0')

        move = players[turn % 2].recv(1024) #C: turn % 4
        
        for player in players:
            player.sendall(move)
        
        if move == b'fechar':
            players[0].sendall(b'2')
            break
        turn += 1

HUB_HOST = ''
HUB_PORT = int(os.environ.get("HUB_PORT"))

HOST = ''
PORT = int(os.environ.get("PORT"))

players = []
room_lock = threading.Lock()
players_lock = threading.Lock()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(0)
    while len(players) < 2: #C: 4 players
        conn, addr = s.accept()
        players.append(conn)
    start_game()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HUB_HOST, HUB_PORT))
    s.sendall(bytes(f'RMV{os.environ.get("ROOM_NAME")}', encoding='utf-8'))

