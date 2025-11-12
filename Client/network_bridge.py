import socket
import threading
import queue
import pickle

class NetworkBridge:
    def __init__(self):
        self.hub_host = None
        self.hub_port = None
        self.hub_sock = None
        self.room_sock = None
        self.hub_queue = queue.Queue()
        self.room_queue = queue.Queue()
        self.running = False

    # ----- HUB -----
    def connect_to_hub(self, host, port):
        self.hub_host = host  # Fixa o host para uso futuro
        self.hub_port = port
        self.hub_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hub_sock.connect((host, port))
        self.hub_sock.settimeout(1.0)
        self.running = True
        t = threading.Thread(target=self._hub_listener, daemon=True)
        t.start()

    def _hub_listener(self):
        while self.running:
            try:
                data = self.hub_sock.recv(2048)
                if data:
                    self.hub_queue.put(data)
            except socket.timeout:
                continue
            except Exception:
                break

    def send_to_hub(self, cmd_bytes):
        self.hub_sock.sendall(cmd_bytes)

    def get_hub_response(self):
        try:
            return self.hub_queue.get_nowait()
        except queue.Empty:
            return None

    # ----- SALA/ROOM -----
    def connect_to_room(self, host, port, username):
        self.room_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.room_sock.connect((host, port))
        self.room_sock.settimeout(1.0)
        self.room_sock.sendall(bytes(username, encoding='utf-8'))
        self.running = True
        t = threading.Thread(target=self._room_listener, daemon=True)
        t.start()

    def _room_listener(self):
        while self.running:
            try:
                data = self.room_sock.recv(4096)
                if data:
                    self.room_queue.put(data)
            except socket.timeout:
                continue
            except Exception:
                break

    def send_ready_status(self, slot_id, ready_flag):
        msg = pickle.dumps({'id': slot_id, 'ready': ready_flag})
        self.room_sock.sendall(msg)

    def get_room_message(self):
        try:
            return self.room_queue.get_nowait()
        except queue.Empty:
            return None

    def send_game_command(self, cmd_bytes):
        self.room_sock.sendall(cmd_bytes)

    def close(self):
        self.running = False
        if self.hub_sock:
            self.hub_sock.close()
        if self.room_sock:
            self.room_sock.close()
