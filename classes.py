"""Class, skill, energy and role data for Simulated Arena.

Pure data (no pygame). Imported by arena.py and sounds.py.
"""


DMG_CLASSES = ("Mage","Rogue", "Warrior", "Warlock", "Thumper", "Trident", "Slasher", "Seeping", "Elementalist", "Stoning", "Balthazar", "Ranger", "Deathdancer", "Mesmer", "Deadsword", "Migraine", "Surger", "Double Dragon", "Dark Cultist", "Beast Master")
CASTER_ENERGY = {
    "Mage", "Priest","Lingwah", "Warlock", "Bellringer", "Trident", "Spiritualist", "Zealous", "Elementalist", "Stoning", "Ether", "Expeller", "Bonder", "Mesmer", "Escaper", "Migraine", "Surger", "Lifesheath", "AirEnchant", "Judge", "Conditioner", "Double Dragon", "Dark Cultist", "Beast Master",
}
MARTIAL_ENERGY = {
    "Rogue", "Warrior","Thumper", "Slasher", "Seeping", "Balthazar", "Ranger", "Deathdancer", "Deadsword", "PermaShadow", "Riposte",
}
PET_KINDS = ("Bear", "Bird", "Cat", "Wolf", "Spider")
BEAST_PETS = ("Chimp", "Boa")
HEAL_CLASS = "Priest"

RANKED_SIZES = (2, 3, 5, 8)
RANKED_COMPS = {
    2: [(2, 0, 0), (1, 1, 0), (1, 0, 1)],
    3: [(3, 0, 0), (2, 1, 0), (1, 1, 1), (2, 0, 1)],
    5: [(3, 2, 0), (5, 0, 0), (2, 3, 0), (2, 2, 1), (4, 1, 1), (4, 0, 2), (1, 3, 1)],
    8: [(4, 4, 0), (7, 1, 0), (5, 3, 0)],
}
START_RANK_MMR = 1000
RANK_K = 32

# Keep only the newest TWO patches. Insert new notes at the top.
PATCH_NOTES = [
    ("Patch 4 — Sep 21, 2026", [
        "Beast Master added: a pet caster whose companion fights alongside it.",
        "Passive: all damaging skills cost 52% less energy.",
        "Companions: a ranged Chimp (poo stun) or a high-health melee Boa (stacking poison).",
        "Pet skills: Predators Pounce, Brutal Pet Strike, Scavenger Strike, Feral Aggression.",
        "Support: Strike as One, Great Dwarf Weapon, Call of Protection, Comfort Animal.",
        "Pets have 400 health; Comfort Animal heals 110 or resurrects at 61%.",
    ]),
    ("Patch 3 — Sep 18, 2026", [
        "Dark Cultist added: a hex caster built on health degeneration and shadow clones.",
        "Cultists Rot: a new 8s degeneration hex that ticks 84 damage every 2 seconds.",
        "Reuses existing hexes (Curse of Curses, Seeping Wound, Curse of Anti Healing) and Soul Siphon.",
        "At low health the Cultist splits off a Shadow Clone, mirroring the Rogue's shade.",
    ]),
    ("Patch 2 — Sep 15, 2026", [
        "Mesmer, Blessed Escaper, and Glimmer added. Bellringer counts as a healer.",
        "Tanks (Warrior, Thumper) have 508 HP and their own select row.",
        "Ranked builds must match legal comps; illegal teams are grayed out.",
        "Edit a team and unchanged members keep their win/loss record.",
        "Raise / lower casual bets. Hover a fighter in-match to see class.",
        "Healers wait for 1% damage before ally spells. Heals lose 1% per second.",
        "Hex strip waits 1–2s after the hex is seen in range.",
        "Thumper can keep Comfort-summoning up to 4 pets.",
        "Wards only after the caster has been hit in the last 2 seconds.",
        "Stealth is -50% move speed. Rez morale is one credit per fighter.",
        "Cast bars under channeling units. Comp list is a small ? button.",
        "Bellringer can keep two summons; each ring is a random Knight or Archer after the fight starts.",
        "Deadsword added: axe spins, honor standard, Live Vicariously.",
        "Migraine Mesmer: 28% faster casts, interrupt hexes, Flesh of My Flesh.",
        "Lightning Surger: 60 energy, delayed surge, overcast chain, homing shock arrow.",
        "Lifesheath healer: cheap enchants, sheath, imbue, watchful 25% save.",
        "Perma Shadow tank: 33% faster CDs, shadow form, smoke steps.",
        "Riposte tank: white blocks, Dolyak, Gladiator, Honor standard.",
        "Air Enchanter: +29 heal on ally casts, Protective Spirit 10% cap.",
        "Judges Eye: +32 on casts, reflect damage, Ray of Judgement, shouts.",
        "Conditioner: strip all conditions, Aegis, Spirit Bond 86, anti-KD.",
    ]),
][:2]

