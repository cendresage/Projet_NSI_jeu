import pygame

class Music:
    def __init__(self):
    
        self.tracks = {
            "menu": "musique/menu.mp3",
            "game": "musique/game.mp3",
            "game_over": "musique/game_over.mp3",
            "boss": "musique/bossbattle.mp3"
        }

        self.global_volume = 0.5  # Volume par défaut (50%) -> Ce sera modifiable par la barre de son
        self.game_volume_ratio = 0.3

        self.current_track_name = None


    def play(self, track_name):
        """Lance une musique en boucle"""

        if track_name not in self.tracks:
            print(f"Erreur : La piste {track_name} n'existe pas.")
            return

        # Évite de relancer la musique si c'est déjà la même qui joue
        if self.current_track_name == track_name:
            return
        
        try:
            pygame.mixer.music.load(self.tracks[track_name])
            self.current_track_name = track_name
            self.apply_volume()
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Erreur chargement musique ({track_name}): {e}")

    
    def stop(self):
        pygame.mixer.music.stop()

    def set_global_volume(self, volume):
        """
        Sert à modifier le volume général (pour la future barre de paramètres).
        volume : float entre 0.0 et 1.0
        """
        self.global_volume = max(0.0, min(1.0, volume)) # Borne entre 0 et 1
        self.apply_volume() # Met à jour le volume immédiatement

    def apply_volume(self):
        """Calcule et applique le volume réel selon la piste en cours."""
        final_volume = self.global_volume

        # Si on est en jeu, on réduit le volume (bruit de fond)
        if self.current_track_name == "game":
            final_volume = self.global_volume * self.game_volume_ratio
        
        pygame.mixer.music.set_volume(final_volume)