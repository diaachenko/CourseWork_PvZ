#pragma once
#include <vector>
#include <nlohmann/json.hpp> 
#include "Vec.h"

using json = nlohmann::json;

class GameMap {
public:
    int width, height;
    float tile_w = 110.0f;
    float tile_h = 141.0f;
    std::vector<int> grid;
    std::vector<int> active_rows;

    GameMap() : width(9), height(5) {}

    void load_from_json(const json& settings) {
        width = settings.value("width", 9);
        height = settings.value("height", 5);
        grid.assign(width * height, 0);

        active_rows.clear();
        if (settings.contains("active_rows")) {
            for (int r : settings["active_rows"]) active_rows.push_back(r);
        }
        else {
            for (int i = 0; i < height; i++) active_rows.push_back(i);
        }
    }

    bool is_buildable(float x, float y) {
        int gx = (int)(x / tile_w);
        int gy = (int)(y / tile_h);

        if (gx < 0 || gx >= width || gy < 0 || gy >= height) return false;

        bool row_allowed = false;
        for (int r : active_rows) {
            if (gy == r) { row_allowed = true; break; }
        }
        if (!row_allowed) return false;

        return grid[gy * width + gx] == 0;
    }
};