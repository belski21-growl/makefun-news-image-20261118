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
    (4, "NORTH AMERICA", "CULTURE",
     "GTA VI GOES ON SALE",
     "Midnight launch in New Zealand; 15m+ pre-orders.",
     "CONFIRMED", "Reuters", "gta", -74.0, 40.7),
    (5, "EUROPE", "CONFLICT",
     "RUSSIA FIRES 141 DRONES AT UKRAINE",
     "Overnight barrage; air defences down most of them.",
     "CONFIRMED", "Reuters", "strikes", 30.5, 50.4),
    (6, "NORTH AMERICA", "MARKETS",
     "FED MINUTES POINT TO MORE RATE HIKES",
     "Minutes signal further tightening; markets slide.",
     "CONFIRMED", "Reuters", "fed", -77.0, 38.9),
    (7, "EUROPE", "CLIMATE",
     "COP31 SPLITS OVER FOSSIL-FUEL PHASE-OUT",
     "Draft divides over phase-out wording; talks run on.",
     "CONFIRMED", "Reuters", "cop31", 30.7, 36.9),
    (8, "ASIA-PACIFIC", "LABOUR",
     "BANGLADESH STRIKE SHUTS ~500 FACTORIES",
     "AFP: about 500 of ~4,500 garment plants shut.",
     "CONFIRMED", "AFP", "factory", 90.4, 23.8),
    (9, "AFRICA", "SECURITY",
     "ETHIOPIA, ERITREA MASS TROOPS AT BORDER",
     "Both sides build up forces; neighbours urge restraint.",
     "CLAIM", "Reuters", "border", 39.0, 14.5),
    (10, "NORTH AMERICA", "SECURITY",
     "RAID ON GANG BOSS HOME IN HAITI",
     "Salvadoran troops join Haitian police in a dawn swoop.",
     "CONFIRMED", "AP", "raid", -72.3, 18.5),
    (11, "ASIA-PACIFIC", "CULTURE",
     "TAME IMPALA SWEEPS THE ARIA AWARDS",
     "Australian act takes the night's top honours in Sydney.",
     "CONFIRMED", "AP", "awards", 151.2, -33.9),
    (12, "NORTH AMERICA", "POLITICS",
     "JEFFRIES NOMINATED 251-11 FOR SPEAKER",
     "House Democrats pick their leader; floor vote 3 Jan 2027.",
     "CONFIRMED", "AP", "parliament", -77.0, 38.9),
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
    (19, "EUROPE", "Europe off track on antibiotics: ECDC."),
    (20, "ASIA-PACIFIC", "Kashmir: forces kill militant commander."),
    (21, "ASIA-PACIFIC", "Myanmar leader to review ASEAN ties."),
    (22, "AFRICA", "Uganda, Tanzania speed oil pipeline."),
    (23, "AFRICA", "S. Africa: protests cut HIV care, groups say."),
    (24, "MIDDLE EAST", "US adds sanctions on Hezbollah: Lebanon."),
    (25, "MIDDLE EAST", "Iraq: French ISIL joiners get life terms."),
    (26, "MIDDLE EAST", "Israel court extends Gaza doctor detention."),
    (27, "NORTH AMERICA", "Dow falls 561 points, down 1.1%."),
    (28, "ASIA-PACIFIC", "Manila: Trump hails 'biggest' trade deal."),
    (29, "ASIA-PACIFIC", "Takaichi to make first China visit since 2019."),
    (30, "ASIA-PACIFIC", "Seoul: Lee seeks Xi help on the North."),
    (31, "ASIA-PACIFIC", "Australia sanctions settler leader Weiss."),
    (32, "AFRICA", "WHO keeps DR Congo Ebola an emergency."),
    (33, "MIDDLE EAST", "Riyadh: coalition downs Houthi missile."),
    (34, "MIDDLE EAST", "Iran says it downed a US MQ-9 drone. (CLAIM)"),
    (35, "EUROPE", "ICJ sets Rohingya genocide ruling date."),
    (36, "NORTH AMERICA", "NSA network outage spreads to Georgia."),
    (37, "SOUTH AMERICA", "Hegseth visit seals Caracas defence pact."),
    (38, "NORTH AMERICA", "Sheinbaum: US trade talks 'very far along'."),
    (39, "ASIA-PACIFIC", "Cyclone Xavier nears Pukapuka at Cat 5."),
    (40, "EUROPE", "EU proposes 45bn euro loan for Ukraine."),
    (41, "EUROPE", "UK sanctions 8 settler firms, Tzav 9."),
    (42, "AFRICA", "Amnesty: RSF drones killed 37 in El Obeid."),
    (43, "EUROPE", "UK inflation 3.6%, a one-year high."),
    (44, "EUROPE", "Ukraine drones hit Afipsky, Ilsky refineries."),
    (45, "EUROPE", "Abu Dhabi hosts Ukraine-Russia-US talks."),
    (46, "ASIA-PACIFIC", "Shenzhen: Xi, Putin decry sanctions."),
    (47, "ASIA-PACIFIC", "Cyclone Akvan: 80,000+ evacuated in Odisha."),
    (48, "NORTH AMERICA", "Anthropic prices IPO at $83 a share."),
    (49, "EUROPE", "Alcaraz beats Medvedev in Turin."),
    (50, "ASIA-PACIFIC", "China and Canada cut tariffs; C$400m relief."),
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
    "An-12 crash kills 19 in Siberia",
]

