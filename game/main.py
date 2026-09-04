import pygame; 

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x,y,width, height)
        self.text = text
        self.action = action

        self.color = (30,144,255)
        self.hover_color = (65, 105, 225)

    def draw(self,screen,font):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (0,0,0), self.rect, width=3, border_radius=5)
        text_surface = font.render(self.text, True, (255,255,255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface,text_rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800,600))
        pygame.display.set_caption("Luna - a Hanover College Mystery")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 50)
        self.title_font = pygame.font.Font(None, 60)
        self.state = "menu"
        self.background = pygame.image.load("game/assets/background.png").convert()
        self.background = pygame.transform.scale(self.background, (800,600))
        self.buttons = [ Button(300,250,200,60, "Start", "start"), Button(300,330,200,60, "Quit", "quit"),]

    def draw_menu(self):
        self.screen.blit(self.background, (0, 0))
        title_surface = self.title_font.render("Luna - a Hanover College Mystery", True, (0,0,0))
        title_rect = title_surface.get_rect(center = (self.screen.get_width() // 2, 90))
        self.screen.blit(title_surface, title_rect)
        for button in self.buttons:
            button.draw(self.screen, self.font)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.buttons:
                        if button.rect.collidepoint(event.pos):
                            if button.action == "start":
                                self.state = "playing"
                            elif button.action == "quit":
                                running = False
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "playing":
                self.screen.fill((0,128,0))
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
        
if __name__ == "__main__":
    Game().run()



