#pragma once
#include "Entity.h"
#include "Enums.h"
#include <vector>
#include <memory>
#include <algorithm>
#include <cmath>

class Zombie;

struct VisualEffect {
    float x, y;
    int type;    //0 = Mine, 1 = Cherry, 2 = Ice
    float timer;
};

class Projectile : public Entity {
public:
    Vec velocity;
    float damage;
    bool hit_triggered;

    Projectile(float x, float y, Vec target, float speed, float dmg)
        : Entity(x, y, 20.0f), damage(dmg), hit_triggered(false) {
        Vec dir = (target - pos).normalized();
        velocity = dir * speed;
    }
    void update(float dt, float data = 1.0f) override {
        pos = pos + velocity * dt;
        if (pos.x > 2000 || pos.x < -200) to_delete = true;
    }
};

class Zombie : public Entity {
public:
    ZombieType type;
    float health; float max_health; float body_health;
    float speed_base; float current_speed;
    float freeze_timer;
    float damage;
    int id;
    int path_index;
    const std::vector<Vec>* path_ref;

    int armor_state;
    bool has_arm;
    bool has_newspaper;

    Zombie(ZombieType t, float x, float y)
        : Entity(x, y, 40.0f), type(t), freeze_timer(0.0f) {
        speed_base = 30.0f; current_speed = speed_base;
        max_health = 125.0f; body_health = 125.0f; health = 125.0f;
        damage = 30.0f;
        armor_state = 0; has_arm = true; has_newspaper = false;
    }

    virtual void take_damage(float amount) {
        health -= amount;
        if (health <= 0) to_delete = true;
        update_visual_state();
    }

    virtual void update_visual_state() {
        if (type != ZombieType::Gargantuar && health < body_health * 0.5f) has_arm = false;
    }

    void apply_freeze(float duration) { freeze_timer = duration; }

    void update(float dt, float move_multiplier = 1.0f) override {
        float effective_speed = speed_base;

        if (freeze_timer > 0) {
            freeze_timer -= dt;
            effective_speed *= 0.0f;
        }

        current_speed = effective_speed * move_multiplier;
        pos.x -= current_speed * dt;
    }
};

class NormalZombie : public Zombie { public: NormalZombie(float x, float y) : Zombie(ZombieType::Normal, x, y) {} };

class ConeheadZombie : public Zombie {
public:
    ConeheadZombie(float x, float y) : Zombie(ZombieType::Conehead, x, y) {
        body_health = 125; max_health = body_health + 150; health = max_health; armor_state = 1;
    }
    void update_visual_state() override {
        float current_armor = health - body_health;
        if (current_armor <= 0) armor_state = 0;
        else if (current_armor < 50) armor_state = 3;
        else if (current_armor < 100) armor_state = 2;
        else armor_state = 1;
        Zombie::update_visual_state();
    }
};

class BucketheadZombie : public Zombie {
public:
    BucketheadZombie(float x, float y) : Zombie(ZombieType::Buckethead, x, y) {
        body_health = 125; max_health = body_health + 325; health = max_health; armor_state = 1;
    }
    void update_visual_state() override {
        float current_armor = health - body_health;
        if (current_armor <= 0) armor_state = 0;
        else if (current_armor < 125) armor_state = 3;
        else if (current_armor < 275) armor_state = 2;
        else armor_state = 1;
        Zombie::update_visual_state();
    }
};

class FootballZombie : public Zombie {
public:
    FootballZombie(float x, float y) : Zombie(ZombieType::Football, x, y) {
        body_health = 125; max_health = body_health + 325; health = max_health; speed_base = 35; armor_state = 1;
    }
    void update_visual_state() override {
        if (health <= body_health) armor_state = 0;
        Zombie::update_visual_state();
    }
};

class NewspaperZombie : public Zombie {
public:
    NewspaperZombie(float x, float y) : Zombie(ZombieType::Newspaper, x, y) {
        body_health = 125; max_health = body_health + 100; health = max_health; has_newspaper = true;
    }
    void update_visual_state() override {
        if (health <= body_health && has_newspaper) {
            has_newspaper = false; speed_base = 40.0f;
        }
        Zombie::update_visual_state();
    }
};

class ImpZombie : public Zombie { public: ImpZombie(float x, float y) : Zombie(ZombieType::Imp, x, y) { max_health = 100; health = 100; speed_base = 40; } };

class GargantuarZombie : public Zombie {
public:
    GargantuarZombie(float x, float y) : Zombie(ZombieType::Gargantuar, x, y) {
        max_health = 3000; health = 3000; speed_base = 20; radius = 80; damage = 5000;
    };
};

class FlagZombie : public Zombie { public: FlagZombie(float x, float y) : Zombie(ZombieType::Flag, x, y) { speed_base = 45; } };

class Plant : public Entity {
public:
    PlantType type;
    float health; float max_health;
    float cost;
    float cooldown_timer;
    float action_cooldown;

    Plant(PlantType t, float x, float y)
        : Entity(x, y, 40.0f), type(t), cooldown_timer(0.0f), cost(0.0f) {
        max_health = 100.0f; health = 100.0f; action_cooldown = 1.5f;
    }
    virtual void take_damage(float amount) {
        health -= amount;
        if (health <= 0) to_delete = true;
    }
    virtual int produce_money() { return 0; }
    virtual void update_logic(float dt, const std::vector<std::shared_ptr<Zombie>>& z,
        std::vector<std::shared_ptr<Projectile>>& p,
        std::vector<VisualEffect>& e,
        std::vector<int>& sounds) = 0;