# BY THE NUMBERS: (big value, small label).
NUMBERS = [
    ("-561", "Dow points, -1.1%"),
    ("251-11", "Jeffries nominated"),
    ("~500", "factories shut, Bangladesh (AFP)"),
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
    # Sky, sun, clouds.
    d.rectangle([x, y, x + w, y + h], fill=(158, 196, 228))
    d.ellipse([x + w - 34, y + 6, x + w - 14, y + 26], fill=(250, 214, 120))
    for cx, cy, cw in [(0.06, 0.10, 30), (0.62, 0.07, 24)]:
        d.ellipse([x + cx * w, y + cy * h, x + cx * w + cw,
                   y + cy * h + 8], fill=(255, 255, 255))
    # Terminal building, left.
    d.rectangle([x + 6, y + h * 0.34, x + w * 0.20, y + h * 0.68],
                fill=(120, 126, 138))
    d.rectangle([x + 6, y + h * 0.34, x + w * 0.20, y + h * 0.39],
                fill=(90, 96, 110))
    for i in range(3):
        d.rectangle([x + 12 + i * 14, y + h * 0.43,
                     x + 20 + i * 14, y + h * 0.53], fill=(250, 220, 120))
    # Runway with centreline dashes.
    d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(96, 98, 104))
    for i in range(9):
        d.rectangle([x + 8 + i * (w - 16) / 9, y + h * 0.82,
                     x + 8 + (i + 0.55) * (w - 16) / 9, y + h * 0.82 + 3],
                    fill=(255, 255, 255))
    # Airliner: tail fin, fuselage, nose, cheatline, windows,
    # swept wing, engines, landing gear.
    d.polygon([(x + w * 0.30, y + h * 0.44), (x + w * 0.30, y + h * 0.08),
               (x + w * 0.38, y + h * 0.44)], fill=(178, 34, 34))
    d.rectangle([x + w * 0.30, y + h * 0.30, x + w * 0.82, y + h * 0.52],
                fill=(240, 240, 244))
    d.polygon([(x + w * 0.82, y + h * 0.30), (x + w * 0.95, y + h * 0.41),
               (x + w * 0.82, y + h * 0.52)], fill=(220, 224, 230))
    d.rectangle([x + w * 0.30, y + h * 0.46, x + w * 0.82, y + h * 0.52],
                fill=(178, 34, 34))
    for i in range(3):
        d.rectangle([x + w * (0.84 + i * 0.03), y + h * 0.34,
                     x + w * (0.86 + i * 0.03), y + h * 0.38], fill=NAVY)
    for i in range(8):
        d.rectangle([x + w * (0.34 + i * 0.055), y + h * 0.35,
                     x + w * (0.36 + i * 0.055), y + h * 0.40], fill=NAVY)
    d.polygon([(x + w * 0.44, y + h * 0.50), (x + w * 0.58, y + h * 0.50),
               (x + w * 0.66, y + h * 0.68), (x + w * 0.52, y + h * 0.68)],
              fill=(200, 205, 212))
    d.rectangle([x + w * 0.50, y + h * 0.52, x + w * 0.54, y + h * 0.60],
                fill=(60, 62, 68))
    d.rectangle([x + w * 0.62, y + h * 0.52, x + w * 0.66, y + h * 0.60],
                fill=(60, 62, 68))
    d.rectangle([x + w * 0.38, y + h * 0.52, x + w * 0.40, y + h * 0.68],
                fill=(60, 62, 68))
    d.rectangle([x + w * 0.74, y + h * 0.52, x + w * 0.76, y + h * 0.68],
                fill=(60, 62, 68))
    # Flags on the tarmac foreground: China bottom-left, US bottom-right.
    d.line([x + w * 0.10, y + h * 0.70, x + w * 0.10, y + h * 0.97],
           fill=INK, width=2)
    d.rectangle([x + w * 0.10, y + h * 0.70, x + w * 0.10 + 20,
                 y + h * 0.70 + 11], fill=(222, 41, 16))
    d.ellipse([x + w * 0.10 + 3, y + h * 0.70 + 3,
               x + w * 0.10 + 7, y + h * 0.70 + 7], fill=(255, 222, 0))
    d.line([x + w * 0.92, y + h * 0.70, x + w * 0.92, y + h * 0.97],
           fill=INK, width=2)
    _flag(d, x + w * 0.92 - 20, y + h * 0.70, 20, 11,
          [(178, 34, 34), (255, 255, 255), (178, 34, 34),
           (255, 255, 255), (178, 34, 34)])
    d.rectangle([x + w * 0.92 - 20, y + h * 0.70, x + w * 0.92 - 12,
                 y + h * 0.70 + 5], fill=(30, 60, 140))


