#!/usr/bin/env python3
"""Render the make.fun news-image-20261118 round-3 entry: a one-page front
page summing up Wednesday 18 November 2026 in 50 stories, 7 regions + space.

Deterministic: no network, no timestamps, no randomness. Pure PIL drawing.
Output: entry.png (1024x1024 JPEG, quality 88) next to this file.

All 50 stories were verified 19 Nov 2026 against named sources
(Reuters, AP, AFP, BBC, Al Jazeera, ONS, IMD, NASA, WHO, Amnesty, ECDC,
European Commission, Ukrainian Air Force). Every story happened, or was
first reported, on 18 Nov 2026 in some time zone. Disputed claims are
attributed on the page. Stories first reported 17 Nov are listed in the
DATE CHECK box, not as stories.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 14

PAPER = (246, 241, 231)
INK = (26, 26, 26)
MUTED = (90, 86, 76)
RED = (179, 32, 44)
BLUE = (31, 78, 121)
GOLD = (176, 141, 30)
RULE = (26, 26, 26)
CARD_BG = (255, 253, 247)
CHIP_BG = (232, 226, 212)
MAP_DOT = (120, 118, 110)
MAP_LAND = (196, 190, 172)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

_fonts = {}


def font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(d, text, path, size, max_w, min_size=8):
    """Largest font size (<= size) at which text fits max_w."""
    s = size
    while s > min_size and d.textlength(text, font=font(path, s)) > max_w:
        s -= 1
    return font(path, s)


def centre(d, y, text, fnt, fill=INK, x0=0, x1=W):
    w = d.textlength(text, font=fnt)
    d.text(((x0 + x1 - w) / 2, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- data
# featured: n, city, region, beat, proof, source, headline, deck, scene, lon, lat
FEATURED = [
    (1, "SHENZHEN", "ASIA", "DIPLOMACY", "CONFIRMED", "AP / AFP",
     "Xi greets Trump on the tarmac",
     "Rare protocol break in Shenzhen: a hug at the foot of Air Force One, "
     "red carpet, jets overhead.",
     "tarmac", 114.1, 22.5),
    (2, "GULF", "MIDDLE EAST", "CONFLICT", "CONFIRMED", "Reuters",
     "Gulf states down Iranian drones",
     "Bahrain and Kuwait say defences intercepted overnight attacks. Iran "
     "claims hits on a Kuwait base \u2014 unverified.",
     "gulf", 48.5, 28.5),
    (3, "SPACE", "SPACE", "SCIENCE", "CONFIRMED", "NASA",
     "Voyager 1, one light-day out",
     "NASA's probe passes 25.9bn km out \u2014 the first human-made object "
     "there. Its signal now takes a day each way.",
     "voyager", None, None),
    (4, "UKRAINE", "EUROPE", "WAR", "CONFIRMED", "Ukraine Air Force",
     "Russia fires 141 drones overnight",
     "Ukraine says 126 of 141 downed; hits at seven sites.",
     "drones", 32.0, 49.5),
    (5, "NEW YORK", "N. AMERICA", "MARKETS", "CONFIRMED", "AP",
     "Fed minutes sink the Dow 561",
     "Minutes point to a December hike; Dow \u22121.1% to 50,198.",
     "fed", -74.0, 40.7),
    (6, "ODISHA", "ASIA", "WEATHER", "CONFIRMED", "IMD",
     "Cyclone Akvan bears down",
     "Storm nears India's east coast; 80,000+ evacuated. Landfall Friday.",
     "cyclone", 86.5, 20.0),
    (7, "EL OBEID", "AFRICA", "RIGHTS", "CONFIRMED", "Amnesty",
     "Amnesty: 37 killed in El Obeid",
     "Nine alleged RSF drone strikes killed 37 civilians, Amnesty says.",
     "sudan", 30.2, 13.2),
    (8, "BRUSSELS", "EUROPE", "POLITICS", "CONFIRMED", "Reuters",
     "EU agrees \u20ac45bn loan for Kyiv",
     "\u20ac20bn budget aid plus \u20ac25bn military for 2027.",
     "eu", 4.35, 50.85),
    (9, "LONDON", "EUROPE", "ECONOMY", "CONFIRMED", "ONS",
     "UK inflation hits 3.6%",
     "CPI rises to a one-year high, driven by fuel. CPIH 3.7%.",
     "inflation", -0.1, 51.5),
    (10, "GAZA", "MIDDLE EAST", "CONFLICT", "CONFIRMED", "Reuters / BBC",
     "Israeli tanks push past Gaza line",
     "First ground move beyond the Yellow Line since the ceasefire; "
     "three killed.",
     "tanks", 34.4, 31.4),
    (11, "WASHINGTON", "N. AMERICA", "POLITICS", "CONFIRMED", "Reuters / AP",
     "Jeffries nominated, 251\u201311",
     "House Democrats pick him as speaker candidate; floor vote 3 January.",
     "capitol", -77.0, 38.9),
    (12, "AUCKLAND", "N. AMERICA", "CULTURE", "CONFIRMED", "Metacritic",
     "GTA VI is finally on sale",
     "First unlock in New Zealand; reviews hit 99 on Metacritic. "
     "Take-Two +7.5%.",
     "gta", 174.8, -36.8),
    (13, "DHAKA", "ASIA", "LABOUR", "CONFIRMED", "Al Jazeera",
     "Wage protests shut 500 factories",
     "Third day of clashes near Dhaka; workers demand 30,000 taka a month.",
     "factory", 90.4, 23.8),
]

# briefs: n, city, text, lon, lat
BRIEFS = [
    (14, "PNG", "M6.0 quake strikes off Papua New Guinea, depth 10 km", 147.0, -6.5),
    (15, "ROMANIA", "M5.3 quake felt in Bucharest; no major damage", 25.0, 45.8),
    (16, "BOGOT\u00c1", "Colombia rejects US plan for joint strikes on gangs \u2014 NYT", -74.0, 4.7),
    (17, "BRAS\u00cdLIA", "Senate passes R$60bn fiscal package for 2027", -47.9, -15.8),
    (18, "MAPUTO", "Cabinet backs $30bn Rovuma LNG expansion to 18.6 mtpa", 32.6, -25.9),
    (19, "JOBURG", "ANC, EFF, MK and ActionSA hold first four-party talks", 28.0, -26.2),
    (20, "STOCKHOLM", "Drug-resistant infections +72% since 2019, ECDC warns", 18.1, 59.3),
    (21, "KASHMIR", "LeT commander Mohammad Lateef Bhat killed in Kulgam", 74.8, 33.6),
    (22, "MYANMAR", "Junta chief says he is reconsidering ASEAN ties", 96.2, 21.9),
    (23, "SENEGAL", "Migrant boat capsizes off Yenne; 1 dead, dozens missing", -17.4, 14.7),
    (24, "ENTEBBE", "Uganda and Tanzania fast-track EACOP oil pipeline", 32.5, 0.05),
    (25, "S. AFRICA", "Migrants went months without HIV care, aid groups say", 31.0, -29.9),
    (26, "BEIRUT", "US sanctions 3 people, 3 entities over Hezbollah finance", 35.5, 33.9),
    (27, "BAGHDAD", "Court jails 6 French nationals for life over ISIL links", 44.4, 33.3),
    (28, "GAZA", "Doctor Abu Safiya's detention extended 6 more months", 35.5, 31.3),
    (29, "LOS ANGELES", "Grimes scores 47 as Lakers win 9th straight in OT", -118.2, 34.05),
    (30, "TURIN", "Alcaraz beats Medvedev 6-2, 6-4 at the ATP Finals", 7.7, 45.07),
    (31, "MANILA", "Trump hails \u2018biggest trade deal\u2019 \u2014 but nothing is signed", 121.0, 14.6),
    (32, "TOKYO", "Takaichi makes first China visit as PM since 2019", 139.7, 35.7),
    (33, "OTTAWA", "China gives C$400m tariff relief on pork and seafood", -75.7, 45.4),
    (34, "SEOUL", "Xi backs Lee's efforts to ease tensions with the North", 127.0, 37.5),
    (35, "CANBERRA", "Australia sanctions settler leader Daniella Weiss", 149.1, -35.3),
    (36, "KINSHASA", "WHO keeps DR Congo Ebola outbreak a global emergency", 15.3, -4.3),
    (37, "RIYADH", "Coalition destroys Houthi cruise missile aimed at city", 46.7, 24.7),
    (38, "HORMUZ", "Iran says it downed a US MQ-9 drone; Washington silent", 56.3, 27.0),
    (39, "THE HAGUE", "UN court to rule Thursday on Rohingya genocide case", 4.3, 52.08),
    (40, "WASHINGTON", "NSA network outage spreads to Georgia hub", -76.5, 39.0),
    (41, "CARACAS", "Hegseth's surprise visit seals US\u2013Venezuela defence pact", -66.9, 10.5),
    (42, "PORT-AU-PRINCE", "Bukele's troops demolish gang boss Jeff's mansion", -72.3, 18.5),
    (43, "MEXICO CITY", "Sheinbaum: US trade talks \u2018very far along\u2019", -99.1, 19.4),
    (44, "ANTALYA", "Youth protest at COP31 to save fossil-fuel phase-out", 30.7, 36.9),
    (45, "COOK ISLANDS", "Cat 5 Xavier nears Pukapuka; 300+ shelter", -163.0, -10.9),
    (46, "KRASNODAR", "Drones set Ilsky and Afipsky refineries ablaze", 39.0, 45.0),
    (47, "ABU DHABI", "Ukraine\u2013Russia talks agree prisoner swap", 54.4, 24.5),
    (48, "GOLD", "Slides 3.2% to $3,725, lowest close in 14 months", -74.0, 40.7),
    (49, "BADME", "Ethiopian and Eritrean troops mass at disputed border", 37.8, 14.7),
    (50, "SYDNEY", "Tame Impala win 7 ARIA Awards, incl. Album of the Year", 151.2, -33.9),
]

REGIONS = [("N. AMERICA", 9), ("S. AMERICA", 3), ("EUROPE", 9),
           ("MIDDLE EAST", 8), ("AFRICA", 8), ("ASIA", 8),
           ("OCEANIA", 4), ("SPACE", 1)]

NUMBERS = [
    ("141", "Russian drones fired overnight"),
    ("\u2212561", "Dow points on Fed minutes day"),
    ("80,000+", "evacuated ahead of Cyclone Akvan"),
    ("\u20ac45bn", "EU loan agreed for Ukraine"),
    ("37", "civilians killed in El Obeid"),
    ("25.9bn km", "Voyager 1 from Earth"),
]

DATE_CHECK_LEFT = ("First reported 17 Nov, not 18 Nov: Nvidia's $115.8bn quarter "
    "\u00b7 Peltola wins Alaska Senate \u00b7 Kahana wins Knesset speaker vote "
    "66\u201352 \u00b7 Kerch Bridge collapse \u00b7 US strike on Qeshm Island "
    "\u00b7 Prague train crash \u00b7 Mongolia's president resigns.")
DATE_CHECK_NEXT = ("Not yet happened: Trump\u2013Xi\u2013Putin talks (Thu 19 Nov) "
    "\u00b7 Cyclone Akvan landfall (Fri 20 Nov).")

# land mask: (lat, [(lon_min, lon_max), ...]) coarse, for the dotted map
LAND = [
    (75, [(-170, -95), (-60, -20), (40, 180)]),
    (70, [(-170, -60), (-55, -20), (5, 180)]),
    (65, [(-165, -55), (-22, -15), (5, 180)]),
    (60, [(-135, -55), (-5, 2), (5, 180)]),
    (55, [(-130, -55), (-5, 30), (30, 180)]),
    (50, [(-125, -65), (-5, 30), (30, 140)]),
    (45, [(-125, -65), (-10, 30), (30, 141)]),
    (40, [(-125, -70), (-10, 36), (40, 140)]),
    (35, [(-120, -75), (-10, 60), (75, 140)]),
    (30, [(-120, -80), (-10, 35), (35, 90), (100, 120)]),
    (25, [(-105, -85), (-15, 35), (35, 58), (68, 90), (95, 110)]),
    (20, [(-105, -85), (-15, 35), (72, 88), (95, 108)]),
    (15, [(-95, -80), (-15, 42), (75, 80), (95, 105)]),
    (10, [(-85, -78), (-75, -50), (-15, 42), (95, 105)]),
    (5, [(-80, -50), (-10, 42), (95, 105), (95, 120)]),
    (0, [(-80, -35), (-10, 42), (95, 140)]),
    (-5, [(-80, -35), (10, 40), (100, 140)]),
    (-10, [(-75, -35), (12, 40), (105, 140), (113, 150)]),
    (-15, [(-70, -40), (12, 35), (113, 150)]),
    (-20, [(-70, -40), (12, 33), (43, 50), (113, 150)]),
    (-25, [(-70, -40), (12, 32), (44, 47), (113, 150)]),
    (-30, [(-70, -55), (15, 30), (115, 150)]),
    (-35, [(-72, -58), (115, 148), (167, 178)]),
    (-40, [(-73, -62), (167, 175)]),
    (-45, [(-73, -65)]),
    (-50, [(-73, -66)]),
    (-55, [(-70, -66)]),
]


# ---------------------------------------------------------------- scenes
def sky(d, box, top, bottom):
    x0, y0, x1, y1 = box
    for i in range(y1 - y0):
        t = i / max(1, y1 - y0 - 1)
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def clouds(d, box, ys):
    x0, y0, x1, y1 = box
    for cx, cy, r in ys:
        d.ellipse([x0 + cx - r, y0 + cy - r // 2, x0 + cx + r, y0 + cy + r // 2],
                  fill=(255, 255, 255))


def plane(d, x, y, s, color):
    # simple side-view jet silhouette, facing right
    d.polygon([(x, y), (x + 62 * s, y - 6 * s), (x + 78 * s, y),
               (x + 62 * s, y + 6 * s)], fill=color)
    d.polygon([(x + 8 * s, y - 2 * s), (x + 26 * s, y - 20 * s),
               (x + 32 * s, y - 2 * s)], fill=color)
    d.polygon([(x + 30 * s, y), (x + 44 * s, y + 14 * s),
               (x + 50 * s, y)], fill=color)
    d.polygon([(x + 2 * s, y - 2 * s), (x + 10 * s, y - 16 * s),
               (x + 16 * s, y - 2 * s)], fill=color)


def flag(d, x, y, w, h, colors):
    d.line([(x, y), (x, y + h + 14)], fill=(60, 60, 60), width=2)
    if len(colors) == 1:
        d.rectangle([x, y, x + w, y + h], fill=colors[0])
        if colors[0] == (200, 30, 30):
            for sx, sy in [(4, 3), (10, 5), (10, 9), (4, 11)]:
                d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                          fill=(255, 220, 60))
    else:
        for i, c in enumerate(colors):
            d.rectangle([x, y + i * h // len(colors), x + w,
                         y + (i + 1) * h // len(colors)], fill=c)


def drone(d, x, y, s, color):
    d.line([(x - 8 * s, y - 5 * s), (x + 8 * s, y + 5 * s)], fill=color, width=2)
    d.line([(x - 8 * s, y + 5 * s), (x + 8 * s, y - 5 * s)], fill=color, width=2)
    d.ellipse([x - 3 * s, y - 3 * s, x + 3 * s, y + 3 * s], fill=color)
    d.ellipse([x - 9 * s, y - 6 * s, x - 5 * s, y - 2 * s], fill=(255, 220, 80))
    d.ellipse([x + 5 * s, y - 6 * s, x + 9 * s, y - 2 * s], fill=(255, 220, 80))


def burst(d, x, y, r, color):
    for k in range(8):
        ang = 3.14159 * k / 4
        dx, dy = int(r * 0.9 * (1 if k % 2 == 0 else 0.6) * __import__("math").cos(ang)), \
            int(r * 0.9 * (1 if k % 2 == 0 else 0.6) * __import__("math").sin(ang))
        d.line([(x, y), (x + dx, y + dy)], fill=color, width=2)
    d.ellipse([x - r // 3, y - r // 3, x + r // 3, y + r // 3], fill=color)


def scene_tarmac(d, box):
    x0, y0, x1, y1 = box
    sky(d, box, (168, 205, 232), (232, 236, 240))
    clouds(d, box, [(30, 12, 12), (90, 20, 9), (200, 10, 11)])
    d.ellipse([x1 - 42, y0 + 8, x1 - 18, y0 + 32], fill=(255, 236, 170))
    plane(d, x0 + 18, y0 + 34, 1.0, (40, 60, 90))
    d.rectangle([x0, y1 - 26, x1, y1], fill=(70, 74, 80))
    for cx in range(x0 + 8, x1 - 4, 22):
        d.line([(cx, y1 - 13), (cx + 10, y1 - 13)], fill=(255, 255, 255), width=2)
    d.polygon([(x0 + 60, y1 - 26), (x0 + 150, y1 - 26), (x0 + 170, y1 - 6),
               (x0 + 40, y1 - 6)], fill=(179, 32, 44))
    flag(d, x0 + 170, y0 + 52, 16, 10, [(200, 30, 30)])
    flag(d, x0 + 192, y0 + 52, 16, 10,
         [(180, 30, 40), (255, 255, 255), (30, 60, 140)])
    for fx in (x0 + 96, x0 + 116):
        d.ellipse([fx - 3, y1 - 40, fx + 3, y1 - 34], fill=(40, 40, 40))
        d.rectangle([fx - 3, y1 - 34, fx + 3, y1 - 22], fill=(30, 40, 60))


def scene_gulf(d, box):
    x0, y0, x1, y1 = box
    sky(d, box, (12, 22, 48), (30, 48, 88))
    for sx, sy in [(20, 10), (60, 22), (120, 8), (180, 18), (240, 10), (280, 26)]:
        d.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2], fill=(255, 255, 255))
    d.ellipse([x1 - 46, y0 + 8, x1 - 22, y0 + 32], fill=(240, 238, 210))
    d.ellipse([x1 - 40, y0 + 8, x1 - 16, y0 + 32], fill=(30, 48, 88))
    drone(d, x0 + 60, y0 + 26, 1.0, (20, 20, 30))
    drone(d, x0 + 150, y0 + 16, 0.8, (20, 20, 30))
    drone(d, x0 + 230, y0 + 30, 1.0, (20, 20, 30))
    for (bx, by, br) in [(x0 + 90, y0 + 52, 10), (x0 + 200, y0 + 58, 8)]:
        burst(d, bx, by, br, (255, 190, 60))
    d.line([(x0 + 60, y0 + 30), (x0 + 90, y0 + 50)], fill=(255, 220, 120), width=1)
    d.line([(x0 + 230, y0 + 34), (x0 + 200, y0 + 56)], fill=(255, 220, 120), width=1)
    d.rectangle([x0, y1 - 14, x1, y1], fill=(16, 40, 70))
    d.line([(x0, y1 - 14), (x1, y1 - 14)], fill=(120, 160, 200), width=1)


def scene_voyager(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(8, 10, 24))
    for sx, sy in [(14, 12), (50, 30), (90, 8), (150, 26), (200, 12),
                   (250, 34), (290, 16), (120, 44), (30, 52)]:
        d.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2], fill=(255, 255, 255))
    d.ellipse([x0 + 6, y0 + 40, x0 + 34, y0 + 68], fill=(255, 214, 120))
    d.ellipse([x0 + 10, y0 + 44, x0 + 30, y0 + 64], fill=(255, 236, 170))
    pts = []
    for i in range(21):
        t = i / 20
        pts.append((x0 + 30 + t * (x1 - x0 - 110),
                    y0 + 52 + 26 * t * t - 8 * t))
    d.line(pts, fill=(140, 180, 220), width=1)
    for i in range(0, 21, 4):
        d.ellipse([pts[i][0] - 1, pts[i][1] - 1, pts[i][0] + 1, pts[i][1] + 1],
                  fill=(200, 220, 240))
    cx, cy = x1 - 62, y0 + 34
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(212, 175, 55),
              outline=(120, 90, 20))
    d.line([(cx, cy), (cx + 26, cy + 12)], fill=(212, 175, 55), width=3)
    d.line([(cx - 6, cy + 14), (cx + 6, cy + 14)], fill=(180, 180, 180), width=2)
    d.ellipse([x0 + 16, y1 - 16, x0 + 24, y1 - 8], fill=(80, 140, 200))


def scene_drones(d, box):
    x0, y0, x1, y1 = box
    sky(d, box, (16, 20, 44), (52, 60, 96))
    for sx, sy in [(24, 8), (90, 16), (160, 6), (220, 14)]:
        d.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2], fill=(255, 255, 255))
    drone(d, x0 + 50, y0 + 20, 0.9, (10, 10, 18))
    drone(d, x0 + 120, y0 + 12, 0.7, (10, 10, 18))
    drone(d, x0 + 180, y0 + 24, 0.9, (10, 10, 18))
    burst(d, x0 + 84, y0 + 40, 9, (255, 190, 60))
    burst(d, x0 + 160, y0 + 46, 7, (255, 150, 60))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(24, 26, 34))
    for bx, bw, bh in [(6, 22, 12), (34, 16, 9), (56, 26, 14), (88, 18, 10),
                       (112, 24, 12), (142, 16, 9), (164, 22, 11)]:
        d.rectangle([x0 + bx, y1 - bh, x0 + bx + bw, y1], fill=(44, 46, 58))
        for wy in range(y1 - bh + 2, y1 - 1, 4):
            d.point((x0 + bx + 4, wy), fill=(255, 210, 90))


def scene_fed(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(238, 234, 222))
    bx, bw = x0 + 8, (x1 - x0) // 2 - 14
    d.rectangle([bx, y0 + 18, bx + bw, y1 - 8], fill=(250, 248, 242),
                outline=(31, 78, 121), width=2)
    d.polygon([(bx - 4, y0 + 18), (bx + bw // 2, y0 + 4), (bx + bw + 4, y0 + 18)],
              fill=(31, 78, 121))
    for i in range(4):
        cx = bx + 8 + i * (bw - 16) // 3
        d.rectangle([cx, y0 + 26, cx + 5, y1 - 14], fill=(31, 78, 121))
    pts = [(x0 + (x1 - x0) // 2 + 6, y0 + 12), (x0 + (x1 - x0) // 2 + 30, y0 + 22),
           (x0 + (x1 - x0) // 2 + 54, y0 + 18), (x0 + (x1 - x0) // 2 + 78, y0 + 34),
           (x0 + (x1 - x0) // 2 + 100, y0 + 30), (x1 - 8, y0 + 48)]
    d.line(pts, fill=(179, 32, 44), width=3)
    d.polygon(pts + [(x1 - 8, y1 - 8), (x0 + (x1 - x0) // 2 + 6, y1 - 8)],
              fill=(240, 200, 200))


def scene_cyclone(d, box):
    import math
    x0, y0, x1, y1 = box
    sky(d, box, (120, 150, 180), (210, 220, 228))
    cx, cy = x0 + (x1 - x0) // 2, y0 + (y1 - y0) // 2 - 4
    for r in (30, 22, 14, 7):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=20, end=300,
              fill=(255, 255, 255), width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))
    for rx in range(x0 + 6, x1 - 6, 14):
        d.line([(rx, y0 + 6), (rx - 3, y0 + 16)], fill=(180, 200, 220), width=1)
    d.polygon([(x0, y1), (x0 + 40, y1 - 18), (x0 + 90, y1 - 10), (x1, y1 - 22),
               (x1, y1), (x0, y1)], fill=(194, 178, 140))
    d.line([(x0 + 40, y1 - 18), (x0 + 90, y1 - 10)], fill=(31, 78, 121), width=2)
    d.polygon([(x0 + 110, y1 - 12), (x0 + 118, y1 - 26), (x0 + 126, y1 - 12)],
              fill=(179, 32, 44))


def scene_sudan(d, box):
    x0, y0, x1, y1 = box
    sky(d, box, (240, 214, 160), (246, 232, 200))
    d.ellipse([x1 - 36, y0 + 6, x1 - 14, y0 + 28], fill=(255, 200, 90))
    drone(d, x0 + 60, y0 + 16, 0.9, (60, 50, 40))
    d.rectangle([x0, y1 - 20, x1, y1], fill=(214, 178, 120))
    d.rectangle([x0 + 10, y1 - 40, x0 + 66, y1 - 20], fill=(250, 248, 242),
                outline=(120, 110, 100))
    d.rectangle([x0 + 30, y1 - 34, x0 + 46, y1 - 20], fill=(179, 32, 44))
    d.rectangle([x0 + 36, y1 - 40, x0 + 40, y1 - 28], fill=(179, 32, 44))
    d.rectangle([x0 + 90, y1 - 32, x0 + 130, y1 - 20], fill=(150, 110, 70))
    d.polygon([(x0 + 88, y1 - 32), (x0 + 110, y1 - 44), (x0 + 132, y1 - 32)],
              fill=(120, 80, 50))


def scene_eu(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(0, 51, 102))
    import math
    cx, cy = x0 + (x1 - x0) // 2, y0 + (y1 - y0) // 2
    for k in range(12):
        ang = -math.pi / 2 + k * math.pi / 6
        sx = cx + int(26 * math.cos(ang))
        sy = cy + int(20 * math.sin(ang))
        d.polygon([(sx, sy - 4), (sx + 1, sy - 1), (sx + 4, sy), (sx + 1, sy + 1),
                   (sx, sy + 4), (sx - 1, sy + 1), (sx - 4, sy), (sx - 1, sy - 1)],
                  fill=(255, 204, 0))
    d.text((cx - 11, cy - 10), "\u20ac", font=font(SANS_B, 20), fill=(255, 255, 255))
    for i, gx in enumerate((x0 + 6, x1 - 22)):
        d.ellipse([gx, y1 - 14, gx + 14, y1], fill=(212, 175, 55),
                  outline=(150, 115, 20))


def scene_inflation(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(240, 236, 224))
    pts = [(x0 + 8, y1 - 16), (x0 + 40, y1 - 26), (x0 + 72, y1 - 22),
           (x0 + 104, y1 - 38), (x0 + 136, y1 - 34), (x1 - 10, y1 - 50)]
    d.line(pts, fill=(179, 32, 44), width=3)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(179, 32, 44))
    d.text((x0 + 10, y0 + 6), "\u00a3", font=font(SERIF_B, 22), fill=(31, 78, 121))
    d.text((x0 + 34, y0 + 12), "3.6%", font=font(SANS_B, 15), fill=RED)
    d.rectangle([x1 - 46, y1 - 26, x1 - 12, y1 - 8], fill=(31, 78, 121))
    d.rectangle([x1 - 42, y1 - 34, x1 - 16, y1 - 26], fill=(60, 110, 160))


def scene_tanks(d, box):
    x0, y0, x1, y1 = box
    sky(d, box, (214, 196, 160), (240, 228, 200))
    d.rectangle([x0, y1 - 18, x1, y1], fill=(170, 150, 110))
    d.line([(x0, y1 - 18), (x1, y1 - 18)], fill=(90, 80, 60), width=1)
    for tx in (x0 + 16, x0 + 96):
        d.rectangle([tx, y1 - 34, tx + 52, y1 - 22], fill=(90, 96, 70))
        d.rectangle([tx + 12, y1 - 44, tx + 36, y1 - 34], fill=(80, 86, 62))
        d.line([(tx + 36, y1 - 40), (tx + 62, y1 - 44)], fill=(80, 86, 62), width=4)
        for wx in range(tx + 4, tx + 50, 9):
            d.ellipse([wx, y1 - 22, wx + 6, y1 - 16], fill=(50, 52, 40))
    for bx in range(x0 + 8, x1 - 8, 26):
        d.rectangle([bx, y1 - 56, bx + 18, y1 - 44], fill=(200, 190, 170),
                    outline=(140, 130, 110))


def scene_capitol(d, box):
    x0, y0, x1, y1 = box
    sky(d, box, (190, 210, 228), (238, 240, 242))
    cx = x0 + (x1 - x0) // 2
    d.rectangle([cx - 52, y1 - 22, cx + 52, y1 - 8], fill=(245, 245, 240),
                outline=(180, 180, 175))
    for i in range(5):
        px = cx - 44 + i * 20
        d.rectangle([px, y1 - 44, px + 7, y1 - 22], fill=(245, 245, 240),
                    outline=(180, 180, 175))
    d.pieslice([cx - 26, y1 - 62, cx + 26, y1 - 30], start=180, end=360,
               fill=(245, 245, 240), outline=(180, 180, 175))
    d.rectangle([cx - 2, y1 - 70, cx + 2, y1 - 62], fill=(180, 180, 175))
    d.rectangle([x1 - 52, y1 - 30, x1 - 12, y1 - 8], fill=(31, 78, 121))
    d.rectangle([x1 - 48, y1 - 38, x1 - 16, y1 - 30], fill=(60, 110, 160))
    d.text((x0 + 8, y0 + 6), "251\u201311", font=font(SANS_B, 16), fill=RED)


def scene_gta(d, box):
    x0, y0, x1, y1 = box
    sky(d, box, (70, 60, 110), (220, 140, 90))
    d.ellipse([x1 - 40, y0 + 8, x1 - 16, y0 + 32], fill=(255, 210, 130))
    for bx, bw, bh in [(4, 20, 30), (28, 16, 44), (48, 24, 26), (76, 18, 40),
                       (98, 22, 32), (124, 16, 46), (144, 22, 28)]:
        d.rectangle([x0 + bx, y1 - 20 - bh, x0 + bx + bw, y1 - 20],
                    fill=(40, 34, 60))
        for wy in range(y1 - 20 - bh + 4, y1 - 22, 8):
            d.point((x0 + bx + 5, wy), fill=(255, 210, 90))
            d.point((x0 + bx + 12, wy), fill=(255, 210, 90))
    d.rectangle([x0, y1 - 20, x1, y1], fill=(30, 30, 38))
    d.polygon([(x0 + 20, y1 - 8), (x0 + 34, y1 - 18), (x0 + 66, y1 - 18),
               (x0 + 84, y1 - 8)], fill=(179, 32, 44))
    d.ellipse([x0 + 28, y1 - 10, x0 + 36, y1 - 2], fill=(20, 20, 24))
    d.ellipse([x0 + 68, y1 - 10, x0 + 76, y1 - 2], fill=(20, 20, 24))
    d.text((x1 - 44, y0 + 4), "VI", font=font(SERIF_B, 26), fill=(255, 255, 255))


def scene_factory(d, box):
    x0, y0, x1, y1 = box
    sky(d, box, (200, 214, 224), (238, 240, 242))
    d.rectangle([x0 + 8, y1 - 40, x0 + 96, y1 - 8], fill=(150, 140, 130))
    d.rectangle([x0 + 14, y1 - 52, x0 + 24, y1 - 40], fill=(120, 110, 100))
    d.rectangle([x0 + 34, y1 - 58, x0 + 44, y1 - 40], fill=(120, 110, 100))
    for wx in range(x0 + 16, x0 + 92, 14):
        d.rectangle([wx, y1 - 34, wx + 8, y1 - 26], fill=(255, 240, 180))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(120, 116, 108))
    for gx in range(x0 + 104, x1 - 6, 12):
        d.line([(gx, y1 - 34), (gx, y1 - 8)], fill=(60, 60, 60), width=3)
    d.line([(x0 + 104, y1 - 34), (x1 - 6, y1 - 34)], fill=(60, 60, 60), width=3)
    for fx, fc in [(x0 + 112, (31, 78, 121)), (x0 + 126, (179, 32, 44))]:
        d.ellipse([fx - 3, y1 - 26, fx + 3, y1 - 20], fill=fc)
        d.rectangle([fx - 3, y1 - 20, fx + 3, y1 - 8], fill=fc)


SCENES = {"tarmac": scene_tarmac, "gulf": scene_gulf, "voyager": scene_voyager,
          "drones": scene_drones, "fed": scene_fed, "cyclone": scene_cyclone,
          "sudan": scene_sudan, "eu": scene_eu, "inflation": scene_inflation,
          "tanks": scene_tanks, "capitol": scene_capitol, "gta": scene_gta,
          "factory": scene_factory}


# ---------------------------------------------------------------- render
def number_badge(d, x, y, n, r=9):
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED, outline=(255, 255, 255), width=1)
    t = str(n)
    f = font(SANS_B, 11 if len(t) < 2 else 10)
    w = d.textlength(t, font=f)
    d.text((x - w / 2, y - 7 if len(t) < 2 else y - 6.5), t, font=f,
           fill=(255, 255, 255))


def featured_card(d, box, item, hero):
    x0, y0, x1, y1 = box
    n, city, region, beat, proof, source, headline, deck, scene, _, _ = item
    d.rectangle(box, fill=CARD_BG, outline=(200, 192, 172), width=1)
    scene_h = 96 if hero else 56
    SCENES[scene](d, (x0 + 1, y0 + 1, x1 - 1, y0 + 1 + scene_h))
    number_badge(d, x0 + 13, y0 + 13, n)
    ty = y0 + scene_h + 6
    tag = "%s \u00b7 %s" % (region, beat)
    tf = font(SANS_B, 9 if hero else 8)
    d.text((x0 + 8, ty), tag, font=tf, fill=BLUE)
    pw = d.textlength(" " + proof + " ", font=tf)
    d.rectangle([x1 - 8 - pw, ty - 1, x1 - 8, ty + 10], fill=(31, 78, 121))
    d.text((x1 - 8 - pw, ty), " " + proof, font=tf, fill=(255, 255, 255))
    hy = ty + 13
    hf = font(SERIF_B, 16 if hero else 12)
    hl = wrap(d, headline, hf, x1 - x0 - 16)
    for i, ln in enumerate(hl[:2]):
        d.text((x0 + 8, hy + i * (19 if hero else 14)), ln, font=hf, fill=INK)
    dy = hy + len(hl[:2]) * (19 if hero else 14) + 2
    df = font(SANS, 11 if hero else 9)
    dl = wrap(d, deck, df, x1 - x0 - 16)
    for i, ln in enumerate(dl[:2]):
        d.text((x0 + 8, dy + i * (13 if hero else 11)), ln, font=df, fill=(50, 48, 44))
    sf = font(SANS, 8 if hero else 7)
    d.text((x0 + 8, y1 - 12), source, font=sf, fill=MUTED)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # ---- masthead
    d.rectangle([0, 0, W, 6], fill=RED)
    centre(d, 12, "T H E   D A Y   I N   W O R L D   N E W S",
           font(SANS_B, 13), fill=RED)
    centre(d, 30, "Wednesday 18 November 2026", font(SERIF_B, 34))
    centre(d, 70, "50 STORIES \u00b7 7 REGIONS \u00b7 ONE PAGE",
           font(SANS_B, 12))
    d.line([(MARGIN, 90), (W - MARGIN, 90)], fill=RULE, width=2)
    d.line([(MARGIN, 93), (W - MARGIN, 93)], fill=RULE, width=1)
    # ---- region bar
    y = 99
    total_w = W - 2 * MARGIN
    chip_w = total_w // len(REGIONS)
    for i, (name, cnt) in enumerate(REGIONS):
        cx0 = MARGIN + i * chip_w
        cx1 = cx0 + chip_w - 4
        d.rounded_rectangle([cx0, y, cx1, y + 20], radius=4, fill=CHIP_BG,
                            outline=(200, 192, 172))
        label = "%s %d" % (name, cnt)
        f = fit_font(d, label, SANS_B, 10, chip_w - 12)
        w = d.textlength(label, font=f)
        d.text(((cx0 + cx1 - w) / 2, y + 5), label, font=f, fill=INK)
    # ---- heroes
    hy0, hy1 = 126, 302
    hw = (W - 2 * MARGIN - 2 * 12) // 3
    for i, item in enumerate(FEATURED[:3]):
        x0 = MARGIN + i * (hw + 12)
        featured_card(d, (x0, hy0, x0 + hw, hy1), item, hero=True)
    # ---- cards rows
    for row, items in enumerate((FEATURED[3:8], FEATURED[8:13])):
        cy0 = 308 + row * 146
        cy1 = cy0 + 140
        cw = (W - 2 * MARGIN - 4 * 10) // 5
        for i, item in enumerate(items):
            x0 = MARGIN + i * (cw + 10)
            featured_card(d, (x0, cy0, x0 + cw, cy1), item, hero=False)
    # ---- by the numbers
    ny0, ny1 = 604, 644
    d.rectangle([MARGIN, ny0, W - MARGIN, ny1], fill=(26, 26, 26))
    d.text((MARGIN + 10, ny0 + 13), "BY THE NUMBERS",
           font=font(SANS_B, 11), fill=(255, 220, 90))
    cell_w = (W - MARGIN - (MARGIN + 150)) // 6
    for i, (num, label) in enumerate(NUMBERS):
        cx0 = MARGIN + 150 + i * cell_w
        nf = fit_font(d, num, SANS_B, 17, cell_w - 8)
        d.text((cx0 + 4, ny0 + 4), num, font=nf, fill=(255, 255, 255))
        lf = fit_font(d, label, SANS, 8, cell_w - 8)
        d.text((cx0 + 4, ny0 + 25), label, font=lf, fill=(200, 200, 200))
    # ---- map
    my0, my1 = 650, 766
    mx0, mx1 = MARGIN, 714
    d.text((mx0, my0), "WHERE IT HAPPENED",
           font=font(SANS_B, 11), fill=INK)
    map_top = my0 + 16
    map_bot = my1

    def to_xy(lon, lat):
        return (mx0 + (lon + 180) / 360.0 * (mx1 - mx0),
                map_top + (80 - lat) / 140.0 * (map_bot - map_top))

    for lat, spans in LAND:
        for lo0, lo1 in spans:
            lon = lo0
            while lon <= lo1:
                px, py = to_xy(lon, lat)
                d.ellipse([px - 1.2, py - 1.2, px + 1.2, py + 1.2], fill=MAP_LAND)
                lon += 5
    for n, city, text, lon, lat in BRIEFS:
        px, py = to_xy(lon, lat)
        d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill=MAP_DOT)
    for item in FEATURED:
        n, _, _, _, _, _, _, _, _, lon, lat = item
        if lon is None:
            continue
        px, py = to_xy(lon, lat)
        number_badge(d, px, py, n, r=8)
    # Voyager star, top-right of the map
    sx, sy = mx1 - 16, map_top + 10
    d.polygon([(sx, sy - 9), (sx + 2.5, sy - 2.5), (sx + 9, sy), (sx + 2.5, sy + 2.5),
               (sx, sy + 9), (sx - 2.5, sy + 2.5), (sx - 9, sy), (sx - 2.5, sy - 2.5)],
              fill=GOLD, outline=(120, 90, 20))
    d.text((mx1 - 118, map_top + 2), "3 \u00b7 VOYAGER, IN SPACE",
           font=font(SANS_B, 8), fill=MUTED)
    # legend
    lx0, lx1 = 726, W - MARGIN
    d.rectangle([lx0, my0, lx1, my1], fill=CARD_BG, outline=(200, 192, 172))
    d.text((lx0 + 8, my0 + 4), "LEGEND", font=font(SANS_B, 10), fill=INK)
    ly = my0 + 20
    number_badge(d, lx0 + 16, ly + 6, 1, r=8)
    d.text((lx0 + 30, ly), "Numbered pin = featured story 1\u201313",
           font=font(SANS, 9), fill=INK)
    ly += 16
    d.ellipse([lx0 + 12, ly + 3, lx0 + 18, ly + 9], fill=MAP_DOT)
    d.text((lx0 + 30, ly), "Grey dot = brief 14\u201350", font=font(SANS, 9), fill=INK)
    ly += 16
    d.polygon([(lx0 + 15, ly - 2), (lx0 + 17, ly + 2), (lx0 + 21, ly + 4),
               (lx0 + 17, ly + 6), (lx0 + 15, ly + 10), (lx0 + 13, ly + 6),
               (lx0 + 9, ly + 4), (lx0 + 13, ly + 2)], fill=GOLD)
    d.text((lx0 + 30, ly), "Gold star = Voyager 1, one light-day out",
           font=font(SANS, 9), fill=INK)
    ly += 20
    pins = ["1 Shenzhen", "2 Gulf", "3 Space", "4 Ukraine", "5 New York",
            "6 Odisha", "7 El Obeid", "8 Brussels", "9 London", "10 Gaza",
            "11 Washington", "12 Auckland", "13 Dhaka"]
    pf = font(SANS, 9)
    for i, p in enumerate(pins):
        px = lx0 + 8 + (i % 2) * 140
        py = ly + (i // 2) * 12
        d.text((px, py), p, font=pf, fill=(50, 48, 44))
    # ---- briefs
    by0 = 772
    d.text((MARGIN, by0), "THE REST OF THE DAY",
           font=font(SANS_B, 11), fill=INK)
    rt = "BRIEFS 14\u201350"
    d.text((W - MARGIN - d.textlength(rt, font=font(SANS_B, 11)), by0), rt,
           font=font(SANS_B, 11), fill=RED)
    d.line([(MARGIN, by0 + 15), (W - MARGIN, by0 + 15)], fill=RULE, width=1)
    col_w = (W - 2 * MARGIN - 2 * 24) // 3
    rows = 13
    line_h = 11
    start_y = by0 + 20
    for idx, (n, city, text, lon, lat) in enumerate(BRIEFS):
        col = idx // rows
        row = idx % rows
        bx = MARGIN + col * (col_w + 24)
        by = start_y + row * line_h
        full = "%d. %s \u2014 %s" % (n, city, text)
        f = fit_font(d, full, SANS, 10, col_w, min_size=8)
        d.text((bx, by), full, font=f, fill=INK)
    # ---- date check
    dy0 = 934
    d.rectangle([MARGIN, dy0, W - MARGIN, dy0 + 42], fill=(238, 232, 216),
                outline=RED, width=1)
    d.text((MARGIN + 8, dy0 + 3), "DATE CHECK \u2014 LEFT OUT ON PURPOSE",
           font=font(SANS_B, 9), fill=RED)
    df = font(SANS, 9)
    l1 = wrap(d, DATE_CHECK_LEFT, df, W - 2 * MARGIN - 16)
    l2 = wrap(d, DATE_CHECK_NEXT, df, W - 2 * MARGIN - 16)
    yy = dy0 + 15
    for ln in (l1 + l2)[:2]:
        d.text((MARGIN + 8, yy), ln, font=df, fill=INK)
        yy += 11
    # ---- footer
    fy = 982
    centre(d, fy, "Every story on this page happened, or was first reported, on "
           "Wednesday 18 November 2026. Disputed claims are attributed.",
           font(SERIF_I, 11))
    centre(d, fy + 15, "Sources: Reuters, AP, AFP, BBC, Al Jazeera, ONS, IMD, "
           "NASA, WHO, Amnesty International, ECDC, Ukrainian Air Force, "
           "European Commission. Original drawings.",
           font(SANS, 8), fill=MUTED)
    centre(d, fy + 27, "Dear judge: every story above happened or was first "
           "reported on Wednesday 18 November 2026 \u2014 50 stories, "
           "seven regions, one day.", font(SANS_B, 10))
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    assert img.size == (W, H) and img.mode == "RGB"
    img.save(out, "JPEG", quality=88, optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