CLASSES = ("Mage", "Rogue", "Warrior","Priest", "Warlock", "Thumper", "Bellringer", "Trident", "Spiritualist", "Zealous", "Slasher", "Seeping", "Elementalist", "Stoning", "Balthazar", "Ether", "Ranger", "Expeller", "Bonder", "Deathdancer", "Mesmer", "Escaper", "Glimmer", "Deadsword", "Migraine", "Surger", "Lifesheath", "PermaShadow", "Riposte", "AirEnchant", "Judge", "Conditioner", 
           "Double Dragon", "Lingwah", "Dark Cultist", "Beast Master")
HEAL_PICKS = ("Priest","Lingwah", "Spiritualist", "Zealous", "Ether", "Expeller", "Bonder", "Escaper", "Glimmer", "Bellringer", "Lifesheath", "AirEnchant", "Judge", "Conditioner")
TANK_PICKS = ("Warrior", "Thumper", "PermaShadow", "Riposte")
DPS_PICKS = tuple(c for c in CLASSES if c not in HEAL_PICKS and c not in TANK_PICKS)
MELEE_CLS = {"Warrior", "Rogue", "Thumper", "Slasher", "Balthazar", "Knight", "Bear", "Cat", "Wolf", "Spider", "Pup", "Infernal", "Deathdancer", "Deadsword", "PermaShadow", "Riposte"}
RANGE_CLS = {"Seeping", "Archer", "Bird", "Ranger"}
BODY = 38
AUTO_RANGE = {"melee": 52, "short": BODY * 5, "ranged": BODY * 8, "caster": BODY * 10}
WARD_SKILLS = {"Ward Against Melee", "Warding Apparition", "Weapon of Warding", "Ebon Battle Standard"}
HEX_ATTRS = ("curse_t","lament_t","renew_surge_t", "antiheal_t", "blur_t", "water_hex_t", "seeping_t", "ash_t", "insec_t", "wastrel_t", "diversion_t", "hauntbrand_t", "reaper_t", "migraine_t", "frustrate_t","rot_t","")
ENCHANT_ATTRS = ("reversal_t","favor_t","water_armor_t","illusion_t","haste_t","master_t","mystic_t",
    "fire_attune_t","earth_attune_t","kinetic_t","holy_veil_t","spirit_bond_t","shield_regen_t",
    "ward_wep_t","djinn_t","grasp_t","harrier_t","air_of_t","protect_t","absorb_t","guardian_t",
    "vigorous_t","patient_t","sheath_t","vital_t","mirage_t","watchful_t","meditate_t","aegis_t",
    "hands_t","stable_t","balanced_t","spell_shield_t","glimmer_veil_t","live_vic_t","aura_restore_t",
    "ether_renew_t","zealot_fire_t","balth_aura_t","resilient_t","xinrae_t")

