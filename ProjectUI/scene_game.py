import pygame
import math
import pickle
from .base_screen import BaseScreen, Button, TextInput

class SceneGame(BaseScreen):
    
    def __init__(self, screen_width, screen_height, client):
        self.client = client

        super().__init__(screen_width, screen_height)
        #placar
        self.placar_rect = pygame.Rect(self.largura_tela * 0.75, self.margem, 
                                       self.largura_tela * 0.2, self.altura_tela * 0.1)
        
        btn_w = self.largura_tela * 0.15
        btn_h = self.altura_tela * 0.08
        btn_x = self.largura_tela * 0.8
        btn_y_start = self.altura_tela * 0.6

        self.btn_truco = Button(btn_x, btn_y_start, btn_w, btn_h, "TRUCO!", font_obj=self.fonte_padrao)
        self.btn_aceitar = Button(btn_x, btn_y_start + btn_h + 10, btn_w, btn_h, "ACEITAR", font_obj=self.fonte_padrao)
        self.btn_correr = Button(btn_x, btn_y_start + (btn_h + 10)*2, btn_w, btn_h, "CORRER", font_obj=self.fonte_padrao)

        self.botoes_cartas = []

        card_w, card_h = 100, 150
        hand_y = self.altura_tela - card_h - self.margem
        hand_x_start = self.largura_tela // 2 - card_w 

        for i in range(3):
            rect = pygame.Rect(hand_x_start + (i * (card_w + 10)), hand_y, card_w, card_h)
            self.botoes_cartas.append({'rect': rect, 'carta': None}) 

        self.estado_atual = {}     # snapshot do estado do jogo
        self.turn_action = None    # ação pendente

    def handle_events(self, events, game_data):
        #mudar tudo isso aqui pra comunicação do jogo em si
        #oq o client roda a cada jogada e interpretar na tela
        bridge = game_data['bridge']
        username = game_data['username']
        msg = bridge.get_room_message()
        if msg:
            prefix = msg[:3]
            if prefix == b'INF':
                self.estado_atual = pickle.loads(msg[3:])
            elif prefix in [b'MOV', b'AEN', b'ATC', b'AFR', b'CCF']:
                self.turn_action = prefix.decode()
            elif prefix == b'RND':
                info = pickle.loads(msg[3:])
                self.estado_atual['last_round'] = info
            elif prefix == b'TND':
                self.estado_atual['turn_ended'] = True
            elif prefix == b'END':
                return "LOGIN"
            elif prefix == b'ERR':
                # Mostre mensagem de erro no UI se desejar
                pass

        mao = self.estado_atual.get('cards', [])
        # Handle cartas clicadas
        for event in events:
            for i, slot_carta in enumerate(self.botoes_cartas):
                rect = slot_carta['rect']
                carta = slot_carta.get('carta')
                if event.type == pygame.MOUSEMOTION:
                    if rect.collidepoint(event.pos):
                        rect.y = self.altura_tela - 170 - self.margem 
                    else:
                        rect.y = self.altura_tela - 150 - self.margem
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rect.collidepoint(event.pos) and carta is not None and self.turn_action == "MOV":
                        bridge.send_game_command(b'PLY' + str(carta).encode())
                        self.botoes_cartas[i]['carta'] = None 

            # Truco, aceitar, correr
            if self.turn_action == "MOV" and self.btn_truco.handle_event(event):
                bridge.send_game_command(b'TRC')
            if self.turn_action in ("ATC", "AEN"):
                if self.btn_aceitar.handle_event(event):
                    bridge.send_game_command(b'YES')
                if self.btn_correr.handle_event(event):
                    bridge.send_game_command(b'NOO')
        return "GAME"

    def draw(self, screen):
        super().draw(screen)
        estado_jogo = self.estado_atual
        
        placar_nos = estado_jogo.get('t1p', 0)
        placar_eles = estado_jogo.get('t2p', 0)
        valor_rodada = estado_jogo.get('turn_value', 1)

        pygame.draw.rect(screen, self.cor_box, self.placar_rect, border_radius=10) #desenha plcar

        pygame.draw.rect(screen, self.cor_borda, self.placar_rect, border_radius=10, width=3) #desenha placar

        placar_txt = self.fonte_padrao.render(f"NÓS: {placar_nos}", True, self.cor_texto)
        screen.blit(placar_txt, (self.placar_rect.x + 10, self.placar_rect.y + 10))
        placar_txt_eles = self.fonte_padrao.render(f"ELES: {placar_eles}", True, self.cor_texto)
        screen.blit(placar_txt_eles, (self.placar_rect.x + 10, self.placar_rect.y + 45))

        mao = estado_jogo.get('cards', [])
        for i, slot_carta in enumerate(self.botoes_cartas):
            if i < len(mao):
                slot_carta['carta'] = mao[i]
            if slot_carta['carta']:
                pygame.draw.rect(screen, self.cor_input, slot_carta['rect'], border_radius=10)
                pygame.draw.rect(screen, self.cor_borda, slot_carta['rect'], border_radius=10, width=2)
                carta_nome = str(slot_carta['carta'])
                txt_surf = self.fonte_pequena.render(carta_nome, True, self.cor_texto)
                txt_rect = txt_surf.get_rect(center=slot_carta['rect'].center)
                screen.blit(txt_surf, txt_rect)

        # Botões de ação (só desenha se protocolo permitir)
        if self.turn_action == "MOV":
            self.btn_truco.draw(screen)
        if self.turn_action in ("ATC", "AEN"):
            self.btn_aceitar.draw(screen)
            self.btn_correr.draw(screen)
        # Adicione lógica para outras fases se desejar

