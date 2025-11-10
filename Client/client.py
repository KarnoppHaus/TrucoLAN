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
        while not stop_event.is_set():
            with self.thread_lock:
                s.sendall(b'LSR')
                self.rooms = pickle.loads(s.recv(1024))
            print(self.rooms)
            time.sleep(1)

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

    def wait_while_ready(conn):
        pass

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
                    data = int(s.recv(1))
                    print(f'DATA: {data}')
            
            # Entrou na função start_game do ROOM -> Todos players tem ID único [0, 2, 4] setado e todos estão prontos
            pass #TODO receber e enviar dados do truco

    def start(self):
        try:
            while True:
                room_port = self.connect_hub()
                self.connect_room(room_port)

        except KeyboardInterrupt:
            print('Cliente encerrado com Sucesso!')
