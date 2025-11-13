import socket
import os
import threading
import pickle

from TrucoLogic.player import Player
from TrucoLogic.team import Team
from TrucoLogic.turn import Turn

class ExitGame(Exception):
    pass

class TurnEnded(Exception):
    pass

def close_room():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HUB_HOST, HUB_PORT))
        s.sendall(bytes(f'RMV{os.environ.get("ROOM_NAME")}', encoding='utf-8'))

def ready_page(conn : socket) -> int:
    global connected_players
    user = conn.recv(64).decode()
    if not user:
        connected_players -= 1
        conn.close()
        return 1
    conn.sendall(bytes(f'{players_n}', encoding='utf-8'))

    id = None
    last_id = None
    while True:
        
        data = conn.recv(512)
        if not data:
            if type(last_id) is int and last_id >= 0 and last_id < players_n - 1:
                players_conn[last_id] = None
                players_usernames[last_id] = None
                players_ready[last_id] = None
            connected_players -= 1
            conn.close()
            if connected_players == 0:
                close_room()
            return 1
        try:
            id, ready = list(map(int, data.decode().split()))
        except ValueError:
            id = None
            ready = 0
        with players_lock:
            if players_ready[-1]:
                break
            if type(id) is int and id >= 0 and id < players_n and (players_conn[id] is None or players_conn[id] == conn):
                players_conn[id] = conn
                players_usernames[id] = user
                if id != last_id and last_id is not None:
                    players_conn[last_id] = None
                    players_usernames[last_id] = None
                    players_ready[last_id] = None
                last_id = id
            if last_id is not None:
                if ready == 1:
                    players_ready[last_id] = 1
                else:
                    players_ready[last_id] = 0

            if None in players_ready[:-1] or 0 in players_ready:
                conn.sendall(b'0' + pickle.dumps(players_usernames))
            else:
                players_ready[-1] = True
                break
        
    conn.sendall(b'1' + pickle.dumps(players_usernames))
    conn.recv(512)
    return 0
        
def manage_flor(turn, caller):
    #TODO Send All Infos to All Players
    for player_infos, player_conn_infos in zip(players, players_conn):
        send_infos = {'cards': [key for key, item in player_infos.cards.items() if item], 'envido': player_infos.envido_points, 'flor': player_infos.flor, 'turn_value': turn.turn_value, 't1p': t1.points, 't2p': t2.points}
        player_conn_infos.sendall(b'INF' + pickle.dumps(send_infos))
        player_conn_infos.recv(1)
    
    turn.envidos = ''
    flor_type = {'f': 'flor', 'c': 'contra_flor', 'r': 'contra_flor_e_o_resto'}
    for answer_player in players[caller.id + 1:] + players[:caller.id]:
        if answer_player.team is not caller.team and answer_player.flor is not None:
            answer_player_conn = players_conn[answer_player.id]
            answer_player_conn.sendall(b'AFR' + bytes(flor_type[turn.flor[-1]], encoding='utf-8'))
            
            while True:
                ans = answer_player_conn.recv(512)
                match ans:
                    case b'YES':
                        if turn.flor[-1] != 'f':
                            answer_player_conn.sendall(b'SUC')
                            answer_player_conn.recv(1)
                            winners = turn.call_flor(caller.team, True)
                            # print(f'\nORDEM DA FLOR')
                            for player in [p for p in winners if p.flor is not None]:
                                print(f'{player.name} : {player.flor}')
                            return 0
                        else:
                            answer_player_conn.sendall(b'ERR')
                            answer_player_conn.recv(1)
            
                    case b'NOO':
                        if turn.flor[-1] != 'f':
                            answer_player_conn.sendall(b'SUC')
                            answer_player_conn.recv(1)
                            turn.call_flor(caller.team, accepted=False)
                            return 0
                        else:
                            answer_player_conn.sendall(b'ERR')
                            answer_player_conn.recv(1)
                    
                    case b'CTF':
                        if turn.flor[-1] == 'f':
                            answer_player_conn.sendall(b'SUC')
                            answer_player_conn.recv(1)
                            turn.flor += 'c'
                            return manage_flor(turn, answer_player)
                        else:
                            answer_player_conn.sendall(b'ERR')
                            answer_player_conn.recv(1)
                        
                    case b'CFR':
                        if turn.flor[-1] == 'c':
                            answer_player_conn.sendall(b'SUC')
                            answer_player_conn.recv(1)
                            turn.flor += 'r'
                            return manage_flor(turn, answer_player)
                        else:
                            answer_player_conn.sendall(b'ERR')
                            answer_player_conn.recv(1)
            
                    case _:
                        answer_player_conn.sendall(b'ERR')
                        answer_player_conn.recv(1)
                        
    turn.call_flor(caller.team, True)
    return 0
    
