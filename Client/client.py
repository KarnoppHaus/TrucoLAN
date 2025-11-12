import socket
import threading
import pickle
import time

from . import broadcast_receiver

class Client:
    def __init__(self, user):
        self.USER = user
        self.HUB_HOST, self.HUB_PORT = broadcast_receiver.broadcast_receive()
        self.rooms = []
        self.lr_event = threading.Event() # Evento para parar thread de listar salas
        self.thread_lock = threading.Lock() # Lock usado para receber salas e enviar códigos sem sobrepor envios
        self.id : int
        self.team : int

    def lr_timer(self, s, stop_event):
        try:
            while not stop_event.is_set():
                with self.thread_lock:
                    s.sendall(b'LSR')
                    self.rooms = pickle.loads(s.recv(1024))
                print(self.rooms)
                time.sleep(1)
        except (OSError, EOFError):
            pass

    def connect_hub(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.HUB_HOST, self.HUB_PORT))
            stop = threading.Event()
            lr = threading.Thread(target=self.lr_timer, args=(s, stop))
            lr.daemon = True
            lr.start()
            while True:
                msg = input('Insira um código e seu argumento: ')
                with self.thread_lock:
                    s.sendall(bytes(msg, encoding='utf-8'))
                    data = s.recv(1024)

                print(data.decode())

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
            s.connect((self.HUB_HOST, room_port))
            s.sendall(bytes(self.USER, encoding='utf-8')) # Send username

            #Room HUB
            data = 0
            while not data:
                id = int(input(r'Insira o ID do jogador [0, ..., 3]: '))
                ready = 1
                while ready and not data:
                    ready = int(input(f'Insira 1 para PRONTO e 0 para ESPERAR: '))
                    s.sendall(pickle.dumps({'id': id, 'ready': ready}))
                    data = int(s.recv(512))
            
            s.sendall(b'1')
            # Entrou na função start_game do ROOM -> Todos players tem ID único [0, 2, 4] setado e todos estão prontos
            while True:
                data = s.recv(512)
                
                while True:
                    match data[:3]:
                        case b'MOV':
                            mov = input(f'Insira seu movimento: ')
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
                            ans = input(f'Aceita {envido}? YES/NOO para aceitar ou recusar{", REN ou FEN para aumentar" if envido[0] == 'e' else ", FEN para aumentar" if envido[0] == 'r' else ""}: ')
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
                            ans = input(f'Aceita {truco}? YES/NOO para aceitar ou recusar{", RET para aumentar" if truco == 'truco' else ", VQT para aumentar" if truco == 'retruco' else ""}: ')
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
                            ans = input(f'{'YES/NOO para aceitar/recusar ' + ' '.join(data.decode()[3:].split('_'))}{', CTF para Contra-Flor ou CFR para Contra-Flor e o Resto' if data.decode()[3:] == 'flor' else ''}{', CFR para Contra-Flor e o Resto' if data.decode()[3:] == 'contra_flor' else ''}: ')
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
                            ans = input(f'Você deseja chamar sua flor? YES/NOO: ')
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
                            infos_dict = pickle.loads(data[3:])
                            print(f'INFOS:\nTime1 Points: {infos_dict['t1p']}\nTime2 Points: {infos_dict['t2p']}{("\nQuem jogou: " + infos_dict['player_name'] + ' - ' + str(infos_dict['player_turn'])) if infos_dict.get('player_name', False) else ""}{("\nCard Played: " + infos_dict['card_played']) if infos_dict.get('card_played', False) else ""}')
                            print(f'\nCartas: {', '.join(infos_dict['cards'])}\nEnvido: {infos_dict['envido']}\nFlor: {infos_dict['flor']}\nTruco: {infos_dict['turn_value']}')
                            s.sendall(b'1')
                            break
                        
                        case b'RND':
                            round_infos = pickle.loads(data[3:])
                            print(f'O jogador {round_infos['player_name']} jogou {round_infos['card_played']}')
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
        try:
            while True:
                room_port = self.connect_hub()
                self.connect_room(room_port)

        except KeyboardInterrupt:
            print('Cliente encerrado com Sucesso!')
