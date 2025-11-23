
    def manage_events(self, event):
        if event.type == pygame.QUIT:
            self.is_running = False
        # On va gérer d'autres évènements

    def manage_pressed_keys(self):
        pressed = pygame.key.get_pressed()

        vecteur = [0, 0]
        if pressed[K_q] or pressed[K_LEFT]:
            vecteur[0] -= 1
        if pressed[K_d] or pressed[K_RIGHT]:
            vecteur[0] += 1
        if pressed[K_z] or pressed[K_UP]:
            vecteur[1] -= 1
        if pressed[K_s] or pressed[K_DOWN]:
            vecteur[1] += 1
        
        self.player.move(vecteur[0], vecteur[1])

    def quit(self):
        pygame.display.quit()
        pygame.quit()
        del self