def manage_truco(turn, caller):
    #TODO Send All Infos to All Players
    for player_infos, player_conn_infos in zip(players, players_conn):
        send_infos = {'cards': [key for key, item in player_infos.cards.items() if item], 'envido': player_infos.envido_points, 'flor': player_infos.flor, 'turn_value': turn.turn_value, 't1p': t1.points, 't2p': t2.points}
        player_conn_infos.sendall(b'INF' + pickle.dumps(send_infos))
        player_conn_infos.recv(1)
    
    if turn.round == 0 and turn.turn_value == 1 and not turn.envido_completed and not turn.flor:
        for answer_player in players[caller.id + 1:] + players[:caller.id]:
            if answer_player.flor is not None:
                answer_player_conn = players_conn[answer_player.id]
                answer_player_conn.sendall(b'CCF')
                
                while True:
                    ans = answer_player_conn.recv(512)
                    match ans:
                        case b'YES':
                            turn.flor += 'f'
                            answer_player_conn.sendall(b'SUC')
                            answer_player_conn.recv(1)
                            return manage_flor(turn, answer_player)
                        
                        case b'NOO':
                            answer_player_conn.sendall(b'SUC')
                            answer_player_conn.recv(1)
                            break
                            
                        case _:
                            answer_player_conn.sendall(b'ERR')
                            answer_player_conn.recv(1)
        
    answer_player = players[(caller.id + 1) % len(players)]
    answer_player_conn = players_conn[(caller.id + 1) % len(players)]
    truco_values = ['truco', 'retruco', 'vale_quatro']
    answer_player_conn.sendall(b'ATC' + bytes(truco_values[turn.turn_value - 1], encoding='utf-8'))
    
    while True:
        ans = answer_player_conn.recv(512)
        match ans:
            case b'YES':
                answer_player_conn.sendall(b'SUC')
                answer_player_conn.recv(1)
                turn.call_truco(caller.team)
                return 0
            
            case b'NOO':
                answer_player_conn.sendall(b'SUC')
                answer_player_conn.recv(1)
                turn.recused_truco(caller.team)
                return 0
                                                 
            case X if (X == b'ENV' or X == b'REN' or X == b'FEN'):
                if turn.turn_value == 1 and turn.round == 0 and not turn.envido_completed:
                    answer_player_conn.sendall(b'SUC')
                    answer_player_conn.recv(1)
                    turn.envidos += ans.decode()[0].lower()
                    return manage_envido(turn, answer_player)
                else:
                    answer_player_conn.sendall(b'ERR')
                    answer_player_conn.recv(1)
                                     
            case b'RET':
                if turn.turn_value == 1:
                    answer_player_conn.sendall(b'SUC')
                    answer_player_conn.recv(1)
                    turn.call_truco(answer_player.team)
                    return manage_truco(turn, answer_player)
                else:
                    answer_player_conn.sendall(b'ERR')
                    answer_player_conn.recv(1)
            
            case b'VQT':
                if turn.turn_value == 2:
                    answer_player_conn.sendall(b'SUC')
                    answer_player_conn.recv(1)
                    turn.call_truco(answer_player.team)
                    return manage_truco(turn, answer_player)
                else:
                    answer_player_conn.sendall(b'ERR')
                    answer_player_conn.recv(1)
            
            case _:
                answer_player_conn.sendall(b'ERR')
                answer_player_conn.recv(1)

