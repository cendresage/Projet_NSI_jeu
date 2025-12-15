import pygame
import sys
from game1 import Game
from menu import Menu, GameOverMenu

pygame.init()

if __name__ == "__main__":
    current_state = "menu"
    
    while True:
        if current_state == "menu":
            menu = Menu()
            action = menu.run()
            if action == "play":
                current_state = "game"
                
            else:
                break

        elif current_state == "game":
            game = Game()
            result = game.run()
            if result == "game_over":
                current_state = "game_over"     
            else:
                break

        elif current_state == "game_over":
            game_over_menu = GameOverMenu()
            action = game_over_menu.run()
            if action == "menu":
                current_state = "menu"
            else:
                break

    pygame.quit()
    sys.exit()