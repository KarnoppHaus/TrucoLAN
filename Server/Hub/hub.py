import socket
import threading
import time as t
import subprocess
import pickle
import os

from . import broadcast

class Hub:
    def __init__(self):
        self.HOST = ''

        self.rooms = {}
        self.room_lock = threading.Lock()

    def free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, 0))
            return s.getsockname()[1]

    def handle_client(self, conn, addr):
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

                                if room_name in self.rooms:
                                    conn.sendall(bytes(f'CCT{self.rooms.get(room_name)[0]}', encoding='utf-8'))
                                    break
                                print(f'{addr} -> Sala {room_name} cheia.')
                                conn.sendall(bytes(f'NEX{room_name}', encoding='utf-8'))

                            case b'CRT': # Criar sala
                                room_name = data.decode()[3:]

                                with self.room_lock:
                                    if room_name not in self.rooms:
                                        port = self.free_port()
                                        new_env = os.environ.copy()
                                        new_env["PORT"] = str(port)
                                        new_env["ROOM_NAME"] = room_name
                                        new_env["HUB_PORT"] = str(self.PORT)
                                        room = subprocess.Popen(["python3", "Server/Room/room.py"], env=new_env)
                                        t.sleep(0.1)
                                        conn.sendall(bytes(f'RCS{port}', encoding='utf-8'))
                                        self.rooms[room_name] = [port, room]
                                        break
                                print(f'{addr} -> Erro. Sala {room_name} já existente!')
                                conn.sendall(bytes(f'AEX{room_name}', encoding='utf-8'))

                            case b'RMV': # Remover sala
                                room_name = data.decode()[3:]
                                self.rooms[room_name][1].kill()
                                del self.rooms[room_name]
                                conn.sendall(bytes(f'A sala {room_name} foi removida com sucesso!', encoding='utf-8'))

                            case b'LSR': # Listar salas
                                conn.sendall(pickle.dumps([room for room in self.rooms]))

                            case _: # Erro (qualquer comando diferente)
                                print(f'{addr} -> Comando desconhecido: {data}')
                                conn.sendall(bytes(f'UCM{data.decode()[3:]}', encoding='utf-8'))
            #except Exception as e:
            #    print(f'Erro na conexão de {addr}: {e}')
        print(f'{addr} -> Conexão Encerrada.')

    def start(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.HOST, 0))
                self.PORT = s.getsockname()[1]
                s.listen()
                broadcast_thread = threading.Thread(target=broadcast.broadcast, args=(self.PORT,))
                broadcast_thread.daemon = True
                broadcast_thread.start()
                while True:
                    conn, addr = s.accept()
                    thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                    thread.start()

        except KeyboardInterrupt:
            for port, room in self.rooms.items():
                room[1].kill()
            print('Hub Encerrado com Sucesso!')

        except Exception as e:
            print(f'Um erro ocorreu: {e}. Tudo esta sendo fechado em segurança!')
            for port, room in self.rooms.items():
                room[1].kill()
            print('Hub Encerrado.')