SKILLS = {
    "Mage": [("Frostbolt", 1.6, 280), ("Frost Nova", 7.0, 90), ("Cone of Cold", 5.0, 110), ("Ice Block", 14.0, 0), ("Blink", 8.0, 0)],
    "Rogue": [("Backstab", 1, 55), ("Cheap Shot", 8.0, 50), ("Sprint", 10.0, 0), ("Poison Throw", 3.0, 260), ("Shadow Clone", 16.0, 0)],
    "Warrior": [("Slash", 1.4, 50), ("Shield Block", 7.0, 0), ("Charge", 8.0, 0), ("Hamstring", 6.0, 55), ("Fus Ro Dah", 12.0, 140), ("Bladestorm", 14.0, 70)],
    "Priest": [("Barrier", 10.0, 0), ("Qwik Heal", 4.0, 0), ("Thiq Heal", 6.0, 0), ("Fat Heal", 9.0, 0), ("Healing Favor", 12.0, 0), ("Life Grip", 14.0, 0)],
    "Warlock": [("Curse of Curses", 6.0, 260), ("Soul Siphon", 8.0, 180), ("Fear", 10.0, 160), ("Rain of Fire", 12.0, 240), ("Curse of Anti Healing", 14.0, 260), ("Pentagram", 99.0, 0)],
    "Dark Cultist": [("Cultists Rot", 6.0, 260), ("Shadow Clone", 16.0, 0), ("Curse of Curses", 6.0, 260), ("Seeping Wound", 6.0, 140), ("Curse of Anti Healing", 14.0, 260), ("Soul Siphon", 8.0, 180)],
    "Beast Master": [
        ("Predators Pounce", 5.0, 0), ("Brutal Pet Strike", 5.0, 0), ("Scavenger Strike", 10.0, 0),
        ("Feral Aggression", 20.0, 0), ("Strike as One", 10.0, 0), ("Great Dwarf Weapon", 5.0, 0),
        ("Call of Protection", 90.0, 0), ("Comfort Animal", 1.0, 0),
    ],
    "Double Dragon": [("Double Dragon", 15.0, 320), ("Make Haste", 10.0, 190), ("Return", 12.0, 0), ("Immolate", 7.0, 240), ("Fire Attunement", 15.0, 0), ("Rain of Fire", 12.0, 240), ("Rodgorts Invocation", 10.0, 220), ("Resurrection Signet", 99.0, 0) ],
    "Lingwah": [("Lamentation Hex", 9.0, 260),("Xinraes Weapon", 3.0, 190),("Renewing Surge Hex", 15.0, 260),("Resilient Weapon", 6.0, 0),("Wielders Boon", 4.0, 0),("Anguished Was Lingwah", 30.0, 0),("Glyph of Lesser Energy", 30.0, 0),("Bloodsong Spirit", 20.0, 0),
    ],
    "Thumper": [("Hammer Bash", 5.0, 160), ("Crushing Blow", 4.0, 55), ("Bestial Mauling", 7.0, 220), ("Rampage as One", 16.0, 0), ("Comfort Animal", 10.0, 0)],
    "Bellringer": [("Bell Ring", 10.0, 0), ("Archer Bell", 10.0, 0), ("Harmonic Swarm", 12.0, 0), ("Soothing Sounds", 18.0, 0), ("Sound Wave", 8.0, 0), ("High Ring", 14.0, 0)],
    "Trident": [("Water Trident", 3.2, 320), ("Frozen Burst", 7.0, 130), ("Freezing Gust", 5.0, 260), ("Ward Against Melee", 18.0, 0), ("Blurred Vision", 12.0, 220), ("Water Attunement", 16.0, 0)],
    "Spiritualist": [
        ("Soulmend", 4.0, 0), ("Warding Apparition", 10.0, 0), ("Gravewind Purge", 8.0, 0),
        ("Echo Step", 9.0, 0), ("Ancestors Grasp", 7.0, 110), ("Spirit Well", 16.0, 0),
        ("Hauntbrand", 12.0, 240), ("Last Rite", 20.0, 0),
    ],
    "Zealous": [
        ("Reversal of Fortune", 6.0, 0), ("Dismiss Condition", 5.0, 0), ("Zealous Bene", 8.0, 0),
        ("Signet of Devotion", 10.0, 0), ("Spirit Bond", 12.0, 0), ("Holy Veil", 10.0, 0),
        ("Return", 12.0, 0), ("Dark Escape", 14.0, 0),
    ],
    "Slasher": [
        ("Illusionary Weaponry", 20.0, 0), ("Flurry", 8.0, 0), ("Sympathetic Visage", 12.0, 0),
        ("Distortion", 10.0, 0), ("Deadly Riposte", 10.0, 0), ("Deflect Arrow", 10.0, 0),
        ("Healing Signet", 8.0, 0), ("Resurrection Signet", 99.0, 0),
    ],
    "Seeping": [
        ("Seeping Wound", 6.0, 140), ("Barbed Spear", 4.0, 280), ("Vicious Attack", 5.0, 280),
        ("Critical Eye", 20.0, 0), ("Deadly Haste", 22.0, 0), ("Way of the Master", 30.0, 0),
        ("Resurrection Signet", 99.0, 0),
    ],
    "Elementalist": [
        ("Mind Blast", 7.0, 260), ("Immolate", 7.0, 240), ("Blinding Flash", 8.0, 220),
        ("Rodgorts Invocation", 10.0, 220), ("Gale", 10.0, 180), ("Mystic Regeneration", 12.0, 0),
        ("Fire Attunement", 15.0, 0), ("Flame Djinns Haste", 14.0, 280),
    ],
    "Stoning": [
        ("Ebon Hawk", 5.0, 280), ("Stoning", 5.0, 280), ("Ash Blast", 10.0, 200),
        ("Lyssas Aura", 30.0, 0), ("Earth Attunement", 30.0, 0), ("Kinetic Armor", 30.0, 0),
        ("Resurrection Signet", 99.0, 0),
    ],
    "Balthazar": [
        ("Aura Slicer", 4.0, 50), ("Gash", 6.0, 50), ("Sun and Moon Slash", 8.0, 50),
        ("Harriers Grasp", 15.0, 0), ("Avatar of Balthazar", 20.0, 0), ("Heart of Fury", 10.0, 0),
        ("Harriers Haste", 10.0, 0), ("Resurrection Signet", 99.0, 0),
    ],
    "Ether": [
        ("Reversal of Fortune", 2.0, 0), ("Draw Conditions", 4.0, 0), ("Balthazars Aura", 20.0, 0),
        ("Ether Renewal", 30.0, 0), ("Zealots Fire", 30.0, 0), ("Smite Hex", 12.0, 0),
        ("Aura of Restoration", 20.0, 0), ("Resurrection Signet", 99.0, 0),
    ],
    "Ranger": [
        ("Broad Head Arrow", 10.0, 320), ("Distracting Shot", 10.0, 320), ("Savage Shot", 5.0, 320),
        ("Apply Poison", 12.0, 0), ("Natural Stride", 12.0, 0), ("Mending Touch", 6.0, 0),
        ("Resurrection Signet", 99.0, 0),
    ],
    "Expeller": [
        ("Mend Body and Soul", 3.0, 0), ("Soothing Memories", 4.0, 0), ("Spirit Light", 4.0, 0),
        ("Weapon of Warding", 5.0, 0), ("Expel Hexes", 8.0, 0), ("Protective Was Kaolai", 20.0, 0),
        ("Life", 20.0, 0), ("Recovery", 30.0, 0),
    ],
    "Bonder": [
        ("Reversal of Fortune", 4.0, 0), ("Dismiss Condition", 3.0, 0), ("Shield of Regeneration", 8.0, 0),
        ("Deny Hexes", 12.0, 0), ("Lifebond", 8.0, 0), ("Balthazars Spirit", 8.0, 0),
        ("Blessed Signet", 10.0, 0), ("Bonettis Defense", 12.0, 0),
    ],
    "Deathdancer": [
        ("Augury of Death", 20.0, 140), ("Reapers Mark", 15.0, 260), ("Dancing Daggers", 3.0, 200),
        ("Shadow Step", 8.0, 304),
        ("Entangling Asp", 20.0, 55), ("Signet of Toxic Shock", 15.0, 89), ("Deadly Paradox", 10.0, 0),
        ("Signet of Lost Souls", 8.0, 55), ("Resurrection Signet", 99.0, 0),
    ],
    "Mesmer": [
        ("Mark of Insecurity", 10.0, 260), ("Wastrels Worry", 4.0, 260), ("Diversion", 12.0, 260),
        ("Power Leak", 20.0, 260), ("Power Drain", 20.0, 260), ("Shatter Enchantment", 20.0, 260),
        ("Drain Enchantment", 20.0, 260), ("Resurrection Signet", 99.0, 0),
    ],
    "Escaper": [
        ("Reversal of Fortune", 4.0, 0), ("Gift of Health", 5.0, 0), ("Blessed Light", 3.0, 0),
        ("Signet of Devotion", 5.0, 0), ("Mend Condition", 2.0, 0), ("Spirit Bond", 12.0, 0),
        ("Dark Escape", 30.0, 0), ("Return", 15.0, 0),
    ],
    "Glimmer": [
        ("Glimmer of Light", 1.0, 0), ("Spirit Bond", 12.0, 0), ("Dismiss Condition", 3.0, 0),
        ("Guardian", 6.0, 0), ("Shield of Absorption", 10.0, 0), ("Holy Veil", 12.0, 0),
        ("Vigorous Spirit", 4.0, 0), ("Heal Party", 2.0, 0),
    ],
    "Deadsword": [
        ("Cyclone Axe", 4.0, 70), ("Whirlwind Attack", 1.0, 50), ("Triple Chop", 10.0, 55),
        ("Flail", 12.0, 0), ("You Are All Weaklings", 12.0, 90),
        ("Ebon Battle Standard", 20.0, 0), ("Vigorous Spirit", 4.0, 0), ("Live Vicariously", 8.0, 0),
    ],
    "Migraine": [
        ("Migraine", 12.0, 260), ("Frustration", 7.0, 260), ("Power Spike", 12.0, 110),
        ("Cry of Frustration", 20.0, 260), ("Inspired Enchantment", 8.0, 260),
        ("Power Drain", 20.0, 110), ("Flesh of My Flesh", 12.0, 0),
    ],
    "Surger": [
        ("Lightning Surge", 10.0, 320), ("Lightning Strike", 5.0, 320), ("Chain Lightning", 6.0, 320),
        ("Shock Arrow", 8.0, 320), ("Mystic Regeneration", 10.0, 0), ("Windborne Speed", 5.0, 0),
        ("Aura of Restoration", 20.0, 0), ("Air Attunement", 30.0, 0),
    ],
    "Lifesheath": [
        ("Life Sheath", 2.0, 190), ("Imbue Health", 10.0, 190), ("Signet of Pious Light", 20.0, 190),
        ("Vital Boon", 8.0, 0), ("Mirage Cloak", 15.0, 0), ("Watchful Intervention", 15.0, 190),
        ("Meditation", 20.0, 0), ("Eremites Zeal", 15.0, 190),
    ],
    "PermaShadow": [
        ("Deadly Paradox", 10.0, 0), ("Shadow Form", 20.0, 0), ("Natural Stride", 21.0, 0),
        ("Shroud of Distress", 45.0, 0), ("Feigned Neutrality", 25.0, 0),
        ("Deaths Charge", 30.0, 280), ("Ebon Escape", 10.0, 280), ("Heart of Shadow", 15.0, 0),
    ],
    "Riposte": [
        ("Riposte", 10.0, 0), ("Soldiers Defense", 15.0, 0), ("To the Limit", 20.0, 0),
        ("Dolyak Signet", 20.0, 0), ("Bonettis Defense", 12.0, 0), ("Shield Stance", 15.0, 0),
        ("Gladiators Defense", 20.0, 0), ("Ebon Battle Standard", 20.0, 0),
    ],
    "AirEnchant": [
        ("Air of Enchantment", 8.0, 190), ("Reversal of Fortune", 2.0, 190), ("Patient Spirit", 4.0, 190),
        ("Dwaynas Kiss", 3.0, 190), ("Shield of Absorption", 10.0, 190), ("Protective Spirit", 5.0, 190),
        ("Guardian", 6.0, 190), ("Dismiss Condition", 3.0, 190),
    ],
    "Judge": [
        ("Reversal of Damage", 3.0, 190), ("Smite Condition", 7.0, 190), ("Smite Hex", 12.0, 190),
        ("Ray of Judgement", 15.0, 280), ("Spell Shield", 30.0, 0), ("Restful Breeze", 8.0, 190),
        ("Make Haste", 10.0, 190), ("Fall Back", 25.0, 0),
    ],
    "Conditioner": [
        ("Restore Condition", 2.0, 190), ("Spirit Bond", 5.0, 190), ("Aegis", 30.0, 190),
        ("Guardian", 6.0, 190), ("Shielding Hands", 15.0, 190), ("Holy Veil", 12.0, 190),
        ("Aura of Stability", 12.0, 190), ("Balanced Stance", 30.0, 0),
    ],
}

