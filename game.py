# import pygame
# import sys
# import json, pickle
# import os

# from Client.network_bridge import NetworkBridge
# from ProjectUI.base_screen import BaseScreen
# from ProjectUI.scene_login import SceneLogin
# from ProjectUI.scene_lobby import SceneLobby
# from ProjectUI.scene_waitroom import SceneWaitRoom
# from ProjectUI.scene_game import SceneGame

# pygame.init()
# screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
# WIDTH, HEIGHT = screen.get_size() 

# pygame.display.set_caption("TrucoLAN")
# clock = pygame.time.Clock()

# bridge = NetworkBridge()  # O novo bridge!
# game_data = {
#     'username': '',
#     'bridge': bridge,
#     'room_port': None,
#     'current_room': None,
#     'game_state': {},   # Para a UI local, se necessário
#     'hub_error': ''
# }

# scenes = {
#     "LOGIN": SceneLogin(WIDTH, HEIGHT),
#     "LOBBY": SceneLobby(WIDTH, HEIGHT),
#     "WAITROOM": SceneWaitRoom(WIDTH, HEIGHT),
#     "GAME": SceneGame(WIDTH, HEIGHT),
# }

# game_state = "LOGIN"
# current_scene = scenes["LOGIN"]

# # Se preferir, pode deixar host/hub_port fixos, ou permitir input:
# HUB_HOST = os.environ.get("HUB_HOST", "localhost")
# HUB_PORT = int(os.environ.get("HUB_PORT", "52015"))

# # --- Loop Principal ---
# running = True
# print(">> Iniciando loop principal")

# while running:
#     events = pygame.event.get()
#     for event in events:
#         if event.type == pygame.QUIT:
#             print(">> pygame quit event")
#             running = False

#     print(f">> State: {game_state}")

#     # 1. Debug transição inicial (tela login)
#     # if game_state == "LOGIN" and not bridge.hub_sock:
#     #     try:
#     #         print(">> Tentando conectar ao HUB...")
#     #         bridge.connect_to_hub(HUB_HOST, HUB_PORT)
#     #         print(">> Bridge conectado ao HUB!")
#     #     except Exception as e:
#     #         print(f">> ERRO ao conectar HUB: {e}")
#     #         scenes["LOGIN"].msg_erro = str(e)
#     #         pygame.time.wait(2000)
#     #         running = False

#     # Depois de cada get_hub_response
#     hub_msg = bridge.get_hub_response()
#     if hub_msg:
#         print(">> HUB MSG:", hub_msg)

#     if game_state in ("WAITROOM", "GAME"):
#         room_msg = bridge.get_room_message()
#         if room_msg:
#             print(">> ROOM MSG:", room_msg[:20], "...")

#     # Antes de desenhar a cena
#     print(">> Desenhando a tela:", current_scene.STATE_NAME)
#     current_scene.draw(screen, game_data)
#     pygame.display.flip()
#     clock.tick(60)

#     # 2. Respostas do Hub (Lobby)
#     hub_msg = bridge.get_hub_response()
#     if hub_msg:
#         # Decodifique e trate as respostas do hub
#         if hub_msg.startswith(b'RCS') or hub_msg.startswith(b'CCT'):
#             # Recebeu confirmação para conectar/criar sala
#             room_port = int(hub_msg[3:])
#             game_data['room_port'] = room_port
#             game_state = "WAITROOM"
#         elif hub_msg.startswith(b'AEX'):
#             game_data['hub_error'] = f"Sala já existe!"
#         elif hub_msg.startswith(b'NEX'):
#             game_data['hub_error'] = f"Sala não existe!"
#         elif hub_msg.startswith(b'WPD'):
#             game_data['hub_error'] = f"Senha incorreta!"
#         elif hub_msg.startswith(b'UCM'):
#             game_data['hub_error'] = f"Comando desconhecido no hub."
#         # Atualize mensagens, status, etc na tela do lobby conforme necessário

