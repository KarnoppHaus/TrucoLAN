import socket
import time
import json
import os

def get_local_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        return ip

PORT = 50000             # porta conhecida para descoberta
INTERVAL = 2.0           # segundos entre anúncios
SERVICE_NAME = "TrucoHUB"
IP = get_local_ip()
stop = False

def stop_broadcast():
    global stop
    stop = True

def broadcast(port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = json.dumps({"name": SERVICE_NAME, "ip": IP, "port": port}).encode()

        while True:
            # broadcast para endereço de broadcast genérico (0.0.0.0):PORT ou 255.255.255.255
            s.sendto(message, ('<broadcast>', PORT))
            time.sleep(INTERVAL)
            if stop: break