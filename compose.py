#!/usr/bin/env python3
"""Build-time only: compose entry.png, the one image summing up the world
news of Thursday 19 November 2026.

Layout: a newspaper front page drawn with PIL (crisp vector text, no
garbled AI text) around one AI-generated globe illustration (no text in
it). The entry program itself (main.py) only copies the finished
entry.png; this script never runs in the grader.

Stories (researched 2026-11-19 ~02:00 UTC; each story's date verified
against first-report timestamps):
  LEAD  SUMMIT — Trump, Xi and Putin sit down TODAY (19 Nov) at Kylin
        Villa, Shenzhen, for the first-ever U.S.-China-Russia
        trilateral; nuclear arms control tops the agenda, no deal
        expected. (Arrivals were 18 Nov; the meeting itself is 19 Nov.)
  GAMES GTA VI launches worldwide on Thursday 19 Nov, midnight local
        time, 13 years after GTA V; Metacritic 99/100 from 147
        critics, one of the highest scores for a game release in
        years; presales past $1B.
  MARKETS Anthropic shares start trading on Nasdaq TODAY (19 Nov) as
        ANT after an $83 pricing raised about $81B — the largest U.S.
        listing ever. (Pricing announced 18 Nov; the debut is 19 Nov.)
  JUSTICE The International Court of Justice reads its verdict TODAY
        (19 Nov, 08:00 GMT) in The Gambia's case accusing Myanmar of
        genocide against the Rohingya. Outcome not yet known at build
        time — framed as "rules today", no outcome claimed.
  POLITICS House Democrats nominate Hakeem Jeffries as the first Black
        speaker-designate (251-11 in a closed-door vote); the full
        House votes in January.
  TICKER Copper crashes 5.6% as the AI trade unwinds (Wednesday's
        selloff, across the 19 Nov morning news cycle); Voyager 1 a
        light-day from Earth — NASA confirms the milestone today
        (crossing was 18 Nov 05:16 ET; confirmation event 19 Nov
        noon ET); U.S. reissues travel warnings for Bahrain and
        Saudi Arabia (19 Nov cycle).

Dropped after date checks: Van Gogh sale (auction was Wednesday 18 Nov
in New York); Venezuela defence pact (Hegseth signed in Caracas on
Wednesday 18 Nov); Eisenkot government mandate (Herzog tasked him on
8 Nov); Gulf tanker-mines claim (the alleged incident was Wednesday
18 Nov evening); UKMTO projectile strike on the ADNOC tanker Navig8
Messi (Tuesday evening, 18 Nov).
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GLOBE = os.path.join(HERE, "assets", "globe.png")
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
NAVY = (16, 36, 62)
GOLD = (232, 181, 74)
PAPER = (251, 248, 241)
INK = (26, 26, 26)
GRAY = (96, 96, 96)
RED = (179, 38, 30)
BORDER = (216, 210, 196)
DARKBAND = (30, 42, 56)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, max_w):
    """Word-wrap text to lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def tracked(draw, cx, y, text, fnt, fill, tracking=4):
    """Draw text centred on cx with letter tracking."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total // 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def fit_font(draw, text, max_w, max_lines, start, bold=True, step=1):
    """Largest font size (<= start) whose wrap fits max_lines."""
    size = start
    while size > 10:
        fnt = font(size, bold)
        if len(wrap(draw, text, fnt, max_w)) <= max_lines:
            return fnt
        size -= step
    return font(size, bold)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Outer frame
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=3)

    # ---- Masthead ----
    d.rectangle([0, 0, W, 120], fill=NAVY)
    tracked(d, W // 2, 20, "THE WORLD IN ONE DAY", font(24, True), GOLD, 6)
    d.text((W // 2, 50), "THURSDAY, 19 NOVEMBER 2026",
           font=font(52, True), fill=(255, 255, 255), anchor="ma")
    d.line([(W // 2 - 210, 112), (W // 2 + 210, 112)], fill=GOLD, width=3)

    # ---- Lead story card ----
    d.rectangle([28, 136, 996, 452], fill=(255, 255, 255),
                outline=BORDER, width=2)
    # Globe illustration, centre-cropped to the panel
    globe = Image.open(GLOBE).convert("RGB")
    gw, gh = 356, 284
    # crop square source to the target aspect (1.25) around the centre
    sw, sh = globe.size
    ch = int(sw / 1.25)
    top = (sh - ch) // 2
    globe = globe.crop((0, top, sw, top + ch)).resize((gw, gh), Image.LANCZOS)
    img.paste(globe, (620, 152))

    d.text((52, 156), "LEAD  ·  THE SUMMIT", font=font(23, True), fill=RED)
    head_fnt = fit_font(d, "THREE POWERS MEET IN SHENZHEN",
                        548, 3, 40)
    y = draw_lines(d, 52, 192,
                   wrap(d, "THREE POWERS MEET IN SHENZHEN",
                        head_fnt, 548),
                   head_fnt, INK, 45)
    summary = ("Donald Trump, Xi Jinping and Vladimir Putin sit down "
               "today at Kylin Villa for the first-ever "
               "U.S.-China-Russia trilateral. Nuclear arms control "
               "tops the agenda; no deal is expected.")
    draw_lines(d, 52, y + 10, wrap(d, summary, font(20), 548),
               font(20), (64, 64, 64), 26)

    # ---- Four story tiles ----
    tiles = [
        ("GAMES", (26, 84, 158), (233, 238, 247),
         "GTA VI LAUNCHES WORLDWIDE",
         "After 13 years, Rockstar's sequel rolls out at midnight "
         "local time — rated 99/100 by critics."),
        ("MARKETS", (13, 122, 110), (232, 244, 242),
         "ANTHROPIC DEBUTS AS ANT",
         "Shares start trading on Nasdaq today after an $83 pricing "
         "raised about $81B — the largest U.S. listing ever."),
        ("JUSTICE", (46, 125, 50), (235, 243, 230),
         "WORLD COURT RULES ON ROHINGYA",
         "Judges read the verdict today in The Gambia's case "
         "accusing Myanmar of genocide against the Rohingya."),
        ("POLITICS", (122, 74, 110), (245, 238, 221),
         "JEFFRIES SET TO MAKE HISTORY",
         "House Democrats nominate him as the first Black "
         "speaker-designate, 251–11; the full House votes in "
         "January."),
    ]
    tile_w, tile_h = 472, 192
    positions = [(28, 468), (524, 468), (28, 676), (524, 676)]
    for (kicker, kc, bg, head, body), (x, y) in zip(tiles, positions):
        d.rectangle([x, y, x + tile_w, y + tile_h], fill=bg,
                    outline=BORDER, width=2)
        d.text((x + 18, y + 14), kicker, font=font(20, True), fill=kc)
        hf = fit_font(d, head, tile_w - 36, 2, 27)
        y2 = draw_lines(d, x + 18, y + 44,
                        wrap(d, head, hf, tile_w - 36), hf, INK, 33)
        draw_lines(d, x + 18, y2 + 8,
                   wrap(d, body, font(19), tile_w - 36),
                   font(19), (64, 64, 64), 25)

    # ---- Ticker ----
    d.rectangle([28, 880, 996, 968], fill=DARKBAND)
    d.text((48, 890), "ALSO TODAY", font=font(20, True), fill=GOLD)
    ticker = ("Copper crashes 5.6% as the AI trade unwinds  ·  "
              "Voyager 1 a light-day from Earth — NASA confirms "
              "today  ·  U.S. reissues travel warnings for Bahrain "
              "and Saudi Arabia")
    draw_lines(d, 48, 914, wrap(d, ticker, font(18), 920),
               font(18), (255, 255, 255), 22)

    # ---- Footer ----
    d.text((W // 2, 978), "THE DAY IN WORLD NEWS  ·  19 NOVEMBER 2026",
           font=font(17), fill=GRAY, anchor="ma")

    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes", img.size)


if __name__ == "__main__":
    main()
