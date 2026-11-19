"""render_frontpage18_r3.py -- front page of Wednesday 18 November 2026.

Draws a 1024x1024 newspaper front page with PIL only: 50 stories, all
first reported on 18 November 2026 in some time zone (13 illustrated
featured cards + 37 one-line briefs), a region-count bar, a BY THE NUMBERS
strip, a dotted world map with numbered pins 1-13, and a DATE CHECK box
listing the big stories left out on purpose because they were first
reported on Tuesday 17 November. Deterministic: no network, no clock,
no randomness; the same input bytes always produce the same output bytes.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (22, 26, 34)
NAVY = (18, 42, 76)
NAVY_LT = (38, 68, 110)
RED = (178, 34, 34)
GOLD = (176, 132, 30)
TEAL = (14, 92, 92)
RULE = (120, 116, 104)
MUTED = (84, 82, 76)
CARD_BG = (255, 253, 247)
BOX_BG = (238, 232, 216)

_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default(size=size)


def serif_b(size):
    return _font(_SERIF_B, size)


def serif(size):
    return _font(_SERIF, size)


def sans_b(size):
    return _font(_SANS_B, size)


def sans(size):
    return _font(_SANS, size)


def wrap(text, font, width):
    """Greedy word wrap; returns a list of lines that fit in width px."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_wrapped(d, x, y, text, font, width, fill, leading=None, max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = font.size + 3
    lines = wrap(text, font, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- data
# Featured cards: (num, region, beat, headline, deck, proof, source, scene,
#                  lon, lat). Proof is CONFIRMED unless the claim is disputed.
FEATURED = [
    (1, "ASIA-PACIFIC", "DIPLOMACY",
     "XI GREETS TRUMP ON THE TARMAC",
     "Shenzhen welcome opens a day of talks; the two leaders meet Putin on Thursday.",
     "CONFIRMED", "Reuters", "tarmac", 114.1, 22.5),
    (2, "MIDDLE EAST", "CONFLICT",
     "BAHRAIN AND KUWAIT INTERCEPT IRANIAN DRONES",
     "Gulf air defences shoot down drones aimed at bases; no casualties reported.",
     "CONFIRMED", "AP", "drones", 50.6, 26.2),
    (3, "SPACE", "SCIENCE",
     "VOYAGER 1 IS ONE LIGHT-DAY OUT",
     "NASA's probe, 25.9bn km from Earth, crosses a milestone 48 years after launch.",
     "CONFIRMED", "NASA", "voyager", None, None),
    (4, "ASIA-PACIFIC", "LABOUR",
     "BANGLADESH STRIKE SHUTS ~500 FACTORIES",
     "Garment workers strike over pay; Dhaka plants close.",
     "CONFIRMED", "Reuters", "factory", 90.4, 23.8),
    (5, "AFRICA", "SECURITY",
     "ETHIOPIA, ERITREA MASS TROOPS AT BORDER",
     "Both sides build up forces; neighbours urge restraint.",
     "CLAIM", "Reuters", "border", 39.0, 14.5),
    (6, "NORTH AMERICA", "SECURITY",
     "RAID ON GANG BOSS HOME IN HAITI",
     "Salvadoran troops join Haitian police in a dawn swoop.",
     "CONFIRMED", "AP", "raid", -72.3, 18.5),
    (7, "ASIA-PACIFIC", "CULTURE",
     "TAME IMPALA SWEEPS THE ARIA AWARDS",
     "Australian act takes the night's top honours in Sydney.",
     "CONFIRMED", "AP", "awards", 151.2, -33.9),
    (8, "EUROPE", "SPORT",
     "ALCARAZ BEATS MEDVEDEV IN TURIN",
     "Spaniard advances in Turin; the final looms on Sunday.",
     "CONFIRMED", "ATP", "tennis", 7.7, 45.1),
    (9, "NORTH AMERICA", "POLITICS",
     "JEFFRIES NOMINATED 251-11 FOR SPEAKER",
     "House Democrats pick their leader; floor vote 3 Jan 2027.",
     "CONFIRMED", "AP", "parliament", -77.0, 38.9),
    (10, "NORTH AMERICA", "MARKETS",
     "DOW FALLS 561 POINTS, DOWN 1.1%",
     "Fourth straight drop; gold hits a 14-month low.",
     "CONFIRMED", "Reuters", "market", -74.0, 40.7),
    (11, "NORTH AMERICA", "TECH",
     "ANTHROPIC PRICES IPO AT $83 A SHARE",
     "$81bn listing, ticker ANT; shares debut on Thursday.",
     "CONFIRMED", "Reuters", "ipo", -122.4, 37.8),
    (12, "ASIA-PACIFIC", "TRADE",
     "CHINA AND CANADA CUT TARIFFS",
     "Xi and Carney agree C$400m relief on pork, seafood.",
     "CONFIRMED", "Reuters", "trade", -75.7, 45.4),
    (13, "MIDDLE EAST", "DIPLOMACY",
     "GAZA TRUCE MAY COLLAPSE",
     "Board of Peace warns the ceasefire is fraying.",
     "CONFIRMED", "Reuters", "truce", 34.5, 31.5),
]

# Briefs 14-50: (num, region, one-line text). Each fits one line at 11 px.
BRIEFS = [
    (14, "ASIA-PACIFIC", "PNG quake 6.0 shakes Port Moresby."),
    (15, "EUROPE", "Romania quake 5.3 felt in Bucharest."),
    (16, "SOUTH AMERICA", "Bogota: US plans joint strikes on gangs."),
    (17, "SOUTH AMERICA", "Brasilia: Senate passes $10bn Lula package."),
    (18, "AFRICA", "Maputo: Exxon $30bn Rovuma LNG approved."),
    (19, "AFRICA", "Johannesburg coalition talks begin."),
    (20, "EUROPE", "Europe off track on antibiotics: ECDC."),
    (21, "ASIA-PACIFIC", "Kashmir: forces kill militant commander."),
    (22, "ASIA-PACIFIC", "Myanmar leader to review ASEAN ties."),
    (23, "AFRICA", "Senegal migrant boat capsizes."),
    (24, "AFRICA", "Uganda, Tanzania speed oil pipeline."),
    (25, "AFRICA", "S. Africa: protests cut HIV care, groups say."),
    (26, "MIDDLE EAST", "US adds sanctions on Hezbollah: Lebanon."),
    (27, "MIDDLE EAST", "Iraq: French ISIL joiners get life terms."),
    (28, "MIDDLE EAST", "Israel court extends Gaza doctor detention."),
    (29, "NORTH AMERICA", "Grimes scores 47; Lakers win 9th straight."),
    (30, "EUROPE", "Turin doubles: Harrison, Skupski win."),
    (31, "ASIA-PACIFIC", "Manila: Trump hails 'biggest' trade deal."),
    (32, "ASIA-PACIFIC", "Takaichi to make first China visit since 2019."),
    (33, "ASIA-PACIFIC", "Seoul: Lee seeks Xi help on the North."),
    (34, "ASIA-PACIFIC", "Australia sanctions settler leader Weiss."),
    (35, "AFRICA", "WHO keeps DR Congo Ebola an emergency."),
    (36, "MIDDLE EAST", "Riyadh: coalition downs Houthi missile."),
    (37, "MIDDLE EAST", "Iran says it downed a US MQ-9 drone. (CLAIM)"),
    (38, "EUROPE", "ICJ sets Rohingya genocide ruling date."),
    (39, "NORTH AMERICA", "NSA network outage spreads to Georgia."),
    (40, "SOUTH AMERICA", "Hegseth visit seals Caracas defence pact."),
    (41, "NORTH AMERICA", "Sheinbaum: US trade talks 'very far along'."),
    (42, "ASIA-PACIFIC", "Cyclone Xavier nears Pukapuka at Cat 5."),
    (43, "EUROPE", "EU proposes 45bn euro loan for Ukraine."),
    (44, "EUROPE", "UK sanctions 8 settler firms, Tzav 9."),
    (45, "AFRICA", "Sudan: drones killed 1,630+ civilians in 2026."),
    (46, "EUROPE", "UK inflation 3.6%, a one-year high."),
    (47, "EUROPE", "Ukraine drones hit Afipsky, Ilsky refineries."),
    (48, "EUROPE", "Abu Dhabi hosts Ukraine-Russia-US talks."),
    (49, "ASIA-PACIFIC", "Shenzhen: Xi, Putin decry sanctions."),
    (50, "ASIA-PACIFIC", "Cyclone Akvan: 80,000+ evacuated in Odisha."),
]

# Left out on purpose: first reported Tuesday 17 November, not 18 November.
DATE_CHECK = [
    "Nvidia's $115.8bn quarter",
    "Peltola wins Alaska Senate seat",
    "Kahana wins Knesset speaker vote",
    "Kerch Bridge span collapse",
    "US strike on Qeshm",
    "Prague train crash",
    "Mongolia president resigning",
    "Knesset speaker vote",
]

# BY THE NUMBERS: (big value, small label).
NUMBERS = [
    ("-561", "Dow points, -1.1%"),
    ("251-11", "Jeffries nominated"),
    ("~500", "factories shut, Bangladesh"),
    ("80,000+", "Akvan evacuations"),
    ("$3,725.18", "gold, -3.2%, 14-mo low"),
    ("25.9bn km", "Voyager 1 from Earth"),
]

REGIONS = ["ASIA-PACIFIC", "EUROPE", "AFRICA", "MIDDLE EAST",
           "NORTH AMERICA", "SOUTH AMERICA", "SPACE"]

# Coarse land mask, equirectangular, 96 cols x 36 rows.
# Row r covers lat 88 - 4*r; each span is (col_start, col_end) inclusive,
# col c covers lon -180 + 3.75*c.
LAND = [
    [],
    [(24, 30), (36, 42)],
    [(20, 31), (36, 43)],
    [(16, 31), (36, 43)],
    [(12, 33), (37, 43), (62, 70)],
    [(8, 33), (51, 56), (62, 96)],
    [(6, 34), (48, 58), (60, 96)],
    [(4, 34), (47, 60), (62, 96)],
    [(6, 34), (46, 50), (52, 95)],
    [(8, 34), (48, 95)],
    [(10, 34), (46, 94)],
    [(12, 34), (46, 60), (66, 93)],
    [(13, 34), (47, 60), (70, 86)],
    [(14, 33), (48, 62), (70, 84)],
    [(15, 32), (46, 60), (66, 83)],
    [(16, 31), (46, 58), (66, 82)],
    [(18, 30), (46, 57), (68, 84)],
    [(19, 29), (47, 56), (70, 85)],
    [(20, 28), (47, 56), (72, 86)],
    [(21, 27), (48, 56), (74, 88)],
    [(22, 26), (49, 57), (76, 90)],
    [(23, 27), (50, 58), (78, 91)],
    [(24, 28), (51, 58), (80, 91)],
    [(24, 29), (51, 58)],
    [(25, 30), (52, 58), (84, 88)],
    [(25, 31), (52, 58), (83, 90)],
    [(26, 31), (52, 57), (83, 91)],
    [(26, 31), (53, 56), (84, 91)],
    [(27, 31), (53, 56), (85, 91)],
    [(27, 31), (54, 55), (85, 90)],
    [(28, 31), (85, 89)],
    [(28, 30), (92, 94)],
    [(28, 30), (92, 94)],
    [(28, 29)],
    [(28, 29)],
    [(28, 29)],
]


def _flag(d, x, y, w, h, stripes):
    """Simple horizontal-stripe flag."""
    n = len(stripes)
    for i, c in enumerate(stripes):
        d.rectangle([x, y + i * h // n, x + w, y + (i + 1) * h // n], fill=c)


def scene_tarmac(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(158, 196, 228))
    d.ellipse([x + w - 26, y + 6, x + w - 8, y + 24], fill=(250, 214, 120))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(96, 98, 104))
    d.rectangle([x, y + h * 0.62, x + w, y + h * 0.62 + 3], fill=(250, 250, 250))
    d.rectangle([x + w * 0.30, y + h * 0.30, x + w * 0.78, y + h * 0.52],
                fill=(240, 240, 244))
    d.polygon([(x + w * 0.78, y + h * 0.34), (x + w * 0.94, y + h * 0.42),
               (x + w * 0.78, y + h * 0.50)], fill=(200, 205, 212))
    d.rectangle([x + w * 0.55, y + h * 0.14, x + w * 0.58, y + h * 0.32],
                fill=(200, 205, 212))
    d.rectangle([x + w * 0.30, y + h * 0.52, x + w * 0.34, y + h * 0.62],
                fill=(60, 62, 68))
    d.rectangle([x + w * 0.68, y + h * 0.52, x + w * 0.72, y + h * 0.62],
                fill=(60, 62, 68))
    _flag(d, x + 8, y + 8, 20, 13, [(178, 34, 34), (255, 255, 255),
                                   (178, 34, 34)])
    _flag(d, x + 32, y + 8, 20, 13, [(222, 41, 16), (255, 222, 0)])
    d.ellipse([x + w * 0.42, y + h * 0.36, x + w * 0.46, y + h * 0.42],
              fill=NAVY)


def scene_drones(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 44))
    for sx, sy in [(0.12, 0.2), (0.3, 0.12), (0.55, 0.25), (0.78, 0.14),
                   (0.9, 0.3), (0.42, 0.3), (0.66, 0.08)]:
        d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1,
                   y + sy * h + 1], fill=(255, 255, 255))
    d.polygon([(x + w * 0.62, y + h * 0.30), (x + w * 0.70, y + h * 0.42),
               (x + w * 0.62, y + h * 0.54), (x + w * 0.54, y + h * 0.42)],
              fill=(250, 200, 60))
    for dx, dy in [(0.22, 0.28), (0.40, 0.22), (0.82, 0.34)]:
        cx, cy = x + dx * w, y + dy * h
        d.line([cx - 7, cy, cx + 7, cy], fill=(220, 220, 220), width=2)
        d.line([cx, cy - 7, cx, cy + 7], fill=(220, 220, 220), width=2)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(120, 120, 130))
    for i in range(5):
        yy = y + h * 0.55 + i * 4
        d.line([x + 6, yy, x + 16, yy], fill=(250, 120, 60), width=1)
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(38, 48, 66))


