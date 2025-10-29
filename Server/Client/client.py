import socket
import os

import broadcast_receiver

# <-::- TEMPORARIO SISTEMA DE USUARIO -::->
import argparse

parse = argparse.ArgumentParser()
parse.add_argument('-u', '--user', type=str, default='')

args = parse.parse_args()

USER = args.user
# <-::- TEMPORARIO SISTEMA DE USUARIO -::->

def connect_hub():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HUB_HOST, HUB_PORT))
        while True:
            msg = input('Insira um código e seu argumento: ')
            s.sendall(bytes(msg, encoding='utf-8'))

            data = s.recv(1024)

            print(data.decode())

            match data[0:3]:
                case X if (X == b'CCT' or X == b'RCS'): # Pronta para conectar
                    return int(data.decode()[3:])

                case b'AEX': # Sala já existente
                    print(f'A sala {data.decode()[3:]} já existe! Use outro nome.')

                case b'NEX': # Sala não existente
                    print(f'A sala {data.decode()[3:]} não existe! Conecte-se a uma sala existente!')

                case b'UCM': # Comando desconhecido
                    print(f'Comando desconhecido.')

def connect_room(room_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HUB_HOST, room_port))

        s.sendall(bytes(USER, encoding='utf-8'))

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

HUB_HOST, HUB_PORT = broadcast_receiver.broadcast_receive()
HUB_PORT = int(HUB_PORT)
print(HUB_HOST, HUB_PORT)

try:
    while True:
        room_port = connect_hub()
        connect_room(room_port)

except KeyboardInterrupt:
    print('Cliente encerrado com Sucesso!')
