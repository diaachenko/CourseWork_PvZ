import pygame
import sys
import ctypes
import os
import json
import math
import random

import config as cfg
from cpp_bridge import lib, C_Plant, C_Zombie, C_Projectile, C_Effect
from assets import AssetManager
from save_system import load_progress, save_progress


class GameApp:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.W, self.H = self.screen.get_size()

        self.am = AssetManager(self.W, self.H)

        self.title_font = self.am.fonts["title"]
        self.menu_font = self.am.fonts["menu"]
        self.std_font = self.am.fonts["std"]
        self.small_font = self.am.fonts["small"]
        self.money_font = self.am.fonts["money"]

        self.clock = pygame.time.Clock()
        self.engine = lib.Engine_Create()

        self.is_muted = False
        self.is_music_muted = False
        self.eat_sound_timer = 0
        self.next_groan_time = pygame.time.get_ticks() + 2000

        progress = load_progress()
        self.unlocked_level = progress.get("unlocked_level", 1)
        self.available_plants_count = progress.get("plants_count", 1)
        self.is_shovel_unlocked = self.unlocked_level > 4

        self.state = "MAIN_MENU"
        self.current_level = 1
        self.selected_plant = 0
        self.is_shovel_active = False

        self.offset_x = 0;
        self.offset_y = 0
        self.map_w = 9;
        self.map_h = 5
        self.active_rows = []
        self.just_unlocked_item = None
        self.prev_zombie_count = 0

        self.init_ui_elements()
        self.play_music("menu")

    def play_sound(self, name):
        if not self.is_muted and name in self.am.sounds:
            self.am.sounds[name].play()

    def play_random_zombie(self):
        if not self.is_muted and self.am.zombie_sounds:
            random.choice(self.am.zombie_sounds).play()

    def play_music(self, track_type):
        if self.is_music_muted: return
        try:
            target_music = None
            if track_type == "menu":
                target_music = self.am.music_menu
            elif track_type == "game":
                if self.current_level in self.am.music_files:
                    target_music = self.am.music_files[self.current_level]
                else:
                    target_music = self.am.music_game_default

            if target_music:
                pygame.mixer.music.load(target_music)
                pygame.mixer.music.play(-1)
        except:
            pass

    def init_ui_elements(self):
        cx = self.W // 2
        cy = self.H // 2
        self.btn_continue = pygame.Rect(cx - 150, cy - 80, 300, 60)
        self.btn_levels = pygame.Rect(cx - 150, cy, 300, 60)
        self.btn_exit = pygame.Rect(cx - 150, cy + 80, 300, 60)

        self.level_buttons = []
        start_x, start_y = (self.W - 4 * 120) // 2, self.H // 2 - 100
        for i in range(1, 9):
            row, col = (i - 1) // 4, (i - 1) % 4
            self.level_buttons.append(
                {"rect": pygame.Rect(start_x + col * 120, start_y + row * 100, 100, 80), "lvl": i})

        self.btn_back = pygame.Rect(50, 50, 100, 50)

        self.pause_btn = pygame.Rect(self.W - 70, 10, 60, 60)
        self.sound_btn = pygame.Rect(self.W - 140, 10, 60, 60)
        self.music_btn = pygame.Rect(self.W - 210, 10, 60, 60)
        self.shovel_btn = pygame.Rect(self.W - 100, self.H - 100, 80, 80)

    def load_level(self, lvl):
        safe_lvl = lvl
        if safe_lvl > 8: safe_lvl = 1

        lib.Engine_LoadLevel(self.engine, safe_lvl)
        p = f"levels/level_{safe_lvl}.json"
        self.active_rows = []
        if os.path.exists(p):
            try:
                import json
                d = json.load(open(p))
                self.active_rows = d.get("settings", {}).get("active_rows", list(range(5)))
            except:
                self.active_rows = list(range(5))
        else:
            self.active_rows = list(range(5))
        self.map_w = lib.Engine_GetMapWidth(self.engine)
        self.map_h = lib.Engine_GetMapHeight(self.engine)
        self.is_shovel_active = False
        self.prev_zombie_count = 0
        self.played_effects_timers = []
        self.play_music("game")

    def get_screen_pos(self, cpp_x, cpp_y):
        grid_x = cpp_x / cfg.C_TILE_W
        grid_y = cpp_y / cfg.C_TILE_H
        screen_x = cfg.GRID_OFFSET_X + grid_x * cfg.PY_TILE_W
        screen_y = cfg.GRID_OFFSET_Y + grid_y * cfg.PY_TILE_H
        return int(screen_x), int(screen_y)

    def get_cpp_pos_from_screen(self, mx, my):
        rel_x = mx - cfg.GRID_OFFSET_X
        rel_y = my - cfg.GRID_OFFSET_Y
        gx = int(rel_x // cfg.PY_TILE_W)
        gy = int(rel_y // cfg.PY_TILE_H)
        return gx, gy

    def handle_input(self, event):
        mx, my = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state in ["MAIN_MENU", "PAUSE"]:
                if self.sound_btn.collidepoint(mx, my):
                    self.is_muted = not self.is_muted
                    self.play_sound("click")
                    return
                if self.music_btn.collidepoint(mx, my):
                    self.is_music_muted = not self.is_music_muted
                    if self.is_music_muted:
                        pygame.mixer.music.pause()
                    else:
                        if not pygame.mixer.music.get_busy():
                            self.play_music("menu" if self.state == "MAIN_MENU" else "game")
                        else:
                            pygame.mixer.music.unpause()
                    self.play_sound("click")
                    return

        if self.state == "MAIN_MENU":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_continue.collidepoint(mx, my):
                    self.play_sound("click")
                    target_lvl = self.unlocked_level
                    if target_lvl > 8: target_lvl = 1

                    self.current_level = target_lvl
                    self.load_level(self.current_level)
                    self.state = "GAME"

                if self.btn_levels.collidepoint(mx, my):
                    self.play_sound("click");
                    self.state = "LEVEL_SELECT"
                if self.btn_exit.collidepoint(mx, my): lib.Engine_Destroy(self.engine); pygame.quit(); sys.exit()

        elif self.state == "LEVEL_SELECT":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_back.collidepoint(mx, my): self.play_sound("click"); self.state = "MAIN_MENU"
                for btn in self.level_buttons:
                    if btn["rect"].collidepoint(mx, my):
                        if btn["lvl"] <= self.unlocked_level:
                            self.play_sound("click")
                            self.current_level = btn["lvl"];
                            self.load_level(self.current_level);
                            self.state = "GAME"

        elif self.state == "GAME":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.play_sound("pause")
                    self.state = "PAUSE" if not self.is_shovel_active else "GAME"
                    if self.state == "PAUSE": pygame.mixer.music.pause()
                    self.is_shovel_active = False
                if event.key == pygame.K_s and self.is_shovel_unlocked:
                    self.is_shovel_active = not self.is_shovel_active
                    self.play_sound("shovel" if self.is_shovel_active else "click")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3: self.is_shovel_active = False; return

                if self.pause_btn.collidepoint(mx, my):
                    self.play_sound("pause")
                    self.state = "PAUSE"
                    pygame.mixer.music.pause()
                    return

                if self.is_shovel_unlocked and self.shovel_btn.collidepoint(mx, my):
                    self.is_shovel_active = not self.is_shovel_active
                    self.play_sound("shovel" if self.is_shovel_active else "click")
                    return

                ui_width = self.available_plants_count * (cfg.CARD_W + 10)
                ui_start_x = (self.W - ui_width) // 2

                if my < cfg.UI_HEIGHT:
                    for i in range(self.available_plants_count):
                        r = pygame.Rect(ui_start_x + i * (cfg.CARD_W + 10), 10, cfg.CARD_W, cfg.CARD_H)
                        if r.collidepoint(mx, my):
                            self.is_shovel_active = False
                            self.selected_plant = i
                            self.play_sound("click")
                            break
                else:
                    gx, gy = self.get_cpp_pos_from_screen(mx, my)
                    if 0 <= gx < self.map_w and 0 <= gy < self.map_h:
                        c_x = gx * cfg.C_TILE_W + cfg.C_TILE_W / 2
                        c_y = gy * cfg.C_TILE_H + cfg.C_TILE_H / 2

                        if self.is_shovel_active:
                            cnt_before = lib.Engine_GetPlantCount(self.engine)
                            lib.Engine_RemovePlant(self.engine, ctypes.c_float(c_x), ctypes.c_float(c_y))
                            cnt_after = lib.Engine_GetPlantCount(self.engine)
                            if cnt_after < cnt_before: self.play_sound("dig")
                            self.is_shovel_active = False
                        else:
                            cnt_before = lib.Engine_GetPlantCount(self.engine)
                            lib.Engine_TryBuildPlant(self.engine, ctypes.c_float(c_x), ctypes.c_float(c_y),
                                                     self.selected_plant)
                            cnt_after = lib.Engine_GetPlantCount(self.engine)
                            if cnt_after > cnt_before: self.play_sound("plant")

        elif self.state == "PAUSE":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "GAME"
                if not self.is_music_muted: pygame.mixer.music.unpause()

            if event.type == pygame.MOUSEBUTTONDOWN:
                cx, cy = self.W // 2, self.H // 2
                if pygame.Rect(cx - 100, cy - 50, 200, 60).collidepoint(mx, my):
                    self.play_sound("click");
                    self.state = "GAME"
                    if not self.is_music_muted: pygame.mixer.music.unpause()
                elif pygame.Rect(cx - 100, cy + 30, 200, 60).collidepoint(mx, my):
                    self.play_sound("click");
                    self.load_level(self.current_level);
                    self.state = "GAME"
                elif pygame.Rect(cx - 100, cy + 110, 200, 60).collidepoint(mx, my):
                    self.play_sound("click"); self.state = "MAIN_MENU"; self.play_music("menu")

        elif self.state == "UNLOCK":
            if event.type == pygame.MOUSEBUTTONDOWN:
                cx, cy = self.W // 2, self.H // 2 + 100
                if pygame.Rect(cx - 150, cy + 100, 140, 60).collidepoint(mx, my):
                    self.play_sound("click")
                    self.current_level += 1
                    if self.current_level > 8: self.current_level = 1
                    self.load_level(self.current_level);
                    self.state = "GAME"
                elif pygame.Rect(cx + 10, cy + 100, 140, 60).collidepoint(mx, my):
                    self.play_sound("click"); self.state = "MAIN_MENU"; self.play_music("menu")

        elif self.state in ["GAMEOVER", "WIN"]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                btn1 = pygame.Rect(self.W // 2 - 150, self.H // 2, 140, 60)
                btn2 = pygame.Rect(self.W // 2 + 10, self.H // 2, 140, 60)
                if btn1.collidepoint(mx, my):
                    self.play_sound("click")
                    if self.state == "WIN":
                        self.current_level += 1
                        if self.current_level > 8: self.current_level = 1
                    self.load_level(self.current_level);
                    self.state = "GAME"
                elif btn2.collidepoint(mx, my):
                    self.play_sound("click"); self.state = "MAIN_MENU"; self.play_music("menu")

    def draw_button(self, rect, text, col=(0, 200, 0), hover_col=(50, 255, 50)):
        mx, my = pygame.mouse.get_pos()
        c = hover_col if rect.collidepoint(mx, my) else col

        if "btn_generic" in self.am.imgs:
            img = self.am.imgs["btn_generic"]
            img = pygame.transform.scale(img, (rect.width, rect.height))
            self.screen.blit(img, rect)
        else:
            pygame.draw.rect(self.screen, c, rect, border_radius=10)

        txt_col = cfg.TEXT_GREEN if rect.collidepoint(mx, my) else cfg.COLOR_BTN_TEXT
        ts = self.menu_font.render(text, True, txt_col)
        self.screen.blit(ts, (rect.centerx - ts.get_width() // 2, rect.centery - ts.get_height() // 2))

    def draw_toggle_btn(self, rect, is_on, name_on, name_off):
        k = name_on if is_on else name_off
        if k in self.am.imgs:
            self.screen.blit(self.am.imgs[k], rect)
        else:
            col = (0, 200, 0) if is_on else (200, 0, 0)
            pygame.draw.rect(self.screen, col, rect, border_radius=10)
            txt = "ON" if is_on else "OFF"
            ts = self.std_font.render(txt, True, cfg.TEXT_WHITE)
            self.screen.blit(ts, (rect.x + 10, rect.y + 15))

    def draw_common_bg(self, key):
        if key in self.am.imgs:
            self.screen.blit(self.am.imgs[key], (0, 0))
        else:
            self.screen.fill((20, 20, 30))

    def draw_main_menu(self):
        self.draw_common_bg("menu_bg")
        t = self.title_font.render(cfg.GAME_TITLE, True, cfg.COLOR_HEADER)
        self.screen.blit(t, (self.W // 2 - t.get_width() // 2, 100))

        disp_lvl = self.unlocked_level
        if disp_lvl > 8: disp_lvl = 1

        self.draw_button(self.btn_continue, f"CONTINUE (Lvl {disp_lvl})")
        self.draw_button(self.btn_levels, "LEVELS")
        self.draw_button(self.btn_exit, "EXIT")
        self.draw_toggle_btn(self.sound_btn, not self.is_muted, "btn_sound_on", "btn_sound_off")
        self.draw_toggle_btn(self.music_btn, not self.is_music_muted, "btn_music_on", "btn_music_off")

    def draw_level_select(self):
        self.draw_common_bg("level_select_bg")
        t = self.title_font.render("SELECT LEVEL", True, cfg.COLOR_HEADER)
        self.screen.blit(t, (self.W // 2 - t.get_width() // 2, 50))
        self.draw_button(self.btn_back, "BACK")
        for b in self.level_buttons:
            l = b["lvl"] > self.unlocked_level
            if "btn_generic" in self.am.imgs:
                img = self.am.imgs["btn_generic"]
                img = pygame.transform.scale(img, (b["rect"].width, b["rect"].height))

                if l:
                    s = pygame.Surface((b["rect"].width, b["rect"].height));
                    s.set_alpha(150);
                    s.fill((0, 0, 0))
                    img.blit(s, (0, 0))

                self.screen.blit(img, b["rect"])
            else:
                c = (50, 50, 50) if l else (0, 150, 0)
                pygame.draw.rect(self.screen, c, b["rect"], border_radius=10)

            mx, my = pygame.mouse.get_pos()
            hover = b["rect"].collidepoint(mx, my) and not l
            tcol = cfg.TEXT_GREEN if hover else cfg.COLOR_BTN_TEXT
            ts = self.menu_font.render(str(b["lvl"]), True, tcol)
            self.screen.blit(ts, (b["rect"].centerx - ts.get_width() // 2, b["rect"].centery - ts.get_height() // 2))

    def draw_unlock_screen(self):
        s = pygame.Surface((self.W, self.H));
        s.fill((50, 50, 70));
        self.screen.blit(s, (0, 0))
        t = self.title_font.render("NEW ITEM UNLOCKED!", True, cfg.COLOR_HEADER)
        self.screen.blit(t, (self.W // 2 - t.get_width() // 2, 100))
        id = self.just_unlocked_item
        if id in cfg.UNLOCK_INFO:
            n, d = cfg.UNLOCK_INFO[id]
            ico = None
            if id == 4:
                if "cursor_shovel" in self.am.imgs:
                    ico = self.am.imgs["cursor_shovel"]
                elif "btn_shovel" in self.am.imgs:
                    ico = self.am.imgs["btn_shovel"]
            else:
                pid = id if id < 4 else id - 1
                if f"plant_{pid}" in self.am.imgs: ico = self.am.imgs[f"plant_{pid}"]
            if ico:
                sc = pygame.transform.scale(ico, (150, 150))
                ico_rect = sc.get_rect(center=(self.W // 2, self.H // 2 - 50))
                self.screen.blit(sc, ico_rect)

            n_txt = self.menu_font.render(n, True, cfg.TEXT_WHITE)
            d_txt = self.std_font.render(d, True, (200, 200, 200))
            self.screen.blit(n_txt, (self.W // 2 - n_txt.get_width() // 2, self.H // 2 + 60))
            self.screen.blit(d_txt, (self.W // 2 - d_txt.get_width() // 2, self.H // 2 + 100))
        cx, cy = self.W // 2, self.H // 2 + 100
        self.draw_button(pygame.Rect(cx - 150, cy + 100, 140, 60), "NEXT LEVEL")
        self.draw_button(pygame.Rect(cx + 10, cy + 100, 140, 60), "MENU")

    def draw_game_scene(self):
        k = "bg_1"
        if self.current_level == 2 or self.current_level == 3:
            k = "bg_2"
        elif self.current_level > 3:
            k = "bg_3"

        if k in self.am.imgs:
            self.screen.blit(self.am.imgs[k], (0, 0))
        else:
            self.screen.fill((30, 30, 40))

        mx, my = pygame.mouse.get_pos()
        gx, gy = self.get_cpp_pos_from_screen(mx, my)

        for y in range(self.map_h):
            for x in range(self.map_w):
                if y in self.active_rows and x == gx and y == gy:
                    col = (255, 100, 100) if self.is_shovel_active else (255, 255, 255)
                    s = pygame.Surface((cfg.PY_TILE_W, cfg.PY_TILE_H))
                    s.set_alpha(80);
                    s.fill(col)
                    self.screen.blit(s, (cfg.GRID_OFFSET_X + x * cfg.PY_TILE_W, cfg.GRID_OFFSET_Y + y * cfg.PY_TILE_H))

        def draw_ent(key, obj, col, y_off=0, scale_f=1.0):
            sx, sy = self.get_screen_pos(obj.x, obj.y)
            if key in self.am.imgs:
                img = self.am.imgs[key]
                if scale_f != 1.0:
                    w, h = img.get_size()
                    img = pygame.transform.scale(img, (int(w * scale_f), int(h * scale_f)))
                if "plant_1" in key:
                    ang = math.sin(pygame.time.get_ticks() / 500.0) * 3
                    img = pygame.transform.rotate(img, ang)
                    if getattr(obj, 'timer', 0) > getattr(obj, 'max_timer', 0) - 1.0:
                        if "plant_1_active" in self.am.imgs: img = self.am.imgs["plant_1_active"]
                if "plant_2" in key:
                    ang = math.sin(pygame.time.get_ticks() / 800.0) * 2
                    img = pygame.transform.rotate(img, ang)
                self.screen.blit(img, img.get_rect(center=(sx, sy + y_off)))
            return sx, sy + y_off

        cnt = lib.Engine_GetPlantCount(self.engine)
        p = C_Plant()
        current_time = pygame.time.get_ticks() / 1000.0
        for i in range(cnt):
            if lib.Engine_GetPlantData(self.engine, i, ctypes.byref(p)):
                col = cfg.PLANT_COLS[p.type] if p.type < 6 else (255, 255, 255)
                asset_key = f"plant_{p.type}"
                sc = 1.0

                if p.type == 0 and p.timer > p.max_timer - 0.2: sc = 1.15
                if p.type == 2:
                    if p.health < p.max_health * 0.33:
                        asset_key = "plant_2_s3"
                    elif p.health < p.max_health * 0.66:
                        asset_key = "plant_2_s2"
                    else:
                        asset_key = "plant_2_s1"

                if p.type == 3:
                    if p.timer <= 0:
                        asset_key = "plant_3_armed"
                        if (
                                int(current_time * 2) % 2 == 0) and "plant_3_blink" in self.am.imgs: asset_key = "plant_3_blink"
                    else:
                        if p.timer < 0.8 and self.am.imgs.get("anim_mine"):
                            pct = 1.0 - (p.timer / 0.8)
                            f = min(int(pct * 3), 2)
                            img = self.am.imgs["anim_mine"][f]
                            sx, sy = self.get_screen_pos(p.x, p.y)
                            self.screen.blit(img, img.get_rect(center=(sx, sy)))
                            continue
                if p.type == 4:
                    if self.am.imgs.get("anim_cherry_pulse"):
                        pct = 1.0 - (p.timer / 0.8)
                        f = min(int(pct * 5), 4)
                        img = self.am.imgs["anim_cherry_pulse"][f]
                        sx, sy = self.get_screen_pos(p.x, p.y)
                        self.screen.blit(img, img.get_rect(center=(sx, sy)))
                        continue
                sx, sy = draw_ent(asset_key, p, col, 0, sc)

        cnt = lib.Engine_GetZombieCount(self.engine)
        z = C_Zombie()

        for i in range(cnt):
            if lib.Engine_GetZombieData(self.engine, i, ctypes.byref(z)):
                col = (100, 0, 150)
                if z.type == 7: col = (255, 0, 0)

                is_frozen = (z.flags & 8) != 0
                suffix = "norm"
                if is_frozen:
                    suffix = "frozen"

                ak = f"zombie_{z.type}_{suffix}"

                has_arm = (z.flags & 1)
                has_paper = (z.flags & 2)
                has_imp = (z.flags & 4)
                armor = z.armor_state

                if z.type == 1:
                    if armor == 1:
                        ak = f"zombie_1_armor1_{suffix}"
                    elif armor == 2:
                        ak = f"zombie_1_armor2_{suffix}"
                    else:
                        ak = f"zombie_0_{suffix}"
                elif z.type == 2:
                    if armor == 1:
                        ak = f"zombie_2_armor1_{suffix}"
                    elif armor >= 2:
                        ak = f"zombie_2_armor2_{suffix}"
                    else:
                        ak = f"zombie_0_{suffix}"
                elif z.type == 3:
                    if armor == 0:
                        if not has_arm:
                            ak = f"zombie_3_nohelm_noarm_{suffix}"
                        else:
                            ak = f"zombie_3_nohelm_{suffix}"
                elif z.type == 4:
                    if not has_paper:
                        if not has_arm:
                            ak = f"zombie_4_nopaper_noarm_{suffix}"
                        else:
                            ak = f"zombie_4_nopaper_{suffix}"
                elif z.type == 6:
                    ak = f"zombie_{z.type}_{suffix}"
                else:
                    if not has_arm: ak = f"zombie_{z.type}_noarm_{suffix}"

                if ak not in self.am.imgs:
                    if f"zombie_{z.type}_{suffix}" in self.am.imgs:
                        ak = f"zombie_{z.type}_{suffix}"
                    else:
                        ak = f"zombie_{z.type}_norm"

                sx, sy = draw_ent(ak, z, col, -20)

        cnt = lib.Engine_GetProjectileCount(self.engine)
        b = C_Projectile()
        for i in range(cnt):
            if lib.Engine_GetProjectileData(self.engine, i, ctypes.byref(b)):
                k = "proj_0"
                if b.is_frozen: k = "proj_1"
                sx, sy = self.get_screen_pos(b.x, b.y)
                if k in self.am.imgs: self.screen.blit(self.am.imgs[k], self.am.imgs[k].get_rect(center=(sx, sy)))

        cnt = lib.Engine_GetEffectCount(self.engine)
        eff = C_Effect()
        EXPLOSION_DURATION = 0.5
        CHERRY_DURATION = 1.2
        ICE_DURATION = 0.5

        for i in range(cnt):
            if lib.Engine_GetEffectData(self.engine, i, ctypes.byref(eff)):
                sx, sy = self.get_screen_pos(eff.x, eff.y)
                dur = EXPLOSION_DURATION
                if eff.type == 1: dur = CHERRY_DURATION
                if eff.type == 2: dur = ICE_DURATION

                if eff.timer > dur - 0.05:
                    if eff.type in [0, 1]: self.play_sound("cherry")
                    if eff.type == 2: self.play_sound("freeze")

                if eff.type == 0:
                    if "expl_0" in self.am.imgs:
                        sc = 1.0 + 0.5 * (1.0 - eff.timer / EXPLOSION_DURATION)
                        im = pygame.transform.scale(self.am.imgs["expl_0"], (int(200 * sc), int(200 * sc)))
                        self.screen.blit(im, im.get_rect(center=(sx, sy)))

                elif eff.type == 1:
                    if self.am.imgs.get("anim_cherry_expl"):
                        tp = CHERRY_DURATION - eff.timer
                        pct = max(0, min(1, tp / CHERRY_DURATION))
                        f = min(int(pct * 8), 7)
                        img = self.am.imgs["anim_cherry_expl"][f]
                        self.screen.blit(img, img.get_rect(center=(sx, sy)))

                elif eff.type == 2:
                    s = pygame.Surface((150, 150), pygame.SRCALPHA)
                    pygame.draw.circle(s, (0, 100, 255, 150), (75, 75),
                                       int(60 * (1.0 + (1.0 - eff.timer / ICE_DURATION))))
                    self.screen.blit(s, s.get_rect(center=(sx, sy)), special_flags=pygame.BLEND_RGBA_ADD)

        card_gap = 10
        ui_w = self.available_plants_count * (cfg.CARD_W + card_gap)
        ui_x = (self.W - ui_w) // 2

        if "ui_panel_bg" in self.am.imgs:
            panel = pygame.transform.scale(self.am.imgs["ui_panel_bg"], (ui_w + 40, cfg.UI_HEIGHT))
            self.screen.blit(panel, (ui_x - 20, 0))

        for i in range(self.available_plants_count):
            r = pygame.Rect(ui_x + i * (cfg.CARD_W + card_gap), 10, cfg.CARD_W, cfg.CARD_H)

            if "ui_card_bg" in self.am.imgs: self.screen.blit(self.am.imgs["ui_card_bg"], (r.x, r.y))

            if f"icon_{i}" in self.am.imgs:
                self.screen.blit(self.am.imgs[f"icon_{i}"], (r.x + cfg.CARD_ICON_OFF_X, r.y + cfg.CARD_ICON_OFF_Y))

            pct = lib.Engine_GetCardCooldownPct(self.engine, i)
            if pct > 0:
                h = cfg.CARD_H * pct
                s = pygame.Surface((cfg.CARD_W, h));
                s.set_alpha(150);
                s.fill((50, 50, 50))
                self.screen.blit(s, r)

            if i == self.selected_plant and not self.is_shovel_active:
                pygame.draw.rect(self.screen, (255, 255, 255), (r.x - 2, r.y - 2, r.width + 4, r.height + 4), 2)

            txt = self.small_font.render(str(cfg.PLANT_COSTS[i]), True, cfg.TEXT_BLACK)
            self.screen.blit(txt, (r.x + cfg.CARD_COST_OFF_X, r.y + cfg.CARD_COST_OFF_Y))

        money = lib.Engine_GetMoney(self.engine)
        if "ui_sun_display" in self.am.imgs:
            self.screen.blit(self.am.imgs["ui_sun_display"], (10, 10))
            if "sun_icon" in self.am.imgs: self.screen.blit(self.am.imgs["sun_icon"], (15, 5))
            mt = self.money_font.render(str(money), True, cfg.TEXT_WHITE)
            self.screen.blit(mt, (80, 15))
        else:
            self.screen.blit(self.font.render(f"$: {money}", True, cfg.TEXT_WHITE), (20, 20))

        pi = self.am.imgs.get("btn_pause")
        if "btn_pause_hover" in self.am.imgs and self.pause_btn.collidepoint(mx, my): pi = self.am.imgs[
            "btn_pause_hover"]
        if pi: self.screen.blit(pi, pi.get_rect(center=self.pause_btn.center))

        if self.is_shovel_unlocked:
            si = self.am.imgs.get("btn_shovel")
            if (self.is_shovel_active or self.shovel_btn.collidepoint(mx, my)) and "btn_shovel_hover" in self.am.imgs:
                si = self.am.imgs["btn_shovel_hover"]
            if si:
                self.screen.blit(si, si.get_rect(center=self.shovel_btn.center))
                if self.is_shovel_active:
                    pygame.mouse.set_visible(False)
                    cur = self.am.imgs.get("cursor_shovel", si)
                    self.screen.blit(cur, (mx - 30, my - 30))
                else:
                    pygame.mouse.set_visible(True)

    def draw_pause(self):
        if "pause_bg" in self.am.imgs:
            self.screen.blit(self.am.imgs["pause_bg"], (0, 0))
        else:
            s = pygame.Surface((self.W, self.H), pygame.SRCALPHA);
            s.fill((0, 0, 0, 180));
            self.screen.blit(s, (0, 0))
        t = self.title_font.render("PAUSED", True, cfg.COLOR_HEADER);
        self.screen.blit(t, (self.W // 2 - t.get_width() // 2, self.H // 2 - 200))
        cx, cy = self.W // 2, self.H // 2
        self.draw_button(pygame.Rect(cx - 100, cy - 50, 200, 60), "RESUME")
        self.draw_button(pygame.Rect(cx - 100, cy + 30, 200, 60), "RESTART")
        self.draw_button(pygame.Rect(cx - 100, cy + 110, 200, 60), "MENU")
        self.draw_toggle_btn(self.sound_btn, not self.is_muted, "btn_sound_on", "btn_sound_off")
        self.draw_toggle_btn(self.music_btn, not self.is_music_muted, "btn_music_on", "btn_music_off")

    def draw_popup(self, t, b, c):
        s = pygame.Surface((self.W, self.H), pygame.SRCALPHA);
        s.fill((0, 0, 0, 200));
        self.screen.blit(s, (0, 0))
        tt = self.title_font.render(t, True, c);
        self.screen.blit(tt, (self.W // 2 - tt.get_width() // 2, self.H // 3))
        cx, cy = self.W // 2, self.H // 2
        self.draw_button(pygame.Rect(cx - 150, cy, 140, 60), b)
        self.draw_button(pygame.Rect(cx + 10, cy, 140, 60), "MENU")

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT: lib.Engine_Destroy(self.engine); pygame.quit(); sys.exit()
                self.handle_input(e)

            if self.state == "GAME":
                lib.Engine_Update(self.engine, ctypes.c_float(dt))

                if pygame.time.get_ticks() > self.next_groan_time:
                    self.play_random_zombie()
                    self.next_groan_time = pygame.time.get_ticks() + random.randint(5000, 12000)

                snd_cnt = lib.Engine_GetSoundCount(self.engine)
                for i in range(snd_cnt):
                    s_id = lib.Engine_GetSoundData(self.engine, i)
                    if s_id == 1:
                        self.play_sound("pea_hit")
                    elif s_id == 2:
                        now = pygame.time.get_ticks()
                        if now - self.eat_sound_timer > 600: self.play_sound("eat"); self.eat_sound_timer = now
                    elif s_id == 3:
                        self.play_sound("cherry")
                    elif s_id == 4:
                        self.play_sound("imp")
                    elif s_id == 5:
                        self.play_sound("cone_hit")
                    elif s_id == 6:
                        self.play_sound("bucket_hit")
                    elif s_id == 7:
                        self.play_sound("paper_rip")
                    elif s_id == 8:
                        self.play_sound("zombie_angry")

                if lib.Engine_IsLevelComplete(self.engine):
                    is_new_clear = (self.current_level == self.unlocked_level)

                    save_progress(self.current_level)

                    if is_new_clear and self.current_level <= 6:
                        self.just_unlocked_item = self.current_level
                        self.state = "UNLOCK"
                        self.play_sound("win")
                    else:
                        self.state = "WIN"
                        self.play_sound("win")

                    self.unlocked_level = max(self.unlocked_level, self.current_level + 1)
                    p = load_progress()
                    self.available_plants_count = p.get("plants_count", 1)
                    self.is_shovel_unlocked = self.unlocked_level > 4

                if lib.Engine_IsGameOver(self.engine):
                    self.state = "GAMEOVER"
                    self.play_sound("lose")

            self.screen.fill((30, 30, 40))
            if self.state == "MAIN_MENU":
                self.draw_main_menu()
            elif self.state == "LEVEL_SELECT":
                self.draw_level_select()
            elif self.state == "GAME":
                self.draw_game_scene()
            elif self.state == "PAUSE":
                self.draw_game_scene(); self.draw_pause()
            elif self.state == "WIN":
                self.draw_game_scene(); self.draw_popup("LEVEL COMPLETE!", "NEXT", cfg.COLOR_HEADER)
            elif self.state == "GAMEOVER":
                self.draw_game_scene(); self.draw_popup("GAME OVER", "RETRY", (255, 0, 0))
            elif self.state == "UNLOCK":
                self.draw_unlock_screen()
            pygame.display.flip()