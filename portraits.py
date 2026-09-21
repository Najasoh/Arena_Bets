"""Class portrait generation for Simulated Arena.

Paints a small procedural portrait for every class and caches it to disk.
"""

import os

import pygame

from colors import *
from classes import CLASSES, HEAL_PICKS

BASE = os.path.dirname(os.path.abspath(__file__))
PORT_DIR = os.path.join(BASE, "portraits")
os.makedirs(PORT_DIR, exist_ok=True)


PORTRAITS = {}


def _paint_portrait(cls, size=128):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    if cls == "Mage":
        bg, hood, skin, accent = (28, 42, 92), (36, 48, 110), (210, 175, 145), ICE
    elif cls == "Rogue":
        bg, hood, skin, accent = (22, 48, 30), (18, 32, 22), (196, 156, 120), (180, 200, 160)
    elif cls == "Double Dragon":
        bg, hood, skin, accent = (90, 28, 16), (120, 36, 18), (210, 175, 140), FIRE
    elif cls == "Warrior":
        bg, hood, skin, accent = (72, 32, 24), (90, 50, 36), (205, 168, 130), (200, 200, 210)
    elif cls == "Warlock":
        bg, hood, skin, accent = (42, 18, 52), (28, 10, 36), (180, 140, 120), FIRE
    elif cls == "Dark Cultist":
        bg, hood, skin, accent = (24, 12, 34), (16, 8, 24), (150, 130, 140), (150, 60, 200)
    elif cls == "Beast Master":
        bg, hood, skin, accent = (46, 62, 30), (60, 78, 38), (205, 172, 132), (150, 200, 90)
    elif cls == "Thumper":
        bg, hood, skin, accent = (62, 48, 28), (80, 60, 32), (200, 165, 125), (160, 140, 90)
    elif cls == "Bellringer":
        bg, hood, skin, accent = (40, 50, 70), (180, 170, 90), (210, 180, 150), GOLD
    elif cls == "Trident":
        bg, hood, skin, accent = (20, 70, 110), (16, 50, 88), (190, 170, 145), WATER
    elif cls == "Lingwah":
        bg, hood, skin, accent = (111, 70, 33), (180, 50, 170), (190, 170, 145), WATER
    elif cls == "Spiritualist":
        bg, hood, skin, accent = (36, 42, 70), (220, 230, 245), (200, 185, 170), SPIRIT
    elif cls == "Zealous":
        bg, hood, skin, accent = (48, 52, 80), (240, 240, 250), (210, 190, 160), MANA
    elif cls == "Slasher":
        bg, hood, skin, accent = (48, 22, 70), (30, 16, 48), (200, 170, 145), GLASS
    elif cls == "Seeping":
        bg, hood, skin, accent = (70, 40, 18), (90, 50, 20), (205, 175, 140), GOLD
    elif cls == "Elementalist":
        bg, hood, skin, accent = (90, 28, 16), (120, 36, 18), (210, 175, 140), FIRE
    elif cls == "Stoning":
        bg, hood, skin, accent = (62, 52, 36), (80, 70, 48), (200, 170, 135), (160, 140, 100)
    elif cls == "Balthazar":
        bg, hood, skin, accent = (90, 30, 16), (200, 160, 50), (205, 175, 140), GOLD
    elif cls == "Ether":
        bg, hood, skin, accent = (40, 48, 92), (220, 230, 255), (205, 180, 150), MANA
    elif cls == "Ranger":
        bg, hood, skin, accent = (28, 62, 32), (40, 80, 36), (205, 175, 140), (180, 210, 90)
    elif cls == "Expeller":
        bg, hood, skin, accent = (22, 40, 48), (70, 30, 90), (200, 175, 150), (40, 140, 140)
    elif cls == "Bonder":
        bg, hood, skin, accent = (18, 70, 80), (140, 230, 230), (205, 180, 150), (80, 210, 210)
    elif cls == "Deathdancer":
        bg, hood, skin, accent = (28, 40, 28), (50, 60, 50), (180, 160, 140), (90, 140, 70)
    elif cls == "Mesmer":
        bg, hood, skin, accent = (70, 28, 80), (160, 80, 170), (210, 175, 150), (230, 120, 210)
    elif cls == "Escaper":
        bg, hood, skin, accent = (40, 48, 70), (230, 230, 245), (205, 180, 150), (80, 40, 90)
    elif cls == "Glimmer":
        bg, hood, skin, accent = (20, 70, 120), (180, 230, 255), (205, 180, 150), (120, 210, 255)
    elif cls == "Deadsword":
        bg, hood, skin, accent = (48, 28, 22), (70, 40, 28), (200, 165, 130), (180, 160, 80)
    elif cls == "Migraine":
        bg, hood, skin, accent = (50, 20, 70), (140, 50, 160), (210, 180, 160), (220, 80, 180)
    elif cls == "Surger":
        bg, hood, skin, accent = (20, 30, 70), (180, 210, 255), (200, 175, 150), (255, 230, 80)
    elif cls == "Lifesheath":
        bg, hood, skin, accent = (30, 70, 50), (80, 180, 120), (210, 190, 160), (220, 230, 140)
    elif cls == "PermaShadow":
        bg, hood, skin, accent = (18, 12, 28), (70, 30, 90), (160, 140, 150), (120, 40, 160)
    elif cls == "Riposte":
        bg, hood, skin, accent = (40, 40, 48), (230, 230, 240), (200, 180, 160), WHITE
    elif cls == "AirEnchant":
        bg, hood, skin, accent = (40, 90, 120), (180, 230, 255), (210, 190, 170), (120, 210, 180)
    elif cls == "Judge":
        bg, hood, skin, accent = (30, 50, 90), (220, 210, 120), (200, 180, 155), (255, 230, 90)
    elif cls == "Conditioner":
        bg, hood, skin, accent = (40, 80, 70), (160, 230, 200), (205, 185, 160), (90, 210, 170)
    else:
        bg, hood, skin, accent = (70, 58, 28), (240, 236, 220), (220, 185, 150), HOLY2
    pygame.draw.circle(s, bg, (cx, cy), cx - 2)
    pygame.draw.ellipse(s, hood, (cx - size * 0.42, cy + size * 0.08, size * 0.84, size * 0.55))
    pygame.draw.ellipse(s, skin, (cx - size * 0.22, cy - size * 0.22, size * 0.44, size * 0.5))
    if cls == "Mage":
        pygame.draw.polygon(s, hood, [(cx, cy - size * 0.46), (cx - size * 0.32, cy + size * 0.08), (cx + size * 0.32, cy + size * 0.08)])
        pygame.draw.circle(s, accent, (cx, cy - size * 0.18), 7)
        pygame.draw.circle(s, WHITE, (cx, cy - size * 0.18), 3)
    elif cls == "Rogue":
        pygame.draw.rect(s, (12, 16, 14), (cx - size * 0.22, cy - size * 0.06, size * 0.44, size * 0.12))
        pygame.draw.polygon(s, accent, [(cx + size * 0.08, cy + size * 0.18), (cx + size * 0.28, cy - size * 0.02), (cx + size * 0.22, cy + size * 0.22)])
    elif cls == "Warrior":
        pygame.draw.rect(s, accent, (cx - size * 0.26, cy - size * 0.18, size * 0.52, size * 0.16), border_radius=3)
        pygame.draw.circle(s, GOLD, (cx, cy - size * 0.1), 5)
        pygame.draw.rect(s, (160, 160, 170), (cx - 6, cy + size * 0.22, 12, size * 0.2))
    elif cls == "Lingwah":
        pygame.draw.circle(s, accent, (cx, cy + size * 0.14), 10)
        pygame.draw.circle(s, (255, 220, 90), (cx, cy + size * 0.14), 4)
        pygame.draw.polygon(s, (80, 200, 220), [(cx, cy - size * 0.4), (cx - 8, cy - size * 0.1), (cx + 8, cy - size * 0.1)])
    elif cls == "Warlock":
        pygame.draw.polygon(s, hood, [(cx - size * 0.28, cy - size * 0.02), (cx - size * 0.18, cy - size * 0.42), (cx - size * 0.08, cy - size * 0.12)])
        pygame.draw.polygon(s, hood, [(cx + size * 0.28, cy - size * 0.02), (cx + size * 0.18, cy - size * 0.42), (cx + size * 0.08, cy - size * 0.12)])
        pygame.draw.circle(s, FIRE, (cx, cy + size * 0.22), 7)
        pygame.draw.circle(s, (40, 10, 10), (cx, cy + size * 0.22), 3)
    elif cls == "Dark Cultist":
        pygame.draw.polygon(s, hood, [(cx, cy - size * 0.46), (cx - size * 0.34, cy + size * 0.1), (cx + size * 0.34, cy + size * 0.1)])
        pygame.draw.circle(s, (150, 60, 200), (cx, cy - size * 0.16), 6)
        pygame.draw.circle(s, (30, 10, 40), (cx, cy - size * 0.16), 3)
        pygame.draw.circle(s, (90, 40, 120), (cx - size * 0.24, cy + size * 0.2), 5)
        pygame.draw.circle(s, (90, 40, 120), (cx + size * 0.24, cy + size * 0.2), 5)
    elif cls == "Double Dragon":
        pygame.draw.polygon(s, hood, [(cx - size * 0.28, cy - size * 0.02), (cx - size * 0.18, cy - size * 0.42), (cx - size * 0.08, cy - size * 0.12)])
        pygame.draw.polygon(s, hood, [(cx + size * 0.28, cy - size * 0.02), (cx + size * 0.18, cy - size * 0.42), (cx + size * 0.08, cy - size * 0.12)])
        pygame.draw.circle(s, FIRE, (cx, cy + size * 0.22), 7)
        pygame.draw.circle(s, (40, 10, 10), (cx, cy + size * 0.22), 3)
    elif cls == "Thumper":
        pygame.draw.rect(s, (90, 70, 40), (cx - 5, cy + size * 0.05, 10, size * 0.35))
        pygame.draw.circle(s, accent, (cx, cy + size * 0.08), 12)
        pygame.draw.circle(s, (40, 30, 16), (cx + size * 0.22, cy + size * 0.18), 8)
    elif cls == "Bellringer":
        pygame.draw.polygon(s, GOLD, [(cx, cy + size * 0.08), (cx - size * 0.18, cy + size * 0.32), (cx + size * 0.18, cy + size * 0.32)])
        pygame.draw.circle(s, GOLD, (cx, cy + size * 0.1), 6)
    elif cls == "Trident":
        pygame.draw.line(s, WATER, (cx, cy + size * 0.32), (cx, cy - size * 0.28), 4)
        pygame.draw.polygon(s, accent, [(cx, cy - size * 0.36), (cx - size * 0.16, cy - size * 0.12), (cx, cy - size * 0.18), (cx + size * 0.16, cy - size * 0.12)])
        pygame.draw.circle(s, ICE, (cx, cy + size * 0.18), 5)
    elif cls == "Spiritualist":
        pygame.draw.ellipse(s, SPIRIT, (cx - size * 0.16, cy - size * 0.42, size * 0.32, size * 0.22))
        pygame.draw.circle(s, WHITE, (cx, cy + size * 0.18), 8)
        pygame.draw.circle(s, (140, 180, 220), (cx, cy + size * 0.18), 3)
    elif cls == "Zealous":
        pygame.draw.polygon(s, WHITE, [(cx, cy - size * 0.38), (cx - 6, cy - size * 0.08), (cx + 6, cy - size * 0.08)])
        pygame.draw.circle(s, MANA, (cx, cy + size * 0.16), 9)
        pygame.draw.circle(s, WHITE, (cx, cy + size * 0.16), 3)
    elif cls == "Slasher":
        pygame.draw.polygon(s, GLASS, [(cx + size * 0.28, cy - size * 0.1), (cx + size * 0.08, cy + size * 0.28), (cx + size * 0.18, cy + size * 0.3)])
        pygame.draw.polygon(s, WHITE, [(cx + size * 0.22, cy - size * 0.16), (cx + size * 0.3, cy - size * 0.02), (cx + size * 0.16, cy - size * 0.02)])
    elif cls == "Seeping":
        pygame.draw.line(s, GOLD, (cx - size * 0.22, cy + size * 0.28), (cx + size * 0.26, cy - size * 0.28), 3)
        pygame.draw.polygon(s, GOLD, [(cx + size * 0.28, cy - size * 0.32), (cx + size * 0.12, cy - size * 0.18), (cx + size * 0.22, cy - size * 0.12)])
        pygame.draw.circle(s, RED, (cx + size * 0.1, cy + size * 0.18), 4)
    elif cls == "Elementalist":
        pygame.draw.circle(s, FIRE, (cx, cy + size * 0.16), 11)
        pygame.draw.circle(s, GOLD, (cx, cy + size * 0.12), 5)
        pygame.draw.polygon(s, (255, 220, 80), [(cx, cy - size * 0.36), (cx - 7, cy - size * 0.08), (cx + 7, cy - size * 0.08)])
    elif cls == "Stoning":
        pygame.draw.circle(s, (140, 120, 80), (cx, cy + size * 0.16), 12)
        pygame.draw.polygon(s, (180, 160, 110), [(cx - 10, cy - 4), (cx, cy - size * 0.28), (cx + 10, cy - 4)])
    elif cls == "Balthazar":
        pygame.draw.rect(s, GOLD, (cx + 8, cy - size * 0.22, 5, size * 0.5))
        pygame.draw.polygon(s, (255, 80, 40), [(cx + 10, cy - size * 0.28), (cx + 2, cy - size * 0.08), (cx + 18, cy - size * 0.08)])
    elif cls == "Ether":
        pygame.draw.circle(s, MANA, (cx, cy + size * 0.16), 10)
        pygame.draw.circle(s, (80, 160, 255), (cx, cy + size * 0.16), 4)
        pygame.draw.polygon(s, HOLY, [(cx, cy - size * 0.36), (cx - 6, cy - size * 0.1), (cx + 6, cy - size * 0.1)])
    elif cls == "Ranger":
        pygame.draw.line(s, (90, 60, 30), (cx - size * 0.28, cy + size * 0.22), (cx + size * 0.28, cy - size * 0.22), 3)
        pygame.draw.polygon(s, (200, 220, 120), [(cx + size * 0.3, cy - size * 0.28), (cx + size * 0.12, cy - size * 0.1), (cx + size * 0.22, cy - size * 0.06)])
        pygame.draw.circle(s, POISON, (cx - 8, cy + 10), 4)
    elif cls == "Expeller":
        pygame.draw.circle(s, (40, 130, 130), (cx, cy + size * 0.16), 10)
        pygame.draw.circle(s, (90, 40, 120), (cx, cy + size * 0.16), 4)
        pygame.draw.ellipse(s, (80, 40, 110), (cx - size * 0.18, cy - size * 0.38, size * 0.36, size * 0.2))
    elif cls == "Bonder":
        pygame.draw.circle(s, (80, 210, 210), (cx, cy + size * 0.14), 10)
        pygame.draw.line(s, (140, 240, 240), (cx, cy + size * 0.14), (cx + size * 0.28, cy - size * 0.2), 2)
        pygame.draw.circle(s, WHITE, (cx + size * 0.28, cy - size * 0.2), 3)
    elif cls == "Deathdancer":
        pygame.draw.polygon(s, (90, 140, 70), [(cx + size * 0.26, cy - size * 0.08), (cx + size * 0.08, cy + size * 0.28), (cx + size * 0.2, cy + size * 0.3)])
        pygame.draw.circle(s, (40, 50, 40), (cx, cy + size * 0.16), 5)
    elif cls == "Mesmer":
        pygame.draw.circle(s, (220, 110, 200), (cx, cy + size * 0.14), 9)
        pygame.draw.circle(s, (160, 70, 190), (cx, cy + size * 0.14), 4)
        pygame.draw.circle(s, (240, 180, 230), (cx + size * 0.2, cy - size * 0.16), 3)
    elif cls == "Escaper":
        pygame.draw.polygon(s, SHADOW, [(cx - size * 0.38, cy + size * 0.06), (cx - size * 0.02, cy - size * 0.22), (cx - size * 0.08, cy + size * 0.22)])
        pygame.draw.polygon(s, (30, 18, 50), [(cx + size * 0.38, cy + size * 0.06), (cx + size * 0.02, cy - size * 0.22), (cx + size * 0.08, cy + size * 0.22)])
        pygame.draw.polygon(s, WHITE, [(cx, cy - size * 0.42), (cx - 7, cy - size * 0.12), (cx + 7, cy - size * 0.12)])
        pygame.draw.circle(s, HOLY2, (cx, cy + size * 0.18), 9)
        pygame.draw.circle(s, WHITE, (cx, cy + size * 0.18), 3)
        pygame.draw.circle(s, (200, 180, 255), (cx + size * 0.22, cy - size * 0.08), 4)
    elif cls == "Glimmer":
        pygame.draw.circle(s, (120, 210, 255), (cx, cy + size * 0.14), 11)
        pygame.draw.circle(s, WHITE, (cx, cy + size * 0.14), 4)
        pygame.draw.circle(s, (180, 240, 255), (cx - size * 0.22, cy - size * 0.1), 5)
        pygame.draw.circle(s, (180, 240, 255), (cx + size * 0.22, cy - size * 0.1), 5)
    elif cls == "Deadsword":
        pygame.draw.polygon(s, (160, 150, 90), [(cx + size * 0.08, cy - size * 0.28), (cx + size * 0.34, cy + size * 0.22), (cx + size * 0.16, cy + size * 0.26)])
        pygame.draw.circle(s, (90, 50, 30), (cx, cy + size * 0.16), 7)
    elif cls == "Migraine":
        pygame.draw.circle(s, (180, 40, 140), (cx, cy - size * 0.02), 6)
        pygame.draw.circle(s, (120, 20, 90), (cx, cy + size * 0.2), 4)
        pygame.draw.line(s, (160, 30, 100), (cx - 3, cy + 4), (cx - 2, cy + size * 0.28), 2)
    elif cls == "Surger":
        pygame.draw.line(s, (255, 230, 90), (cx, cy - size * 0.32), (cx + 4, cy + size * 0.1), 2)
        pygame.draw.line(s, WHITE, (cx + 4, cy + size * 0.1), (cx - 6, cy + size * 0.22), 2)
    elif cls == "Lifesheath":
        pygame.draw.ellipse(s, (200, 230, 160), (cx - 8, cy + size * 0.08, 16, 10), 2)
        pygame.draw.circle(s, (240, 240, 180), (cx, cy - 2), 4)
    elif cls == "PermaShadow":
        pygame.draw.circle(s, (40, 10, 50), (cx, cy + 4), 8)
        pygame.draw.circle(s, (120, 50, 160), (cx - 4, cy - 2), 3)
    elif cls == "Riposte":
        pygame.draw.rect(s, WHITE, (cx - 6, cy, 12, 14), 2)
        pygame.draw.line(s, WHITE, (cx, cy - 8), (cx, cy + 10), 2)
    elif cls == "AirEnchant":
        pygame.draw.circle(s, (140, 220, 255), (cx + 6, cy), 5, 1)
        pygame.draw.circle(s, (80, 200, 140), (cx + 6, cy), 2)
    elif cls == "Judge":
        pygame.draw.polygon(s, GOLD, [(cx, cy - 10), (cx + 7, cy + 4), (cx - 7, cy + 4)])
    elif cls == "Conditioner":
        pygame.draw.circle(s, (100, 220, 180), (cx, cy + 6), 6, 2)
    elif cls == "Beast Master":
        # feral hood with a beast-claw accent and a small companion silhouette
        pygame.draw.polygon(s, hood, [(cx - size * 0.3, cy - size * 0.02), (cx - size * 0.2, cy - size * 0.44), (cx - size * 0.06, cy - size * 0.12)])
        pygame.draw.polygon(s, hood, [(cx + size * 0.3, cy - size * 0.02), (cx + size * 0.2, cy - size * 0.44), (cx + size * 0.06, cy - size * 0.12)])
        pygame.draw.circle(s, (150, 200, 90), (cx, cy - size * 0.14), 5)
        pygame.draw.circle(s, (30, 40, 18), (cx, cy - size * 0.14), 2)
        # claw marks
        for i in range(3):
            pygame.draw.line(s, (220, 230, 200), (cx - size * 0.16 + i * 6, cy + size * 0.06), (cx - size * 0.1 + i * 6, cy + size * 0.26), 2)
        # companion silhouette (small beast head)
        pygame.draw.circle(s, (90, 70, 40), (cx + size * 0.26, cy + size * 0.22), 7)
        pygame.draw.circle(s, (40, 30, 16), (cx + size * 0.26, cy + size * 0.22), 3)
    else:
        pygame.draw.ellipse(s, hood, (cx - size * 0.28, cy - size * 0.42, size * 0.56, size * 0.28))
        pygame.draw.rect(s, GOLD, (cx - 4, cy + size * 0.16, 8, size * 0.28))
        pygame.draw.circle(s, HOLY2, (cx, cy + size * 0.14), 8)
        pygame.draw.circle(s, WHITE, (cx, cy + size * 0.14), 3)
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (cx, cy), cx - 1)
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.circle(s, GOLD, (cx, cy), cx - 1, 3)
    return s


def load_portraits():
    has_display = pygame.display.get_surface() is not None
    for cls in list(CLASSES) + [c for c in HEAL_PICKS if c not in CLASSES]:
        path = os.path.join(PORT_DIR, f"{cls.lower()}.png")
        if os.path.exists(path):
            img = pygame.image.load(path)
            if has_display:
                img = img.convert_alpha()
        else:
            img = _paint_portrait(cls, 160)
            if has_display:
                pygame.image.save(img, path)
        PORTRAITS[cls] = img


load_portraits()