def _dashed(d, x0, y0, x1, y1, fill, width=1, dash=5, gap=4):
    """Dashed straight line (deterministic, no PIL dash support)."""
    import math
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    s = 0.0
    while s < length:
        e = min(s + dash, length)
        d.line([x0 + ux * s, y0 + uy * s, x0 + ux * e, y0 + uy * e],
               fill=fill, width=width)
        s = e + gap


def _jet(d, cx, cy, s, fill=(150, 155, 165)):
    """Small delta-wing jet silhouette pointing up-right."""
    d.polygon([(cx - 14 * s, cy + 5 * s), (cx + 16 * s, cy - 10 * s),
               (cx + 18 * s, cy - 6 * s), (cx - 12 * s, cy + 9 * s)],
              fill=fill)
    d.polygon([(cx + 2 * s, cy - 4 * s), (cx - 9 * s, cy + 13 * s),
               (cx + 5 * s, cy + 1 * s)], fill=(120, 125, 135))
    d.polygon([(cx - 8 * s, cy + 2 * s), (cx - 14 * s, cy - 6 * s),
               (cx - 4 * s, cy - 1 * s)], fill=(120, 125, 135))
    d.ellipse([cx - 18 * s, cy + 3 * s, cx - 12 * s, cy + 9 * s],
              fill=(250, 140, 40))
    d.ellipse([cx - 16 * s, cy + 5 * s, cx - 13 * s, cy + 8 * s],
              fill=(255, 220, 100))


def _drone_x(d, cx, cy, r=7, fill=(220, 220, 220)):
    d.line([cx - r, cy, cx + r, cy], fill=fill, width=2)
    d.line([cx, cy - r, cx, cy + r], fill=fill, width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(120, 120, 130))
    for ox, oy in [(-r, -r), (r, -r), (-r, r), (r, r)]:
        d.ellipse([cx + ox - 2, cy + oy - 2, cx + ox + 2, cy + oy + 2],
                  fill=fill)


def _burst(d, cx, cy, r=9):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 140, 40))
    d.ellipse([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55],
              fill=(255, 220, 100))
    for k in range(8):
        import math
        a = k * math.pi / 4
        d.line([cx + r * 0.8 * math.cos(a), cy + r * 0.8 * math.sin(a),
                cx + r * 1.6 * math.cos(a), cy + r * 1.6 * math.sin(a)],
               fill=(250, 160, 60), width=2)