# L1..L5 strike power. L5 caps ~190. Higher L = longer windup.
L_DMG = {1: 42, 2: 84, 3: 126, 4: 162, 5: 192}
L_CAST = {1: 0.20, 2: 0.55, 3: 1.00, 4: 1.50, 5: 2.20}
L_HEAL = {1: 48, 2: 92, 3: 132, 4: 172, 5: 210}
L_CD = {1: 4.0, 2: 7.0, 3: 10.0, 4: 14.0, 5: 18.0}
L_EN = {1: 5, 2: 8, 3: 10, 4: 13, 5: 15}
FIRE_SKILLS = {"Mind Blast","Rain of Fire", "Double Dragon", "Immolate", "Rodgorts Invocation", "Flame Djinns Haste", "Fire Attunement", "Double Dragon"}
AIR_SKILLS = {"Lightning Surge", "Lightning Strike", "Chain Lightning", "Shock Arrow", "Air Attunement"}
SHEATH_ENCH = {"Life Sheath", "Vital Boon", "Mirage Cloak", "Watchful Intervention", "Meditation", "Eremites Zeal"}


EARTH_SKILLS = {"Ebon Hawk", "Stoning", "Ash Blast", "Earth Attunement", "Kinetic Armor"}
# Beast Master passive: these damaging skills cost 52% less energy.
BEAST_DMG_SKILLS = {"Predators Pounce", "Brutal Pet Strike", "Scavenger Strike"}

