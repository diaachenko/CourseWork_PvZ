#include "GameEngine.h"
#include <vector>
#define EXPORT extern "C" __declspec(dllexport)

struct C_Zombie { float x, y; int type; float health, max_health, speed; int id; int armor_state; int flags; };
struct C_Plant { float x, y; int type; float health, max_health, timer, max_timer; };
struct C_Projectile { float x, y; int is_frozen; };
struct C_Effect { float x, y; int type; float timer; };

EXPORT GameEngine* Engine_Create() { return new GameEngine(); }
EXPORT void Engine_Destroy(GameEngine* engine) { if (engine) delete engine; }
EXPORT void Engine_LoadLevel(GameEngine* engine, int lvl) { if (engine) engine->load_level(lvl); }
EXPORT void Engine_Update(GameEngine* engine, float dt) { if (engine) engine->update(dt); }
EXPORT void Engine_TryBuildPlant(GameEngine* engine, float x, float y, int card) { if (engine) engine->try_build_plant(x, y, card); }
EXPORT void Engine_RemovePlant(GameEngine* engine, float x, float y) { if (engine) engine->remove_plant_at(x, y); }

EXPORT int Engine_GetMoney(GameEngine* engine) { return engine ? engine->get_money() : 0; }
EXPORT int Engine_GetLives(GameEngine* engine) { return engine ? engine->get_lives() : 0; }
EXPORT int Engine_GetMapWidth(GameEngine* engine) { return engine ? engine->get_map_width() : 0; }
EXPORT int Engine_GetMapHeight(GameEngine* engine) { return engine ? engine->get_map_height() : 0; }
EXPORT bool Engine_IsLevelComplete(GameEngine* engine) { return engine ? engine->is_level_complete() : false; }
EXPORT bool Engine_IsGameOver(GameEngine* engine) { return engine ? engine->is_game_over() : false; }

EXPORT int Engine_GetZombieCount(GameEngine* engine) { return engine ? (int)engine->get_zombies().size() : 0; }
EXPORT bool Engine_GetZombieData(GameEngine* engine, int i, C_Zombie* out) {
    if (!engine || !out || i < 0 || i >= engine->get_zombies().size()) return false;
    auto z = engine->get_zombies()[i];
    out->x = z->pos.x; out->y = z->pos.y; out->type = (int)z->type;
    out->health = z->health; out->max_health = z->max_health;
    out->speed = z->current_speed; out->id = z->id;

    out->armor_state = z->armor_state;

    int flags = 0;
    if (z->has_arm) flags |= 1;
    if (z->has_newspaper) flags |= 2;
    if (z->freeze_timer > 0) flags |= 8;

    out->flags = flags;
    return true;
}

EXPORT int Engine_GetPlantCount(GameEngine* engine) { return engine ? (int)engine->get_plants().size() : 0; }
EXPORT bool Engine_GetPlantData(GameEngine* engine, int i, C_Plant* out) {
    if (!engine || !out || i < 0 || i >= engine->get_plants().size()) return false;
    auto p = engine->get_plants()[i];
    out->x = p->pos.x; out->y = p->pos.y; out->type = (int)p->type;
    out->health = p->health; out->max_health = p->max_health;
    out->timer = p->cooldown_timer; out->max_timer = p->action_cooldown;
    return true;
}

EXPORT int Engine_GetProjectileCount(GameEngine* engine) { return engine ? (int)engine->get_projectiles().size() : 0; }
EXPORT bool Engine_GetProjectileData(GameEngine* engine, int i, C_Projectile* out) {
    if (!engine || !out || i < 0 || i >= engine->get_projectiles().size()) return false;
    auto p = engine->get_projectiles()[i];
    out->x = p->pos.x; out->y = p->pos.y;
    return true;
}

EXPORT int Engine_GetEffectCount(GameEngine* engine) { return engine ? (int)engine->get_effects().size() : 0; }
EXPORT bool Engine_GetEffectData(GameEngine* engine, int i, C_Effect* out) {
    if (!engine || !out || i < 0 || i >= engine->get_effects().size()) return false;
    auto e = engine->get_effects()[i];
    out->x = e.x; out->y = e.y; out->type = e.type; out->timer = e.timer;
    return true;
}

EXPORT float Engine_GetCardCooldownPct(GameEngine* engine, int id) { return engine ? engine->get_card_cooldown_pct(id) : 0.0f; }

EXPORT int Engine_GetSoundCount(GameEngine* engine) { return engine ? (int)engine->get_sounds().size() : 0; }
EXPORT int Engine_GetSoundData(GameEngine* engine, int i) {
    if (!engine || i < 0 || i >= engine->get_sounds().size()) return 0;
    return engine->get_sounds()[i];
}