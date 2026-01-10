import pygame

from SoundManager import SoundManager

class Music:
    def __init__(self):
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)

    def play(self, name):
        try:
            # On demande le chemin au SoundManager
            path = SoundManager.get_path(name)
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Erreur musique ({name}): {e}")

    def stop(self):
        pygame.mixer.music.stop()

    def change_volume(self, amount):
        self.volume = max(0.0, min(1.0, self.volume + amount))
        pygame.mixer.music.set_volume(self.volume)