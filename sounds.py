"""Procedural sound-effect generation for Simulated Arena.

Builds every skill sound at import time (stdlib only, no numpy).
"""

import array
import math
import random

import pygame

from classes import SKILLS



# --- sfx (stdlib only, no numpy) ---
_SFX = {}
_SFX_CD = {}
_SR = 22050


def _make_samples(freq, ms, vol, kind, slide):
    n = max(1, int(_SR * ms / 1000.0))
    out = []
    for i in range(n):
        t = i / _SR
        env = 1.0 - (i / max(1, n - 1)) * 0.96
        f = freq + slide * t
        if kind == "noise":
            v = (random.random() * 2 - 1) * env
        elif kind == "square":
            v = (1.0 if math.sin(2 * math.pi * f * t) >= 0 else -1.0) * env
        else:
            v = math.sin(2 * math.pi * f * t) * env
        s = int(max(-32767, min(32767, v * vol * 32767)))
        out.append(s)
        out.append(s)
    return out


def _snd_from(samples):
    if not pygame.mixer.get_init():
        return None
    buf = array.array("h", samples)
    try:
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None


def _tone(freq, ms, vol=0.25, kind="sine", slide=0):
    return _snd_from(_make_samples(freq, ms, vol, kind, slide))


def _combo(*parts):
    samples = []
    for p in parts:
        samples.extend(_make_samples(*p))
    return _snd_from(samples)


