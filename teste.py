import socket

HOST = ''
PORT = 52015

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("TESTE: Escutando na porta", PORT)
    s.accept()  # Nunca vai sair, mas imprime "escutando"