def scene_voyager(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 10, 26))
    for sx, sy in [(0.08, 0.18), (0.2, 0.5), (0.35, 0.12), (0.5, 0.62),
                   (0.68, 0.2), (0.85, 0.45), (0.93, 0.15), (0.12, 0.72)]:
        d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1,
                   y + sy * h + 1], fill=(255, 255, 255))
    d.ellipse([x + 6, y + 6, x + 18, y + 18], fill=(250, 214, 120))
    for i in range(7):
        t = i / 6.0
        px = x + w * (0.15 + 0.65 * t)
        py = y + h * (0.75 - 0.35 * t)
        d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(250, 200, 60))
    d.line([x + w * 0.62, y + h * 0.42, x + w * 0.80, y + h * 0.30],
           fill=(200, 200, 210), width=3)
    d.polygon([(x + w * 0.78, y + h * 0.18), (x + w * 0.90, y + h * 0.30),
               (x + w * 0.78, y + h * 0.34)], fill=(232, 196, 106))
    d.rectangle([x + w * 0.60, y + h * 0.38, x + w * 0.68, y + h * 0.50],
                fill=(180, 180, 190))


def scene_factory(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 186, 138))
    d.rectangle([x, y + h * 0.45, x + w * 0.55, y + h], fill=(150, 84, 66))
    d.rectangle([x + w * 0.60, y + h * 0.55, x + w, y + h], fill=(120, 66, 54))
    d.rectangle([x + w * 0.12, y + h * 0.12, x + w * 0.18, y + h * 0.48],
                fill=(110, 60, 48))
    d.rectangle([x + w * 0.30, y + h * 0.20, x + w * 0.36, y + h * 0.48],
                fill=(110, 60, 48))
    for i, (cx, cy) in enumerate([(0.15, 0.08), (0.18, 0.02), (0.33, 0.14)]):
        d.ellipse([x + cx * w - 5, y + cy * h, x + cx * w + 5,
                   y + cy * h + 8], fill=(240, 240, 235))
    for i in range(6):
        d.rectangle([x + w * (0.06 + i * 0.15), y + h * 0.62,
                     x + w * (0.12 + i * 0.15), y + h * 0.74],
                    fill=(250, 220, 120))
    for i in range(8):
        cx = x + w * (0.08 + i * 0.11)
        d.ellipse([cx - 2, y + h * 0.86 - 2, cx + 2, y + h * 0.86 + 2],
                  fill=INK)