# Per-class energy overrides for skills whose global cost is set by another class.
CLASS_ENERGY_OVERRIDE = {
    "Beast Master": {"Comfort Animal": 2},
}
SKILL_L = {
    "Mind Blast": 2, "Immolate": 2, "Blinding Flash": 2, "Rodgorts Invocation": 3,"Gale": 3, "Mystic Regeneration": 2, "Fire Attunement": 1, "Flame Djinns Haste": 4, "Double Dragon": 4, "Xinraes Weapon": 2, 
}
ENERGY_COST = {name: L_EN[SKILL_L[name]] for name in SKILL_L}
ENERGY_COST.update({
    #Lingwah
    "Xinraes Weapon": 5,"Lamentation Hex": 10,"Renewing Surge Hex": 5,"Resilient Weapon": 10,"Wielders Boon": 5,"Anguished Was Lingwah": 5,"Glyph of Lesser Energy": 5,"Bloodsong Spirit": 5,
    #Double Dragon
    "Double Dragon": 10,"Make Haste": 5,"Return": 5,"Rain of Fire": 13,"Resurrection Signet": 0,
    # Stoning / Balthazar (already tuned)
    "Ebon Hawk": 10, "Stoning": 15, "Ash Blast": 5, "Lyssas Aura": 5,"Earth Attunement": 10, "Kinetic Armor": 15,"Aura Slicer": 0, "Gash": 6, "Sun and Moon Slash": 8,
    "Harriers Grasp": 6, "Avatar of Balthazar": 5, "Heart of Fury": 4, "Harriers Haste": 6,
    # Mage
    "Frostbolt": 5, "Frost Nova": 10, "Cone of Cold": 8, "Ice Block": 5, "Blink": 8,
    # Rogue
    "Backstab": 6, "Cheap Shot": 8, "Sprint": 5, "Poison Throw": 6, "Shadow Clone": 12,
    # Warrior
    "Slash": 0, "Shield Block": 5, "Charge": 6, "Hamstring": 5, "Fus Ro Dah": 10, "Bladestorm": 10,
    # Priest
    "Barrier": 10, "Qwik Heal": 5, "Thiq Heal": 8, "Fat Heal": 12, "Healing Favor": 8, "Life Grip": 10,
    # Warlock
    "Curse of Curses": 8, "Soul Siphon": 10, "Fear": 10, "Rain of Fire": 13, "Curse of Anti Healing": 10, "Pentagram": 15,
    # Dark Cultist
    "Cultists Rot": 8, "Seeping Wound": 8,
    # Thumper
    "Hammer Bash": 8, "Crushing Blow": 6, "Bestial Mauling": 8, "Rampage as One": 10, "Comfort Animal": 8,
    # Bellringer
    "Bell Ring": 12, "Archer Bell": 12, "Harmonic Swarm": 10, "Soothing Sounds": 10, "Sound Wave": 8, "High Ring": 12,
    # Trident
    "Water Trident": 8, "Frozen Burst": 10, "Freezing Gust": 6, "Ward Against Melee": 10, "Blurred Vision": 8, "Water Attunement": 8,
    # Spiritualist
    "Soulmend": 8, "Warding Apparition": 10, "Gravewind Purge": 6, "Echo Step": 8,
    "Ancestors Grasp": 8, "Spirit Well": 12, "Hauntbrand": 8, "Last Rite": 15,
    # Zealous
    "Reversal of Fortune": 5, "Dismiss Condition": 5, "Zealous Bene": 10, "Signet of Devotion": 0,
    "Spirit Bond": 10, "Holy Veil": 8, "Return": 5, "Dark Escape": 5,
    # Slasher
    "Illusionary Weaponry": 10, "Flurry": 5, "Sympathetic Visage": 8, "Distortion": 5,
    "Deadly Riposte": 6, "Deflect Arrow": 5, "Healing Signet": 0,
    # Seeping
    "Seeping Wound": 8, "Barbed Spear": 6, "Vicious Attack": 8, "Critical Eye": 5,
    "Deadly Haste": 10, "Way of the Master": 10,
    # Signets are free
    "Resurrection Signet": 0,
    "Mend Body and Soul": 5, "Soothing Memories": 5, "Spirit Light": 5,
    "Weapon of Warding": 10, "Expel Hexes": 5, "Protective Was Kaolai": 10,
    "Life": 10, "Recovery": 15,
    "Shield of Regeneration": 10, "Deny Hexes": 5, "Lifebond": 10,
    "Balthazars Spirit": 10, "Blessed Signet": 0, "Bonettis Defense": 8,
    "Augury of Death": 5, "Reapers Mark": 5, "Dancing Daggers": 5, "Shadow Step": 8,
    "Entangling Asp": 10, "Signet of Toxic Shock": 0, "Deadly Paradox": 15, "Signet of Lost Souls": 0,
    "Glimmer of Light": 5, "Guardian": 5, "Shield of Absorption": 5,
    "Holy Veil": 5, "Vigorous Spirit": 5, "Heal Party": 15,
    "Cyclone Axe": 5, "Whirlwind Attack": 6, "Triple Chop": 5, "Flail": 4,
    "You Are All Weaklings": 5, "Ebon Battle Standard": 10, "Live Vicariously": 5,
    "Migraine": 10, "Frustration": 10, "Power Spike": 5, "Cry of Frustration": 10,
    "Inspired Enchantment": 10, "Power Drain": 5, "Flesh of My Flesh": 5,
    "Lightning Surge": 15, "Lightning Strike": 5, "Chain Lightning": 10, "Shock Arrow": 5,
    "Windborne Speed": 10, "Air Attunement": 10,
    "Deadly Paradox": 15, "Shadow Form": 10, "Shroud of Distress": 10, "Feigned Neutrality": 5,
    "Deaths Charge": 5, "Ebon Escape": 5, "Heart of Shadow": 5,
    "Riposte": 4, "Soldiers Defense": 5, "To the Limit": 5, "Dolyak Signet": 0,
    "Shield Stance": 5, "Gladiators Defense": 5,
    "Air of Enchantment": 5, "Patient Spirit": 5, "Dwaynas Kiss": 5, "Protective Spirit": 10,
    "Reversal of Damage": 5, "Smite Condition": 5, "Smite Hex": 5, "Ray of Judgement": 10,
    "Spell Shield": 10, "Restful Breeze": 5, "Make Haste": 5, "Fall Back": 10,
    "Restore Condition": 5, "Aegis": 10, "Shielding Hands": 5, "Aura of Stability": 5, "Balanced Stance": 5,
    "Life Sheath": 5, "Imbue Health": 10, "Signet of Pious Light": 0, "Vital Boon": 3,
    "Mirage Cloak": 5, "Watchful Intervention": 5, "Meditation": 5, "Eremites Zeal": 3,
    "Gift of Health": 5, "Blessed Light": 10, "Mend Condition": 5,
    "Mark of Insecurity": 5, "Wastrels Worry": 5, "Diversion": 10,
    "Power Leak": 10, "Power Drain": 5, "Shatter Enchantment": 10, "Drain Enchantment": 5,
    "Broad Head Arrow": 4, "Distracting Shot": 2, "Savage Shot": 4,
    "Apply Poison": 6, "Natural Stride": 2, "Mending Touch": 2,
    "Draw Conditions": 5, "Balthazars Aura": 15, "Ether Renewal": 10,
    "Zealots Fire": 10, "Smite Hex": 5, "Aura of Restoration": 5,
    # Beast Master
    "Predators Pounce": 2, "Brutal Pet Strike": 5, "Scavenger Strike": 2,
    "Feral Aggression": 7, "Strike as One": 2, "Great Dwarf Weapon": 10,
    "Call of Protection": 2,
})

