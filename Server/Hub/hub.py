import socket
import threading
import time as t
import subprocess
import os

import broadcast

def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, 0))
        return s.getsockname()[1]

def teste(players):
    for player in players:
        data = player.recv(1024)
        player.sendall(data)

def handle_client(conn, addr):
    print(f'Connected by {addr}')
    with conn:
        #try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                if data:
                    match data[:3]:
                        case b'CCT': # Conectar a sala
                            room_name = data.decode()[3:]

                            if room_name in rooms:
                                conn.sendall(bytes(f'CCT{rooms.get(room_name)[0]}', encoding='utf-8'))
                                break
                            print(f'{addr} -> Sala {room_name} cheia.')
                            conn.sendall(bytes(f'NEX{room_name}', encoding='utf-8'))

                        case b'CRT': # Criar sala
                            room_name = data.decode()[3:]

                            with room_lock:
                                if room_name not in rooms:
                                    port = free_port()
                                    new_env = os.environ.copy()
                                    new_env["PORT"] = str(port)
                                    new_env["ROOM_NAME"] = room_name
                                    new_env["HUB_PORT"] = PORT
                                    room = subprocess.Popen(["python3", "../Room/room.py"], env=new_env)
                                    t.sleep(0.1)
                                    conn.sendall(bytes(f'RCS{port}', encoding='utf-8'))
                                    rooms[room_name] = [port, room]
                                    break
                            print(f'{addr} -> Erro. Sala {room_name} já existente!')
                            conn.sendall(bytes(f'AEX{room_name}', encoding='utf-8'))

                        case b'RMV': # Remover sala
                            room_name = data.decode()[3:]
                            rooms[room_name][1].kill()
                            del rooms[room_name]
                            conn.sendall(bytes(f'A sala {room_name} foi removida com sucesso!', encoding='utf-8'))

                        case b'LS0':
                            print(f'Salas: {", ".join([key for key, item in rooms.items()])}')
                            conn.sendall(b'UCM')

                        case _: # Erro (qualquer comando diferente)
                            print(f'{addr} -> Comando desconhecido: {data}')
                            conn.sendall(bytes(f'UCM{data.decode()[3:]}', encoding='utf-8'))
        #except Exception as e:
            #print(f'Erro na conexão de {addr}: {e}')
    print(f'{addr} -> Conexão Encerrada.')

HOST = ''

players = []
rooms = {}
room_lock = threading.Lock()

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, 0)) #C: Alterar PORT para 0
        PORT = s.getsockname()[1]
        s.listen()
        print(PORT)
        broadcast_thread = threading.Thread(target=broadcast.broadcast, args=(PORT,))
        broadcast_thread.daemon = True
        broadcast_thread.start()
        while len(players) < 2:
            conn, addr = s.accept()
            players.append(conn)
            #thread = threading.Thread(target=handle_client, args=(conn, addr))
            #thread.start()
        teste(players)

except KeyboardInterrupt:
    for port, room in rooms.items():
        room[1].kill()
    print('Hub Encerrado com Sucesso!')

except Exception as e:
    print(f'Um erro ocorreu: {e}. Tudo esta sendo fechado em segurança!')
    for port, room in rooms.items():
        room[1].kill()
    print('Hub Encerrado.')