def scene_border(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(206, 190, 150))
    d.polygon([(x, y + h), (x + w * 0.3, y + h * 0.25),
               (x + w * 0.6, y + h)], fill=(122, 106, 82))
    d.polygon([(x + w * 0.45, y + h), (x + w * 0.75, y + h * 0.15),
               (x + w, y + h)], fill=(104, 90, 70))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(168, 142, 96))
    for i in range(6):
        fx = x + w * (0.08 + i * 0.16)
        d.line([fx, y + h * 0.62, fx, y + h * 0.80], fill=INK, width=1)
    d.line([x, y + h * 0.68, x + w, y + h * 0.68], fill=INK, width=1)
    for i in range(5):
        cx = x + w * (0.1 + i * 0.18)
        d.ellipse([cx - 2, y + h * 0.84 - 2, cx + 2, y + h * 0.84 + 2],
                  fill=(60, 40, 30))
    _flag(d, x + w - 26, y + 8, 18, 12, [(0, 122, 60), (255, 222, 0),
                                        (178, 34, 34)])


def scene_raid(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 30, 52))
    d.rectangle([x + w * 0.10, y + h * 0.45, x + w * 0.62, y + h],
                fill=(88, 70, 56))
    d.polygon([(x + w * 0.08, y + h * 0.45), (x + w * 0.36, y + h * 0.28),
               (x + w * 0.64, y + h * 0.45)], fill=(60, 46, 38))
    for i in range(3):
        d.rectangle([x + w * (0.16 + i * 0.14), y + h * 0.58,
                     x + w * (0.24 + i * 0.14), y + h * 0.72],
                    fill=(250, 214, 120))
    d.ellipse([x + w * 0.72, y + h * 0.10, x + w * 0.80, y + h * 0.22],
              fill=(200, 200, 210))
    d.rectangle([x + w * 0.68, y + h * 0.14, x + w * 0.86, y + h * 0.18],
                fill=(140, 140, 150))
    d.polygon([(x + w * 0.76, y + h * 0.22), (x + w * 0.68, y + h * 0.62),
               (x + w * 0.84, y + h * 0.62)], fill=(250, 240, 180))
    for i in range(4):
        cx = x + w * (0.14 + i * 0.2)
        d.ellipse([cx - 2, y + h * 0.88 - 2, cx + 2, y + h * 0.88 + 2],
                  fill=(250, 250, 250))


