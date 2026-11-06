"""The test that decides whether a text entry of a cdp.js dump is drawn on the screen.

check_render.py (R1, R4, R7, R19, R21, R22, R35) and check_shippable_text.py --dom share it, so that the
two scripts never disagree on which text exists. Import it as `from render.visibility import rendered` from
`scripts/`, or as `from visibility import rendered` from `scripts/render/`.

A field an older dump lacks reads as "drawn": `effOpacity` falls back to the element's own `opacity`, `consent`
to false, and a missing rect or font size skips the test that needs it.
"""

OPACITY_MIN = 0.05        # at or under this effective opacity nothing is visible
TINY_PX = 1.0             # a font size, or a rect side, at or under this draws no text


def _px(value):
    try:
        return float(str(value).replace("px", ""))
    except ValueError:
        return None


def rendered(entry, dump):
    """True when the entry's text can be seen: it is not 1px type, screen-reader-only, outside the page,
    transparent or inside a consent banner."""
    size = _px(entry.get("fontSize"))
    if size is not None and size <= TINY_PX:
        return False
    rect = entry.get("rect") or {}
    w, h = rect.get("w"), rect.get("h")
    if "sr-only" in (entry.get("cls") or "") or (w is not None and h is not None and min(w, h) <= TINY_PX):
        return False
    if rect:
        viewport = dump.get("innerWidth") or (dump.get("viewport") or {}).get("width")
        x, y = rect.get("x", 0), rect.get("y", 0)
        if x + (w or 0) <= 0 or y + (h or 0) <= 0 or (viewport and x >= viewport):
            return False
    opacity = entry.get("effOpacity")
    if opacity is None:
        opacity = entry.get("opacity", 1)
    try:
        if float(opacity) <= OPACITY_MIN:
            return False
    except (TypeError, ValueError):
        pass
    return not entry.get("consent")
