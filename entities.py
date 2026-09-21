"""Game entities (Fighter, projectiles, effects) and the per-class AI.

The class AI lives here because it spawns Fighters, Particles, Tethers and
DelayedHeals directly. It is a mixin (ClassAI) that Match inherits from.
"""

import math
import random
from dataclasses import dataclass, field

import pygame

from colors import *
from classes import *
from sounds import sfx


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: tuple
    size: float
    gravity: float = 0.0

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, min(1.0, self.life / max(0.001, self.max_life)))
        a = max(0, min(255, int(220 * t)))
        r = max(1, int(self.size * (0.4 + 0.6 * t)))
        rgb = (int(max(0, min(255, self.color[0]))), int(max(0, min(255, self.color[1]))), int(max(0, min(255, self.color[2]))))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2))
        s.set_colorkey((0, 0, 0))
        pygame.draw.circle(s, rgb, (r + 1, r + 1), r)
        s.set_alpha(a)
        surf.blit(s, (int(self.x) - r, int(self.y) - r))


@dataclass
class Burst:
    x: float
    y: float
    life: float
    max_life: float
    color: tuple
    radius: float

    def update(self, dt):
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, min(1.0, 1.0 - self.life / max(0.001, self.max_life)))
        rad = max(1, int(self.radius * (0.3 + 0.7 * t)))
        a = max(0, min(255, int(160 * (1 - t))))
        rgb = (int(max(0, min(255, self.color[0]))), int(max(0, min(255, self.color[1]))), int(max(0, min(255, self.color[2]))))
        s = pygame.Surface((rad * 2 + 4, rad * 2 + 4))
        s.set_colorkey((0, 0, 0))
        pygame.draw.circle(s, rgb, (rad + 2, rad + 2), rad, max(1, min(3, rad)))
        s.set_alpha(a)
        surf.blit(s, (int(self.x) - rad, int(self.y) - rad))


@dataclass
class Tether:
    a: object
    b: object
    life: float
    color: tuple = HOLY

    def update(self, dt):
        self.life -= dt
        return self.life > 0 and self.a.alive and self.b.alive

    def draw(self, surf):
        pygame.draw.line(surf, self.color, (self.a.x, self.a.y), (self.b.x, self.b.y), 5)


@dataclass
class DelayedHeal:
    target: object
    amount: float
    delay: float
    kind: str = "holy"
    source: object = None

    def update(self, dt):
        self.delay -= dt
        return self.delay > 0


@dataclass
class Projectile:
    x: float
    y: float
    dx: float
    dy: float
    speed: float
    dmg: float
    team: int
    kind: str
    life: float = 1.2
    radius: int = 6
    pierce: int = 1
    hit_ids: list = field(default_factory=list)
    owner: object = None
    home: object = None
    on_hit: object = None

    def update(self, dt):
        h = self.home
        if h is not None and getattr(h, "alive", False):
            tx, ty = h.x - self.x, h.y - self.y
            n = math.hypot(tx, ty) or 1
            self.dx = self.dx * 0.72 + (tx / n) * 0.28
            self.dy = self.dy * 0.72 + (ty / n) * 0.28
            nn = math.hypot(self.dx, self.dy) or 1
            self.dx, self.dy = self.dx / nn, self.dy / nn
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt
        self.life -= dt
        return self.life > 0


@dataclass
class Fighter:
    name: str
    cls: str
    team: int
    x: float
    y: float
    max_hp: float = 100
    hp: float = 100
    speed: float = 90
    facing: float = 0.0
    cds: dict = field(default_factory=dict)
    slow_t: float = 0
    freeze_t: float = 0
    stun_t: float = 0
    fear_t: float = 0
    iceblock_t: float = 0
    block_t: float = 0
    sprint_t: float = 0
    storm_t: float = 0
    shield: float = 0
    favor_t: float = 0
    favor_tick: float = 0
    curse_t: float = 0
    curse_tick: float = 0
    rot_t: float = 0
    rot_tick: float = 0
    antiheal_t: float = 0
    channel: str = ""
    channel_t: float = 0
    channel_max: float = 1.0
    channel_acc: float = 0
    channel_target: object = None
    pentagram_used: bool = False
    infernal: bool = False
    fear_wander: bool = False
    fear_dir: tuple = (1.0, 0.0)
    fear_turn: float = 0
    knockdown_t: float = 0
    deepwound_t: float = 0
    daze_t: float = 0
    bleed: int = 0
    bleed_tick: float = 0
    rampage_t: float = 0
    soothe_t: float = 0
    soothe_tick: float = 0
    is_pet: bool = False
    pet_kind: str = ""
    owner_name: str = ""
    base_max: float = 0
    attacks_left: int = -1
    water_hex_t: float = 0
    water_armor_t: float = 0
    blur_t: float = 0
    near_ward: bool = False
    was_moving: bool = False
    soulmend_t: float = 0
    intercept: bool = False
    hauntbrand_t: float = 0
    spirit_form_t: float = 0
    last_cast: str = ""
    in_well: bool = False
    reversal_t: float = 0
    spirit_bond_t: float = 0
    spirit_bond_hits: int = 0
    holy_veil_t: float = 0
    dark_escape_t: float = 0
    illusion_t: float = 0
    flurry_t: float = 0
    visage_t: float = 0
    distortion_t: float = 0
    riposte_t: float = 0
    deflect_t: float = 0
    frail_armor: float = 0
    extra_armor: float = 0
    rez_ready: bool = True
    enemy_deaths_at_rez: int = 0
    morale_spent: bool = False
    pending_cast: object = None
    seeping_t: float = 0
    seeping_tick: float = 0
    barbed_t: float = 0
    barbed_tick: float = 0
    crit_eye_t: float = 0
    haste_t: float = 0
    master_t: float = 0
    energy: float = 20
    max_energy: float = 20
    burn_t: float = 0
    burn_tick: float = 0
    blind_t: float = 0
    mystic_t: float = 0
    fire_attune_t: float = 0
    djinn_t: float = 0
    weakness_t: float = 0
    ash_t: float = 0
    lyssa_t: float = 0
    earth_attune_t: float = 0
    kinetic_t: float = 0
    kite_t: float = 0
    kite_dir: tuple = (1.0, 0.0)
    slicer_ch: int = 0
    grasp_t: float = 0
    grasp_n: int = 0
    avatar_t: float = 0
    avatar_lock: float = 0
    fury_t: float = 0
    harrier_t: float = 0
    cracked_t: float = 0
    acted: bool = False
    landed: bool = False
    chase_t: float = 0.0
    poison_t: float = 0
    poison_tick: float = 0
    poison_prep_t: float = 0
    stride_t: float = 0
    last_skill: str = ""
    is_spirit: bool = False
    spirit_kind: str = ""
    spirit_life: float = 0
    spirit_age: float = 0
    ward_wep_t: float = 0
    kaolai_t: float = 0
    shield_regen_t: float = 0
    lifebond_t: float = 0
    balth_spirit_t: float = 0
    bonetti_t: float = 0
    bond_src: object = None
    spirit_src: object = None
    augury_t: float = 0
    augury_src: object = None
    reaper_t: float = 0
    reaper_src: object = None
    lead_atk: bool = False
    paradox_t: float = 0
    attack_lock: float = 0
    soul_n: int = 0
    soul_reset: float = 0
    stealth_t: float = 0
    gift_lock_t: float = 0
    hurt_t: float = 0
    dealt_t: float = 0
    gcd_t: float = 0
    plant_t: float = 0
    sheath_t: float = 0
    vital_t: float = 0
    mirage_t: float = 0
    watchful_t: float = 0
    meditate_t: float = 0
    zeal_t: float = 0
    shadow_form_t: float = 0
    shroud_t: float = 0
    feign_t: float = 0
    hold_t: float = 0
    soldier_t: float = 0
    ttl_t: float = 0
    dolyak_t: float = 0
    shield_st_t: float = 0
    glad_t: float = 0
    air_of_t: float = 0
    patient_t: float = 0
    protect_t: float = 0
    rod_t: float = 0
    spell_shield_t: float = 0
    breeze_t: float = 0
    haste_sh_t: float = 0
    fallback_t: float = 0
    aegis_t: float = 0
    hands_t: float = 0
    stable_t: float = 0
    balanced_t: float = 0
    shield_ch: int = 0
    air_attune_t: float = 0
    wind_t: float = 0
    surge_t: float = 0
    strike_hex_t: float = 0
    hex_notice_at: float = 0
    hex_cleanse_at: float = 0
    stat_dmg: float = 0
    stat_heal: float = 0
    stat_taken: float = 0
    stat_kills: int = 0
    stat_deaths: int = 0
    stat_cc: int = 0
    stat_absorb: float = 0
    flail_t: float = 0
    live_vic_t: float = 0
    migraine_t: float = 0
    frustrate_t: float = 0
    guardian_t: float = 0
    absorb_t: float = 0
    vigorous_t: float = 0
    glimmer_veil_t: float = 0
    insec_t: float = 0
    wastrel_t: float = 0
    wastrel_on: bool = False
    diversion_t: float = 0
    balth_aura_t: float = 0
    ether_renew_t: float = 0
    zealot_fire_t: float = 0
    aura_restore_t: float = 0
    reversal_cap: float = 28
    clone: bool = False
    alive: bool = True
    wins: int = 0
    losses: int = 0
    target: object = None
    xinrae_t: float = 0
    xinrae_src: object = None
    lament_t: float = 0
    lament_tick: float = 0
    renew_surge_t: float = 0
    renew_surge_tick: float = 0
    renew_surge_src: object = None
    resilient_t: float = 0
    ashes_t: float = 0
    ashes_active: bool = False
    glyph_charges: int = 0
    glyph_t: float = 0
    # --- Beast Master / pet support ---
    cripple_t: float = 0
    pet_feral_t: float = 0
    pet_feral_bonus: float = 0
    pet_brutal_stacks: int = 0
    pet_brutal_t: float = 0
    pet_dr_t: float = 0
    pet_poison_stacks: int = 0
    pet_poison_t: float = 0
    pet_poison_tick: float = 0
    pet_poison_src: object = None
    strike_as_one_t: float = 0
    strike_as_one_src: object = None
    gdw_t: float = 0
    gdw_src: object = None
    poo_t: float = 0
    poo_tick: float = 0
    poo_src: object = None
    pet_owner_cls: str = ""

    @property
    def mmr(self):
        games = self.wins + self.losses
        if games == 0:
            return 1000
        return int(800 + (self.wins / games) * 600 + games * 4)

    def locked(self):
        return self.freeze_t > 0 or self.stun_t > 0 or self.iceblock_t > 0 or self.knockdown_t > 0 or bool(self.channel)
    
    def has_condition(self):
        return (self.bleed > 0 or self.poison_t > 0 or self.burn_t > 0 or self.weakness_t > 0
                or self.blind_t > 0 or self.deepwound_t > 0 or self.slow_t > 0 or self.daze_t > 0)

    def has_hex(self):
        return any(getattr(self, a, 0) > 0 for a in HEX_ATTRS)

    def has_enchantment(self):
        return any(getattr(self, a, 0) > 0 for a in ENCHANT_ATTRS)

    def tick_status(self, dt):
        old_veil = self.holy_veil_t
        for attr in ("slow_t", "freeze_t", "stun_t", "fear_t", "iceblock_t", "block_t", "sprint_t", "storm_t", "favor_t", "curse_t", "rot_t", "antiheal_t",
                    "knockdown_t", "daze_t", "rampage_t", "soothe_t", "water_hex_t", "water_armor_t", "blur_t", "soulmend_t", "hauntbrand_t", "spirit_form_t",
                    "reversal_t", "spirit_bond_t", "holy_veil_t", "dark_escape_t", "illusion_t", "flurry_t", "visage_t", "distortion_t", "riposte_t", "deflect_t",
                    "seeping_t", "barbed_t", "crit_eye_t", "haste_t", "master_t", "burn_t", "blind_t", "mystic_t", "fire_attune_t", "djinn_t", "weakness_t", "ash_t", 
                    "lyssa_t", "earth_attune_t", "kinetic_t", "kite_t", "grasp_t", "avatar_t", "avatar_lock", "fury_t", "harrier_t", "cracked_t", "balth_aura_t", "ether_renew_t", 
                    "zealot_fire_t", "aura_restore_t", "poison_t", "poison_prep_t", "stride_t", "ward_wep_t", "kaolai_t", "shield_regen_t", "lifebond_t", "balth_spirit_t", "bonetti_t", 
                    "augury_t", "reaper_t", "paradox_t", "attack_lock", "insec_t", "wastrel_t", "diversion_t", "stealth_t", "gift_lock_t", "hurt_t", "guardian_t", "absorb_t", "vigorous_t", 
                    "glimmer_veil_t", "flail_t", "live_vic_t", "migraine_t", "frustrate_t", "dealt_t", "air_attune_t", "wind_t", "surge_t", "strike_hex_t", "gcd_t", "plant_t", "sheath_t", "vital_t", 
                    "mirage_t", "watchful_t", "meditate_t", "zeal_t", "shadow_form_t", "shroud_t", "feign_t", "hold_t", "riposte_t", "soldier_t", "ttl_t", "dolyak_t", "shield_st_t", "glad_t", "air_of_t", 
                    "patient_t", "protect_t", "rod_t", "spell_shield_t", "breeze_t", "haste_sh_t", "fallback_t", "aegis_t", "hands_t", "stable_t", "balanced_t", 
                    "xinrae_t","stable_t", "balanced_t", "lament_t", "renew_surge_t", "resilient_t", "ashes_t", "glyph_t",
                    "cripple_t", "pet_feral_t", "pet_brutal_t", "pet_dr_t", "pet_poison_t", "strike_as_one_t", "gdw_t", "poo_t"):
            v = getattr(self, attr, 0) or 0
            if v > 0:
                setattr(self, attr, max(0.0, v - dt))
        if self.fear_t <= 0:
            self.fear_wander = False
        if old_veil > 0 and self.holy_veil_t <= 0:
            for attr in ("curse_t", "antiheal_t", "blur_t", "water_hex_t", "hauntbrand_t"):
                if getattr(self, attr, 0) > 0:
                    setattr(self, attr, 0.0)
                    break
        extra = dt if self.in_well else 0.0
        hexed = self.curse_t > 0 or self.antiheal_t > 0 or self.blur_t > 0 or self.water_hex_t > 0 or self.seeping_t > 0 or self.ash_t > 0
        enchanted = self.favor_t > 0 or self.water_armor_t > 0 or self.illusion_t > 0 or self.holy_veil_t > 0 or self.spirit_bond_t > 0 or self.reversal_t > 0 or self.fire_attune_t > 0 or self.earth_attune_t > 0
        if self.stride_t > 0 and (hexed or enchanted):
            self.stride_t = 0
        if extra:
            for attr in ("slow_t", "freeze_t", "stun_t", "fear_t", "knockdown_t", "daze_t"):
                v = getattr(self, attr)
                if v > 0:
                    setattr(self, attr, max(0.0, v - extra))
        for k in list(self.cds):
            self.cds[k] = max(0.0, self.cds[k] - dt)
        if self.ashes_t <= 0 and self.ashes_active:
            self.ashes_active = False
            self.cds["Lamentation Hex"] = 0.0
            self.cds["Renewing Surge Hex"] = 0.0
        if self.ashes_t > 0:
            self.ashes_active = True
        if self.glyph_t <= 0:
            self.glyph_charges = 0
        if getattr(self, "glimmer_veil_t", 0) > 0 and self.cls == "Glimmer":
            self.energy = max(0.0, self.energy - 1.0 * dt)
            if self.energy <= 0:
                self.glimmer_veil_t = 0
        if getattr(self, "live_vic_hold", False):
            self.energy = max(0.0, self.energy - 1.0 * dt)
            if self.energy <= 0:
                self.live_vic_hold = False
                tgt = getattr(self, "live_vic_on", None)
                if tgt:
                    tgt.live_vic_t = 0
                    tgt.live_vic_src = None
        bonds = (1 if self.lifebond_t > 0 else 0) + (1 if self.balth_spirit_t > 0 else 0)
        if bonds and self.cls == "Bonder":
            self.energy = max(0.0, self.energy - bonds * dt)
            if self.energy <= 0:
                self.lifebond_t = 0
                self.balth_spirit_t = 0
        if self.cls in ("Warrior", "Thumper", "Slasher", "Balthazar", "Deathdancer"):
            regen = 2.0
        elif self.cls in ("Ranger", "Archer"):
            regen = 3.0
        else:
            regen = 4.0
        if getattr(self, "lyssa_t", 0) > 0:
            regen += 4.0
        self.energy = min(self.max_energy, self.energy + dt * regen)

    def ready(self, skill):
        if skill != "auto" and getattr(self, "gcd_t", 0) > 0:
            return False
        if self.cds.get(skill, 0) > 0:
            return False
        if skill == "Ward Against Melee" and getattr(self, "hurt_t", 0) <= 0:
            return False
        if skill in WARD_SKILLS and skill != "Ward Against Melee" and getattr(self, "hurt_t", 0) <= 0 and getattr(self, "dealt_t", 0) <= 0:
            return False
        cost = ENERGY_COST.get(skill, 0)
        cost = CLASS_ENERGY_OVERRIDE.get(self.cls, {}).get(skill, cost)
        if self.cls == "Beast Master" and skill in BEAST_DMG_SKILLS:
            cost *= 0.48
        if self.cls == "Lifesheath" and skill in SHEATH_ENCH:
            cost *= 0.52
        if self.cls == "AirEnchant" and skill in ("Air of Enchantment", "Patient Spirit", "Reversal of Fortune", "Protective Spirit", "Guardian", "Shield of Absorption"):
            cost = max(0, cost - 5)
        if self.cls == "Lingwah" and skill in ("Lamentation Hex", "Renewing Surge Hex") and self.ashes_t > 0:
            cost = max(0, cost - 4)
        return self.energy + 0.01 >= cost

    def use(self, skill, cd):
        cost = ENERGY_COST.get(skill, 0)
        cost = CLASS_ENERGY_OVERRIDE.get(self.cls, {}).get(skill, cost)
        if self.cls == "Beast Master" and skill in BEAST_DMG_SKILLS:
            cost *= 0.48
        if self.cls == "Lingwah" and skill in ("Lamentation Hex", "Renewing Surge Hex") and self.ashes_t > 0:
            cost = max(0, cost - 4)
        if self.glyph_charges > 0 and skill not in ("auto", "Glyph of Lesser Energy"):
            cost = max(0, cost - 10)
            self.glyph_charges -= 1
        if self.cls == "Lifesheath" and skill in SHEATH_ENCH:
            cost *= 0.52
        if self.cls == "AirEnchant" and skill in ("Air of Enchantment", "Patient Spirit", "Reversal of Fortune", "Protective Spirit", "Guardian", "Shield of Absorption"):
            cost = max(0, cost - 5)
        self.energy = max(0.0, self.energy - cost)
        if self.fire_attune_t > 0 and skill in FIRE_SKILLS:
            self.energy = min(self.max_energy, self.energy + 1 + 0.30 * cost)
        if getattr(self, "earth_attune_t", 0) > 0 and skill in EARTH_SKILLS:
            self.energy = min(self.max_energy, self.energy + 1 + 0.30 * cost)
        if getattr(self, "kinetic_t", 0) > 0 and cost > 0:
            self.kinetic_t = 12.0
        self.cds[skill] = cd
        self.acted = True
        if getattr(self, "vigorous_t", 0) > 0:
            self.heal(17)
        if getattr(self, "stealth_t", 0) > 0 and skill != "Sprint":
            self.stealth_t = 0
        if getattr(self, "wastrel_on", False):
            self.wastrel_on = False
            self.wastrel_t = 0
        if getattr(self, "diversion_t", 0) > 0 and skill != "auto":
            self.cds[skill] = self.cds.get(skill, 0) + 53
            self.diversion_t = 0
        if skill == "auto":
            if self.cls not in MELEE_CLS:
                self.plant_t = 0.45
            if getattr(self, "feign_t", 0) > 0:
                self.feign_t = 0
        else:
            self.last_skill = skill
            self.gcd_t = max(getattr(self, "gcd_t", 0), 1.0)
            sfx(skill, 0.1)
            if getattr(self, "feign_t", 0) > 0 and skill != "Feigned Neutrality":
                self.feign_t = 0
            if getattr(self, "breeze_t", 0) > 0:
                self.breeze_t = 0
            if self.bonetti_t > 0:
                self.bonetti_t = 0.0
        if any(k in skill.lower() for k in ("heal", "barrier", "favor", "grip", "soulmend", "devotion", "bene", "reversal", "bond", "veil", "mend", "wave", "sooth", "comfort", "rite", "glimmer", "gift", "light", "party")):
            self.landed = True
            self._casting_heal = True
        enchants = sum(1 for a in ("reversal_t", "favor_t", "water_armor_t", "illusion_t", "haste_t", "master_t", "mystic_t", "fire_attune_t", "lyssa_t", "earth_attune_t", "kinetic_t", "grasp_t", "harrier_t", "avatar_t", "ether_renew_t", "zealot_fire_t", "aura_restore_t", "balth_aura_t", "holy_veil_t", "spirit_bond_t") if getattr(self, a, 0) > 0)
        if self.ether_renew_t > 0 and cost > 0:
            self.energy = min(self.max_energy, self.energy + 4)
            self.heal(20 * max(1, enchants))
        if self.aura_restore_t > 0 and cost > 0:
            if self.cls == "Surger":
                self.energy = min(self.max_energy, self.energy + 10)
                self.heal(cost * 4.0)
            else:
                self.heal(cost * 5.0)
        if getattr(self, "air_attune_t", 0) > 0 and skill in AIR_SKILLS:
            self.energy = min(self.max_energy, self.energy + 10 + 0.30 * cost)

    def heal(self, amt, source=None):
        if not self.alive:
            return
        if self.antiheal_t > 0:
            amt *= 0.35
        amt *= max(0.0, getattr(self, "heal_mod", 1.0))
        if amt <= 0:
            return
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amt)
        got = self.hp - before
        src = source
        if src is None:
            src = getattr(self, "_last_healer", None)
        if src is not None and got > 0:
            src.stat_heal = getattr(src, "stat_heal", 0) + got

    def take(self, dmg, melee=False, source=None, projectile=False, unblockable=False):
        incoming = max(0.0, float(dmg))
        if self.iceblock_t > 0:
            self.stat_absorb = getattr(self, "stat_absorb", 0) + incoming
            return
        if getattr(self, "is_spirit", False):
            dmg *= 0.35
        if source and getattr(source, "cls", "") == "Deadsword":
            dmg *= 1.10
        if source and getattr(source, "cls", "") == "Surger":
            dmg *= 1.25
        src_cls = getattr(source, "cls", "") if source else ""
        own = getattr(source, "owner_ref", None) if source else None
        if src_cls == "Bellringer" or getattr(own, "cls", "") == "Bellringer":
            dmg *= 0.67
        if source and getattr(source, "honor_buff", False):
            dmg += 15
        if melee and source and getattr(source, "gdw_t", 0) > 0:
            dmg += 20
        if getattr(self, "ward_wep_t", 0) > 0 and not unblockable and random.random() < 0.5:
            self.stat_absorb = getattr(self, "stat_absorb", 0) + max(0.0, incoming if "incoming" in dir() else dmg)
            return "blocked"
        if getattr(self, "guardian_t", 0) > 0 and not unblockable and random.random() < 0.5:
            self.stat_absorb = getattr(self, "stat_absorb", 0) + max(0.0, incoming if "incoming" in dir() else dmg)
            return "blocked"
        if getattr(self, "absorb_t", 0) > 0:
            dmg = max(0.0, dmg - 5)
        if getattr(self, "pet_dr_t", 0) > 0:
            dmg = max(0.0, dmg - 21)
        if getattr(self, "kaolai_t", 0) > 0:
            dmg *= 0.88
        if source and getattr(source, "spirit_form_t", 0) > 0:
            dmg *= 0.55
        if source and getattr(source, "flurry_t", 0) > 0:
            dmg *= 0.75
        if source and getattr(source, "weakness_t", 0) > 0:
            dmg *= 0.7
        if getattr(self, "cracked_t", 0) > 0:
            dmg *= 1.22
        if getattr(self, "avatar_t", 0) > 0 and (melee or projectile):
            dmg *= 0.82
        if source and getattr(source, "harrier_t", 0) > 0 and getattr(self, "was_moving", False):
            dmg += 10
        if getattr(self, "kinetic_t", 0) > 0:
            dmg *= 0.55
        if getattr(self, "ash_t", 0) > 0 and source and random.random() < 0.64:
            return
        if source and getattr(source, "blur_t", 0) > 0 and random.random() < 0.5:
            return
        if getattr(self, "blind_t", 0) > 0 and random.random() < 0.6:
            return
        if source and getattr(source, "blind_t", 0) > 0 and random.random() < 0.6:
            return
        if self.intercept:
            self.intercept = False
            return
        if self.riposte_t > 0 and melee:
            self.riposte_t = 0
            if source and source.alive:
                source.bleed = min(8, source.bleed + 2)
                source.bleed_tick = 1.0
                source.hp -= L_DMG[4]
                if source.hp <= 0:
                    source.hp = 0
                    source.alive = False
            return
        blocked = False
        if getattr(self, "bonetti_t", 0) > 0 and not unblockable and (melee or projectile) and random.random() < 0.75:
            if melee and source:
                self.energy = min(self.max_energy, self.energy + 5)
            self.stat_absorb = getattr(self, "stat_absorb", 0) + max(0.0, incoming if "incoming" in dir() else dmg)
            return "blocked"
        if getattr(self, "shield_regen_t", 0) > 0:
            dmg *= 0.62
        if getattr(self, "stride_t", 0) > 0 and not unblockable and random.random() < 0.5:
            self.stat_absorb = getattr(self, "stat_absorb", 0) + max(0.0, incoming if "incoming" in dir() else dmg)
            return "blocked"
        if not unblockable and self.distortion_t > 0 and random.random() < 0.75:
            blocked = True
            skills = [s[0] for s in SKILLS.get(self.cls, [])]
            ready = [s for s in skills if self.cds.get(s, 0) <= 0]
            if not ready:
                self.distortion_t = 0
            else:
                self.cds[ready[0]] = 8.0
        if not unblockable and self.deflect_t > 0 and random.random() < 0.75:
            blocked = True
        if blocked:
            self.stat_absorb = getattr(self, "stat_absorb", 0) + max(0.0, incoming if "incoming" in dir() else dmg)
            return "blocked"
        if source and getattr(source, "dark_escape_t", 0) > 0:
            source.dark_escape_t = 0
        if self.dark_escape_t > 0:
            dmg *= 0.5
        if self.extra_armor > 0:
            dmg *= 0.9
        if self.frail_armor > 0:
            dmg *= 1.4
        if getattr(self, "resilient_t", 0) > 0 and (self.has_hex() or self.has_condition()):
            dmg = max(0.0, dmg - 24)
        if getattr(self, "rod_t", 0) > 0 and source and source is not self:
            self.rod_t = 0
            bounce = min(dmg, 80)
            source.take(bounce, source=getattr(self, "rod_src", None), unblockable=True)
            self.heal(32, source=getattr(self, "rod_src", None))
            return
        if self.reversal_t > 0:
            self.reversal_t = 0
            self.heal(min(dmg, getattr(self, "reversal_cap", L_HEAL[2])), source=getattr(self, "reversal_src", None))
            return
        if getattr(self, "xinrae_t", 0) > 0 and source and source.team != self.team:
            self.xinrae_t = 0
            cap = self.max_hp * 0.05
            dmg = min(dmg, cap)
            steal = min(64, cap)
            self.heal(steal, source=getattr(self, "xinrae_src", None))
            if source and source.alive:
                source.hp = max(0, source.hp - steal)
                if source.hp <= 0:
                    source.alive = False
        if getattr(self, "sheath_t", 0) > 0:
            self.sheath_t = 0
            self.heal(min(dmg, 84), source=getattr(self, "sheath_src", None))
            return
        if getattr(self, "mirage_t", 0) > 0 and (melee or projectile) and random.random() < 0.48:
            self.stat_absorb = getattr(self, "stat_absorb", 0) + max(0.0, incoming if "incoming" in dir() else dmg)
            return "blocked"
        if getattr(self, "riposte_t", 0) > 0 and melee and source:
            self.riposte_t = 0
            source.take(80, source=self, unblockable=True)
            self.stat_absorb = getattr(self, "stat_absorb", 0) + max(0.0, incoming if "incoming" in dir() else dmg)
            return "blocked"
        if getattr(self, "shield_st_t", 0) > 0 and getattr(self, "shield_ch", 0) > 0 and (melee or projectile):
            self.shield_ch -= 1
            dmg = max(0.0, dmg - 2)
            if self.shield_ch <= 0:
                self.shield_st_t = 0
            self.stat_absorb = getattr(self, "stat_absorb", 0) + max(0.0, incoming if "incoming" in dir() else dmg)
            return "blocked"
        shout = getattr(self, "ttl_t", 0) > 0
        if getattr(self, "soldier_t", 0) > 0 and shout and random.random() < 0.75:
            self.energy = min(self.max_energy, self.energy + 1)
            self.stat_absorb = getattr(self, "stat_absorb", 0) + max(0.0, incoming if "incoming" in dir() else dmg)
            return "blocked"
        if getattr(self, "glad_t", 0) > 0 and not unblockable and random.random() < 0.75:
            if melee and source:
                source.take(35, source=self, unblockable=True)
            self.stat_absorb = getattr(self, "stat_absorb", 0) + max(0.0, incoming if "incoming" in dir() else dmg)
            return "blocked"
        if getattr(self, "dolyak_t", 0) > 0:
            dmg *= 0.72
        if getattr(self, "protect_t", 0) > 0 and self.max_hp > 0:
            dmg = min(dmg, self.max_hp * 0.10)
        if getattr(self, "aegis_t", 0) > 0:
            self.stat_absorb = getattr(self, "stat_absorb", 0) + max(0.0, incoming if "incoming" in dir() else dmg)
            return "blocked"
        if getattr(self, "hands_t", 0) > 0:
            dmg *= 0.6
        if getattr(self, "balanced_t", 0) > 0 and getattr(self, "crit_hit", False):
            dmg *= 0.75
        if getattr(self, "shroud_t", 0) > 0 and self.hp < self.max_hp * 0.5 and random.random() < 0.75:
            self.stat_absorb = getattr(self, "stat_absorb", 0) + max(0.0, incoming if "incoming" in dir() else dmg)
            return "blocked"
        if getattr(self, "feign_t", 0) > 0:
            dmg *= 0.45
        if getattr(self, "shadow_form_t", 0) > 0:
            n = sum(1 for a in ("shadow_form_t", "shroud_t", "feign_t", "stride_t", "paradox_t") if getattr(self, a, 0) > 0)
            dmg = max(0.0, dmg - 5 * max(1, n))
        if source and getattr(source, "shadow_form_t", 0) > 0:
            dmg = min(dmg, 25)
        if self.spirit_bond_t > 0 and self.spirit_bond_hits > 0 and dmg >= getattr(self, "bond_min", 10):
            self.spirit_bond_hits -= 1
            self.heal(getattr(self, "bond_heal_amt", L_HEAL[2]), source=getattr(self, "bond_heal_src", None))
        if melee and self.near_ward and random.random() < 0.5:
            return
        if self.water_armor_t > 0:
            dmg *= 0.78
        if self.block_t > 0:
            dmg *= 0.25
        if self.shield > 0:
            absorb = min(self.shield, dmg)
            self.shield -= absorb
            dmg -= absorb
        popped = self.soulmend_t > 0
        if getattr(self, "augury_t", 0) > 0 and self.hp >= self.max_hp * 0.5 and self.hp - dmg < self.max_hp * 0.5:
            if not self.base_max:
                self.base_max = self.max_hp
            self.deepwound_t = 17
            self.max_hp = max(1.0, (self.base_max or self.max_hp or 480) * 0.8)
            self.hp = min(self.hp, self.max_hp)
            src = self.augury_src
            if src and src.alive:
                src.x, src.y = self.x + 12, self.y
                self.augury_t = 0
        if getattr(self, "watchful_t", 0) > 0 and self.max_hp > 0:
            if self.hp >= self.max_hp * 0.25 and self.hp - dmg < self.max_hp * 0.25:
                src = getattr(self, "watchful_src", None)
                self.heal(170, source=src)
                self.watchful_t = 0
                if src and getattr(src, "alive", False):
                    self._watch_wisp = (src.x, src.y)
        mitigated = max(0.0, incoming - max(0.0, dmg))
        if mitigated > 0:
            self.stat_absorb = getattr(self, "stat_absorb", 0) + mitigated
        self.hp -= dmg
        if dmg > 0:
            self.hurt_t = 3.0
            self.stat_taken = getattr(self, "stat_taken", 0) + dmg
            log = getattr(self, "dmg_log", None)
            if log is None:
                self.dmg_log = log = []
            log.append(2.0)
            hits_to_die = {"Archer": 1, "Bird": 3, "Cat": 3, "Spider": 4, "Wolf": 4, "Knight": 3, "Bear": 5, "Pup": 3}
            if self.cls in hits_to_die:
                self.hit_n = getattr(self, "hit_n", 0) + 1
                if self.hit_n >= hits_to_die[self.cls]:
                    self.hp = 0
            elif getattr(self, "spirit_kind", "") == "Life" or self.cls == "Life":
                self.hit_n = getattr(self, "hit_n", 0) + 1
                if self.hit_n >= 4:
                    self.hp = 0
            if source:
                if getattr(source, "haste_sh_t", 0) > 0:
                    source.haste_sh_t = 0
                if getattr(source, "fallback_t", 0) > 0:
                    source.fallback_t = 0
                if getattr(source, "breeze_t", 0) > 0:
                    source.breeze_t = 0
                source.dealt_t = 3.0
                source.stat_dmg = getattr(source, "stat_dmg", 0) + dmg
                vs = getattr(source, "live_vic_src", None)
                if vs and getattr(vs, "alive", False):
                    vs.heal(12, source=vs)
                own = getattr(source, "owner_ref", None)
                if own is not None and own is not source:
                    own.stat_dmg = getattr(own, "stat_dmg", 0) + dmg
                hits = getattr(self, "hitters", None)
                if hits is None:
                    hits = {}
                    self.hitters = hits
                hits[id(source)] = 2.0
                if len(hits) >= 3 and getattr(self, "flee_t", 0) <= 0 and not getattr(self, "flee_wait", False):
                    if self.channel:
                        if random.choice((1, 2)) == 1:
                            self.channel = ""
                            self.pending_cast = None
                            self.channel_target = None
                            self.channel_t = 0
                            self.flee_t = 2.0
                        else:
                            self.flee_wait = True
                    else:
                        self.flee_t = 2.0
        if getattr(self, "bond_src", None) and getattr(self.bond_src, "alive", False) and getattr(self.bond_src, "lifebond_t", 0) > 0 and (melee or projectile):
            half = dmg * 0.5
            dmg = half
            self.bond_src.take(max(0.0, half - 28), source=source)
        if getattr(self, "spirit_src", None) and getattr(self.spirit_src, "balth_spirit_t", 0) > 0 and dmg > 0:
            self.energy = min(self.max_energy, self.energy + 2)
            if self.cls == "Balthazar":
                self.slicer_ch = min(6, self.slicer_ch + 1)
        if source and dmg > 0:
            source.landed = True
        if source and source.cls == "Balthazar" and dmg > 0:
            gain = 1.25 if source.avatar_t > 0 else 1.0
            source.energy = min(source.max_energy, source.energy + gain)
            if source.grasp_t > 0 and self.was_moving and source.grasp_n < 2:
                self.slow_t = max(self.slow_t, 7.0)
                source.grasp_n += 1
                if source.grasp_n >= 2:
                    source.grasp_t = 0
        if popped and self.hp > 0:
            self.soulmend_t = 0
            self.heal(18)
        if self.hauntbrand_t > 0 and source and source.team != self.team and source.alive:
            source.heal(dmg * 0.25)
        if self.hp <= 0:
            if self.spirit_form_t > 0:
                self.hp = 1
                return
            self.hp = 0
            self.alive = False
            if source:
                source.stat_kills = getattr(source, "stat_kills", 0) + 1
                own = getattr(source, "owner_ref", None)
                if own is not None and own is not source:
                    own.stat_kills = getattr(own, "stat_kills", 0) + 1

    def move_dir(self):
        if self.fear_wander and self.fear_t > 0:
            return self.fear_dir
        if self.fear_t > 0 and self.target:
            return -self.target[0], -self.target[1]
        if self.target:
            return self.target
        return math.cos(self.facing), math.sin(self.facing)


