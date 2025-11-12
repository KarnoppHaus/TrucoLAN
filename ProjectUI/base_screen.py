import pygame
import os

# --- CORES GLOBAIS (Usadas como padrão pelos botões/inputs) ---
COR_TEXTO_VERMELHO = (111, 29, 27)
COR_BEGE_CLARO = (225, 191, 146)
COR_BEGE_INPUT = (240, 228, 210)
COR_FUNDO_HOVER = (111, 29, 27)
COR_TEXTO_HOVER = (240, 228, 210)
# --- FIM CORES ---


# --- CAMINHO DA FONTE ---
# (Certifique-se que o arquivo da fonte está em 'ProjectUI/fonts/')
FONT_PATH = os.path.join('ProjectUI', 'fonts', 'MochiyPopOne-Regular.ttf')


# 
# --- CLASSE MÃE (BaseScreen) ---
#
class BaseScreen:
    """
    A classe "mãe" para todas as telas do jogo.
    Define todas as cores, fontes e layout principal.
    """
    
    STATE_NAME = "BASE" 
    
    def __init__(self, screen_width, screen_height):
        # --- Dimensões ---
        self.largura_tela = screen_width
        self.altura_tela = screen_height
        
        # --- Cores Padrão ---
        self.cor_fundo = (187, 148, 87)       # marrom
        self.cor_texto = (111, 29, 27)        # vermelho escuro
        self.cor_box = (225, 191, 146)        # bege claro
        self.cor_input = (240, 228, 210)      # bege bem clarinho
        self.cor_borda = (111, 29, 27)        # vermelho escuro (borda)
        self.cor_erro = (200, 50, 50)         # Vermelho vivo
        
        self.cor_texto_hover = self.cor_input
        self.cor_fundo_hover = self.cor_texto

        # --- Fontes (Sem verificação) ---
        try:
            self.fonte_titulo = pygame.font.Font(FONT_PATH, self.altura_tela // 10)
            self.fonte_padrao = pygame.font.Font(FONT_PATH, self.altura_tela // 30)
            self.fonte_pequena = pygame.font.Font(FONT_PATH, self.altura_tela // 40)
        except FileNotFoundError:
            print(f"ERRO: Fonte não encontrada em '{FONT_PATH}'")
            print("Usando fontes padrão do Pygame.")
            self.fonte_titulo = pygame.font.Font(None, self.altura_tela // 10)
            self.fonte_padrao = pygame.font.Font(None, self.altura_tela // 30)
            self.fonte_pequena = pygame.font.Font(None, self.altura_tela // 40)


        # --- Layout Proporcional ---
        self.margem = int(self.largura_tela * 0.02)
        
        # Painel da Esquerda/Central (2/3)
        self.largura_central = (self.largura_tela * 2) // 3 - self.margem
        self.altura_painel = self.altura_tela - 2 * self.margem
        self.y_painel = self.margem
        self.x_central = self.margem
        self.rect_painel_central = pygame.Rect(self.x_central, self.y_painel, self.largura_central, self.altura_painel)

        # Painel da Direita (1/3)
        self.largura_direita = self.largura_tela - self.largura_central - 3 * self.margem
        self.x_direita = self.x_central + self.largura_central + self.margem
        self.rect_painel_direita = pygame.Rect(self.x_direita, self.y_painel, self.largura_direita, self.altura_painel)

    def handle_events(self, events, game_data):
        """ Método placeholder para as telas filhas."""
        pass

    def draw(self, screen):
        """ Desenho base (só o fundo)."""
        screen.fill(self.cor_fundo)

#
# --- CLASSES DE UI (No mesmo arquivo) ---
#

class Button:
    """
    Classe de Botão CORRIGIDA.
    A lógica de hover agora está no DRAW.
    """
    def __init__(self, x, y, width, height, text, 
                 font_obj, # Recebe a fonte pronta (ex: self.fonte_padrao)
                 color_normal=COR_BEGE_INPUT, 
                 color_hover=COR_FUNDO_HOVER, 
                 text_color_normal=COR_TEXTO_VERMELHO,
                 text_color_hover=COR_TEXTO_HOVER,
                 border_color=COR_TEXTO_VERMELHO,
                 border_width=3):
        
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font_obj # Usa a fonte recebida
        
        # Cores
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.text_color_normal = text_color_normal
        self.text_color_hover = text_color_hover
        
        # Borda
        self.border_color = border_color
        self.border_width = border_width

    def draw(self, screen):
        """
        Desenha o botão e checa o hover AQUI.
        """
        # --- CORREÇÃO: Lógica de Hover movida para o DRAW ---
        mouse_pos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse_pos)
        
        cor_atual = self.color_hover if hover else self.color_normal
        text_color_atual = self.text_color_hover if hover else self.text_color_normal
        # --- FIM DA CORREÇÃO ---

        # 1. Desenha o fundo
        pygame.draw.rect(screen, cor_atual, self.rect, border_radius=8)
        
        # 2. Desenha a borda
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, self.rect, 
                             width=self.border_width, border_radius=8)
        
        # 3. Desenha o texto
        text_surf = self.font.render(self.text, True, text_color_atual)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        """
        Agora só checa o clique, não mais o movimento.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True # Clicou!
        return False

class TextInput:
    """
    Classe de TextInput (com a lógica de 'clip' corrigida)
    """
    def __init__(self, x, y, width, height, 
                 font_obj, # Recebe a fonte pronta
                 color_bg=COR_BEGE_INPUT, 
                 text_color=COR_TEXTO_VERMELHO,
                 placeholder="",
                 placeholder_color=(160, 140, 110)): # Placeholder marrom
        
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.font = font_obj 
        self.ativo = False
        
        self.color_bg = color_bg
        self.text_color = text_color
        
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.ativo = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN:
            if self.ativo:
                if event.key == pygame.K_RETURN:
                    pass
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self, screen):
        """Desenha a caixa de texto."""
        pygame.draw.rect(screen, self.color_bg, self.rect, border_radius=8)
        
        text_to_render = ""
        color_to_render = self.text_color
        
        if self.text:
            text_to_render = self.text
            color_to_render = self.text_color
        elif not self.ativo:
            text_to_render = self.placeholder
            color_to_render = self.placeholder_color
        
        # Renderiza ANTES de calcular a posição
        text_surf = self.font.render(text_to_render, True, color_to_render)
        
        clip_area_rect = self.rect.inflate(-20, -10) 
        text_pos_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        
        if text_surf.get_width() > clip_area_rect.width:
            text_pos_x = clip_area_rect.right - text_surf.get_width()
        else:
            text_pos_x = clip_area_rect.x
            
        screen.set_clip(clip_area_rect)
        screen.blit(text_surf, (text_pos_x, text_pos_y))
        screen.set_clip(None)