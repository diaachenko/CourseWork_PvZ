#pragma once
#include <vector>
#include <memory>
#include <algorithm>
#include <iostream>
#include <fstream>
#include <nlohmann/json.hpp> 
#include "GameObjects.h"
#include "GameMap.h"

using json = nlohmann::json;

struct PlantCard {
    PlantType type; int cost; float current_cooldown; float max_cooldown;
    PlantCard(PlantType t, int c, float max_cd) : type(t), cost(c), max_cooldown(max_cd), current_cooldown(0.0f) {}
};

class GameEngine {
    GameMap map;
    std::vector<std::shared_ptr<Zombie>> zombies;
    std::vector<std::shared_ptr<Plant>> plants;
    std::vector<std::shared_ptr<Projectile>> projectiles;
    std::vector<VisualEffect> effects;
    std::vector<PlantCard> cards;
    std::vector<int> sound_events;

    float level_time;
    float auto_sun_timer; float auto_sun_interval; int auto_sun_amount;
    int money; int lives;

    struct WaveEvent { float time; ZombieType type; int row; };
    std::vector<WaveEvent> pending_waves;
    bool level_completed; bool game_over;

public:
    GameEngine() : level_time(0), auto_sun_timer(0), money(0), lives(0), level_completed(false), game_over(false) {
        cards.push_back(PlantCard(PlantType::Peashooter, 100, 5.0f));
        cards.push_back(PlantCard(PlantType::Sunflower, 50, 5.0f));
        cards.push_back(PlantCard(PlantType::WallNut, 50, 20.0f));
        cards.push_back(PlantCard(PlantType::PotatoMine, 25, 20.0f));
        cards.push_back(PlantCard(PlantType::CherryBomb, 150, 30.0f));
        cards.push_back(PlantCard(PlantType::IceLettuce, 0, 15.0f));
    }

    const std::vector<std::shared_ptr<Zombie>>& get_zombies() const { return zombies; }
    const std::vector<std::shared_ptr<Plant>>& get_plants() const { return plants; }
    const std::vector<std::shared_ptr<Projectile>>& get_projectiles() const { return projectiles; }
    const std::vector<VisualEffect>& get_effects() const { return effects; }
    const std::vector<int>& get_sounds() const { return sound_events; }

    int get_money() const { return money; }
    int get_lives() const { return lives; }
    int get_map_width() const { return map.width; }
    int get_map_height() const { return map.height; }
    bool is_level_complete() const { return level_completed; }
    bool is_game_over() const { return game_over; }

    float get_card_cooldown_pct(int index) {
        if (index < 0 || index >= cards.size()) return 0.0f;
        if (cards[index].current_cooldown <= 0) return 0.0f;
        return cards[index].current_cooldown / cards[index].max_cooldown;
    }

    void remove_plant_at(float x, float y) {
        int gx = (int)(x / map.tile_w);
        int gy = (int)(y / map.tile_h);
        float cx = gx * map.tile_w + map.tile_w / 2.0f;
        float cy = gy * map.tile_h + map.tile_h / 2.0f;

        for (auto& p : plants) {
            if (!p->to_delete && std::abs(p->pos.x - cx) < 20.0f && std::abs(p->pos.y - cy) < 20.0f) {
                p->to_delete = true; return;
            }
        }
    }

    void load_level(int level_id) {
        zombies.clear(); plants.clear(); projectiles.clear(); pending_waves.clear(); effects.clear(); sound_events.clear();
        for (auto& c : cards) c.current_cooldown = 0.0f;
        level_time = 0; level_completed = false; game_over = false;

        std::string path = "levels/level_" + std::to_string(level_id) + ".json";
        std::ifstream file(path);

        json j; file >> j;
        auto settings = j["settings"];
        money = settings.value("start_money", 50);
        lives = settings.value("lives", 5);
        auto_sun_amount = settings.value("auto_sun_amount", 25);
        auto_sun_interval = settings.value("auto_sun_interval", 10.0f);
        auto_sun_timer = auto_sun_interval;

        map.load_from_json(settings);

        for (const auto& w : j["waves"]) {
            float t = w["time"]; int r = w["row"]; int type_id = w["type"];
            pending_waves.push_back({ t, static_cast<ZombieType>(type_id), r });
        }
        std::sort(pending_waves.begin(), pending_waves.end(), [](const auto& a, const auto& b) { return a.time < b.time; });
    }