BOT_NAMES = [
    "Ashen", "Brine", "Cinder", "Dusk", "Ember", "Flint", "Gloom", "Haze", "Ryder", "Xar", "Xaryu", "Pielot",
    "Ivy", "Jinx", "Knell", "Lurk", "Moth", "Nyx", "Onyx", "Pike", "Catalina", "Monica", "Onzie", "Hostage",
    "Quill", "Rook", "Sable", "Thorn", "Umbra", "Vex", "Wren", "Yarn", "Sham", "Huey", "Arma", "Thrall",
    "Zeal", "Bramble", "Crow", "Drift", "Echo", "Fang", "Greaf", "Sham", "Zeus", "Nickelodeon", "Spinner",
]


# ===========================================================================
# PART B — Reusable skill definitions + declarative class builder
# ===========================================================================
#
# Goal: stop hand-writing a new AI branch for every class. Instead:
#
#   1. SKILL_DEFS describes HOW a skill behaves ("ai") plus its default
#      numbers (range, cast, cooldown, energy, dmg, heal, duration, aoe, hex).
#   2. A new skill can REUSE an existing skill's AI by naming a base skill and
#      overriding only the numbers you care about:
#
#         skill("Firebolt", base="Fireball", range=360, cast=0.5, cd=3, dmg=60)
#
#      "Firebolt" now behaves exactly like "Fireball" but with your numbers.
#   3. A whole class can be declared in CLASS_DEFS and built automatically:
#
#         CLASS_DEFS["Firemage"] = dict(
#             role="Dps", energy="caster", projectiles="caster",
#             skills=["Glory Animal", "Firebolt", "Fireball"],
#         )
#
#      "Glory Animal" is just a rename of "Comfort Animal": it reuses the
#      Comfort Animal AI (pet_heal) so the pet knows what to do.
#
# The generic AI runner in entities.py (run_defined_class) executes any class
# declared here, so you never touch the big per-class AI again.
# ---------------------------------------------------------------------------

