#!/usr/bin/env python3
"""Simulated Arena — bet on bot teams. Player watches; bots fight."""

import json
import math
import os
import random
import sys

import pygame

pygame.init()
pygame.display.set_caption("Simulated Arena")
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
except Exception:
    pass

W, H = 1280, 720
SCREEN = pygame.display.set_mode((W, H), pygame.DOUBLEBUF)
CLOCK = pygame.time.Clock()
FPS = 60

BASE = os.path.dirname(os.path.abspath(__file__))
PORT_DIR = os.path.join(BASE, "portraits")
TEAMS_PATH = os.path.join(BASE, "ranked_teams.json")
os.makedirs(PORT_DIR, exist_ok=True)

# --- modular pieces (colors / class data / sounds) ---
from colors import *
from classes import *
from sounds import *
from entities import *
from portraits import *

FONT = pygame.font.SysFont("georgia", 22)
FONT_SM = pygame.font.SysFont("georgia", 16)
FONT_LG = pygame.font.SysFont("georgia", 42)
FONT_XL = pygame.font.SysFont("georgia", 64)
FONT_TINY = pygame.font.SysFont("georgia", 13)

START_GP = 40
WIN_PAY = 7
LOSS_PAY = -4


def draw_text(surf, text, font, color, pos, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surf.blit(img, rect)
    return rect


def draw_class_icon(surf, cls, cx, cy, r, selected=False, show_label=True):
    img = PORTRAITS.get(cls)
    if img:
        surf.blit(pygame.transform.smoothscale(img, (r * 2, r * 2)), (cx - r, cy - r))
    else:
        pygame.draw.circle(surf, PANEL2, (cx, cy), r)
    pygame.draw.circle(surf, GOLD if selected else (200, 200, 210), (cx, cy), r, 3 if selected else 2)
    if show_label:
        label = FONT_TINY.render(cls, True, WHITE)
        surf.blit(label, label.get_rect(center=(cx, cy + r + 12)))


def draw_spell_tooltip(surf, cls, mx, my):
    names = [s[0] for s in SKILLS.get(cls, [])]
    if not names:
        return
    pad, line_h = 10, 18
    title = FONT_SM.render(cls, True, GOLD)
    lines = [FONT_TINY.render(n, True, WHITE) for n in names]
    width = max([title.get_width()] + [im.get_width() for im in lines]) + pad * 2
    height = pad + title.get_height() + 6 + line_h * len(lines) + pad
    x = min(max(12, mx + 16), W - width - 12)
    y = min(max(12, my + 16), H - height - 12)
    box = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surf, PANEL, box, border_radius=8)
    pygame.draw.rect(surf, GOLD, box, 1, border_radius=8)
    surf.blit(title, (x + pad, y + pad))
    ty = y + pad + title.get_height() + 6
    for im in lines:
        surf.blit(im, (x + pad, ty))
        ty += line_h