def build_sfx():
    if not pygame.mixer.get_init():
        return
    _SFX.update({
        "frostbolt": _tone(880, 140, 0.22, "sine", -400),
        "frostnova": _combo((200, 80, 0.2, "sine", 0), (140, 180, 0.25, "sine", -80)),
        "cone": _tone(520, 180, 0.2, "sine", -200),
        "iceblock": _combo((900, 60, 0.15, "sine", 0), (400, 200, 0.2, "sine", -100)),
        "blink": _tone(1200, 80, 0.18, "square", 600),
        "Lamentation Hex": _combo((90, 160, 0.22, "sine", -20), (60, 200, 0.2, "square", -10)),
        "Renewing Surge Hex": _combo((300, 100, 0.2, "square", -80), (200, 140, 0.18, "sine", -40)),
        "Resilient Weapon": _combo((500, 90, 0.18, "sine", 40), (700, 110, 0.16, "sine", 20)),
        "Wielders Boon": _combo((600, 80, 0.18, "sine", 0), (850, 100, 0.16, "sine", 30)),
        "Anguished Was Lingwah": _combo((120, 200, 0.24, "sine", -30), (80, 220, 0.2, "square", -10)),
        "Glyph of Lesser Energy": _combo((900, 60, 0.16, "sine", 100), (1200, 70, 0.14, "sine", 60)),
        "Bloodsong Spirit": _combo((300, 140, 0.2, "sine", 20), (450, 160, 0.18, "sine", 40)),
        "slash": _tone(180, 70, 0.22, "noise", 0),
        "Knight's Slash": _tone(160, 70, 0.22, "noise", 0),
        "backstab": _tone(240, 90, 0.24, "noise", 0),
        "cheapshot": _combo((300, 40, 0.2, "square", 0), (120, 80, 0.2, "noise", 0)),
        "sprint": _tone(500, 90, 0.12, "sine", 200),
        "poison": _tone(360, 140, 0.18, "square", -120),
        "clone": _combo((200, 80, 0.15, "sine", 0), (280, 120, 0.15, "sine", 80)),
        "block": _tone(160, 100, 0.22, "square", 0),
        "charge": _tone(140, 160, 0.22, "noise", 0),
        "hamstring": _tone(220, 100, 0.18, "square", -80),
        "shout": _combo((90, 120, 0.28, "sine", 0), (60, 180, 0.22, "sine", -20)),
        "bladestorm": _tone(300, 200, 0.16, "noise", 0),
        "heal": _combo((523, 70, 0.16, "sine", 0), (784, 90, 0.16, "sine", 0)),
        "barrier": _combo((400, 80, 0.16, "sine", 0), (600, 120, 0.16, "sine", 40)),
        "favor": _tone(660, 160, 0.14, "sine", 80),
        "grip": _tone(300, 180, 0.2, "sine", 250),
        "curse": _combo((110, 120, 0.22, "sine", 0), (90, 160, 0.18, "square", -20)),
        "antiheal": _tone(90, 220, 0.2, "square", -30),
        "siphon": _tone(180, 200, 0.16, "sine", 40),
        "fear": _combo((80, 80, 0.18, "sine", 40), (140, 160, 0.16, "sine", -40)),
        "rain": _tone(70, 80, 0.2, "noise", 0),
        "meteor": _combo((70, 90, 0.38, "noise", 0), (110, 110, 0.32, "sine", -50), (40, 140, 0.28, "square", -20)),
        "meteor_hit": _combo((160, 50, 0.36, "noise", 0), (80, 90, 0.3, "sine", -40)),
        "pentagram": _combo((80, 200, 0.2, "sine", 20), (120, 200, 0.18, "sine", 40)),
        "infernal": _combo((50, 180, 0.28, "noise", 0), (70, 200, 0.22, "sine", 10)),
        "bash": _combo((70, 80, 0.26, "noise", 0), (90, 90, 0.2, "sine", -20)),
        "bell": _combo((523, 80, 0.18, "sine", 0), (784, 120, 0.16, "sine", 0)),
        "howl": _tone(180, 220, 0.2, "sine", -40),
        "web": _tone(400, 140, 0.16, "square", -150),
        "trident": _combo((500, 50, 0.2, "square", 0), (220, 90, 0.18, "sine", -80)),
        "burst": _combo((180, 80, 0.22, "sine", 0), (90, 140, 0.2, "sine", -40)),
        "ward": _tone(240, 180, 0.16, "sine", 60),
        "spirit": _combo((660, 70, 0.16, "sine", 0), (880, 110, 0.14, "sine", 40)),
        "purge": _tone(420, 140, 0.16, "sine", 80),
        "holy": _combo((784, 70, 0.16, "sine", 0), (1046, 90, 0.14, "sine", 20)),
        "shadow": _combo((90, 100, 0.2, "sine", 0), (60, 140, 0.16, "sine", -20)),
        "glass": _combo((900, 40, 0.16, "square", 200), (1400, 50, 0.12, "sine", -400)),
        "spear": _combo((300, 50, 0.18, "square", 0), (180, 80, 0.16, "sine", -60)),
        "blast": _combo((220, 70, 0.22, "noise", 0), (160, 90, 0.18, "sine", -40)),
        "doubledragon": _combo((220, 70, 0.22, "noise", 0), (160, 90, 0.18, "sine", -40)),
        "stone": _combo((90, 80, 0.22, "noise", 0), (140, 70, 0.16, "sine", -30)),
        "lightning": _combo((1400, 40, 0.18, "square", 400), (700, 90, 0.16, "sine", -500)),
        "chain": _combo((1100, 50, 0.18, "square", 200), (900, 60, 0.14, "square", -200), (600, 70, 0.14, "sine", -100)),
        "wind": _tone(700, 160, 0.14, "sine", 180),
        "air": _combo((980, 60, 0.14, "sine", 0), (1300, 80, 0.12, "sine", 200)),
        "axe": _combo((160, 50, 0.24, "noise", 0), (90, 80, 0.2, "square", -40)),
        "whirl": _tone(260, 180, 0.18, "noise", 40),
        "rez": _combo((392, 80, 0.18, "sine", 0), (523, 100, 0.16, "sine", 40), (784, 120, 0.14, "sine", 60)),
        "drain": _tone(140, 220, 0.18, "sine", 80),
        "shatter": _combo((1600, 40, 0.16, "square", -600), (900, 80, 0.14, "sine", -300)),
        "arrow": _tone(640, 70, 0.16, "square", -180),
    })
    for names in SKILLS.values():
        for n, _, _ in names:
            if n in _SFX:
                continue
            h = abs(hash(n))
            freq = 90 + (h % 980)
            kind = ("sine", "square", "noise")[h % 3]
            ms = 70 + (h % 170)
            slide = ((h // 11) % 520) - 260
            vol = 0.16 + (h % 10) * 0.008
            _SFX[n] = _tone(freq, ms, vol, kind, slide)


build_sfx()


def sfx(name, cooldown=0.12):
    snd = _SFX.get(name)
    if not snd:
        return
    now = pygame.time.get_ticks() / 1000.0
    if now < _SFX_CD.get(name, 0):
        return
    _SFX_CD[name] = now + cooldown
    try:
        snd.play()
    except Exception:
        pass
