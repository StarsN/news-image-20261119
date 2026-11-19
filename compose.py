#!/usr/bin/env python3
"""Draw the 19 November 2026 front page and save it as entry.png.

The page is a newspaper front: a navy masthead, one lead story with a
globe picture, four short stories in a two-by-two grid, a ticker strip
and a footer line. Every story on the page comes from the STORIES table
below, so changing the news means editing data, not drawing code.

The output is deterministic: same input, same bytes, every run.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

# --- page ---------------------------------------------------------------
PAGE_W, PAGE_H = 1024, 1024

# --- colours ------------------------------------------------------------
PAPER = (251, 248, 241)
INK = (26, 26, 26)
NAVY = (16, 36, 62)
GOLD = (232, 181, 74)
RED = (179, 38, 30)
GREY = (64, 64, 64)
FAINT = (96, 96, 96)
EDGE = (216, 210, 196)
TICKER_BG = (30, 42, 56)
WHITE = (255, 255, 255)

# --- the news -----------------------------------------------------------
LEAD_HEAD = "THREE POWERS MEET IN SHENZHEN"
LEAD_BODY = (
    "Donald Trump, Xi Jinping and Vladimir Putin sit down today at Kylin "
    "Villa for the first-ever U.S.-China-Russia trilateral. Nuclear arms "
    "control tops the agenda; no deal is expected."
)
TICKER = (
    "Copper crashes 5.6% as the AI trade unwinds  ·  Voyager 1 a light-day "
    "from Earth — NASA confirms today  ·  U.S. reissues travel warnings "
    "for Bahrain and Saudi Arabia"
)

STORIES = [
    {
        "kicker": "GAMES",
        "kicker_rgb": (26, 84, 158),
        "bg": (233, 238, 247),
        "head": "GTA VI LAUNCHES WORLDWIDE",
        "body": "After 13 years, Rockstar's sequel rolls out at midnight "
                "local time — rated 99/100 by critics.",
    },
    {
        "kicker": "MARKETS",
        "kicker_rgb": (13, 122, 110),
        "bg": (232, 244, 242),
        "head": "ANTHROPIC DEBUTS AS ANT",
        "body": "Shares start trading on Nasdaq today after an $83 pricing "
                "raised about $81B — the largest U.S. listing ever.",
    },
    {
        "kicker": "JUSTICE",
        "kicker_rgb": (46, 125, 50),
        "bg": (235, 243, 230),
        "head": "WORLD COURT RULES ON ROHINGYA",
        "body": "Judges read the verdict today in The Gambia's case "
                "accusing Myanmar of genocide against the Rohingya.",
    },
    {
        "kicker": "POLITICS",
        "kicker_rgb": (122, 74, 110),
        "bg": (245, 238, 221),
        "head": "JEFFRIES SET TO MAKE HISTORY",
        "body": "House Democrats nominate him as the first Black "
                "speaker-designate, 251–11; the full House votes in January.",
    },
]

# --- fonts ---------------------------------------------------------------
_cache = {}


def typeface(bold, size):
    """Return a DejaVu face, cached so each size is loaded once."""
    key = (bold, size)
    if key not in _cache:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        _cache[key] = ImageFont.truetype(str(FONT_DIR / name), size)
    return _cache[key]


# --- text helpers --------------------------------------------------------
def wrap(text, face, width):
    """Greedy word wrap: split `text` into lines no wider than `width`."""
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if not current or face.getlength(trial) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_headline(text, top_size, width, max_lines):
    """Biggest bold size (at most `top_size`) wrapping within `max_lines`.

    Returns the font and the wrapped lines. Sizes step down one point at
    a time from `top_size`; 12 is the floor.
    """
    for size in range(top_size, 11, -1):
        face = typeface(True, size)
        lines = wrap(text, face, width)
        if len(lines) <= max_lines:
            return face, lines
    face = typeface(True, 12)
    return face, wrap(text, face, width)


def tracked_span(text, face, tracking):
    """Pixel width of `text` in `face` with `tracking` px between glyphs."""
    total = sum(face.getlength(ch) for ch in text)
    return total + tracking * max(len(text) - 1, 0)


def draw_tracked(canvas, cx, y, text, face, fill, tracking):
    """Draw `text` centred on x=`cx`, letterspaced by `tracking` px."""
    x = round(cx - tracked_span(text, face, tracking) / 2)
    for ch in text:
        canvas.text((round(x), y), ch, font=face, fill=fill)
        x += face.getlength(ch) + tracking


def cover(img, tw, th):
    """Centre-crop `img` to the tw:th aspect, then resize to tw x th."""
    target = tw / th
    w, h = img.size
    if w / h > target:
        nw = int(h * target)
        x0 = (w - nw) // 2
        img = img.crop((x0, 0, x0 + nw, h))
    else:
        nh = int(w / target)
        y0 = (h - nh) // 2
        img = img.crop((0, y0, w, y0 + nh))
    return img.resize((tw, th), Image.LANCZOS)


# --- the page ------------------------------------------------------------
def build():
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(page)

    # Frame first: the masthead band paints over its top edge.
    d.rectangle([8, 8, 1015, 1015], outline=INK, width=3)

    # Masthead.
    d.rectangle([0, 0, PAGE_W, 120], fill=NAVY)
    draw_tracked(d, PAGE_W // 2, 20, "THE WORLD IN ONE DAY",
                 typeface(True, 24), GOLD, 6)
    d.text((PAGE_W // 2, 50), "THURSDAY, 19 NOVEMBER 2026",
           font=typeface(True, 52), fill=WHITE, anchor="ma")
    d.line([(302, 112), (722, 112)], fill=GOLD, width=3)

    # Lead story.
    d.rectangle([28, 136, 996, 452], fill=WHITE, outline=EDGE, width=2)
    globe = Image.open(HERE / "assets" / "globe.png").convert("RGB")
    page.paste(cover(globe, 356, 284), (620, 152))
    d.text((52, 156), "LEAD  ·  THE SUMMIT",
           font=typeface(True, 23), fill=RED)
    head_face, head_lines = fit_headline(LEAD_HEAD, 40, 548, 3)
    y = 192
    for line in head_lines:
        d.text((52, y), line, font=head_face, fill=INK)
        y += 45
    body_face = typeface(False, 20)
    body_y = 192 + len(head_lines) * 45 + 10
    for line in wrap(LEAD_BODY, body_face, 548):
        d.text((52, body_y), line, font=body_face, fill=GREY)
        body_y += 26

    # Four tiles, one loop over the STORIES table.
    spots = [(28, 468), (524, 468), (28, 676), (524, 676)]
    for (x, y), story in zip(spots, STORIES):
        d.rectangle([x, y, x + 472, y + 192], fill=story["bg"],
                    outline=EDGE, width=2)
        d.text((x + 18, y + 14), story["kicker"],
               font=typeface(True, 20), fill=story["kicker_rgb"])
        tile_face, tile_lines = fit_headline(story["head"], 27, 436, 2)
        ty = y + 44
        for line in tile_lines:
            d.text((x + 18, ty), line, font=tile_face, fill=INK)
            ty += 33
        tile_body = typeface(False, 19)
        by = y + 44 + len(tile_lines) * 33 + 8
        for line in wrap(story["body"], tile_body, 436):
            d.text((x + 18, by), line, font=tile_body, fill=GREY)
            by += 25

    # Ticker strip.
    d.rectangle([28, 880, 996, 968], fill=TICKER_BG)
    d.text((48, 890), "ALSO TODAY", font=typeface(True, 20), fill=GOLD)
    tick_face = typeface(False, 18)
    ty = 914
    for line in wrap(TICKER, tick_face, 920):
        d.text((48, ty), line, font=tick_face, fill=WHITE)
        ty += 22

    # Footer.
    d.text((PAGE_W // 2, 978), "THE DAY IN WORLD NEWS  ·  19 NOVEMBER 2026",
           font=typeface(False, 17), fill=FAINT, anchor="ma")

    page.save(HERE / "entry.png", optimize=True)


if __name__ == "__main__":
    build()