def manage_envido(turn : Turn, caller : Player) -> None:
    #TODO Send All Infos to All Players
    for player_infos, player_conn_infos in zip(players, players_conn):
        send_infos = {'cards': [key for key, item in player_infos.cards.items() if item], 'envido': player_infos.envido_points, 'flor': player_infos.flor, 'turn_value': turn.turn_value, 't1p': t1.points, 't2p': t2.points}
        player_conn_infos.sendall(b'INF' + pickle.dumps(send_infos))
        player_conn_infos.recv(1)
    
    if turn.round == 0 and turn.turn_value == 1 and not turn.envido_completed and not turn.flor:
        for answer_player in players[caller.id + 1:] + players[:caller.id]:
            if answer_player.flor is not None:
                answer_player_conn = players_conn[answer_player.id]
                answer_player_conn.sendall(b'CCF')
                
                while True:
                    ans = answer_player_conn.recv(512)
                    match ans:
                        case b'YES':
                            turn.flor += 'f'
                            answer_player_conn.sendall(b'SUC')
                            answer_player_conn.recv(1)
                            return manage_flor(turn, answer_player)
                        
                        case b'NOO':
                            answer_player_conn.sendall(b'SUC')
                            answer_player_conn.recv(1)
                            break
                            
                        case _:
                            answer_player_conn.sendall(b'ERR')
                            answer_player_conn.recv(1)
                            
    answer_player = players[(caller.id + 1) % len(players)]
    answer_player_conn = players_conn[(caller.id + 1) % len(players)]
    envido_type = {'e': 'envido', 'r': 'real_envido', 'f': 'falta_envido'}
    answer_player_conn.sendall(b'AEN' + bytes(envido_type[turn.envidos[-1]], encoding='utf-8'))
    
    
    while True:
        ans = answer_player_conn.recv(512)
        match ans:
            case b'YES':
                answer_player_conn.sendall(b'SUC')
                answer_player_conn.recv(1)
                winners = turn.call_envido(caller.team, accepted=True)
                print(f'\nORDEM DO ENVIDO')
                for player in winners:
                    print(f'{player.name} : {player.envido_points}')
                return 0
            
            case b'NOO':
                answer_player_conn.sendall(b'SUC')
                answer_player_conn.recv(1)
                turn.call_envido(caller.team, accepted=False)
                return 0
                      
            case b'REN':
                if not any(env in turn.envidos for env in ['r', 'f']):
                    answer_player_conn.sendall(b'SUC')
                    answer_player_conn.recv(1)
                    turn.envidos += 'r'
                    return manage_envido(turn, answer_player)
                else:
                    answer_player_conn.sendall(b'ERR')
                    answer_player_conn.recv(1)
            
            case b'FEN':
                if 'f' not in turn.envidos:
                    answer_player_conn.sendall(b'SUC')
                    answer_player_conn.recv(1)
                    turn.envidos += 'f'
                    return manage_envido(turn, answer_player)
                else:
                    answer_player_conn.sendall(b'ERR')
                    answer_player_conn.recv(1)
            
            case _:
                answer_player_conn.sendall(b'ERR')
                answer_player_conn.recv(1)