class ClassAI:
    """Per-class stat setup and combat AI, mixed into Match."""

    def _stats(self, f):
        if f.cls in CLASS_DEFS:
            f.speed = CLASS_DEFS[f.cls].get("speed", 85)
        elif f.cls == "Mage":
            f.speed = 88
        elif f.cls == "Lingwah":
            f.speed = 90
        elif f.cls == "Rogue":
            f.speed = 110
            f.stealth_t = 999
        elif f.cls == "Priest":
            f.speed = 86
        elif f.cls == "Warlock":
            f.speed = 84
        elif f.cls == "Dark Cultist":
            f.speed = 86
        elif f.cls == "Infernal":
            f.speed = 55
            f.infernal = True
        elif f.cls == "Thumper":
            f.speed = 82
        elif f.cls == "Bellringer":
            f.speed = 86
        elif f.cls == "Trident":
            f.speed = 88
        elif f.cls == "Spiritualist":
            f.speed = 90
        elif f.cls == "Zealous":
            f.speed = 92
        elif f.cls == "Ether":
            f.speed = 90
        elif f.cls == "Expeller":
            f.speed = 88
        elif f.cls == "Bonder":
            f.speed = 89
        elif f.cls in ("Life", "Recovery"):
            f.speed = 0
            f.is_spirit = True
        elif f.cls == "Slasher":
            f.speed = 100
        elif f.cls == "Seeping":
            f.speed = 94
        elif f.cls == "Ranger":
            f.speed = 96
        elif f.cls == "Elementalist":
            f.speed = 86
        elif f.cls == "Double Dragon":
            f.speed = 80
        elif f.cls == "Stoning":
            f.speed = 87
        elif f.cls == "Balthazar":
            f.speed = 92
        elif f.cls == "Deathdancer":
            f.speed = 100
        elif f.cls == "Mesmer":
            f.speed = 88
        elif f.cls == "Escaper":
            f.speed = 96
        elif f.cls == "Glimmer":
            f.speed = 90
        elif f.cls == "Deadsword":
            f.speed = 96
        elif f.cls == "Migraine":
            f.speed = 92
        elif f.cls == "Surger":
            f.speed = 90
            f.max_energy = 60
        elif f.cls == "Lifesheath":
            f.speed = 92
        elif f.cls == "PermaShadow":
            f.speed = 98
        elif f.cls == "Riposte":
            f.speed = 88
        elif f.cls == "AirEnchant":
            f.speed = 90
        elif f.cls == "Judge":
            f.speed = 90
        elif f.cls == "Conditioner":
            f.speed = 90
        elif f.cls == "Beast Master":
            f.speed = 88
        elif f.cls == "Chimp":
            f.speed = 100
            f.is_pet = True
        elif f.cls == "Boa":
            f.speed = 92
            f.is_pet = True
        elif f.cls == "Bear":
            f.speed = 70
            f.is_pet = True
        elif f.cls == "Bird":
            f.speed = 130
            f.is_pet = True
        elif f.cls == "Cat":
            f.speed = 125
            f.is_pet = True
        elif f.cls == "Wolf":
            f.speed = 115
            f.is_pet = True
        elif f.cls == "Spider":
            f.speed = 110
            f.is_pet = True
        elif f.cls == "Pup":
            f.speed = 140
            f.is_pet = True
            f.attacks_left = 2
        elif f.cls == "Knight":
            f.speed = 80
            f.is_pet = True
        elif f.cls == "Archer":
            f.speed = 95
            f.is_pet = True
        else:
            f.speed = 85
        if f.cls in ("Life", "Recovery"):
            f.max_hp = f.hp = 456
            f.is_spirit = True
            f.spirit_kind = f.cls
        elif f.cls in TANK_PICKS:
            f.max_hp = f.hp = 508
        elif f.cls in CLASSES:
            f.max_hp = f.hp = 480
        elif f.cls == "Infernal":
            f.max_hp = f.hp = 960
        elif f.cls == "Bear":
            f.max_hp = f.hp = 720
        elif f.cls == "Knight":
            f.max_hp = f.hp = 360
        elif f.cls in ("Wolf", "Cat"):
            f.max_hp = f.hp = 400
        elif f.cls in ("Chimp", "Boa"):
            f.max_hp = f.hp = 400
        elif f.cls == "Pup":
            f.max_hp = f.hp = 160
        else:
            f.max_hp = f.hp = 320
        f.base_max = f.max_hp
        if f.cls == "Balthazar":
            f.max_energy = 12
        elif f.cls == "Surger":
            f.max_energy = 60
        elif f.cls in CASTER_ENERGY:
            f.max_energy = 30
        elif f.cls in MARTIAL_ENERGY:
            f.max_energy = 25
        else:
            f.max_energy = 20
        f.energy = f.max_energy

    def run_defined_class(self, u, dt):
        """Generic AI for any class declared in CLASS_DEFS (see classes.py).

        Executes each skill by looking up its SKILL_DEFS behavior tag, so a new
        class needs no hand-written branch here. Returns True if it handled the
        unit (always, for a defined class).
        """
        cdef = CLASS_DEFS.get(u.cls)
        if not cdef:
            return False
        e = self.nearest(u)
        dist = math.hypot(e.x - u.x, e.y - u.y) if e else 999
        pets = [un for un in self.units if un.owner_name == u.name and un.is_pet]
        live = [p for p in pets if p.alive]
        pet = live[0] if live else None

        for name, _, _ in SKILLS.get(u.cls, []):
            d = SKILL_DEFS.get(name)
            if not d or not u.ready(name):
                continue
            ai = d.get("ai")
            cd = d.get("cd", 5.0)

            if ai == "pet_heal":
                if pet and pet.hp < pet.max_hp * 0.55:
                    u.use(name, cd)
                    sfx("heal")
                    u.channel = "beast_comfort"
                    u.channel_t = u.channel_max = 1.0
                    u.channel_target = pet
                    return True
                if not live and pets:
                    u.use(name, cd)
                    sfx("heal")
                    u.channel = "beast_comfort"
                    u.channel_t = u.channel_max = 1.0
                    u.channel_target = pets[0]
                    return True
                continue

            if ai == "pet_buff":
                if not pet:
                    continue
                kind = d.get("kind")
                if kind == "dr" and pet.pet_dr_t <= 0:
                    u.use(name, cd)
                    sfx("ward")
                    pet.pet_dr_t = d.get("duration", 120)
                    self.emit(pet.x, pet.y, (120, 180, 120), 16, 40, 4, 0.4)
                    return True
                if kind == "feral" and pet.pet_feral_t <= 0:
                    u.use(name, cd)
                    sfx("howl")
                    pet.pet_feral_t = d.get("duration", 21)
                    pet.pet_feral_bonus = d.get("bonus", 10)
                    self.emit(pet.x, pet.y, (200, 120, 60), 18, 60, 4, 0.45)
                    return True
                continue

            if ai == "pet_attack":
                if not (pet and e):
                    continue
                u.use(name, cd)
                pet.facing = math.atan2(e.y - pet.y, e.x - pet.x)
                on_hit = d.get("on_hit")

                def _pa(pet=pet, u=u, d=d, on_hit=on_hit):
                    def _hit(tgt, pet=pet, u=u, d=d, on_hit=on_hit):
                        if on_hit == "heal_pet":
                            pet.heal(d.get("on_hit_heal", 53), source=pet)
                        elif on_hit == "brutal":
                            if tgt.hp < tgt.max_hp * 0.5:
                                tgt.take(37, source=pet)
                                pet.pet_brutal_stacks = min(4, pet.pet_brutal_stacks + 1)
                                pet.pet_brutal_t = 30
                                if not pet.base_max:
                                    pet.base_max = pet.max_hp
                                pet.max_hp = pet.base_max * (1 + 0.25 * pet.pet_brutal_stacks)
                                pet.hp = min(pet.max_hp, pet.hp + pet.base_max * 0.25)
                                self.burst(pet.x, pet.y, (200, 80, 40), 44, 0.35)
                        elif on_hit == "energy_on_condition":
                            if tgt.has_condition():
                                u.energy = min(u.max_energy, u.energy + d.get("on_hit_energy", 16))
                                self.emit(u.x, u.y, (120, 220, 140), 12, 40, 3, 0.35)
                    self.fire(pet, d.get("kind", "maul"), L_DMG[1] + d.get("dmg", 37), 320, 1.0, on_hit=_hit)
                self.start_cast(u, 2, _pa, cast=d.get("cast", 0.5))
                return True

            if ai == "ally_enchant":
                reach = d.get("range", 260)
                mates = [a for a in self.living(u.team) if a is not u
                         and not getattr(a, "is_spirit", False)
                         and getattr(a, "gdw_t", 0) <= 0
                         and math.hypot(a.x - u.x, a.y - u.y) <= reach]
                if not mates:
                    continue
                ally = min(mates, key=lambda a: (a.x - u.x) ** 2 + (a.y - u.y) ** 2)
                u.use(name, cd)

                def _g(ally=ally, u=u, d=d):
                    ally.gdw_t = d.get("duration", 20)
                    ally.gdw_src = u
                    self.emit(ally.x, ally.y, (210, 180, 90), 16, 50, 4, 0.4)
                    self.burst(ally.x, ally.y, GOLD, 34, 0.3)
                self.start_cast(u, 2, _g, cast=d.get("cast", 1.0))
                return True

            if ai == "shout":
                if not (pet and e):
                    continue
                u.use(name, cd)
                sfx("shout")
                pet.x, pet.y = e.x + random.uniform(-14, 14), e.y + random.uniform(-14, 14)
                self.clamp(pet)
                pet.strike_as_one_t = d.get("duration", 16)
                pet.strike_as_one_src = u
                u.strike_as_one_t = d.get("duration", 16)
                u.strike_as_one_src = u
                self.emit(e.x, e.y, (200, 60, 60), 18, 70, 4, 0.4)
                return True

            if ai == "heal":
                ally = self.neediest(u, d.get("range", 200))
                if not ally:
                    continue
                u.use(name, cd)

                def _h(ally=ally, u=u, d=d):
                    ally.heal(d.get("heal", 92), source=u)
                self.start_cast(u, 2, _h, cast=d.get("cast", 1.0))
                return True

            if ai == "projectile":
                if not e:
                    continue
                u.use(name, cd)
                u.facing = math.atan2(e.y - u.y, e.x - u.x)

                def _fire(u=u, d=d):
                    self.fire(u, d.get("kind", "bolt"), d.get("dmg", 42), 320, 1.1)
                self.start_cast(u, 2, _fire, cast=d.get("cast", 0.55))
                return True

            if ai == "melee":
                if not (e and dist < 52):
                    continue
                u.use(name, cd)
                e.take(d.get("dmg", 42), melee=True, source=u)
                return True

            if ai == "hex":
                if not e:
                    continue
                u.use(name, cd)
                e.curse_t = max(e.curse_t, d.get("duration", 8))
                self.emit(e.x, e.y, (150, 60, 200), 14, 50, 4, 0.4)
                return True

            if ai == "aoe":
                if not e:
                    continue
                u.use(name, cd)
                radius = 40 * max(1, d.get("aoe", 3))

                def _a(u=u, e=e, d=d, radius=radius):
                    self.burst(e.x, e.y, FIRE, radius, 0.4)
                    for o in self.living(1 - u.team):
                        if math.hypot(o.x - e.x, o.y - e.y) < radius:
                            o.take(d.get("dmg", 60), source=u)
                self.start_cast(u, 2, _a, cast=d.get("cast", 1.0))
                return True
        return True

    def ai(self, u, dt):
        self.acting = u
        e = self.nearest(u)
        if u.cls in HEAL_PICKS and self.healer_swing(u, e):
            return
        if u.cls in CLASS_DEFS:
            self.run_defined_class(u, dt)
            return
        if u.cls in HEAL_PICKS:
            ally = self.neediest(u, 180)
            if ally:
                dx, dy = ally.x - u.x, ally.y - u.y
                dist = math.hypot(dx, dy) or 1
                u.target = (dx / dist, dy / dist)
                if u.fear_t <= 0:
                    u.facing = math.atan2(dy, dx)
                self.notice_hex(u, ally, 180)
            elif u.cls != "Bellringer":
                return
        if u.cls == "Priest":
            ally = self.neediest(u)
            if ally:
                dx, dy = ally.x - u.x, ally.y - u.y
                dist = math.hypot(dx, dy) or 1
                u.target = (dx / dist, dy / dist)
                if u.fear_t <= 0:
                    u.facing = math.atan2(dy, dx)
                if e:
                    ex, ey = e.x - u.x, e.y - u.y
                    ed = math.hypot(ex, ey) or 1
                    if ed < (70 if u.hp >= u.max_hp - 25 else 110):
                        u.target = (-ex / ed, -ey / ed)
                ratio = ally.hp / ally.max_hp if ally.max_hp else 1
                if ratio <= 0.32 and u.ready("Life Grip") and ally is not u:
                    u.use("Life Grip", 14)
                    sfx("grip")
                    self.tethers.append(Tether(u, ally, 0.7))
                    self.emit(ally.x, ally.y, HOLY2, 16, 90, 4, 0.4)
                    ally.x += (u.x - ally.x) * 0.72
                    ally.y += (u.y - ally.y) * 0.72
                    self.clamp(ally)
                    self.burst(u.x, u.y, HOLY, 36, 0.35)
                    return
                if ratio < 0.55 and ally.shield <= 0 and u.ready("Barrier"):
                    u.use("Barrier", 10)
                    sfx("barrier")
                    ally.shield = L_HEAL[3]
                    self.burst(ally.x, ally.y, HOLY2, 46, 0.4)
                    self.emit(ally.x, ally.y, HOLY, 18, 40, 5, 0.6)
                    return
                if ally.favor_t <= 0 and u.ready("Healing Favor") and ratio < 0.85:
                    u.use("Healing Favor", 12)
                    sfx("favor")
                    ally.favor_t = 8.0
                    ally.favor_tick = 2.0
                    return
                if ratio < 0.4 and u.ready("Fat Heal"):
                    u.use("Fat Heal", 9)
                    sfx("heal")
                    self.heals.append(DelayedHeal(ally, L_HEAL[5], 3.0 + L_CAST[5], "fat"))
                    return
                if ratio < 0.65 and u.ready("Thiq Heal"):
                    u.use("Thiq Heal", 6)
                    sfx("heal")
                    self.heals.append(DelayedHeal(ally, L_HEAL[3], 2.0 + L_CAST[3], "thiq"))
                    return
                if ratio < 0.9 and u.ready("Qwik Heal"):
                    u.use("Qwik Heal", 4)
                    sfx("heal")
                    self.heals.append(DelayedHeal(ally, L_HEAL[2], 1.5 + L_CAST[2], "qwik"))
                    return
            return

        elif u.cls == "Lingwah":
            reach = AUTO_RANGE["caster"]
            ally = self.neediest(u, 220) or u
            e = self.nearest(u)
            ad = math.hypot(ally.x - u.x, ally.y - u.y)
            dist = math.hypot(e.x - u.x, e.y - u.y) if e else 9999
            
            # --- PREBUFFS FIRST ---
            if getattr(u, "ashes_t", 0) <= 0 and u.ready("Anguished Was Lingwah") and self.time > 4:
                u.use("Anguished Was Lingwah", 30)
                def _ash(u=u):
                    u.ashes_t = 47
                    self.emit(u.x, u.y, (90, 60, 40), 14, 30, 3, 0.4)
                    sfx("Anguished Was Lingwah", 0.1)
                self.start_cast(u, 1, _ash, cast=2.0)
                return

            if getattr(u, "glyph_charges", 0) <= 0 and u.ready("Glyph of Lesser Energy"):
                u.use("Glyph of Lesser Energy", 30)
                def _gl(u=u):
                    u.glyph_charges = 2
                    u.glyph_t = 15
                    self.emit(u.x, u.y, (255, 230, 90), 12, 40, 3, 0.4)
                self.start_cast(u, 1, _gl, cast=1.0)
                return

            # --- BLOODSONG SPIRIT ---
            if not any(getattr(s, "spirit_kind", "") == "Bloodsong" and s.alive for s in self.living(u.team)) and u.ready("Bloodsong Spirit"):
                u.use("Bloodsong Spirit", 20)
                self.start_cast(u, 2, lambda u=u: self.spawn_bloodsong(u), cast=1.5)
                return

            # --- RESILIENT WEAPON (only if ally has hex OR condition) ---
            hex_or_cond = ally is not u and (ally.has_hex() or ally.has_condition())
            if hex_or_cond and getattr(ally, "resilient_t", 0) <= 0 and u.ready("Resilient Weapon") and ad <= reach:
                u.use("Resilient Weapon", 6)
                def _rw(u=u, ally=ally):
                    ally.resilient_t = self.apply_ench_dur(u, 14)
                    self.emit(ally.x, ally.y, (60, 200, 120), 14, 40, 4, 0.4)
                    self.burst(ally.x, ally.y, (80, 220, 140), 30, 0.3)
                    sfx("Resilient Weapon", 0.1)
                self.start_cast(u, 1, _rw, cast=1.0)
                return

            # --- WIELDERS BOON (only if ally has enchantment) ---
            if ally is not u and ally.has_enchantment() and ally.hp < ally.max_hp * 0.85 and u.ready("Wielders Boon") and ad <= reach:
                u.use("Wielders Boon", 4)
                def _wb(u=u, ally=ally):
                    amt = 48 + (59 if ally.has_enchantment() else 0)
                    ally.heal(amt, source=u)
                    self.emit(ally.x, ally.y, (100, 220, 255), 12, 40, 3, 0.35)
                self.start_cast(u, 1, _wb, cast=0.25)
                return

            # --- XINRAE'S WEAPON (your exact version) ---
            if getattr(ally, "xinrae_t", 0) <= 0 and u.ready("Xinraes Weapon") and ad <= reach:
                u.use("Xinraes Weapon", 3)
                def _xw(u=u, ally=ally):
                    ally.xinrae_t = self.apply_ench_dur(u, 12)
                    ally.xinrae_src = u
                    self.emit(ally.x, ally.y, (80, 140, 255), 16, 50, 4, 0.4)
                    self.burst(ally.x, ally.y, (60, 120, 255), 34, 0.3)
                    sfx("holy", 0.1)
                self.start_cast(u, 1, _xw, cast=0.25)
                return

            # --- RENEWING SURGE ---
            if e and getattr(e, "renew_surge_t", 0) <= 0 and u.ready("Renewing Surge Hex") and dist < 320:
                u.use("Renewing Surge Hex", 15)
                def _rs(u=u, e=e):
                    dur = 8 * (1.33 if u.ashes_t > 0 else 1.0)
                    e.renew_surge_t = dur
                    e.renew_surge_tick = 1.0
                    e.renew_surge_src = u
                    self.emit(e.x, e.y, (70, 200, 90), 12, 40, 3, 0.35)
                self.start_cast(u, 1, _rs, cast=1.0)
                return

            # --- LAMENTATION HEX ---
            if e and getattr(e, "lament_t", 0) <= 0 and u.ready("Lamentation Hex") and dist < 320:
                u.use("Lamentation Hex", 15)
                def _lam(u=u, e=e):
                    near_spirit_or_corpse = any(
                        ((getattr(s, "is_spirit", False) and s.alive) or (not s.alive and not s.is_pet and not getattr(s, "is_spirit", False)))
                        and math.hypot(s.x - e.x, s.y - e.y) < 200
                        for s in self.units
                    )
                    dur = 18 * (1.33 if u.ashes_t > 0 else 1.0)
                    for o in self.living(1 - u.team):
                        if o is e or math.hypot(o.x - e.x, o.y - e.y) < 100:
                            o.lament_t = dur
                            o.lament_tick = 1.0
                            if near_spirit_or_corpse:
                                o.take(45, source=u)
                    self.burst(e.x, e.y, (60, 180, 100), 60, 0.4)
                    self.emit(e.x, e.y, (90, 220, 140), 16, 60, 4, 0.4)
                    sfx("Lamentation Hex", 0.1)
                self.start_cast(u, 2, _lam, cast=1.0)
                return

            # --- AUTO ATTACK (only when enemy exists + in range) ---
            if e and dist < reach and u.ready("auto"):
                self.fire(u, "verdant", L_DMG[1], 320, 1.1)
                u.use("auto", 1.15)


        if u.cls == "Spiritualist":
            ally = self.neediest(u)
            fallen = [a for a in self.units if a.team == u.team and not a.alive and not a.is_pet and not getattr(a, "is_spirit", False) and a.cls not in PET_KINDS]
            if fallen and u.ready("Last Rite"):
                t = fallen[0]
                u.use("Last Rite", 20)
                u.last_cast = "Last Rite"
                sfx("spirit")
                t.alive = True
                t.hp = t.max_hp * 0.28
                t.spirit_form_t = 5.0
                self.burst(t.x, t.y, SPIRIT, 50, 0.5)
                self.emit(t.x, t.y, WHITE, 22, 70, 5, 0.55)
                return
            if ally:
                dx, dy = ally.x - u.x, ally.y - u.y
                dist = math.hypot(dx, dy) or 1
                u.target = (dx / dist, dy / dist)
                if u.fear_t <= 0:
                    u.facing = math.atan2(dy, dx)
                if e:
                    ex, ey = e.x - u.x, e.y - u.y
                    ed = math.hypot(ex, ey) or 1
                    if ed < (70 if u.hp >= u.max_hp - 25 else 110):
                        u.target = (-ex / ed, -ey / ed)
                ratio = ally.hp / ally.max_hp if ally.max_hp else 1
                if u.ready("Echo Step") and e and math.hypot(e.x - u.x, e.y - u.y) < 90:
                    u.use("Echo Step", 9)
                    sfx("blink")
                    ox, oy = u.x, u.y
                    u.x -= math.cos(u.facing) * 90
                    u.y -= math.sin(u.facing) * 90
                    self.clamp(u)
                    self.echoes.append([ox, oy, u.team, 1.0, u.last_cast or "Soulmend", u])
                    self.emit(ox, oy, SPIRIT, 16, 50, 4, 0.4)
                    return
                if ratio < 0.55 and u.ready("Soulmend"):
                    u.use("Soulmend", 4)
                    u.last_cast = "Soulmend"
                    sfx("spirit")
                    self.apply_heal(ally, L_HEAL[3], "soul")
                    ally.soulmend_t = 2.0
                    self.tethers.append(Tether(u, ally, 2.0))
                    return
                if not ally.intercept and u.ready("Warding Apparition"):
                    u.use("Warding Apparition", 10)
                    u.last_cast = "Warding Apparition"
                    sfx("barrier")
                    ally.intercept = True
                    self.burst(ally.x, ally.y, SPIRIT, 40, 0.4)
                    return
                condi = ally.slow_t > 0 or ally.stun_t > 0 or ally.bleed > 0 or ally.knockdown_t > 0
                hexed = bool(self.unit_hexes(ally))
                if (condi or (hexed and self.can_cleanse_hex(u, ally, 160))) and u.ready("Gravewind Purge"):
                    u.use("Gravewind Purge", 8)
                    u.last_cast = "Gravewind Purge"
                    sfx("purge")
                    for attr in ("slow_t", "freeze_t", "stun_t", "fear_t", "curse_t", "antiheal_t", "blur_t", "knockdown_t", "daze_t", "water_hex_t"):
                        setattr(ally, attr, 0.0)
                    ally.bleed = 0
                    self.apply_heal(ally, L_HEAL[1], "purge")
                    return
                if u.ready("Spirit Well"):
                    u.use("Spirit Well", 16)
                    u.last_cast = "Spirit Well"
                    sfx("ward")
                    self.wells.append([u.x, u.y, u.team, 12.0])
                    self.burst(u.x, u.y, SPIRIT, 80, 0.45)
                    return
            if e:
                if e.hauntbrand_t <= 0 and u.ready("Hauntbrand"):
                    u.use("Hauntbrand", 12)
                    u.last_cast = "Hauntbrand"
                    sfx("curse")
                    e.hauntbrand_t = 10.0
                    self.burst(e.x, e.y, SPIRIT, 30, 0.35)
                    return
                if u.ready("Ancestors Grasp") and math.hypot(e.x - u.x, e.y - u.y) < 120:
                    u.use("Ancestors Grasp", 7)
                    u.last_cast = "Ancestors Grasp"
                    sfx("grip")
                    self.burst(e.x, e.y, SPIRIT, 70, 0.4)
                    self.emit(e.x, e.y, WHITE, 18, 40, 4, 0.5)
                    for o in self.living(1 - u.team):
                        if math.hypot(o.x - e.x, o.y - e.y) < 70:
                            o.slow_t = max(o.slow_t, 2.8)
                            o.take(L_DMG[1], source=u)
                    return
            return

        if u.cls == "Zealous":
            ally = self.neediest(u)
            if u.dark_escape_t <= 0 and u.hp / u.max_hp < 0.45 and u.ready("Dark Escape"):
                u.use("Dark Escape", 14)
                sfx("shadow")
                u.dark_escape_t = 9.0
                self.emit(u.x, u.y, SHADOW, 20, 60, 4, 0.5)
            if ally:
                dx, dy = ally.x - u.x, ally.y - u.y
                dist = math.hypot(dx, dy) or 1
                u.target = (dx / dist, dy / dist)
                if u.fear_t <= 0:
                    u.facing = math.atan2(dy, dx)
                if e and math.hypot(e.x - u.x, e.y - u.y) < (70 if u.hp >= u.max_hp - 25 else 110):
                    ex, ey = e.x - u.x, e.y - u.y
                    ed = math.hypot(ex, ey) or 1
                    u.target = (-ex / ed, -ey / ed)
                ratio = ally.hp / ally.max_hp
                enchanted = ally.reversal_t > 0 or ally.spirit_bond_t > 0 or ally.holy_veil_t > 0 or ally.favor_t > 0 or ally.shield > 0 or ally.water_armor_t > 0
                condi = [a for a in ("slow_t", "stun_t", "curse_t", "bleed", "blur_t", "antiheal_t", "knockdown_t", "daze_t") if getattr(ally, a, 0) > 0]
                if condi and u.ready("Dismiss Condition"):
                    u.use("Dismiss Condition", 5)
                    sfx("purge")
                    attr = condi[0]
                    if attr == "bleed":
                        ally.bleed = 0
                    else:
                        setattr(ally, attr, 0.0)
                    if enchanted:
                        self.apply_heal(ally, L_HEAL[2])
                    self.emit(ally.x, ally.y, MANA, 12, 40, 4, 0.35)
                    return
                if ratio < 0.5 and u.ready("Zealous Bene"):
                    u.use("Zealous Bene", 8)
                    sfx("holy")
                    amt = L_HEAL[5]
                    self.apply_heal(ally, amt)
                    self.emit(ally.x, ally.y, WHITE, 20, 70, 5, 0.45)
                    others = [a for a in self.living(u.team) if a is not ally and not a.is_pet]
                    if others:
                        self.apply_heal(min(others, key=lambda a: a.hp / a.max_hp), amt * 0.15)
                    return
                if ratio < 0.62 and u.ready("Signet of Devotion"):
                    u.use("Signet of Devotion", 10)
                    sfx("holy")
                    self.apply_heal(ally, L_HEAL[4])
                    self.emit(ally.x, ally.y, MANA, 16, 50, 4, 0.4)
                    return
                if ally.reversal_t <= 0 and u.ready("Reversal of Fortune"):
                    u.use("Reversal of Fortune", 6)
                    sfx("holy")
                    ally.reversal_t = 8; ally.reversal_src = u
                    self.apply_heal(ally, L_HEAL[1])
                    self.burst(ally.x, ally.y, MANA, 34, 0.35)
                    return
                if ally.spirit_bond_t <= 0 and ratio < 0.8 and u.ready("Spirit Bond"):
                    u.use("Spirit Bond", 12)
                    sfx("holy")
                    ally.spirit_bond_t = 8.0
                    ally.spirit_bond_hits = 10
                    self.burst(ally.x, ally.y, WHITE, 40, 0.35)
                    return
                if ally.holy_veil_t <= 0 and u.ready("Holy Veil"):
                    u.use("Holy Veil", 10)
                    sfx("holy")
                    ally.holy_veil_t = 10.0
                    self.emit(ally.x, ally.y, MANA, 10, 30, 3, 0.4)
                    return
                if ratio < 0.7 and dist > 80 and u.ready("Return"):
                    u.use("Return", 12)
                    sfx("shadow")
                    self.emit(u.x, u.y, SHADOW, 18, 70, 4, 0.4)
                    for o in self.living(1 - u.team):
                        if math.hypot(o.x - u.x, o.y - u.y) < 70:
                            o.slow_t = max(o.slow_t, 5.0)
                    u.x, u.y = ally.x + 12, ally.y
                    self.clamp(u)
                    self.emit(u.x, u.y, SHADOW, 18, 70, 4, 0.4)
                    return
            return

        if u.cls == "Ether":
            ally = self.neediest(u, 165) or u
            ad = math.hypot(ally.x - u.x, ally.y - u.y)
            if ally is not u:
                dx, dy = ally.x - u.x, ally.y - u.y
                dist = math.hypot(dx, dy) or 1
                u.target = (dx / dist, dy / dist)
                if u.fear_t <= 0:
                    u.facing = math.atan2(dy, dx)
            if e and math.hypot(e.x - u.x, e.y - u.y) < 160:
                ex, ey = e.x - u.x, e.y - u.y
                ed = math.hypot(ex, ey) or 1
                u.target = (-ex / ed, -ey / ed)
            if self.try_rez(u) if hasattr(self, "try_rez") else False:
                return
            fallen = [a for a in self.units if a.team == u.team and not a.alive and not a.is_pet and not getattr(a, "is_spirit", False)]
            if fallen and u.rez_ready and u.ready("Resurrection Signet"):
                u.use("Resurrection Signet", 99)
                u.rez_ready = False
                u.enemy_deaths_at_rez = self.morale[1 - u.team]
                u.channel, u.channel_t, u.channel_target = "rez_sig", 2.2, fallen[0]
                return
            if u.aura_restore_t <= 0 and u.ready("Aura of Restoration"):
                u.use("Aura of Restoration", 20)
                u.aura_restore_t = 60
                self.emit(u.x, u.y, MANA, 12, 30, 3, 0.4)
                return
            if u.ether_renew_t <= 0 and u.ready("Ether Renewal"):
                u.use("Ether Renewal", 30)
                u.ether_renew_t = 20
                self.emit(u.x, u.y, (120, 180, 255), 14, 40, 3, 0.4)
                return
            if u.zealot_fire_t <= 0 and u.ready("Zealots Fire"):
                u.use("Zealots Fire", 30)
                u.zealot_fire_t = 60
                return
            hexes = ("curse_t", "antiheal_t", "blur_t", "water_hex_t", "hauntbrand_t", "seeping_t", "ash_t", "weakness_t")
            if self.can_cleanse_hex(u, ally, 155) and u.ready("Smite Hex"):
                u.use("Smite Hex", 12)
                sfx("holy")
                for h in hexes:
                    if getattr(ally, h, 0) > 0:
                        setattr(ally, h, 0.0)
                        for o in self.living(1 - u.team):
                            if math.hypot(o.x - ally.x, o.y - ally.y) < 90:
                                o.take(60, source=u)
                        self.burst(ally.x, ally.y, HOLY, 70, 0.4)
                        break
                self._zealot_orbs(u, ally)
                return
            condi = [a for a in ("slow_t", "stun_t", "curse_t", "bleed", "blur_t", "antiheal_t", "knockdown_t", "daze_t", "fear_t", "burn_t") if getattr(ally, a, 0) > 0]
            if ally is not u and condi and u.ready("Draw Conditions") and ad < 155:
                u.use("Draw Conditions", 4)
                n = 0
                for attr in condi:
                    if attr == "bleed":
                        n += 1
                        u.bleed = min(8, u.bleed + ally.bleed)
                        ally.bleed = 0
                    else:
                        n += 1
                        setattr(u, attr, max(getattr(u, attr, 0), getattr(ally, attr, 0)))
                        setattr(ally, attr, 0.0)
                u.heal(19 * n, source=u)
                self.emit(u.x, u.y, MANA, 14, 40, 3, 0.35)
                self._zealot_orbs(u, ally)
                return
            if ally.reversal_t <= 0 and u.ready("Reversal of Fortune") and ad < 155:
                u.use("Reversal of Fortune", 2)
                ally.reversal_t = 8; ally.reversal_src = u
                ally.reversal_cap = 58
                self.apply_heal(ally, L_HEAL[1])
                self._zealot_orbs(u, ally)
                return
            if (getattr(ally, "balth_aura_t", 0) <= 0) and u.ready("Balthazars Aura") and ad < 155:
                u.use("Balthazars Aura", 20)
                ally.balth_aura_t = 8
                self._zealot_orbs(u, ally)
                return
            return

        if u.cls == "Expeller":
            ally = self.neediest(u, 165) or u
            ad = math.hypot(ally.x - u.x, ally.y - u.y)
            spirits = self.spirits_near(u, 200)
            earshot = self.spirits_near(ally, 200)
            if e and math.hypot(e.x - u.x, e.y - u.y) < 80 and u.hp < u.max_hp - 25:
                ex, ey = e.x - u.x, e.y - u.y
                ed = math.hypot(ex, ey) or 1
                u.target = (-ex / ed, -ey / ed)
            elif ally is not u:
                dx, dy = ally.x - u.x, ally.y - u.y
                d = math.hypot(dx, dy) or 1
                u.target = (dx / d, dy / d)
                if u.fear_t <= 0:
                    u.facing = math.atan2(dy, dx)
            hexes = ("curse_t", "antiheal_t", "blur_t", "water_hex_t", "hauntbrand_t", "seeping_t", "ash_t", "weakness_t")
            if u.kaolai_t > 0 and any(a.hp <= a.max_hp - 90 for a in self.living(u.team) if not getattr(a, "is_spirit", False)):
                self.drop_kaolai(u)
                return
            if not any(s.spirit_kind == "Life" and s.alive for s in self.living(u.team) if getattr(s, "is_spirit", False)) and u.ready("Life"):
                u.use("Life", 20)
                self.start_cast(u, 2, lambda u=u: self.spawn_spirit(u, "Life", 20), cast=0.75)
                return
            if not any(s.spirit_kind == "Recovery" and s.alive for s in self.living(u.team) if getattr(s, "is_spirit", False)) and u.ready("Recovery"):
                u.use("Recovery", 30)
                self.start_cast(u, 2, lambda u=u: self.spawn_spirit(u, "Recovery", 62), cast=0.75)
                return
            if u.kaolai_t <= 0 and u.ready("Protective Was Kaolai"):
                u.use("Protective Was Kaolai", 20)
                def _k(u=u):
                    u.kaolai_t = 63
                    self.emit(u.x, u.y, (70, 30, 100), 14, 30, 3, 0.4)
                self.start_cast(u, 2, _k, cast=1.0)
                return
            ratio = ally.hp / ally.max_hp
            if self.can_cleanse_hex(u, ally, 165) and u.ready("Expel Hexes"):
                u.use("Expel Hexes", 8)
                n = 0
                for h in hexes:
                    if getattr(ally, h, 0) > 0 and n < 2:
                        setattr(ally, h, 0.0)
                        n += 1
                self.emit(ally.x, ally.y, (90, 40, 120), 14, 40, 3, 0.4)
                return
            if getattr(ally, "ward_wep_t", 0) <= 0 and u.ready("Weapon of Warding") and ad < 165:
                u.use("Weapon of Warding", 5)
                ally.ward_wep_t = 12
                self.emit(ally.x, ally.y, (30, 110, 110), 12, 30, 3, 0.35)
                return
            if ratio < 0.55 and u.ready("Spirit Light") and ad < 165:
                u.use("Spirit Light", 4)
                def _sl(u=u, ally=ally):
                    if not self.spirits_near(ally, 200):
                        u.hp = max(1, u.hp - u.max_hp * 0.17)
                    ally.heal(188, source=u)
                    self.emit(ally.x, ally.y, (40, 140, 140), 16, 50, 4, 0.4)
                self.start_cast(u, 2, _sl, cast=1.0)
                return
            if ratio < 0.75 and u.ready("Mend Body and Soul") and ad < 165:
                u.use("Mend Body and Soul", 3)
                def _mb(u=u, ally=ally):
                    ally.heal(121, source=u)
                    n = len(self.spirits_near(ally, 200))
                    condi = [a for a in ("slow_t", "stun_t", "poison_t", "daze_t", "bleed", "curse_t") if getattr(ally, a, 0) > 0]
                    for attr in condi[:n]:
                        if attr == "bleed":
                            ally.bleed = 0
                        else:
                            setattr(ally, attr, 0.0)
                    self.emit(ally.x, ally.y, (80, 40, 110), 12, 40, 3, 0.35)
                self.start_cast(u, 2, _mb, cast=0.75)
                return
            if ratio < 0.9 and u.ready("Soothing Memories") and ad < 165:
                u.use("Soothing Memories", 4)
                def _sm(u=u, ally=ally):
                    ally.heal(106, source=u)
                    u.energy = min(u.max_energy, u.energy + 3)
                    self.emit(ally.x, ally.y, (30, 100, 110), 10, 30, 3, 0.35)
                self.start_cast(u, 2, _sm, cast=0.75)
                return
            return

        if u.cls == "Bonder":
            ally = self.neediest(u, 165) or u
            ad = math.hypot(ally.x - u.x, ally.y - u.y)
            if ally is not u:
                dx, dy = ally.x - u.x, ally.y - u.y
                d = math.hypot(dx, dy) or 1
                u.target = (dx / d, dy / d)
                if u.fear_t <= 0:
                    u.facing = math.atan2(dy, dx)
            enchanted = ally.reversal_t > 0 or ally.shield_regen_t > 0 or ally.favor_t > 0 or ally.ward_wep_t > 0 or ally.holy_veil_t > 0
            condi = [a for a in ("slow_t", "stun_t", "poison_t", "daze_t", "bleed", "curse_t", "knockdown_t") if getattr(ally, a, 0) > 0]
            hexes = ("curse_t", "antiheal_t", "blur_t", "water_hex_t", "seeping_t", "ash_t", "weakness_t")
            if u.bonetti_t <= 0 and e and math.hypot(e.x-u.x, e.y-u.y) < 70 and u.ready("Bonettis Defense"):
                u.use("Bonettis Defense", 12)
                u.bonetti_t = 6
                self.teal_cast(u, u)
                return
            if condi and u.ready("Dismiss Condition") and ad < 165:
                u.use("Dismiss Condition", 3)
                def _dc(u=u, ally=ally, condi=condi, enchanted=enchanted):
                    attr = condi[0]
                    if attr == "bleed":
                        ally.bleed = 0
                    else:
                        setattr(ally, attr, 0.0)
                    if enchanted:
                        ally.heal(71, source=u)
                    self.teal_cast(u, ally)
                self.start_cast(u, 2, _dc, cast=0.75)
                return
            if self.can_cleanse_hex(u, ally, 165) and u.ready("Deny Hexes"):
                u.use("Deny Hexes", 12)
                def _dh(u=u, ally=ally):
                    for h in hexes:
                        if getattr(ally, h, 0) > 0:
                            setattr(ally, h, 0.0)
                            break
                    divine = ("Reversal of Fortune", "Dismiss Condition", "Shield of Regeneration", "Deny Hexes", "Blessed Signet")
                    n = sum(1 for s in divine if u.cds.get(s, 0) > 0)
                    ally.heal(42 * max(1, n), source=u)
                    self.teal_cast(u, ally)
                self.start_cast(u, 2, _dh, cast=1.0)
                return
            if ally.reversal_t <= 0 and u.ready("Reversal of Fortune") and ad < 165:
                u.use("Reversal of Fortune", 4)
                def _rf(u=u, ally=ally):
                    ally.reversal_t = 8; ally.reversal_src = u
                    ally.reversal_cap = 58
                    self.teal_cast(u, ally)
                self.start_cast(u, 2, _rf, cast=0.25)
                return
            if ally.shield_regen_t <= 0 and u.ready("Shield of Regeneration") and ad < 165:
                u.use("Shield of Regeneration", 8)
                def _sr(u=u, ally=ally):
                    ally.shield_regen_t = 12
                    self.teal_cast(u, ally)
                self.start_cast(u, 2, _sr, cast=0.25)
                return
            if ally is not u and u.lifebond_t <= 0 and u.ready("Lifebond") and ad < 165:
                u.use("Lifebond", 8)
                def _lb(u=u, ally=ally):
                    u.lifebond_t = 999
                    ally.bond_src = u
                    ally.heal(42, source=u)
                    self.teal_cast(u, ally)
                self.start_cast(u, 2, _lb, cast=2.0)
                return
            if u.balth_spirit_t <= 0 and u.ready("Balthazars Spirit") and ad < 165:
                u.use("Balthazars Spirit", 8)
                def _bs(u=u, ally=ally):
                    u.balth_spirit_t = 999
                    ally.spirit_src = u
                    ally.heal(42, source=u)
                    self.teal_cast(u, ally)
                self.start_cast(u, 2, _bs, cast=2.0)
                return
            if u.ready("Blessed Signet"):
                u.use("Blessed Signet", 10)
                def _bsg(u=u):
                    n = (1 if u.lifebond_t > 0 else 0) + (1 if u.balth_spirit_t > 0 else 0)
                    u.energy = min(u.max_energy, u.energy + min(21, 3 * max(1, n)))
                    self.teal_cast(u, u)
                self.start_cast(u, 2, _bsg, cast=2.0)
                return
            return

        if u.cls == "Escaper":
            ally = self.neediest(u, 170) or u
            ad = math.hypot(ally.x - u.x, ally.y - u.y)
            if e and math.hypot(e.x - u.x, e.y - u.y) < 80 and u.hp < u.max_hp - 20:
                ex, ey = e.x - u.x, e.y - u.y
                ed = math.hypot(ex, ey) or 1
                u.target = (-ex / ed, -ey / ed)
            elif ally is not u:
                dx, dy = ally.x - u.x, ally.y - u.y
                d = math.hypot(dx, dy) or 1
                u.target = (dx / d, dy / d)
                if u.fear_t <= 0:
                    u.facing = math.atan2(dy, dx)
            def holy(a=ally):
                self.emit(u.x, u.y, HOLY, 12, 40, 3, 0.3)
                self.burst(u.x, u.y, WHITE, 22, 0.2)
                if a is not u:
                    self.emit(a.x, a.y, HOLY2, 10, 35, 3, 0.3)
                    self.tethers.append(Tether(u, a, 0.3, HOLY))
                sfx("holy", 0.1)
            locked = getattr(u, "gift_lock_t", 0) > 0
            escaping = u.dark_escape_t > 0
            ratio = ally.hp / ally.max_hp if ally.max_hp else 1
            allow_heal = (not escaping) or ratio <= 0.75
            hexes = ("curse_t", "antiheal_t", "blur_t", "water_hex_t", "seeping_t", "ash_t", "insec_t", "wastrel_t", "diversion_t")
            condi = [a for a in ("slow_t", "stun_t", "poison_t", "daze_t", "bleed", "knockdown_t", "weakness_t") if getattr(ally, a, 0) > 0]
            if e and math.hypot(e.x - u.x, e.y - u.y) < 70 and u.dark_escape_t <= 0 and u.ready("Dark Escape"):
                u.use("Dark Escape", 30)
                u.dark_escape_t = 10
                self.emit(u.x, u.y, SHADOW, 14, 40, 3, 0.35)
                return
            if allow_heal and ally is not u:
                best, best_s = None, -1
                for a in self.living(u.team):
                    if a is u or getattr(a, "is_pet", False) or getattr(a, "is_spirit", False):
                        continue
                    foes = self.living(1 - u.team)
                    near = min((math.hypot(a.x - f.x, a.y - f.y) for f in foes), default=0)
                    if near > best_s:
                        best_s, best = near, a
                if best and u.ready("Return") and best_s > 90 and math.hypot(e.x - u.x, e.y - u.y) < 90 if e else False:
                    u.use("Return", 15)
                    def _ret(u=u, best=best):
                        for o in self.living(1 - u.team):
                            if math.hypot(o.x - u.x, o.y - u.y) < 80:
                                o.slow_t = max(o.slow_t, 5.0)
                        self.emit(u.x, u.y, SHADOW, 16, 50, 4, 0.35)
                        u.x, u.y = best.x, best.y
                        self.clamp(u)
                        holy(best)
                    self.start_cast(u, 1, _ret, cast=0.25)
                    return
            if allow_heal and ally is not u and ratio < 0.7 and not locked and u.ready("Gift of Health") and ad < 170:
                u.use("Gift of Health", 5)
                def _gh(u=u, ally=ally):
                    ally.heal(135, source=u)
                    u.gift_lock_t = 5
                    holy(ally)
                self.start_cast(u, 2, _gh, cast=0.75)
                return
            if allow_heal and ratio < 0.8 and not locked and u.ready("Blessed Light") and ad < 170:
                u.use("Blessed Light", 3)
                def _bl(u=u, ally=ally, condi=condi):
                    ally.heal(178, source=u)
                    if condi:
                        attr = condi[0]
                        if attr == "bleed":
                            ally.bleed = 0
                        else:
                            setattr(ally, attr, 0.0)
                    for h in hexes:
                        if getattr(ally, h, 0) > 0:
                            setattr(ally, h, 0.0)
                            break
                    holy(ally)
                self.start_cast(u, 2, _bl, cast=0.75)
                return
            if allow_heal and ally is not u and condi and not locked and u.ready("Mend Condition") and ad < 170:
                u.use("Mend Condition", 2)
                def _mc(u=u, ally=ally, condi=condi):
                    attr = condi[0]
                    if attr == "bleed":
                        ally.bleed = 0
                    else:
                        setattr(ally, attr, 0.0)
                    ally.heal(89, source=u)
                    holy(ally)
                self.start_cast(u, 2, _mc, cast=0.75)
                return
            if allow_heal and ally.reversal_t <= 0 and not locked and u.ready("Reversal of Fortune") and ad < 170:
                u.use("Reversal of Fortune", 4)
                def _rf(u=u, ally=ally):
                    ally.reversal_t = 8; ally.reversal_src = u
                    ally.reversal_cap = 58
                    holy(ally)
                self.start_cast(u, 1, _rf, cast=0.25)
                return
            if allow_heal and ally.spirit_bond_t <= 0 and not locked and u.ready("Spirit Bond") and ad < 170:
                u.use("Spirit Bond", 12)
                def _sb(u=u, ally=ally):
                    ally.spirit_bond_t = 8
                    holy(ally)
                self.start_cast(u, 2, _sb, cast=1.0)
                return
            if allow_heal and ratio < 0.9 and not locked and u.ready("Signet of Devotion") and ad < 170:
                u.use("Signet of Devotion", 5)
                def _sd(u=u, ally=ally):
                    ally.heal(94, source=u)
                    holy(ally)
                self.start_cast(u, 3, _sd, cast=2.0)
                return
            return

        if u.cls == "Glimmer":
            ally = self.neediest(u, 170) or u
            ad = math.hypot(ally.x - u.x, ally.y - u.y)
            if ally is not u:
                dx, dy = ally.x - u.x, ally.y - u.y
                d = math.hypot(dx, dy) or 1
                u.target = (dx / d, dy / d)
                if u.fear_t <= 0:
                    u.facing = math.atan2(dy, dx)
            def glow(a=ally):
                col = (120, 210, 255)
                self.emit(u.x, u.y, col, 14, 50, 4, 0.35)
                self.burst(u.x, u.y, WHITE, 24, 0.2)
                if a is not u:
                    self.emit(a.x, a.y, col, 12, 40, 3, 0.3)
                    self.tethers.append(Tether(u, a, 0.35, col))
                sfx("holy", 0.1)
            pals = [a for a in self.living(u.team) if not getattr(a, "is_spirit", False) and not a.is_pet]
            if pals and all(a.hp / a.max_hp <= 0.90 for a in pals) and u.ready("Heal Party"):
                u.use("Heal Party", 2)
                def _hp(u=u, pals=pals):
                    for a in pals:
                        if a.alive:
                            a.heal(66, source=u)
                            self.emit(a.x, a.y, (120, 210, 255), 10, 40, 3, 0.35)
                    glow(u)
                self.start_cast(u, 3, _hp, cast=2.0)
                return
            ratio = ally.hp / ally.max_hp if ally.max_hp else 1
            condi = [a for a in ("slow_t", "stun_t", "poison_t", "daze_t", "bleed", "knockdown_t") if getattr(ally, a, 0) > 0]
            if condi and u.ready("Dismiss Condition") and ad < 170:
                u.use("Dismiss Condition", 3)
                def _dc(u=u, ally=ally, condi=condi):
                    attr = condi[0]
                    if attr == "bleed":
                        ally.bleed = 0
                    else:
                        setattr(ally, attr, 0.0)
                    if ally.reversal_t > 0 or ally.spirit_bond_t > 0 or ally.guardian_t > 0 or ally.holy_veil_t > 0:
                        ally.heal(71, source=u)
                    glow(ally)
                self.start_cast(u, 2, _dc, cast=0.75)
                return
            if getattr(ally, "guardian_t", 0) <= 0 and u.ready("Guardian") and ad < 170:
                u.use("Guardian", 6)
                def _g(u=u, ally=ally):
                    ally.guardian_t = 6
                    ally.heal(35, source=u)
                    glow(ally)
                self.start_cast(u, 2, _g, cast=1.0)
                return
            if getattr(ally, "absorb_t", 0) <= 0 and u.ready("Shield of Absorption") and ad < 170:
                u.use("Shield of Absorption", 10)
                def _sa(u=u, ally=ally):
                    ally.absorb_t = 6
                    ally.heal(35, source=u)
                    glow(ally)
                self.start_cast(u, 2, _sa, cast=1.0)
                return
            if u.glimmer_veil_t <= 0 and u.ready("Holy Veil") and ad < 170:
                u.use("Holy Veil", 12)
                def _hv(u=u, ally=ally):
                    u.glimmer_veil_t = 999
                    ally.holy_veil_t = 999
                    ally.veil_src = u
                    ally.heal(35, source=u)
                    glow(ally)
                self.start_cast(u, 2, _hv, cast=1.0)
                return
            if getattr(ally, "vigorous_t", 0) <= 0 and u.ready("Vigorous Spirit") and ad < 170:
                u.use("Vigorous Spirit", 4)
                def _vs(u=u, ally=ally):
                    ally.vigorous_t = 30
                    glow(ally)
                self.start_cast(u, 1, _vs, cast=0.25)
                return
            if ally.spirit_bond_t <= 0 and u.ready("Spirit Bond") and ad < 170:
                u.use("Spirit Bond", 12)
                def _sb(u=u, ally=ally):
                    ally.spirit_bond_t = 8
                    glow(ally)
                self.start_cast(u, 2, _sb, cast=1.0)
                return
            if ratio < 0.95 and u.ready("Glimmer of Light") and ad < 170:
                u.use("Glimmer of Light", 1)
                def _gl(u=u, ally=ally):
                    ally.heal(136, source=u)
                    glow(ally)
                self.start_cast(u, 1, _gl, cast=0.25)
                return
            return

        if u.cls == "Lifesheath":
            reach = AUTO_RANGE["short"]
            ally = self.neediest(u, reach + 20) or u
            ad = math.hypot(ally.x - u.x, ally.y - u.y)
            targeted = any(self.nearest(o) is u for o in self.living(1 - u.team) if o)
            if targeted and u.ready("Mirage Cloak"):
                u.use("Mirage Cloak", 15)
                def _mc(u=u):
                    u.mirage_t = 5
                    self.burst(u.x, u.y, (180, 170, 120), 70, 0.3)
                    for o in self.living(1 - u.team):
                        if math.hypot(o.x - u.x, o.y - u.y) < 90:
                            o.take(28, source=u)
                self.start_cast(u, 1, _mc, cast=0.2)
                return
            if u.meditate_t <= 0 and u.ready("Meditation") and u.energy < 8:
                u.use("Meditation", 20)
                def _md(u=u):
                    u.energy = 0
                    u.meditate_t = 20
                    u._ench_n = 1
                self.start_cast(u, 1, _md, cast=0.25)
                return
            if u.zeal_t <= 0 and u.ready("Eremites Zeal"):
                u.use("Eremites Zeal", 15)
                def _ez(u=u):
                    foes = [o for o in self.living(1 - u.team) if math.hypot(o.x - u.x, o.y - u.y) < reach]
                    u.energy = min(u.max_energy, u.energy + min(8, 3 * len(foes)))
                    u.zeal_t = 10
                self.start_cast(u, 1, _ez, cast=0.25)
                return
            if u.vital_t <= 0 and u.ready("Vital Boon"):
                u.use("Vital Boon", 8)
                def _vb(u=u):
                    u.vital_t = 20
                    u.max_hp += 76
                    u.hp += 76
                    u._vital_on = True
                self.start_cast(u, 2, _vb, cast=1.0)
                return
            if getattr(ally, "watchful_t", 0) <= 0 and u.ready("Watchful Intervention") and ad <= reach:
                u.use("Watchful Intervention", 15)
                def _wi(u=u, ally=ally):
                    ally.watchful_t = 60
                    ally.watchful_src = u
                    self.tethers.append(Tether(u, ally, 0.4, (240, 220, 80)))
                self.start_cast(u, 2, _wi, cast=1.0)
                return
            if getattr(ally, "sheath_t", 0) <= 0 and u.ready("Life Sheath") and ad <= reach:
                u.use("Life Sheath", 2)
                def _ls(u=u, ally=ally):
                    n = 0
                    for attr in ("slow_t", "bleed", "burn_t", "poison_t", "weakness_t", "cripple_t", "daze_t"):
                        if attr == "bleed" and ally.bleed > 0:
                            ally.bleed = 0
                            n += 1
                        elif getattr(ally, attr, 0) > 0:
                            setattr(ally, attr, 0.0)
                            n += 1
                        if n >= 2:
                            break
                    ally.sheath_t = 8
                    ally.sheath_src = u
                    self.emit(ally.x, ally.y, (180, 230, 160), 14, 50, 4, 0.35)
                self.start_cast(u, 1, _ls, cast=0.25)
                return