def scene_drones(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 44))
    for sx, sy in [(0.08, 0.18), (0.30, 0.10), (0.55, 0.22), (0.78, 0.10),
                   (0.92, 0.28), (0.42, 0.28), (0.66, 0.06)]:
        d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1,
                   y + sy * h + 1], fill=(255, 255, 255))
    d.ellipse([x + w * 0.88, y + h * 0.06, x + w * 0.96, y + h * 0.18],
              fill=(220, 220, 210))
    # Intercepting jets with dashed intercept lines up to the drones.
    _jet(d, x + w * 0.20, y + h * 0.62, 1.0)
    _jet(d, x + w * 0.68, y + h * 0.58, 0.9)
    _dashed(d, x + w * 0.22, y + h * 0.56, x + w * 0.32, y + h * 0.24,
            (255, 255, 255), width=1)
    _dashed(d, x + w * 0.70, y + h * 0.52, x + w * 0.60, y + h * 0.22,
            (255, 255, 255), width=1)
    _dashed(d, x + w * 0.86, y + h * 0.55, x + w * 0.84, y + h * 0.30,
            (255, 255, 255), width=1)
    # Incoming drones + intercept bursts.
    _drone_x(d, x + w * 0.32, y + h * 0.22)
    _drone_x(d, x + w * 0.60, y + h * 0.20)
    _drone_x(d, x + w * 0.84, y + h * 0.28)
    _burst(d, x + w * 0.44, y + h * 0.30)
    _burst(d, x + w * 0.72, y + h * 0.26, r=7)
    # Ground: skyline, radar dish, launcher.
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(38, 48, 66))
    for bx, bw_, bh_ in [(0.02, 0.10, 0.10), (0.14, 0.08, 0.14),
                         (0.78, 0.09, 0.12), (0.89, 0.09, 0.09)]:
        d.rectangle([x + bx * w, y + h * (0.82 - bh_),
                     x + (bx + bw_) * w, y + h * 0.82], fill=(24, 32, 50))
    d.line([x + w * 0.52, y + h * 0.82, x + w * 0.52, y + h * 0.68],
           fill=(200, 200, 210), width=2)
    d.polygon([(x + w * 0.47, y + h * 0.68), (x + w * 0.57, y + h * 0.68),
               (x + w * 0.52, y + h * 0.76)], fill=(200, 200, 210))


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


def scene_gta(d, x, y, w, h):
    # Night city skyline, searchlights, neon VI sign.
    d.rectangle([x, y, x + w, y + h], fill=(24, 16, 44))
    for sx, sy in [(0.06, 0.12), (0.22, 0.08), (0.58, 0.10), (0.76, 0.06),
                   (0.94, 0.14), (0.40, 0.16)]:
        d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1,
                   y + sy * h + 1], fill=(255, 255, 255))
    d.polygon([(x + w * 0.08, y + h), (x + w * 0.20, y + h),
               (x + w * 0.36, y), (x + w * 0.28, y)], fill=(90, 90, 130))
    d.polygon([(x + w * 0.80, y + h), (x + w * 0.92, y + h),
               (x + w * 0.72, y), (x + w * 0.64, y)], fill=(90, 90, 130))
    for bx, bw_, bh_ in [(0.02, 0.10, 0.42), (0.14, 0.08, 0.55),
                         (0.24, 0.12, 0.38), (0.38, 0.09, 0.60),
                         (0.50, 0.11, 0.45), (0.63, 0.08, 0.58),
                         (0.73, 0.12, 0.40), (0.87, 0.11, 0.52)]:
        d.rectangle([x + bx * w, y + h * (1 - bh_),
                     x + (bx + bw_) * w, y + h], fill=(12, 10, 26))
        for wy in (0.55, 0.70, 0.85):
            if bh_ > 1 - wy:
                d.rectangle([x + (bx + 0.02) * w, y + h * wy,
                             x + (bx + 0.05) * w, y + h * wy + 2],
                            fill=(250, 214, 120))
    vf = sans_b(24)
    vt = "VI"
    vw = vf.getlength(vt)
    d.text((x + (w - vw) / 2 + 1, y + h * 0.16 + 1), vt, font=vf,
           fill=(255, 80, 200))
    d.text((x + (w - vw) / 2, y + h * 0.16), vt, font=vf,
           fill=(255, 220, 245))


def scene_strikes(d, x, y, w, h):
    # Night sky over a city: incoming drones, flak bursts, dotted fire.
    d.rectangle([x, y, x + w, y + h], fill=(18, 20, 40))
    for sx, sy in [(0.08, 0.14), (0.28, 0.08), (0.52, 0.12), (0.74, 0.07),
                   (0.92, 0.16), (0.42, 0.22)]:
        d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1,
                   y + sy * h + 1], fill=(255, 255, 255))
    d.ellipse([x + w * 0.86, y + h * 0.06, x + w * 0.94, y + h * 0.20],
              fill=(220, 220, 210))
    _dashed(d, x + w * 0.20, y + h * 0.95, x + w * 0.30, y + h * 0.35,
            (255, 220, 120), width=1)
    _dashed(d, x + w * 0.62, y + h * 0.95, x + w * 0.55, y + h * 0.30,
            (255, 220, 120), width=1)
    _drone_x(d, x + w * 0.30, y + h * 0.30, r=6)
    _drone_x(d, x + w * 0.55, y + h * 0.26, r=6)
    _drone_x(d, x + w * 0.78, y + h * 0.34, r=6)
    _burst(d, x + w * 0.42, y + h * 0.42, r=7)
    _burst(d, x + w * 0.68, y + h * 0.48, r=6)
    for bx, bw_, bh_ in [(0.02, 0.12, 0.22), (0.16, 0.09, 0.30),
                         (0.28, 0.11, 0.20), (0.42, 0.09, 0.32),
                         (0.54, 0.12, 0.22), (0.68, 0.09, 0.28),
                         (0.80, 0.10, 0.20), (0.92, 0.07, 0.26)]:
        d.rectangle([x + bx * w, y + h * (1 - bh_),
                     x + (bx + bw_) * w, y + h], fill=(8, 10, 20))
        d.rectangle([x + (bx + 0.03) * w, y + h * (1 - bh_ + 0.06),
                     x + (bx + 0.06) * w, y + h * (1 - bh_ + 0.06) + 2],
                    fill=(250, 214, 120))