def start_game():
    for i, conn in enumerate(players_conn):
        conn.sendall(bytes(f'{i}', encoding='utf-8'))
        conn.recv(1)
    
    for player_id in range(int(os.environ.get("PLAYERS"))):
        team = t1 if player_id % 2 == 0 else t2
        player = Player(player_id, players_usernames[player_id], team)
        players[player_id] = player
        team.players.append(player)
        
    ERR = False
    p = -1
    try:
        while True:
            t1.is_hand = not t1.is_hand
            t2.is_hand = not t2.is_hand
            p = (p + 1) % len(players)
            start_turn = players[p]
            turn = Turn(players, teams)
               
            while not turn.ended:
                try:
                    for player in (players[start_turn.id:] + players[:start_turn.id]):                       
                        player_conn = players_conn[player.id]
                        while player.playing_turn:
                            for team in teams:
                                if team.points >= 30:
                                    print(f'{team.team} venceu o jogo!')
                                    raise ExitGame
                            if turn.ended: raise TurnEnded
                            if not ERR:
                                #TODO Send All Infos to All Players
                                for player_infos, player_conn_infos in zip(players, players_conn):
                                    send_infos = {'cards': [key for key, item in player_infos.cards.items() if item], 'envido': player_infos.envido_points, 'flor': player_infos.flor, 'turn_value': turn.turn_value, 't1p': t1.points, 't2p': t2.points}
                                    player_conn_infos.sendall(b'INF' + pickle.dumps(send_infos))
                                    player_conn_infos.recv(1)
                                
                                player_conn.sendall(b'MOV')
                            ERR = False
                            mov = player_conn.recv(512)
                            print(f'MOV: {mov.decode()}')
                            
                            match mov[:3]:
                                case X if (X == b'ENV' or X == b'REN' or X == b'FEN'):
                                    if not turn.envidos and turn.round == 0 and turn.turn_value == 1 and not turn.flor:
                                        player_conn.sendall(b'SUC')
                                        player_conn.recv(1)
                                        turn.envidos += mov.decode()[0].lower()
                                        manage_envido(turn, player)
                                    else:
                                        player_conn.sendall(b'ERR')
                                        player_conn.recv(1)
                                        ERR = True
                                        
                                case b'FLR':
                                    if turn.round == 0 and turn.turn_value == 1 and not turn.envido_completed and player.flor is not None:
                                        player_conn.sendall(b'SUC')
                                        player_conn.recv(1)
                                        turn.flor += 'f'
                                        manage_flor(turn, player)
                                    else:
                                        player_conn.sendall(b'ERR')
                                        player_conn.recv(1)
                                        ERR = True
                                
                                case b'TRC':
                                    if player.team is not turn.truco_caller and turn.turn_value < 4:
                                        player_conn.sendall(b'SUC')
                                        player_conn.recv(1)
                                        manage_truco(turn, player)
                                    else:
                                        player_conn.sendall(b'ERR')
                                        player_conn.recv(1)
                                        ERR = True
                                        
                                case b'ABN':
                                    player_conn.sendall(b'SUC')
                                    player_conn.recv(1)
                                    turn.abandon_round(player)
                                    break
                            
                                case b'PLY':
                                    played = turn.play_card(player, mov.decode()[3:])
                                    if played: 
                                        player_conn.sendall(b'SUC')
                                        player_conn.recv(1)
                                        break
                                    else:
                                        player_conn.sendall(b'ERR')
                                        player_conn.recv(1)
                                        ERR = True
                                
                                case _:
                                    player_conn.sendall(b'ERR')
                                    player_conn.recv(1)
                                    ERR = True
                                                
                        for player_conn, s_player in zip(players_conn, players):
                            game_infos = {'player_turn': player.id, 'player_name': player.name, 'card_played': turn.played_cards.get(player, 'Abandoned')}
                            player_conn.sendall(b'RND' + pickle.dumps(game_infos))
                            player_conn.recv(1)
                
                except TurnEnded:
                    for player_conn, s_player in zip(players_conn, players):
                        player_conn.sendall(b'TND')
                        player_conn.recv(1)
                
                if not turn.ended: start_turn = turn.end_round()
                else: 
                    print(f'Turn ended')
                    for player_conn, s_player in zip(players_conn, players):
                        player_conn.sendall(b'TND')
                        player_conn.recv(1)
            
    except ExitGame:
        for player_conn in players_conn:
            player_conn.sendall(b'END')
            players_conn.close()

HUB_HOST = ''
HUB_PORT = int(os.environ.get("HUB_PORT"))

HOST = ''
PORT = int(os.environ.get("PORT"))

connected_players = 0
players_n = int(os.environ.get("PLAYERS"))

players_conn = [None] * players_n
players_usernames = [None] * players_n
players_ready = [None] * (players_n + 1)

room_lock = threading.Lock()
players_lock = threading.Lock()

players = [None] * players_n
t1 = Team('Time1')
t2 = Team('Time2')
teams = [t1, t2]
t1.is_hand = False
t2.is_hand = True

ready_page_threads = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(0)
    while not players_ready[-1]:
        if connected_players < players_n:
            conn, addr = s.accept()
            connected_players += 1
            t = threading.Thread(target=ready_page, args=(conn,))
            t.daemon = True
            ready_page_threads.append(t)
            t.start()
    for t in ready_page_threads:
        t.join()
    try:
        start_game()
    except:
        pass
        
close_room()