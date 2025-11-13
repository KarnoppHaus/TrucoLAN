import pygame
import os
from .base_screen import BaseScreen, Button

class SceneGame(BaseScreen):
    
    def __init__(self, screen_width, screen_height, client):
        self.client = client
        self.__screen_z_index = 0
        self.mostrando_envido = False

        super().__init__(screen_width, screen_height)

        # Área do placar
        self.placar_rect = pygame.Rect(self.largura_tela * 0.75, self.margem, 
                                       self.largura_tela * 0.2, self.altura_tela * 0.1)
        
        self.cartas_imgs = {}
        for filename in os.listdir("ProjectUI/assets/cards_png"):
            if filename.endswith(".png"):
                nome = os.path.splitext(filename)[0]
                caminho = os.path.join("ProjectUI/assets/cards_png", filename)
                self.cartas_imgs[nome] = pygame.image.load(caminho).convert_alpha()

        btn_w = self.largura_tela * 0.15
        btn_h = self.altura_tela * 0.08
        btn_x = self.margem
        btn_y_start = self.altura_tela * 0.3
        self.btn_truco = Button(btn_x, btn_y_start, btn_w, btn_h, "TRUCO!", font_obj=self.fonte_padrao)
        self.btn_envido = Button(btn_x, btn_y_start + btn_h + 10, btn_w, btn_h, "ENVIDO", font_obj=self.fonte_padrao)
        self.btn_flor = Button(btn_x, btn_y_start + 2 * (btn_h + 10), btn_w, btn_h, "FLOR", font_obj=self.fonte_padrao)
        self.btn_baralho = Button(btn_x, btn_y_start + 3 * (btn_h + 10), btn_w, btn_h, "BARALHO", font_obj=self.fonte_padrao)

        self._chamar_envido_popup()

    def _chamar_envido_popup(self):
        popup_w, popup_h = self.largura_tela * 0.4, self.altura_tela * 0.6
        self.popup_rect = pygame.Rect(0, 0, popup_w, popup_h)
        self.popup_rect.center = (self.largura_tela // 2, self.altura_tela // 2)

        btn_w = popup_w * 0.4
        btn_h = popup_h * 0.12

        self.btn_call_envido = Button(
            self.popup_rect.x + popup_w * 0.1,
            self.popup_rect.y + popup_h * 0.4,
            btn_w, btn_h,
            "ENVIDO", font_obj=self.fonte_pequena, z_index=1
        )

        self.btn_call_real_envido = Button(
            self.popup_rect.x + popup_w * 0.55,
            self.popup_rect.y + popup_h * 0.4,
            btn_w, btn_h,
            "REAL ENVIDO", font_obj=self.fonte_pequena, z_index=1
        )

        self.btn_call_falta_envido = Button(
            self.popup_rect.x + popup_w * 0.1,
            self.popup_rect.y + popup_h * 0.55,
            btn_w, btn_h,
            "FALTA ENVIDO", font_obj=self.fonte_pequena, z_index=1
        )

        self.btn_cancel_call_envido = Button(
            self.popup_rect.x + popup_w * 0.55,
            self.popup_rect.y + popup_h * 0.55,
            btn_w, btn_h,
            "CANCELAR", font_obj=self.fonte_pequena, z_index=1
        )

    def _handle_chamar_envido_popup(self, events):
        self.__screen_z_index = 1
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if self.btn_cancel_call_envido.handle_event(event, z_index=1):
                self.mostrando_envido = False
                self._limpar_popups()
                        
            elif self.btn_call_envido.handle_event(event, z_index=1):
                self.mostrando_envido = False
                self._limpar_popups()
                return "ENV"
                        
            elif self.btn_call_real_envido.handle_event(event, z_index=1):
                self.mostrando_envido = False
                self._limpar_popups()
                return "REN"
                        
            elif self.btn_call_falta_envido.handle_event(event, z_index=1):
                self.mostrando_envido = False
                self._limpar_popups()
                return "FEN"

    def _limpar_popups(self):
        self.__screen_z_index = 0

    # Atualiza as cartas do jogador
    def atualizar_mao(self):
        mao = self.client.infos_dict.get("cards", [])
        for i, carta in enumerate(mao):
            if i < len(self.botoes_cartas):
                self.botoes_cartas[i]["carta"] = carta

    def handle_events(self, events):
        if self.mostrando_envido:
            return self._handle_chamar_envido_popup(events)

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if self.client.to_do == "MOV":
                    if self.btn_truco.handle_event(event):
                        print("TRUCO")
                        return "TRC"
                            
                    elif self.btn_envido.handle_event(event):
                        self.mostrando_envido = True
                        return None
                        
                    elif self.btn_flor.handle_event(event):
                        return "CCF"
                    
                    for botao in self.botoes_cartas:
                        if botao["rect"].collidepoint(mouse_pos) and botao["carta"] and self.client.to_do == 'MOV':
                            carta = botao["carta"]
                            comando = f"MOV {carta}"
                            return comando
                        
                    


    def draw(self, screen):
        super().draw(screen)
        self.draw_layout(screen)

        # === Placar ===
        pygame.draw.rect(screen, self.cor_box, self.placar_rect, border_radius=10)
        pygame.draw.rect(screen, self.cor_borda, self.placar_rect, border_radius=10, width=3)
        placar_txt = self.fonte_pequena.render("NÓS: 0", True, self.cor_texto)
        placar_txt_eles = self.fonte_pequena.render("ELES: 0", True, self.cor_texto)
        screen.blit(placar_txt, (self.placar_rect.x + 10, self.placar_rect.y + 10))
        screen.blit(placar_txt_eles, (self.placar_rect.x + 10, self.placar_rect.y + 45))

        # === Cartas da mesa (4 jogadores) ===
        for pos, data in self.slots_mesa.items():
            rect = data["rect"]
            nome = data["nome"]

            # desenhar carta se existir
            carta_nome = self.cartas_mesa.get(pos)
            if carta_nome:
                img = pygame.transform.scale(self.cartas_imgs[carta_nome], (rect.width, rect.height))
                screen.blit(img, rect.topleft)
            else:
                pygame.draw.rect(screen, (200, 180, 150), rect, border_radius=8)
                pygame.draw.rect(screen, (60, 40, 20), rect, 2, border_radius=8)

            # desenhar nome do jogador
            nome_surf = self.fonte_padrao.render(nome, True, (0, 0, 0))
            nome_rect = nome_surf.get_rect(midtop=(rect.centerx, rect.bottom + 5))
            screen.blit(nome_surf, nome_rect)


        # === Cartas do jogador ===
        for botao in self.botoes_cartas:
            rect = botao["rect"]
            carta_nome = botao["carta"]
            if carta_nome:
                img = pygame.transform.scale(self.cartas_imgs[carta_nome], (rect.width, rect.height))
                screen.blit(img, rect.topleft)
            else:
                pygame.draw.rect(screen, (80, 80, 80), rect, 2)

        # === Baralho ===
        baralho_img_scaled = pygame.transform.scale(self.baralho_img, (self.baralho_rect.width, self.baralho_rect.height))
        screen.blit(baralho_img_scaled, self.baralho_rect.topleft)

    def _draw_overlay(self, screen):
        overlay = pygame.Surface((self.largura_tela, self.altura_tela), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

    def _draw_envido_popup(self, screen):
        # Fundo escurecido atrás do popup
        self._draw_overlay(screen)

        # Caixa principal do popup
        pygame.draw.rect(screen, self.cor_box, self.popup_rect, border_radius=10)
        pygame.draw.rect(screen, self.cor_borda, self.popup_rect, border_radius=10, width=3)

        # Título
        popup_title = self.fonte_padrao.render("Chamar Envido", True, self.cor_texto)
        popup_title_rect = popup_title.get_rect(center=(self.popup_rect.centerx, self.popup_rect.top + self.popup_rect.height * 0.1))
        screen.blit(popup_title, popup_title_rect)

        # Subtítulo opcional
        popup_sub = self.fonte_pequena.render("Escolha uma opção:", True, self.cor_texto)
        popup_sub_rect = popup_sub.get_rect(center=(self.popup_rect.centerx, self.popup_rect.top + self.popup_rect.height * 0.25))
        screen.blit(popup_sub, popup_sub_rect)

        # Desenha os 4 botões
        self.btn_call_envido.draw(screen, self.__screen_z_index)
        self.btn_call_real_envido.draw(screen, self.__screen_z_index)
        self.btn_call_falta_envido.draw(screen, self.__screen_z_index)
        self.btn_cancel_call_envido.draw(screen, self.__screen_z_index)


    def draw_layout(self, screen):
        # Draw Envido Popup
        if self.mostrando_envido:
            self._draw_envido_popup(screen)

        # Botões laterais
        if self.client.to_do == 'MOV':
            # === Botões laterais ===
            for btn in [self.btn_truco, self.btn_envido, self.btn_flor, self.btn_baralho]:
                btn.draw(screen, self.__screen_z_index)

        # Slots de cartas do jogador
        card_w, card_h = 100, 150
        hand_y = self.altura_tela - card_h - self.margem
        hand_x_start = self.largura_tela // 2 - card_w - 60
        self.botoes_cartas = []
        for i, card in enumerate(self.client.infos_dict['cards']):
            self.botoes_cartas.append(
                {'rect': pygame.Rect(hand_x_start + i*(card_w+20), hand_y, card_w, card_h), 'carta': card}
                )

        # --- Na __init__ ---
        self.slots_mesa = {
            "baixo": {"rect": pygame.Rect(self.largura_tela//2 - 50, self.altura_tela - 370, 100, 150), "nome": "Você"},
            "cima": {"rect": pygame.Rect(self.largura_tela//2 - 50, 100, 100, 150), "nome": "Jogador Cima"},
            "esquerda": {"rect": pygame.Rect(280, self.altura_tela//2 - 115, 100, 150), "nome": "Jogador Esq"},
            "direita": {"rect": pygame.Rect(self.largura_tela - 380, self.altura_tela//2 - 115, 100, 150), "nome": "Jogador Dir"},
        }

        # Caso queira associar uma carta temporária pra teste:
        self.cartas_mesa = {
            "baixo": "1_espadas",
            "cima": "7_ouros",
            "esquerda": "3_copas",
            "direita": "k_paus"
        }
        #---------------------- teste

        # Baralho (imagem virada)
        self.baralho_img = pygame.image.load("ProjectUI/assets/cards_png/j_ouros.png").convert_alpha()
        self.baralho_rect = pygame.Rect(self.largura_tela - 150, self.altura_tela - 200, 100, 150)
