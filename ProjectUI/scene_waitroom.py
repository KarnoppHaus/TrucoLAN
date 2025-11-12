import pygame
import math
import pickle
from .base_screen import BaseScreen, Button

class SceneWaitRoom(BaseScreen):
    STATE_NAME = "WAITROOM"

    def __init__(self, screen_width, screen_height, client):
        self.client = client

        super().__init__(screen_width, screen_height)

        # self.conectado_a_sala = False

        # self.is_ready = False
        # self.meu_id_selecionado = -1
        # self.max_players = 0

        self.titulo_surf = self.fonte_titulo.render("Aguardando Jogadores", True, self.cor_texto)
        self.titulo_rect = self.titulo_surf.get_rect(
            center=(self.largura_tela // 2, self.altura_tela * 0.15)
        )

        self.btn_voltar = Button(
            x=self.margem, y=self.margem,
            width=self.largura_tela * 0.1, height=self.altura_tela * 0.07,
            text="< Voltar", font_obj=self.fonte_pequena
        )

        btn_pronto_w = self.largura_tela * 0.25
        btn_pronto_h = self.altura_tela * 0.1
        self.btn_pronto = Button(
            x=self.largura_tela // 2 - (btn_pronto_w // 2),
            y=self.altura_tela * 0.8,
            width=btn_pronto_w, height=btn_pronto_h,
            text="PRONTO", font_obj=self.fonte_padrao
        )

        self.btn_pronto_original_rect = self.btn_pronto.rect.copy()
        self.botoes_slots = []
        # self.msg_status = "Conectando..."
        self.players_snapshot = []

    def _criar_slots_dinamicos(self):
        self.botoes_slots = []
        slot_width = self.largura_tela * 0.3
        slot_height = self.altura_tela * 0.2
        
        if self.max_players == 2:
            posicoes = [
                (self.largura_tela * 0.35, self.altura_tela * 0.5),
                (self.largura_tela * 0.65, self.altura_tela * 0.5)
            ]
        
        else:
            offset_x = self.largura_tela * 0.18
            offset_y = self.altura_tela * 0.14
            grid_center_x = self.largura_tela // 2
            grid_center_y = self.altura_tela // 2
            posicoes = [
                (grid_center_x - offset_x, grid_center_y - offset_y),
                (grid_center_x + offset_x, grid_center_y - offset_y),
                (grid_center_x - offset_x, grid_center_y + offset_y),
                (grid_center_x + offset_x, grid_center_y + offset_y)
            ]
        
        for i in range(len(self.client.draw_data)):
            pos = posicoes[i]
            btn = Button(
                x=pos[0] - slot_width // 2, y=pos[1] - slot_height // 2,
                width=slot_width, height=slot_height,
                text=f"Slot {i}",
                font_obj=self.fonte_padrao
            )
            btn.slot_id = i
            self.botoes_slots.append(btn)

    # def handle_events(self, events):
    #     # bridge = game_data['bridge']
    #     # username = user
    #     # room_port = game_data.get('room_port')
    #     players_data = self.players_snapshot

    #     if room_port is not None and not self.conectado_a_sala:
    #         try:
    #             bridge.connect_to_room(bridge.hub_host, room_port, username)
    #             self.conectado_a_sala = True
    #             game_data['room_port'] = None
    #             self.msg_status = "Conectado. Escolha seu lugar e clique PRONTO."
    #             self.meu_id_selecionado = -1
    #         except Exception:
    #             game_data['hub_error'] = "Falha ao conectar na sala."
    #             return "LOBBY"
    #         return "WAITROOM"

    #     # Ouve mensagens de prontidão da sala
    #     # msg = bridge.get_room_message()
    #     # if msg:
    #         # if msg == b'0':
    #         #     self.msg_status = "Aguardando todos ficarem prontos..."
    #         # elif msg == b'1':
    #         #     return "GAME"
    #         # else:
    #     try:
    #         # data = pickle.loads(msg)
    #         if isinstance(data, dict):
    #             # Atualiza "snapshot" dos jogadores
    #             self.players_snapshot = self.client.draw_data#data.get('players', [])
    #             maxp = data.get('max_players', len(self.players_snapshot))
    #             if maxp > 0 and maxp != self.max_players:
    #                 self.max_players = maxp
    #                 self._criar_slots_dinamicos()
    #     except Exception:
    #         pass

    #     for event in events:
    #         # if self.btn_voltar.handle_event(event):
    #         #     return "LOGOUT"

    #         if not self.is_ready:
    #             for btn_slot in self.botoes_slots:
    #                 if btn_slot.handle_event(event):
    #                     self.meu_id_selecionado = btn_slot.slot_id
    #                     self.msg_status = f"Você escolheu o Slot {self.meu_id_selecionado}."
    #                     # bridge.send_ready_status(self.meu_id_selecionado, 0)
    #         if self.btn_pronto.handle_event(event):
    #             if self.meu_id_selecionado == -1:
    #                 for i, player in enumerate(players_data):
    #                     if username == player.get('name'):
    #                         self.meu_id_selecionado = i
    #                         break
    #                 if self.meu_id_selecionado == -1:
    #                     self.msg_status = "ERRO: O servidor ainda não te alocou!"
    #                 else:
    #                     self.is_ready = not self.is_ready
    #                     bridge.send_ready_status(self.meu_id_selecionado, int(self.is_ready))
    #             else:
    #                 self.is_ready = not self.is_ready
    #                 bridge.send_ready_status(self.meu_id_selecionado, int(self.is_ready))
    #     # return "WAITROOM"

    def handle_events(self, events):
        for event in events:
            # if self.btn_voltar.handle_event(event):
            #     return 

            if self.btn_pronto.handle_event(event):
                return 
            
            for btn_slot in self.botoes_slots:
                if btn_slot.handle_event(event):
                    return 
                
        return None

    def draw(self, screen):
        try:
            super().draw(screen)
            players_data = self.players_snapshot
            if self.max_players > 0 and len(self.botoes_slots) != self.max_players:
                self._criar_slots_dinamicos()
            screen.blit(self.titulo_surf, self.titulo_rect)
            self.btn_voltar.draw(screen)

            if self.is_ready:
                self.btn_pronto.text = "ESPERANDO..."
                self.btn_pronto.rect = self.btn_pronto_original_rect.copy()
            else:
                self.btn_pronto.text = "PRONTO"
                self.btn_pronto.rect = self.btn_pronto_original_rect.copy()
                if self.meu_id_selecionado != -1:
                    pulse = 1.0 + (math.sin(pygame.time.get_ticks() * 0.006) * 0.05)
                    new_width = self.btn_pronto_original_rect.width * pulse
                    new_height = self.btn_pronto_original_rect.height * pulse
                    self.btn_pronto.rect.width = new_width
                    self.btn_pronto.rect.height = new_height
                    self.btn_pronto.rect.center = self.btn_pronto_original_rect.center
            self.btn_pronto.draw(screen)

            for i, btn_slot in enumerate(self.botoes_slots):
                if i >= len(players_data):
                    btn_slot.text = f"Slot {i} Vazio"
                    btn_slot.border_color = self.cor_borda
                    btn_slot.border_width = 3
                    btn_slot.draw(screen)
                    continue
                player_info = players_data[i]
                is_occupied = bool(player_info.get('name'))
                is_ready = player_info.get('ready')
                slot_name = player_info.get('name') if is_occupied else f"Slot {i} Vazio"
                btn_slot.text = slot_name
                if is_occupied and player_info.get('name') == game_data['username']:
                    btn_slot.border_color = (0, 200, 0)
                    btn_slot.border_width = 5
                elif is_occupied:
                    btn_slot.border_color = (200, 200, 0) if is_ready else (200, 0, 0)
                    btn_slot.border_width = 3
                else:
                    btn_slot.border_color = self.cor_borda
                    btn_slot.border_width = 3
                btn_slot.draw(screen)

            if self.msg_status:
                status_color = self.cor_erro if "Falha" in self.msg_status else self.cor_texto
                status_surf = self.fonte_pequena.render(self.msg_status, True, status_color)
                status_rect = status_surf.get_rect(center=(self.largura_tela // 2, self.altura_tela * 0.9))
                screen.blit(status_surf, status_rect)
        except Exception as e:
            print("Erro no draw da SceneWaitRoom:", e)