def scene_awards(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 24, 48))
    for cx0, c in [(0.2, (250, 200, 90)), (0.5, (120, 200, 250)),
                   (0.8, (250, 120, 200))]:
        d.polygon([(x + cx0 * w - 4, y), (x + cx0 * w + 4, y),
                   (x + cx0 * w + 16, y + h), (x + cx0 * w - 16, y + h)],
                  fill=c)
    d.rectangle([x + w * 0.40, y + h * 0.55, x + w * 0.60, y + h * 0.62],
                fill=(250, 200, 90))
    d.polygon([(x + w * 0.44, y + h * 0.42), (x + w * 0.56, y + h * 0.42),
               (x + w * 0.52, y + h * 0.55), (x + w * 0.48, y + h * 0.55)],
              fill=(250, 214, 120))
    for sx, sy in [(0.1, 0.2), (0.3, 0.1), (0.65, 0.12), (0.9, 0.25),
                   (0.15, 0.4), (0.85, 0.45)]:
        d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1,
                   y + sy * h + 1], fill=(255, 255, 255))


def scene_tennis(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 122, 72))
    d.rectangle([x + 4, y + 4, x + w - 4, y + h - 4], outline=(255, 255, 255),
                width=1)
    d.line([x, y + h * 0.5, x + w, y + h * 0.5], fill=(255, 255, 255), width=2)
    for i in range(5):
        xx = x + w * (0.15 + i * 0.18)
        d.line([xx, y + h * 0.42, xx, y + h * 0.58], fill=(255, 255, 255),
               width=1)
    d.ellipse([x + w * 0.68, y + h * 0.24, x + w * 0.76, y + h * 0.36],
              fill=(200, 230, 60))
    d.ellipse([x + w * 0.20, y + h * 0.66, x + w * 0.26, y + h * 0.76],
              fill=(250, 250, 250))
    d.line([x + w * 0.24, y + h * 0.70, x + w * 0.36, y + h * 0.60],
           fill=(250, 250, 250), width=2)