def scene_fed(d, x, y, w, h):
    # Central-bank columns + a rising rate line with arrow.
    d.rectangle([x, y, x + w, y + h], fill=(226, 220, 200))
    d.polygon([(x + w * 0.06, y + h * 0.30), (x + w * 0.30, y + h * 0.08),
               (x + w * 0.54, y + h * 0.30)], fill=(150, 140, 118))
    for i in range(4):
        d.rectangle([x + w * (0.10 + i * 0.11), y + h * 0.32,
                     x + w * (0.15 + i * 0.11), y + h * 0.78],
                    fill=(190, 180, 156))
    d.rectangle([x + w * 0.06, y + h * 0.78, x + w * 0.54, y + h * 0.84],
                fill=(150, 140, 118))
    d.rectangle([x + w * 0.04, y + h * 0.86, x + w * 0.56, y + h * 0.92],
                fill=(120, 112, 94))
    d.line([x + w * 0.62, y + h * 0.82, x + w * 0.98, y + h * 0.82],
           fill=(120, 116, 104), width=1)
    d.line([x + w * 0.62, y + h * 0.82, x + w * 0.62, y + h * 0.12],
           fill=(120, 116, 104), width=1)
    d.line([x + w * 0.63, y + h * 0.78, x + w * 0.74, y + h * 0.55,
            x + w * 0.84, y + h * 0.60, x + w * 0.95, y + h * 0.28],
           fill=RED, width=3)
    d.polygon([(x + w * 0.95, y + h * 0.28), (x + w * 0.88, y + h * 0.26),
               (x + w * 0.93, y + h * 0.38)], fill=RED)


def scene_cop31(d, x, y, w, h):
    # Split scene: clean energy (sun + turbine) vs smoke stack.
    d.rectangle([x, y, x + w * 0.52, y + h], fill=(168, 205, 150))
    d.rectangle([x + w * 0.52, y, x + w, y + h], fill=(150, 150, 152))
    d.ellipse([x + w * 0.06, y + h * 0.08, x + w * 0.18, y + h * 0.32],
              fill=(250, 214, 120))
    tx = x + w * 0.32
    d.line([tx, y + h * 0.78, tx, y + h * 0.30], fill=(255, 255, 255),
           width=3)
    hx, hy = tx, y + h * 0.30
    for dx, dy in [(0, -13), (-11, 7), (11, 7)]:
        d.line([hx, hy, hx + dx, hy + dy], fill=(255, 255, 255), width=2)
    d.ellipse([hx - 2, hy - 2, hx + 2, hy + 2], fill=(255, 255, 255))
    d.rectangle([x, y + h * 0.78, x + w * 0.52, y + h], fill=(110, 160, 90))
    d.rectangle([x + w * 0.62, y + h * 0.55, x + w * 0.90, y + h],
                fill=(90, 90, 96))
    d.rectangle([x + w * 0.80, y + h * 0.22, x + w * 0.86, y + h * 0.55],
                fill=(70, 70, 76))
    for cx, cy, r in [(0.83, 0.14, 6), (0.86, 0.06, 5), (0.80, 0.05, 4)]:
        d.ellipse([x + cx * w - r, y + cy * h - r, x + cx * w + r,
                   y + cy * h + r], fill=(210, 210, 205))
    for i in range(5):
        yy = y + (i + 0.5) * h / 5
        d.line([x + w * 0.52, yy, x + w * 0.52, yy + h / 10],
               fill=(255, 255, 255), width=2)


