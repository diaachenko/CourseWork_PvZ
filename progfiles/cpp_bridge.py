import ctypes
import sys
import os
import config as cfg

if not os.path.exists(cfg.DLL_NAME):
    print(f"CRITICAL ERROR: {cfg.DLL_NAME} missing!")
    sys.exit(1)

lib = ctypes.CDLL(os.path.abspath(cfg.DLL_NAME))

class C_Zombie(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("type", ctypes.c_int),
                ("health", ctypes.c_float), ("max_health", ctypes.c_float),
                ("speed", ctypes.c_float), ("id", ctypes.c_int),
                ("armor_state", ctypes.c_int), ("flags", ctypes.c_int)]

class C_Plant(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("type", ctypes.c_int),
                ("health", ctypes.c_float), ("max_health", ctypes.c_float),
                ("timer", ctypes.c_float), ("max_timer", ctypes.c_float)]

class C_Projectile(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("is_frozen", ctypes.c_int)]

class C_Effect(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("type", ctypes.c_int), ("timer", ctypes.c_float)]

lib.Engine_Create.restype = ctypes.c_void_p
lib.Engine_Destroy.argtypes = [ctypes.c_void_p]
lib.Engine_LoadLevel.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.Engine_Update.argtypes = [ctypes.c_void_p, ctypes.c_float]
lib.Engine_TryBuildPlant.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float, ctypes.c_int]
lib.Engine_RemovePlant.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float]

lib.Engine_GetMoney.argtypes = [ctypes.c_void_p]; lib.Engine_GetMoney.restype = ctypes.c_int
lib.Engine_GetLives.argtypes = [ctypes.c_void_p]; lib.Engine_GetLives.restype = ctypes.c_int
lib.Engine_GetMapWidth.argtypes = [ctypes.c_void_p]; lib.Engine_GetMapWidth.restype = ctypes.c_int
lib.Engine_GetMapHeight.argtypes = [ctypes.c_void_p]; lib.Engine_GetMapHeight.restype = ctypes.c_int
lib.Engine_IsLevelComplete.argtypes = [ctypes.c_void_p]; lib.Engine_IsLevelComplete.restype = ctypes.c_bool
lib.Engine_IsGameOver.argtypes = [ctypes.c_void_p]; lib.Engine_IsGameOver.restype = ctypes.c_bool

lib.Engine_GetZombieCount.argtypes = [ctypes.c_void_p]; lib.Engine_GetZombieCount.restype = ctypes.c_int
lib.Engine_GetZombieData.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(C_Zombie)]
lib.Engine_GetPlantCount.argtypes = [ctypes.c_void_p]; lib.Engine_GetPlantCount.restype = ctypes.c_int
lib.Engine_GetPlantData.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(C_Plant)]
lib.Engine_GetProjectileCount.argtypes = [ctypes.c_void_p]; lib.Engine_GetProjectileCount.restype = ctypes.c_int
lib.Engine_GetProjectileData.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(C_Projectile)]

lib.Engine_GetEffectCount.argtypes = [ctypes.c_void_p]; lib.Engine_GetEffectCount.restype = ctypes.c_int
lib.Engine_GetEffectData.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(C_Effect)]
lib.Engine_GetCardCooldownPct.argtypes = [ctypes.c_void_p, ctypes.c_int]; lib.Engine_GetCardCooldownPct.restype = ctypes.c_float

lib.Engine_GetSoundCount.argtypes = [ctypes.c_void_p]; lib.Engine_GetSoundCount.restype = ctypes.c_int
lib.Engine_GetSoundData.argtypes = [ctypes.c_void_p, ctypes.c_int]; lib.Engine_GetSoundData.restype = ctypes.c_int