# Behavior tags understood by run_defined_class() in entities.py.
#   projectile   - fire a projectile at the enemy
#   melee        - land a melee hit on the enemy
#   heal         - heal the neediest ally
#   pet_heal     - heal / resurrect your own companion
#   pet_buff     - buff your own companion (dr / feral / size)
#   ally_enchant - enchant another ally
#   shout        - instant self / team effect
#   hex          - apply a hex to the enemy
#   aoe          - area damage centred on the enemy
SKILL_DEFS = {
    # --- canonical skills (the "AI" that others reuse) ---------------------
    "Reversal of Fortune": dict(ai="ally_enchant", kind="heal", range=300, cast=0.5, cd=1.0,
                           energy=5, heal=69, duration=8),
    "Fireball": dict(ai="projectile", kind="fire", range=280, cast=1.0, cd=5.0,
                     energy=10, dmg=84, heal=0, duration=0, aoe=0, hex=False),
    "Comfort Animal": dict(ai="pet_heal", kind="heal", range=0, cast=1.0, cd=1.0,
                           energy=2, dmg=0, heal=110, duration=0, aoe=0, hex=False, rez=0.61),
    "Predators Pounce": dict(ai="pet_attack", kind="maul", range=0, cast=0.5, cd=5.0,
                             energy=2, dmg=37, heal=0, duration=0, aoe=0, hex=False,
                             on_hit="heal_pet", on_hit_heal=53),
    "Brutal Pet Strike": dict(ai="pet_attack", kind="maul", range=0, cast=0.5, cd=5.0,
                              energy=5, dmg=37, heal=0, duration=0, aoe=0, hex=False,
                              on_hit="brutal"),
    "Scavenger Strike": dict(ai="pet_attack", kind="maul", range=0, cast=0.5, cd=10.0,
                             energy=2, dmg=26, heal=0, duration=0, aoe=0, hex=False,
                             on_hit="energy_on_condition", on_hit_energy=16),
    "Feral Aggression": dict(ai="pet_buff", kind="feral", range=0, cast=0, cd=20.0,
                             energy=7, dmg=0, heal=0, duration=21, aoe=0, hex=False, bonus=10),
    "Call of Protection": dict(ai="pet_buff", kind="dr", range=0, cast=0, cd=90.0,
                               energy=2, dmg=0, heal=0, duration=120, aoe=0, hex=False, dr=21),
    "Great Dwarf Weapon": dict(ai="ally_enchant", kind="gdw", range=260, cast=1.0, cd=5.0,
                               energy=10, dmg=0, heal=0, duration=20, aoe=0, hex=False, bonus=20),
    "Strike as One": dict(ai="shout", kind="strike_as_one", range=0, cast=0, cd=10.0,
                          energy=2, dmg=0, heal=0, duration=16, aoe=0, hex=False),
    "Healing Breeze": dict(ai="heal", kind="heal", range=200, cast=1.0, cd=5.0,
                           energy=5, dmg=0, heal=92, duration=0, aoe=0, hex=False),
    "Lightning Bolt": dict(ai="projectile", kind="bolt", range=300, cast=0.55, cd=4.0,
                           energy=8, dmg=42, heal=0, duration=0, aoe=0, hex=False),
    "Fire Nova": dict(ai="aoe", kind="fire", range=120, cast=1.0, cd=10.0,
                      energy=10, dmg=60, heal=0, duration=0, aoe=3, hex=False),
    "Withering Hex": dict(ai="hex", kind="curse", range=260, cast=1.0, cd=8.0,
                          energy=8, dmg=0, heal=0, duration=8, aoe=0, hex=True),
}


