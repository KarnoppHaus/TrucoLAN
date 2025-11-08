import socket
import json
import time

PORT = 50000

def broadcast_receive():
    servers = {}  # ip -> (nome, ip, port)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        s.bind(('0.0.0.0', PORT))
        s.settimeout(1.0)
        while True:
            try:
                data, addr = s.recvfrom(2048)
                info = json.loads(data.decode())
                ip = addr[0]
                servers[ip] = (info.get("name"), info.get("ip"), info.get("port"))
            except socket.timeout:
                pass
            # mostrar lista
            if servers:
                for ip, (name, ipservice, port) in servers.items():
                    if name == 'TrucoHUB':
                        return (ipservice, int(port))
            else:
                pass
            time.sleep(1)
