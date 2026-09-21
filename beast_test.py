#!/usr/bin/env python3
"""Headless verification for the Beast Master class."""
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import arena
from arena import Match
from classes import SKILLS, ENERGY_COST, BEAST_DMG_SKILLS, BEAST_PETS


class Stub:
    def __init__(self, name, cls):
        self.name = name
        self.cls = cls
        self.wins = 0
        self.losses = 0


def main():
    random.seed(11)
    print("== Beast Master verification ==")

    # 1. pet spawns
    a = [Stub("BM", "Beast Master"), Stub("H", "Priest")]
    b = [Stub("W", "Warrior"), Stub("M", "Mage")]
    m = Match(a, b)
    pets = [u for u in m.units if u.cls in BEAST_PETS]
    assert pets, "no Beast Master pet spawned!"
    pet = pets[0]
    print("   pet spawned: %s  hp=%.0f/%.0f  is_pet=%s" % (pet.cls, pet.hp, pet.max_hp, pet.is_pet))
    assert pet.max_hp == 400, "pet should have 400 hp, got %s" % pet.max_hp

    # 2. energy passive: damaging skills cost 52% less
    bm = [u for u in m.units if u.cls == "Beast Master"][0]
    for sk in BEAST_DMG_SKILLS:
        base = ENERGY_COST[sk]
        bm.energy = bm.max_energy
        before = bm.energy
        bm.cds[sk] = 0
        bm.gcd_t = 0
        bm.use(sk, 5)
        spent = before - bm.energy
        expect = base * 0.48
        print("   %-18s base=%s spent=%.2f expect=%.2f" % (sk, base, spent, expect))
        assert abs(spent - expect) < 0.01, "passive energy wrong for %s" % sk

    # 3. run a full fight and confirm skills fire + pet acts
    fired = set()
    orig_use = arena.Fighter.use

    def use(self, skill, cd):
        if self.cls == "Beast Master":
            fired.add(skill)
        return orig_use(self, skill, cd)

    arena.Fighter.use = use
    try:
        a = [Stub("BM", "Beast Master"), Stub("H", "Priest")]
        b = [Stub("W", "Warrior"), Stub("M", "Mage")]
        m = Match(a, b)
        for _ in range(int(120 / (1 / 60))):
            m.update(1 / 60)
            if m.done:
                break
    finally:
        arena.Fighter.use = orig_use

    print("   skills used in fight:", sorted(fired))
    missing = [s for s, _, _ in SKILLS["Beast Master"] if s not in fired]
    print("   skills NOT used:", missing)

    # 4. force each pet type and verify its signature mechanic
    for kind in BEAST_PETS:
        a = [Stub("BM", "Beast Master"), Stub("H", "Priest")]
        b = [Stub("W", "Warrior"), Stub("M", "Mage")]
        m2 = Match(a, b)
        # replace the auto-spawned pet with the requested kind
        m2.units = [u for u in m2.units if u.cls not in BEAST_PETS]
        bm2 = [u for u in m2.units if u.cls == "Beast Master"][0]
        pet2 = m2.spawn_beast_pet(bm2, kind=kind)
        assert pet2.cls == kind and pet2.max_hp == 400
        for _ in range(int(60 / (1 / 60))):
            m2.update(1 / 60)
            if m2.done:
                break
        if kind == "Boa":
            print("   Boa poison stacks after fight:", pet2.pet_poison_stacks)
        else:
            print("   Chimp fired poo:", any(p.kind == "poo" for p in m2.projs) or pet2.cds.get("poo", 0) > 0)
    print("== done ==")


if __name__ == "__main__":
    main()
