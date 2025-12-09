import pygame
from game1 import Game
from menu import Menu

pygame.init()

if __name__ == "__main__":
    menu = Menu()
    action = menu.run()

    if action == "play":
        del menu
        game = Game()
        game.run()
    
    pygame.quit()