    void update(float dt, float data = 1.0f) override {
        if (cooldown_timer > 0) cooldown_timer -= dt;
    }
};

class Peashooter : public Plant {
public:
    Peashooter(float x, float y) : Plant(PlantType::Peashooter, x, y) { cost = 100; action_cooldown = 1.5f; }
    void update_logic(float dt, const std::vector<std::shared_ptr<Zombie>>& zombies,
        std::vector<std::shared_ptr<Projectile>>& projectiles,
        std::vector<VisualEffect>&, std::vector<int>&) override {
        if (cooldown_timer > 0) return;
        int my_row = (int)(pos.y / 180.0f);

        for (const auto& z : zombies) {
            if (z->to_delete) continue;
            int zombie_row = (int)(z->pos.y / 180.0f);

            if (my_row == zombie_row && z->pos.x > pos.x && z->pos.x < 1500.0f) {
                auto proj = std::make_shared<Projectile>(pos.x + 60, pos.y - 25, Vec(z->pos.x, pos.y - 25), 500.0f, 20.0f);
                projectiles.push_back(proj);
                cooldown_timer = action_cooldown;
                break;
            }
        }
    }
};

class Sunflower : public Plant {
public:
    Sunflower(float x, float y) : Plant(PlantType::Sunflower, x, y) { cost = 50; action_cooldown = 10.0f; cooldown_timer = 5.0f; }
    void update_logic(float dt, const std::vector<std::shared_ptr<Zombie>>& z,
        std::vector<std::shared_ptr<Projectile>>& p,
        std::vector<VisualEffect>& e,
        std::vector<int>& sounds) override {}
    int produce_money() override {
        if (cooldown_timer <= 0) { cooldown_timer = action_cooldown; return 25; }
        return 0;
    }
};

class WallNut : public Plant {
public:
    WallNut(float x, float y) : Plant(PlantType::WallNut, x, y) { cost = 50; health = max_health = 2000.0f; }
    void update_logic(float dt, const std::vector<std::shared_ptr<Zombie>>& z,
        std::vector<std::shared_ptr<Projectile>>& p,
        std::vector<VisualEffect>& e,
        std::vector<int>& sounds) override {}
};

class PotatoMine : public Plant {
public:
    bool is_armed;
    PotatoMine(float x, float y) : Plant(PlantType::PotatoMine, x, y), is_armed(false) {
        cost = 25; action_cooldown = 12.0f; cooldown_timer = action_cooldown;
    }
    void update_logic(float dt, const std::vector<std::shared_ptr<Zombie>>& zombies,
        std::vector<std::shared_ptr<Projectile>>&, std::vector<VisualEffect>& effects,
        std::vector<int>& sounds) override {
        if (!is_armed) {
            if (cooldown_timer <= 0) is_armed = true;
            return;
        }

        bool triggered = false;
        for (const auto& z : zombies) {
            if (z->to_delete) continue;
            if (Vec::distance(pos, z->pos) < 60.0f) { triggered = true; break; }
        }

        if (triggered) {
            for (const auto& z : zombies) {
                if (z->to_delete) continue;
                if (Vec::distance(pos, z->pos) < 150.0f) { z->take_damage(1000.0f); }
            }
            effects.push_back({ pos.x, pos.y, 0, 0.5f });
            sounds.push_back((int)GameSound::CherryExplode);
            this->to_delete = true;
        }
    }
};

class CherryBomb : public Plant {
public:
    CherryBomb(float x, float y) : Plant(PlantType::CherryBomb, x, y) {
        cost = 150; health = 1000;
        action_cooldown = 1.2f;
        cooldown_timer = action_cooldown;
    }
    void update_logic(float dt, const std::vector<std::shared_ptr<Zombie>>& zombies,
        std::vector<std::shared_ptr<Projectile>>&, std::vector<VisualEffect>& effects,
        std::vector<int>& sounds) override {
        if (cooldown_timer <= 0) {
            for (const auto& z : zombies) {
                if (Vec::distance(pos, z->pos) < 200.0f) { z->take_damage(1800.0f); }
            }
            effects.push_back({ pos.x, pos.y, 1, 1.2f });
            sounds.push_back(3);
            this->to_delete = true;
        }
    }
};

class IceLettuce : public Plant {
public:
    IceLettuce(float x, float y) : Plant(PlantType::IceLettuce, x, y) { cost = 0; health = 50; }
    void update_logic(float dt, const std::vector<std::shared_ptr<Zombie>>& zombies,
        std::vector<std::shared_ptr<Projectile>>&, std::vector<VisualEffect>& effects,
        std::vector<int>& sounds) override {
        for (const auto& z : zombies) {
            if (z->to_delete) continue;
            if (Vec::distance(pos, z->pos) < 90.0f) {
                z->take_damage(20.0f);
                z->apply_freeze(10.0f);
                effects.push_back({ pos.x, pos.y, 2, 0.5f });
                this->to_delete = true;
                break;
            }
        }
    }
};