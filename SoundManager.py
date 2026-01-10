class SoundManager:
    # Par défaut, le mode secret est désactivé
    _secret_mode = False

    # Dictionnaire de tous les sons (Clé : {normal: chemin, secret: chemin})
    SOUNDS = {
        # Musiques
        "menu": {"normal": "musique/menu.mp3", "secret": "musique/secret_sound/menu_ouf.mp3"},
        "game": {"normal": "musique/game.mp3", "secret": "musique/secret_sound/ratdance.mp3"},
        "game_over": {"normal": "musique/game_over.mp3", "secret": "musique/secret_sound/justover.mp3"},
        "bossbattle": {"normal": "musique/bossbattle.mp3", "secret": "musique/secret_sound/boss_sound.mp3"},
        
        # Sons
        "chest_open": {"normal": "musique/son_ingame/chest_open.mp3", "secret": "musique/secret_sound/zelda_chest.mp3"},
        "footstep": {"normal": "musique/son_ingame/footstep.wav", "secret": "musique/secret_sound/foot.mp3"},
        "hitmarker": {"normal": "musique/son_ingame/hitmarker.wav", "secret": "musique/secret_sound/fahhhh.mp3"},
        "laser": {"normal": "musique/son_ingame/laser.wav", "secret": "musique/secret_sound/shot.mp3"},
        "roar": {"normal": "musique/son_ingame/roar.wav", "secret": "musique/secret_sound/jack.mp3"},
        "slam_door": {"normal": "musique/son_ingame/slam_door.wav", "secret": "musique/secret_sound/metal.mp3"},
        "wallbump": {"normal": "musique/son_ingame/wallbump.wav", "secret": "musique/secret_sound/death_ouf.mp3"},
        "boss_impact": {"normal": "musique/son_ingame/boss_impact.wav", "secret": "musique/secret_sound/boum.mp3"},
        "boss_shot": {"normal": "musique/son_ingame/boss_shot.wav", "secret": "musique/secret_sound/ftg.mp3"},
    }

    @staticmethod
    def get_path(key):
        """Renvoie le chemin du fichier selon le mode actuel"""
        mode = "secret" if SoundManager._secret_mode else "normal"
        # Sécurité : si la clé n'existe pas, on renvoie une chaine vide ou on gère l'erreur
        if key in SoundManager.SOUNDS:
            return SoundManager.SOUNDS[key][mode]
        return ""

    @staticmethod
    def toggle_secret_mode():
        """Active ou désactive le mode secret"""
        SoundManager._secret_mode = not SoundManager._secret_mode
        state = "ACTIVÉ" if SoundManager._secret_mode else "DÉSACTIVÉ"
        print(f"--- MODE SECRET {state} ---")