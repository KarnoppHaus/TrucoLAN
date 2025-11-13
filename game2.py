import pygame
import threading
from Client.client import Client
from ProjectUI.scene_game import SceneGame
from ProjectUI.scene_lobby import SceneLobby
from ProjectUI.scene_login import SceneLogin
from ProjectUI.scene_waitroom import SceneWaitRoom

if __name__ == "__main__":
    client = Client()
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_size() 
    pygame.display.set_caption("TrucoLAN")
    clock = pygame.time.Clock()

    # login_scene = SceneLogin(WIDTH, HEIGHT)
    # result = ""
    
    t = threading.Thread(target=client.start)
    t.daemon = True
    t.start()

    game_instances = {
        "LOGIN" : SceneLogin(WIDTH, HEIGHT, client),
        "LOBBY" : SceneLobby(WIDTH,HEIGHT, client),
        "WAITROOM" : SceneWaitRoom(WIDTH, HEIGHT, client),
        "GAME" : SceneGame(WIDTH, HEIGHT, client)
    }
    
    print(1)

    # running = True
    # while running and result == "":
    #     events = pygame.event.get()

    #     for event in events:
    #         if event.type == pygame.QUIT:
    #             running = False
    #             break

        # result = login_scene.handle_events(events)
        #if result == "LOGIN_CONNECT":
           # username = login_scene.input_usuario.text
            #running = False

        # screen.fill((0, 0, 0))
        # login_scene.draw(screen, {})
        # pygame.display.flip()
        # clock.tick(60)

    #pygame.quit()  # Fecha o Pygame para o client CLI continuar limpo (se for CLI puro)

    while True:
        screen_atual = game_instances.get(client.screen)
        events = pygame.event.get()
        if client.screen == "LOGIN":
            result = screen_atual.handle_events(events)
            if result != '':
                client.USER = result
                client.start_client_event.set()
        if client.screen == "LOBBY":
            result = screen_atual.handle_events(events)
            if result is not None:
                client.data = result
                client.screen_input_event.set()
                
        if client.screen == "WAITROOM": #TODO
            screen_atual.handle_events(events)

        if client.screen == "GAME": #TODO
            result = screen_atual.handle_events(events)
            if result is not None:
                client.data = result
                client.screen_input_event.set(events)

        if screen_atual:
            screen.fill((0, 0, 0))
            screen_atual.draw(screen) # Pode passar dados úteis aqui se quiser customizar
            pygame.display.flip()

        clock.tick(60)
