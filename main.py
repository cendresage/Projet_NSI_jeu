import pygame
import sys

from game1 import Game
from menu import Menu, GameOverMenu
from music import Music

pygame.init()

if __name__ == "__main__":

    music_manager = Music()

    current_state = "menu"
    
    while True:
        if current_state == "menu":
            music_manager.play("menu")
            menu = Menu()
            action = menu.run()
            if action == "play":
                current_state = "game"
                
            else:
                break

        elif current_state == "game":
            music_manager.play("game")
            game = Game()
            result = game.run()
            if result == "game_over":
                final_score = game.Player.point
                current_state = "game_over"
            else:
                break

        elif current_state == "game_over":
            music_manager.play("game_over")
            game_over_menu = GameOverMenu(final_score)
            action = game_over_menu.run()
            if action == "menu":
                current_state = "menu"
            else:
                break

    pygame.quit()
    sys.exit()