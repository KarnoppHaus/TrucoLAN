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

    def lr_timer(self, s, stop_event):
        while not stop_event.is_set():
            with self.thread_lock:
                s.sendall(b'LSR')
                self.rooms = pickle.loads(s.recv(1024))
            print(self.rooms)
            time.sleep(2)

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

                    case b'UCM': # Comando desconhecido
                        print(f'Comando desconhecido.')

    def connect_room(self, room_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.HUB_HOST, room_port))
            s.sendall(bytes(self.USER, encoding='utf-8'))

            start = s.recv(1)

            print(f'O jogo iniciará em breve...')
            while True:
                s.sendall(b'1') # Confirmação para seguir jogo
                is_my_turn = s.recv(1)
                if is_my_turn == b'1':
                    move = input('Insira sua jogada: ')
                    s.sendall(bytes(move + '\n', encoding='utf-8'))
                if is_my_turn == b'2': break
                else:
                    print(f'Espere sua vez de jogar!')
                data = s.recv(2048)
                print(data)

    def start(self):
        try:
            while True:
                room_port = self.connect_hub()
                self.connect_room(room_port)

        except KeyboardInterrupt:
            print('Cliente encerrado com Sucesso!')
