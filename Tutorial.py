import pygame

class Tutorial:
    def __init__(self, screen):
        self.screen = screen
        self.active = False
        self.current_slide = 0
        
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_bold = pygame.font.SysFont("Arial", 26, bold=True)
        
        # Chargement des images (avec sécurité si elles n'existent pas)
        self.img_enemy = self.load_image("Image/Tuto/Ennemie.png", scale=0.5)
        self.img_door = self.load_image("Image/Tuto/Porte.png", scale=0.8)
        self.img_path = self.load_image("Image/Tuto/Chemin.png", scale=0.8)  
        self.img_chest = self.load_image("Image/Tuto/Coffre.png", scale=1.0)

        self.slides = [
            {
                "text": "Le but du jeu est de finir la partie avec le plus de points possible. Pour cela, vous évoluerez sur une carte de 3 étages, dont le dernier sera un combat de boss.",
                "image": None
            },
            {
                "text": "Vous pouvez tirer avec le clic gauche de votre souris (l'utiliser est fortement conseillé !). Le tir se fera en fonction de la position du curseur (haut, bas, gauche, droite), mais uniquement en face du joueur (sur la même case).",
                "image": None
            },
            {
                "text": "Chaque étage comporte son nombre d'ennemis. Attention : au deuxième étage, les ennemis sont plus forts mais rapportent plus de points.",
                "image": self.img_enemy
            },
            {
                "text": "Vous devrez trouver les portes cachées dans la carte pour accéder à l'étage supérieur. Vous pourrez toujours redescendre à l'étage 1 si vous le souhaitez.",
                "image": self.img_door
            },
            {
                "text": "Si vous êtes perdu, ne vous en faites pas : à certains endroits, des indications au sol pourraient vous aider. Soyez attentif !",
                "image": self.img_path
            },
            {
                "text": "Si vous êtes en difficulté, vous pourrez trouver des coffres (2 par étage). Approchez-vous et tirez dessus pour récupérer 1 point de vie.",
                "image": self.img_chest
            },
            {
                "text": "Enfin, si vous parvenez en vie à la salle du boss, essayez de le battre ! Aucun retour en arrière ne sera possible. Il rapporte 500 points (spoiler : il devient plus fort au fil du combat, à vos risques et périls !).",
                "image": None
            }
        ]

        # Rectangle du fond (Carré noir semi-transparent)
        sw, sh = self.screen.get_size()
        self.rect = pygame.Rect(0, 0, 600, 450) # Un peu plus haut pour contenir le texte et l'image
        self.rect.center = (sw // 2, sh // 2)
        
        self.overlay = pygame.Surface((self.rect.width, self.rect.height))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(240) # Fond bien sombre pour la lisibilité

    def load_image(self, path, scale=1):
        try:
            img = pygame.image.load(path).convert_alpha()
            if scale != 1:
                img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
            return img
        except:
            # Si l'image n'est pas encore créée, on affiche un carré vide pour ne pas faire planter le jeu
            print(f"Image introuvable : {path}")
            surf = pygame.Surface((50, 50))
            surf.fill((100, 100, 100))
            return surf

    def handle_input(self, event):
        if not self.active:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Clic gauche : Slide suivant
            self.current_slide += 1
            if self.current_slide >= len(self.slides):
                self.active = False # Fin du tuto
                self.current_slide = 0
            return True # On indique qu'on a traité l'événement
        
        return False
    
    def start(self):
        self.active = True
        self.current_slide = 0

    def draw(self):
        if not self.active:
            return

        # Dessiner le fond noir
        self.screen.blit(self.overlay, self.rect.topleft)
        pygame.draw.rect(self.screen, (255, 255, 255), self.rect, 2) # Bordure blanche

        # Récupérer les infos du slide actuel
        slide = self.slides[self.current_slide]
        text = slide["text"]
        image = slide["image"]

        # Affichage du texte (avec retour à la ligne automatique)
        self.draw_text_wrapped(text, self.rect.x + 30, self.rect.y + 30, self.rect.width - 60)

        # Affichage de l'image (centrée en bas)
        if image:
            # On la place un peu au-dessus du texte "Cliquez..."
            img_rect = image.get_rect(center=(self.rect.centerx, self.rect.bottom - 160))
            self.screen.blit(image, img_rect)

        # Indication "Cliquez pour continuer"
        next_text = self.font.render("Cliquez pour continuer...", True, (200, 200, 200))
        self.screen.blit(next_text, (self.rect.right - next_text.get_width() - 20, self.rect.bottom - 30))
        
        # Compteur de pages (ex: 1/7)
        page_text = self.font_bold.render(f"{self.current_slide + 1}/{len(self.slides)}", True, (255, 215, 0))
        self.screen.blit(page_text, (self.rect.x + 30, self.rect.bottom - 30))

    def draw_text_wrapped(self, text, x, y, max_width):
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            # On teste la taille de la ligne avec le nouveau mot
            fw, fh = self.font.size(' '.join(current_line))
            if fw > max_width:
                current_line.pop() # On enlève le mot qui dépasse
                lines.append(' '.join(current_line))
                current_line = [word] # On le met sur la ligne suivante
        
        lines.append(' '.join(current_line))

        for i, line in enumerate(lines):
            text_surf = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surf, (x, y + i * 30))