# 🔥 Lamentation periodic damage
            if getattr(u, "lament_t", 0) > 0:
                u.lament_tick -= dt
                if u.lament_tick <= 0:
                    u.lament_tick = 1.0
                    u.take(3)
                    self.emit(u.x, u.y, (60, 180, 100), 6, 20, 3, 0.3)
            # 🔥 Renewing Surge periodic damage + refund
            if getattr(u, "renew_surge_t", 0) > 0:
                u.renew_surge_tick -= dt
                if u.renew_surge_tick <= 0:
                    u.renew_surge_tick = 1.0
                    u.take(11, source=getattr(u, "renew_surge_src", None))
                    self.emit(u.x, u.y, (70, 200, 90), 6, 20, 3, 0.3)
                u._renew_surge_was_on = True
            elif getattr(u, "_renew_surge_was_on", False):
                u._renew_surge_was_on = False
                src = getattr(u, "renew_surge_src", None)
                if src and src.alive:
                    src.energy = min(src.max_energy, src.energy + 7)

            # 🔥 Resilient Weapon heal-over-time
            if getattr(u, "resilient_t", 0) > 0 and (u.has_hex() or u.has_condition()):
                u.heal(5 * dt)

            if ally is not u and u.ready("Imbue Health") and ad <= reach and ally.hp < ally.max_hp * 0.85:
                u.use("Imbue Health", 10)
                def _ih(u=u, ally=ally):
                    amt = min(300, u.hp * 0.41)
                    ally.heal(amt, source=u)
                    self.tethers.append(Tether(u, ally, 0.35, HOLY))
                self.start_cast(u, 1, _ih, cast=0.25)
                return
            if u.ready("Signet of Pious Light") and ad <= reach and ally.hp < ally.max_hp * 0.8:
                u.use("Signet of Pious Light", 20)
                def _sp(u=u, ally=ally):
                    stripped = False
                    for attr in ("vital_t", "mirage_t", "meditate_t", "zeal_t", "sheath_t"):
                        if getattr(u, attr, 0) > 0:
                            setattr(u, attr, 0.0)
                            stripped = True
                            break
                    ally.heal(102, source=u)
                    if stripped:
                        u.cds["Signet of Pious Light"] = 5.0
                    self.emit(ally.x, ally.y, HOLY, 16, 50, 4, 0.35)
                self.start_cast(u, 2, _sp, cast=1.0)
                return
            return


        if u.cls == "AirEnchant":
            reach = BODY * 8
            ally = self.neediest(u, reach + 30) or u
            ad = math.hypot(ally.x - u.x, ally.y - u.y)
            hurt_recent = getattr(ally, "hurt_t", 0) > 1.0
            if getattr(ally, "air_of_t", 0) <= 0 and u.ready("Air of Enchantment") and (hurt_recent or ally is not u) and ad <= reach:
                u.use("Air of Enchantment", 8)
                def _ae(u=u, ally=ally):
                    ally.air_of_t = 10
                    ally.heal(29, source=u)
                    self.emit(ally.x, ally.y, (160, 220, 255), 12, 40, 3, 0.3)
                self.start_cast(u, 1, _ae, cast=0.25)
                return
            if getattr(ally, "protect_t", 0) <= 0 and u.ready("Protective Spirit") and ad <= reach:
                u.use("Protective Spirit", 5)
                def _ps(u=u, ally=ally):
                    ally.protect_t = 22
                    ally.heal(29, source=u)
                    self.emit(ally.x, ally.y, (100, 200, 230), 12, 40, 3, 0.3)
                self.start_cast(u, 1, _ps, cast=0.25)
                return
            if getattr(ally, "absorb_t", 0) <= 0 and u.ready("Shield of Absorption") and ad <= reach:
                u.use("Shield of Absorption", 10)
                def _ab(u=u, ally=ally):
                    ally.absorb_t = 6
                    ally.heal(35, source=u)
                    ally.heal(29, source=u)
                self.start_cast(u, 2, _ab, cast=1.0)
                return
            if getattr(ally, "guardian_t", 0) <= 0 and u.ready("Guardian") and ad <= reach:
                u.use("Guardian", 6)
                def _g(u=u, ally=ally):
                    ally.guardian_t = 6
                    ally.heal(29, source=u)
                self.start_cast(u, 2, _g, cast=1.0)
                return
            if getattr(ally, "patient_t", 0) <= 0 and u.ready("Patient Spirit") and ad <= reach:
                u.use("Patient Spirit", 4)
                def _pt(u=u, ally=ally):
                    ally.patient_t = 2
                    ally.patient_src = u
                    ally._patient_on = True
                    ally.heal(29, source=u)
                self.start_cast(u, 1, _pt, cast=0.25)
                return
            if getattr(ally, "reversal_t", 0) <= 0 and u.ready("Reversal of Fortune") and ad <= reach:
                u.use("Reversal of Fortune", 2)
                def _rf(u=u, ally=ally):
                    ally.reversal_t = 8
                    ally.reversal_src = u
                    ally.reversal_cap = 58
                    ally.heal(29, source=u)
                self.start_cast(u, 1, _rf, cast=0.25)
                return
            condi = any(getattr(ally, a, 0) > 0 for a in ("slow_t", "bleed", "burn_t", "poison_t", "weakness_t", "daze_t"))
            if condi and u.ready("Dismiss Condition") and ad <= reach:
                u.use("Dismiss Condition", 3)
                def _dc(u=u, ally=ally):
                    for attr in ("slow_t", "burn_t", "poison_t", "weakness_t", "daze_t"):
                        if getattr(ally, attr, 0) > 0:
                            setattr(ally, attr, 0.0)
                            break
                    else:
                        ally.bleed = 0
                    ally.heal(71, source=u)
                    ally.heal(29, source=u)
                self.start_cast(u, 2, _dc, cast=0.75)
                return
            if ally is not u and u.ready("Dwaynas Kiss") and ad <= reach and ally.hp < ally.max_hp * 0.92:
                u.use("Dwaynas Kiss", 3)
                def _dk(u=u, ally=ally):
                    ench = sum(1 for a in ("reversal_t", "patient_t", "protect_t", "air_of_t", "guardian_t", "absorb_t", "sheath_t") if getattr(ally, a, 0) > 0)
                    hx = sum(1 for a in HEX_ATTRS if getattr(ally, a, 0) > 0)
                    ally.heal(71 + 28 * (ench + hx), source=u)
                    ally.heal(29, source=u)
                    self.emit(ally.x, ally.y, (180, 140, 255), 14, 50, 4, 0.35)
                self.start_cast(u, 2, _dk, cast=1.0)
                return
            return


        if u.cls == "Judge":
            reach = BODY * 8
            ally = self.neediest(u, reach + 40) or u
            ad = math.hypot(ally.x - u.x, ally.y - u.y)
            if u.spell_shield_t <= 0 and u.ready("Spell Shield") and u.hp < u.max_hp * 0.7:
                u.use("Spell Shield", 30)
                def _ss(u=u):
                    u.spell_shield_t = 15
                    u._shield_on = True
                    self.emit(u.x, u.y, (160, 210, 255), 16, 40, 4, 0.35)
                self.start_cast(u, 3, _ss, cast=2.0)
                return
            if u.ready("Fall Back") and any(a.hurt_t > 0 for a in self.living(u.team)):
                u.use("Fall Back", 25)
                self.burst(u.x, u.y, GOLD, 90, 0.4)
                for a in self.living(u.team):
                    if not getattr(a, "is_spirit", False) and math.hypot(a.x - u.x, a.y - u.y) < 200:
                        a.fallback_t = 8
                        a.fallback_src = u
                return
            if ally is not u and getattr(ally, "haste_sh_t", 0) <= 0 and u.ready("Make Haste") and ad < 200:
                u.use("Make Haste", 10)
                ally.haste_sh_t = 14
                self.burst(u.x, u.y, GOLD, 50, 0.3)
                ally.heal(32, source=u)
                return
            if getattr(ally, "breeze_t", 0) <= 0 and u.ready("Restful Breeze") and ad <= reach:
                u.use("Restful Breeze", 8)
                def _rb(u=u, ally=ally):
                    ally.breeze_t = 10
                    ally.breeze_src = u
                    ally.heal(32, source=u)
                self.start_cast(u, 2, _rb, cast=1.0)
                return
            if getattr(ally, "rod_t", 0) <= 0 and u.ready("Reversal of Damage") and ad <= reach:
                u.use("Reversal of Damage", 3)
                def _rd(u=u, ally=ally):
                    ally.rod_t = 8
                    ally.rod_src = u
                    ally.heal(32, source=u)
                    self.emit(ally.x, ally.y, (140, 200, 255), 12, 40, 3, 0.3)
                self.start_cast(u, 1, _rd, cast=0.25)
                return
            hexed = any(getattr(ally, a, 0) > 0 for a in HEX_ATTRS)
            if hexed and u.ready("Smite Hex") and ad <= reach:
                u.use("Smite Hex", 12)
                def _sh(u=u, ally=ally):
                    for a in HEX_ATTRS:
                        if getattr(ally, a, 0) > 0:
                            setattr(ally, a, 0.0)
                            self.burst(ally.x, ally.y, GOLD, 70, 0.4)
                            for o in self.living(1 - u.team):
                                if math.hypot(o.x - ally.x, o.y - ally.y) < 90:
                                    o.take(90, source=u)
                            break
                    ally.heal(32, source=u)
                self.start_cast(u, 2, _sh, cast=1.0)
                return
            condi = any(getattr(ally, a, 0) > 0 for a in ("slow_t", "bleed", "burn_t", "poison_t", "weakness_t", "daze_t"))
            if condi and u.ready("Smite Condition") and ad <= reach:
                u.use("Smite Condition", 7)
                def _sc(u=u, ally=ally):
                    stripped = False
                    for attr in ("slow_t", "burn_t", "poison_t", "weakness_t", "daze_t"):
                        if getattr(ally, attr, 0) > 0:
                            setattr(ally, attr, 0.0)
                            stripped = True
                            break
                    if not stripped and ally.bleed:
                        ally.bleed = 0
                        stripped = True
                    col = (80, 220, 120) if stripped else (80, 140, 255)
                    self.tethers.append(Tether(u, ally, 0.4, col))
                    if stripped:
                        for o in self.living(1 - u.team):
                            if math.hypot(o.x - ally.x, o.y - ally.y) < 100:
                                o.take(63, source=u)
                    ally.heal(32, source=u)
                self.start_cast(u, 2, _sc, cast=1.0)
                return
            e = self.nearest(u)
            if e and u.ready("Ray of Judgement") and math.hypot(e.x - u.x, e.y - u.y) < 280:
                u.use("Ray of Judgement", 15)
                def _rj(u=u, e=e):
                    self.rays.append([e.x, e.y, u.team, 5.0, u])
                    self.burst(e.x, e.y, GOLD, 60, 0.35)
                self.start_cast(u, 2, _rj, cast=1.0)
                return
            return


        if u.cls == "Conditioner":
            reach = BODY * 8
            ally = self.neediest(u, reach + 40) or u
            ad = math.hypot(ally.x - u.x, ally.y - u.y)
            if u.balanced_t <= 0 and u.ready("Balanced Stance"):
                u.use("Balanced Stance", 30)
                u.balanced_t = 16
                return
            if ally is not u and getattr(ally, "aegis_t", 0) <= 0 and u.ready("Aegis") and getattr(ally, "hurt_t", 0) > 0 and ad <= reach:
                u.use("Aegis", 30)
                def _ag(u=u, ally=ally):
                    ally.aegis_t = 3
                    ally.heal(29, source=u)
                    self.emit(ally.x, ally.y, (200, 230, 255), 16, 50, 4, 0.35)
                self.start_cast(u, 1, _ag, cast=0.25)
                return
            flags = [
                ("poison_t",), ("blind_t",), ("daze_t",), ("bleed",), ("burn_t",), ("weakness_t",),
                ("cracked_t",), ("deepwound_t",), ("slow_t",),
            ]
            ncond = 0
            if ally is not u:
                if ally.bleed > 0: ncond += 1
                for attr in ("poison_t", "blind_t", "daze_t", "burn_t", "weakness_t", "cracked_t", "deepwound_t", "slow_t"):
                    if getattr(ally, attr, 0) > 0:
                        ncond += 1
            if ncond and u.ready("Restore Condition") and ad <= reach and ally is not u:
                u.use("Restore Condition", 2)
                def _rc(u=u, ally=ally):
                    n = 0
                    if ally.bleed:
                        ally.bleed = 0
                        n += 1
                    for attr in ("poison_t", "blind_t", "daze_t", "burn_t", "weakness_t", "cracked_t", "deepwound_t", "slow_t"):
                        if getattr(ally, attr, 0) > 0:
                            setattr(ally, attr, 0.0)
                            n += 1
                    ally.heal(66 * n + 29, source=u)
                    self.emit(ally.x, ally.y, (140, 230, 190), 16, 50, 4, 0.4)
                self.start_cast(u, 2, _rc, cast=0.75)
                return
            if getattr(ally, "spirit_bond_t", 0) <= 0 and u.ready("Spirit Bond") and ad <= reach:
                u.use("Spirit Bond", 5)
                def _sb(u=u, ally=ally):
                    ally.spirit_bond_t = 8
                    ally.spirit_bond_hits = 10
                    ally.bond_min = 50
                    ally.bond_heal_amt = 86
                    ally.bond_heal_src = u
                    ally.heal(29, source=u)
                self.start_cast(u, 1, _sb, cast=0.25)
                return
            if getattr(ally, "hands_t", 0) <= 0 and u.ready("Shielding Hands") and ad <= reach:
                u.use("Shielding Hands", 15)
                def _hd(u=u, ally=ally):
                    ally.hands_t = 8
                    ally.heal(29, source=u)
                self.start_cast(u, 1, _hd, cast=0.25)
                return
            if getattr(ally, "guardian_t", 0) <= 0 and u.ready("Guardian") and ad <= reach:
                u.use("Guardian", 6)
                def _g(u=u, ally=ally):
                    ally.guardian_t = 6
                    ally.heal(29, source=u)
                self.start_cast(u, 2, _g, cast=1.0)
                return
            if getattr(ally, "holy_veil_t", 0) <= 0 and u.ready("Holy Veil") and ad <= reach:
                u.use("Holy Veil", 12)
                def _hv(u=u, ally=ally):
                    ally.holy_veil_t = 12
                    ally.heal(29, source=u)
                self.start_cast(u, 2, _hv, cast=1.0)
                return
            if ally is not u and getattr(ally, "stable_t", 0) <= 0 and u.ready("Aura of Stability") and ad <= reach:
                u.use("Aura of Stability", 12)
                def _st(u=u, ally=ally):
                    ally.stable_t = 8
                    ally.heal(29, source=u)
                self.start_cast(u, 1, _st, cast=0.25)
                return
            return

        if not e:
            return
        dx, dy = e.x - u.x, e.y - u.y
        dist = math.hypot(dx, dy) or 1
        u.target = (dx / dist, dy / dist)
        if u.fear_t <= 0:
            u.facing = math.atan2(dy, dx)
        if u.cls not in MELEE_CLS and u.cls not in HEAL_PICKS:
            reach = AUTO_RANGE[self.auto_band(u)] if u.cls not in HEAL_PICKS else AUTO_RANGE["caster"]
            if getattr(u, "chase_t", 0) >= 2.0:
                u.target = (dx / dist, dy / dist)
            elif dist < reach * 0.78:
                u.target = (-dx / dist, -dy / dist)
            elif dist > reach:
                u.target = (dx / dist, dy / dist)
            else:
                sign = getattr(u, "kite_sign", 0) or (1 if random.random() < 0.5 else -1)
                if random.random() < 0.08:
                    sign = -sign
                    u.kite_sign = sign
                if random.random() < 0.12:
                    u.target = (dx / dist, dy / dist)
                else:
                    u.target = (-dy / dist * 0.55 * sign, dx / dist * 0.55 * sign)

        if u.cls == "Mage":
            if u.hp < 28 and u.ready("Ice Block"):
                u.use("Ice Block", 14)
                sfx("iceblock")
                u.iceblock_t = 3.0
                self.burst(u.x, u.y, ICE, 40, 0.4)
                return
            melee_on = any(
                o.cls in MELEE_CLS and math.hypot(o.x - u.x, o.y - u.y) < 58
                for o in self.living(1 - u.team)
            )
            def _nova(u=u):
                self.burst(u.x, u.y, ICE, 95, 0.45)
                self.emit(u.x, u.y, ICE, 28, 120, 4, 0.5)
                for o in self.living(1 - u.team):
                    if math.hypot(o.x - u.x, o.y - u.y) < 95:
                        o.freeze_t = max(o.freeze_t, 1.6)
                        o.take(12, source=u)
            def _blink(u=u, toward=True):
                sfx("blink")
                self.emit(u.x, u.y, PURPLE, 16, 90, 4, 0.3)
                face = u.facing if toward else u.facing + math.pi
                u.x += math.cos(face) * 140
                u.y += math.sin(face) * 140
                self.clamp(u)
                self.emit(u.x, u.y, PURPLE, 16, 90, 4, 0.3)
            if melee_on:
                if u.ready("Frost Nova") and u.ready("Blink"):
                    if random.random() < 0.5:
                        u.use("Frost Nova", 7)
                        sfx("frostnova")
                        _nova()
                    else:
                        u.use("Blink", 8)
                        _blink(toward=False)
                    return
                if u.ready("Frost Nova"):
                    u.use("Frost Nova", 7)
                    sfx("frostnova")
                    _nova()
                    return
                if u.ready("Blink"):
                    u.use("Blink", 8)
                    _blink(toward=False)
                    return
            elif e and u.ready("Blink") and dist > 100 and random.random() < 0.35:
                u.use("Blink", 8)
                u.facing = math.atan2(e.y - u.y, e.x - u.x)
                _blink(toward=True)
                nd = math.hypot(e.x - u.x, e.y - u.y)
                if nd < 95 and u.ready("Frost Nova"):
                    u.use("Frost Nova", 7)
                    sfx("frostnova")
                    _nova()
                return
            if dist < 85 and u.ready("Frost Nova"):
                u.use("Frost Nova", 7)
                sfx("frostnova")
                self.burst(u.x, u.y, ICE, 95, 0.45)
                self.emit(u.x, u.y, ICE, 28, 120, 4, 0.5)
                for o in self.living(1 - u.team):
                    if math.hypot(o.x - u.x, o.y - u.y) < 95:
                        o.freeze_t = max(o.freeze_t, 1.6)
                        o.take(12)
                return
            if dist < 120 and u.ready("Cone of Cold"):
                u.use("Cone of Cold", 5)
                sfx("cone")
                fx, fy = math.cos(u.facing), math.sin(u.facing)
                for _ in range(10):
                    ang = u.facing + random.uniform(-0.5, 0.5)
                    self.particles.append(Particle(u.x + fx * 10, u.y + fy * 10, math.cos(ang) * 180, math.sin(ang) * 180, 0.35, 0.35, ICE, 4))
                for o in self.living(1 - u.team):
                    if self.in_front(u, o, 120, 0.55):
                        o.slow_t = max(o.slow_t, 2.2)
                        o.take(16)
                return
            if dist > 160 and u.ready("Blink"):
                u.use("Blink", 8)
                sfx("blink")
                self.emit(u.x, u.y, PURPLE, 16, 90, 4, 0.3)
                u.x += math.cos(u.facing) * 140
                u.y += math.sin(u.facing) * 140
                self.clamp(u)
                self.emit(u.x, u.y, PURPLE, 16, 90, 4, 0.3)
                return
            if u.ready("Frostbolt") and dist < 300:
                u.use("Frostbolt", 1.6)
                self.start_cast(u, 2, lambda u=u: self.fire(u, "frost", L_DMG[2], 300, 1.3))
        elif u.cls == "Rogue":
            if dist > 90 and u.ready("Sprint"):
                u.use("Sprint", 10)
                sfx("sprint")
                u.sprint_t = 2.5
            if dist < 260 and u.ready("Poison Throw"):
                u.use("Poison Throw", 3)
                self.start_cast(u, 2, lambda u=u: self.fire(u, "poison", L_DMG[2], 340, 1.0))
            if dist < 52 and u.ready("Cheap Shot"):
                u.use("Cheap Shot", 8)
                sfx("cheapshot")
                self.give_cc(e, "stun", 1.4, u)
                e.take(L_DMG[2])
            if dist < 48 and u.ready("Backstab"):
                u.use("Backstab", 2.2)
                sfx("backstab")
                bonus = 1.6 if abs(((u.facing - e.facing + math.pi) % (2 * math.pi)) - math.pi) < 1.2 else 1.0
                self.start_cast(u, 3, lambda e=e, bonus=bonus, u=u: e.take(L_DMG[3] * bonus, melee=True, source=u))
            if u.hp < 40 and u.ready("Shadow Clone") and not u.clone:
                u.use("Shadow Clone", 16)
                sfx("clone")
                c = Fighter(u.name + " Shade", "Rogue", u.team, u.x + 12, u.y + 12)
                self._stats(c)
                c.hp = u.hp * 0.5
                c.max_hp = c.hp
                c.clone = True
                self.units.append(c)

                
        elif u.cls == "Warlock":
            reach = AUTO_RANGE["caster"]
            if not u.pentagram_used and u.ready("Pentagram") and self.time > 6:
                u.use("Pentagram", 99)
                sfx("pentagram")
                u.pentagram_used = True
                u.channel = "pentagram"
                u.channel_t = 5.0
                u.channel_acc = 0
                return
            if e and dist <= reach and u.ready("Fear") and getattr(e, "fear_t", 0) <= 0:
                u.use("Fear", 10)
                sfx("fear")
                e.fear_t = max(e.fear_t, 2.4)
                e.fear_wander = True
                ang = random.uniform(0, math.tau)
                e.fear_dir = (math.cos(ang), math.sin(ang))
                e.fear_turn = 0.35
                self.emit(e.x, e.y, CURSE, 16, 50, 4, 0.4)
                return
            if e and dist <= reach and u.ready("Rain of Fire"):
                u.use("Rain of Fire", 12)
                sfx("rain")
                u.channel = "rain"
                u.channel_t = 3.0
                u.channel_acc = 0
                u.rain_n = 0
                u.channel_target = e
                return
            if e and dist <= reach and u.ready("Soul Siphon"):
                u.use("Soul Siphon", 8)
                sfx("siphon")
                u.channel = "siphon"
                u.channel_t = 2.4
                u.channel_target = e
                self.tethers.append(Tether(u, e, 0.4, CURSE))
                return
            if e and e.antiheal_t <= 0 and u.ready("Curse of Anti Healing") and dist <= reach:
                u.use("Curse of Anti Healing", 14)
                sfx("antiheal")
                e.antiheal_t = 10.0
                return
            if e and e.curse_t <= 0 and u.ready("Curse of Curses") and dist <= reach:
                u.use("Curse of Curses", 6)
                sfx("curse")
                e.curse_t = 8.0
                e.curse_tick = 2.0
        elif u.cls == "Dark Cultist":
            reach = AUTO_RANGE["caster"]
            if u.hp < 45 and u.ready("Shadow Clone") and not u.clone:
                u.use("Shadow Clone", 16)
                sfx("clone")
                c = Fighter(u.name + " Shade", "Dark Cultist", u.team, u.x + 12, u.y + 12)
                self._stats(c)
                c.hp = u.hp * 0.5
                c.max_hp = c.hp
                c.clone = True
                self.units.append(c)
                self.emit(u.x, u.y, SHADOW, 20, 60, 4, 0.5)
                return
            if e and dist <= reach and u.ready("Soul Siphon"):
                u.use("Soul Siphon", 8)
                sfx("siphon")
                u.channel = "siphon"
                u.channel_t = 2.4
                u.channel_target = e
                self.tethers.append(Tether(u, e, 0.4, CURSE))
                return
            if e and e.antiheal_t <= 0 and u.ready("Curse of Anti Healing") and dist <= reach:
                u.use("Curse of Anti Healing", 14)
                sfx("antiheal")
                e.antiheal_t = 10.0
                return
            if e and e.rot_t <= 0 and u.ready("Cultists Rot") and dist <= reach:
                u.use("Cultists Rot", 6)
                sfx("curse")
                e.rot_t = 8.0
                e.rot_tick = 2.0
                self.emit(e.x, e.y, (90, 40, 120), 14, 40, 4, 0.4)
                return
            if e and e.seeping_t <= 0 and u.ready("Seeping Wound") and dist <= reach:
                u.use("Seeping Wound", 6)
                sfx("curse")
                def _seep(e=e):
                    e.seeping_t = 7
                    e.seeping_tick = 1
                    e.slow_t = max(e.slow_t, 7)
                    self.emit(e.x, e.y, (180, 40, 40), 12, 40, 3, 0.35)
                self.start_cast(u, 2, _seep)
                return
            if e and e.curse_t <= 0 and u.ready("Curse of Curses") and dist <= reach:
                u.use("Curse of Curses", 6)
                sfx("curse")
                e.curse_t = 8.0
                e.curse_tick = 2.0
        elif u.cls == "Beast Master":
            pets = [un for un in self.units if un.owner_name == u.name and un.cls in BEAST_PETS]
            live = [p for p in pets if p.alive]
            pet = live[0] if live else None
            # Comfort Animal: heal the pet, or resurrect it if it has fallen.
            if pet and pet.hp < pet.max_hp * 0.55 and u.ready("Comfort Animal"):
                u.use("Comfort Animal", 1)
                sfx("heal")
                u.channel = "beast_comfort"
                u.channel_t = 1.0
                u.channel_max = 1.0
                u.channel_target = pet
                return
            if not live and pets and u.ready("Comfort Animal"):
                u.use("Comfort Animal", 1)
                sfx("heal")
                u.channel = "beast_comfort"
                u.channel_t = 1.0
                u.channel_max = 1.0
                u.channel_target = pets[0]
                return
            # Call of Protection: long-duration pet damage reduction.
            if pet and pet.pet_dr_t <= 0 and u.ready("Call of Protection"):
                u.use("Call of Protection", 90)
                sfx("ward")
                pet.pet_dr_t = 120
                self.emit(pet.x, pet.y, (120, 180, 120), 16, 40, 4, 0.4)
                self.burst(pet.x, pet.y, (90, 150, 90), 34, 0.3)
                return
            # Feral Aggression: pet attacks faster and hits harder.
            if pet and pet.pet_feral_t <= 0 and u.ready("Feral Aggression"):
                u.use("Feral Aggression", 20)
                sfx("howl")
                pet.pet_feral_t = 21
                pet.pet_feral_bonus = 10
                self.emit(pet.x, pet.y, (200, 120, 60), 18, 60, 4, 0.45)
                return
            # Great Dwarf Weapon: enchant another ally for +20 melee damage.
            if u.ready("Great Dwarf Weapon"):
                mates = [a for a in self.living(u.team) if a is not u and not getattr(a, "is_spirit", False)
                         and getattr(a, "gdw_t", 0) <= 0]
                mates = [a for a in mates if math.hypot(a.x - u.x, a.y - u.y) <= 260]
                if mates:
                    ally = min(mates, key=lambda a: (a.x - u.x) ** 2 + (a.y - u.y) ** 2)
                    u.use("Great Dwarf Weapon", 5)
                    def _gdw(u=u, ally=ally):
                        ally.gdw_t = 20
                        ally.gdw_src = u
                        self.emit(ally.x, ally.y, (210, 180, 90), 16, 50, 4, 0.4)
                        self.burst(ally.x, ally.y, GOLD, 34, 0.3)
                    self.start_cast(u, 2, _gdw, cast=1.0)
                    return
            # Strike as One: shout that sends the pet in and sets up bleed + cripple.
            if pet and e and u.ready("Strike as One"):
                u.use("Strike as One", 10)
                sfx("shout")
                pet.x, pet.y = e.x + random.uniform(-14, 14), e.y + random.uniform(-14, 14)
                self.clamp(pet)
                pet.strike_as_one_t = 16
                pet.strike_as_one_src = u
                u.strike_as_one_t = 16
                u.strike_as_one_src = u
                self.emit(e.x, e.y, (200, 60, 60), 18, 70, 4, 0.4)
                self.burst(e.x, e.y, (180, 40, 40), 40, 0.3)
                return
            # Pet attack skills (only usable while the companion lives).
            if pet and e:
                if u.ready("Predators Pounce"):
                    u.use("Predators Pounce", 5)
                    pet.facing = math.atan2(e.y - pet.y, e.x - pet.x)
                    def _pounce(pet=pet, u=u):
                        self.fire(pet, "maul", L_DMG[1] + 37, 320, 1.0,
                                  on_hit=lambda tgt, pet=pet: pet.heal(53, source=pet))
                    self.start_cast(u, 2, _pounce, cast=0.5)
                    return
                if u.ready("Brutal Pet Strike"):
                    u.use("Brutal Pet Strike", 5)
                    pet.facing = math.atan2(e.y - pet.y, e.x - pet.x)
                    def _brutal(pet=pet, u=u):
                        def _hit(tgt, pet=pet):
                            if tgt.hp < tgt.max_hp * 0.5:
                                tgt.take(37, source=pet)
                                pet.pet_brutal_stacks = min(4, pet.pet_brutal_stacks + 1)
                                pet.pet_brutal_t = 30
                                if not pet.base_max:
                                    pet.base_max = pet.max_hp
                                pet.max_hp = pet.base_max * (1 + 0.25 * pet.pet_brutal_stacks)
                                pet.hp = min(pet.max_hp, pet.hp + pet.base_max * 0.25)
                                self.burst(pet.x, pet.y, (200, 80, 40), 44, 0.35)
                        self.fire(pet, "maul", L_DMG[1] + 37, 320, 1.0, on_hit=_hit)
                    self.start_cast(u, 2, _brutal, cast=0.5)
                    return
                if u.ready("Scavenger Strike"):
                    u.use("Scavenger Strike", 10)
                    pet.facing = math.atan2(e.y - pet.y, e.x - pet.x)
                    def _scav(pet=pet, u=u):
                        def _hit(tgt, pet=pet, u=u):
                            if tgt.has_condition():
                                u.energy = min(u.max_energy, u.energy + 16)
                                self.emit(u.x, u.y, (120, 220, 140), 12, 40, 3, 0.35)
                        self.fire(pet, "maul", L_DMG[1] + 26, 320, 1.0, on_hit=_hit)
                    self.start_cast(u, 2, _scav, cast=0.5)
                    return
        elif u.cls == "Trident":
            if u.water_armor_t <= 0 and u.ready("Water Attunement"):
                u.use("Water Attunement", 16)
                sfx("ward")
                u.water_armor_t = 14
                self.burst(u.x, u.y, WATER, 50, 0.5)
                self.emit(u.x, u.y, ICE, 24, 80, 5, 0.7)
            if getattr(u, "hurt_t", 0) > 0 and u.hp < u.max_hp * 0.99 and u.ready("Ward Against Melee"):
                u.use("Ward Against Melee", 18)
                sfx("ward")
                wx, wy = u.x, u.y
                if e:
                    d = math.hypot(e.x - u.x, e.y - u.y) or 1
                    wx += (e.x - u.x) / d * 50
                    wy += (e.y - u.y) / d * 50
                self.wards.append([wx, wy, u.team, 16.0])
                self.burst(wx, wy, WATER, 50, 0.35)
            if e and dist < 160 and u.ready("Frozen Burst"):
                u.use("Frozen Burst", 7)
                sfx("burst")
                self.burst(e.x, e.y, WATER, 110, 0.55)
                self.emit(e.x, e.y, ICE, 28, 140, 6, 0.55)
                for o in self.living(1 - u.team):
                    if math.hypot(o.x - e.x, o.y - e.y) < 110:
                        o.take(L_DMG[3], source=u)
                        o.slow_t = max(o.slow_t, 8.0)
                        o.water_hex_t = max(o.water_hex_t, 8.0)
                return
            if e and u.ready("Blurred Vision"):
                u.use("Blurred Vision", 12)
                sfx("cone")
                for o in self.living(1 - u.team):
                    if math.hypot(o.x - e.x, o.y - e.y) < 70:
                        o.blur_t = max(o.blur_t, 10.0)
                        o.water_hex_t = max(o.water_hex_t, 10.0)
                        self.burst(o.x, o.y, (180, 220, 255), 36, 0.35)
                return
            if e and u.ready("Freezing Gust"):
                u.use("Freezing Gust", 5)
                sfx("cone")
                self.emit(e.x, e.y, WATER, 20, 90, 5, 0.45)
                if e.water_hex_t > 0:
                    e.take(L_DMG[3], source=u)
                    self.burst(e.x, e.y, ICE, 40, 0.35)
                else:
                    e.slow_t = max(e.slow_t, 4.0)
                    e.water_hex_t = max(e.water_hex_t, 4.0)
                return
            if e and u.ready("Water Trident") and dist < 320:
                u.use("Water Trident", 3.2)
                sfx("trident")
                self.start_cast(u, 4, lambda u=u: self.fire(u, "trident", L_DMG[4], 460, 1.15))
                self.emit(u.x, u.y, WATER, 16, 70, 5, 0.35)
        elif u.cls == "Thumper":
            pets = [un for un in self.units if un.owner_name == u.name and un.cls in PET_KINDS]
            live = [p for p in pets if p.alive]
            pet = live[0] if live else None
            if len(live) < 4 and u.ready("Comfort Animal"):
                u.use("Comfort Animal", 10)
                sfx("heal")
                u.channel = "comfort"
                u.channel_t = 3.0
                u.channel_max = 3.0
                return
            if live and any(p.hp < p.max_hp * 0.45 for p in live) and u.ready("Comfort Animal"):
                u.use("Comfort Animal", 10)
                sfx("heal")
                u.channel = "comfort"
                u.channel_t = 3.0
                u.channel_max = 3.0
                return
            if live and u.ready("Rampage as One"):
                u.use("Rampage as One", 16)
                sfx("sprint")
                u.rampage_t = 13
                for p in live:
                    p.rampage_t = 13
            if pet and pet.alive and u.ready("Bestial Mauling") and e:
                u.use("Bestial Mauling", 7)
                pet.facing = math.atan2(e.y - pet.y, e.x - pet.x)
                self.start_cast(u, 2, lambda pet=pet: self.fire(pet, "maul", L_DMG[2], 300, 1.0))
            if dist < 150 and u.ready("Hammer Bash"):
                u.use("Hammer Bash", 5)
                sfx("bash")
                fx, fy = math.cos(u.facing), math.sin(u.facing)
                for o in self.living(1 - u.team):
                    ox, oy = o.x - u.x, o.y - u.y
                    along = ox * fx + oy * fy
                    perp = abs(ox * fy - oy * fx)
                    if 0 < along < 160 and perp < 28:
                        o.take(L_DMG[3])
                        self.give_cc(o, "kd", 1.4, u)
                        self.emit(o.x, o.y, (160, 140, 80), 10, 50, 3, 0.3)
                return
            if dist < 52 and u.ready("Crushing Blow"):
                u.use("Crushing Blow", 4)
                sfx("slash")
                e.take(L_DMG[3], melee=True, source=u)
                if e.knockdown_t > 0:
                    if not e.base_max:
                        e.base_max = e.max_hp
                    e.deepwound_t = 16
                    e.max_hp = e.base_max * 0.8
                    e.hp = min(e.hp, e.max_hp)
                    self.emit(e.x, e.y, RED, 12, 40, 3, 0.35)
        elif u.cls == "Bellringer":
            fighting = any(
                (u2.alive and not getattr(u2, "is_spirit", False) and u2.hp < u2.max_hp * 0.995)
                or getattr(u2, "hurt_t", 0) > 0
                for u2 in self.units
            )
            foe = e or self.nearest(u)
            if foe and u.ready("Harmonic Swarm") and not any(s[0] == u.team for s in self.swarms):
                u.use("Harmonic Swarm", 12)
                sfx("favor")
                self.swarms.append([u.team, foe])
                self.emit(foe.x, foe.y, GOLD, 18, 70, 4, 0.4)
                self.burst(foe.x, foe.y, GOLD, 40, 0.3)
                self.tethers.append(Tether(u, foe, 0.5, GOLD))
                return
            n_pets = sum(1 for p in self.units if p.owner_name == u.name and p.alive and p.cls in ("Knight", "Archer"))
            if fighting and n_pets < 2 and (u.ready("Bell Ring") or u.ready("Archer Bell")):
                kind = random.choice(["Knight", "Archer"])
                skill = "Bell Ring" if kind == "Knight" else "Archer Bell"
                if not u.ready(skill):
                    skill = "Archer Bell" if skill == "Bell Ring" else "Bell Ring"
                if u.ready(skill):
                    u.use(skill, 10)
                    u.cds["Bell Ring"] = max(u.cds.get("Bell Ring", 0), 10)
                    u.cds["Archer Bell"] = max(u.cds.get("Archer Bell", 0), 10)
                    sfx("bell")
                    def _summon(u=u, kind=kind):
                        pet = Fighter(u.name + " " + kind, kind, u.team, u.x + 18, u.y + (-16 if kind == "Archer" else 0))
                        pet.owner_name = u.name
                        pet.owner_ref = u
                        pet.is_pet = True
                        self._stats(pet)
                        self.units.append(pet)
                    self.start_cast(u, 3, _summon, cast=2.2)
                    return
            if u.ready("Soothing Sounds"):
                u.use("Soothing Sounds", 18)
                sfx("heal")
                for a in self.living(u.team):
                    if not a.is_pet:
                        a.soothe_t = 15
                        a.soothe_src = u
                        a.soothe_tick = 3
            if u.ready("Sound Wave"):
                u.use("Sound Wave", 8)
                sfx("heal")
                allies = [a for a in self.living(u.team) if not a.is_pet]
                allies.sort(key=lambda a: a.hp / a.max_hp)
                picks = []
                if u in allies:
                    picks.append(u)
                for a in allies:
                    if a not in picks:
                        picks.append(a)
                    if len(picks) == 2:
                        break
                for a in picks:
                    self.apply_heal(a, L_HEAL[2], "wave")
            if u.ready("High Ring"):
                u.use("High Ring", 14)
                sfx("bell")
                self.burst(u.x, u.y, GOLD, 160, 0.4)
                for o in self.living(1 - u.team):
                    if math.hypot(o.x - u.x, o.y - u.y) < 150:
                        self.give_cc(o, "stun", 1.3, u)
        elif u.cls in PET_KINDS or u.cls in ("Pup", "Knight", "Archer") or u.cls in BEAST_PETS:
            if not e:
                return
            if u.cls == "Chimp":
                # Ranged companion: hurls a block of poo that stuns a foe.
                feral = getattr(u, "pet_feral_t", 0) > 0
                bonus = getattr(u, "pet_feral_bonus", 0) if feral else 0
                if dist < 300 and u.ready("poo"):
                    u.use("poo", 8 * (0.67 if feral else 1.0))
                    self.fire(u, "poo", L_DMG[1] + bonus, 300, 1.1,
                              on_hit=lambda tgt, u=u: self.give_cc(tgt, "stun", 1.2, u))
                elif dist < 300 and u.ready("throw"):
                    u.use("throw", 1.6 * (0.67 if feral else 1.0))
                    self.fire(u, "poo", 16 + bonus, 280, 0.9)
                return
            if u.cls == "Boa":
                # Melee companion: every landed hit stacks a 20s health-degeneration poison.
                feral = getattr(u, "pet_feral_t", 0) > 0
                bonus = getattr(u, "pet_feral_bonus", 0) if feral else 0
                if dist < 48 and u.ready("bite"):
                    u.use("bite", 1.2 * (0.67 if feral else 1.0))
                    def _boa_hit(tgt, u=u):
                        u.pet_poison_stacks = min(10, u.pet_poison_stacks + 1)
                        u.pet_poison_t = 20.0
                        u.pet_poison_tick = 2.0
                        u.pet_poison_src = getattr(u, "owner_ref", None)
                        tgt.poison_t = max(tgt.poison_t, 20.0)
                        tgt.poison_tick = 2.0
                        self.emit(tgt.x, tgt.y, POISON, 10, 40, 3, 0.3)
                    e.take(L_DMG[1] + bonus, melee=True, source=u)
                    _boa_hit(e)
                return
            if u.cls == "Bird" and e.channel and u.ready("interrupt"):
                u.use("interrupt", 6)
                e.channel = ""
                e.channel_target = None
                self.give_cc(e, "stun", 0.3, u)
                sfx("cheapshot")
            if u.cls == "Wolf" and u.ready("howl"):
                u.use("howl", 12)
                sfx("howl")
                for k in (-12, 12):
                    pup = Fighter(u.name + " Pup", "Pup", u.team, u.x + k, u.y)
                    pup.owner_name = u.owner_name
                    pup.owner_ref = getattr(u, "owner_ref", None)
                    pup.is_pet = True
                    self._stats(pup)
                    self.units.append(pup)
            if u.cls == "Spider" and dist < 240 and u.ready("web"):
                u.use("web", 7)
                self.fire(u, "web", L_DMG[1], 280, 1.1)
            if u.cls == "Archer":
                if dist > AUTO_RANGE["short"] + 10:
                    return
                if u.ready("strafe"):
                    u.use("strafe", 14)
                    for _ in range(3):
                        self.fire(u, "arrow", 12, 300, 0.7)
                elif u.ready("shot"):
                    u.use("shot", 1.6)
                    self.fire(u, "arrow", 16, 280, 0.75)
            elif u.cls == "Cat" and dist < 48:
                if u.ready("scratch"):
                    u.use("scratch", 0.85)
                    e.take(L_DMG[2] + 12, melee=True, source=u)
                    e.bleed = min(8, e.bleed + 1)
                    e.bleed_tick = min(getattr(e, "bleed_tick", 2) or 2, 1.0)
                    self.emit(e.x, e.y, (180, 30, 60), 10, 40, 3, 0.25)
            elif u.cls == "Knight" and dist < 46:
                if u.ready("melee"):
                    u.use("melee", 1.45)
                    e.take(22, melee=True, source=u)
            elif u.cls in ("Bear", "Wolf", "Pup") and dist < 46:
                if u.ready("melee"):
                    u.use("melee", 1.15)
                    raw = (L_DMG[2] + 8) if u.cls == "Bear" else (L_DMG[2] if u.cls == "Wolf" else 28)
                    e.take(raw, melee=True, source=u)
                    if u.cls == "Pup":
                        u.attacks_left -= 1
                        if u.attacks_left <= 0:
                            u.alive = False
                            u.hp = 0
            elif u.cls == "Bird" and dist < 40 and u.ready("peck"):
                u.use("peck", 1.0)
                e.take(L_DMG[1], melee=True, source=u)
            elif u.cls == "Spider" and dist < 40 and u.ready("bite"):
                u.use("bite", 1.2)
                e.take(L_DMG[1], melee=True, source=u)
        elif u.cls == "Infernal":
            if e and dist < 70:
                for o in self.living(1 - u.team):
                    if math.hypot(o.x - u.x, o.y - u.y) < 62:
                        o.take(L_DMG[2] * dt)
                if random.random() < 0.4:
                    self.particles.append(Particle(u.x + random.uniform(-18, 18), u.y + random.uniform(-18, 18), 0, -30, 0.3, 0.3, FIRE, 4, -20))
        elif u.cls == "Deadsword":
            if not e:
                return
            if getattr(u, "live_vic_hold", False) is False and u.ready("Live Vicariously"):
                tgt = u
                u.use("Live Vicariously", 8)
                def _lv(u=u, tgt=tgt):
                    u.live_vic_hold = True
                    u.live_vic_on = tgt
                    tgt.live_vic_t = 999
                    tgt.live_vic_src = u
                    self.emit(tgt.x, tgt.y, (140, 210, 255), 16, 50, 4, 0.4)
                    self.burst(tgt.x, tgt.y - 20, (180, 220, 255), 28, 0.3)
                    sfx("holy")
                self.start_cast(u, 3, _lv, cast=2.0)
                return
            if getattr(u, "vigorous_t", 0) <= 0 and u.ready("Vigorous Spirit"):
                u.use("Vigorous Spirit", 4)
                def _vs(u=u):
                    u.vigorous_t = 30
                    self.emit(u.x, u.y, (120, 210, 255), 10, 30, 3, 0.25)
                self.start_cast(u, 1, _vs, cast=0.25)
                return
            if u.flail_t <= 0 and u.ready("Flail"):
                u.use("Flail", 12)
                u.flail_t = 10
                sfx("sprint")
            if getattr(u, "hurt_t", 0) > 0 and u.ready("Ebon Battle Standard"):
                u.use("Ebon Battle Standard", 20)
                def _eb(u=u):
                    self.honor.append([u.x, u.y, u.team, 20.0])
                    self.burst(u.x, u.y, GOLD, 50, 0.4)
                    sfx("ward")
                self.start_cast(u, 2, _eb, cast=1.0)
                return
            if dist < 90 and u.ready("You Are All Weaklings"):
                u.use("You Are All Weaklings", 12)
                sfx("shout")
                self.burst(e.x, e.y, (180, 160, 80), 70, 0.35)
                for o in self.living(1 - u.team):
                    if o is e or math.hypot(o.x - e.x, o.y - e.y) < 80:
                        o.weakness_t = max(o.weakness_t, 12.0)
                return
            if dist < 70 and u.ready("Cyclone Axe"):
                u.use("Cyclone Axe", 4)
                sfx("bladestorm")
                self.burst(u.x, u.y, (200, 190, 140), 78, 0.35)
                for o in self.living(1 - u.team):
                    if math.hypot(o.x - u.x, o.y - u.y) < 72:
                        o.take(L_DMG[1] + 13, melee=True, source=u)
                        self.emit(o.x, o.y, (220, 200, 150), 8, 50, 3, 0.25)
                return
            if dist < 52 and u.ready("Triple Chop"):
                u.use("Triple Chop", 10)
                sfx("slash")
                hits = [e] + [o for o in self.living(1 - u.team) if o is not e and math.hypot(o.x - e.x, o.y - e.y) < 70]
                for o in hits:
                    o.take(L_DMG[1] + 42, melee=True, source=u)
                    self.emit(o.x, o.y, WHITE, 10, 60, 3, 0.25)
                return
            if dist < 52 and u.ready("Whirlwind Attack"):
                u.use("Whirlwind Attack", 1)
                sfx("slash")
                self.emit(e.x, e.y, WHITE, 18, 80, 5, 0.45)
                self.burst(e.x, e.y, (230, 230, 240), 40, 0.3)
                for o in self.living(1 - u.team):
                    if o is e or math.hypot(o.x - e.x, o.y - e.y) < 68:
                        o.take(L_DMG[1] + 20, melee=True, source=u)
                return
            if dist < 52 and u.ready("auto"):
                self.try_auto(u)

        elif u.cls == "PermaShadow":
            def smoke(u=u, nx=None, ny=None):
                self.emit(u.x, u.y, (20, 8, 28), 26, 80, 6, 0.5)
                self.burst(u.x, u.y, (30, 10, 40), 56, 0.4)
                if nx is not None:
                    u.x, u.y = nx, ny
                    self.clamp(u)
                    self.emit(u.x, u.y, (40, 16, 50), 22, 70, 5, 0.4)
                    self.burst(u.x, u.y, SHADOW, 40, 0.3)
            if getattr(u, "hold_t", 0) > 0 and not (e and e.hp / e.max_hp < 0.3 and dist < 52):
                return
            if u.paradox_t <= 0 and u.ready("Deadly Paradox"):
                u.use("Deadly Paradox", 10)
                u.paradox_t = 15
                u.attack_lock = 10
                self.emit(u.x, u.y, SHADOW, 12, 40, 3, 0.3)
                return
            if getattr(u, "shadow_form_t", 0) <= 0 and u.ready("Shadow Form"):
                u.use("Shadow Form", 20)
                def _sf(u=u):
                    u.shadow_form_t = 21
                    self.emit(u.x, u.y, (80, 30, 110), 18, 50, 5, 0.45)
                self.start_cast(u, 2, _sf, cast=0.8)
                return
            if u.hp < u.max_hp * 0.5 and getattr(u, "shroud_t", 0) <= 0 and u.ready("Shroud of Distress"):
                u.use("Shroud of Distress", 45)
                def _sd(u=u):
                    u.shroud_t = 60
                self.start_cast(u, 2, _sd, cast=1.0)
                return
            if u.hp < u.max_hp * 0.55 and u.ready("Feigned Neutrality"):
                u.use("Feigned Neutrality", 25)
                def _fn(u=u):
                    u.feign_t = 10
                    if random.random() < 0.66:
                        u.hold_t = 2.0
                self.start_cast(u, 1, _fn, cast=0.25)
                return
            if e and u.ready("Deaths Charge") and dist < 280:
                u.use("Deaths Charge", 30)
                def _dc(u=u, e=e):
                    smoke(u, e.x - 18, e.y)
                    if e.hp > u.hp:
                        u.heal(200, source=u)
                self.start_cast(u, 1, _dc, cast=0.25)
                return
            ally = self.neediest(u, 280)
            if ally and ally is not u and u.ready("Ebon Escape"):
                u.use("Ebon Escape", 10)
                def _ee(u=u, ally=ally):
                    smoke(u, ally.x + 16, ally.y)
                    u.heal(110, source=u)
                    ally.heal(110, source=u)
                self.start_cast(u, 1, _ee, cast=0.25)
                return
            if u.hp < u.max_hp * 0.7 and u.ready("Heart of Shadow"):
                u.use("Heart of Shadow", 15)
                def _hs(u=u, e=e):
                    if e:
                        d = math.hypot(e.x - u.x, e.y - u.y) or 1
                        smoke(u, u.x - (e.x - u.x) / d * 130, u.y - (e.y - u.y) / d * 130)
                    u.heal(150, source=u)
                self.start_cast(u, 1, _hs, cast=0.25)
                return
            if u.stride_t <= 0 and dist > 90 and u.ready("Natural Stride"):
                u.use("Natural Stride", 21)
                u.stride_t = 8
                return
            if e and dist < 52 and u.attack_lock <= 0 and u.ready("auto"):
                self.try_auto(u)

        elif u.cls == "Riposte":
            if getattr(u, "hold_t", 0) > 0:
                return
            if getattr(u, "hurt_t", 0) > 0 and u.ready("Ebon Battle Standard"):
                u.use("Ebon Battle Standard", 20)
                def _eb(u=u):
                    self.honor.append([u.x, u.y, u.team, 20.0])
                    self.burst(u.x, u.y, WHITE, 50, 0.4)
                self.start_cast(u, 2, _eb, cast=1.0)
                return
            if u.ttl_t <= 0 and u.ready("To the Limit"):
                u.use("To the Limit", 20)
                n = sum(1 for o in self.living(1 - u.team) if math.hypot(o.x - u.x, o.y - u.y) < 160)
                n = min(6, n)
                u.energy = min(u.max_energy, u.energy + n)
                u.ttl_t = 20
                u.max_hp += 60
                u.hp += 60
                self.burst(u.x, u.y, WHITE, 80, 0.35)
                sfx("shout")
                return
            if u.dolyak_t <= 0 and u.ready("Dolyak Signet") and len(getattr(u, "dmg_log", []) or []) >= 3:
                u.use("Dolyak Signet", 20)
                u.dolyak_t = 20
                self.emit(u.x, u.y, WHITE, 12, 30, 3, 0.3)
                return
            if u.riposte_t <= 0 and u.ready("Riposte"):
                u.use("Riposte", 10)
                u.riposte_t = 8
                self.emit(u.x, u.y, WHITE, 10, 40, 3, 0.25)
                return
            if u.soldier_t <= 0 and u.ttl_t > 0 and u.ready("Soldiers Defense"):
                u.use("Soldiers Defense", 15)
                u.soldier_t = 6
                return
            if u.glad_t <= 0 and u.ready("Gladiators Defense"):
                u.use("Gladiators Defense", 20)
                u.glad_t = 11
                self.emit(u.x, u.y, WHITE, 14, 40, 4, 0.3)
                return
            if getattr(u, "shield_st_t", 0) <= 0 and u.ready("Shield Stance"):
                u.use("Shield Stance", 15)
                u.shield_st_t = 6
                u.shield_ch = 8
                return
            if u.bonetti_t <= 0 and u.ready("Bonettis Defense"):
                u.use("Bonettis Defense", 12)
                u.bonetti_t = 11
                u.hold_t = 2.0
                return
            if e and dist < 52 and u.ready("auto"):
                self.try_auto(u)

        elif u.cls == "Warrior":
            if u.hp < 50 and u.ready("Shield Block"):
                u.use("Shield Block", 7)
                sfx("block")
                u.block_t = 2.2
            if dist > 80 and dist < 220 and u.ready("Charge"):
                u.use("Charge", 8)
                sfx("charge")
                u.x += (dx / dist) * min(160, dist - 20)
                u.y += (dy / dist) * min(160, dist - 20)
                self.clamp(u)
                e.take(L_DMG[2], melee=True, source=u)
                self.give_cc(e, "stun", 0.4, u)
            if dist < 55 and u.ready("Hamstring"):
                u.use("Hamstring", 6)
                sfx("hamstring")
                e.slow_t = max(e.slow_t, 2.5)
                e.take(L_DMG[2], melee=True, source=u)
            if dist < 140 and u.ready("Fus Ro Dah"):
                u.use("Fus Ro Dah", 12)
                sfx("shout")
                self.burst(u.x, u.y, (220, 200, 160), 140, 0.4)
                self.emit(u.x, u.y, (230, 210, 170), 30, 200, 5, 0.4)
                for o in self.living(1 - u.team):
                    if self.in_front(u, o, 150, 0.4):
                        o.fear_t = max(o.fear_t, 1.6)
                        ox, oy = o.x - u.x, o.y - u.y
                        od = math.hypot(ox, oy) or 1
                        o.x += ox / od * 80
                        o.y += oy / od * 80
                        self.clamp(o)
                        o.take(L_DMG[2])
            if dist < 70 and u.ready("Bladestorm"):
                u.use("Bladestorm", 14)
                sfx("bladestorm")
                u.storm_t = 2.4
            if dist < 50 and u.ready("Slash"):
                u.use("Slash", 1.4)
                sfx("slash", 0.2)
                fx, fy = math.cos(u.facing), math.sin(u.facing)
                for _ in range(6):
                    ang = u.facing + random.uniform(-0.7, 0.7)
                    self.particles.append(Particle(u.x + fx * 12, u.y + fy * 12, math.cos(ang) * 140, math.sin(ang) * 140, 0.2, 0.2, (230, 230, 240), 3))
                for o in self.living(1 - u.team):
                    if self.in_front(u, o, 52, 0.35):
                        o.take(L_DMG[3])

        elif u.cls == "Slasher":
            self.refresh_rez(u)
            fallen = [a for a in self.units if a.team == u.team and not a.alive and not a.is_pet and not getattr(a, "is_spirit", False)]
            if fallen and u.rez_ready and u.ready("Resurrection Signet"):
                u.use("Resurrection Signet", 99)
                u.rez_ready = False
                u.enemy_deaths_at_rez = self.morale[1 - u.team]
                u.channel = "rez_sig"
                u.channel_t = 2.6
                u.channel_target = fallen[0]
                sfx("spirit")
                return
            if u.hp / u.max_hp < 0.4 and u.ready("Healing Signet"):
                u.use("Healing Signet", 8)
                u.channel = "heal_sig"
                u.channel_t = 1.8
                sfx("holy")
                return
            if u.illusion_t <= 0 and u.ready("Illusionary Weaponry"):
                u.use("Illusionary Weaponry", 20)
                u.illusion_t = 30
                u.extra_armor = 1
                self.emit(u.x, u.y, GLASS, 16, 50, 4, 0.4)
                sfx("glass")
            if u.flurry_t <= 0 and u.ready("Flurry"):
                u.use("Flurry", 8)
                u.flurry_t = 5
            if u.distortion_t <= 0 and u.hp < 70 and u.ready("Distortion"):
                u.use("Distortion", 10)
                u.distortion_t = 5
                self.burst(u.x, u.y, GLASS, 36, 0.3)
            if u.riposte_t <= 0 and u.ready("Deadly Riposte"):
                u.use("Deadly Riposte", 10)
                u.riposte_t = 8
            if u.deflect_t <= 0 and u.ready("Deflect Arrow"):
                u.use("Deflect Arrow", 10)
                u.deflect_t = 5
            ally = self.neediest(u)
            if ally and ally.visage_t <= 0 and u.ready("Sympathetic Visage"):
                u.use("Sympathetic Visage", 12)
                ally.visage_t = 10
                self.emit(ally.x, ally.y, GLASS, 10, 30, 3, 0.35)
            if dist < 48 and u.ready("cut"):
                u.use("cut", 1.15 if u.flurry_t <= 0 else 0.85)
                sfx("slash", 0.15)
                self.melee_attack(u, e, L_DMG[2])
        elif u.cls == "Seeping":
            self.refresh_rez(u)
            fallen = [a for a in self.units if a.team == u.team and not a.alive and not a.is_pet and not getattr(a, "is_spirit", False)]
            if fallen and u.rez_ready and u.ready("Resurrection Signet"):
                u.use("Resurrection Signet", 99)
                u.rez_ready = False
                u.enemy_deaths_at_rez = self.morale[1 - u.team]
                u.channel = "rez_sig"
                u.channel_t = 2.6
                u.channel_target = fallen[0]
                sfx("spirit")
                return
            if u.master_t <= 0 and u.ready("Way of the Master"):
                u.use("Way of the Master", 30)
                u.master_t = 60
                self.emit(u.x, u.y, GOLD, 10, 30, 3, 0.35)
            if u.crit_eye_t <= 0 and u.ready("Critical Eye"):
                u.use("Critical Eye", 20)
                u.crit_eye_t = 33
            if u.haste_t <= 0 and u.ready("Deadly Haste"):
                u.use("Deadly Haste", 22)
                u.haste_t = 33
                self.emit(u.x, u.y, ORANGE, 12, 40, 3, 0.35)
            cond = e and (e.bleed > 0 or e.slow_t > 0 or e.stun_t > 0 or e.barbed_t > 0 or e.deepwound_t > 0 or e.curse_t > 0)
            if e and dist < 140 and u.ready("Seeping Wound"):
                u.use("Seeping Wound", 6)
                sfx("curse")
                def _seep(e=e):
                    e.seeping_t = 7
                    e.seeping_tick = 1
                    e.slow_t = max(e.slow_t, 7)
                    self.emit(e.x, e.y, (180, 40, 40), 12, 40, 3, 0.35)
                self.start_cast(u, 2, _seep)
                return
            if e and dist < 280 and u.ready("Barbed Spear"):
                u.use("Barbed Spear", 4)
                self.start_cast(u, 2, lambda u=u: self.fire(u, "spear", L_DMG[2], 400, 1.1))
                return
            if e and dist < 280 and u.ready("Vicious Attack"):
                u.use("Vicious Attack", 5)
                chance = 0.08 + (0.14 if u.crit_eye_t > 0 else 0) + (0.31 if u.master_t > 0 else 0)
                crit = random.random() < chance
                extra = 17 if True else 0
                def _vic(u=u, crit=crit):
                    self.fire(u, "vicious", L_DMG[3] + 17, 420, 1.1)
                    if self.projs:
                        self.projs[-1].crit = crit
                self.start_cast(u, 3, _vic)
                return
        elif u.cls == "Elementalist":
            if u.fire_attune_t <= 0 and u.ready("Fire Attunement"):
                u.use("Fire Attunement", L_CD[1])
                u.fire_attune_t = 60
                sfx("blast")
                self.emit(u.x, u.y, FIRE, 18, 50, 4, 0.45)
            if u.mystic_t <= 0 and u.ready("Mystic Regeneration"):
                u.use("Mystic Regeneration", L_CD[2])
                u.mystic_t = 13
                sfx("holy")
            if e and dist < 360 and u.ready("Rodgorts Invocation"):
                u.use("Rodgorts Invocation", L_CD[3])
                sfx("blast")
                def _rod(e=e, u=u):
                    self.burst(e.x, e.y, FIRE, 90, 0.5)
                    self.emit(e.x, e.y, FIRE, 28, 120, 5, 0.5)
                    for o in self.living(1 - u.team):
                        if math.hypot(o.x - e.x, o.y - e.y) < 88:
                            o.take(120, source=u)
                            o.burn_t = max(o.burn_t, 3.0)
                            o.burn_tick = 1.0
                self.start_cast(u, 3, _rod)
                return
            if e and dist < 360 and u.ready("Flame Djinns Haste"):
                u.use("Flame Djinns Haste", L_CD[4])
                def _dj(u=u, e=e):
                    self.fire(u, "phoenix", 120, 440, 1.2)
                    hit = any(math.hypot(o.x - e.x, o.y - e.y) < 90 for o in self.living(1 - u.team))
                    u.djinn_t = 14
                    if hit:
                        u.cds["Flame Djinns Haste"] *= 0.5
                    self.emit(u.x, u.y, FIRE, 16, 70, 4, 0.4)
                self.start_cast(u, 4, _dj)
                return
            if e and dist < 360 and u.ready("Immolate"):
                u.use("Immolate", L_CD[2])
                def _im(e=e, u=u):
                    e.take(75, source=u)
                    e.burn_t = max(e.burn_t, 3.0)
                    e.burn_tick = 1.0
                    self.emit(e.x, e.y, FIRE, 18, 80, 4, 0.45)
                    self.burst(e.x, e.y, FIRE, 36, 0.3)
                self.start_cast(u, 2, _im)
                return
            if e and dist < 360 and u.ready("Mind Blast"):
                u.use("Mind Blast", L_CD[2])
                def _mb(e=e, u=u):
                    e.take(60, source=u)
                    self.emit(e.x, e.y, FIRE, 14, 70, 4, 0.35)
                    if u.energy > e.energy:
                        u.energy = min(u.max_energy, u.energy + 8)
                self.start_cast(u, 2, _mb)
                return
            if e and dist < 340 and u.ready("Blinding Flash"):
                u.use("Blinding Flash", L_CD[2])
                def _bf(e=e):
                    e.blind_t = max(e.blind_t, 6.0)
                    self.burst(e.x, e.y, (255, 255, 210), 50, 0.4)
                    self.emit(e.x, e.y, WHITE, 20, 90, 4, 0.4)
                self.start_cast(u, 2, _bf)
                return
            if e and dist < 300 and u.ready("Gale"):
                u.use("Gale", L_CD[3])
                def _gale(e=e, u=u):
                    if random.random() < 0.5:
                        self.emit(e.x, e.y, MUTED, 8, 30, 3, 0.25)
                        return
                    self.give_cc(e, "kd", 2.0, u)
                    self.emit(e.x, e.y, ICE, 16, 80, 4, 0.35)
                self.start_cast(u, 3, _gale)
                return
            if e and dist < BODY * 8 and u.ready("auto"):
                self.fire(u, "fire", L_DMG[1], 320, 1.1)
                u.use("auto", 1.15)
        
        elif u.cls == "Double Dragon":
            if u.fire_attune_t <= 0 and u.ready("Fire Attunement"):
                u.use("Fire Attunement", 15)
                u.fire_attune_t = 60
                self.emit(u.x, u.y, FIRE, 18, 50, 4, 0.45)
                return
            ally_near = min(
                (a for a in self.living(u.team) if a is not u and not a.is_pet and not getattr(a, "is_spirit", False)),
                key=lambda a: math.hypot(a.x - u.x, a.y - u.y),
                default=None
            )
            if ally_near and getattr(ally_near, "haste_sh_t", 0) <= 0 and u.ready("Make Haste"):
                if math.hypot(ally_near.x - u.x, ally_near.y - u.y) < 200:
                    u.use("Make Haste", 10)
                    ally_near.haste_sh_t = 14
                    self.burst(u.x, u.y, GOLD, 50, 0.3)
                    ally_near.heal(32, source=u)
                    return
            if e and math.hypot(e.x - u.x, e.y - u.y) < 90 and u.ready("Return"):
                best = max(
                    (a for a in self.living(u.team) if a is not u and not a.is_pet and not getattr(a, "is_spirit", False)),
                    key=lambda a: min((math.hypot(a.x - o.x, a.y - o.y) for o in self.living(1 - u.team)), default=0),
                    default=None
                )
                if best:
                    u.use("Return", 12)
                    def _ret(u=u, best=best):
                        for o in self.living(1 - u.team):
                            if math.hypot(o.x - u.x, o.y - u.y) < 80:
                                o.slow_t = max(o.slow_t, 5.0)
                        self.emit(u.x, u.y, SHADOW, 16, 50, 4, 0.35)
                        u.x, u.y = best.x + 14, best.y
                        self.clamp(u)
                        self.emit(u.x, u.y, FIRE, 18, 60, 4, 0.4)
                        sfx("blast", 0.1)
                    self.start_cast(u, 1, _ret, cast=0.25)
                    return
            if e and dist < 320 and u.ready("Double Dragon"):
                u.use("Double Dragon", 15)
                def _dd(u=u, e=e):
                    ang = math.atan2(e.y - u.y, e.x - u.x)
                    for offset in (-0.18, 0.18):
                        self.projs.append(Projectile(
                            u.x, u.y,
                            math.cos(ang + offset), math.sin(ang + offset),
                            400, 130, u.team, "phoenix", 1.2, 10, 3, [], u
                        ))
                    self.burst(u.x, u.y, FIRE, 60, 0.45)
                    self.emit(u.x, u.y, FIRE, 24, 100, 5, 0.5)
                    sfx("blast")
                self.start_cast(u, 4, _dd)
                return
            if e and dist < 360 and u.ready("Rain of Fire"):
                u.use("Rain of Fire", 12)
                u.channel = "rain"
                u.channel_t = 3.0
                u.channel_acc = 0
                u.rain_n = 0
                u.channel_target = e
                return
            if e and dist < 360 and u.ready("Rodgorts Invocation"):
                u.use("Rodgorts Invocation", 10)
                def _rod(e=e, u=u):
                    self.burst(e.x, e.y, FIRE, 90, 0.5)
                    self.emit(e.x, e.y, FIRE, 28, 120, 5, 0.5)
                    for o in self.living(1 - u.team):
                        if math.hypot(o.x - e.x, o.y - e.y) < 88:
                            o.take(120, source=u)
                            o.burn_t = max(o.burn_t, 3.0)
                            o.burn_tick = 1.0
                self.start_cast(u, 3, _rod)
                return
            if e and dist < 360 and u.ready("Immolate"):
                u.use("Immolate", 7)
                def _im(e=e, u=u):
                    e.take(75, source=u)
                    e.burn_t = max(e.burn_t, 3.0)
                    e.burn_tick = 1.0
                    self.emit(e.x, e.y, FIRE, 18, 80, 4, 0.45)
                    self.burst(e.x, e.y, FIRE, 36, 0.3)
                self.start_cast(u, 2, _im)
                return
            if e and dist < BODY * 8 and u.ready("auto"):
                self.fire(u, "fire", L_DMG[1], 320, 1.1)
                u.use("auto", 1.15)

        elif u.cls == "Lingwah":
            reach = BODY * 8
            ally = self.neediest(u, reach + 20) or u
            ad = math.hypot(ally.x - u.x, ally.y - u.y)
            if getattr(ally, "xinrae_t", 0) <= 0 and u.ready("Xinraes Weapon") and ad <= reach:
                u.use("Xinraes Weapon", 3)
                def _xw(u=u, ally=ally):
                    ally.xinrae_t = self.apply_ench_dur(u, 12)
                    ally.xinrae_src = u
                    self.emit(ally.x, ally.y, (80, 140, 255), 16, 50, 4, 0.4)
                    self.burst(ally.x, ally.y, (60, 120, 255), 34, 0.3)
                    sfx("holy", 0.1)
                self.start_cast(u, 1, _xw, cast=0.25)
                return


        elif u.cls == "Stoning":
            self.refresh_rez(u)
            fallen = [a for a in self.units if a.team == u.team and not a.alive and not a.is_pet and not getattr(a, "is_spirit", False)]
            if fallen and u.rez_ready and u.ready("Resurrection Signet"):
                u.use("Resurrection Signet", 99)
                u.rez_ready = False
                u.enemy_deaths_at_rez = self.morale[1 - u.team]
                u.channel = "rez_sig"
                u.channel_t = 2.1
                u.channel_target = fallen[0]
                sfx("spirit")
                return
            if u.earth_attune_t <= 0 and u.ready("Earth Attunement"):
                u.use("Earth Attunement", 30)
                def _ea(u=u):
                    u.earth_attune_t = 55
                    self.emit(u.x, u.y, (140, 120, 80), 16, 40, 4, 0.4)
                self.start_cast(u, 2, _ea, cast=1.0)
                return
            if u.lyssa_t <= 0 and u.ready("Lyssas Aura"):
                u.use("Lyssas Aura", 30)
                def _ly(u=u):
                    u.lyssa_t = 10
                    self.emit(u.x, u.y, HOLY, 12, 30, 3, 0.4)
                self.start_cast(u, 1, _ly, cast=0.6)
                return
            if u.kinetic_t <= 0 and u.ready("Kinetic Armor"):
                u.use("Kinetic Armor", 30)
                def _ka(u=u):
                    u.kinetic_t = 12
                    self.burst(u.x, u.y, (180, 210, 255), 40, 0.35)
                self.start_cast(u, 3, _ka, cast=1.9)
                return
            if e and dist < 200 and u.ready("Ash Blast"):
                u.use("Ash Blast", 10)
                def _ab(e=e, u=u):
                    self.burst(e.x, e.y, (90, 80, 70), 70, 0.35)
                    for o in self.living(1 - u.team):
                        if math.hypot(o.x - e.x, o.y - e.y) < 70:
                            o.take(59, source=u)
                            if o.burn_t > 0:
                                o.ash_t = 5.0
                                o.blind_t = max(o.blind_t, 0.2)
                    sfx("stone")
                self.start_cast(u, 2, _ab, cast=1.0)
                return
            if e and dist < 360 and u.ready("Stoning"):
                u.use("Stoning", 5)
                self.start_cast(u, 2, lambda u=u: self.fire(u, "stone", 93, 340, 1.15), cast=1.0)
                return
            if e and dist < 360 and u.ready("Ebon Hawk"):
                u.use("Ebon Hawk", 5)
                self.start_cast(u, 2, lambda u=u: self.fire(u, "hawk", 70, 380, 1.15), cast=1.0)
                return
        elif u.cls == "Ranger":
            if u.channel:
                return
            self.refresh_rez(u)
            fallen = [a for a in self.units if a.team == u.team and not a.alive and not a.is_pet and not getattr(a, "is_spirit", False)]
            if fallen and u.rez_ready and u.ready("Resurrection Signet") and dist > 90:
                u.use("Resurrection Signet", 99)
                u.rez_ready = False
                u.enemy_deaths_at_rez = self.morale[1 - u.team]
                u.channel, u.channel_t, u.channel_target = "rez_sig", 2.2, fallen[0]
                return
            ally = self.neediest(u, 200)
            if ally:
                condi = [a for a in ("slow_t", "stun_t", "curse_t", "poison_t", "daze_t", "bleed", "blur_t", "antiheal_t") if getattr(ally, a, 0) > 0]
                ad = math.hypot(ally.x - u.x, ally.y - u.y)
                if condi and u.ready("Mending Touch"):
                    if ad > 70:
                        u.target = ((ally.x - u.x) / (ad or 1), (ally.y - u.y) / (ad or 1))
                    if ad <= 80:
                        u.use("Mending Touch", 6)
                        n = 0
                        for attr in condi[:2]:
                            n += 1
                            if attr == "bleed":
                                ally.bleed = 0
                            else:
                                setattr(ally, attr, 0.0)
                        ally.heal(24 * n, source=u)
                        self.emit(ally.x, ally.y, (160, 230, 160), 12, 40, 3, 0.35)
                        return
            if u.poison_prep_t <= 0 and u.ready("Apply Poison"):
                u.use("Apply Poison", 12)
                def _pp(u=u):
                    u.poison_prep_t = 24
                    self.emit(u.x, u.y, POISON, 16, 40, 4, 0.4)
                self.start_cast(u, 3, _pp, cast=2.0)
                return
            if u.stride_t <= 0 and dist > 160 and dist < 280 and u.ready("Natural Stride"):
                u.use("Natural Stride", 12)
                u.stride_t = 6
                self.emit(u.x, u.y, (120, 200, 90), 10, 50, 3, 0.3)
            casters = [o for o in self.living(1 - u.team) if o.channel and math.hypot(o.x - u.x, o.y - u.y) < AUTO_RANGE["ranged"] + 40]
            mark = min(casters, key=lambda o: (o.x - u.x) ** 2 + (o.y - u.y) ** 2) if casters else e
            bow = AUTO_RANGE["ranged"]
            if mark:
                md = math.hypot(mark.x - u.x, mark.y - u.y)
                u.facing = math.atan2(mark.y - u.y, mark.x - u.x)
                if mark.channel and u.ready("Distracting Shot") and md <= bow:
                    u.use("Distracting Shot", 10)
                    self.start_cast(u, 2, lambda u=u: self.fire(u, "distract", 16, 420, 1.15), cast=0.5)
                    return
                if u.ready("Savage Shot") and md <= bow:
                    u.use("Savage Shot", 5)
                    self.start_cast(u, 2, lambda u=u: self.fire(u, "savage", L_DMG[2], 420, 1.1), cast=0.5)
                    return
                if u.ready("Broad Head Arrow") and md <= bow:
                    u.use("Broad Head Arrow", 10)
                    self.start_cast(u, 2, lambda u=u: self.fire(u, "broad", L_DMG[2], 210, 1.6), cast=0.4)
                    return
            if e and dist < BODY * 8 and u.ready("auto"):
                u.facing = math.atan2(e.y - u.y, e.x - u.x)
                u.use("auto", 1.0)
                self.fire(u, "rarrow", L_DMG[1], 360, 1.1)
        elif u.cls == "Balthazar":
            self.refresh_rez(u)
            fallen = [a for a in self.units if a.team == u.team and not a.alive and not a.is_pet and not getattr(a, "is_spirit", False)]
            if fallen and u.energy >= 0 and u.rez_ready and u.ready("Resurrection Signet") and dist > 80:
                u.use("Resurrection Signet", 99)
                u.rez_ready = False
                u.enemy_deaths_at_rez = self.morale[1 - u.team]
                u.channel = "rez_sig"
                u.channel_t = 2.1
                u.channel_target = fallen[0]
                return
            if u.fury_t <= 0 and u.ready("Heart of Fury") and dist < 70:
                u.use("Heart of Fury", 10)
                u.fury_t = 7
            if u.harrier_t <= 0 and u.ready("Harriers Haste") and 80 < dist < 220:
                u.use("Harriers Haste", 10)
                u.harrier_t = 6
            if u.grasp_t <= 0 and u.ready("Harriers Grasp"):
                u.use("Harriers Grasp", 15)
                u.grasp_t = 16
                u.grasp_n = 0
            if u.avatar_t <= 0 and u.avatar_lock <= 0 and u.energy >= 5 and u.ready("Avatar of Balthazar") and dist < 70:
                u.use("Avatar of Balthazar", 20)
                def _av(u=u):
                    u.avatar_t = 63
                    u.avatar_lock = 45
                    self.burst(u.x, u.y, GOLD, 50, 0.45)
                    sfx("holy")
                self.start_cast(u, 3, _av, cast=2.0)
                return
            enchanted = u.grasp_t > 0 or u.harrier_t > 0 or u.avatar_t > 0
            if e and dist < 56 and u.slicer_ch >= 6 and u.ready("Aura Slicer"):
                u.use("Aura Slicer", 4)
                u.slicer_ch = 0
                e.take(L_DMG[3], melee=True, source=u)
                e.bleed = min(8, e.bleed + 2)
                e.bleed_tick = 1
                if enchanted:
                    e.cracked_t = max(e.cracked_t, 7)
                self.emit(e.x, e.y, (40, 180, 255), 14, 90, 4, 0.3)
                return
            if e and dist < 54 and e.bleed > 0 and u.ready("Gash"):
                u.use("Gash", 6)
                e.take(L_DMG[3] + 17, melee=True, source=u)
                if not e.base_max:
                    e.base_max = e.max_hp
                e.deepwound_t = 17
                e.max_hp = e.base_max * 0.8
                e.hp = min(e.hp, e.max_hp)
                return
            if e and dist < 54 and u.ready("Sun and Moon Slash"):
                u.use("Sun and Moon Slash", 8)
                e.take(L_DMG[2], melee=True, source=u, unblockable=True)
                e.take(L_DMG[2], melee=True, source=u, unblockable=True)
                self.emit(e.x, e.y, GOLD, 12, 50, 3, 0.3)
                return
            if e and dist < 58 and u.ready("auto"):
                cd = 0.85 if u.fury_t <= 0 else 0.62
                u.use("auto", cd)
                e.take(L_DMG[2], melee=True, source=u)
                u.slicer_ch = min(6, u.slicer_ch + 1)
                sfx("slash", 0.12)
        elif u.cls == "Deathdancer":
            if getattr(u, "soul_reset", 0) > 0:
                pass
            if u.attack_lock > 0 and not u.ready("Dancing Daggers"):
                pass
            self.refresh_rez(u)
            fallen = [a for a in self.units if a.team == u.team and not a.alive and not a.is_pet and not getattr(a, "is_spirit", False)]
            if fallen and u.rez_ready and u.ready("Resurrection Signet") and dist > 70:
                u.use("Resurrection Signet", 99)
                u.rez_ready = False
                u.enemy_deaths_at_rez = self.morale[1 - u.team]
                u.channel, u.channel_t, u.channel_target = "rez_sig", 2.2, fallen[0]
                return
            if u.paradox_t <= 0 and u.ready("Deadly Paradox"):
                u.use("Deadly Paradox", 10)
                u.paradox_t = 13
                u.attack_lock = 10
                self.nec_flash(u, u)
            if e and e.hp / e.max_hp < 0.5 and u.ready("Signet of Lost Souls") and dist < 70:
                u.use("Signet of Lost Souls", 8)
                def _ls(u=u):
                    u.heal(94)
                    u.energy = min(u.max_energy, u.energy + 9)
                    self.nec_flash(u, e)
                self.start_cast(u, 1, _ls, cast=0.25)
                return
            if e and e.poison_t > 0 and u.ready("Signet of Toxic Shock") and dist < 60:
                u.use("Signet of Toxic Shock", 15)
                def _ts(u=u, e=e):
                    e.take(82, source=u)
                    self.nec_flash(u, e)
                self.start_cast(u, 2, _ts, cast=1.0)
                return
            if e and u.lead_atk and u.attack_lock <= 0 and u.ready("Entangling Asp") and dist < 58:
                u.use("Entangling Asp", 20)
                u.lead_atk = False
                def _ea(u=u, e=e):
                    self.give_cc(e, "kd", 1.4, u)
                    e.poison_t = max(e.poison_t, 17)
                    e.poison_tick = 2
                    self.nec_flash(u, e)
                self.start_cast(u, 2, _ea, cast=1.0)
                return
            if e and getattr(e, "augury_t", 0) <= 0 and u.ready("Augury of Death") and dist < 140:
                u.use("Augury of Death", 20)
                def _ag(u=u, e=e):
                    e.augury_t = 29
                    e.augury_src = u
                    self.nec_flash(u, e)
                self.start_cast(u, 2, _ag, cast=1.0)
                return
            if e and getattr(e, "reaper_t", 0) <= 0 and u.ready("Reapers Mark") and dist < 260:
                u.use("Reapers Mark", 15)
                def _rm(u=u, e=e):
                    e.reaper_t = 30
                    e.reaper_src = u
                    self.nec_flash(u, e)
                self.start_cast(u, 2, _rm, cast=1.0)
                return
            if e and dist > 64 and dist <= AUTO_RANGE["ranged"] and u.ready("Shadow Step"):
                u.use("Shadow Step", 8)
                def _ss(u=u, e=e):
                    nx = e.x - math.cos(math.atan2(e.y - u.y, e.x - u.x)) * 28
                    ny = e.y - math.sin(math.atan2(e.y - u.y, e.x - u.x)) * 28
                    self.emit(u.x, u.y, (40, 80, 50), 14, 40, 4, 0.3)
                    u.x, u.y = nx, ny
                    self.clamp(u)
                    self.emit(u.x, u.y, (60, 120, 70), 16, 50, 4, 0.3)
                    self.tethers.append(Tether(type("P", (), {"x": nx, "y": ny, "alive": True})(), e, 0.2, (70, 110, 60)))
                    sfx("blink")
                self.start_cast(u, 1, _ss, cast=0.25)
                return
            if e and u.attack_lock <= 0 and u.ready("Dancing Daggers") and dist < 150:
                u.use("Dancing Daggers", 5)
                def _dd(u=u, e=e):
                    u.lead_atk = True
                    for i in range(3):
                        ang = u.facing + (i - 1) * 0.28
                        self.projs.append(Projectile(u.x, u.y, math.cos(ang), math.sin(ang), 280, 29, u.team, "dagger", 0.9, 5, 4, [], u))
                    self.nec_flash(u, e)
                self.start_cast(u, 2, _dd, cast=1.0)
                return
            if e and dist < 90 and u.attack_lock <= 0 and u.ready("auto"):
                u.use("auto", 0.9)
                fx, fy = math.cos(u.facing), math.sin(u.facing)
                for o in self.living(1 - u.team):
                    ox, oy = o.x - u.x, o.y - u.y
                    along = ox * fx + oy * fy
                    perp = abs(ox * fy - oy * fx)
                    if 0 < along < 88 and perp < 22:
                        o.take(L_DMG[1], melee=True, source=u)
                self.nec_flash(u, e)

        elif u.cls == "Mesmer":
            PINK = (220, 90, 200)
            if not e:
                e = self.nearest(u)
            if not e:
                return
            def flash(a=None):
                self.emit(u.x, u.y, PINK, 14, 50, 4, 0.35)
                self.burst(u.x, u.y, (160, 70, 180), 26, 0.22)
                if a:
                    self.emit(a.x, a.y, PINK, 12, 45, 3, 0.3)
                    self.tethers.append(Tether(u, a, 0.35, PINK))
                sfx("curse", 0.1)
            ENCH = ("reversal_t", "favor_t", "water_armor_t", "illusion_t", "haste_t", "master_t", "mystic_t", "fire_attune_t", "earth_attune_t", "kinetic_t", "holy_veil_t", "spirit_bond_t", "shield_regen_t", "ward_wep_t", "djinn_t", "grasp_t", "harrier_t")
            if e.channel and u.ready("Power Drain") and dist < 280:
                u.use("Power Drain", 20)
                def _pd(u=u, e=e):
                    if e.channel:
                        self.interrupt_cast(e, "leak")
                        u.energy = min(u.max_energy, u.energy + 19)
                    flash(e)
                self.start_cast(u, 1, _pd, cast=0.2)
                return
            if e.channel and u.ready("Power Leak") and dist < 280:
                u.use("Power Leak", 20)
                def _pl(u=u, e=e):
                    if e.channel:
                        self.interrupt_cast(e, "leak")
                        e.energy = max(0.0, e.energy - 16)
                    flash(e)
                self.start_cast(u, 1, _pl, cast=0.2)
                return
            if any(getattr(e, a, 0) > 0 for a in ENCH) and u.ready("Shatter Enchantment") and dist < 280:
                u.use("Shatter Enchantment", 20)
                def _sh(u=u, e=e):
                    stripped = False
                    for a in ENCH:
                        if getattr(e, a, 0) > 0:
                            setattr(e, a, 0.0)
                            stripped = True
                            break
                    if stripped:
                        e.take(94, source=u)
                    flash(e)
                self.start_cast(u, 2, _sh, cast=0.7)
                return
            if any(getattr(e, a, 0) > 0 for a in ENCH) and u.ready("Drain Enchantment") and dist < 280:
                u.use("Drain Enchantment", 20)
                def _de(u=u, e=e):
                    stripped = False
                    for a in ENCH:
                        if getattr(e, a, 0) > 0:
                            setattr(e, a, 0.0)
                            stripped = True
                            break
                    if stripped:
                        u.energy = min(u.max_energy, u.energy + 13)
                        u.heal(88)
                    flash(e)
                self.start_cast(u, 2, _de, cast=1.3)
                return
            hex_opts = []
            if getattr(e, "diversion_t", 0) <= 0:
                hex_opts.append("Diversion")
            if getattr(e, "insec_t", 0) <= 0:
                hex_opts.append("Mark of Insecurity")
            if getattr(e, "wastrel_t", 0) <= 0:
                hex_opts.append("Wastrels Worry")
            hx = self.pick_ready(u, hex_opts) if dist < 280 else None
            if hx == "Diversion":
                u.use("Diversion", 12)
                def _dv(u=u, e=e):
                    e.diversion_t = 6
                    flash(e)
                self.start_cast(u, 3, _dv, cast=2.0)
                return
            if hx == "Mark of Insecurity":
                u.use("Mark of Insecurity", 10)
                def _mk(u=u, e=e):
                    e.insec_t = 14
                    names = [s[0] for s in SKILLS.get(e.cls, [])]
                    random.shuffle(names)
                    for s in names[:4]:
                        e.cds[s] = max(e.cds.get(s, 0), 6.0)
                    flash(e)
                self.start_cast(u, 2, _mk, cast=1.0)
                return
            if hx == "Wastrels Worry" or (getattr(e, "wastrel_t", 0) <= 0 and u.ready("Wastrels Worry") and dist < 280):
                u.use("Wastrels Worry", 4)
                def _ww(u=u, e=e):
                    e.wastrel_t = 3
                    e.wastrel_on = True
                    flash(e)
                self.start_cast(u, 1, _ww, cast=0.2)
                return
            if dist < BODY * 8 and u.ready("auto"):
                u.facing = math.atan2(e.y - u.y, e.x - u.x)
                u.use("auto", 1.15)
                self.fire(u, "glass", L_DMG[1], 320, 1.1)
                flash()
                return
            if not u.rez_ready:
                self.refresh_rez(u)
            fallen = [a for a in self.units if a.team == u.team and not a.alive and not a.is_pet and not getattr(a, "is_spirit", False)]
            if fallen and u.rez_ready and u.ready("Resurrection Signet") and getattr(u, "post_rez", 0) <= 0:
                u.use("Resurrection Signet", 99)
                u.rez_ready = False
                u.post_rez = 8
                u.enemy_deaths_at_rez = self.morale[1 - u.team]
                u.channel, u.channel_t, u.channel_max, u.channel_target = "rez_sig", 2.2, 2.2, fallen[0]
                return
        elif u.cls == "Migraine":
            PINK = (220, 80, 190)
            CLOSE = AUTO_RANGE["caster"]
            fallen = [a for a in self.units if a.team == u.team and not a.alive and not a.is_pet and not getattr(a, "is_spirit", False) and a.cls in CLASSES]
            if fallen and u.hp > u.max_hp * 0.35 and u.ready("Flesh of My Flesh"):
                u.use("Flesh of My Flesh", 12)
                u.channel = "flesh"
                u.channel_t = 2.9
                u.channel_max = 2.9
                u.channel_target = fallen[0]
                sfx("rez")
                return
            if e.channel and dist <= CLOSE and u.ready("Power Spike"):
                if random.random() < 0.25:
                    u.use("Power Spike", 12)
                    self.emit(e.x, e.y - 18, PINK, 8, 40, 3, 0.2)
                else:
                    u.use("Power Spike", 12)
                    def _ps(u=u, e=e):
                        if e.channel:
                            self.interrupt_cast(e, "spike")
                            e.take(72, source=u)
                        self.burst(e.x, e.y - 16, PINK, 22, 0.2)
                        self.emit(e.x, e.y - 16, (240, 120, 200), 12, 70, 4, 0.25)
                    self.start_cast(u, 1, _ps, cast=0.2)
                    return
            if e.channel and dist <= CLOSE and u.ready("Power Drain"):
                if random.random() >= 0.25:
                    u.use("Power Drain", 20)
                    def _pd(u=u, e=e):
                        if e.channel:
                            self.interrupt_cast(e, "drain")
                            u.energy = min(u.max_energy, u.energy + 23)
                        self.emit(e.x, e.y, PINK, 10, 50, 3, 0.25)
                        self.tethers.append(Tether(e, u, 0.3, PINK))
                    self.start_cast(u, 1, _pd, cast=0.2)
                    return
                u.use("Power Drain", 20)
            if e.channel and u.ready("Cry of Frustration"):
                u.use("Cry of Frustration", 20)
                def _cf(u=u, e=e):
                    for o in self.living(1 - u.team):
                        if o is e or math.hypot(o.x - e.x, o.y - e.y) < 90:
                            if o.channel:
                                self.interrupt_cast(o, "cry")
                            o.take(43, source=u)
                            self.emit(o.x, o.y - 18, PINK, 6, 40, 3, 0.35)
                    sfx("shatter")
                self.start_cast(u, 1, _cf, cast=0.2)
                return
            if getattr(e, "migraine_t", 0) <= 0 and u.ready("Migraine") and dist < 280:
                u.use("Migraine", 12)
                def _mg(u=u, e=e):
                    e.migraine_t = 19
                    self.emit(e.x, e.y, (140, 30, 110), 16, 40, 4, 0.4)
                self.start_cast(u, 2, _mg, cast=1.4)
                return
            if getattr(e, "frustrate_t", 0) <= 0 and u.ready("Frustration") and dist < 280:
                u.use("Frustration", 7)
                def _fr(u=u, e=e):
                    e.frustrate_t = 19
                    e.frustrate_src = u
                    self.tethers.append(Tether(u, e, 0.35, PINK))
                self.start_cast(u, 2, _fr, cast=0.7)
                return
            ENCH = ("reversal_t", "favor_t", "water_armor_t", "illusion_t", "haste_t", "master_t", "mystic_t", "fire_attune_t", "earth_attune_t", "kinetic_t", "holy_veil_t", "spirit_bond_t", "shield_regen_t", "ward_wep_t", "djinn_t", "grasp_t", "harrier_t", "live_vic_t", "vigorous_t")
            if any(getattr(e, a, 0) > 0 for a in ENCH) and u.ready("Inspired Enchantment") and dist < 280:
                u.use("Inspired Enchantment", 8)
                def _ie(u=u, e=e):
                    stolen = None
                    left = 0
                    for a in ENCH:
                        if getattr(e, a, 0) > 0:
                            stolen, left = a, getattr(e, a)
                            setattr(e, a, 0.0)
                            break
                    if stolen:
                        setattr(u, stolen, max(getattr(u, stolen, 0), min(20, left)))
                        u.energy = min(u.max_energy, u.energy + 12)
                    self.tethers.append(Tether(e, u, 0.5, PINK))
                    for i in range(3):
                        self.emit(e.x, e.y, PINK, 6, 30, 3, 0.25)
                    sfx("drain")
                self.start_cast(u, 2, _ie, cast=0.7)
                return
            if dist < BODY * 8 and u.ready("auto"):
                self.fire(u, "glass", L_DMG[1], 320, 1.1)
                u.use("auto", 1.15)
        elif u.cls == "Surger":
            BOLT = (180, 210, 255)
            if u.aura_restore_t <= 0 and u.ready("Aura of Restoration"):
                u.use("Aura of Restoration", 20)
                def _ar(u=u):
                    u.aura_restore_t = 60
                    self.emit(u.x, u.y, HOLY, 10, 30, 3, 0.3)
                self.start_cast(u, 1, _ar, cast=0.25)
                return
            if getattr(u, "air_attune_t", 0) <= 0 and u.ready("Air Attunement"):
                u.use("Air Attunement", 30)
                def _aa(u=u):
                    u.air_attune_t = 62
                    self.emit(u.x, u.y, BOLT, 14, 40, 4, 0.35)
                self.start_cast(u, 2, _aa, cast=1.0)
                return
            if u.mystic_t <= 0 and u.ready("Mystic Regeneration"):
                u.use("Mystic Regeneration", 10)
                def _my(u=u):
                    u.mystic_t = 14
                self.start_cast(u, 1, _my, cast=0.25)
                return
            ally = self.neediest(u, 280) or u
            if getattr(ally, "wind_t", 0) <= 0 and u.ready("Windborne Speed"):
                u.use("Windborne Speed", 5)
                def _wb(u=u, ally=ally):
                    ally.wind_t = 14
                    self.emit(ally.x, ally.y, (220, 220, 230), 10, 40, 3, 0.3)
                self.start_cast(u, 2, _wb, cast=0.75)
                return
            if e and getattr(e, "surge_t", 0) <= 0 and u.ready("Lightning Surge") and dist < 320:
                u.use("Lightning Surge", 10)
                def _ls(u=u, e=e):
                    e.surge_t = 3.0
                    e.surge_src = u
                    self.lightning_flash(u, e)
                    sfx("blast")
                self.start_cast(u, 2, _ls, cast=1.0)
                return
            if e and u.ready("Chain Lightning") and dist < 320:
                u.use("Chain Lightning", 6)
                u.max_energy = max(15, u.max_energy - 5)
                u.energy = min(u.energy, u.max_energy)
                def _cl(u=u, e=e):
                    hits = [e]
                    near = [o for o in self.living(1 - u.team) if o is not e]
                    near.sort(key=lambda o: math.hypot(o.x - e.x, o.y - e.y))
                    for o in near:
                        if math.hypot(o.x - e.x, o.y - e.y) < 110 and len(hits) < 3:
                            hits.append(o)
                    prev = u
                    for h in hits:
                        h.take(90, source=u)
                        self.lightning_flash(prev, h)
                        prev = h
                    sfx("blast")
                self.start_cast(u, 3, _cl, cast=2.0)
                return
            if e and u.ready("Shock Arrow") and dist < 320:
                u.use("Shock Arrow", 8)
                def _sa(u=u, e=e):
                    fx, fy = math.cos(u.facing), math.sin(u.facing)
                    self.projs.append(Projectile(u.x, u.y, fx, fy, 520, 53, u.team, "shock", 1.2, 8, 1, [], u, e))
                    self.emit(u.x, u.y, BOLT, 14, 60, 5, 0.3)
                    sfx("spear")
                self.start_cast(u, 2, _sa, cast=1.0)
                return
            if e and u.ready("Lightning Strike") and dist < 320:
                u.use("Lightning Strike", 5)
                def _lk(u=u, e=e):
                    e.take(42, source=u)
                    self.lightning_flash(u, e)
                    if getattr(u, "max_energy", 60) < 60:
                        e.strike_hex_t = 3.0
                        e.strike_src = u
                    sfx("blast", 0.12)
                self.start_cast(u, 2, _lk, cast=1.0)
                return
            if dist < BODY * 8 and u.ready("auto"):
                self.fire(u, "bolt", L_DMG[1], 340, 1.1)
                u.use("auto", 1.15)
