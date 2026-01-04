import pygame

class Music:
    def __init__(self):
        self.tracks = {
            "menu": "musique/menu.mp3",
            "game": "musique/game.mp3",
            "game_over": "musique/game_over.mp3",
            "boss": "musique/bossbattle.mp3"
        }
        self.current_track = None
        self.volume = 0.1 # <--- Volume par défaut faible
        pygame.mixer.music.set_volume(self.volume)

    def play(self, track_name):
        if track_name in self.tracks:
            if self.current_track != track_name:
                try:
                    pygame.mixer.music.load(self.tracks[track_name])
                    pygame.mixer.music.set_volume(self.volume)
                    pygame.mixer.music.play(-1)
                    self.current_track = track_name
                except Exception as e:
                    print(f"Erreur musique {track_name}: {e}")

    def stop(self):
        pygame.mixer.music.stop()
        self.current_track = None

    def change_volume(self, change):
        self.volume += change
        if self.volume > 1.0: self.volume = 1.0
        if self.volume < 0.0: self.volume = 0.0
        pygame.mixer.music.set_volume(self.volume)