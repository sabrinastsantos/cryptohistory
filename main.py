import pygame
import pygame_gui

pygame.init()

# Constantes
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
TEMPO_LOADING = 9000
TEMPO_PISCADA = 500
TEMPO_MOSTRA_RESPOSTA = 3000

# Tela e fonte
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Biblioteca")
font_instrucao = pygame.font.Font(None, 24)

# Gerenciador para controle
ui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# Estados do jogo
MENU, PLAYING, FASE2 = 0, 1, 2
estado_jogo = MENU

# Botão inicial
start_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 25), (150, 50)),
    text='Start Game',
    manager=ui_manager
)

# Botão para andar
botao_cima = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((SCREEN_WIDTH - 60, 200), (40, 40)),
    text='UP',
    manager=ui_manager
)
botao_cima.hide()

# Carregamento de imagem
def carregar_e_escalar(caminho):
    try:
        img = pygame.image.load(caminho).convert()
        return pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        return None

# Imagens
background_image = carregar_e_escalar('imagens/start.png')
game_image = carregar_e_escalar('imagens/tela_inicial.png')
fase2_image = carregar_e_escalar('imagens/lib_sala1.png')
enigma1_img = carregar_e_escalar('imagens/enigma1.png')
resp_enigma1 = carregar_e_escalar('imagens/resp_enigma1.png')
enigma2_img = carregar_e_escalar('imagens/enigma2.png')
resp_enigma2 = carregar_e_escalar('imagens/resp_enigma2.png')
lib_sala2_image = carregar_e_escalar('imagens/lib_sala2.png')
enigma3_img = carregar_e_escalar('imagens/enigma3.png')
resp_enigma3 = carregar_e_escalar('imagens/resp_enigma3.png')
enigma4_img = carregar_e_escalar('imagens/enigma4.png')
resp_enigma4 = carregar_e_escalar('imagens/resp_enigma4.png')
enigma_final_img = carregar_e_escalar('imagens/enigma_final.png')

# Sons
pygame.mixer.music.load('sons/vento.mp3')
pygame.mixer.music.set_volume(0.5)
som_passo = pygame.mixer.Sound('sons/passos.mp3')
som_porta = pygame.mixer.Sound('sons/porta.mp3')

# Classe para enigmas
class Enigma:
    def __init__(self, rect, certas, imagem_enigma, imagem_resposta, cor_brilho):
        self.rect = rect
        self.respostas_certas = set(certas)
        self.respostas_clicadas = set()
        self.botoes = []
        self.botao = None
        self.aberto = False
        self.finalizado = False
        self.mostrar_resposta = False
        self.tempo_resposta = 0
        self.imagem_enigma = imagem_enigma
        self.imagem_resposta = imagem_resposta
        self.mostrar_destaque = False
        self.cor_brilho = cor_brilho

    def criar_botao(self):
        self.botao = pygame_gui.elements.UIButton(
            relative_rect=self.rect,
            text='',
            manager=ui_manager,
            tool_tip_text='Clique para abrir o livro'
        )

    def criar_botoes_resposta(self, opcoes):
        espaco = 80
        x_ini = 170
        y_ini = 520
        for i, valor in enumerate(opcoes):
            botao = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((x_ini + i * espaco, y_ini), (60, 40)),
                text=str(valor),
                manager=ui_manager
            )
            self.botoes.append(botao)

    def verificar_resposta(self, event):
        for botao in self.botoes:
            if event.ui_element == botao:
                valor = int(botao.text)
                self.respostas_clicadas.add(valor)
                if self.respostas_certas.issubset(self.respostas_clicadas):
                    self.finalizado = True
                    self.mostrar_resposta = True
                    self.tempo_resposta = pygame.time.get_ticks()
                    for b in self.botoes:
                        b.kill()
                    self.botoes.clear()

    def desenhar_brilho(self):
        global mostrar_brilho, tempo_piscada
        if pygame.time.get_ticks() - tempo_piscada > TEMPO_PISCADA:
            mostrar_brilho = not mostrar_brilho
            tempo_piscada = pygame.time.get_ticks()
        if mostrar_brilho:
            brilho_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            brilho_surface.fill(self.cor_brilho)
            screen.blit(brilho_surface, self.rect.topleft)