def pick_from_roles(click, mx, my, dps_y=150, heal_y=280, radius=36, tank_y=None):
    """Draw DPS / Tank / Healer rows. Return clicked class or None."""
    if tank_y is None:
        tank_y = (dps_y + heal_y) // 2
    draw_text(SCREEN, "DPS", FONT, GOLD, (80, dps_y - 38))
    hit = None
    hovered = None
    n = len(DPS_PICKS)
    per = max(1, min(n, (W - 100) // 72))
    gap = min(92, (W - 100) // per)
    for i, cls in enumerate(DPS_PICKS):
        row, col = divmod(i, per)
        cx = 80 + col * gap
        cy = dps_y + row * (radius * 2 + 26)
        over = math.hypot(mx - cx, my - cy) <= radius + 4
        draw_class_icon(SCREEN, cls, cx, cy, radius, selected=over)
        if over:
            hovered = cls
        if click and over:
            hit = cls
    draw_text(SCREEN, "TANK", FONT, ORANGE, (80, tank_y - 38))
    for i, cls in enumerate(TANK_PICKS):
        cx = 80 + i * 140
        over = math.hypot(mx - cx, my - tank_y) <= radius + 4
        draw_class_icon(SCREEN, cls, cx, tank_y, radius, selected=over)
        if over:
            hovered = cls
        if click and over:
            hit = cls
    draw_text(SCREEN, "HEALER", FONT, GREEN, (80, heal_y - 38))
    hn = len(HEAL_PICKS)
    per = max(1, min(hn, (W - 120) // 100))
    hgap = min(120, (W - 120) // per)
    for i, cls in enumerate(HEAL_PICKS):
        row, col = divmod(i, per)
        cx = 80 + col * hgap
        cy = heal_y + row * (radius * 2 + 28)
        over = math.hypot(mx - cx, my - cy) <= radius + 4
        draw_class_icon(SCREEN, cls, cx, cy, radius, selected=over)
        if over:
            hovered = cls
        if click and over:
            hit = cls
    if hovered:
        draw_spell_tooltip(SCREEN, hovered, mx, my)
    return hit


class Match(ClassAI):
    def __init__(self, team_a, team_b):
        self.units = []
        self.projs = []
        self.particles = []
        self.bursts = []
        self.tethers = []
        self.heals = []
        self.done = False
        self.winner = None
        self.time = 0.0
        self.max_time = 90.0
        arena = pygame.Rect(40, 80, W - 80, H - 140)
        self.arena = arena
        n_a, n_b = len(team_a), len(team_b)
        for i, u in enumerate(team_a):
            y = arena.top + 40 + (arena.height - 80) * ((i + 0.5) / max(1, n_a))
            f = Fighter(u.name, u.cls, 0, arena.left + 70, y, wins=u.wins, losses=u.losses)
            self._stats(f)
            self.units.append(f)
        for i, u in enumerate(team_b):
            y = arena.top + 40 + (arena.height - 80) * ((i + 0.5) / max(1, n_b))
            f = Fighter(u.name, u.cls, 1, arena.right - 70, y, wins=u.wins, losses=u.losses)
            f.facing = math.pi
            self._stats(f)
            self.units.append(f)
        self.swarms = []
        self.rays = []
        self.wards = []
        self.honor = []
        self.wells = []
        self.echoes = []
        self.deaths = [0, 0]
        self.morale = [0, 0]
        for f in list(self.units):
            if f.cls == "Beast Master":
                self.spawn_beast_pet(f)
            elif f.cls in CLASS_DEFS and CLASS_DEFS[f.cls].get("pet"):
                self.spawn_beast_pet(f, kind=CLASS_DEFS[f.cls]["pet"])

    def spawn_thumper_pet(self, owner):
        live = [un for un in self.units if un.owner_name == owner.name and un.cls in PET_KINDS and un.alive]
        if len(live) >= 4:
            return live[0]
        back = getattr(owner, "facing", 0.0) if getattr(owner, "facing", None) is not None else (0 if owner.team == 0 else math.pi)
        bx = owner.x - math.cos(back) * 42 + random.uniform(-10, 10)
        by = owner.y - math.sin(back) * 42 + random.uniform(-8, 8)
        dead = [un for un in self.units if un.owner_name == owner.name and un.cls in PET_KINDS and not un.alive]
        if dead:
            pet = dead[0]
            pet.alive = True
            pet.hp = pet.max_hp * 0.48
            pet.x, pet.y = bx, by
            pet.owner_ref = owner
            return pet
        kind = random.choice(PET_KINDS)
        pet = Fighter(owner.name + " " + kind, kind, owner.team, bx, by)
        pet.is_pet = True
        pet.pet_kind = kind
        pet.owner_name = owner.name
        pet.owner_ref = owner
        owner.pet_kind = kind
        self._stats(pet)
        self.units.append(pet)
        return pet

    def find_pet(self, owner):
        for un in self.units:
            if un.is_pet and un.owner_name == owner.name and un.cls in PET_KINDS:
                return un
        return None

    def spawn_beast_pet(self, owner, kind=None):
        """Spawn (or resurrect) a Beast Master companion: a ranged Chimp or melee Boa."""
        live = [un for un in self.units if un.owner_name == owner.name and un.cls in BEAST_PETS and un.alive]
        if live:
            return live[0]
        back = getattr(owner, "facing", 0.0) if getattr(owner, "facing", None) is not None else (0 if owner.team == 0 else math.pi)
        bx = owner.x - math.cos(back) * 42 + random.uniform(-10, 10)
        by = owner.y - math.sin(back) * 42 + random.uniform(-8, 8)
        dead = [un for un in self.units if un.owner_name == owner.name and un.cls in BEAST_PETS and not un.alive]
        if dead:
            pet = dead[0]
            pet.alive = True
            pet.hp = pet.max_hp * 0.61
            pet.x, pet.y = bx, by
            pet.owner_ref = owner
            return pet
        if kind is None:
            kind = random.choice(BEAST_PETS)
        pet = Fighter(owner.name + " " + kind, kind, owner.team, bx, by)
        pet.is_pet = True
        pet.pet_kind = kind
        pet.owner_name = owner.name
        pet.owner_ref = owner
        owner.pet_kind = kind
        self._stats(pet)
        self.units.append(pet)
        return pet


    def living(self, team=None):
        if team is None:
            return [u for u in self.units if u.alive]
        return [u for u in self.units if u.alive and u.team == team]


    def unit_hexes(self, u):
        return [a for a in HEX_ATTRS if getattr(u, a, 0) > 0]

    def notice_hex(self, caster, ally, reach=180):
        if not ally or not ally.alive:
            return False
        if math.hypot(ally.x - caster.x, ally.y - caster.y) > reach:
            return False
        if self.unit_hexes(ally):
            if getattr(ally, "hex_notice_at", 0) <= 0:
                ally.hex_notice_at = self.time
                ally.hex_cleanse_at = self.time + random.uniform(1.0, 2.0)
            return True
        ally.hex_notice_at = 0
        ally.hex_cleanse_at = 0
        return False

    def can_cleanse_hex(self, caster, ally, reach=170):
        if not self.notice_hex(caster, ally, reach):
            return False
        return self.time >= getattr(ally, "hex_cleanse_at", 0)

    def pick_ready(self, u, names):
        ready = [n for n in names if u.ready(n)]
        if not ready:
            return None
        random.shuffle(ready)
        return ready[0]

    def refresh_rez(self, u):
        if u.rez_ready:
            return
        if self.morale[1 - u.team] >= u.enemy_deaths_at_rez + 2:
            u.rez_ready = True
            u.cds["Resurrection Signet"] = 0

    def living_real(self, team=None):
        units = [u for u in self.living(team) if u.spirit_form_t <= 0 and not getattr(u, "is_spirit", False)]
        return units

    def nearest(self, u):
        foes = self.living(1 - u.team)
        if not foes:
            return None
        if u.cls not in MELEE_CLS:
            clear = [f for f in foes if getattr(f, "shadow_form_t", 0) <= 0 and getattr(f, "aegis_t", 0) <= 0 and not (getattr(f, "spell_shield_t", 0) > 0 and f.channel)]
            if clear:
                foes = clear
        def d2(e):
            return (e.x - u.x) ** 2 + (e.y - u.y) ** 2
        if u.cls in HEAL_PICKS:
            return min(foes, key=d2)
        heals = [f for f in foes if f.cls in HEAL_PICKS]
        others = [f for f in foes if f.cls not in HEAL_PICKS]
        locked = [o for o in others if o.stun_t > 0 or o.knockdown_t > 0 or o.freeze_t > 0]
        if locked and heals:
            return min(heals, key=d2)
        if u.cls in MELEE_CLS and getattr(u, "chase_t", 0) >= 2.0:
            skip = getattr(u, "focus", None)
            pool = [f for f in foes if f is not skip] or foes
            return min(pool, key=d2)
        if getattr(u, "chase_t", 0) >= 3.0:
            return min(foes, key=d2)
        if heals:
            h = min(heals, key=d2)
            if d2(h) ** 0.5 < 240:
                return h
        return min(foes, key=d2)

    def neediest(self, u, reach=180):
        allies = [a for a in self.living(u.team) if not getattr(a, "is_spirit", False)]
        if not allies:
            return None
        spd = max(50.0, getattr(u, "speed", 90) or 90)
        def eta(a):
            return math.hypot(a.x - u.x, a.y - u.y) / spd
        fresh = [a for a in allies if getattr(a, "hurt_t", 0) > 1.0 and a.hp < a.max_hp * 0.995]
        pool = fresh if fresh else [a for a in allies if a.hp < a.max_hp * 0.99]
        pool = [a for a in pool if eta(a) <= 3.0]
        if not pool:
            return None
        near = [a for a in pool if math.hypot(a.x - u.x, a.y - u.y) <= reach]
        use = near if near else pool
        use.sort(key=lambda a: (0 if getattr(a, "hurt_t", 0) > 1.0 else 1, a.hp / a.max_hp))
        return use[0]

    def give_cc(self, tgt, kind, dur, src=None):
        if kind != "stun" and (getattr(tgt, "dolyak_t", 0) > 0 or getattr(tgt, "stable_t", 0) > 0 or getattr(tgt, "balanced_t", 0) > 0):
            return
        attr = "stun_t" if kind == "stun" else "knockdown_t"
        setattr(tgt, attr, max(getattr(tgt, attr, 0), dur))
        if src is not None and src is not tgt:
            src.stat_cc = getattr(src, "stat_cc", 0) + 1
            own = getattr(src, "owner_ref", None)
            if own is not None and own is not src:
                own.stat_cc = getattr(own, "stat_cc", 0) + 1

    def team_has_dps(self, u):
        return any(
            a.cls not in HEAL_PICKS and not a.is_pet and not getattr(a, "is_spirit", False)
            for a in self.living(u.team)
        )

    def healer_swing(self, u, e):
        # 🔥 STOP AUTO‑ATTACKS WHILE HOLDING ASHES
        if getattr(u, "ashes_t", 0) > 0:
            return False

        # 🔥 MUST HAVE TARGET + DPS PRESENCE
        if not e or self.team_has_dps(u):
            return False

        # 🔥 RANGE CHECK
        dist = math.hypot(e.x - u.x, e.y - u.y)
        if dist > AUTO_RANGE["caster"]:
            return False

        # 🔥 READY?
        if not u.ready("auto"):
            return False

        # 🔥 FIRE HEALER AUTO ATTACK (aimed at the enemy, never a teammate)
        u.facing = math.atan2(e.y - u.y, e.x - u.x)
        self.fire(u, "auto", L_DMG[1], 320, 1.1)
        u.use("auto", 1.15)
        return True





    def team_anchor(self, u):
        pals = [a for a in self.living(u.team) if a is not u and not a.is_pet and not getattr(a, "is_spirit", False)]
        if not pals:
            pals = [a for a in self.living(u.team) if a is not u]
        if not pals:
            return u.x, u.y
        return sum(a.x for a in pals) / len(pals), sum(a.y for a in pals) / len(pals)

    def in_front(self, u, e, reach, cone=0.7):
        dx, dy = e.x - u.x, e.y - u.y
        dist = math.hypot(dx, dy) or 1
        if dist > reach:
            return False
        fx, fy = math.cos(u.facing), math.sin(u.facing)
        return (fx * dx + fy * dy) / dist > cone

    def emit(self, x, y, color, n=18, speed=110, size=5, life=0.5, grav=0):
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(speed * 0.3, speed)
            self.particles.append(Particle(x, y, math.cos(ang) * spd, math.sin(ang) * spd, life * random.uniform(0.6, 1.2), life, color, size, grav))

    def burst(self, x, y, color, radius=52, life=0.4):
        self.bursts.append(Burst(x, y, life, life, color, radius))

    def begin_kite(self, u):
        sign = getattr(u, "kite_sign", 0) or (1 if random.random() < 0.5 else -1)
        if random.random() < 0.45:
            sign = -sign
        u.kite_sign = sign
        side = math.pi / 2 * sign
        ang = u.facing + side + random.uniform(-0.7, 0.7)
        fx, fy = math.cos(u.facing), math.sin(u.facing)
        sx, sy = math.cos(ang), math.sin(ang)
        inward = 0.35 if random.random() < 0.35 else -0.25
        dx, dy = sx * 0.85 + fx * inward, sy * 0.85 + fy * inward
        n = math.hypot(dx, dy) or 1
        u.kite_dir = (dx / n, dy / n)
        u.kite_t = random.uniform(0.35, 0.9)

    def start_cast(self, u, level, fn, cast=None):
        if u.lyssa_t > 0:
            u.lyssa_t = 10.0
        if level <= 1 and not cast:
            fn()
            self.begin_kite(u)
            return
        u.pending_cast = fn
        u.channel = "power"
        t = cast if cast is not None else L_CAST[level]
        if u.haste_t > 0:
            t /= 1.47
        if u.cls == "Migraine":
            t /= 1.28
        if getattr(u, "migraine_t", 0) > 0:
            t *= 2.0
        if getattr(u, "frustrate_t", 0) > 0:
            t *= 1.5
        foe = None
        try:
            foe = self.nearest(u)
        except Exception:
            foe = None
        HEX = {"Curse of Curses", "Curse of Anti Healing", "Mark of Insecurity", "Wastrels Worry", "Diversion", "Seeping Wound", "Ash Blast", "Blurred Vision", "Hauntbrand", "Reapers Mark", "Augury of Death", "Cultists Rot"}
        if foe and getattr(foe, "holy_veil_t", 0) > 0 and u.last_skill in HEX:
            t *= 2
        u.channel_t = t
        u.channel_max = max(0.05, t)
        col = CLASS_COL.get(u.cls, GOLD) if "CLASS_COL" in dir() else GOLD
        cols = {
            "Mage": ICE, "Trident": WATER, "Warlock": CURSE, "Priest": HOLY, "Elementalist": FIRE,
            "Stoning": (150, 130, 90), "Surger": (200, 230, 255), "Migraine": (220, 80, 190),
            "Mesmer": GLASS, "Deadsword": GOLD, "Deathdancer": (80, 130, 70), "Ranger": (160, 200, 80),
            "Dark Cultist": (150, 60, 200),
        }
        col = cols.get(u.cls, GOLD)
        self.emit(u.x, u.y, col, 16, 70, 5, max(0.2, t * 0.5))
        self.burst(u.x, u.y, col, 34, 0.28)

    def fire(self, u, kind, dmg, speed=320, life=1.1, on_hit=None):
        fx, fy = math.cos(u.facing), math.sin(u.facing)
        pierce = 8 if kind == "phoenix" else (3 if kind == "trident" else 1)
        if getattr(u, "cls", "") == "Deathdancer":
            pierce = max(pierce, 4)
        rad = 10 if kind in ("phoenix", "trident") else 6
        rad = 11 if kind == "broad" else rad
        self.projs.append(Projectile(u.x, u.y, fx, fy, speed, dmg, u.team, kind, life, rad, pierce, [], u, on_hit=on_hit))
        col = {"frost": ICE, "poison": POISON, "web": (230, 230, 230), "maul": ORANGE, "arrow": (200, 180, 120), "spear": GOLD, "vicious": (255, 210, 80), "hawk": (90, 80, 70),"verdant": (100, 220, 140), "stone": (150, 130, 90), "poo": (120, 90, 50), 
               "holy": HOLY, "fire": FIRE, "bolt": MANA, "broad": (210, 190, 80), "distract": (220, 140, 40), "savage": (180, 80, 40), "rarrow": (160, 200, 80)}.get(kind, WHITE)
        self.emit(u.x + fx * 16, u.y + fy * 16, col, 8, 60, 3, 0.25)
        if kind == "frost":
            sfx("frostbolt")
        elif kind == "web":
            sfx("web")
        elif kind in ("spear", "vicious"):
            sfx("spear")
        elif kind == "phoenix":
            sfx("blast")
        elif kind in ("hawk", "stone"):
            sfx("stone")
        elif kind in ("holy", "fire", "bolt"):
            sfx("blast", 0.12)
        elif kind == "verdant":
            sfx("holy", 0.12)
        elif kind != "arrow":
            sfx("poison")
        

    def shatter(self, x, y):
        self.emit(x, y, GLASS, 22, 140, 4, 0.4)
        self.emit(x, y, WHITE, 10, 90, 2, 0.3)
        self.burst(x, y, GLASS, 28, 0.25)
        sfx("glass", 0.08)

    def melee_attack(self, u, e, dmg):
        if not e or not e.alive:
            return
        if u.illusion_t > 0:
            dmg = random.uniform(L_DMG[2] * 0.85, L_DMG[2] * 1.1)
            self.shatter(e.x, e.y)
        res = e.take(dmg, melee=True, source=u)
        if res == "blocked":
            if e.deflect_t > 0:
                pass
            return
        self.begin_kite(u)
        if e.visage_t > 0:
            for o in self.living(1 - e.team):
                if math.hypot(o.x - e.x, o.y - e.y) < 70:
                    o.slow_t = max(o.slow_t, 2.5)
                    for k in list(o.cds):
                        o.cds[k] = o.cds[k] + 1.5
            self.emit(e.x, e.y, GLASS, 12, 40, 3, 0.3)

    def _zealot_orbs(self, caster, ally):
        if not caster or caster.zealot_fire_t <= 0 or not ally:
            return
        caster.energy = max(0.0, caster.energy - 1)
        for o in self.living(1 - caster.team):
            if math.hypot(o.x - ally.x, o.y - ally.y) < 78:
                o.take(25, source=caster)
                self.particles.append(Particle(ally.x, ally.y, (o.x - ally.x) * 2, (o.y - ally.y) * 2, 0.35, 0.35, (80, 160, 255), 4, 0))
        self.emit(ally.x, ally.y, (70, 140, 255), 8, 30, 3, 0.3)

    def spirits_near(self, u, reach=200):
        return [s for s in self.living(u.team) if getattr(s, "is_spirit", False) and math.hypot(s.x - u.x, s.y - u.y) <= reach]

    def spawn_spirit(self, owner, kind, life):
        s = Fighter(owner.name + " " + kind, kind, owner.team, owner.x + random.uniform(-28, 28), owner.y + random.uniform(-20, 20))
        self._stats(s)
        s.is_spirit = True
        s.spirit_kind = kind
        s.spirit_life = life
        s.spirit_age = 0
        s.owner_name = owner.name
        s.plant_x, s.plant_y = s.x, s.y
        s.speed = 0
        self.units.append(s)
        self.burst(s.x, s.y, (40, 120, 120), 50, 0.4)
        self.emit(s.x, s.y, (80, 40, 110), 18, 50, 4, 0.45)
        return s

    def spawn_bloodsong(self, owner):
        s = Fighter(owner.name + " Bloodsong", "Bloodsong", owner.team, owner.x + random.uniform(-28, 28), owner.y + random.uniform(-20, 20))
        self._stats(s)
        s.is_spirit = True
        s.spirit_kind = "Bloodsong"
        s.spirit_life = 30
        s.spirit_age = 0
        s.owner_name = owner.name
        s.plant_x, s.plant_y = s.x, s.y
        s.speed = 0
        self.units.append(s)
        self.burst(s.x, s.y, (60, 200, 140), 50, 0.4)
        self.emit(s.x, s.y, (90, 220, 150), 18, 50, 4, 0.45)
        return s

    def apply_ench_dur(self, caster, base):
        if getattr(caster, "cls", "") == "Lingwah":
            return base * 1.44
        return base
    def teal_cast(self, u, ally, extra=True):
        col = (70, 210, 210)
        self.emit(u.x, u.y, col, 16, 55, 4, 0.4)
        self.burst(u.x, u.y, col, 28, 0.25)
        if ally and ally is not u:
            self.tethers.append(Tether(u, ally, 0.45, col))
            self.emit(ally.x, ally.y, (160, 240, 240), 12, 40, 3, 0.35)
            self.burst(ally.x, ally.y, col, 24, 0.25)
        sfx("holy", 0.12)

    def drop_kaolai(self, u):
        if u.kaolai_t <= 0:
            return
        u.kaolai_t = 0
        for a in self.living(u.team):
            if not getattr(a, "is_spirit", False):
                a.heal(90, source=u)
                self.emit(a.x, a.y, (50, 130, 130), 10, 30, 3, 0.35)
        self.burst(u.x, u.y, (70, 30, 90), 40, 0.35)

    def interrupt_cast(self, e, kind=""):
        if not e.channel:
            return False
        was_spell = e.channel in ("power", "siphon", "rez_sig", "comfort", "pentagram", "heal_sig", "rain")
        skill = e.last_skill
        e.channel = ""
        e.pending_cast = None
        e.channel_target = None
        e.channel_t = 0
        if kind == "distract" and skill:
            e.cds[skill] = max(e.cds.get(skill, 0), 20.0)
        self.emit(e.x, e.y, WHITE, 14, 70, 3, 0.25)
        sfx("cheapshot", 0.1)
        if getattr(e, "frustrate_t", 0) > 0:
            dmg = 94 if (was_spell or skill) else 47
            src = getattr(e, "frustrate_src", None)
            e.take(dmg, source=src)
            self.emit(e.x, e.y - 12, (200, 60, 200), 14, 80, 4, 0.3)
        return was_spell

    def apply_heal(self, target, amt, kind="holy", source=None):
        if source is None:
            source = getattr(self, "acting", None)
        if target and target.alive:
            if source and getattr(source, "cls", "") in ("AirEnchant", "Judge", "Conditioner") and target is not source:
                amt += 29 if source.cls in ("AirEnchant", "Conditioner") else 32
            target.heal(amt, source=source)
            target.landed = True
            self.emit(target.x, target.y, HOLY, 14, 50, 4, 0.5, -40)
            self.burst(target.x, target.y, HOLY, 28, 0.3)
            sfx("heal", 0.18)

    def drop_meteor(self, caster):
        tgt = getattr(caster, "channel_target", None)
        foes = self.living(1 - caster.team)
        if tgt and tgt.alive:
            cx, cy = tgt.x, tgt.y
        elif foes:
            t = random.choice(foes)
            cx, cy = t.x, t.y
        else:
            return
        ox = cx + random.uniform(-70, 70)
        oy = cy + random.uniform(-70, 70)
        self.burst(ox, oy, FIRE, 28, 0.35)
        self.emit(ox, oy, FIRE, 10, 70, 3, 0.3)
        sfx("meteor", 0)
        hit = False
        for o in foes:
            if math.hypot(o.x - ox, o.y - oy) < 38:
                o.take(L_DMG[2], source=caster)
                hit = True
        if hit:
            sfx("meteor_hit", 0)
            sfx("blast", 0)

    def replay_echo(self, x, y, team, cast, owner):
        if cast == "Soulmend":
            allies = self.living(team)
            if allies:
                a = min(allies, key=lambda t: t.hp / t.max_hp)
                self.apply_heal(a, 14)
        elif cast == "Ancestors Grasp":
            self.burst(x, y, SPIRIT, 60, 0.3)
            for o in self.living(1 - team):
                if math.hypot(o.x - x, o.y - y) < 65:
                    o.slow_t = max(o.slow_t, 1.6)
        elif cast == "Gravewind Purge":
            allies = self.living(team)
            if allies:
                a = allies[0]
                self.apply_heal(a, 8)
        elif cast == "Hauntbrand":
            foes = self.living(1 - team)
            if foes:
                foes[0].hauntbrand_t = max(foes[0].hauntbrand_t, 4.0)
        elif cast == "Warding Apparition":
            allies = self.living(team)
            if allies:
                allies[0].intercept = True

    def summon_infernal(self, u):
        inn = Fighter(u.name + " Infernal", "Infernal", u.team, u.x + 28, u.y)
        inn.owner_name = u.name
        inn.owner_ref = u
        inn.is_pet = True
        self._stats(inn)
        self.units.append(inn)
        self.burst(inn.x, inn.y, FIRE, 70, 0.5)
        self.emit(inn.x, inn.y, FIRE, 28, 120, 5, 0.55)
        sfx("infernal")

    def tick_channel(self, u, dt):
        if not u.channel:
            return
        u.channel_t -= dt
        u.channel_acc += dt
        if u.channel == "power":
            if u.last_skill == "Dancing Daggers":
                for i in range(3):
                    ang = self.time * 8 + i * 2.1
                    self.particles.append(Particle(u.x + math.cos(ang) * 28, u.y + math.sin(ang) * 28, 0, 0, 0.12, 0.12, (80, 130, 70), 4))
            if u.channel_t <= 0:
                fn = u.pending_cast
                u.pending_cast = None
                u.channel = ""
                if fn:
                    fn()
                if getattr(u, "flee_wait", False):
                    u.flee_wait = False
                    u.flee_t = 2.0
                self.begin_kite(u)
                return
        if u.channel == "siphon":
            tgt = u.channel_target
            if tgt and tgt.alive:
                dmg = 8 * dt
                tgt.take(dmg)
                u.heal(dmg * 2)
                self.particles.append(Particle(tgt.x, tgt.y, (u.x - tgt.x) * 0.4, (u.y - tgt.y) * 0.4, 0.25, 0.25, CURSE, 3))
            else:
                u.channel = ""
        elif u.channel == "rain":
            if u.channel_acc >= 0.55 and getattr(u, "rain_n", 0) < 5:
                u.channel_acc -= 0.55
                u.rain_n = getattr(u, "rain_n", 0) + 1
                self.drop_meteor(u)
        elif u.channel == "heal_sig":
            u.frail_armor = 1
            if u.channel_t <= 0:
                u.heal(u.max_hp * 0.42)
                self.apply_heal(u, L_HEAL[1])
                u.frail_armor = 0
                u.channel = ""
                return
        elif u.channel == "rez_sig":
            tgt = u.channel_target
            if u.channel_t <= 0:
                if tgt and not tgt.alive:
                    tgt.alive = True
                    tgt.hp = tgt.max_hp
                    tgt.spirit_form_t = 0
                    self.burst(tgt.x, tgt.y, GLASS, 50, 0.4)
                u.channel = ""
                u.channel_target = None
                return
            if u.stun_t > 0 or u.freeze_t > 0:
                u.channel = ""
                u.rez_ready = True
                return
        elif u.channel == "flesh":
            tgt = u.channel_target
            self.emit(u.x, u.y - 40 + u.channel_t * 8, (180, 220, 255), 4, 20, 2, 0.2)
            pygame = __import__("pygame")
            if u.channel_t <= 0:
                if tgt and not tgt.alive and u.alive:
                    pay = u.hp * 0.5
                    u.hp = max(1, u.hp - pay)
                    tgt.alive = True
                    tgt.hp = max(8, u.hp)
                    tgt.energy = tgt.max_energy * 0.05
                    tgt.spirit_form_t = 0
                    self.burst(tgt.x, tgt.y, HOLY, 55, 0.45)
                    self.emit(tgt.x, tgt.y, (180, 30, 50), 20, 90, 5, 0.4)
                    sfx("rez")
                u.channel = ""
                u.channel_target = None
                return
            if u.stun_t > 0 or u.freeze_t > 0:
                u.channel = ""
                return
        elif u.channel == "comfort":
            if u.channel_t <= 0:
                live = [un for un in self.units if un.owner_name == u.name and un.cls in PET_KINDS and un.alive]
                wounded = [p for p in live if p.hp < p.max_hp * 0.45]
                if wounded and len(live) >= 4:
                    pet = min(wounded, key=lambda p: p.hp / p.max_hp)
                    pet.heal(pet.max_hp * 0.4)
                    self.apply_heal(pet, 8)
                elif len(live) < 4:
                    pet = self.spawn_thumper_pet(u)
                    if pet:
                        pet.hp = pet.max_hp if pet.hp < pet.max_hp * 0.5 else pet.hp
                        self.emit(pet.x, pet.y, (180, 140, 80), 12, 40, 3, 0.35)
                elif live:
                    pet = min(live, key=lambda p: p.hp / p.max_hp)
                    pet.heal(pet.max_hp * 0.4)
                u.channel = ""
                return
        elif u.channel == "beast_comfort":
            if u.channel_t <= 0:
                pet = u.channel_target
                if pet is not None:
                    if not pet.alive:
                        pet.alive = True
                        pet.hp = pet.max_hp * 0.61
                        pet.x, pet.y = u.x + random.uniform(-16, 16), u.y + random.uniform(-16, 16)
                        self.clamp(pet)
                        self.burst(pet.x, pet.y, (180, 140, 80), 50, 0.4)
                        self.emit(pet.x, pet.y, (200, 170, 90), 20, 80, 5, 0.5)
                        sfx("rez")
                    else:
                        pet.heal(110, source=u)
                        self.apply_heal(pet, 110)
                        self.emit(pet.x, pet.y, (180, 220, 140), 16, 50, 4, 0.4)
                u.channel = ""
                u.channel_target = None
                return
        elif u.channel == "pentagram":
            self.particles.append(Particle(u.x + math.cos(self.time * 6) * 22, u.y + math.sin(self.time * 6) * 22, 0, 0, 0.2, 0.2, FIRE, 4))
            if u.channel_t <= 0:
                self.summon_infernal(u)
                u.channel = ""
                return
        if u.channel_t <= 0:
            u.channel = ""
            u.channel_target = None


    def lightning_flash(self, a, b):
        col = (200, 230, 255)
        if a and b:
            self.tethers.append(Tether(a, b, 0.4, col))
            for i in range(10):
                f = i / 10
                x = a.x + (b.x - a.x) * f + random.uniform(-8, 8)
                y = a.y + (b.y - a.y) * f + random.uniform(-8, 8)
                self.particles.append(Particle(x, y, random.uniform(-20, 20), random.uniform(-40, 10), 0.28, 0.28, col, 4))
        if a:
            self.emit(a.x, a.y - 34, (255, 255, 200), 18, 50, 5, 0.45)
            self.burst(a.x, a.y - 30, WHITE, 36, 0.3)
        if b:
            self.emit(b.x, b.y, col, 22, 100, 6, 0.45)
            self.burst(b.x, b.y, WHITE, 42, 0.35)

    def nec_flash(self, u, tgt):
        col = (80, 130, 70)
        self.emit(u.x, u.y, col, 12, 50, 3, 0.35)
        self.burst(u.x, u.y, (160, 160, 160), 22, 0.2)
        if tgt and tgt is not u:
            self.emit(tgt.x, tgt.y, col, 10, 40, 3, 0.3)
            self.burst(tgt.x, tgt.y, (120, 120, 120), 18, 0.2)
        sfx("curse", 0.1)

    def auto_band(self, u):
        if u.cls in MELEE_CLS:
            return "melee"
        if u.cls in ("Archer", "Lifesheath"):
            return "short"
        if u.cls in RANGE_CLS:
            return "ranged"
        return "caster"

    def try_auto(self, u):
        # 17. Cannot auto‑attack while holding ashes
        if getattr(u, "ashes_t", 0) > 0:
            return

        if getattr(u, "acted", False) or u.channel or u.iceblock_t > 0 or getattr(u, "attack_lock", 0) > 0:
            return
        if not u.ready("auto"):
            return

        e = self.nearest(u)
        if not e:
            return

        dist = math.hypot(e.x - u.x, e.y - u.y)
        reach = AUTO_RANGE["caster"] if u.cls in CASTER_ENERGY else AUTO_RANGE["melee"]

        if dist <= reach:
            # Healers face their ally while healing/enchanting, so their auto-attack
            # must be re-aimed at the enemy during downtime. Never fire at a teammate.
            if u.cls in HEAL_PICKS:
                u.facing = math.atan2(e.y - u.y, e.x - u.x)
            self.fire(u, "auto", L_DMG[1], 320, 1.1)
            u.use("auto", 1.15)



    def clamp(self, u):
        r = 18 if getattr(u, "infernal", False) else 14
        u.x = max(self.arena.left + r, min(self.arena.right - r, u.x))
        u.y = max(self.arena.top + r, min(self.arena.bottom - r, u.y))

    def update(self, dt):
        if self.done:
            return
        self.time += dt
        heal_mod = max(0.0, 1.0 - int(self.time) * 0.01)
        for u in self.units:
            u.heal_mod = heal_mod
        self.wards = [[x, y, team, life - dt] for x, y, team, life in self.wards if life - dt > 0]
        self.honor = [[x, y, team, life - dt] for x, y, team, life in getattr(self, "honor", []) if life - dt > 0]
        self.wells = [[x, y, team, life - dt] for x, y, team, life in self.wells if life - dt > 0]
        kept_echo = []
        for ex, ey, team, life, cast, owner in self.echoes:
            life -= dt
            if life <= 0.55 and cast:
                self.replay_echo(ex, ey, team, cast, owner)
                cast = ""
            if life > 0:
                kept_echo.append([ex, ey, team, life, cast, owner])
                self.particles.append(Particle(ex + random.uniform(-8, 8), ey, 0, -20, 0.25, 0.25, SPIRIT, 3))
        self.echoes = kept_echo
        pending = []
        for h in self.heals:
            if h.update(dt):
                if h.target.alive:
                    self.particles.append(Particle(h.target.x + random.uniform(-10, 10), h.target.y + random.uniform(-16, 4), 0, -20, 0.3, 0.3, HOLY, 3, 0))
                pending.append(h)
            else:
                self.apply_heal(h.target, h.amount, h.kind, source=getattr(h, "source", None))
        self.heals = pending

        for u in self.units:
            if getattr(u, "is_spirit", False) or u.cls in ("Life", "Recovery"):
                u.is_spirit = True
                u.speed = 0
                u.x, u.y = getattr(u, "plant_x", u.x), getattr(u, "plant_y", u.y)
                if not hasattr(u, "plant_x"):
                    u.plant_x, u.plant_y = u.x, u.y
            if not u.alive:
                if not getattr(u, "_dead_counted", False):
                    u._dead_counted = True
                    if not getattr(u, "is_spirit", False):
                        self.deaths[u.team] += 1
                        u.stat_deaths = getattr(u, "stat_deaths", 0) + 1
                        if not getattr(u, "is_pet", False) and not getattr(u, "morale_spent", False):
                            u.morale_spent = True
                            self.morale[u.team] += 1
                        for n in self.living():
                            if n.cls == "Deathdancer" and math.hypot(n.x - u.x, n.y - u.y) < 200:
                                if getattr(n, "soul_n", 0) < 3:
                                    n.energy = min(n.max_energy, n.energy + 14)
                                    n.soul_n = getattr(n, "soul_n", 0) + 1
                                    n.soul_reset = 15
                                    self.emit(n.x, n.y, (80, 140, 70), 8, 30, 3, 0.3)
                    if getattr(u, "reaper_src", None) and u.reaper_t > 0 and u.reaper_src.alive:
                        u.reaper_src.energy = min(u.reaper_src.max_energy, u.reaper_src.energy + 14)
                    if getattr(u, "is_spirit", False):
                        for own in self.units:
                            if own.name == getattr(u, "owner_name", "") and own.alive:
                                skill = "Life" if u.spirit_kind == "Life" else ("Recovery" if u.spirit_kind == "Recovery" else None)
                                if skill:
                                    own.cds[skill] = max(own.cds.get(skill, 0), 8.0)
                    if getattr(u, "spirit_kind", "") == "Life":
                        heal = 7 * max(1, int(getattr(u, "spirit_age", 1)))
                        for a in self.living(u.team):
                            if not getattr(a, "is_spirit", False) and math.hypot(a.x - u.x, a.y - u.y) < 200:
                                a.heal(heal, source=next((x for x in self.units if x.name == getattr(u, "owner_name", "") and x.alive), None))
                continue
            u._dead_counted = False
            old_g, old_h = u.grasp_t, u.harrier_t
            u.tick_status(dt)
            if u.avatar_t > 0 and ((old_g > 0 and u.grasp_t <= 0) or (old_h > 0 and u.harrier_t <= 0)):
                for o in self.living(1 - u.team):
                    if math.hypot(o.x - u.x, o.y - u.y) < 80:
                        o.burn_t = max(o.burn_t, 2.0)
                        o.burn_tick = 1.0
                self.emit(u.x, u.y, FIRE, 14, 50, 3, 0.35)
            u.near_ward = any((w[2] == u.team and math.hypot(u.x - w[0], u.y - w[1]) < 95) for w in self.wards)
            u.honor_buff = any((h[2] == u.team and math.hypot(u.x - h[0], u.y - h[1]) < 140) for h in getattr(self, "honor", []))
            u.in_well = any((w[2] == u.team and math.hypot(u.x - w[0], u.y - w[1]) < 78) for w in self.wells)
            if u.in_well and random.random() < 0.2:
                u.heal(7 * dt * 8)
                self.particles.append(Particle(u.x, u.y, 0, -20, 0.3, 0.3, SPIRIT, 3))
            if (u.fire_attune_t > 0 or u.burn_t > 0) and random.random() < 0.45:
                self.particles.append(Particle(u.x + random.uniform(-14, 14), u.y + random.uniform(-8, 8), random.uniform(-15, 15), random.uniform(-50, -15), 0.4, 0.4, FIRE, 4, -20))
            if u.water_armor_t > 0 and random.random() < 0.35:
                self.particles.append(Particle(u.x + random.uniform(-16, 16), u.y + random.uniform(-16, 16), 0, -25, 0.4, 0.4, WATER, 4))
            if u.blur_t > 0 and random.random() < 0.25:
                self.particles.append(Particle(u.x + random.uniform(-18, 18), u.y, random.uniform(-10, 10), -10, 0.3, 0.3, (200, 230, 255), 4))
            if (u.stun_t > 0 or u.freeze_t > 0 or u.fear_t > 0) and u.channel:
                u.channel = ""
                u.channel_target = None
            if u.fear_wander and u.fear_t > 0:
                u.fear_turn -= dt
                if u.fear_turn <= 0:
                    ang = random.uniform(0, math.tau)
                    u.fear_dir = (math.cos(ang), math.sin(ang))
                    u.fear_turn = random.uniform(0.25, 0.5)
                if random.random() < 0.5:
                    self.particles.append(Particle(u.x + random.uniform(-16, 16), u.y - 10, random.uniform(-20, 20), random.uniform(-40, -10), 0.35, 0.35, (10, 10, 12), 3))
            if u.curse_t > 0:
                u.curse_tick -= dt
                if u.curse_tick <= 0:
                    u.curse_tick = 2.0
                    u.take(L_DMG[1])
                    self.emit(u.x, u.y, CURSE, 8, 30, 3, 0.3)
            if u.rot_t > 0:
                u.rot_tick -= dt
                if u.rot_tick <= 0:
                    u.rot_tick = 2.0
                    u.take(L_DMG[2])
                    self.emit(u.x, u.y, (90, 40, 120), 10, 34, 3, 0.35)
                    self.burst(u.x, u.y, (60, 20, 80), 26, 0.3)
            if u.channel:
                self.tick_channel(u, dt)
            if u.favor_t > 0:
                u.favor_tick -= dt
                if u.favor_tick <= 0:
                    u.favor_tick = 2.0
                    self.apply_heal(u, L_HEAL[1], "favor", source=getattr(u, "favor_src", None))
            if u.soothe_t > 0:
                u.soothe_tick -= dt
                if u.soothe_tick <= 0:
                    u.soothe_tick = 3.0
                    self.apply_heal(u, L_HEAL[2], "soothe", source=getattr(u, "soothe_src", None))
            if u.bleed > 0:
                u.take(1.0 * u.bleed * dt)
                u.bleed_tick -= dt
                if u.bleed_tick <= 0:
                    u.bleed_tick = 2.0
                    u.take(8 * u.bleed)
            if u.deepwound_t > 0:
                u.deepwound_t -= dt
                if u.deepwound_t <= 0 and u.base_max:
                    u.max_hp = u.base_max
            if u.rampage_t > 0:
                for k in list(u.cds):
                    u.cds[k] = max(0.0, u.cds[k] - dt * 0.33)
            if u.flurry_t > 0:
                for k in list(u.cds):
                    u.cds[k] = max(0.0, u.cds[k] - dt * 0.33)
            if u.fury_t > 0:
                for k in list(u.cds):
                    u.cds[k] = max(0.0, u.cds[k] - dt * 0.25)
            if u.haste_t > 0:
                for k in list(u.cds):
                    u.cds[k] = max(0.0, u.cds[k] - dt * 0.47)
            if getattr(u, "paradox_t", 0) > 0:
                for k in list(u.cds):
                    u.cds[k] = max(0.0, u.cds[k] - dt * 0.33)
            if u.cls == "PermaShadow":
                for k in list(u.cds):
                    u.cds[k] = max(0.0, u.cds[k] - dt * 0.33)
            if getattr(u, "soul_reset", 0) > 0:
                u.soul_reset -= dt
                if u.soul_reset <= 0:
                    u.soul_n = 0
            if getattr(u, "reaper_t", 0) > 0:
                u.take(5 * dt)
            if u.illusion_t <= 0:
                u.extra_armor = 0
            if not u.channel:
                u.frail_armor = 0
            if getattr(u, "migraine_t", 0) > 0:
                u.take(8 * dt)
                if random.random() < 0.35:
                    self.particles.append(Particle(u.x + random.uniform(-6, 6), u.y - 8, 0, 30, 0.4, 0.4, (140, 30, 110), 3))
            if u.seeping_t > 0:
                u.seeping_tick -= dt
                if u.seeping_tick <= 0:
                    u.seeping_tick = 1.0
                    has_cond = u.bleed > 0 or u.stun_t > 0 or u.barbed_t > 0 or u.deepwound_t > 0 or u.curse_t > 0 or u.knockdown_t > 0 or u.daze_t > 0
                    if has_cond:
                        u.take(24)
                        self.emit(u.x, u.y, (160, 20, 30), 8, 30, 3, 0.3)
            if getattr(u, "balth_aura_t", 0) > 0:
                if random.random() < 0.4:
                    self.emit(u.x, u.y, (80, 160, 255), 8, 40, 3, 0.3)
                for o in self.living(1 - u.team):
                    if math.hypot(o.x - u.x, o.y - u.y) < 78:
                        o.take(23 * dt, source=u)
            if getattr(u, "wastrel_on", False) and getattr(u, "wastrel_t", 0) <= 0:
                u.wastrel_on = False
                for o in self.living(u.team) + [u]:
                    if o is u or math.hypot(o.x - u.x, o.y - u.y) < 78:
                        o.take(95)
                        self.emit(o.x, o.y, (220, 90, 200), 12, 40, 3, 0.3)
                self.burst(u.x, u.y, (180, 70, 190), 40, 0.3)
            if getattr(u, "insec_t", 0) > 0:
                u.hp = max(0, u.hp - 2 * dt)
                if u.hp <= 0:
                    u.alive = False
                extra = dt * 0.39
                for attr in ("reversal_t", "favor_t", "water_armor_t", "illusion_t", "haste_t", "master_t", "mystic_t", "fire_attune_t", "earth_attune_t", "kinetic_t", "holy_veil_t", "spirit_bond_t", "shield_regen_t", "ward_wep_t", "djinn_t", "flurry_t", "distortion_t", "deflect_t", "bonetti_t", "stride_t", "paradox_t", "dark_escape_t", "fury_t"):
                    if getattr(u, attr, 0) > 0:
                        setattr(u, attr, max(0.0, getattr(u, attr) - extra))
            if getattr(u, "poison_t", 0) > 0:
                u.poison_tick -= dt
                if u.poison_tick <= 0:
                    u.poison_tick = 2.0
                    u.take(14)
                    self.emit(u.x, u.y, POISON, 6, 20, 3, 0.3)
            if getattr(u, "pet_poison_t", 0) > 0:
                u.pet_poison_tick -= dt
                if u.pet_poison_tick <= 0:
                    u.pet_poison_tick = 2.0
                    u.take(14 * max(1, u.pet_poison_stacks), source=getattr(u, "pet_poison_src", None))
                    self.emit(u.x, u.y, POISON, 8, 24, 3, 0.3)
            if u.burn_t > 0:
                u.burn_tick -= dt
                if u.burn_tick <= 0:
                    u.burn_tick = 1.0
                    u.take(18)
                    self.emit(u.x, u.y, FIRE, 10, 40, 3, 0.3)

            if getattr(u, "surge_t", 0) > 0:
                u.surge_t -= dt
                src = getattr(u, "surge_src", None)
                if random.random() < 0.4 and src:
                    self.particles.append(Particle(src.x, src.y - 30, 0, 20, 0.2, 0.2, (200, 220, 255), 3))
                if u.surge_t <= 0:
                    self.give_cc(u, "kd", 1.4, src)
                    u.cracked_t = max(u.cracked_t, 21)
                    u.take(106, source=src)
                    self.emit(u.x, u.y, (200, 230, 255), 28, 140, 7, 0.5)
                    self.burst(u.x, u.y, WHITE, 55, 0.4)
                    if src:
                        self.lightning_flash(src, u)
            if getattr(u, "strike_hex_t", 0) > 0:
                u.strike_hex_t -= dt
                if u.strike_hex_t <= 0:
                    u.take(42, source=getattr(u, "strike_src", None))
                    self.emit(u.x, u.y, (180, 210, 255), 12, 60, 4, 0.3)
            if getattr(u, "breeze_t", 0) > 0:
                u.heal(10 * dt, source=getattr(u, "breeze_src", None))
            if getattr(u, "fallback_t", 0) > 0 and getattr(u, "still_t", 0) < 0.35:
                u.heal(11 * dt, source=getattr(u, "fallback_src", None))
            if getattr(u, "spell_shield_t", 0) <= 0 and getattr(u, "_shield_on", False):
                u._shield_on = False
                for k in list(u.cds):
                    u.cds[k] = max(u.cds.get(k, 0), 7.0)
                for s, _, _ in SKILLS.get(u.cls, []):
                    u.cds[s] = max(u.cds.get(s, 0), 7.0)
            if getattr(u, "spell_shield_t", 0) > 0:
                u._shield_on = True
            if getattr(u, "shroud_t", 0) > 0 and u.hp < u.max_hp * 0.5:
                u.heal(8 * dt, source=u)
                if random.random() < 0.25:
                    self.particles.append(Particle(u.x, u.y, random.uniform(-20, 20), random.uniform(-10, 10), 0.3, 0.3, (10, 10, 16), 4))
            if getattr(u, "feign_t", 0) > 0:
                u.heal(7 * dt, source=u)
            if u.mystic_t > 0:
                n = sum(1 for a in ("fire_attune_t", "mystic_t", "djinn_t", "water_armor_t", "favor_t", "illusion_t", "haste_t", "master_t", "reversal_t", "spirit_bond_t", "holy_veil_t", "dark_escape_t", "air_attune_t", "aura_restore_t", "wind_t") if getattr(u, a, 0) > 0)
                n = min(8, max(1, n))
                u.heal(3 * n * dt)
            if u.barbed_t > 0:
                u.barbed_tick -= dt
                if u.barbed_tick <= 0:
                    u.barbed_tick = 1.0
                    u.take(16)
                    self.emit(u.x, u.y, RED, 10, 45, 3, 0.35)
            if u.bleed > 0 and random.random() < 0.35:
                self.particles.append(Particle(u.x + random.uniform(-8, 8), u.y, random.uniform(-15, 15), -25, 0.4, 0.4, (200, 20, 80), 3))
                if random.random() < 0.3:
                    self.particles.append(Particle(u.x, u.y, random.uniform(-40, 40), random.uniform(-40, 40), 0.25, 0.25, GLASS, 2))
            if getattr(u, "is_spirit", False):
                u.spirit_age += dt
                u.spirit_life -= dt
                if u.spirit_life <= 0:
                    u.alive = False
                    u.hp = 0
                    for own in self.units:
                        if own.name == u.owner_name and own.alive:
                            skill = "Life" if u.spirit_kind == "Life" else "Recovery"
                            own.cds[skill] = max(own.cds.get(skill, 0), 8.0)
                if u.alive and u.spirit_kind == "Recovery":
                    for a in self.living(u.team):
                        if getattr(a, "is_spirit", False):
                            continue
                        if math.hypot(a.x - u.x, a.y - u.y) < 200:
                            for attr in ("slow_t", "stun_t", "poison_t", "daze_t", "bleed", "curse_t", "antiheal_t", "blur_t"):
                                if attr == "bleed" and a.bleed > 0 and random.random() < 0.08:
                                    a.bleed = max(0, a.bleed - 1)
                                elif getattr(a, attr, 0) > 0:
                                    setattr(a, attr, max(0.0, getattr(a, attr) - dt * 0.52))
                continue
            if getattr(u, "ward_wep_t", 0) > 0:
                u.heal(4 * dt)
            if getattr(u, "shield_regen_t", 0) > 0:
                u.heal(10 * dt)
            if u.iceblock_t > 0:
                continue
            lx, ly = getattr(u, "last_pos", (u.x, u.y))
            if math.hypot(u.x - lx, u.y - ly) < 7:
                u.still_t = getattr(u, "still_t", 0) + dt
            else:
                u.still_t = 0.0
            u.last_pos = (u.x, u.y)
            u.acted = False
            u.landed = False
            ht = getattr(u, "hitters", None)
            if ht:
                dead = [k for k, v in ht.items() if v - dt <= 0]
                for k in list(ht.keys()):
                    ht[k] -= dt
                for k in dead:
                    ht.pop(k, None)
            lg = getattr(u, "dmg_log", None)
            if lg:
                u.dmg_log = [x - dt for x in lg if x - dt > 0]
            if getattr(u, "patient_t", 0) <= 0 and getattr(u, "_patient_on", False):
                u._patient_on = False
                src = getattr(u, "patient_src", None)
                u.heal(96, source=src)
            if getattr(u, "patient_t", 0) > 0:
                u._patient_on = True
            if getattr(u, "post_rez", 0) > 0:
                u.post_rez = max(0.0, u.post_rez - dt)
            if getattr(u, "flee_t", 0) > 0:
                u.flee_t = max(0.0, u.flee_t - dt)
            if getattr(u, "vital_t", 0) <= 0 and getattr(u, "_vital_on", False):
                u._vital_on = False
                u.max_hp = max(1, u.max_hp - 76)
                u.hp = min(u.hp, u.max_hp)
                u.heal(150, source=u)
            if getattr(u, "vital_t", 0) > 0:
                u._vital_on = True
            if getattr(u, "zeal_t", 0) <= 0 and getattr(u, "_zeal_on", False):
                u._zeal_on = False
                foes = [o for o in self.living(1 - u.team) if math.hypot(o.x - u.x, o.y - u.y) < AUTO_RANGE["short"]]
                u.energy = min(u.max_energy, u.energy + min(8, 3 * len(foes)))
            if getattr(u, "zeal_t", 0) > 0:
                u._zeal_on = True
            if getattr(u, "meditate_t", 0) > 0:
                ended = getattr(u, "_ench_n", 0)
                now = sum(1 for a in ("sheath_t", "vital_t", "mirage_t", "watchful_t", "meditate_t", "zeal_t", "reversal_t", "mystic_t", "aura_restore_t") if getattr(u, a, 0) > 0)
                if ended > now:
                    u.energy = min(u.max_energy, u.energy + 3 * (ended - now))
                u._ench_n = now
                if random.random() < 0.3:
                    self.particles.append(Particle(u.x + random.uniform(-8, 8), u.y, 0, -20, 0.3, 0.3, WHITE if random.random() < 0.5 else (20, 20, 20), 3))
            self.ai(u, dt)
            if u.alive and not u.locked():
                self.try_auto(u)
            e = self.nearest(u)
            reach = AUTO_RANGE[self.auto_band(u)]
            if u.landed:
                u.chase_t = 0.0
                if e:
                    u.focus = e
            elif e and math.hypot(e.x - u.x, e.y - u.y) > reach:
                u.chase_t += dt
                if getattr(u, "focus", None) is None:
                    u.focus = e
            else:
                u.chase_t = 0.0
                if e:
                    u.focus = e
            if u.locked():
                continue
            if getattr(u, "flee_t", 0) > 0:
                e = self.nearest(u)
                spd = u.speed * 1.35
                if e:
                    d = math.hypot(e.x - u.x, e.y - u.y) or 1
                    u.x += (u.x - e.x) / d * spd * dt
                    u.y += (u.y - e.y) / d * spd * dt
                self.clamp(u)
                continue
            if getattr(u, "plant_t", 0) > 0 and u.cls not in MELEE_CLS:
                self.clamp(u)
                continue
            spd = u.speed
            if getattr(u, "stride_t", 0) > 0:
                spd *= 1.33
                if random.random() < 0.2:
                    self.particles.append(Particle(u.x, u.y + 10, random.uniform(-20, 20), 10, 0.3, 0.3, (100, 160, 70), 3))
            if u.slow_t > 0:
                spd *= 0.34
            if getattr(u, "cripple_t", 0) > 0:
                spd *= 0.5
            u.was_moving = not u.locked()
            if getattr(u, "haste_sh_t", 0) > 0 or getattr(u, "fallback_t", 0) > 0:
                spd *= 1.33
            if getattr(u, "wind_t", 0) > 0:
                spd *= 1.33
                if random.random() < 0.35:
                    self.particles.append(Particle(u.x, u.y + 8, random.uniform(-15, 15), 20, 0.28, 0.28, (210, 215, 220), 3))
            if getattr(u, "dolyak_t", 0) > 0:
                spd *= 0.25
            if getattr(u, "stealth_t", 0) > 0:
                spd *= 0.5
            if getattr(u, "flail_t", 0) > 0:
                spd *= 0.67
            if u.sprint_t > 0:
                spd *= 1.7
            if u.rampage_t > 0:
                spd *= 1.25
            if u.dark_escape_t > 0:
                spd *= 1.25
            if u.djinn_t > 0:
                spd *= 1.25
            if u.harrier_t > 0:
                spd *= 1.25
            if u.daze_t > 0:
                spd *= 0.7
            if u.storm_t > 0:
                spd *= 0.3
                for o in self.living(1 - u.team):
                    if math.hypot(o.x - u.x, o.y - u.y) < 70:
                        o.take(L_DMG[2] * dt)
            ox, oy = u.x, u.y
            mx, my = u.move_dir()
            e = self.nearest(u)
            dist = math.hypot(e.x - u.x, e.y - u.y) if e else 999
            healer = u.cls in HEAL_PICKS
            ranged = u.cls in ("Mage", "Warlock", "Bellringer", "Trident", "Seeping", "Elementalist", "Stoning", "Ranger", "Mesmer", "Migraine", "Surger", "Dark Cultist", "Beast Master")
            ideal = 40 if u.cls == "Balthazar" else (160 if ranged else 40)
            if ranged and getattr(u, "chase_t", 0) >= 2.0:
                ideal = 100
            u.retreat = False
            if u.cls in MELEE_CLS and e and u.max_hp:
                ratio = u.hp / u.max_hp
                if 0.01 < ratio <= 0.25 and (e.hp / e.max_hp) >= ratio:
                    pals = [a for a in self.living(u.team) if a.cls in HEAL_PICKS]
                    if pals:
                        h = min(pals, key=lambda a: (a.x - u.x) ** 2 + (a.y - u.y) ** 2)
                        hd = math.hypot(h.x - u.x, h.y - u.y) or 1
                        mx, my = (h.x - u.x) / hd, (h.y - u.y) / hd
                        u.retreat = True
            if u.fear_t > 0:
                u.x += mx * spd * dt
                u.y += my * spd * dt
            elif getattr(u, "retreat", False):
                u.x += mx * spd * 1.15 * dt
                u.y += my * spd * 1.15 * dt
            elif healer:
                last = not self.team_has_dps(u)
                ax, ay = self.team_anchor(u)
                ad = math.hypot(u.x - ax, u.y - ay) or 1
                hurt = u.hp < u.max_hp - 25
                if last and e:
                    if dist > 200:
                        u.x += (e.x - u.x) / (dist or 1) * spd * dt
                        u.y += (e.y - u.y) / (dist or 1) * spd * dt
                    elif dist < 50:
                        u.x += (u.x - e.x) / (dist or 1) * spd * 0.7 * dt
                        u.y += (u.y - e.y) / (dist or 1) * spd * 0.7 * dt
                    elif u.kite_t > 0:
                        u.x += u.kite_dir[0] * spd * 0.4 * dt
                        u.y += u.kite_dir[1] * spd * 0.4 * dt
                    else:
                        self.begin_kite(u)
                elif ad > 120:
                    u.x += (ax - u.x) / ad * spd * 1.1 * dt
                    u.y += (ay - u.y) / ad * spd * 1.1 * dt
                elif e and dist < 70 and hurt:
                    u.x += (u.x - e.x) / (dist or 1) * spd * dt
                    u.y += (u.y - e.y) / (dist or 1) * spd * dt
                elif e and dist < 55:
                    u.x += (u.x - e.x) / (dist or 1) * spd * 0.8 * dt
                    u.y += (u.y - e.y) / (dist or 1) * spd * 0.8 * dt
                elif u.kite_t > 0:
                    u.x += u.kite_dir[0] * spd * 0.45 * dt
                    u.y += u.kite_dir[1] * spd * 0.45 * dt
                else:
                    self.begin_kite(u)
            elif dist > ideal + 28:
                u.x += mx * spd * dt
                u.y += my * spd * dt
            elif u.kite_t > 0 and not u.channel:
                u.x += u.kite_dir[0] * spd * dt
                u.y += u.kite_dir[1] * spd * dt
            elif dist < ideal - 16 and ranged and e:
                u.x += (u.x - e.x) / (dist or 1) * spd * dt
                u.y += (u.y - e.y) / (dist or 1) * spd * dt
            elif ranged and not u.channel:
                if u.kite_t <= 0:
                    self.begin_kite(u)
                u.x += u.kite_dir[0] * spd * 0.7 * dt
                u.y += u.kite_dir[1] * spd * 0.7 * dt
            self.clamp(u)
            moved = math.hypot(u.x - ox, u.y - oy)
            if not u.locked() and (abs(mx) + abs(my) > 0.05) and moved < 1.2:
                u.wall_t = getattr(u, "wall_t", 0) + dt
            else:
                u.wall_t = 0.0
            if getattr(u, "wall_t", 0) > 1.0:
                self.begin_kite(u)
                u.x += u.kite_dir[0] * 10
                u.y += u.kite_dir[1] * 10
                self.clamp(u)
                u.wall_t = 0.0

        bodies = [u for u in self.units if u.alive and not getattr(u, "is_spirit", False)]
        for _ in range(2):
            for i, a in enumerate(bodies):
                ra = 20 if getattr(a, "infernal", False) else (16 if getattr(a, "avatar_t", 0) > 0 else 13)
                for b in bodies[i + 1:]:
                    rb = 20 if getattr(b, "infernal", False) else (16 if getattr(b, "avatar_t", 0) > 0 else 13)
                    dx, dy = b.x - a.x, b.y - a.y
                    d = math.hypot(dx, dy)
                    need = ra + rb
                    if d < 0.01:
                        dx, dy, d = 1, 0, 1
                    if d < need:
                        push = (need - d) * 0.5
                        nx, ny = dx / d, dy / d
                        a.x -= nx * push
                        a.y -= ny * push
                        b.x += nx * push
                        b.y += ny * push
                        self.clamp(a)
                        self.clamp(b)

        alive_p = []
        for p in self.projs:
            trail = ICE if p.kind == "frost" else ((180, 210, 255) if p.kind in ("shock", "surge", "chain") else POISON)
            if random.random() < 0.7:
                self.particles.append(Particle(p.x, p.y, 0, 0, 0.18, 0.18, trail, 3))
            if not p.update(dt):
                continue
            hit = False
            for u in self.living(1 - p.team):
                if id(u) in p.hit_ids:
                    continue
                if math.hypot(u.x - p.x, u.y - p.y) < 16 + p.radius:
                    blocked = u.take(p.dmg, projectile=True, source=getattr(p, "owner", None)) == "blocked"
                    if not blocked and getattr(p, "on_hit", None):
                        p.on_hit(u)
                    ow = getattr(p, "owner", None)
                    if not blocked and ow is not None and getattr(ow, "cls", "") == "Beast Master" and getattr(ow, "strike_as_one_t", 0) > 0:
                        u.cripple_t = max(u.cripple_t, 16.0)
                        ow.strike_as_one_t = 0
                        self.emit(u.x, u.y, (200, 120, 60), 14, 50, 4, 0.4)
                    if not blocked and ow is not None and getattr(ow, "is_pet", False) and getattr(ow, "strike_as_one_t", 0) > 0:
                        u.bleed = min(8, u.bleed + 3)
                        u.bleed_tick = 1.0
                        ow.strike_as_one_t = 0
                        self.emit(u.x, u.y, (180, 30, 70), 14, 50, 4, 0.4)
                    if p.kind == "shock" and blocked != "blocked" and getattr(u, "cracked_t", 0) > 0:
                        ow = getattr(p, "owner", None)
                        if ow:
                            ow.energy = min(ow.max_energy, ow.energy + 20)
                    p.hit_ids.append(id(u))
                    if blocked and u.deflect_t > 0:
                        for o in self.living(1 - u.team):
                            if math.hypot(o.x - u.x, o.y - u.y) < 72:
                                o.bleed = min(8, o.bleed + 1)
                                o.bleed_tick = min(o.bleed_tick or 2, 2)
                                self.emit(o.x, o.y, (180, 30, 70), 10, 40, 3, 0.35)
                    if blocked:
                        p.pierce -= 1
                        if p.pierce <= 0:
                            hit = True
                            break
                        continue
                    p.pierce -= 1
                    if p.kind == "trident":
                        self.emit(u.x, u.y, WATER, 18, 90, 5, 0.4)
                        self.burst(u.x, u.y, WATER, 34, 0.3)
                        if u.was_moving and not u.locked():
                            self.give_cc(u, "kd", 1.3, getattr(p, "owner", None))
                    if p.kind == "frost":
                        u.slow_t = max(u.slow_t, 1.8)
                        self.emit(u.x, u.y, ICE, 10, 70, 3, 0.3)
                    if p.kind == "poison":
                        u.take(L_DMG[1], projectile=True, source=getattr(p, "owner", None))
                        self.emit(u.x, u.y, POISON, 10, 70, 3, 0.3)
                    if p.kind == "web":
                        self.give_cc(u, "stun", 1.0, getattr(p, "owner", None))
                        spiders = [s for s in self.living(p.team) if s.cls == "Spider"]
                        if spiders:
                            sp = min(spiders, key=lambda s: (s.x - u.x) ** 2 + (s.y - u.y) ** 2)
                            u.x, u.y = sp.x, sp.y
                            self.clamp(u)
                            self.tethers.append(Tether(sp, u, 0.4))
                    if p.kind == "poo":
                        self.give_cc(u, "stun", 1.2, getattr(p, "owner", None))
                        self.emit(u.x, u.y, (120, 90, 50), 14, 50, 4, 0.4)
                        self.burst(u.x, u.y, (110, 80, 45), 30, 0.3)
                    if p.kind == "maul":
                        if u.knockdown_t > 0:
                            u.daze_t = max(u.daze_t, 3.0)
                    if p.kind == "spear":
                        u.barbed_t = max(u.barbed_t, 17.0)
                        u.barbed_tick = 1.0
                        self.emit(u.x, u.y, RED, 14, 50, 3, 0.4)
                    if p.kind == "vicious":
                        crit = getattr(p, "crit", False)
                        if crit:
                            if not u.base_max:
                                u.base_max = u.max_hp
                            u.deepwound_t = 13
                            u.max_hp = u.base_max * 0.8
                            u.hp = min(u.hp, u.max_hp)
                            self.emit(u.x, u.y, GOLD, 16, 60, 4, 0.4)
                    if p.kind == "hawk":
                        u.weakness_t = max(u.weakness_t, 13.0)
                        self.emit(u.x, u.y, (110, 100, 80), 12, 40, 3, 0.35)
                    if p.kind == "stone":
                        if u.weakness_t > 0:
                            self.give_cc(u, "kd", 1.4, getattr(p, "owner", None))
                            self.emit(u.x, u.y, (160, 140, 90), 16, 60, 4, 0.4)
                    if p.kind in ("broad", "distract", "savage", "rarrow"):
                        owner = getattr(p, "owner", None)
                        was = self.interrupt_cast(u, p.kind)
                        if p.kind == "broad":
                            u.daze_t = max(u.daze_t, 15.0)
                            self.emit(u.x, u.y, (200, 180, 80), 16, 50, 4, 0.4)
                        if p.kind == "savage" and was:
                            u.take(23, projectile=True, source=owner)
                            self.emit(u.x, u.y, ORANGE, 12, 60, 3, 0.3)
                        if owner and getattr(owner, "poison_prep_t", 0) > 0:
                            u.poison_t = max(u.poison_t, 11.0)
                            u.poison_tick = 2.0
                        self.emit(u.x, u.y, (180, 210, 90), 8, 40, 3, 0.25)
                    hit = True
                    if p.pierce <= 0:
                        break
            if (not hit or p.pierce > 0) and self.arena.inflate(20, 20).collidepoint(p.x, p.y):
                alive_p.append(p)
        self.projs = alive_p
        self.particles = [p for p in self.particles if p.update(dt)]
        self.bursts = [b for b in self.bursts if b.update(dt)]
        self.tethers = [t for t in self.tethers if t.update(dt)]
        nr = []
        for ray in getattr(self, "rays", []):
            ray[3] -= dt
            if ray[3] <= 0:
                continue
            x, y, team, life, owner = ray
            if random.random() < 0.4:
                self.particles.append(Particle(x + random.uniform(-20, 20), y, 0, -40, 0.3, 0.3, GOLD, 3))
            for o in self.living(1 - team):
                if math.hypot(o.x - x, o.y - y) < 78:
                    o.take(53 * dt, source=owner)
                    o.burn_t = max(o.burn_t, 3.0)
                    o.burn_tick = min(o.burn_tick or 1, 1)
            nr.append(ray)
        self.rays = nr
        fresh = []
        for team, tgt in self.swarms:
            if tgt is None or not tgt.alive:
                foes = self.living(1 - team)
                tgt = min(foes, key=lambda o: o.hp) if foes else None
            if tgt and tgt.alive:
                tgt.take(8 * dt, source=next((x for x in self.units if x.team == team and x.cls == "Bellringer" and x.alive), None))
                if random.random() < 0.45:
                    self.particles.append(Particle(tgt.x + random.uniform(-10, 10), tgt.y, random.uniform(-30, 30), -30, 0.35, 0.35, GOLD, 3))
                fresh.append([team, tgt])
        self.swarms = fresh
        a, b = self.living_real(0), self.living_real(1)
        if not a or not b or self.time >= self.max_time:
            self.done = True
            if len(a) > len(b):
                self.winner = 0
            elif len(b) > len(a):
                self.winner = 1
            else:
                self.winner = 0 if sum(u.hp for u in a) >= sum(u.hp for u in b) else 1

    def draw(self, surf):
        pygame.draw.rect(surf, (18, 22, 30), self.arena)
        pygame.draw.rect(surf, (60, 70, 90), self.arena, 2)
        pygame.draw.line(surf, (40, 48, 62), (self.arena.centerx, self.arena.top), (self.arena.centerx, self.arena.bottom), 1)
        for x, y, team, life in self.wells:
            pygame.draw.circle(surf, SPIRIT, (int(x), int(y)), 78, 2)
            pygame.draw.circle(surf, WHITE, (int(x), int(y)), 8)
        for x, y, team, life in self.wards:
            col = WATER
            pygame.draw.circle(surf, col, (int(x), int(y)), 90, 2)
            pygame.draw.circle(surf, BLUE if team == 0 else RED, (int(x), int(y)), 10)
            pygame.draw.circle(surf, ICE, (int(x), int(y)), 16, 2)
        for x, y, team, life in getattr(self, "honor", []):
            pygame.draw.circle(surf, GOLD, (int(x), int(y)), 140, 2)
            pygame.draw.circle(surf, (180, 150, 60), (int(x), int(y)), 12)
            pygame.draw.polygon(surf, GOLD, [(int(x), int(y) - 22), (int(x) - 8, int(y) - 4), (int(x) + 8, int(y) - 4)])
        for t in self.tethers:
            t.draw(surf)
        for b in self.bursts:
            b.draw(surf)
        for p in self.particles:
            p.draw(surf)
        for p in self.projs:
            pcol = {"frost": ICE, "poison": POISON, "web": WHITE, "maul": ORANGE, "arrow": (210, 190, 130), "trident": WATER, "spear": GOLD, "vicious": (255, 220, 90), "phoenix": FIRE, "hawk": (80, 70, 60), "stone": (170, 150, 110), "holy": HOLY, "fire": FIRE, "bolt": MANA, "broad": (220, 200, 80), "distract": (230, 140, 50), "savage": (200, 90, 40), "rarrow": (150, 200, 80), "dagger": (90, 140, 70), "glass": (220, 110, 210)}.get(p.kind, WHITE)
            if p.kind == "broad":
                pygame.draw.circle(surf, pcol, (int(p.x), int(p.y)), p.radius + 2, 1)
            pygame.draw.circle(surf, pcol, (int(p.x), int(p.y)), p.radius)
        for u in self.units:
            if not u.alive:
                pygame.draw.circle(surf, (40, 40, 48), (int(u.x), int(u.y)), 10)
                continue
            col = BLUE if u.team == 0 else RED
            if u.iceblock_t > 0:
                col = ICE
            stealthed = getattr(u, "stealth_t", 0) > 0
            if u.infernal:
                size = 44
            elif u.is_pet or u.clone:
                size = 30
            else:
                size = 38
            if u.avatar_t > 0:
                size = int(size * 1.5)
            r = size // 2
            port = PORTRAITS.get(u.cls)
            if port:
                img = pygame.transform.smoothscale(port, (size, size))
                if stealthed:
                    img.set_alpha(110)
                surf.blit(img, (int(u.x) - r, int(u.y) - r))
            else:
                pygame.draw.circle(surf, PANEL2, (int(u.x), int(u.y)), r)
                nm = FONT_TINY.render(u.cls[:2], True, WHITE)
                surf.blit(nm, nm.get_rect(center=(int(u.x), int(u.y))))
            ring = (90, 90, 110) if stealthed else col
            pygame.draw.circle(surf, ring, (int(u.x), int(u.y)), r, 3)
            if u.infernal:
                pygame.draw.circle(surf, FIRE, (int(u.x), int(u.y)), r + 6, 2)
            if u.shield > 0:
                pygame.draw.circle(surf, HOLY2, (int(u.x), int(u.y)), r + 4, 2)
            if u.favor_t > 0:
                pygame.draw.circle(surf, (255, 245, 180), (int(u.x), int(u.y)), r + 7, 1)
            if u.water_armor_t > 0:
                pygame.draw.circle(surf, WATER, (int(u.x), int(u.y)), r + 6, 2)
            if u.blur_t > 0:
                pygame.draw.circle(surf, (190, 230, 255), (int(u.x), int(u.y)), r + 10, 1)
            if u.spirit_form_t > 0:
                pygame.draw.circle(surf, SPIRIT, (int(u.x), int(u.y)), r + 8, 2)
            if u.intercept:
                pygame.draw.circle(surf, WHITE, (int(u.x), int(u.y)), r + 5, 2)
            if u.hauntbrand_t > 0:
                pygame.draw.circle(surf, SPIRIT, (int(u.x), int(u.y)), r + 2, 1)
            if getattr(u, "rot_t", 0) > 0:
                pygame.draw.circle(surf, (150, 60, 200), (int(u.x), int(u.y)), r + 3, 2)
            if u.reversal_t > 0:
                pygame.draw.circle(surf, MANA, (int(u.x), int(u.y)), r + 6, 2)
            if u.spirit_bond_t > 0:
                pygame.draw.circle(surf, WHITE, (int(u.x), int(u.y)), r + 8, 1)
            if u.holy_veil_t > 0:
                pygame.draw.circle(surf, MANA, (int(u.x), int(u.y)), r + 11, 1)
            if u.dark_escape_t > 0:
                pygame.draw.circle(surf, SHADOW, (int(u.x), int(u.y)), r + 4, 2)
            if u.illusion_t > 0:
                pygame.draw.circle(surf, GLASS, (int(u.x), int(u.y)), r + 5, 2)
            if u.distortion_t > 0 or u.deflect_t > 0:
                pygame.draw.circle(surf, (230, 200, 255), (int(u.x), int(u.y)), r + 7, 1)
            if u.bleed > 0:
                pygame.draw.circle(surf, (180, 20, 70), (int(u.x), int(u.y) + r + 2), 3)
            if u.barbed_t > 0 or u.seeping_t > 0:
                pygame.draw.circle(surf, RED, (int(u.x), int(u.y) + r + 6), 3)
            if u.haste_t > 0 or u.master_t > 0:
                pygame.draw.circle(surf, GOLD, (int(u.x), int(u.y)), r + 4, 1)
            if u.fire_attune_t > 0:
                pygame.draw.circle(surf, FIRE, (int(u.x), int(u.y)), r + 8, 2)
            if u.earth_attune_t > 0:
                pygame.draw.circle(surf, (130, 110, 70), (int(u.x), int(u.y)), r + 6, 3)
            if u.kinetic_t > 0:
                pygame.draw.circle(surf, (160, 210, 255), (int(u.x), int(u.y)), r + 10, 2)
            if u.lyssa_t > 0:
                pygame.draw.line(surf, HOLY, (int(u.x), int(u.y) - r - 18), (int(u.x), int(u.y) - r - 4), 2)
                pygame.draw.circle(surf, WHITE, (int(u.x), int(u.y) - r - 20), 4)
            if u.ash_t > 0:
                pygame.draw.circle(surf, (90, 70, 40), (int(u.x), int(u.y)), r + 1, 4)
            if u.fury_t > 0:
                pulse = 4 + int(2 * abs(math.sin(self.time * 8)))
                pygame.draw.circle(surf, RED, (int(u.x), int(u.y) - r - 18), pulse)
                pygame.draw.circle(surf, (255, 120, 140), (int(u.x), int(u.y) - r - 18), max(2, pulse - 3))
            if u.avatar_t > 0:
                pygame.draw.circle(surf, GOLD, (int(u.x), int(u.y)), r + 5, 2)
            if getattr(u, "is_spirit", False):
                pygame.draw.circle(surf, (80, 40, 110), (int(u.x), int(u.y)), r + 8, 2)
                pygame.draw.circle(surf, (30, 110, 110), (int(u.x), int(u.y)), r + 3, 1)
            if getattr(u, "ward_wep_t", 0) > 0:
                pygame.draw.circle(surf, (30, 120, 120), (int(u.x), int(u.y)), r + 6, 2)
            if getattr(u, "xinrae_t", 0) > 0:
                pulse = 0.7 + 0.3 * abs(math.sin(self.time * 3))
                aura_col = (int(60 * pulse), int(120 * pulse), int(255 * pulse))
                aura_surf = pygame.Surface((48, 16), pygame.SRCALPHA)
                pygame.draw.ellipse(aura_surf, (*aura_col, 120), (0, 0, 48, 16))
                surf.blit(aura_surf, (int(u.x) - 24, int(u.y) + r - 4))
                pygame.draw.ellipse(surf, aura_col, (int(u.x) - 24, int(u.y) + r - 4, 48, 16), 2)
            if getattr(u, "guardian_t", 0) > 0:
                ang = self.time * 5
                pygame.draw.circle(surf, (120, 210, 255), (int(u.x + math.cos(ang) * (r + 8)), int(u.y + math.sin(ang) * (r + 8))), 6)
            if getattr(u, "absorb_t", 0) > 0:
                pygame.draw.circle(surf, (150, 230, 255), (int(u.x), int(u.y)), r + 7, 2)
            if getattr(u, "holy_veil_t", 0) > 0:
                pygame.draw.circle(surf, (180, 230, 255), (int(u.x - r - 6), int(u.y)), 7, 2)
                pygame.draw.circle(surf, (180, 230, 255), (int(u.x + r + 6), int(u.y)), 7, 2)
            if getattr(u, "vigorous_t", 0) > 0:
                pygame.draw.circle(surf, (100, 200, 255), (int(u.x), int(u.y) - r - 6), 3)
            if getattr(u, "frustrate_t", 0) > 0:
                pygame.draw.line(surf, (180, 40, 200), (int(u.x), int(u.y) - r - 22), (int(u.x), int(u.y) - 2), 2)
            if getattr(u, "live_vic_t", 0) > 0:
                pygame.draw.line(surf, (140, 210, 255), (int(u.x), int(u.y) - r - 28), (int(u.x), int(u.y) - r - 4), 2)
                ang = self.time * 4
                for i in range(3):
                    a = ang + i * 2.1
                    pygame.draw.circle(surf, (180, 220, 255), (int(u.x + math.cos(a) * (r + 10)), int(u.y + math.sin(a) * (r + 8))), 4)
                    pygame.draw.circle(surf, GOLD, (int(u.x + math.cos(a) * (r + 10)), int(u.y + math.sin(a) * (r + 8))), 2)
            if getattr(u, "kaolai_t", 0) > 0:
                pygame.draw.circle(surf, (70, 30, 90), (int(u.x) - r, int(u.y) - r), 5)
            if getattr(u, "shield_regen_t", 0) > 0:
                pygame.draw.circle(surf, (80, 210, 210), (int(u.x), int(u.y)), r + 6, 1)
            if getattr(u, "bonetti_t", 0) > 0:
                pygame.draw.circle(surf, (160, 240, 240), (int(u.x), int(u.y)), r + 8, 1)
            src = getattr(u, "bond_src", None)
            if src and src.alive and getattr(src, "lifebond_t", 0) > 0:
                flicker = 1 if int(self.time * 12) % 2 == 0 else 0
                if flicker:
                    pygame.draw.line(surf, (80, 230, 230), (src.x, src.y), (u.x, u.y), 2)
            src2 = getattr(u, "spirit_src", None)
            if src2 and src2.alive and getattr(src2, "balth_spirit_t", 0) > 0:
                flicker = 1 if int(self.time * 10 + 1) % 2 == 0 else 0
                if flicker:
                    pygame.draw.line(surf, (40, 180, 190), (src2.x, src2.y), (u.x, u.y), 2)
            if getattr(u, "poison_t", 0) > 0:
                pygame.draw.circle(surf, (20, 80, 20), (int(u.x), int(u.y) - r - 18), 6)
                pygame.draw.circle(surf, POISON, (int(u.x), int(u.y) - r - 18), 4)
                pygame.draw.circle(surf, (20, 40, 20), (int(u.x) - 3, int(u.y) - r - 22), 2)
                pygame.draw.circle(surf, (20, 40, 20), (int(u.x) + 3, int(u.y) - r - 22), 2)
            if getattr(u, "stride_t", 0) > 0:
                pygame.draw.circle(surf, (120, 200, 90), (int(u.x), int(u.y)), r + 5, 1)
            if getattr(u, "poison_prep_t", 0) > 0:
                pygame.draw.circle(surf, POISON, (int(u.x) + r, int(u.y) - r), 3)
            if getattr(u, "balth_aura_t", 0) > 0:
                pygame.draw.circle(surf, (70, 150, 255), (int(u.x), int(u.y)), 70, 1)
            if getattr(u, "ether_renew_t", 0) > 0 or getattr(u, "aura_restore_t", 0) > 0:
                pygame.draw.circle(surf, MANA, (int(u.x), int(u.y)), r + 6, 1)
            if u.blind_t > 0:
                pygame.draw.circle(surf, WHITE, (int(u.x), int(u.y)), r + 12, 1)
            if u.near_ward:
                pygame.draw.circle(surf, WATER, (int(u.x), int(u.y)), r + 3, 1)
            fx, fy = math.cos(u.facing), math.sin(u.facing)
            pygame.draw.line(surf, WHITE, (u.x + fx * r, u.y + fy * r), (u.x + fx * (r + 10), u.y + fy * (r + 10)), 2)
            if u.knockdown_t > 0:
                ang = self.time * 6
                pygame.draw.circle(surf, GOLD, (int(u.x + math.cos(ang) * 16), int(u.y + math.sin(ang) * 10)), 5, 1)
                pygame.draw.circle(surf, (220, 200, 80), (int(u.x + math.cos(ang + 3.14) * 16), int(u.y + math.sin(ang + 3.14) * 10)), 5, 1)
            if getattr(u, "augury_t", 0) > 0 or getattr(u, "reaper_t", 0) > 0:
                pygame.draw.circle(surf, (70, 110, 60), (int(u.x), int(u.y)), r + 5, 1)
            if u.cls == "Warrior" and u.storm_t > 0:
                pygame.draw.circle(surf, (220, 180, 80), (int(u.x), int(u.y)), 70, 1)
            bw = 36
            pygame.draw.rect(surf, (40, 20, 20), (u.x - 18, u.y - r - 10, bw, 4))
            pygame.draw.rect(surf, GREEN, (u.x - 18, u.y - r - 10, bw * (u.hp / max(1.0, u.max_hp)), 4))
            pygame.draw.rect(surf, (20, 28, 50), (u.x - 18, u.y - r - 16, bw, 3))
            pygame.draw.rect(surf, (80, 170, 255), (u.x - 18, u.y - r - 16, bw * (u.energy / max(1.0, u.max_energy or 1)), 3))
            if u.channel and u.channel_t > 0:
                mx = max(0.05, getattr(u, "channel_max", 1.0) or 1.0)
                frac = max(0.0, min(1.0, 1.0 - u.channel_t / mx))
                pygame.draw.rect(surf, (40, 24, 50), (u.x - 18, u.y + r + 8, bw, 4))
                pygame.draw.rect(surf, (210, 120, 220), (u.x - 18, u.y + r + 8, bw * frac, 4))
                pygame.draw.rect(surf, (240, 200, 255), (u.x - 18, u.y + r + 8, bw, 4), 1)
            if getattr(u, "diversion_t", 0) > 0 and random.random() < 0.5:
                self.particles.append(Particle(u.x + random.uniform(-10, 10), u.y - r - 8, random.uniform(-20, 20), random.uniform(-50, -10), 0.35, 0.35, (230, 140, 230), 2))
            if getattr(u, "insec_t", 0) > 0:
                pygame.draw.circle(surf, (200, 80, 190), (int(u.x), int(u.y)), r + 6, 1)
            if getattr(u, "wastrel_t", 0) > 0:
                pygame.draw.circle(surf, (180, 70, 200), (int(u.x), int(u.y)), r + 8, 1)
            if u.shield > 0:
                pygame.draw.rect(surf, HOLY2, (u.x - 18, u.y - r - 14, bw * min(1, u.shield / 35), 3))

        mx, my = pygame.mouse.get_pos()
        hover = None
        best = 999
        for u in self.units:
            if not u.alive and u.cls not in PET_KINDS:
                if not u.alive:
                    continue
            size = 44 if u.infernal else (30 if u.is_pet or u.clone else 38)
            if getattr(u, "avatar_t", 0) > 0:
                size = int(size * 1.5)
            r = size // 2
            d = math.hypot(mx - u.x, my - u.y)
            if d <= r + 8 and d < best:
                best = d
                hover = u
        if hover:
            tag = hover.cls if hover.alive else f"{hover.cls} (down)"
            title = FONT_SM.render(f"{hover.name}  •  {tag}", True, WHITE)
            skills = [s[0] for s in SKILLS.get(hover.cls, [])]
            rows = []
            for name in skills:
                cd = hover.cds.get(name, 0) if hover.alive else 1
                col = MUTED if cd > 0 else WHITE
                extra = f"  {cd:.1f}s" if cd > 0 and hover.alive else ""
                rows.append(FONT_TINY.render(name + extra, True, col))
            tw = max([title.get_width()] + [r.get_width() for r in rows] + [80]) + 16
            th = 12 + title.get_height() + 6 + 16 * len(rows)
            x = min(max(8, mx + 14), W - tw - 8)
            y = min(max(64, my - 12), H - th - 8)
            box = pygame.Rect(x, y, tw, th)
            pygame.draw.rect(surf, PANEL, box, border_radius=6)
            pygame.draw.rect(surf, GOLD if hover.team == 0 else RED, box, 1, border_radius=6)
            surf.blit(title, (x + 8, y + 6))
            ty = y + 8 + title.get_height() + 4
            for r in rows:
                surf.blit(r, (x + 8, ty))
                ty += 16


class BotCard:
    def __init__(self, name, cls):
        self.name = name
        self.cls = cls
        self.wins = 0
        self.losses = 0

    @property
    def mmr(self):
        g = self.wins + self.losses
        if g == 0:
            return 1000
        return int(800 + (self.wins / g) * 600 + g * 4)


def team_mmr(team):
    if not team:
        return 1000
    return int(sum(b.mmr for b in team) / len(team))


def elo_delta(my_mmr, opp_mmr, won):
    expected = 1.0 / (1.0 + 10 ** ((opp_mmr - my_mmr) / 400.0))
    return int(round(RANK_K * ((1.0 if won else 0.0) - expected)))


def count_roles(classes):
    h = sum(1 for c in classes if c in HEAL_PICKS)
    k = sum(1 for c in classes if c in TANK_PICKS)
    d = len(classes) - h - k
    return d, h, k


def legal_ranked_comp(size, classes):
    return len(classes) == size


def format_comp(d, h, k):
    parts = []
    if d:
        parts.append(f"{d} DPS")
    if k:
        parts.append(f"{k} Tank" + ("s" if k != 1 else ""))
    if h:
        parts.append(f"{h} Healer" + ("s" if h != 1 else ""))
    return " + ".join(parts) if parts else "—"


def draw_comp_guide(size, x, y):
    rows = RANKED_COMPS.get(size, [])
    title = FONT_SM.render(f"{size}v{size} compositions", True, GOLD)
    lines = [FONT_TINY.render(format_comp(d, h, k), True, WHITE) for d, h, k in rows]
    w = max([title.get_width()] + [im.get_width() for im in lines] + [120]) + 24
    hgt = 16 + title.get_height() + 8 + 18 * len(lines) + 12
    box = pygame.Rect(x, y, w, hgt)
    if box.right > W - 8:
        box.x = W - 8 - w
    if box.bottom > H - 8:
        box.y = H - 8 - hgt
    pygame.draw.rect(SCREEN, PANEL, box, border_radius=8)
    pygame.draw.rect(SCREEN, GOLD, box, 1, border_radius=8)
    SCREEN.blit(title, (box.x + 12, box.y + 10))
    ty = box.y + 14 + title.get_height()
    for im in lines:
        SCREEN.blit(im, (box.x + 12, ty))
        ty += 18
    return box


def ranked_pick_ok(size, current, cls):
    return len(current) < size


def classes_from_comp(dmg_n, heal_n, tank_n=0):
    dps_pool = [c for c in DMG_CLASSES if c not in TANK_PICKS] or list(DPS_PICKS)
    picks = [random.choice(dps_pool) for _ in range(dmg_n)]
    picks += [random.choice(HEAL_PICKS) for _ in range(heal_n)]
    picks += [random.choice(TANK_PICKS) for _ in range(tank_n)]
    random.shuffle(picks)
    return picks


def load_ranked_teams():
    if not os.path.exists(TEAMS_PATH):
        return []
    try:
        with open(TEAMS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_ranked_teams(teams):
    with open(TEAMS_PATH, "w", encoding="utf-8") as f:
        json.dump(teams, f, indent=2)


class Game:
    def __init__(self):
        self.state = "menu"
        self.gp = START_GP
        self.mode = None
        self.team_a = []
        self.team_b = []
        self.bet_team = None
        self.bet_mult = 1
        self.rank_edit_id = None
        self.comp_help = False
        self.board_sort = "dmg"
        self.board_desc = True
        self.match = None
        self.msg = ""
        self.draft_side = 0
        self.name_i = 0
        self.ranked_teams = load_ranked_teams()
        self.rank_size = 2
        self.rank_selected = None
        self.rank_build = []
        self.rank_mmr_delta = 0
        self.is_ranked = False
        self.opp_mmr = START_RANK_MMR

    def next_name(self):
        n = BOT_NAMES[self.name_i % len(BOT_NAMES)]
        self.name_i += 1
        return n + str(random.randint(1, 99))

    def random_team(self, n):
        return [BotCard(self.next_name(), random.choice(CLASSES)) for _ in range(n)]

    def start_random(self):
        self.mode = "Random Arenas"
        self.is_ranked = False
        self.team_a = self.random_team(4)
        self.team_b = self.random_team(4)
        self.bet_team = None
        self.bet_mult = 1
        self.state = "lobby"

    def start_ascent_draft(self):
        self.mode = "Heroes Ascent"
        self.is_ranked = False
        self.team_a, self.team_b = [], []
        self.draft_side = 0
        self.bet_team = None
        self.bet_mult = 1
        self.state = "draft"

    def add_draft(self, cls):
        card = BotCard(self.next_name(), cls)
        if self.draft_side == 0:
            if len(self.team_a) < 8:
                self.team_a.append(card)
            if len(self.team_a) == 8:
                self.draft_side = 1
        else:
            if len(self.team_b) < 8:
                self.team_b.append(card)
            if len(self.team_b) == 8:
                self.state = "lobby"

    def teams_for_size(self, size):
        return [t for t in self.ranked_teams if t.get("size") == size]

    def persist_teams(self):
        save_ranked_teams(self.ranked_teams)

    def merge_members(self, classes, old_members=None):
        leftover = [dict(m) for m in (old_members or [])]
        out = []
        for cls in classes:
            hit = None
            for i, m in enumerate(leftover):
                if m.get("cls") == cls:
                    hit = leftover.pop(i)
                    break
            if hit:
                hit["cls"] = cls
                out.append(hit)
            else:
                out.append({"cls": cls, "name": self.next_name(), "wins": 0, "losses": 0})
        return out

    def make_team(self, size, classes):
        if self.rank_edit_id:
            for team in self.ranked_teams:
                if team.get("id") == self.rank_edit_id:
                    team["classes"] = list(classes)
                    team["members"] = self.merge_members(classes, team.get("members") or [
                        {"cls": c, "name": self.next_name(), "wins": team.get("wins", 0), "losses": team.get("losses", 0)}
                        for c in team.get("classes", [])
                    ])
                    self.persist_teams()
                    self.rank_edit_id = None
                    return team
        n = len(self.teams_for_size(size)) + 1
        members = self.merge_members(classes, None)
        team = {"id": f"{size}-{random.randint(1000, 9999)}-{n}", "name": f"{size}v{size} Squad {n}", "size": size, "classes": list(classes), "members": members, "mmr": START_RANK_MMR, "wins": 0, "losses": 0}
        self.ranked_teams.append(team)
        self.persist_teams()
        return team

    def remove_team(self, team_id):
        self.ranked_teams = [t for t in self.ranked_teams if t.get("id") != team_id]
        if self.rank_selected and self.rank_selected.get("id") == team_id:
            self.rank_selected = None
        self.persist_teams()

    def team_to_cards(self, rec):
        cards = []
        members = rec.get("members") or []
        for i, cls in enumerate(rec["classes"]):
            m = members[i] if i < len(members) and members[i].get("cls") == cls else None
            if m is None:
                for mm in members:
                    if mm.get("cls") == cls and mm.get("_used") is not True:
                        m = mm
                        mm["_used"] = True
                        break
            c = BotCard((m or {}).get("name") or self.next_name(), cls)
            c.wins = (m or {}).get("wins", rec.get("wins", 0))
            c.losses = (m or {}).get("losses", rec.get("losses", 0))
            cards.append(c)
        return cards

    def bot_ranked_opponent(self, size, around_mmr):
        dmg_n, heal_n, tank_n = random.choice(RANKED_COMPS[size])
        mmr = max(600, int(random.gauss(around_mmr, 40)))
        return {"id": "bot", "name": f"Queue {size}s", "size": size, "classes": classes_from_comp(dmg_n, heal_n, tank_n), "mmr": mmr, "wins": max(0, int((mmr - 800) / 30)), "losses": max(0, int((1200 - mmr) / 30))}

    def queue_ranked(self):
        if not self.rank_selected:
            self.msg = "Select one of your teams."
            return
        if self.rank_selected["size"] != self.rank_size:
            self.msg = "That team is the wrong bracket."
            return
        if len(self.rank_selected.get("classes", [])) != self.rank_size:
            self.msg = "Team is the wrong size for this bracket."
            return
        self.is_ranked = True
        self.mode = f"Ranked {self.rank_size}v{self.rank_size}"
        mine = self.rank_selected
        opp = self.bot_ranked_opponent(self.rank_size, mine["mmr"])
        self.opp_mmr = opp["mmr"]
        self.team_a = self.team_to_cards(mine)
        self.team_b = self.team_to_cards(opp)
        self.bet_team = None
        self.msg = ""
        self.state = "lobby"

    def begin_fight(self):
        if not self.is_ranked and self.bet_team is None:
            self.msg = "Pick a side to bet on."
            return
        self.match = Match(self.team_a, self.team_b)
        self.state = "fight"
        self.msg = ""

    def settle(self):
        w = self.match.winner
        winners = self.team_a if w == 0 else self.team_b
        losers = self.team_b if w == 0 else self.team_a
        for b in winners:
            b.wins += 1
        for b in losers:
            b.losses += 1
        extra = ""
        self.rank_mmr_delta = 0
        if self.is_ranked and self.rank_selected:
            my = self.rank_selected["mmr"]
            delta = elo_delta(my, self.opp_mmr, w == 0)
            self.rank_mmr_delta = delta
            self.rank_selected["mmr"] = max(100, my + delta)
            if w == 0:
                self.rank_selected["wins"] += 1
            else:
                self.rank_selected["losses"] += 1
            for rec in self.ranked_teams:
                if rec.get("id") == self.rank_selected["id"]:
                    rec["mmr"] = self.rank_selected["mmr"]
                    rec["wins"] = self.rank_selected["wins"]
                    rec["losses"] = self.rank_selected["losses"]
                    rec["classes"] = [b.cls for b in self.team_a]
                    rec["members"] = [{"cls": b.cls, "name": b.name, "wins": b.wins, "losses": b.losses} for b in self.team_a]
                    self.rank_selected = rec
            self.persist_teams()
            sign = "+" if delta >= 0 else ""
            extra = f"   Team MMR {my} → {self.rank_selected['mmr']} ({sign}{delta})"
        if self.is_ranked:
            self.msg = ("Victory." if w == 0 else "Defeat.") + extra
        elif self.bet_team == w:
            pay = WIN_PAY * self.bet_mult
            self.gp += pay
            self.msg = f"Correct call. +{pay} GP  (x{self.bet_mult}){extra}"
        else:
            pay = LOSS_PAY * self.bet_mult
            self.gp += pay
            self.msg = f"Wrong call. {pay} GP  (x{self.bet_mult}){extra}"
        self.state = "result"

    def draw_header(self, title):
        pygame.draw.rect(SCREEN, PANEL, (0, 0, W, 56))
        draw_text(SCREEN, title, FONT, WHITE, (20, 16))
        draw_text(SCREEN, f"{self.gp} GP", FONT, GOLD, (W - 140, 16))

    def button(self, rect, label, hot=False):
        pygame.draw.rect(SCREEN, GOLD_DIM if hot else PANEL2, rect, border_radius=8)
        pygame.draw.rect(SCREEN, GOLD, rect, 2, border_radius=8)
        draw_text(SCREEN, label, FONT, WHITE, rect.center, center=True)
        return rect


def run():
    g = Game()
    running = True
    while running:
        dt = min(CLOCK.tick(FPS) / 1000.0, 0.05)
        mx, my = pygame.mouse.get_pos()
        click = False
        pygame.event.pump()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                if g.state in ("fight", "result", "lobby", "draft", "modes", "ranked", "rank_build", "notes"):
                    g.state = "menu"
                    g.match = None
                else:
                    running = False
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                click = True

        SCREEN.fill(BG)

        if g.state == "menu":
            draw_text(SCREEN, "Momo Arenas", FONT_XL, GOLD, (W // 2, 15), center=True)
            draw_text(SCREEN, "microtransactions coming soon!", FONT, MUTED, (W // 2, 53), center=True)
            pick_from_roles(False, mx, my, dps_y=430, heal_y=270, radius=25, tank_y=115)
            r1 = pygame.Rect(W // 2 - 160, 560, 320, 40)
            rR = pygame.Rect(W // 2 - 160, 600, 320, 40)
            r2 = pygame.Rect(W // 2 - 160, 640, 320, 40)
            rN = pygame.Rect(W // 2 - 160, 680, 320, 40)
            g.button(r1, "Open Lobby")
            g.button(rR, "Ranked")
            g.button(r2, "Quit")
            g.button(rN, "Patch Notes")
            if click and r1.collidepoint(mx, my):
                g.state = "modes"
            if click and rR.collidepoint(mx, my):
                g.msg = ""
                g.state = "ranked"
            if click and r2.collidepoint(mx, my):
                running = False
            if click and rN.collidepoint(mx, my):
                g.state = "notes"

        elif g.state == "notes":
            g.draw_header("Patch Notes")
            y = 80
            for title, bullets in PATCH_NOTES[:2]:
                draw_text(SCREEN, title, FONT, GOLD, (80, y))
                y += 32
                for b in bullets:
                    draw_text(SCREEN, "•  " + b, FONT_TINY, WHITE, (96, y))
                    y += 20
                y += 16
            back = pygame.Rect(40, H - 70, 140, 40)
            g.button(back, "Back")
            if click and back.collidepoint(mx, my):
                g.state = "menu"

        elif g.state == "modes":
            g.draw_header("New Lobby — Choose Mode")
            draw_text(SCREEN, "Random Arenas", FONT_LG, WHITE, (W // 4, 200), center=True)
            draw_text(SCREEN, "4 random bots each side", FONT_SM, MUTED, (W // 4, 250), center=True)
            ra = pygame.Rect(W // 4 - 120, 300, 240, 50)
            g.button(ra, "Queue Random 4v4")
            draw_text(SCREEN, "Heroes Ascent", FONT_LG, WHITE, (3 * W // 4, 200), center=True)
            draw_text(SCREEN, "8v8 — you pick both lineups", FONT_SM, MUTED, (3 * W // 4, 250), center=True)
            ha = pygame.Rect(3 * W // 4 - 120, 300, 240, 50)
            g.button(ha, "Draft 8v8")
            rk = pygame.Rect(W // 2 - 120, 420, 240, 50)
            g.button(rk, "Ranked Brackets")
            back = pygame.Rect(40, H - 70, 140, 40)
            g.button(back, "Back")
            if click and ra.collidepoint(mx, my):
                g.start_random()
            if click and ha.collidepoint(mx, my):
                g.start_ascent_draft()
            if click and rk.collidepoint(mx, my):
                g.msg = ""
                g.state = "ranked"
            if click and back.collidepoint(mx, my):
                g.state = "menu"

        elif g.state == "draft":
            side = "BLUE" if g.draft_side == 0 else "RED"
            g.draw_header(f"Heroes Ascent Draft — picking {side} ({len(g.team_a)}/8 vs {len(g.team_b)}/8)")
            draw_text(SCREEN, "Pick from DPS or Healer.", FONT, MUTED, (W // 2, 72), center=True)
            picked = pick_from_roles(click, mx, my, dps_y=430, heal_y=270, radius=25, tank_y=115)
            if picked:
                g.add_draft(picked)
            draw_text(SCREEN, "Blue", FONT, BLUE, (4, 635))
            for i, b in enumerate(g.team_a):
                draw_class_icon(SCREEN, b.cls, 20 + (i % 8) * 80, 688, 24, show_label=False)
            draw_text(SCREEN, "Red", FONT, RED, (590, 635))
            for i, b in enumerate(g.team_b):
                draw_class_icon(SCREEN, b.cls, 644 + (i % 8) * 80, 688, 24, show_label=False)

        elif g.state == "ranked":
            g.draw_header("Ranked Arena — permanent teams")
            draw_text(SCREEN, "Pick a bracket, build or select a team, then queue. No betting — MMR only.", FONT_SM, MUTED, (W // 2, 72), center=True)
            for i, sz in enumerate(RANKED_SIZES):
                rect = pygame.Rect(80 + i * 300, 100, 270, 46)
                g.button(rect, f"Ranked {sz}v{sz}", g.rank_size == sz)
                if click and rect.collidepoint(mx, my):
                    g.rank_size = sz
                    g.rank_selected = None
                    g.msg = ""
            mine = g.teams_for_size(g.rank_size)
            draw_text(SCREEN, f"Your {g.rank_size}v{g.rank_size} teams", FONT, WHITE, (80, 168))
            if not mine:
                draw_text(SCREEN, "No team yet. Create one.", FONT_SM, MUTED, (80, 210))
            del_hits, sel_hits, edit_hits = [], [], []
            for i, rec in enumerate(mine[:6]):
                rx = pygame.Rect(80, 200 + i * 70, 720, 62)
                ok = True
                hot = ok and g.rank_selected and g.rank_selected.get("id") == rec.get("id")
                bg = (28, 28, 34) if not ok else (GOLD_DIM if hot else PANEL2)
                bd = (70, 70, 78) if not ok else (GOLD if hot else (70, 78, 96))
                pygame.draw.rect(SCREEN, bg, rx, border_radius=8)
                pygame.draw.rect(SCREEN, bd, rx, 2, border_radius=8)
                name_col = MUTED if not ok else WHITE
                draw_text(SCREEN, rec["name"] + ("" if ok else "  (illegal comp)"), FONT, name_col, (rx.x + 16, rx.y + 8))
                draw_text(SCREEN, f"{rec['wins']}-{rec['losses']}   MMR {rec['mmr']}", FONT_SM, MUTED if not ok else GOLD, (rx.x + 16, rx.y + 34))
                for j, cls in enumerate(rec["classes"]):
                    draw_class_icon(SCREEN, cls, rx.x + 390 + j * 32, rx.y + 31, 13, show_label=False)
                dx = pygame.Rect(rx.right - 92, rx.y + 14, 80, 34)
                ex = pygame.Rect(rx.right - 184, rx.y + 14, 84, 34)
                g.button(dx, "Remove")
                g.button(ex, "Edit")
                if ok:
                    sel_hits.append((rx, rec))
                del_hits.append((dx, rec))
                edit_hits.append((ex, rec))
            nb = pygame.Rect(840, 200, 360, 50)
            qb = pygame.Rect(840, 270, 360, 50)
            bb = pygame.Rect(840, 340, 360, 50)
            g.button(nb, f"Create {g.rank_size}v{g.rank_size} Team")
            g.button(qb, "Queue Match")
            g.button(bb, "Back")
            info = pygame.Rect(840, 400, 80, 32)
            g.button(info, "?", g.comp_help)
            if g.comp_help:
                draw_comp_guide(g.rank_size, 840, 440)
            if g.msg:
                draw_text(SCREEN, g.msg, FONT_SM, ORANGE, (840, 500))
            if click:
                handled = False
                for dx, rec in del_hits:
                    if dx.collidepoint(mx, my):
                        g.remove_team(rec["id"])
                        g.msg = "Team removed."
                        handled = True
                        break
                if not handled:
                    for ex, rec in edit_hits:
                        if ex.collidepoint(mx, my):
                            g.rank_edit_id = rec.get("id")
                            g.rank_build = list(rec.get("classes", []))
                            g.rank_selected = rec
                            g.msg = f"Editing {rec['name']} — unchanged classes keep their record."
                            g.state = "rank_build"
                            handled = True
                            break
                if not handled:
                    for rx, t in sel_hits:
                        if rx.collidepoint(mx, my):
                            g.rank_selected = t
                            g.msg = f"Selected {t['name']}  MMR {t['mmr']}"
                            handled = True
                            break
                    if nb.collidepoint(mx, my):
                        g.rank_build = []
                        g.rank_edit_id = None
                        g.state = "rank_build"
                    elif qb.collidepoint(mx, my):
                        g.queue_ranked()
                    elif bb.collidepoint(mx, my):
                        g.comp_help = False
                        g.state = "menu"
                    elif info.collidepoint(mx, my):
                        g.comp_help = not g.comp_help
                        handled = True

        elif g.state == "rank_build":
            need = g.rank_size
            g.draw_header(f"Build Ranked {need}v{need} Team  ({len(g.rank_build)}/{need})")
            picked = pick_from_roles(click, mx, my, dps_y=430, heal_y=270, radius=25, tank_y=115)
            if picked and len(g.rank_build) < need:
                if ranked_pick_ok(need, g.rank_build, picked):
                    g.rank_build.append(picked)
                    g.msg = ""
                else:
                    g.msg = "That pick cannot finish a legal ranked composition."
            d, h, k = count_roles(g.rank_build)
            draw_text(SCREEN, f"Current  {d} DPS · {h} Heal · {k} Tank", FONT_SM, GOLD, (W // 2, 350), center=True)
            info = pygame.Rect(W - 70, 64, 36, 32)
            g.button(info, "?", g.comp_help)
            if g.comp_help:
                draw_comp_guide(need, W - 280, 100)
            draw_text(SCREEN, "Roster", FONT_SM, MUTED, (400, 550))
            for i, cls in enumerate(g.rank_build):
                draw_class_icon(SCREEN, cls, 400 + i * 90, 600, 28, show_label=False)
            if g.msg:
                draw_text(SCREEN, g.msg, FONT_SM, ORANGE, (W // 2, 500), center=True)
            undo = pygame.Rect(80, H - 80, 160, 44)
            save = pygame.Rect(W // 2 - 100, H - 80, 200, 44)
            back = pygame.Rect(W - 220, H - 80, 160, 44)
            legal = len(g.rank_build) == need
            g.button(undo, "Undo")
            g.button(save, "Save Team", legal)
            g.button(back, "Cancel")
            if click and undo.collidepoint(mx, my) and g.rank_build:
                g.rank_build.pop()
                g.msg = ""
            if click and save.collidepoint(mx, my):
                if legal:
                    rec = g.make_team(need, g.rank_build)
                    g.rank_selected = rec
                    g.msg = f"Saved {rec['name']}"
                    g.state = "ranked"
                else:
                    g.msg = "Roster is not a legal ranked composition."
            if click and info.collidepoint(mx, my):
                g.comp_help = not g.comp_help
            elif click and back.collidepoint(mx, my):
                g.comp_help = False
                g.state = "ranked"

        elif g.state == "lobby":
            g.draw_header(f"Lobby — {g.mode}")
            if g.is_ranked and g.rank_selected:
                draw_text(SCREEN, f"Your team MMR {g.rank_selected['mmr']}", FONT, BLUE, (W // 4, 80), center=True)
                draw_text(SCREEN, f"Enemy MMR {g.opp_mmr}", FONT, RED, (3 * W // 4, 80), center=True)
                draw_text(SCREEN, "No betting in ranked. Win to climb.", FONT_SM, MUTED, (W // 2, 112), center=True)
            else:
                draw_text(SCREEN, f"Blue MMR {team_mmr(g.team_a)}", FONT, BLUE, (W // 4, 80), center=True)
                draw_text(SCREEN, f"Red MMR {team_mmr(g.team_b)}", FONT, RED, (3 * W // 4, 80), center=True)
                draw_text(SCREEN, "MMR is just a record. Any bot can pop off.", FONT_SM, MUTED, (W // 2, 112), center=True)

            def draw_team(team, x0, y0):
                for i, b in enumerate(team):
                    cx = x0 + (i % 4) * 110
                    cy = y0 + (i // 4) * 130
                    draw_class_icon(SCREEN, b.cls, cx, cy, 28, show_label=False)
                    draw_text(SCREEN, b.name, FONT_TINY, WHITE, (cx, cy + 36), center=True)
                    draw_text(SCREEN, b.cls, FONT_TINY, MUTED, (cx, cy + 50), center=True)
                    draw_text(SCREEN, f"{b.wins}-{b.losses}  {b.mmr}", FONT_TINY, MUTED, (cx, cy + 64), center=True)

            draw_team(g.team_a, 120, 200)
            draw_team(g.team_b, W // 2 + 80, 200)
            st = pygame.Rect(W // 2 - 110, H - 120, 220, 48)
            if g.is_ranked:
                g.button(st, "Start Match")
                if click and st.collidepoint(mx, my):
                    g.begin_fight()
            else:
                ba = pygame.Rect(W // 4 - 110, H - 120, 220, 48)
                bb = pygame.Rect(3 * W // 4 - 110, H - 120, 220, 48)
                g.button(ba, "Bet BLUE", g.bet_team == 0)
                g.button(bb, "Bet RED", g.bet_team == 1)
                g.button(st, "Start Match")
                up = pygame.Rect(W // 2 - 110, H - 64, 100, 36)
                dn = pygame.Rect(W // 2 + 10, H - 64, 100, 36)
                g.button(up, "Raise")
                g.button(dn, "Lower")
                win_p = WIN_PAY * g.bet_mult
                lose_p = LOSS_PAY * g.bet_mult
                draw_text(SCREEN, f"Stake x{g.bet_mult}   Win +{win_p} / Lose {lose_p}   Purse {g.gp} GP", FONT_SM, GOLD, (W // 2, 140), center=True)
                max_mult = max(1, g.gp // max(1, abs(LOSS_PAY)))
                if click and ba.collidepoint(mx, my):
                    g.bet_team = 0
                    g.msg = f"Wager x{g.bet_mult} on Blue."
                if click and bb.collidepoint(mx, my):
                    g.bet_team = 1
                    g.msg = f"Wager x{g.bet_mult} on Red."
                if click and up.collidepoint(mx, my):
                    if g.bet_mult < max_mult:
                        g.bet_mult += 1
                        g.msg = f"Raised to x{g.bet_mult}  (+{WIN_PAY * g.bet_mult} / {LOSS_PAY * g.bet_mult})"
                    else:
                        g.msg = "Purse cannot cover a bigger loss."
                if click and dn.collidepoint(mx, my) and g.bet_mult > 1:
                    g.bet_mult -= 1
                    g.msg = f"Lowered to x{g.bet_mult}"
                if click and st.collidepoint(mx, my):
                    g.begin_fight()
            if g.msg:
                draw_text(SCREEN, g.msg, FONT_SM, ORANGE, (W // 2, H - 56), center=True)

        elif g.state == "fight":
            g.match.update(dt)
            g.draw_header(f"{g.mode}   {g.match.time:.0f}s")
            if g.is_ranked:
                draw_text(SCREEN, "Ranked — MMR only", FONT_SM, GOLD, (W // 2, 36), center=True)
            else:
                side = "BLUE" if g.bet_team == 0 else "RED"
                draw_text(SCREEN, f"Your ticket: {side}  x{g.bet_mult}", FONT_SM, GOLD, (W // 2, 36), center=True)
            g.match.draw(SCREEN)
            draw_text(SCREEN, f"Blue alive {len(g.match.living(0))}", FONT_SM, BLUE, (60, H - 40))
            draw_text(SCREEN, f"Red alive {len(g.match.living(1))}", FONT_SM, RED, (W - 180, H - 40))
            if g.match.done:
                g.settle()

        elif g.state == "result":
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((10, 12, 18, 230))
            SCREEN.blit(overlay, (0, 0))
            win_name = "BLUE" if g.match.winner == 0 else "RED"
            draw_text(SCREEN, f"{win_name} WINS", FONT_LG, GOLD, (W // 2, 36), center=True)
            draw_text(SCREEN, g.msg, FONT_SM, WHITE, (W // 2, 68), center=True)
            foe = 1 if (g.is_ranked or g.bet_team == 0) else 0
            if g.is_ranked:
                foe = 1
            draw_text(SCREEN, "Enemy lineup", FONT_SM, RED if foe == 1 else BLUE, (80, 92))
            foes = [u for u in g.match.units if u.team == foe and not u.is_pet and not getattr(u, "is_spirit", False) and u.cls in CLASSES]
            for i, u in enumerate(foes):
                cx = 70 + i * 70
                draw_class_icon(SCREEN, u.cls, cx, 130, 22, show_label=False)
                draw_text(SCREEN, u.cls[:8], FONT_TINY, MUTED, (cx, 158), center=True)
            rows = [u for u in g.match.units if not u.is_pet and not getattr(u, "is_spirit", False) and u.cls in CLASSES]
            key = {
                "dmg": lambda u: getattr(u, "stat_dmg", 0),
                "heal": lambda u: getattr(u, "stat_heal", 0),
                "taken": lambda u: getattr(u, "stat_taken", 0),
                "kills": lambda u: getattr(u, "stat_kills", 0),
                "deaths": lambda u: getattr(u, "stat_deaths", 0),
                "cc": lambda u: getattr(u, "stat_cc", 0),
                "abs": lambda u: getattr(u, "stat_absorb", 0),
            }[g.board_sort]
            rows.sort(key=key, reverse=g.board_desc)
            headers = [("Name", None, 60), ("Cls", None, 200), ("Dmg", "dmg", 300), ("Heal", "heal", 390), ("Taken", "taken", 480), ("Abs", "abs", 560), ("K", "kills", 640), ("D", "deaths", 700), ("CC", "cc", 760)]
            hy = 178
            head_hits = []
            for label, sk, x in headers:
                col = GOLD if sk == g.board_sort else MUTED
                r = pygame.Rect(x - 8, hy - 4, 90, 22)
                draw_text(SCREEN, label + (" ▼" if sk == g.board_sort and g.board_desc else " ▲" if sk == g.board_sort else ""), FONT_TINY, col, (x, hy))
                if sk:
                    head_hits.append((r, sk))
            y = hy + 22
            for u in rows:
                tcol = BLUE if u.team == 0 else RED
                pygame.draw.rect(SCREEN, (24, 28, 36), (50, y - 2, W - 100, 22), border_radius=3)
                draw_text(SCREEN, u.name[:14], FONT_TINY, tcol, (70, y))
                draw_text(SCREEN, u.cls, FONT_TINY, WHITE, (230, y))
                draw_text(SCREEN, str(int(getattr(u, "stat_dmg", 0))), FONT_TINY, WHITE, (300, y))
                draw_text(SCREEN, str(int(getattr(u, "stat_heal", 0))), FONT_TINY, GREEN, (390, y))
                draw_text(SCREEN, str(int(getattr(u, "stat_taken", 0))), FONT_TINY, RED, (480, y))
                draw_text(SCREEN, str(int(getattr(u, "stat_absorb", 0))), FONT_TINY, (140, 200, 255), (560, y))
                draw_text(SCREEN, str(int(getattr(u, "stat_kills", 0))), FONT_TINY, WHITE, (640, y))
                draw_text(SCREEN, str(int(getattr(u, "stat_deaths", 0))), FONT_TINY, MUTED, (700, y))
                draw_text(SCREEN, str(int(getattr(u, "stat_cc", 0))), FONT_TINY, (200, 180, 80), (760, y))
                y += 24
                if y > H - 90:
                    break
            ag = pygame.Rect(W // 2 - 220, H - 64, 200, 44)
            mn = pygame.Rect(W // 2 + 20, H - 64, 200, 44)
            g.button(ag, "Rematch Lobby")
            g.button(mn, "Main Menu")
            if click:
                for r, sk in head_hits:
                    if r.collidepoint(mx, my):
                        if g.board_sort == sk:
                            g.board_desc = not g.board_desc
                        else:
                            g.board_sort = sk
                            g.board_desc = True
                        break
                if ag.collidepoint(mx, my):
                    if g.mode == "Random Arenas":
                        g.start_random()
                    elif g.is_ranked:
                        g.queue_ranked()
                    else:
                        g.state = "lobby"
                        g.bet_team = None
                        g.msg = ""
                if mn.collidepoint(mx, my):
                    g.state = "menu"

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()
