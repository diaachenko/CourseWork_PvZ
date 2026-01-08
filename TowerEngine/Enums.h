#pragma once

enum class ZombieType {
    Normal,
    Conehead,
    Buckethead,
    Football,
    Newspaper,
    Imp,
    Gargantuar,
    Flag
};

enum class PlantType {
    Peashooter,
    Sunflower,
    WallNut,
    PotatoMine,
    CherryBomb,
    IceLettuce
};

enum class GameSound {
    None, 
    PeaHit, 
    ZombieEat, 
    CherryExplode, 
    ImpThrow,
    ConeHit,       // 5: ”дар по конусу (пластик)
    BucketHit,     // 6: ”дар по в≥дру (метал)
    PaperRip,      // 7: –ванн€ газети
    ZombieAngry
};