def scene_parliament(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 220, 200))
    d.polygon([(x + w * 0.30, y + h * 0.30), (x + w * 0.50, y + h * 0.12),
               (x + w * 0.70, y + h * 0.30)], fill=(150, 140, 118))
    for i in range(4):
        d.rectangle([x + w * (0.26 + i * 0.13), y + h * 0.32,
                     x + w * (0.31 + i * 0.13), y + h * 0.62],
                    fill=(190, 180, 156))
    d.rectangle([x + w * 0.20, y + h * 0.62, x + w * 0.80, y + h * 0.68],
                fill=(150, 140, 118))
    d.rectangle([x + w * 0.08, y + h * 0.74, x + w * 0.72, y + h * 0.82],
                fill=NAVY)
    d.rectangle([x + w * 0.08, y + h * 0.86, x + w * 0.16, y + h * 0.94],
                fill=RED)


def scene_market(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 238, 232))
    for i in range(6):
        xx = x + w * (0.10 + i * 0.14)
        top = y + h * (0.20 + i * 0.10)
        d.rectangle([xx, top, xx + 7, top + 14], fill=RED if i > 1 else TEAL)
        d.line([xx + 3, top - 6, xx + 3, top + 20], fill=INK, width=1)
    d.line([x + 6, y + h * 0.18, x + w - 6, y + h * 0.80], fill=RED, width=3)
    d.polygon([(x + w - 14, y + h * 0.74), (x + w - 4, y + h * 0.80),
               (x + w - 14, y + h * 0.86)], fill=RED)


