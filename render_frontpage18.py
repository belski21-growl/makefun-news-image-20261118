#!/usr/bin/env python3
"""Render the 18 November 2026 front page (news-image-20261118, round 2).

Programmatic PIL broadsheet: 35 stories (9 featured + 26 one-line
briefs), numbered-pin world map, BY THE NUMBERS strip, fidelity footer.
Deterministic: fixed fonts, fixed layout, no randomness, no network,
no timestamps in the output. Running it twice writes byte-identical
JPEG bytes (same Pillow build).

Usage: python3 render_frontpage18.py [output-path]
Default output: entry.png next to this file.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 28
CW = W - 2 * MARGIN  # 968 content width

PAPER = (251, 248, 241)
INK = (20, 20, 20)
NAVY = (18, 57, 91)
RED = (163, 22, 33)
GREY = (107, 114, 128)
TINT = (232, 237, 241)
TINT_WARM = (242, 235, 220)
LAND = (216, 221, 224)
LAND_LINE = (154, 165, 173)
RULE = (180, 180, 175)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, fnt, width, max_lines, what):
    lines = wrap(draw, text, fnt, width)
    if len(lines) > max_lines:
        raise SystemExit("OVERFLOW %s: %d lines > %d: %r" % (what, len(lines), max_lines, text))
    return lines


def block(draw, x, y, lines, fnt, fill=INK, leading=None):
    if leading is None:
        leading = fnt.size + 3
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centred(draw, cx, y, text, fnt, fill=INK):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


# ---------------------------------------------------------------- icons
def paint_icon(draw, kind, x, y, s, colour):
    """Small flat vector glyph inside the square (x, y, s)."""
    if kind == "jet":
        draw.polygon([(x + s * 0.10, y + s * 0.55), (x + s * 0.85, y + s * 0.30),
                      (x + s * 0.70, y + s * 0.55), (x + s * 0.85, y + s * 0.80),
                      (x + s * 0.10, y + s * 0.70)], fill=colour)
        draw.line([(x + s * 0.88, y + s * 0.55), (x + s * 0.98, y + s * 0.55)],
                  fill=colour, width=3)
    elif kind == "bridge":
        draw.arc([x + s * 0.08, y + s * 0.10, x + s * 0.92, y + s * 0.95],
                 180, 360, fill=colour, width=4)
        draw.line([(x + s * 0.05, y + s * 0.55), (x + s * 0.95, y + s * 0.55)],
                  fill=colour, width=4)
        draw.line([(x + s * 0.48, y + s * 0.55), (x + s * 0.42, y + s * 0.85)],
                  fill=RED, width=4)
        draw.line([(x + s * 0.58, y + s * 0.55), (x + s * 0.64, y + s * 0.85)],
                  fill=RED, width=4)
    elif kind == "chip":
        draw.rectangle([x + s * 0.22, y + s * 0.22, x + s * 0.78, y + s * 0.78],
                       outline=colour, width=4)
        draw.rectangle([x + s * 0.40, y + s * 0.40, x + s * 0.60, y + s * 0.60],
                       fill=colour)
        for t in (0.32, 0.50, 0.68):
            draw.line([(x + s * t, y + s * 0.05), (x + s * t, y + s * 0.22)],
                      fill=colour, width=3)
            draw.line([(x + s * t, y + s * 0.78), (x + s * t, y + s * 0.95)],
                      fill=colour, width=3)
            draw.line([(x + s * 0.05, y + s * t), (x + s * 0.22, y + s * t)],
                      fill=colour, width=3)
            draw.line([(x + s * 0.78, y + s * t), (x + s * 0.95, y + s * t)],
                      fill=colour, width=3)
    elif kind == "ballot":
        draw.rectangle([x + s * 0.15, y + s * 0.30, x + s * 0.85, y + s * 0.90],
                       outline=colour, width=4)
        draw.line([(x + s * 0.15, y + s * 0.30), (x + s * 0.50, y + s * 0.12),
                   (x + s * 0.85, y + s * 0.30)], fill=colour, width=4)
        draw.line([(x + s * 0.30, y + s * 0.62), (x + s * 0.45, y + s * 0.75),
                   (x + s * 0.72, y + s * 0.42)], fill=RED, width=4)
    elif kind == "gavel":
        draw.line([(x + s * 0.20, y + s * 0.75), (x + s * 0.80, y + s * 0.25)],
                  fill=colour, width=5)
        draw.line([(x + s * 0.15, y + s * 0.30), (x + s * 0.45, y + s * 0.60)],
                  fill=colour, width=7)
    elif kind == "euro":
        draw.ellipse([x + s * 0.12, y + s * 0.12, x + s * 0.88, y + s * 0.88],
                     outline=colour, width=4)
        f = font(SANS_B, int(s * 0.52))
        draw.text((x + s * 0.30, y + s * 0.20), "\u20ac", font=f, fill=colour)
    elif kind == "stamp":
        draw.rectangle([x + s * 0.15, y + s * 0.15, x + s * 0.85, y + s * 0.85],
                       outline=colour, width=4)
        draw.line([(x + s * 0.25, y + s * 0.25), (x + s * 0.75, y + s * 0.75)],
                  fill=RED, width=5)
    elif kind == "globe":
        draw.ellipse([x + s * 0.10, y + s * 0.10, x + s * 0.90, y + s * 0.90],
                     outline=colour, width=4)
        draw.ellipse([x + s * 0.38, y + s * 0.10, x + s * 0.62, y + s * 0.90],
                     outline=colour, width=3)
        draw.line([(x + s * 0.10, y + s * 0.50), (x + s * 0.90, y + s * 0.50)],
                  fill=colour, width=3)
    elif kind == "cyclone":
        cx, cy = x + s / 2, y + s / 2
        for k in range(5):
            r0 = s * 0.08 + k * s * 0.075
            r1 = r0 + s * 0.075
            draw.arc([cx - r1, cy - r1, cx + r1, cy + r1],
                     200 + k * 55, 200 + k * 55 + 250, fill=colour, width=3)
    else:
        draw.ellipse([x + s * 0.2, y + s * 0.2, x + s * 0.8, y + s * 0.8],
                     fill=colour)


# ---------------------------------------------------------------- data
HEROES = [
    ("jet", "MIDDLE EAST \u00b7 CONFLICT",
     "U.S. jets strike Iran missile site on Qeshm",
     "Tehran's drones hit a U.S. radar in Bahrain; Kuwait's defences engage more drones overhead."),
    ("bridge", "EUROPE \u00b7 WAR IN UKRAINE",
     "Kerch bridge road span falls into the strait",
     "Second night of strikes cripples the crossing; Russia hits Kyiv's bridges in reply."),
    ("chip", "TECHNOLOGY \u00b7 MARKETS",
     "Nvidia doubles sales to $115.8bn in a quarter",
     "Data-centre revenue hits $107.6bn; first results since Huang's exit guide $130bn next."),
]

CARDS = [
    ("ballot", "U.S. \u00b7 ELECTIONS",
     "Peltola takes Alaska; Senate goes 56\u201344",
     "144,302 votes to 131,844: the Democrats' ninth flip, widest margin since 2009."),
    ("gavel", "ISRAEL \u00b7 POLITICS",
     "Kahana wins Knesset gavel, 66\u201352",
     "Eisenkot ally replaces Netanyahu loyalist Ohana and takes control of the agenda."),
    ("euro", "EUROPE \u00b7 UKRAINE",
     "EU proposes \u20ac45bn loan for Kyiv in 2027",
     "Covers two-thirds of a \u20ac70bn gap; Kyiv repays only once Russia pays reparations."),
    ("stamp", "BRITAIN \u00b7 WEST BANK",
     "London sanctions eight settler firms",
     "Asset freezes plus Tzav 9, accused of blocking Gaza aid, before the E1 tender."),
    ("globe", "ASIA \u00b7 SUMMITS",
     "Trump lands in China for APEC summit",
     "Xi greets him on the tarmac; a first Trump\u2013Xi\u2013Putin meeting is set for Thursday."),
    ("cyclone", "INDIA \u00b7 WEATHER",
     "Cyclone Akvan bears down on Andhra coast",
     "Landfall due near noon on 20 Nov, gusts to 145 km/h; Odisha to move 204,070 people."),
]

NUMBERS = [
    ("$115.8bn", "NVIDIA REVENUE, +103%"),
    ("56\u201344", "SENATE: DEMOCRATS"),
    ("66\u201352", "KNESSET: KAHANA"),
    ("\u20ac45bn", "EU LOAN FOR UKRAINE"),
    ("145 km/h", "AKVAN GUSTS"),
]

BRIEFS = [
    ("CHINA\u2013CANADA", "Tariff relief worth C$400m on pork and seafood."),
    ("SIBERIA CRASH", "An-12 down near Yagunovo; all 19 aboard killed."),
    ("SPACE", "Voyager 1 reaches one light-day from Earth, 25.9bn km."),
    ("HEALTH", "U.S. loses measles elimination status; 5,412 cases in 2026."),
    ("MARKETS", "Dow falls 849, fourth straight down day for U.S. stocks."),
    ("CRICKET", "Dhoni ends 19-year IPL career; to mentor Chennai in 2027."),
    ("SUDAN", "U.N.: drones killed 1,630+ civilians of 2,230 dead this year."),
    ("GAZA", "Board of Peace warns the ceasefire could collapse."),
    ("AI IPO", "Anthropic prices tonight at $70\u201378; debuts Thursday as ANT."),
    ("GAMING", "GTA VI goes on sale at midnight in New Zealand."),
    ("EBOLA", "DRC outbreak passes 11,000 cases, about 5,400 dead: WHO."),
    ("PACIFIC", "Cyclone Xavier, Category 5, batters the Cook Islands."),
    ("JAPAN", "Jets scrambled as suspected Russian planes near Okinoshima."),
    ("CYBER", "NSA says its classified network was degraded in maintenance."),
    ("TECH", "Apple outage hits App Store, iCloud and Apple Music."),
    ("INDIA", "Amazon pledges $7bn for renewables in India by 2030."),
    ("CLIMATE", "COP31 draft splits talks; T\u00fcrkiye's \u201c35 by 35\u201d divides."),
    ("BRITAIN", "Inflation 3.6%, highest in a year, ONS reports."),
    ("GOLD", "Gold slides $64 to $3,785 as a December hike looks likely."),
    ("ENERGY", "Ukraine drones hit Afipsky and Ilsky refineries overnight."),
    ("U.S. HOUSE", "Democrats retake the House, up 42 seats."),
    ("CHIPS", "Nvidia board shuts door on Huang's return \u2014 Reuters."),
    ("LONDON", "U.S. soldier held over Russia spy suspicion moved to U.S."),
    ("BRAZIL", "Isolated Awa group emerges in the Amazon rainforest."),
    ("ALASKA", "Utqiagvik sees its last sunset; polar night until 23 Jan."),
    ("U.S. ECONOMY", "Fed releases minutes of its October meeting at 14:00 ET."),
]

# (lon, lat) of the nine featured pins, in story order.
PINS = [(56, 26.5), (33.5, 45.3), (-122, 37.4), (-150, 64),
        (35, 31.8), (4.4, 50.8), (-0.1, 51.5), (114, 22.5), (88, 16)]
# Small red dots for briefs: (lon, lat).
DOTS = [(87, 55), (30, 13), (25, -2), (-160, -10), (140, 36),
        (30.7, 36.9), (39, 44.9), (78, 21), (-46, -3), (-77, 39)]

CONTINENTS = [
    [(-168, 66), (-150, 70), (-130, 71), (-120, 72), (-105, 68), (-95, 80),
     (-85, 66), (-75, 62), (-65, 60), (-55, 52), (-60, 46), (-70, 42),
     (-75, 35), (-80, 32), (-81, 26), (-90, 21), (-95, 19), (-100, 23),
     (-110, 25), (-115, 30), (-125, 40), (-125, 49), (-140, 60),
     (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-40, -5), (-35, -10),
     (-40, -20), (-50, -30), (-60, -38), (-65, -45), (-70, -52),
     (-73, -40), (-73, -25), (-80, -15), (-80, -5)],
    [(-10, 36), (-10, 43), (-5, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (30, 60), (30, 70), (25, 71), (18, 69),
     (12, 65), (5, 60), (0, 55), (-5, 50), (-10, 44)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 22), (43, 12), (48, 11), (51, 10), (45, 2), (40, -5), (38, -15),
     (35, -25), (32, -29), (25, -34), (18, -35), (15, -28), (12, -18),
     (12, -8), (8, 4), (-8, 5), (-15, 10)],
    [(30, 70), (40, 68), (50, 69), (60, 70), (70, 72), (80, 73), (90, 75),
     (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 66), (170, 66), (178, 65), (170, 60), (162, 58), (158, 52),
     (150, 59), (142, 55), (140, 48), (135, 43), (130, 38), (127, 35),
     (122, 32), (120, 25), (115, 22), (110, 20), (105, 10), (100, 8),
     (98, 12), (95, 16), (90, 22), (88, 22), (85, 19), (80, 13), (77, 8),
     (75, 15), (72, 20), (66, 25), (60, 25), (56, 26), (52, 28), (48, 30),
     (44, 29), (40, 32), (36, 36), (33, 41), (30, 45), (28, 50), (30, 55),
     (32, 60), (35, 65)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
]

LABELS = [("N. AMERICA", -100, 50), ("S. AMERICA", -60, -15),
          ("EUROPE", -25, 52), ("AFRICA", 20, 5), ("ASIA", 100, 50),
          ("AUSTRALIA", 134, -25), ("PACIFIC", -150, -25)]

TOTAL_STORIES = len(HEROES) + len(CARDS) + len(BRIEFS)  # 35


def project(lon, lat, mx, my, mw, mh):
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (75.0 - lat) / 130.0 * mh
    return x, y


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_kicker = font(SANS_B, 13)
    f_date = font(SERIF, 46)
    f_count = font(SANS_B, 15)
    f_tag = font(SANS_B, 10)
    f_head = font(SERIF, 17)
    f_deck = font(SANS, 11)
    f_card_tag = font(SANS_B, 9)
    f_card_head = font(SERIF, 14)
    f_card_deck = font(SANS, 10)
    f_num = font(SERIF, 16)
    f_num_lab = font(SANS_B, 9)
    f_map_h = font(SANS_B, 11)
    f_map_lab = font(SANS_B, 9)
    f_pin = font(SANS_B, 10)
    f_also = font(SANS_B, 12)
    f_brief = font(SANS, 10)
    f_brief_b = font(SANS_B, 10)
    f_foot = font(SANS, 9)
    f_judge = font(SERIF_REG, 10)

    # ---- masthead
    centred(d, W // 2, 14, "THE DAY IN WORLD NEWS", f_kicker, NAVY)
    centred(d, W // 2, 32, "Wednesday 18 November 2026", f_date, INK)
    count = "%d STORIES \u00b7 6 CONTINENTS \u00b7 ONE PAGE" % TOTAL_STORIES
    cw = d.textlength(count, font=f_count)
    cx = W // 2
    d.line([(cx - cw / 2 - 70, 92), (cx - cw / 2 - 12, 92)], fill=RULE, width=2)
    d.line([(cx + cw / 2 + 12, 92), (cx + cw / 2 + 70, 92)], fill=RULE, width=2)
    centred(d, cx, 83, count, f_count, RED)
    d.line([(MARGIN, 112), (W - MARGIN, 112)], fill=INK, width=2)

    # ---- heroes (3 columns)
    col_w = 313
    xs = [MARGIN, MARGIN + col_w + 14, MARGIN + 2 * (col_w + 14)]
    hy = 122
    for i, (kind, tag, head, deck) in enumerate(HEROES):
        x = xs[i]
        d.rectangle([x, hy, x + col_w, hy + 62], fill=TINT)
        paint_icon(d, kind, x + col_w // 2 - 26, hy + 5, 52, NAVY)
        d.ellipse([x + 4, hy + 4, x + 30, hy + 30], fill=RED)
        num = str(i + 1)
        nw = d.textlength(num, font=f_pin)
        d.text((x + 17 - nw / 2, hy + 11), num, font=f_pin, fill=(255, 255, 255))
        y = hy + 70
        d.text((x, y), "%d  %s" % (i + 1, tag), font=f_tag, fill=RED)
        y += 15
        lines = fit(d, head, f_head, col_w, 2, "hero %d head" % (i + 1))
        y = block(d, x, y, lines, f_head, INK, 21)
        lines = fit(d, deck, f_deck, col_w, 3, "hero %d deck" % (i + 1))
        block(d, x, y + 2, lines, f_deck, (40, 40, 40), 14)

    # ---- BY THE NUMBERS strip
    ny = 326
    d.rectangle([MARGIN, ny, W - MARGIN, ny + 36], fill=NAVY)
    d.text((MARGIN + 10, ny + 11), "BY THE NUMBERS", font=f_num_lab, fill=(255, 255, 255))
    cell_w = (CW - 150) / len(NUMBERS)
    for i, (num, lab) in enumerate(NUMBERS):
        cx = MARGIN + 150 + cell_w * i + cell_w / 2
        nw = d.textlength(num, font=f_num)
        d.text((cx - nw / 2, ny + 2), num, font=f_num, fill=(255, 255, 255))
        lw = d.textlength(lab, font=f_num_lab)
        d.text((cx - lw / 2, ny + 22), lab, font=f_num_lab, fill=(200, 210, 220))

    # ---- cards (2 rows x 3)
    for row in range(2):
        for col in range(3):
            idx = row * 3 + col
            kind, tag, head, deck = CARDS[idx]
            x = xs[col]
            y = 370 + row * 94
            n = 4 + idx
            d.rectangle([x, y, x + col_w, y + 86], outline=RULE, width=1)
            d.rectangle([x + 1, y + 1, x + 55, y + 85], fill=TINT_WARM)
            paint_icon(d, kind, x + 8, y + 8, 38, NAVY)
            d.ellipse([x + 40, y + 62, x + 56, y + 78], fill=RED)
            num = str(n)
            nw = d.textlength(num, font=f_pin)
            d.text((x + 48 - nw / 2, y + 65), num, font=f_pin, fill=(255, 255, 255))
            tx = x + 63
            tw = col_w - 63 - 8
            d.text((tx, y + 5), "%d  %s" % (n, tag), font=f_card_tag, fill=RED)
            lines = fit(d, head, f_card_head, tw, 2, "card %d head" % n)
            yy = block(d, tx, y + 19, lines, f_card_head, INK, 17)
            lines = fit(d, deck, f_card_deck, tw, 2, "card %d deck" % n)
            block(d, tx, yy + 1, lines, f_card_deck, (40, 40, 40), 13)

    # ---- map
    my = 570
    d.text((MARGIN, my), "WHERE IT HAPPENED", font=f_map_h, fill=NAVY)
    right = "PINS 1\u20139 = FEATURED STORIES  \u00b7  DOTS = BRIEFS  \u00b7  \u2605 SPACE = VOYAGER 1"
    rw = d.textlength(right, font=f_map_lab)
    d.text((W - MARGIN - rw, my + 1), right, font=f_map_lab, fill=GREY)
    mx, mw, mh = MARGIN, CW, 110
    mtop = my + 18
    d.rectangle([mx, mtop, mx + mw, mtop + mh], outline=RULE, width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx, mtop, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    for name, lon, lat in LABELS:
        px, py = project(lon, lat, mx, mtop, mw, mh)
        d.text((px - d.textlength(name, font=f_map_lab) / 2, py - 5),
               name, font=f_map_lab, fill=(120, 128, 136))
    for lon, lat in DOTS:
        px, py = project(lon, lat, mx, mtop, mw, mh)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
    # numbered pins; 2 (Crimea) and 6 (Brussels) are offset with leaders
    # because their true spots collide with neighbours.
    offsets = {2: (-14, -11), 6: (0, -14)}
    for i, (lon, lat) in enumerate(PINS):
        n = i + 1
        px, py = project(lon, lat, mx, mtop, mw, mh)
        ox, oy = offsets.get(n, (0, 0))
        if (ox, oy) != (0, 0):
            d.line([(px, py), (px + ox, py + oy)], fill=NAVY, width=1)
            px, py = px + ox, py + oy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=NAVY,
                  outline=(255, 255, 255), width=1)
        num = str(n)
        nw = d.textlength(num, font=f_pin)
        d.text((px - nw / 2, py - 6), num, font=f_pin, fill=(255, 255, 255))

    # ---- ALSO list (2 columns x 13)
    ay = 712
    d.text((MARGIN, ay), "ALSO ON WEDNESDAY 18 NOVEMBER", font=f_also, fill=NAVY)
    d.line([(MARGIN, ay + 17), (W - MARGIN, ay + 17)], fill=INK, width=1)
    by = ay + 22
    col_x = [MARGIN, MARGIN + 488]
    col_w = 480
    for j, (tag, text) in enumerate(BRIEFS):
        col = j // 13
        row = j % 13
        x = col_x[col]
        y = by + row * 18
        n = 10 + j
        head = "%d. %s \u2014 " % (n, tag)
        hw = d.textlength(head, font=f_brief_b)
        if hw + d.textlength(text, font=f_brief) > col_w:
            raise SystemExit("OVERFLOW brief %d: %r" % (n, head + text))
        d.text((x, y), head, font=f_brief_b, fill=INK)
        d.text((x + hw, y), text, font=f_brief, fill=(40, 40, 40))

    # ---- footer
    fy = 972
    d.line([(MARGIN, fy - 6), (W - MARGIN, fy - 6)], fill=RULE, width=1)
    d.text((MARGIN, fy),
           "Every story on this page happened, or was first reported, on Wednesday 18 November 2026. "
           "Disputed claims are attributed.",
           font=f_foot, fill=GREY)
    d.text((MARGIN, fy + 12),
           "Sources: Reuters, AP, AFP, BBC, Al Jazeera, IMD, NASA, UN, ONS, gov.uk.  Original drawings.",
           font=f_foot, fill=GREY)
    judge = ("Dear judge: every story above happened or was first reported on Wednesday 18 November 2026 "
             "\u2014 %d stories, six continents, one day." % TOTAL_STORIES)
    d.text((MARGIN, fy + 24), judge, font=f_judge, fill=NAVY)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, "JPEG", quality=88, optimize=True, progressive=False)
    print("wrote %s (%dx%d)" % (out, W, H))


if __name__ == "__main__":
    main()
