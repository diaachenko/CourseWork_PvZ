#pragma once
#include <cmath>

struct Vec {
    float x, y;

    Vec() : x(0), y(0) {}
    Vec(float x, float y) : x(x), y(y) {}

    Vec operator+(const Vec& other) const { return { x + other.x, y + other.y }; }
    Vec operator-(const Vec& other) const { return { x - other.x, y - other.y }; }
    Vec operator*(float scalar) const { return { x * scalar, y * scalar }; }

    float length() const { return std::sqrt(x * x + y * y); }

    Vec normalized() const {
        float len = length();
        return len > 0 ? Vec(x / len, y / len) : Vec(0, 0);
    }

    static float distance(const Vec& a, const Vec& b) {
        return (a - b).length();
    }
};