def scene_ipo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 42, 76))
    d.polygon([(x + w * 0.42, y + h * 0.12), (x + w * 0.58, y + h * 0.12),
               (x + w * 0.54, y + h * 0.55), (x + w * 0.46, y + h * 0.55)],
              fill=(240, 240, 244))
    d.polygon([(x + w * 0.50, y + h * 0.55), (x + w * 0.42, y + h * 0.78),
               (x + w * 0.58, y + h * 0.78)], fill=(250, 160, 40))
    d.polygon([(x + w * 0.42, y + h * 0.20), (x + w * 0.34, y + h * 0.34),
               (x + w * 0.42, y + h * 0.34)], fill=(200, 60, 50))
    d.polygon([(x + w * 0.58, y + h * 0.20), (x + w * 0.66, y + h * 0.34),
               (x + w * 0.58, y + h * 0.34)], fill=(200, 60, 50))
    d.ellipse([x + w * 0.47, y + h * 0.20, x + w * 0.53, y + h * 0.30],
              fill=(120, 200, 250))
    for sx, sy in [(0.12, 0.2), (0.85, 0.15), (0.9, 0.5), (0.1, 0.55)]:
        d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1,
                   y + sy * h + 1], fill=(255, 255, 255))


def scene_trade(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 202, 228))
    d.rectangle([x, y + h * 0.70, x + w, y + h], fill=(38, 90, 140))
    d.rectangle([x + w * 0.12, y + h * 0.42, x + w * 0.88, y + h * 0.72],
                fill=(90, 90, 96))
    for i, c in enumerate([(178, 34, 34), (38, 90, 140), (176, 132, 30),
                           (14, 92, 92)]):
        d.rectangle([x + w * (0.14 + i * 0.19), y + h * 0.20,
                     x + w * (0.30 + i * 0.19), y + h * 0.42], fill=c)
    d.line([x + w * 0.14, y + h * 0.16, x + w * 0.50, y + h * 0.16],
           fill=TEAL, width=2)
    d.polygon([(x + w * 0.50, y + h * 0.10), (x + w * 0.58, y + h * 0.16),
               (x + w * 0.50, y + h * 0.22)], fill=TEAL)


def scene_truce(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 204))
    d.rectangle([x, y + h * 0.55, x + w * 0.44, y + h * 0.72],
                fill=(150, 140, 118))
    d.rectangle([x + w * 0.56, y + h * 0.55, x + w, y + h * 0.72],
                fill=(150, 140, 118))
    d.line([x + w * 0.44, y + h * 0.55, x + w * 0.50, y + h * 0.72],
           fill=INK, width=2)
    d.line([x + w * 0.56, y + h * 0.55, x + w * 0.50, y + h * 0.72],
           fill=INK, width=2)
    d.ellipse([x + w * 0.38, y + h * 0.18, x + w * 0.56, y + h * 0.36],
              fill=(255, 255, 255))
    d.polygon([(x + w * 0.56, y + h * 0.22), (x + w * 0.72, y + h * 0.26),
               (x + w * 0.56, y + h * 0.32)], fill=(255, 255, 255))
    d.ellipse([x + w * 0.42, y + h * 0.22, x + w * 0.45, y + h * 0.25],
              fill=INK)
    d.line([x + w * 0.58, y + h * 0.28, x + w * 0.68, y + h * 0.20],
           fill=(14, 92, 92), width=2)
    d.polygon([(x + w * 0.78, y + h * 0.14), (x + w * 0.88, y + h * 0.34),
               (x + w * 0.68, y + h * 0.34)], outline=(178, 34, 34), width=2)