# Instâncias dos enigmas
enigma1 = Enigma(pygame.Rect(247, 438, 8, 30), [16, 25], enigma1_img, resp_enigma1, (255, 255, 0, 100))
enigma2 = Enigma(pygame.Rect(535, 310, 10, 30), [1, 8, 20], enigma2_img, resp_enigma2, (255, 255, 0, 100))
enigma3 = Enigma(pygame.Rect(35, 140, 8, 46), [7, 15], enigma3_img, resp_enigma3, (255, 255, 0, 100))
enigma4 = Enigma(pygame.Rect(589, 442, 8, 28), [18, 1], enigma4_img, resp_enigma4, (255, 255, 0, 100))
enigma_final = Enigma(pygame.Rect(699, 265, 12, 43), [9], enigma_final_img, None, (255, 255, 0, 100))
porta2 = pygame.Rect(379, 347, 24, 28)
porta2_botao = None
porta2_destaque = False
porta2_aberta = False

# Variáveis
porta_rect = pygame.Rect(340, 200, 120, 200)
porta_aberta = False
zoom_scale, zoom_step, max_zoom = 1.0, 0.02, 2.5
mostrar_brilho = True
mostra_instrucao = True
mostra_instrucao_fase2 = True
loading_start = 0
tempo_piscada = 0
clock = pygame.time.Clock()
running = True
enigma2_pode_aparecer = False
porta2_pode_abrir = False
porta2_aberta = False
porta2_destaque = False
botao_porta2 = None
loading2_start = 0  # loading para a porta 2