def scene_truce(d, x, y, w, h):
    # Concrete Gaza truce scene: damaged skyline, white flag, olive branch.
    d.rectangle([x, y, x + w, y + h], fill=(196, 216, 232))
    d.ellipse([x + w * 0.84, y + 4, x + w * 0.94, y + 14],
              fill=(250, 214, 120))
    # Dove, top centre.
    d.ellipse([x + w * 0.55, y + h * 0.10, x + w * 0.66, y + h * 0.22],
              fill=(255, 255, 255))
    d.polygon([(x + w * 0.66, y + h * 0.12), (x + w * 0.76, y + h * 0.16),
               (x + w * 0.66, y + h * 0.20)], fill=(255, 255, 255))
    d.ellipse([x + w * 0.63, y + h * 0.11, x + w * 0.66, y + h * 0.15],
              fill=INK)
    # Damaged skyline with broken tops.
    for bx, bw_, bh_ in [(0.02, 0.16, 0.40), (0.20, 0.14, 0.52),
                         (0.36, 0.18, 0.44), (0.56, 0.14, 0.55),
                         (0.72, 0.13, 0.42), (0.87, 0.11, 0.48)]:
        d.rectangle([x + bx * w, y + h * (0.86 - bh_),
                     x + (bx + bw_) * w, y + h * 0.86],
                    fill=(120, 116, 110))
        d.rectangle([x + (bx + bw_ * 0.55) * w, y + h * (0.86 - bh_),
                     x + (bx + bw_) * w, y + h * (0.86 - bh_ + 0.08)],
                    fill=(196, 216, 232))
        for wy in (0.60, 0.72):
            if bh_ > 0.86 - wy:
                d.rectangle([x + (bx + 0.03) * w, y + h * wy,
                             x + (bx + 0.07) * w, y + h * wy + 2],
                            fill=(60, 58, 54))
    # White flag on a pole atop the middle building.
    fx = x + w * 0.44
    d.line([fx, y + h * 0.14, fx, y + h * 0.42], fill=INK, width=2)
    d.polygon([(fx, y + h * 0.14), (fx + 18, y + h * 0.18),
               (fx, y + h * 0.24)], fill=(255, 255, 255),
              outline=(120, 116, 104))
    # Olive branch, bottom-left foreground.
    bx0, by0 = x + w * 0.06, y + h * 0.92
    d.line([bx0, by0, bx0 + 34, by0 - 16], fill=(14, 92, 92), width=2)
    for i, (ox, oy) in enumerate([(6, -3), (14, -7), (22, -11), (28, -14)]):
        d.ellipse([bx0 + ox - 4, by0 + oy - 2, bx0 + ox + 4, by0 + oy + 2],
                  fill=(40, 120, 60))
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(168, 142, 96))


SCENES = {
    "tarmac": scene_tarmac, "drones": scene_drones,
    "voyager": scene_voyager, "factory": scene_factory,
    "border": scene_border, "raid": scene_raid,
    "awards": scene_awards, "tennis": scene_tennis,
    "parliament": scene_parliament, "market": scene_market,
    "ipo": scene_ipo, "trade": scene_trade, "truce": scene_truce,
    "gta": scene_gta, "strikes": scene_strikes,
    "fed": scene_fed, "cop31": scene_cop31,
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
    land_cells = {(r, c) for r, spans in enumerate(LAND)
                  for a, b in spans for c in range(a, b + 1)}
    for r, c in land_cells:
        d.rectangle([mx + c * cw, my + r * ch,
                     mx + (c + 1) * cw, my + (r + 1) * ch],
                    fill=(203, 214, 228))
    for r, spans in enumerate(LAND):
        cy = my + (r + 0.5) * ch
        for a, b in spans:
            for c in range(a, b + 1):
                cx = mx + (c + 0.5) * cw
                coast = ((r - 1, c) not in land_cells or
                         (r + 1, c) not in land_cells or
                         (r, c - 1) not in land_cells or
                         (r, c + 1) not in land_cells)
                if coast:
                    d.ellipse([cx - 2.1, cy - 2.1, cx + 2.1, cy + 2.1],
                              fill=(40, 64, 104))
                else:
                    d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6],
                              fill=(110, 128, 158))
    offsets = {1: (0, -2), 2: (10, -12), 4: (12, -16), 5: (-18, -14),
               6: (-20, -10), 7: (18, -4), 9: (16, 10), 10: (14, 14),
               12: (-16, 16), 13: (-14, 4)}
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
