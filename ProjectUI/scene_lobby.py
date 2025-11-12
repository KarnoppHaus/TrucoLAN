import pygame, pickle
from .base_screen import BaseScreen, Button, TextInput

class SceneLobby(BaseScreen):
    STATE_NAME = "LOBBY"
    
    def __init__(self, screen_width, screen_height, client):
        self.client = client

        super().__init__(screen_width, screen_height)
        self.label_lista_vazia = None

        self.titulo_surf = self.fonte_titulo.render("Salas", True, self.cor_texto)
        self.titulo_rect = self.titulo_surf.get_rect(
            center=(self.rect_painel_central.centerx, self.rect_painel_central.top + self.altura_tela * 0.1)
        )
        self.btn_voltar = Button(
            x=self.margem, y=self.margem, 
            width=self.largura_tela * 0.1, height=self.altura_tela * 0.07,
            text="< Voltar", font_obj=self.fonte_pequena
        )
        btn_criar_w = self.rect_painel_central.width * 0.4
        btn_criar_h = self.altura_tela * 0.1
        self.btn_criar_sala = Button(
            x=self.rect_painel_central.centerx - (btn_criar_w // 2),
            y=self.rect_painel_central.height * 0.7,
            width=btn_criar_w, height=btn_criar_h,
            text="CRIAR SALA", font_obj=self.fonte_padrao
        )
        
        self.botoes_salas = []
        self.lista_y_start = self.rect_painel_direita.top + self.margem

        self.mostrando_popup_criar = False
        self.mostrando_popup_entrar = False
        self.popup_player_count = 4 

        self._criar_elementos_popup_criar()
        self._criar_elementos_popup_entrar()

        self.last_error = ""
        self.error_surf = None
        self.error_rect = None

    def _criar_elementos_popup_criar(self):

        popup_w, popup_h = self.largura_tela * 0.4, self.altura_tela * 0.6
        self.popup_rect = pygame.Rect(0, 0, popup_w, popup_h)
        self.popup_rect.center = (self.largura_tela // 2, self.altura_tela // 2)

        self.popup_criar_label = self.fonte_padrao.render("Criar Nova Sala", True, self.cor_texto)
        self.popup_criar_label_rect = self.popup_criar_label.get_rect(
            center=(self.popup_rect.centerx, self.popup_rect.top + popup_h * 0.1))

        input_h = popup_h * 0.12
        self.input_criar_nome = TextInput(self.popup_rect.x + popup_w * 0.1, self.popup_rect.y + popup_h * 0.2, popup_w * 0.8, input_h,
                                          font_obj=self.fonte_padrao, placeholder="Nome da Sala")
        self.input_criar_senha = TextInput(self.popup_rect.x + popup_w * 0.1, self.popup_rect.y + popup_h * 0.35, popup_w * 0.8, input_h,
                                           font_obj=self.fonte_padrao, placeholder="Senha (opcional)")

        self.popup_jogadores_label = self.fonte_pequena.render("Jogadores:", True, self.cor_texto)
        self.popup_jogadores_label_rect = self.popup_jogadores_label.get_rect(
            center=(self.popup_rect.centerx, self.popup_rect.y + popup_h * 0.52))

        btn_player_h = popup_h * 0.12
        btn_player_w = popup_w * 0.35
        self.btn_players_2 = Button(self.popup_rect.x + popup_w * 0.1, self.popup_rect.y + popup_h * 0.6, btn_player_w, btn_player_h,
                                    "2 Jogadores", font_obj=self.fonte_pequena)
        self.btn_players_4 = Button(self.popup_rect.x + popup_w * 0.55, self.popup_rect.y + popup_h * 0.6, btn_player_w, btn_player_h,
                                    "4 Jogadores", font_obj=self.fonte_pequena)

        btn_h = popup_h * 0.15
        self.btn_criar_ok = Button(self.popup_rect.x + popup_w * 0.1, self.popup_rect.y + popup_h * 0.8, popup_w * 0.35, btn_h,
                                   "OK", font_obj=self.fonte_padrao)
        self.btn_criar_cancel = Button(self.popup_rect.x + popup_w * 0.55, self.popup_rect.y + popup_h * 0.8, popup_w * 0.35, btn_h,
                                       "CANCELAR", font_obj=self.fonte_padrao)
        


    def _criar_elementos_popup_entrar(self):

        popup_w, popup_h = self.largura_tela * 0.4, self.altura_tela * 0.5
        self.popup_entrar_rect = pygame.Rect(0, 0, popup_w, popup_h)
        self.popup_entrar_rect.center = (self.largura_tela // 2, self.altura_tela // 2)
        self.popup_entrar_label = self.fonte_padrao.render("Entrar na Sala", True, self.cor_texto)
        self.popup_entrar_label_rect = self.popup_entrar_label.get_rect(
            center=(self.popup_entrar_rect.centerx, self.popup_entrar_rect.top + popup_h * 0.15))
        input_h = popup_h * 0.15
        self.input_entrar_senha = TextInput(self.popup_entrar_rect.x + popup_w * 0.1, self.popup_entrar_rect.y + popup_h * 0.45, popup_w * 0.8, input_h,
                                            font_obj=self.fonte_padrao, placeholder="Digite a senha da sala")
        btn_h = popup_h * 0.18
        self.btn_entrar_ok = Button(self.popup_entrar_rect.x + popup_w * 0.1, self.popup_entrar_rect.y + popup_h * 0.75, popup_w * 0.35, btn_h,
                                    "ENTRAR", font_obj=self.fonte_padrao)
        self.btn_entrar_cancel = Button(self.popup_entrar_rect.x + popup_w * 0.55, self.popup_entrar_rect.y + popup_h * 0.75, popup_w * 0.35, btn_h,
                                        "CANCELAR", font_obj=self.fonte_padrao)

    def handle_events(self, events):
        #bridge = game_data['bridge']
        #hub_msg = bridge.get_hub_response()

        # if hub_msg and hub_msg[0:3] == b'LSR':
        #     try:
        #         rooms_dict = pickle.loads(hub_msg)
        #     except Exception:
        #         rooms_dict = {}

                # self._atualizar_lista_salas(self.client.draw_data)
        # else:
            # rooms_dict = {}

        if self.mostrando_popup_criar:
            return self._handle_popup_criar(events)
        
        elif self.mostrando_popup_entrar:
            return self._handle_popup_entrar(events)
        
        for event in events:
            if self.btn_voltar.handle_event(event):
                # return "LOGOUT"
                pass 
            if self.btn_criar_sala.handle_event(event):
                self.mostrando_popup_criar = True
                # game_data['hub_error'] = "" 
                # return "LOBBY"

            for btn_sala in self.botoes_salas:
                if btn_sala.handle_event(event):
                    self.selected_room_name = btn_sala.room_name 
                    self.mostrando_popup_entrar = True
                    # game_data['hub_error'] = ""
                    self.popup_entrar_nome_sala_surf = self.fonte_padrao.render(f"Sala: {self.selected_room_name}", True, self.cor_texto)
                    self.popup_entrar_nome_sala_rect = self.popup_entrar_nome_sala_surf.get_rect(
                        center=(self.popup_entrar_rect.centerx, self.popup_entrar_rect.top + self.popup_entrar_rect.height * 0.3))
                    # return "LOBBY"
        # return "LOBBY"

    def _handle_popup_criar(self, events):
        for event in events:
            self.input_criar_nome.handle_event(event)
            self.input_criar_senha.handle_event(event)
            if self.btn_players_2.handle_event(event):
                self.popup_player_count = 2
            if self.btn_players_4.handle_event(event):
                self.popup_player_count = 4
            if self.btn_criar_ok.handle_event(event):
                nome_sala = self.input_criar_nome.text
                senha_sala = self.input_criar_senha.text
                if nome_sala:
                    # msg = f'CRT{nome_sala}\n{senha_sala}\n{self.popup_player_count}'.encode()
                    # bridge.send_to_hub(msg)
                    self.mostrando_popup_criar = False
                    self._limpar_popups()
                    return f'CRT{nome_sala}\n{senha_sala}\n{self.popup_player_count}'
            if self.btn_criar_cancel.handle_event(event):
                self.mostrando_popup_criar = False
                self._limpar_popups()
        # return "LOBBY"

    def _handle_popup_entrar(self, events):
        for event in events:
            self.input_entrar_senha.handle_event(event)
            if self.btn_entrar_ok.handle_event(event):
                senha_digitada = self.input_entrar_senha.text
                if self.selected_room_name:
                    #msg = f'CCT{self.selected_room_name}\n{senha_digitada}'.encode()
                    #bridge.send_to_hub(msg)
                    self.mostrando_popup_entrar = False
                    srm = self.selected_room_name
                    self._limpar_popups()
                    return f'CCT{srm}\n{senha_digitada}'
            if self.btn_entrar_cancel.handle_event(event):
                self.mostrando_popup_entrar = False
                self._limpar_popups()
        #return "LOBBY"

    def _limpar_popups(self):
        self.input_criar_nome.text = ""
        self.input_criar_senha.text = ""
        self.input_entrar_senha.text = ""
        self.selected_room_name = None
        self.popup_player_count = 4

    def _atualizar_lista_salas(self, rooms):
        self.botoes_salas = []
        self.label_lista_vazia = None
        y_pos = self.lista_y_start 
        x_pos = self.rect_painel_direita.centerx
        btn_width = self.rect_painel_direita.width * 0.8
        btn_height = self.altura_tela * 0.08
        if not rooms:
            self.label_lista_vazia = self.fonte_padrao.render("Nenhuma sala encontrada.", True, self.cor_texto)
            self.label_lista_vazia_rect = self.label_lista_vazia.get_rect(center=(x_pos, y_pos + 50))
            return
        for room_name in rooms:
            text = f"{room_name}" 
            if len(text) > 20: text = text[:18] + "..."
            btn = Button(
                x=x_pos - (btn_width // 2), y=y_pos, 
                width=btn_width, height=btn_height, 
                text=text, 
                font_obj=self.fonte_pequena 
            )
            btn.room_name = room_name
            self.botoes_salas.append(btn)
            y_pos += btn_height + 15

    def draw(self, screen):
        super().draw(screen) 

        pygame.draw.rect(screen, self.cor_box, self.rect_painel_direita, border_radius=10)
        pygame.draw.rect(screen, self.cor_borda, self.rect_painel_direita, border_radius=10, width=3)

        screen.blit(self.titulo_surf, self.titulo_rect)

        self.btn_voltar.draw(screen)
        self.btn_criar_sala.draw(screen)

        for btn in self.botoes_salas:
            btn.draw(screen)

        if self.label_lista_vazia:
            screen.blit(self.label_lista_vazia, self.label_lista_vazia_rect)

        self._atualizar_lista_salas(self.client.draw_data)
        # hub_error = game_data.get('hub_error', '')
        # if hub_error:
        #     if hub_error != self.last_error:
        #         self.last_error = hub_error
        #         self.error_surf = self.fonte_pequena.render(hub_error, True, self.cor_erro)
        #         self.error_rect = self.error_surf.get_rect(center=(self.rect_painel_central.centerx, self.rect_painel_central.bottom - self.margem))
        #     if self.error_surf:
        #         screen.blit(self.error_surf, self.error_rect)
        # else:
        #     self.last_error = ""

        if self.mostrando_popup_criar:
            self._draw_popup_criar(screen)

        elif self.mostrando_popup_entrar:
            self._draw_popup_entrar(screen)
    
    def _draw_overlay(self, screen):
        overlay = pygame.Surface((self.largura_tela, self.altura_tela), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

    def _draw_popup_criar(self, screen):
        self._draw_overlay(screen)
        pygame.draw.rect(screen, self.cor_box, self.popup_rect, border_radius=10)
        pygame.draw.rect(screen, self.cor_borda, self.popup_rect, border_radius=10, width=3)
        screen.blit(self.popup_criar_label, self.popup_criar_label_rect)
        self.input_criar_nome.draw(screen)

        self.input_criar_senha.draw(screen)

        self.btn_players_2.cor_atual = self.btn_players_2.color_normal
        self.btn_players_2.text_color_atual = self.btn_players_2.text_color_normal

        self.btn_players_4.cor_atual = self.btn_players_4.color_normal
        self.btn_players_4.text_color_atual = self.btn_players_4.text_color_normal

        if self.popup_player_count == 2:
            self.btn_players_2.cor_atual = self.btn_players_2.color_hover
            self.btn_players_2.text_color_atual = self.btn_players_2.text_color_hover
        elif self.popup_player_count == 4:
            self.btn_players_4.cor_atual = self.btn_players_4.color_hover
            self.btn_players_4.text_color_atual = self.btn_players_4.text_color_hover
        screen.blit(self.popup_jogadores_label, self.popup_jogadores_label_rect)
        self.btn_players_2.draw(screen)
        self.btn_players_4.draw(screen)
        self.btn_criar_ok.draw(screen)
        self.btn_criar_cancel.draw(screen)

    def _draw_popup_entrar(self, screen):
        self._draw_overlay(screen)
        pygame.draw.rect(screen, self.cor_box, self.popup_entrar_rect, border_radius=10)
        pygame.draw.rect(screen, self.cor_borda, self.popup_entrar_rect, border_radius=10, width=3)
        screen.blit(self.popup_entrar_label, self.popup_entrar_label_rect)
        screen.blit(self.popup_entrar_nome_sala_surf, self.popup_entrar_nome_sala_rect) 
        self.input_entrar_senha.draw(screen)
        self.btn_entrar_ok.draw(screen)
        self.btn_entrar_cancel.draw(screen)
