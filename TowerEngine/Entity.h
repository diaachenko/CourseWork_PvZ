#pragma once
#include "Vec.h"

class Entity {
    public:
        int id;
        Vec pos;
        float radius;
        bool to_delete;

        static int next_id;

        Entity(float x, float y, float r) : pos(x, y), radius(r), to_delete(false) {
            id = next_id++;
        }

        virtual ~Entity() = default;

        virtual void update(float dt, float data = 1.0f) = 0;
};


inline int Entity::next_id = 0;