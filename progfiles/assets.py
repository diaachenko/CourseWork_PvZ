import pygame
import os
import config as cfg

class AssetManager:
    def __init__(self, width, height):
        self.W = width
        self.H = height
        self.imgs = {}
        self.sounds = {}
        self.zombie_sounds = []
        self.music_files = {}
        self.fonts = {}
        
        print("\n=== START LOADING ASSETS ===")
        self._load_fonts()
        self._load_audio()
        self._load_images()
        print("=== ASSETS LOADING FINISHED ===\n")

    def _load_fonts(self):
        font_path = f"assets/{cfg.FONT_NAME}"
        if os.path.exists(font_path):
            self.fonts["title"] = pygame.font.Font(font_path, 70)
            self.fonts["menu"] = pygame.font.Font(font_path, 32)
            self.fonts["std"] = pygame.font.Font(font_path, 20)
            self.fonts["small"] = pygame.font.Font(font_path, 18)
            self.fonts["money"] = pygame.font.Font(font_path, 28)
        else:
            print(f"[WARN] Custom font {font_path} missing. Using system default.")
            self.fonts["title"] = pygame.font.SysFont("Comic Sans MS", 70, bold=True)
            self.fonts["menu"] = pygame.font.SysFont("Comic Sans MS", 32, bold=True)
            self.fonts["std"] = pygame.font.SysFont("Arial", 20, bold=True)
            self.fonts["small"] = pygame.font.SysFont("Arial", 18, bold=True)
            self.fonts["money"] = pygame.font.SysFont("Arial", 28, bold=True)

    def _load_audio(self):
        sound_files = {
            "click": "snd_click.ogg", "pause": "snd_pause.ogg",
            "shovel": "snd_shovel.ogg", "plant": "snd_plant.ogg",
            "win": "snd_win.ogg", "lose": "snd_lose.ogg",
            "cherry": "snd_cherrybomb.ogg", "imp": "snd_imp.ogg",
            "pea_hit": "snd_pea_hit.ogg", "eat": "snd_eat.ogg",
            "freeze": "snd_freeze.ogg", "dig": "snd_dig.ogg",
            "gargantuar": "snd_gargantuar.ogg",
            "cone_hit": "snd_cone_hit.ogg", "bucket_hit": "snd_bucket_hit.ogg",
            "paper_rip": "snd_paper_rip.ogg", "zombie_angry": "snd_zombie_angry.ogg"
        }
        for k, v in sound_files.items():
            p = f"assets/{v}"
            if os.path.exists(p): 
                self.sounds[k] = pygame.mixer.Sound(p)
            else:
                print(f"[MISSING SOUND] {v}")

        for i in range(1, 7):
            p = f"assets/snd_zombie_{i}.ogg"
            if os.path.exists(p): self.zombie_sounds.append(pygame.mixer.Sound(p))
        if not self.zombie_sounds and os.path.exists("assets/snd_zombie.ogg"):
            self.zombie_sounds.append(pygame.mixer.Sound("assets/snd_zombie.ogg"))

        self.music_menu = "assets/music_menu.ogg" if os.path.exists("assets/music_menu.ogg") else None
        self.music_game_default = "assets/music_game.ogg" if os.path.exists("assets/music_game.ogg") else None
        for i in range(1, 21):
            p = f"assets/music_level_{i}.ogg"
            if os.path.exists(p): self.music_files[i] = p

    def _load_images(self):
        gw, gh = int(cfg.PY_TILE_W - 10), int(cfg.PY_TILE_H - 10)
        for i in range(len(cfg.PLANT_NAMES)):
            p = f"assets/plant_{i}.png"
            if os.path.exists(p):
                img = pygame.image.load(p).convert_alpha()
                self.imgs[f"plant_{i}"] = pygame.transform.scale(img, (gw, gh))
                self.imgs[f"icon_{i}"] = pygame.transform.scale(img, (cfg.CARD_ICON_W, cfg.CARD_ICON_H))
                print(f"[LOADED] plant_{i}.png")
            else:
                print(f"[MISSING] plant_{i}.png")

        extras = ["plant_1_active.png", "plant_3_armed.png", "plant_3_blink.png"]
        for e in extras:
            if os.path.exists(f"assets/{e}"):
                img = pygame.image.load(f"assets/{e}").convert_alpha()
                self.imgs[e.replace(".png", "")] = pygame.transform.scale(img, (gw, gh))
        
        if "plant_3_armed" in self.imgs:
             self.imgs["icon_3"] = pygame.transform.scale(self.imgs["plant_3_armed"], (cfg.CARD_ICON_W, cfg.CARD_ICON_H))

        if "plant_2" in self.imgs: self.imgs["plant_2_s1"] = self.imgs["plant_2"]
        for i in range(1, 4):
            p = f"assets/plant_2_cracked{i}.png"
            if os.path.exists(p):
                idx = i + 1
                self.imgs[f"plant_2_s{idx}"] = pygame.transform.scale(pygame.image.load(p).convert_alpha(), (100, 100))

        def load_anim(key, prefix, count):
            self.imgs[key] = []
            for i in range(count):
                p = f"assets/{prefix}_{i}.png"
                if os.path.exists(p):
                    self.imgs[key].append(pygame.transform.scale(pygame.image.load(p).convert_alpha(), (gw, gh)))

        load_anim("anim_cherry_pulse", "cherry_pulse", 5)

        zw, zh = int(cfg.PY_TILE_W), int(cfg.PY_TILE_H * 1.2)
        
        def load_z(key, fname):
            if os.path.exists(f"assets/{fname}"):
                self.imgs[key] = pygame.transform.scale(pygame.image.load(f"assets/{fname}").convert_alpha(), (zw, zh))
                print(f"[LOADED] {fname} -> {key}")
            else:
                print(f"[MISSING] {fname}")

        for i in range(8):
            load_z(f"zombie_{i}_norm", f"zombie_{i}.png")
            load_z(f"zombie_{i}_frozen", f"zombie_{i}_frozen.png")
            load_z(f"zombie_{i}_noarm_norm", f"zombie_{i}_noarm.png")
            load_z(f"zombie_{i}_noarm_frozen", f"zombie_{i}_noarm_frozen.png")
        
        # Variants
        load_z("zombie_1_armor1_norm", "zombie_1_armor1.png"); load_z("zombie_1_armor1_frozen", "zombie_1_armor1_frozen.png")
        load_z("zombie_1_armor2_norm", "zombie_1_armor2.png"); load_z("zombie_1_armor2_frozen", "zombie_1_armor2_frozen.png")
        load_z("zombie_2_armor1_norm", "zombie_2_armor1.png"); load_z("zombie_2_armor1_frozen", "zombie_2_armor1_frozen.png")
        load_z("zombie_2_armor2_norm", "zombie_2_armor2.png"); load_z("zombie_2_armor2_frozen", "zombie_2_armor2_frozen.png")
        
        load_z("zombie_3_nohelm_norm", "zombie_3.png"); load_z("zombie_3_nohelm_frozen", "zombie_3_frozen.png")
        load_z("zombie_3_nohelm_noarm_norm", "zombie_3_nohelm.png"); load_z("zombie_3_nohelm_frozen", "zombie_3_nohelm_noarm_frozen.png")

        load_z("zombie_4_nopaper_norm", "zombie_4.png"); load_z("zombie_4_nopaper_frozen", "zombie_4_frozen.png")
        load_z("zombie_4_nopaper_noarm_norm", "zombie_4_nopaper.png"); load_z("zombie_4_nopaper_noarm_frozen", "zombie_4_nopaper_frozen.png")

        if os.path.exists("assets/proj_pea.png"): self.imgs["proj_0"] = pygame.transform.scale(pygame.image.load("assets/proj_pea.png").convert_alpha(), (40, 40))
        if os.path.exists("assets/effect_mine.png"): self.imgs["expl_0"] = pygame.transform.scale(pygame.image.load("assets/effect_mine.png").convert_alpha(), (200, 200))
        
        self.imgs["anim_cherry_expl"] = []
        for i in range(8):
            p = f"assets/expl_cherry_{i}.png"
            if os.path.exists(p): self.imgs["anim_cherry_expl"].append(pygame.transform.scale(pygame.image.load(p).convert_alpha(), (350, 350)))

        def load_bg(name, key):
            p = f"assets/{name}.png"
            if not os.path.exists(p): p = f"assets/{name}.jpg"
            
            if os.path.exists(p):
                self.imgs[key] = pygame.transform.scale(pygame.image.load(p).convert(), (self.W, self.H))
                print(f"[LOADED] Background: {p}")
            else:
                print(f"[MISSING] Background: {name}")

        load_bg("menu_background", "menu_bg")
        load_bg("level_select_bg", "level_select_bg")
        load_bg("pause_bg", "pause_bg")

        for i in range(1, 4):
            load_bg(f"background_{i}", f"bg_{i}")

        ui_files = ["btn_generic", "btn_shovel", "btn_shovel_hover", "btn_pause", "btn_pause_hover", 
                    "ui_panel_bg", "ui_card_bg", "btn_sound_on", "btn_sound_off", "btn_music_on", "btn_music_off", 
                    "ui_sun_display", "sun_icon"]
        
        for b in ui_files:
            p = f"assets/{b}.png"
            if os.path.exists(p):
                img = pygame.image.load(p).convert_alpha()
                if "shovel" in b: img = pygame.transform.scale(img, (80, 80))
                elif "pause" in b or "sound" in b or "music" in b: img = pygame.transform.scale(img, (60, 60))
                elif "card" in b: img = pygame.transform.scale(img, (cfg.CARD_W, cfg.CARD_H))
                elif "sun_display" in b: img = pygame.transform.scale(img, (140, 50))
                elif "sun_icon" in b: img = pygame.transform.scale(img, (50, 50))
                self.imgs[b] = img
            else:
                print(f"[MISSING] UI: {b}.png")
        
        if os.path.exists("assets/cursor_shovel.png"): 
            self.imgs["cursor_shovel"] = pygame.transform.scale(pygame.image.load("assets/cursor_shovel.png").convert_alpha(), (60, 60))
        elif "btn_shovel" in self.imgs: 
            self.imgs["cursor_shovel"] = pygame.transform.scale(self.imgs["btn_shovel"], (60, 60))