# Loop principal
while running:
    time_delta = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        ui_manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == start_button and estado_jogo == MENU:
                estado_jogo = PLAYING
                pygame.mixer.music.play(-1)
                botao_cima.show()
                start_button.kill()

            elif event.ui_element == botao_cima and estado_jogo == PLAYING:
                if zoom_scale < max_zoom:
                    zoom_scale += zoom_step
                    som_passo.play()
                    mostra_instrucao = False

            elif estado_jogo == FASE2:
                if event.ui_element == enigma1.botao and not enigma1.aberto:
                    enigma1.aberto = True
                    mostra_instrucao_fase2 = False
                    enigma1.botao.kill()
                    enigma1.criar_botoes_resposta([16, 17, 19, 24, 25, 27])

                elif event.ui_element == enigma2.botao and not enigma2.aberto:
                    enigma2.aberto = True
                    enigma2.botao.kill()
                    enigma2.criar_botoes_resposta([1, 5, 8, 12, 20, 23])
                # Clique no botão da porta da fase 2
                elif event.ui_element == botao_porta2 and not porta2_aberta:
                    porta2_aberta = True
                    som_porta.play()
                    botao_porta2.kill()
                    botao_porta2 = None
                    porta2_destaque = False
                    loading2_start = pygame.time.get_ticks()  # tempo de loading...
                elif event.ui_element == enigma3.botao and not enigma3.aberto:
                    enigma3.aberto = True
                    enigma3.botao.kill()
                    enigma3.criar_botoes_resposta([5, 7, 9, 14, 15, 17])
                elif event.ui_element == enigma4.botao and not enigma4.aberto:
                    enigma4.aberto = True
                    enigma4.botao.kill()
                    enigma4.criar_botoes_resposta([1, 2, 3, 16, 18, 21])
                elif event.ui_element == enigma_final.botao and not enigma_final.aberto:
                    enigma_final.aberto = True
                    enigma_final.botao.kill()
                    enigma_final.finalizado = True
                    enigma_final.mostrar_resposta = True
                    enigma_final.tempo_resposta = pygame.time.get_ticks()


                if not enigma1.finalizado:
                    enigma1.verificar_resposta(event)
                if not enigma2.finalizado:
                    enigma2.verificar_resposta(event)
                if not enigma3.finalizado:
                    enigma3.verificar_resposta(event)
                if not enigma4.finalizado:
                    enigma4.verificar_resposta(event)

        elif event.type == pygame.MOUSEBUTTONDOWN and estado_jogo == PLAYING:
            if game_image and not porta_aberta:
                new_width = int(game_image.get_width() * zoom_scale)
                new_height = int(game_image.get_height() * zoom_scale)
                offset_x = (SCREEN_WIDTH - new_width) // 2
                offset_y = (SCREEN_HEIGHT - new_height) // 2
                mouse_x, mouse_y = event.pos
                rel_x = int((mouse_x - offset_x) / zoom_scale)
                rel_y = int((mouse_y - offset_y) / zoom_scale)
                if porta_rect.collidepoint(rel_x, rel_y):
                    porta_aberta = True
                    loading_start = pygame.time.get_ticks()
                    som_porta.play()
                    pygame.mixer.music.stop()
                    botao_cima.hide()

    ui_manager.update(time_delta)

    if estado_jogo == MENU:
        screen.blit(background_image, (0, 0)) if background_image else screen.fill(BLACK)

    elif estado_jogo == PLAYING:
        if game_image:
            new_width = int(game_image.get_width() * zoom_scale)
            new_height = int(game_image.get_height() * zoom_scale)
            zoomed_image = pygame.transform.smoothscale(game_image, (new_width, new_height))
            offset_x = (SCREEN_WIDTH - new_width) // 2
            offset_y = (SCREEN_HEIGHT - new_height) // 2
            screen.blit(zoomed_image, (offset_x, offset_y))
        else:
            screen.fill(WHITE)

        if mostra_instrucao:
            pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
            texto = font_instrucao.render("Descubra o enigma! Mova para encontrar vestígios!", True, WHITE)
            screen.blit(texto, (10, SCREEN_HEIGHT - 30))

        if porta_aberta:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(180)
            s.fill(BLACK)
            screen.blit(s, (0, 0))
            font_loading = pygame.font.Font(None, 48)
            texto_loading = font_loading.render("Loading...", True, WHITE)
            texto_rect = texto_loading.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(texto_loading, texto_rect)
            if pygame.time.get_ticks() - loading_start > TEMPO_LOADING:
                estado_jogo = FASE2
                enigma1.mostrar_destaque = True
                enigma1.criar_botao()

    elif estado_jogo == FASE2:
        if enigma1.aberto and enigma1.imagem_enigma:
            screen.blit(enigma1.imagem_enigma, (0, 0))
        elif enigma2.aberto and enigma2.imagem_enigma:
            screen.blit(enigma2.imagem_enigma, (0, 0))
        elif enigma3.aberto and enigma3.imagem_enigma:
            screen.blit(enigma3.imagem_enigma, (0, 0))
        elif enigma4.aberto and enigma4.imagem_enigma:
            screen.blit(enigma4.imagem_enigma, (0, 0))
        elif enigma_final.aberto and enigma_final.imagem_enigma:
            screen.blit(enigma_final.imagem_enigma, (0, 0))

        else:
            if porta2_aberta:
                tempo_passado = pygame.time.get_ticks() - loading2_start
                if tempo_passado < TEMPO_LOADING:
                    # Tela escura com loading
                    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    s.set_alpha(180)
                    s.fill(BLACK)
                    screen.blit(s, (0, 0))
                    font_loading = pygame.font.Font(None, 48)
                    texto_loading = font_loading.render("Loading...", True, WHITE)
                    texto_rect = texto_loading.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    screen.blit(texto_loading, texto_rect)
                else:
                    screen.blit(lib_sala2_image, (0, 0)) if lib_sala2_image else screen.fill((50, 50, 50))
                    if not enigma3.botao:
                        enigma3.mostrar_destaque = True
                        enigma3.criar_botao()


            else:
                screen.blit(fase2_image, (0, 0)) if fase2_image else screen.fill((30, 30, 30))


        if mostra_instrucao_fase2:
            pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
            texto_fase2 = font_instrucao.render("Explore os livros, através deles poderá descobrir o enigma...", True, WHITE)
            screen.blit(texto_fase2, (10, SCREEN_HEIGHT - 30))

        if enigma1.mostrar_destaque and enigma1.botao and not enigma1.aberto:
            enigma1.desenhar_brilho()
        if enigma2_pode_aparecer and not enigma2.botao:
            enigma2.mostrar_destaque = True
            enigma2.criar_botao()
            enigma2_pode_aparecer = False
        if enigma2.mostrar_destaque and enigma2.botao and not enigma2.aberto:
            enigma2.desenhar_brilho()
        if enigma3.mostrar_destaque and enigma3.botao and not enigma3.aberto:
            enigma3.desenhar_brilho()
        if enigma4.mostrar_destaque and enigma4.botao and not enigma4.aberto:
            enigma4.desenhar_brilho()
        if enigma_final.mostrar_destaque and enigma_final.botao and not enigma_final.aberto:
            enigma_final.desenhar_brilho()

        if enigma1.mostrar_resposta and pygame.time.get_ticks() - enigma1.tempo_resposta < TEMPO_MOSTRA_RESPOSTA:
            screen.blit(enigma1.imagem_resposta, (0, 0))
        elif enigma1.mostrar_resposta:
            enigma1.mostrar_resposta = False
            enigma1.aberto = False
            enigma1.finalizado = False
            enigma2_pode_aparecer = True  # botão 2
            enigma1.mostrar_destaque = False  # desliga o brilho do botão 1
        if enigma2.mostrar_resposta and pygame.time.get_ticks() - enigma2.tempo_resposta < TEMPO_MOSTRA_RESPOSTA:
            screen.blit(enigma2.imagem_resposta, (0, 0))
        elif enigma2.mostrar_resposta:
            enigma2.mostrar_resposta = False
            enigma2.aberto = False
            enigma2.mostrar_destaque = False # desliga o brilho do botão 2
            porta2_destaque = True  # ativa o botão da porta
            enigma2.mostrar_resposta = False
            enigma2.aberto = False
            enigma2.mostrar_destaque = False  # desliga o brilho do botão piscante 2
        # Criar botão piscante da porta após enigma 2 resolvido
        if porta2_destaque and botao_porta2 is None:
            botao_porta2 = pygame_gui.elements.UIButton(
                relative_rect=porta2,
                text='',
                manager=ui_manager,
                tool_tip_text='Abrir a porta'
            )

        if enigma3.mostrar_resposta and pygame.time.get_ticks() - enigma3.tempo_resposta < TEMPO_MOSTRA_RESPOSTA:
            screen.blit(enigma3.imagem_resposta, (0, 0))
        elif enigma3.mostrar_resposta:
            enigma3.mostrar_resposta = False
            enigma3.aberto = False
            enigma3.finalizado = False
            enigma3.mostrar_destaque = False #desliga o brilho botão 1

            # botão do enigma 4
            enigma4.mostrar_destaque = True
            if not enigma4.botao:
                enigma4.criar_botao()

        if enigma4.mostrar_resposta and pygame.time.get_ticks() - enigma4.tempo_resposta < TEMPO_MOSTRA_RESPOSTA:
            screen.blit(enigma4.imagem_resposta, (0, 0))
        elif enigma4.mostrar_resposta:
            enigma4.mostrar_resposta = False
            enigma4.aberto = False
            enigma4.finalizado = False
            enigma4.mostrar_destaque = False
            enigma_final.mostrar_destaque = True
            if not enigma_final.botao:
                enigma_final.criar_botao()

        if enigma_final.mostrar_resposta:
            if enigma_final.imagem_enigma:
                screen.blit(enigma_final.imagem_enigma, (0, 0))
            pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
            texto_final = font_instrucao.render("Parabéns, você concluiu o jogo e descobriu o nome da biblioteca abandonada, Pythagora.", True, WHITE)
            screen.blit(texto_final, (10, SCREEN_HEIGHT - 30))

        elif enigma_final.mostrar_resposta:
            pass


    ui_manager.draw_ui(screen)
    pygame.display.update()

pygame.quit()