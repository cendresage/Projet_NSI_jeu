import pygame

from Menu import Menu
from EndMenu import EndMenu
from Game1 import Game

def main():
    pygame.init()
    
    # Boucle infinie pour pouvoir relancer le jeu autant qu'on veut
    while True:
        # 1. On lance le Menu Principal
        menu = Menu()
        action = menu.run()
        
        if action == "exit":
            break
        
        if action == "play":
            # 2. On lance le Jeu
            game = Game()
            result = game.run() # Peut renvoyer "game_over", "time_out", "win" ou "quit"
            
            if result == "quit":
                break
            
            # 3. GESTION DE LA FIN DE PARTIE
            if result in ["game_over", "time_out", "win"]:
                # On détermine le type d'écran à afficher
                result_type = "dead" # Par défaut
                
                if result == "time_out":
                    result_type = "time_out"
                elif result == "win":
                    result_type = "win"
                
                # On récupère le score final du joueur
                final_score = game.Player.point
                
                # On lance le menu de fin avec les bons paramètres
                end_menu = EndMenu(final_score, result_type=result_type)
                end_action = end_menu.run()
                
                # Si le joueur clique sur "Menu", la boucle while recommence au début
                if end_action == "menu":
                    continue
                else:
                    break # Sinon on quitte

if __name__ == "__main__":
    main()