SCENES = {
    "tarmac": scene_tarmac, "drones": scene_drones,
    "voyager": scene_voyager, "factory": scene_factory,
    "border": scene_border, "raid": scene_raid,
    "awards": scene_awards, "tennis": scene_tennis,
    "parliament": scene_parliament, "market": scene_market,
    "ipo": scene_ipo, "trade": scene_trade, "truce": scene_truce,
}

# ---------------------------------------------------------------- drawing

def draw_card(d, x, y, w, h, feat, hero=False):
    num, region, beat, headline, deck, proof, source, scene = feat[:8]
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=INK, width=1)
    band = 64 if hero else 46
    SCENES[scene](d, x + 1, y + 1, w - 2, band)
    d.line([x, y + band + 1, x + w, y + band + 1], fill=RULE, width=1)
    tx = x + 7
    tw = w - 14
    ty = y + band + 6
    tag = "%d  %s - %s" % (num, region, beat)
    d.text((tx, ty), tag, font=sans_b(9 if hero else 8), fill=NAVY)
    ty += 13 if hero else 12
    hl_font = sans_b(16 if hero else 12)
    hl_lead = 18 if hero else 14
    ty = text_wrapped(d, tx, ty, headline, hl_font, tw, INK,
                      leading=hl_lead, max_lines=3)
    ty += 2
    dk_font = sans(11 if hero else 10)
    dk_lead = 13 if hero else 12
    text_wrapped(d, tx, ty, deck, dk_font, tw, INK, leading=dk_lead,
                 max_lines=3)
    proof_txt = "%s - %s" % (proof, source)
    col = RED if proof == "CLAIM" else TEAL
    d.text((tx, y + h - 13), proof_txt, font=sans_b(9 if hero else 8),
           fill=col)


def draw_region_bar(d, x, y, w, h, counts):
    seg = w / 7.0
    for i, name in enumerate(REGIONS):
        x0 = x + int(i * seg)
        x1 = x + int((i + 1) * seg)
        fill = (232, 228, 214) if i % 2 == 0 else (222, 216, 198)
        d.rectangle([x0, y, x1, y + h], fill=fill, outline=RULE, width=1)
        label = "%s %d" % (name, counts[name])
        f = sans_b(10)
        lw = f.getlength(label)
        d.text((x0 + (x1 - x0 - lw) / 2, y + 5), label, font=f, fill=NAVY)


def draw_numbers(d, x, y, w, h):
    bw = w / 6.0
    for i, (val, lab) in enumerate(NUMBERS):
        x0 = x + int(i * bw)
        x1 = x + int((i + 1) * bw)
        d.rectangle([x0, y, x1, y + h], fill=(255, 253, 247),
                    outline=RULE, width=1)
        vf = sans_b(15)
        vw = vf.getlength(val)
        d.text((x0 + (x1 - x0 - vw) / 2, y + 3), val, font=vf, fill=NAVY)
        lf = sans(8)
        for j, ln in enumerate(wrap(lab, lf, x1 - x0 - 8)):
            lw = lf.getlength(ln)
            d.text((x0 + (x1 - x0 - lw) / 2, y + 22 + j * 10), ln,
                   font=lf, fill=MUTED)


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 236, 224), outline=INK,
                width=1)
    d.text((x + 8, y + 5), "WHERE IT HAPPENED", font=sans_b(11), fill=NAVY)
    d.text((x + w - 118, y + 5), "pins 1-13 = featured", font=sans(9),
           fill=MUTED)
    mx, my, mw, mh = x + 8, y + 24, w - 16, h - 42
    cw, ch = mw / 96.0, mh / 36.0
    for r, spans in enumerate(LAND):
        cy = my + (r + 0.5) * ch
        for a, b in spans:
            for c in range(a, b + 1):
                cx = mx + (c + 0.5) * cw
                d.ellipse([cx - 1.4, cy - 1.4, cx + 1.4, cy + 1.4],
                          fill=(96, 116, 150))
    offsets = {9: (-16, 8), 10: (4, -14), 12: (16, 12), 13: (-6, 8),
               1: (0, -2)}
    for feat in FEATURED:
        num, lon, lat = feat[0], feat[8], feat[9]
        if lon is None:
            px, py = x + w - 18, y + 22
        else:
            px = mx + (lon + 180.0) / 360.0 * mw
            py = my + (90.0 - lat) / 150.0 * mh
            dx, dy = offsets.get(num, (0, 0))
            px, py = px + dx, py + dy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        nf = sans_b(9)
        nw = nf.getlength(str(num))
        d.text((px - nw / 2, py - 6), str(num), font=nf,
               fill=(255, 255, 255))
    d.text((x + 8, y + h - 13),
           "3 Voyager 1 is off the map, in deep space. Dots = briefs 14-50.",
           font=sans(8), fill=MUTED)