#     # 3. Respostas da Sala/Room
#     if game_state in ("WAITROOM", "GAME"):
#         room_msg = bridge.get_room_message()
#         if room_msg:
#             # --- Telas de espera ---
#             if game_state == "WAITROOM":
#                 if room_msg == b'0':
#                     game_data['msg_status'] = "Aguardando todos ficarem prontos..."
#                 elif room_msg == b'1':
#                     # Começar o jogo!
#                     game_state = "GAME"
#             # --- Tela de jogo ---
#             elif game_state == "GAME":
#                 prefix = room_msg[:3]
#                 if prefix == b'MOV':
#                     # UI: peça jogada ao usuário, depois envie para bridge.send_game_command(...)
#                     game_data['game_state']['turn_action'] = "MOV"
#                 elif prefix == b'INF':
#                     infos = pickle.loads(room_msg[3:])
#                     game_data['game_state']['infos'] = infos
#                 elif prefix == b'AEN':
#                     # Solicita aceitação de envido
#                     game_data['game_state']['turn_action'] = "AEN"
#                 elif prefix == b'ATC':
#                     # Solicita aceitação truco/retruco
#                     game_data['game_state']['turn_action'] = "ATC"
#                 elif prefix == b'AFR':
#                     # Solicita aceitação flor
#                     game_data['game_state']['turn_action'] = "AFR"
#                 elif prefix == b'CCF':
#                     # UI: pode chamar flor?
#                     game_data['game_state']['turn_action'] = "CCF"
#                 elif prefix == b'RND':
#                     round_infos = pickle.loads(room_msg[3:])
#                     game_data['game_state']['round'] = round_infos
#                 elif prefix == b'TND':
#                     game_data['msg_status'] = "Turno terminou."
#                 elif prefix == b'END':
#                     game_state = "LOGIN"
#                     game_data['msg_status'] = "Partida finalizada!"
#                 elif prefix == b'ERR':
#                     game_data['msg_status'] = "Erro: movimento inválido."
#                 elif prefix == b'SUC':
#                     game_data['msg_status'] = "Sucesso!"
#                 # Outras mensagens...

#     # 4. UI: comandos enviados pelas telas (handle_events retorna string)
#     scene_command = current_scene.handle_events(events, game_data)

#     if scene_command == "LOGIN_CONNECT":
#         # Faça login → chamar bridge.send_to_hub() na tela de login ou aqui
#         try:
#             print(">> Tentando conectar ao HUB...")
#             bridge.connect_to_hub(HUB_HOST, HUB_PORT)
#             print(">> Bridge conectado ao HUB!")
#             bridge.send_to_hub(b'LSR')  # Solicita lista de salas logo após
#             game_state = "LOBBY"
#         except Exception as e:
#             scenes["LOGIN"].msg_erro = f"Erro ao conectar HUB: {e}"
#             continue

#     elif scene_command == "LOBBY_CRIA_SALA":
#         # Espera esses campos em game_data, pois na tela do popup serão preenchidos
#         nome_sala = game_data.get('novo_nome_sala', '')
#         senha = game_data.get('nova_senha_sala', '')
#         num_jogadores = game_data.get('novo_n_jogadores', 4)
#         if nome_sala:
#             msg = f'CRT{nome_sala}\n{senha}\n{num_jogadores}'.encode()
#             bridge.send_to_hub(msg)
#         else:
#             print("Nome da sala não definido!")
#         # Permanece no Lobby até receber resposta do hub

#     elif scene_command == "LOBBY_ENTRA_SALA":
#         nome_sala = game_data.get('sala_selecionada', '')
#         senha = game_data.get('senha_digitada', '')
#         if nome_sala:
#             msg = f'CCT{nome_sala}\n{senha}'.encode()
#             bridge.send_to_hub(msg)
#         else:
#             print("Nome da sala não selecionado!")
#         # Permanece no Lobby até receber resposta do hub

#     elif scene_command == "LOGOUT":
#         bridge.close()
#         game_state = "LOGIN"

#     # Troca de telas conforme o novo estado
#     if game_state != current_scene.STATE_NAME:
#         current_scene = scenes[game_state]

#     # Desenhar tela
#     screen.fill((0, 0, 0))
#     current_scene.draw(screen, game_data)
#     pygame.display.flip()
#     clock.tick(60)

# print("Encerrando o cliente...")
# bridge.close()
# pygame.quit()
# sys.exit()



from Client.client import Client
from ProjectUI.scene_login import SceneLogin
import pygame

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_size() 
    pygame.display.set_caption("TrucoLAN")
    clock = pygame.time.Clock()

    # Inicializa a tela de login
    login_scene = SceneLogin(WIDTH, HEIGHT)
    username = ""

    # Loop de login
    running = True
    while running and username == "":
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                break
        # processa eventos e checa se login foi feito
        result = login_scene.handle_events(events, {})
        if result == "LOGIN_CONNECT":
            username = login_scene.input_usuario.text
            running = False

        screen.fill((0, 0, 0))
        login_scene.draw(screen, {})
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()  # Fecha o Pygame para o client CLI continuar limpo (se for CLI puro)
    if username:
        # Agora sim, inicia o client
        client = Client(username)
        client.start()

