#!/usr/bin/env python3
"""product-ui: colour arithmetic shared by validate_tokens.py and the lookup.

Standard library only. Parses oklch(...) values, converts hex to OKLCH, measures
the distance between two colours (Delta E in OKLab, "ΔE_OK") and matches a colour
against assets/default_colours.json, the palette a model reaches for when nobody
chose one.

A colour is a tuple (lightness 0-1, chroma, hue in degrees).

Self-check:
    python colour.py
"""

import json
import math
import os
import re
import sys

DEFAULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "default_colours.json")
THRESHOLD = 0.02

_OKLCH = re.compile(r"^oklch\(\s*([^\s/)]+)\s+([^\s/)]+)\s+([^\s/)]+)\s*(?:/[^)]*)?\)$", re.IGNORECASE)


def parse_oklch(text):
    """Return (L, C, h) for an oklch(...) string, or None when it does not parse."""
    found = _OKLCH.match(str(text).strip())
    if not found:
        return None
    raw_l, raw_c, raw_h = found.groups()
    try:
        lightness = float(raw_l[:-1]) / 100 if raw_l.endswith("%") else float(raw_l)
        chroma = float(raw_c[:-1]) * 0.4 / 100 if raw_c.endswith("%") else float(raw_c)
        hue = 0.0 if raw_h.lower() == "none" else float(re.sub(r"deg$", "", raw_h, flags=re.IGNORECASE))
    except ValueError:
        return None
    return lightness, chroma, hue % 360


def _linear(channel):
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def hex_to_oklch(text):
    """Return (L, C, h) for #RGB or #RRGGBB."""
    digits = text.strip().lstrip("#")
    if len(digits) == 3:
        digits = "".join(c * 2 for c in digits)
    red, green, blue = (_linear(int(digits[i:i + 2], 16) / 255) for i in (0, 2, 4))
    long_ = 0.4122214708 * red + 0.5363325363 * green + 0.0514459929 * blue
    medium = 0.2119034982 * red + 0.6806995451 * green + 0.1073969566 * blue
    short = 0.0883024619 * red + 0.2817188376 * green + 0.6299787005 * blue
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (long_, medium, short))
    lightness = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    chroma = math.hypot(a, b)
    # Hue is powerless on a grey (CSS Color 4); print 0 there, never rounding noise.
    return lightness, chroma, (math.degrees(math.atan2(b, a)) % 360) if chroma >= 1e-4 else 0.0


def _lab(colour):
    lightness, chroma, hue = colour
    return lightness, chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))


def delta_e(first, second):
    """Euclidean distance in OKLab between two (L, C, h) colours."""
    return math.dist(_lab(first), _lab(second))


def load_defaults(path=DEFAULTS_PATH):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def default_entries(data):
    """Return {name: (L, C, h)} for every Tailwind (v4 and v3) and second-set entry."""
    entries = {name: parse_oklch(value) for name, value in data["tailwind"].items()}
    # v3 hex steps sit up to ~0.03 away from the v4 oklch ones (sRGB vs P3), and the lookup emits v3 hex.
    entries.update({f"{name} (v3)": hex_to_oklch(value) for name, value in data.get("tailwind_v3", {}).items()})
    entries.update({name: parse_oklch(item["oklch"]) for name, item in data["second_set"].items()})
    return entries


def _same_tint(colour, entry):
    """A near-neutral default (cream) matches only a colour tinted the same way, never a plain grey."""
    if entry[1] >= 0.03:
        return True
    hue_gap = abs((colour[2] - entry[2] + 180) % 360 - 180)
    return colour[1] >= entry[1] / 2 and hue_gap <= 30


def match_default(value, names=None, threshold=THRESHOLD, data=None):
    """Return the name of the closest default within threshold, or None.

    value is an oklch(...) string. names limits the search to those entries.
    """
    colour = parse_oklch(value)
    if colour is None:
        return None
    best = None
    for name, entry in default_entries(data or load_defaults()).items():
        if names is not None and name not in names:
            continue
        distance = delta_e(colour, entry)
        if distance <= threshold and _same_tint(colour, entry) and (best is None or distance < best[1]):
            best = (name, distance)
    return best[0] if best else None


def match_acid_green(value, background, data=None):
    """True when value is acid green and background is a near-black ground."""
    rule = (data or load_defaults())["acid_green"]
    colour, ground = parse_oklch(value), parse_oklch(background)
    if colour is None or ground is None:
        return False
    lightness, chroma, hue = colour
    return (rule["hue_min"] <= hue <= rule["hue_max"] and chroma >= rule["min_chroma"]
            and lightness >= rule["min_lightness"] and ground[0] <= rule["background_max_lightness"])


def _self_check():
    assert parse_oklch("oklch(54.6% 0.245 262.881)") == (0.546, 0.245, 262.881)
    assert parse_oklch("oklch(0.5 0.1 none / 50%)") == (0.5, 0.1, 0.0)
    assert parse_oklch("#fff") is None
    blue_600 = hex_to_oklch("#155dfc")  # Tailwind v4 blue-600
    assert delta_e(blue_600, (0.546, 0.245, 262.881)) < 0.01, blue_600
    assert delta_e(blue_600, blue_600) == 0
    white = hex_to_oklch("#ffffff")
    assert abs(white[0] - 1) < 0.001 and white[1] < 0.001, white
    assert delta_e((0.5, 0.1, 10), (0.5, 0.1, 190)) > 0.19
    data = load_defaults()
    assert match_default("oklch(54.6% 0.245 262.881)", data=data) == "blue-600"
    assert match_default("oklch(52% 0.16 172)", data=data) is None
    # Tailwind v3 blue-600 (#2563eb), as a mockup or the lookup writes it.
    assert match_default("oklch(54.6% 0.215 263)", data=data) == "blue-600 (v3)"
    # A plain grey ground is no cream, however close in lightness; a warm tint is.
    assert match_default("oklch(96.1% 0 0)", names=["cream"], data=data) is None
    assert match_default("oklch(95.5% 0.011 85)", names=["cream"], data=data) == "cream"
    assert match_acid_green("oklch(88% 0.25 128)", "oklch(15% 0.01 128)", data=data)
    assert not match_acid_green("oklch(88% 0.25 128)", "oklch(98% 0.01 128)", data=data)
    print("colour.py: self-check passed")


if __name__ == "__main__":
    sys.exit(_self_check())