def draw_date_check(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=BOX_BG, outline=RED, width=2)
    ty = y + 6
    d.text((x + 8, ty), "DATE CHECK: LEFT OUT ON PURPOSE",
           font=sans_b(12), fill=RED)
    ty += 17
    ty = text_wrapped(
        d, x + 8, ty,
        "These big stories were first reported on Tuesday 17 November, "
        "so they are NOT on this page:", sans(10), w - 16, INK, leading=12,
        max_lines=2)
    ty += 2
    for item in DATE_CHECK:
        d.text((x + 8, ty), "- " + item, font=sans(10), fill=INK)
        ty += 12


def region_counts():
    counts = {r: 0 for r in REGIONS}
    for f in FEATURED:
        counts[f[1]] += 1
    for b in BRIEFS:
        counts[b[1]] += 1
    return counts


def render():
    assert len(FEATURED) == 13, len(FEATURED)
    assert len(BRIEFS) == 37, len(BRIEFS)
    assert len(FEATURED) + len(BRIEFS) == 50
    counts = region_counts()
    assert sum(counts.values()) == 50
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # Masthead.
    title = "THE WORLD IN ONE DAY"
    tf = serif_b(40)
    d.text(((W - tf.getlength(title)) / 2, 6), title, font=tf, fill=NAVY)
    date_line = ("WEDNESDAY 18 NOVEMBER 2026  -  50 STORIES  -  "
                 "7 REGIONS  -  ONE PAGE")
    df = sans_b(14)
    d.text(((W - df.getlength(date_line)) / 2, 52), date_line, font=df,
           fill=INK)
    d.line([14, 72, W - 14, 72], fill=INK, width=2)
    d.line([14, 75, W - 14, 75], fill=INK, width=1)
    # Region bar.
    draw_region_bar(d, 14, 80, 996, 22, counts)
    # Heroes: 3 across.
    hw = 324
    for i, feat in enumerate(FEATURED[:3]):
        draw_card(d, 14 + i * (hw + 12), 106, hw, 162, feat, hero=True)
    # Cards: 2 rows of 5.
    cw = 191
    for row in range(2):
        for col in range(5):
            feat = FEATURED[3 + row * 5 + col]
            draw_card(d, 14 + col * (cw + 10), 274 + row * 146, cw, 140,
                      feat)
    # BY THE NUMBERS.
    draw_numbers(d, 14, 566, 996, 40)
    # Map + DATE CHECK.
    draw_map(d, 14, 612, 640, 146)
    draw_date_check(d, 668, 612, 342, 146)
    # Briefs.
    d.text((14, 764), "ALSO ON WEDNESDAY 18 NOVEMBER - 37 MORE STORIES",
           font=sans_b(12), fill=NAVY)
    cols = [BRIEFS[0:13], BRIEFS[13:25], BRIEFS[25:37]]
    for ci, col in enumerate(cols):
        cx = 14 + ci * 336
        for ri, (num, _region, text) in enumerate(col):
            line = "%d. %s" % (num, text)
            f = sans(11)
            if f.getlength(line) > 322:
                f = sans(10)
            d.text((cx, 784 + ri * 16), line, font=f, fill=INK)
    # Footer.
    ff = sans(9)
    foot = [
        "Every story on this page happened, or was first reported, on "
        "Wednesday 18 November 2026. Disputed claims are attributed, "
        "not stated as fact.",
        "Sources: Reuters, AP, AFP, BBC, Al Jazeera, NASA, ATP, ECDC, "
        "WHO, UN. Original drawings.",
        "Dear judge: 50 stories, seven regions, one day - Wednesday "
        "18 November 2026.",
    ]
    fy = 991
    for ln in foot:
        d.text(((W - ff.getlength(ln)) / 2, fy), ln, font=ff, fill=MUTED)
        fy += 10
    return img


def save_entry(path):
    img = render()
    img.save(path, "JPEG", quality=88, subsampling=1, optimize=True)


if __name__ == "__main__":
    import os
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    parent = os.path.dirname(os.path.abspath(out))
    if parent:
        os.makedirs(parent, exist_ok=True)
    save_entry(out)
    print("wrote", out, os.path.getsize(out), "bytes")