def skill(name, base, **overrides):
    """Register a new skill that reuses `base`'s AI, with numeric overrides.

    Example:
        skill("Glory Animal", base="Comfort Animal")          # pure rename
        skill("Firebolt", base="Fireball", range=360, dmg=60) # retuned clone
    """
    if base not in SKILL_DEFS:
        raise KeyError("unknown base skill %r" % base)
    d = dict(SKILL_DEFS[base])
    d["base"] = base
    d.update(overrides)
    SKILL_DEFS[name] = d
    return name


# Declarative class definitions. Each entry is built into SKILLS / ENERGY_COST
# and the role tuples by build_class_defs() below.
CLASS_DEFS = {
    # Example class showing the whole flow: a fire caster that also keeps a pet.
    # "Glory Animal" is a rename of "Comfort Animal" (same AI, new name).
    # "Firebolt" reuses the "Fireball" AI with a longer range and lower cost.
    
}

# Renames created by skill(); maps new name -> base name (for reference / docs).
SKILL_ALIAS = {}


def _register_alias(name, base):
    SKILL_ALIAS[name] = base


def build_class_defs():
    """Merge CLASS_DEFS into SKILLS / ENERGY_COST and the role tuples.

    Safe to call repeatedly. Existing classes are never overwritten.
    """
    global CLASSES, DMG_CLASSES, HEAL_PICKS, TANK_PICKS, DPS_PICKS
    classes = list(CLASSES)
    dmg = list(DMG_CLASSES)
    heal = list(HEAL_PICKS)
    tank = list(TANK_PICKS)

    for cls, cdef in CLASS_DEFS.items():
        skills = cdef.get("skills", [])
        rows = []
        for entry in skills:
            # entry is one of:
            #   "Skill"                       -> use an existing skill as-is
            #   "New = Base"                  -> rename Base's AI to New
            #   {"name":..,"base":.., ...}    -> rename + numeric overrides
            if isinstance(entry, dict):
                name = entry["name"]
                base = entry.get("base")
                overrides = {k: v for k, v in entry.items() if k not in ("name", "base")}
                if base:
                    skill(name, base, **overrides)
                    _register_alias(name, base)
            elif "=" in entry:
                name, base = [s.strip() for s in entry.split("=", 1)]
                skill(name, base)
                _register_alias(name, base)
            else:
                name = entry
                if name not in SKILL_DEFS:
                    # plain name that already exists as a real skill elsewhere
                    continue
            d = SKILL_DEFS[name]
            rows.append((name, d.get("cd", 0.0), d.get("range", 0)))
            # energy: explicit override wins, else the def's energy
            ENERGY_COST[name] = int(d.get("energy", ENERGY_COST.get(name, 0)))
        if rows:
            SKILLS[cls] = rows

        # role registration
        role = cdef.get("role", "Dps")
        if role == "Healer" and cls not in heal:
            heal.append(cls)
        elif role == "Tank" and cls not in tank:
            tank.append(cls)
        elif role == "Dps" and cls not in dmg:
            dmg.append(cls)
        if cls not in classes:
            classes.append(cls)

        # energy pool registration
        if cdef.get("energy") == "caster":
            CASTER_ENERGY.add(cls)
        elif cdef.get("energy") == "martial":
            MARTIAL_ENERGY.add(cls)

    CLASSES = tuple(classes)
    DMG_CLASSES = tuple(dmg)
    HEAL_PICKS = tuple(heal)
    TANK_PICKS = tuple(tank)
    DPS_PICKS = tuple(c for c in CLASSES if c not in HEAL_PICKS and c not in TANK_PICKS)


# Build the declarative classes now (no-op if CLASS_DEFS is empty).
build_class_defs()
