import pygame
from .base_screen import BaseScreen
import pickle
import cairosvg

class SceneGame(BaseScreen):
    def __init__(self, screen_width, screen_height, client):
        self.client = client
        #sem client só pra teste
        #self.client = client
        super().__init__(screen_width, screen_height)

        # Mesa
        self.mesa_rect = pygame.Rect(self.margem*2, self.margem*2,
                                     self.largura_tela - self.margem*4,
                                     self.altura_tela - self.margem*4)

        # Botão Sair (topo-esquerdo da mesa)
        sair_w = int(self.mesa_rect.w * 0.18)
        sair_h = int(self.altura_tela * 0.07)
        self.btn_sair = pygame.Rect(self.mesa_rect.x + self.margem,
                                    self.mesa_rect.y + self.margem,
                                    sair_w, sair_h)

        # Coluna de botões à esquerda (dentro da mesa)
        col_w = int(self.mesa_rect.w * 0.22)
        col_x = self.mesa_rect.x + self.margem
        col_y0 = self.btn_sair.bottom + self.margem*2
        esp = int(self.altura_tela * 0.02)
        btn_h_col = int(self.altura_tela * 0.08)
        labels = ["Truco", "Envido", "Flor", "Ir ao baralho"]
        self.btns_esq = [(label, pygame.Rect(col_x, col_y0 + i*(btn_h_col+esp), col_w, btn_h_col))
                         for i, label in enumerate(labels)]

        # Placar no topo direito da mesa
        self.placar_rect = pygame.Rect(self.mesa_rect.right - int(self.mesa_rect.w*0.25) - self.margem,
                                       self.mesa_rect.y + self.margem,
                                       int(self.mesa_rect.w*0.25),
                                       int(self.altura_tela*0.10))

        # Tapete + baralho à direita inferior
        tapete_w = int(self.mesa_rect.w * 0.12)
        tapete_h = int(self.mesa_rect.h * 0.35)
        tapete_x = self.mesa_rect.right - self.margem - tapete_w
        tapete_y = self.mesa_rect.bottom - self.margem - tapete_h
        self.tapete_rect = pygame.Rect(tapete_x, tapete_y, tapete_w, tapete_h)

        baralho_w = int(tapete_w*0.7)
        baralho_h = int(tapete_h*0.8)
        self.baralho_rect = pygame.Rect(
            tapete_x + (tapete_w - baralho_w)//2,
            tapete_y + (tapete_h - baralho_h)//2,
            baralho_w, baralho_h
        )

        # Cartas na mesa (3 slots)
        cm_w, cm_h = int(self.mesa_rect.w*0.09), int(self.mesa_rect.h*0.16)
        cx = self.mesa_rect.centerx
        cy = self.mesa_rect.centery - int(self.mesa_rect.h*0.10)
        self.cartas_mesa_rects = [
            pygame.Rect(cx - cm_w - 20, cy, cm_w, cm_h),
            pygame.Rect(cx + 20, cy, cm_w, cm_h),
            pygame.Rect(cx - cm_w//2, cy + cm_h + 20, cm_w, cm_h),
        ]

        # Mão do jogador (3 slots, retos)
        hand_w, hand_h = 100, 150
        hand_gap = 12
        hand_y = self.mesa_rect.bottom - hand_h - self.margem
        hand_x = self.mesa_rect.centerx - (hand_w*3 + hand_gap*2)//2
        self.mao_rects = [
            pygame.Rect(hand_x + i*(hand_w+hand_gap), hand_y, hand_w, hand_h)
            for i in range(3)
        ]

        # Estado visual mínimo
        self.placar_nos = 0
        self.placar_eles = 0
        self.valor_rodada = 1
        self.labels_mao = ["4♦", "7♥", "A♣"]  # apenas para visual
        self.labels_mesa = ["", "", ""]       # preenchidos quando você quiser

        # Hover tracking (opcional, só visual)
        self._hover = None

    # Handlers vazios para plugar depois
    def on_click_sair(self): pass
    def on_click_truco(self): pass
    def on_click_envido(self): pass
    def on_click_flor(self): pass
    def on_click_ir_baralho(self): pass
    def on_click_baralho(self): pass
    def on_click_carta(self, i): pass
    def on_click_mesa_slot(self, k): pass


    def handle_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEMOTION:
                self._hover = e.pos
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                # Sair
                if self.btn_sair.collidepoint(mx, my):
                    self.on_click_sair(); continue
                # Coluna esquerda
                for idx, (label, r) in enumerate(self.btns_esq):
                    if r.collidepoint(mx, my):
                        if idx == 0: self.on_click_truco()
                        elif idx == 1: self.on_click_envido()
                        elif idx == 2: self.on_click_flor()
                        elif idx == 3: self.on_click_ir_baralho()
                        break
                # Baralho
                if self.baralho_rect.collidepoint(mx, my):
                    self.on_click_baralho()
                # Cartas da mão
                for i, r in enumerate(self.mao_rects):
                    if r.collidepoint(mx, my):
                        self.on_click_carta(i); break
                # Slots na mesa
                for k, r in enumerate(self.cartas_mesa_rects):
                    if r.collidepoint(mx, my):
                        self.on_click_mesa_slot(k); break

    def draw(self, screen):
        super().draw(screen)

        # Mesa
        mesa_cor = (175, 137, 88)   # marrom da referência
        pygame.draw.rect(screen, mesa_cor, self.mesa_rect, border_radius=8)
        pygame.draw.rect(screen, self.cor_borda, self.mesa_rect, width=4, border_radius=8)

        # Sair
        pygame.draw.rect(screen, self.cor_box, self.btn_sair, border_radius=20)
        pygame.draw.rect(screen, self.cor_borda, self.btn_sair, width=3, border_radius=20)
        t = self.fonte_padrao.render("← Sair", True, self.cor_texto)
        screen.blit(t, t.get_rect(center=self.btn_sair.center))

        # Placar
        pygame.draw.rect(screen, self.cor_box, self.placar_rect, border_radius=10)
        pygame.draw.rect(screen, self.cor_borda, self.placar_rect, width=3, border_radius=10)
        txt1 = self.fonte_padrao.render(f"NÓS: {self.placar_nos}", True, self.cor_texto)
        txt2 = self.fonte_padrao.render(f"ELES: {self.placar_eles}", True, self.cor_texto)
        screen.blit(txt1, (self.placar_rect.x + 10, self.placar_rect.y + 10))
        screen.blit(txt2, (self.placar_rect.x + 10, self.placar_rect.y + 45))

        # Coluna esquerda
        for label, r in self.btns_esq:
            pygame.draw.rect(screen, self.cor_box, r, border_radius=20)
            pygame.draw.rect(screen, self.cor_borda, r, width=3, border_radius=20)
            t = self.fonte_padrao.render(label, True, self.cor_texto)
            screen.blit(t, t.get_rect(center=r.center))

        # Tapete + baralho
        pygame.draw.rect(screen, (30,110,60), self.tapete_rect, border_radius=8)
        pygame.draw.rect(screen, (200,0,0), self.baralho_rect, border_radius=10)
        pygame.draw.rect(screen, self.cor_borda, self.baralho_rect, width=2, border_radius=10)

        # Cartas na mesa
        for k, r in enumerate(self.cartas_mesa_rects):
            pygame.draw.rect(screen, self.cor_input, r, border_radius=10)
            pygame.draw.rect(screen, self.cor_borda, r, width=2, border_radius=10)
            label = self.labels_mesa[k]
            if label:
                s = self.fonte_pequena.render(label, True, self.cor_texto)
                screen.blit(s, s.get_rect(center=r.center))

        # Mão do jogador
        for i, r in enumerate(self.mao_rects):
            pygame.draw.rect(screen, self.cor_input, r, border_radius=10)
            pygame.draw.rect(screen, self.cor_borda, r, width=2, border_radius=10)
            label = self.labels_mao[i] if i < len(self.labels_mao) else ""
            if label:
                s = self.fonte_pequena.render(label, True, self.cor_texto)
                screen.blit(s, s.get_rect(center=r.center))

        # Hover outline (opcional)
        if self._hover:
            mx, my = self._hover
            for r in [self.btn_sair, *[r for _, r in self.btns_esq],
                      self.baralho_rect, *self.cartas_mesa_rects, *self.mao_rects]:
                if r.collidepoint(mx, my):
                    pygame.draw.rect(screen, (255, 255, 0), r, width=2, border_radius=12)
                    break

if __name__ == "__main__":

    pygame.init()
    W, H = 1280, 720
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Truco - Tela Standalone")

    #pygame.font.init()

    # Cliente dummy só para satisfazer assinatura
    scene = SceneGame(W, H, DummyClient())

    clock = pygame.time.Clock()
    running = True

    while running:
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                events.append(event)

        scene.handle_events(events)
        scene.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()