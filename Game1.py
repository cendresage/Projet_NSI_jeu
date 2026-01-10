import pygame

from Screen import Screen
from Map import Map
from Keylistener import Keylistener
from Player import Player
from Boss import Agis
from Music import Music

HUD_SCALE = 2

PLAYER_STATUS_BG_PATH = "Sprites/ATH/spr_player_status_version1.png"
HEALTHBAR_PATH = "Sprites/ATH/spr_player_status_healthbar_bk.png"
MONEY_ICON_PATH = "Sprites/ATH/spr_money_interface.png"

class Game:
    def __init__(self):
        self.running = True
        self.screen = Screen()
        self.keylistener = Keylistener()

        self.music = Music()
        self.music.play("game")
        
        # 1. Création des groupes
        self.player_bullets = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()

        # 2. Création de la map en lui passant le groupe d'ennemis
        self.map = Map(self.screen, self.enemy_group)
        
        # 3. Création du joueur et ajout à la map
        self.Player = Player(self.keylistener, self.screen, 92, 1521)
        self.map.add_player(self.Player)
        
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 30, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 18, bold=True)

        self.hud_bg_img = pygame.transform.scale_by(
            pygame.image.load(PLAYER_STATUS_BG_PATH).convert_alpha(), HUD_SCALE
        )
        self.health_bar_img = pygame.transform.scale_by(
            pygame.image.load(HEALTHBAR_PATH).convert_alpha(), HUD_SCALE
        )
        self.money_icon_img = pygame.transform.scale_by(
            pygame.image.load(MONEY_ICON_PATH).convert_alpha(), HUD_SCALE
        )
        
        self.player_head_img = self._get_player_head_image()

        # --- SON HITMARKER ---
        try:
            self.hit_sound = pygame.mixer.Sound("musique/son_ingame/hitmarker.wav")
            self.hit_sound.set_volume(0.5)
            self.chest_sound = pygame.mixer.Sound("musique/son_ingame/chest_open.mp3")
            self.chest_sound.set_volume(0.5)
        except Exception as e:
            print(f"Erreur son hit: {e}")
            self.hit_sound = None
            self.chest_sound = None

        # --- TIMER DU JEU (5 minutes = 300 secondes) ---
        self.total_time = 300 
        self.start_ticks = pygame.time.get_ticks() # Temps au lancement
        self.elapsed_time_paused = 0 # Temps accumulé avant la pause (Boss)
        self.is_timer_paused = False

        # --- MESSAGES FLOTTANTS (Coffres) ---
        self.info_text = ""
        self.info_text_timer = 0
        self.info_color = (255, 255, 255)

        # --- ETAT VICTOIRE ---
        self.boss_defeated_time = None # Pour le délai de 3 secondes
        self.boss_spawned = False # Pour savoir si on a déjà rencontré le boss


    def _get_player_head_image(self):
        player_spritesheet = pygame.image.load("Sprites/Personnages/Player.png")
        
        # Extrait la tête non mise à l'échelle (16x16)
        head_surface_unscaled = player_spritesheet.subsurface(pygame.Rect(12, 2, 16, 16)).convert_alpha()
        return pygame.transform.scale(head_surface_unscaled, (16 * HUD_SCALE, 16 * HUD_SCALE))



    def run(self):
        while self.running:
            if self.Player.hp <= 0:
                self.music.stop()
                return "game_over"
            
            # --- GESTION DU TIMER ---
            current_ticks = pygame.time.get_ticks()

            # Pause du timer si on est dans la map du boss
            if "map_boss" in self.map.current_map_name: # Vérifie si le nom de la map contient "map_boss"
                if not self.is_timer_paused:
                    # On vient d'entrer, on stocke le temps déjà écoulé
                    self.elapsed_time_paused += (current_ticks - self.start_ticks)
                    self.is_timer_paused = True
                display_time = self.total_time - (self.elapsed_time_paused // 1000)
            else:
                if self.is_timer_paused:
                    # On sort de la map boss, on redémarre le compteur
                    self.start_ticks = current_ticks
                    self.is_timer_paused = False

                # Temps écoulé total = temps stocké + temps depuis le dernier start
                seconds_passed = (self.elapsed_time_paused + (current_ticks - self.start_ticks)) // 1000
                display_time = self.total_time - seconds_passed

            # Fin du temps
            if display_time <= 0 and not self.is_timer_paused:
                return "time_out"
                
            self.handle_input()

            # --- MISE A JOUR ENNEMIS ET BOSS ---
            boss_present = False
            for enemy in self.enemy_group:
                if isinstance(enemy, Agis):
                    boss_present = True
                    self.boss_spawned = True
                    continue # Le Boss a son update spécial plus bas
                
                new_bullet = enemy.update()
                if new_bullet:
                    self.map.group.add(new_bullet)
                    self.enemy_bullets.add(new_bullet)

            # --- GESTION VICTOIRE (BOSS MORT) ---
            # Si le boss a spawn, qu'on est sur sa map, mais qu'il n'est plus dans le groupe
            # (et qu'il n'est pas en train de mourir, mais la suppression se fait après l'anim)
            if self.boss_spawned and "map_boss" in self.map.current_map_name and not boss_present:
                # Le boss est mort !
                if self.boss_defeated_time is None:
                    self.boss_defeated_time = current_ticks
                
                # Attente de 3 secondes
                if current_ticks - self.boss_defeated_time > 3000:
                    return "win"

            # --- COLLISIONS JOUEUR vs ENNEMIS ---
            hits = pygame.sprite.groupcollide(
                self.enemy_group, 
                self.player_bullets, 
                False, 
                True,  
                collided=self.check_collision_hitbox 
            )
            
            # Si le dictionnaire 'hits' n'est pas vide, c'est qu'on a touché quelqu'un !
            if hits and self.hit_sound:
                    self.hit_sound.play()

            for enemy in hits:
                enemy.damage(1)
                if enemy.hp <= 0:
                    self.map.remove_dead_enemy(enemy)
                    
            hits = pygame.sprite.groupcollide(
                self.player_bullets, 
                self.enemy_group, 
                True, 
                False, 
                collided=self.check_collision_hitbox
            )
            for bullet in hits:
                bullet.kill()

            # --- COLLISIONS BALLES JOUEUR vs COFFRES  ---
            # On vérifie si les balles touchent les rects des coffres
            for bullet in self.player_bullets:
                # collidelist renvoie l'index du rect touché, ou -1
                index = bullet.rect.collidelist(self.map.chests)
                if index != -1:
                    bullet.kill()
                    
                    # Logique d'ouverture
                    chest_rect = self.map.chests[index]
                    
                    # Vérifier la distance
                    dist = pygame.math.Vector2(self.Player.rect.center) - pygame.math.Vector2(chest_rect.center)
                    if dist.length() < 100: 
                        # MODIFICATION ICI : On vérifie D'ABORD si on a besoin de soin
                        if self.Player.hp < self.Player.max_hp:
                            # On applique le soin et le son
                            self.Player.hp += 1
                            if self.chest_sound:
                                self.chest_sound.play()
                            self.show_message("+1 PV", (0, 255, 0))
                                
                            del self.map.chests[index]
                        else:
                            # Si on a toute la vie, on ne supprime PAS le coffre
                            self.show_message("Vous avez tous vos PV", (200, 200, 200))
                    else:
                        self.show_message("Trop loin !", (255, 100, 100))

            hits_player = pygame.sprite.spritecollide(
                self.Player, 
                self.enemy_bullets, 
                True, 
                collided=self.check_collision_hitbox
            )
            if hits_player and self.hit_sound:
                self.hit_sound.play()
            for bullet in hits_player:
                self.Player.damage(1)
            
            # --- LOGIQUE DU BOSS (AGIS) ---
            current_time = pygame.time.get_ticks()
            
            # Mise à jour du Boss
            for entity in self.map.enemy_group:
                if isinstance(entity, Agis):
                    entity.update(current_time, self.boss_bullets, self.map.collisions)

            # Mise à jour des balles du boss (Déplacement + Collision Joueur interne à la classe BossBullet)
            self.boss_bullets.update(self.Player, self.map.collisions)

            # Ajout des balles du boss au groupe d'affichage pour qu'on les voie
            self.map.group.add(self.boss_bullets)
            
            # --- FIN LOGIQUE BOSS ---

            all_bullets = self.player_bullets.copy()
            all_bullets.add(self.enemy_bullets)

            self.map.update(all_bullets)

            delayed_bullet = self.Player.check_pending_fire()
            if delayed_bullet:
                self.player_bullets.add(delayed_bullet)
                self.map.group.add(delayed_bullet)
            
            self.draw_hud(display_time)
            
            camera_pos = self.map.group.view.topleft
            map_zoom = self.map.map_layer.zoom
            for enemy in self.enemy_group:
                # Petite sécurité pour ne pas crash
                if hasattr(enemy, 'draw_health_bar'):
                    enemy.draw_health_bar(self.screen.get_display(), camera_pos, map_zoom)
            
            self.screen.update()
        
        return "quit"
    
    def show_message(self, text, color):
        self.info_text = text
        self.info_color = color
        self.info_text_timer = pygame.time.get_ticks()

    def check_collision_hitbox(self, sprite1, sprite2):
        return sprite1.hitbox.colliderect(sprite2.hitbox)

    def handle_input(self):
        for event in pygame.event.get():                                            # Gestion des évènements (récupère les touches pressées)
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                self.keylistener.add_key(event.key)
            elif event.type == pygame.KEYUP:
                self.keylistener.remove_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:                                                # Bouton gauche de la souris
                    screen_mouse_x, screen_mouse_y = pygame.mouse.get_pos()

                    camera_x, camera_y = self.map.group.view.topleft
                    zoom = self.map.map_layer.zoom

                    world_mouse_x = (screen_mouse_x / zoom) + camera_x
                    world_mouse_y = (screen_mouse_y / zoom) + camera_y

                    new_bullet = self.Player.fire(world_mouse_x, world_mouse_y)
                    if new_bullet: 
                        self.player_bullets.add(new_bullet)
                        self.map.group.add(new_bullet)
    def draw_hud(self, display_time):
        display = self.screen.get_display()

        # Constantes d'alignement
        BASE_X = 20
        BASE_Y = 20

        display.blit(self.hud_bg_img, (BASE_X, BASE_Y))

        head_x = BASE_X + (9 * HUD_SCALE) 
        head_y = BASE_Y + (6 * HUD_SCALE)
        display.blit(self.player_head_img, (head_x, head_y))

        hp_bar_x = BASE_X + (33 * HUD_SCALE)
        hp_bar_y = BASE_Y + (12 * HUD_SCALE)

        if self.Player.max_hp > 0:
            ratio = self.Player.hp / self.Player.max_hp
            full_width = self.health_bar_img.get_width()
            full_height = self.health_bar_img.get_height()
            visible_width = int(full_width * ratio)
            if visible_width > 0:
                area_rect = pygame.Rect(0, 0, visible_width, full_height)
                display.blit(self.health_bar_img, (hp_bar_x, hp_bar_y), area_rect)

        money_y = BASE_Y + self.hud_bg_img.get_height() + 5 
        money_x = BASE_X

        display.blit(self.money_icon_img, (money_x, money_y))

        score_x = money_x + 60 
        score_y = money_y + (self.money_icon_img.get_height() // 2) - (self.small_font.get_height() // 2)
        
        score_text = self.small_font.render(f"{self.Player.point}", True, (255, 255, 255))
        display.blit(score_text, (score_x, score_y))

        # --- TIMER (HAUT DROITE) ---
        screen_w = display.get_width()
        minutes = int(display_time // 60)
        seconds = int(display_time % 60)
        time_str = f"{minutes:02}:{seconds:02}"
        
        # Couleur : Rouge si < 30 secondes, sinon Blanc
        color_time = (255, 255, 255)
        if display_time < 30 and not self.is_timer_paused:
            color_time = (255, 0, 0)
        elif self.is_timer_paused:
            color_time = (255, 215, 0) # Doré si pause (Boss)

        time_surf = self.font.render(time_str, True, color_time)
        display.blit(time_surf, (screen_w - 120, 20))

        # --- TEXTE D'INFO FLOTTANT (+1 PV, etc) ---
        if self.info_text and pygame.time.get_ticks() - self.info_text_timer < 2000: # Affiche pendant 2s
            text_surf = self.font.render(self.info_text, True, self.info_color)
            rect = text_surf.get_rect(center=(screen_w//2, screen_w//2 - 50))
            # Petit fond noir pour lisibilité
            bg_rect = rect.inflate(10, 10)
            pygame.draw.rect(display, (0,0,0), bg_rect)
            display.blit(text_surf, rect)

    
    def fade_out_game_over(self):
        display_surface = self.screen.get_display()

        # Prend l'écran actuel pour le figer
        snapshot = display_surface.copy()
        
        # Surface noir transparente pour le fondu
        fade_surface = pygame.Surface(display_surface.get_size())
        fade_surface.fill((0, 0, 0))

        # Boucle de fondu
        for alpha in range(0, 255, 5):
            fade_surface.set_alpha(alpha)

            display_surface.blit(snapshot, (0, 0))
            display_surface.blit(fade_surface, (0, 0))

            self.screen.update()
            pygame.time.delay(20)