import pygame
import math
from .base_screen import BaseScreen, Button, TextInput

class SceneLogin(BaseScreen):
    STATE_NAME = "LOGIN"
    
    def __init__(self, screen_width, screen_height, client):
        self.client = client
        super().__init__(screen_width, screen_height)
        y_center = self.altura_tela // 2

        #titulo
        self.titulo_surf = self.fonte_titulo.render("TrucoLAN", True, self.cor_texto)
        self.titulo_rect = self.titulo_surf.get_rect(
            center=(self.largura_tela * 0.25, y_center)
        )
        input_height = self.altura_tela * 0.08
        btn_width = self.largura_tela * 0.1
        input_width = self.largura_tela * 0.3
        start_x = self.largura_tela * 0.55

        #input box
        self.input_usuario = TextInput(
            x=start_x,
            y=y_center - (input_height // 2),
            width=input_width, 
            height=input_height,
            font_obj=self.fonte_padrao,
            placeholder="Digite seu nome..."
        )

        #botao ok
        self.btn_ok = Button(
            x=self.input_usuario.rect.right + 20, 
            y=self.input_usuario.rect.y,
            width=btn_width, 
            height=input_height, 
            text="OK", 
            font_obj=self.fonte_padrao,
            color_normal=self.cor_input,
            color_hover=self.cor_texto,
            text_color_normal=self.cor_texto,
            text_color_hover=self.cor_input,
            border_color=self.cor_texto
        )

        self.btn_ok_original_rect = self.btn_ok.rect.copy()
        self.status_pos = (start_x, self.input_usuario.rect.bottom + 20) 
        self.msg_erro = "" 

    def handle_events(self, events):
        enter_pressed = False
        button_clicked = False

        for event in events:
            self.input_usuario.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.input_usuario.ativo:
                    enter_pressed = True
            if self.btn_ok.handle_event(event):
                button_clicked = True

        if enter_pressed or button_clicked:
            username = self.input_usuario.text
            return username
        return ""

    def draw(self, screen):
        super().draw(screen) 
        if len(self.input_usuario.text) >= 3:
            pulse = 1.0 + (math.sin(pygame.time.get_ticks() * 0.006) * 0.05)
            new_width = self.btn_ok_original_rect.width * pulse
            new_height = self.btn_ok_original_rect.height * pulse
            self.btn_ok.rect.width = new_width
            self.btn_ok.rect.height = new_height
            self.btn_ok.rect.center = self.btn_ok_original_rect.center
        else:
            self.btn_ok.rect = self.btn_ok_original_rect.copy()
        screen.blit(self.titulo_surf, self.titulo_rect)
        self.input_usuario.draw(screen)
        self.btn_ok.draw(screen)
        if self.msg_erro:
            msg_surf = self.fonte_pequena.render(self.msg_erro, True, self.cor_erro)
            msg_rect = msg_surf.get_rect(left=self.status_pos[0], top=self.status_pos[1])
            screen.blit(msg_surf, msg_rect)
