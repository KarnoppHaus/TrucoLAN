import socket
import threading
import pickle
import time

from . import broadcast_receiver

class Client:
    def __init__(self):
        self.USER : str
        self.HUB_HOST, self.HUB_PORT = broadcast_receiver.broadcast_receive()
        self.rooms = []
        self.lr_event = threading.Event() # Evento para parar thread de listar salas
        self.thread_lock = threading.Lock() # Lock usado para receber salas e enviar códigos sem sobrepor envios
        self.data = None
        self.screen : str = 'LOGIN'
        self.infos_dict : dict
        self.infos_game : dict

        self.room_max_players : int
        self.draw_data = {}

        self.player_id : int | None = None
        self.player_ready : int = 0

        self.screen_input_event = threading.Event()
        self.start_client_event = threading.Event()

    def screen_input(self):
        self.screen_input_event.wait()
        self.screen_input_event.clear()
        return self.data

    def lr_timer(self, s, stop_event):
        try:
            while not stop_event.is_set():
                with self.thread_lock:
                    s.sendall(b'LSR')
                    self.rooms = pickle.loads(s.recv(1024))
                    self.draw_data = self.rooms
                # print(self.rooms)
                time.sleep(1)
        except (OSError, EOFError):
            pass

    def connect_hub(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.HUB_HOST, self.HUB_PORT))
            self.screen = 'LOBBY'
            stop = threading.Event()
            lr = threading.Thread(target=self.lr_timer, args=(s, stop))
            lr.daemon = True
            lr.start()
            while True:
                # msg = input(f'Insira o argumento: ')
                msg = self.screen_input()
                with self.thread_lock:
                    s.sendall(bytes(msg, encoding='utf-8'))
                    data = s.recv(1024)

                # print(data.decode())

                match data[0:3]:
                    case X if (X == b'CCT' or X == b'RCS'): # Pronta para conectar
                        stop.set()
                        return int(data.decode()[3:])

                    case b'AEX': # Sala já existente
                        print(f'A sala {data.decode()[3:]} já existe! Use outro nome.')

                    case b'NEX': # Sala não existente
                        print(f'A sala {data.decode()[3:]} não existe! Conecte-se a uma sala existente!')
                        
                    case b'WPD':
                        print(f'A senha esta errada!')

                    case b'UCM': # Comando desconhecido
                        print(f'Comando desconhecido.')

    def connect_room(self, room_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while True:
                try:
                    s.connect((self.HUB_HOST, room_port))
                    break
                except ConnectionRefusedError:
                    pass
            s.sendall(bytes(self.USER, encoding='utf-8')) # Send username
            self.room_max_players = int(s.recv(1))
            
            #Room Draw
            self.draw_data = [None] * self.room_max_players
            
            self.screen = 'WAITROOM'
            
            data = [b'0']
            while data[0] != b'1':
                print(f'ID: {self.player_id} - Ready : {self.player_ready}')
                s.sendall(bytes(f'{self.player_id} {self.player_ready}', encoding='utf-8'))
                data = s.recv(512)
                # print(data)
                self.draw_data = pickle.loads(data[1:])
                # print(self.draw_data)
            
            #while not data:
                #id_ready = int(self.screen_input())
                #id, ready = id_ready.split('\n')
                #if not int(ready):
                #    s.sendall(bytes(id_ready, encoding='utf-8'))
                #    data = s.recv(512)
                #    self.draw_data = pickle.loads(data[1:])
                #    data = int(data[0].decode())
            
            s.sendall(b'1')

            # Entrou na função start_game do ROOM -> Todos players tem ID único [0, 2, 4] setado e todos estão prontos
            while True:
                data = s.recv(512)
                
                while True:
                    match data[:3]:
                        case b'MOV':
                            #mov = input(f'Insira seu movimento: ')
                            mov = self.screen_input()
                            s.sendall(bytes(mov, encoding='utf-8'))
                            conf = s.recv(3)
                            #print(f'CONF MOV: {conf}')
                            if conf == b'ERR':
                                print(f'Erro. Tente novamente!')
                                s.sendall(b'1')
                            else:
                                s.sendall(b'1')
                                break
                    
                        case b'AEN':
                            envido = data.decode()[3:]
                            # ans = input(f'Aceita {envido}? YES/NOO para aceitar ou recusar{", REN ou FEN para aumentar" if envido[0] == 'e' else ", FEN para aumentar" if envido[0] == 'r' else ""}: ')
                            ans = self.screen_input()
                            s.sendall(bytes(ans, encoding='utf-8'))
                            conf = s.recv(3)
                            #print(f'CONF AEN: {conf}')
                            if conf == b'ERR':
                                print(f'Erro. Tente novamente!')
                                s.sendall(b'1')
                            else:
                                s.sendall(b'1')
                                break
                        
                        case b'ATC':
                            truco = data.decode()[3:]
                            print(f'Truco: {truco}')
                            # ans = input(f'Aceita {truco}? YES/NOO para aceitar ou recusar{", RET para aumentar" if truco == 'truco' else ", VQT para aumentar" if truco == 'retruco' else ""}: ')
                            ans = self.screen_input()
                            s.sendall(bytes(ans, encoding='utf-8'))                
                            conf = s.recv(3)
                            #print(f'CONF ATC: {conf}')
                            if conf == b'ERR':
                                print(f'Erro. Tente novamente!')
                                s.sendall(b'1')
                            else:
                                s.sendall(b'1')
                                break

                        case b'AFR':
                            # ans = input(f'{'YES/NOO para aceitar/recusar ' + ' '.join(data.decode()[3:].split('_'))}{', CTF para Contra-Flor ou CFR para Contra-Flor e o Resto' if data.decode()[3:] == 'flor' else ''}{', CFR para Contra-Flor e o Resto' if data.decode()[3:] == 'contra_flor' else ''}: ')
                            ans = self.screen_input()
                            s.sendall(bytes(ans, encoding='utf-8'))
                            conf = s.recv(3)
                            #print(f'CONF AFR: {conf}')
                            if conf == b'ERR':
                                print(f'Erro. Tente novamente!')
                                s.sendall(b'1')
                            else:
                                s.sendall(b'1')
                                break
                        
                        case b'CCF':
                            # ans = input(f'Você deseja chamar sua flor? YES/NOO: ')
                            ans = self.screen_input()
                            s.sendall(bytes(ans, encoding='utf-8'))
                            conf = s.recv(3)
                            #print(f'CONF CCF: {conf}')
                            if conf == b'ERR':
                                print(f'Erro. Tente novamente!')
                                s.sendall(b'1')
                            else:
                                s.sendall(b'1')
                                break
                        
                        case b'INF':
                            self.infos_dict = pickle.loads(data[3:])
                            quem_jogou = f'\nQuem jogou: {self.infos_dict["player_name"]} - {self.infos_dict["player_turn"]}' if self.infos_dict.get("player_name", False) else ""
                            card_played = f'\nCard Played: {self.infos_dict["card_played"]}' if self.infos_dict.get("card_played", False) else ""
                            print(f'INFOS:\nTime1 Points: {self.infos_dict["t1p"]}\nTime2 Points: {self.infos_dict["t2p"]}', f'{quem_jogou}{card_played}')
                            print(f'\nCartas: {", ".join(self.infos_dict["cards"])}\nEnvido: {self.infos_dict["envido"]}', f'\nFlor: {self.infos_dict["flor"]}\nTruco: {self.infos_dict["turn_value"]}')
                            s.sendall(b'1')
                            self.screen = 'GAME'
                            break

                        case b'RND':
                            self.infos_game = pickle.loads(data[3:])
                            print(f'O jogador {self.infos_game["player_name"]} jogou {self.infos_game["card_played"]}')
                            s.sendall(b'1')
                            break

                        
                        case b'TND':
                            print(f'Turn ended')
                            s.sendall(b'1')
                            break
                        
                        case b'END':
                            print(f'Partida finalizada!')
                            return 0
                            
                        case _:
                            print(f'Erro. Tente novamente')
                            s.sendall(b'1')

    def start(self):
        self.start_client_event.wait()
        try:
            while True:
                room_port = self.connect_hub()
                self.connect_room(room_port)

        except KeyboardInterrupt:
            print('Cliente encerrado com Sucesso!')