    void update(float dt) {
        sound_events.clear();

        if (game_over || level_completed) return;
        level_time += dt;

        for (auto& c : cards) if (c.current_cooldown > 0) c.current_cooldown -= dt;
        for (auto& e : effects) e.timer -= dt;
        effects.erase(std::remove_if(effects.begin(), effects.end(), [](const auto& e) { return e.timer <= 0; }), effects.end());

        auto_sun_timer -= dt;
        if (auto_sun_timer <= 0) { money += auto_sun_amount; auto_sun_timer = auto_sun_interval; }

        while (!pending_waves.empty() && pending_waves.front().time <= level_time) {
            WaveEvent ev = pending_waves.front();
            spawn_zombie_at_row(ev.type, ev.row);
            pending_waves.erase(pending_waves.begin());
        }

        float speed_multiplier = 1.0f;
        for (const auto& z : zombies) { if (z->type == ZombieType::Flag && !z->to_delete) { speed_multiplier = 1.3f; break; } }

        for (auto& z : zombies) {
            if (z->to_delete) continue;

            float move_mult = 1.0f;
            bool is_eating = false;

            for (auto& p : plants) {
                if (p->to_delete) continue;

                int z_row = (int)(z->pos.y / map.tile_h);
                int p_row = (int)(p->pos.y / map.tile_h);

                if (z_row == p_row && std::abs(z->pos.x - p->pos.x) < 50.0f) {
                    bool safe_to_eat = true;
                    if (p->type == PlantType::PotatoMine) {
                        auto mine = std::static_pointer_cast<PotatoMine>(p);
                        if (mine->is_armed) safe_to_eat = false;
                    }

                    if (safe_to_eat) {
                        p->take_damage(z->damage * dt);
                        is_eating = true;
                        if (std::rand() % 100 < 5) sound_events.push_back((int)GameSound::ZombieEat);
                        break;
                    }
                }
            }

            if (is_eating) move_mult = 0.0f;

            z->update(dt, move_mult * speed_multiplier);

            if (z->pos.x < -50.0f) {
                z->to_delete = true;
                lives--;
                if (lives <= 0) game_over = true;
            }
        }

        for (auto& p : plants) {
            p->update(dt);
            p->update_logic(dt, zombies, projectiles, effects, sound_events);
            money += p->produce_money();
        }

        for (auto& proj : projectiles) {
            proj->update(dt);
            if (proj->to_delete) continue;
            for (auto& z : zombies) {
                if (!z->to_delete && Vec::distance(proj->pos, z->pos) < z->radius) {
                    bool had_paper = z->has_newspaper;

                    z->take_damage(proj->damage);
                    proj->to_delete = true;

                    bool hit_armor = false;

                    if (z->health > z->body_health) {
                        if (z->type == ZombieType::Conehead) {
                            sound_events.push_back((int)GameSound::ConeHit);
                            hit_armor = true;
                        }
                        else if (z->type == ZombieType::Buckethead || z->type == ZombieType::Football) {
                            sound_events.push_back((int)GameSound::BucketHit);
                            hit_armor = true;
                        }
                    }

                    if (!hit_armor) {
                        sound_events.push_back((int)GameSound::PeaHit);
                    }

                    if (had_paper && !z->has_newspaper) {
                        sound_events.push_back((int)GameSound::PaperRip);
                        sound_events.push_back((int)GameSound::ZombieAngry);
                    }

                    break;
                }
            }
        }

        zombies.erase(std::remove_if(zombies.begin(), zombies.end(), [](const auto& o) { return o->to_delete; }), zombies.end());
        plants.erase(std::remove_if(plants.begin(), plants.end(), [](const auto& o) { return o->to_delete; }), plants.end());
        projectiles.erase(std::remove_if(projectiles.begin(), projectiles.end(), [](const auto& o) { return o->to_delete; }), projectiles.end());

        if (pending_waves.empty() && zombies.empty() && lives > 0) level_completed = true;
    }

    void spawn_zombie_at_row(ZombieType type, int row) {
        if (row < 0 || row >= map.height) return;

        float start_x = map.width * map.tile_w + 100.0f;
        float start_y = row * map.tile_h + map.tile_h / 2.0f;

        std::shared_ptr<Zombie> z = nullptr;

        switch (type) {
        case ZombieType::Normal: z = std::make_shared<NormalZombie>(start_x, start_y); break;
        case ZombieType::Conehead: z = std::make_shared<ConeheadZombie>(start_x, start_y); break;
        case ZombieType::Buckethead: z = std::make_shared<BucketheadZombie>(start_x, start_y); break;
        case ZombieType::Football: z = std::make_shared<FootballZombie>(start_x, start_y); break;
        case ZombieType::Newspaper: z = std::make_shared<NewspaperZombie>(start_x, start_y); break;
        case ZombieType::Imp: z = std::make_shared<ImpZombie>(start_x, start_y); break;
        case ZombieType::Gargantuar: z = std::make_shared<GargantuarZombie>(start_x, start_y); break;
        case ZombieType::Flag: z = std::make_shared<FlagZombie>(start_x, start_y); break;
        }

        if (z) {
            z->id = Entity::next_id++;
            zombies.push_back(z);
        }
    }

    void try_build_plant(float x, float y, int card_index) {
        if (card_index < 0 || card_index >= cards.size()) return;
        auto& card = cards[card_index];
        if (card.current_cooldown > 0) return;
        if (money < card.cost) return;
        if (!map.is_buildable(x, y)) return;

        int gx = (int)(x / map.tile_w);
        int gy = (int)(y / map.tile_h);
        float cx = gx * map.tile_w + map.tile_w / 2.0f;
        float cy = gy * map.tile_h + map.tile_h / 2.0f;

        for (const auto& p : plants) {
            if (Vec::distance({ cx, cy }, p->pos) < 30.0f) return;
        }

        std::shared_ptr<Plant> p = nullptr;
        switch (card.type) {
        case PlantType::Peashooter: p = std::make_shared<Peashooter>(cx, cy); break;
        case PlantType::Sunflower: p = std::make_shared<Sunflower>(cx, cy); break;
        case PlantType::WallNut: p = std::make_shared<WallNut>(cx, cy); break;
        case PlantType::PotatoMine: p = std::make_shared<PotatoMine>(cx, cy); break;
        case PlantType::CherryBomb: p = std::make_shared<CherryBomb>(cx, cy); break;
        case PlantType::IceLettuce: p = std::make_shared<IceLettuce>(cx, cy); break;
        }

        if (p) {
            plants.push_back(p);
            money -= card.cost;
            card.current_cooldown = card.max_cooldown;
        }
    }
};