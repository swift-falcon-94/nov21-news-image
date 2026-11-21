#!/usr/bin/env python3
"""The World Today - 21 November 2026: one dense front page, drawn in code.

The picture sums up Saturday
21 November 2026 in 54 verified stories across 6 continents, and it is
drawn entirely by this program: no photos, no downloaded assets, no
network. It renders at twice the final size and averages each 2x2 block
down, so the small print stays crisp; the lettering is a hand-made 5x7
bitmap face for body copy and a 12x16 stroke face for the masthead.
Run it twice and the PNG bytes are identical.

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import math
import os
import struct
import zlib

# ---------------------------------------------------------------- palette
INK = (13, 27, 46)        # page background
CARD = (20, 40, 64)       # story card background
CARD2 = (25, 50, 76)      # picture panel inside a card
PAPER = (236, 241, 246)   # main text
FAINT = (148, 168, 184)   # secondary text
LINE = (47, 79, 112)      # hairlines and card borders
GOLD = (246, 196, 69)     # accents, numbers, timeline
SKY = (96, 165, 250)      # sea and links
RED = (239, 68, 68)       # alerts and losses
GREEN = (34, 197, 94)     # gains and ok states
LANDC = (46, 111, 86)     # continents on the map
SEA = (16, 36, 58)        # ocean on the map

# ---------------------------------------------------------------- 5x7 face
# Seven rows of five bits per glyph; a "#" is a lit pixel.
_FACE = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ':': ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ';': ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    '-': ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    '+': ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '"': ["01010", "01010", "00000", "00000", "00000", "00000", "00000"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    '$': ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '<': ["00010", "00100", "01000", "10000", "01000", "00100", "00010"],
    '>': ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
    '_': ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    '*': ["00000", "00100", "10101", "01110", "10101", "00100", "00000"],
    '#': ["01010", "01010", "11111", "01010", "11111", "01010", "01010"],
    '@': ["01110", "10001", "10111", "10101", "10110", "10000", "01110"],
    '[': ["01110", "01000", "01000", "01000", "01000", "01000", "01110"],
    ']': ["01110", "00010", "00010", "00010", "00010", "00010", "01110"],
    '\u2022': ["00000", "00000", "01100", "01100", "01100", "00000", "00000"],
}

# ------------------------------------------------------- 12x16 stroke face
# Each glyph is a list of strokes; a stroke is a list of (x, y) points in a
# 12-wide, 16-tall cell, drawn as straight segments between the points.
_STROKES = {
    'A': [[(0, 15), (0, 0), (6, 0), (12, 15)], [(3, 6), (9, 6)]],
    'B': [[(0, 15), (0, 0), (9, 0), (12, 3), (9, 7), (0, 7)], [(0, 7), (10, 7), (12, 11), (9, 15), (0, 15)]],
    'C': [[(11, 2), (8, 0), (3, 0), (0, 3), (0, 12), (3, 15), (8, 15), (11, 13)]],
    'D': [[(0, 15), (0, 0), (8, 0), (12, 4), (12, 11), (8, 15), (0, 15)]],
    'E': [[(11, 0), (0, 0), (0, 15), (11, 15)], [(0, 7), (8, 7)]],
    'F': [[(11, 0), (0, 0), (0, 15)], [(0, 7), (8, 7)]],
    'G': [[(11, 2), (8, 0), (3, 0), (0, 3), (0, 12), (3, 15), (8, 15), (12, 11), (12, 7), (7, 7)]],
    'H': [[(0, 0), (0, 15)], [(12, 0), (12, 15)], [(0, 7), (12, 7)]],
    'I': [[(3, 0), (9, 0)], [(6, 0), (6, 15)], [(3, 15), (9, 15)]],
    'J': [[(12, 0), (12, 11), (9, 15), (3, 15), (0, 12)]],
    'K': [[(0, 0), (0, 15)], [(11, 0), (0, 8)], [(3, 6), (12, 15)]],
    'L': [[(0, 0), (0, 15), (11, 15)]],
    'M': [[(0, 15), (0, 0), (6, 9), (12, 0), (12, 15)]],
    'N': [[(0, 15), (0, 0), (12, 15), (12, 0)]],
    'O': [[(3, 0), (9, 0), (12, 3), (12, 12), (9, 15), (3, 15), (0, 12), (0, 3), (3, 0)]],
    'P': [[(0, 15), (0, 0), (9, 0), (12, 3), (12, 7), (9, 10), (0, 10)]],
    'Q': [[(3, 0), (9, 0), (12, 3), (12, 12), (9, 15), (3, 15), (0, 12), (0, 3), (3, 0)], [(8, 10), (12, 15)]],
    'R': [[(0, 15), (0, 0), (9, 0), (12, 3), (12, 7), (9, 10), (0, 10)], [(7, 10), (12, 15)]],
    'S': [[(11, 3), (8, 0), (3, 0), (0, 3), (0, 7), (12, 8), (12, 12), (9, 15), (3, 15), (0, 12)]],
    'T': [[(0, 0), (12, 0)], [(6, 0), (6, 15)]],
    'U': [[(0, 0), (0, 12), (3, 15), (9, 15), (12, 12), (12, 0)]],
    'V': [[(0, 0), (6, 15), (12, 0)]],
    'W': [[(0, 0), (3, 15), (6, 6), (9, 15), (12, 0)]],
    'X': [[(0, 0), (12, 15)], [(12, 0), (0, 15)]],
    'Y': [[(0, 0), (6, 7), (12, 0)], [(6, 7), (6, 15)]],
    'Z': [[(0, 0), (12, 0), (0, 15), (12, 15)]],
    '0': [[(3, 0), (9, 0), (12, 3), (12, 12), (9, 15), (3, 15), (0, 12), (0, 3), (3, 0)], [(9, 3), (3, 12)]],
    '1': [[(4, 3), (7, 0), (7, 15)], [(4, 15), (10, 15)]],
    '2': [[(1, 3), (3, 0), (9, 0), (12, 3), (12, 7), (0, 15), (12, 15)]],
    '3': [[(0, 0), (10, 0), (12, 2), (9, 6), (5, 7), (9, 8), (12, 10), (10, 15), (0, 15)]],
    '4': [[(9, 0), (9, 15)], [(0, 10), (12, 10)], [(9, 0), (0, 10)]],
    '5': [[(11, 0), (0, 0), (0, 7), (9, 7), (12, 10), (12, 13), (9, 15), (0, 15)]],
    '6': [[(11, 2), (8, 0), (3, 0), (0, 4), (0, 12), (3, 15), (9, 15), (12, 12), (12, 8), (9, 7), (0, 7)]],
    '7': [[(0, 0), (12, 0), (5, 15)]],
    '8': [[(3, 0), (9, 0), (12, 3), (12, 6), (9, 8), (3, 8), (0, 6), (0, 3), (3, 0)], [(3, 8), (0, 10), (0, 13), (3, 15), (9, 15), (12, 13), (12, 10), (9, 8)]],
    '9': [[(0, 13), (0, 4), (3, 0), (9, 0), (12, 3), (12, 12), (9, 15), (3, 15), (1, 13)], [(0, 7), (12, 7)]],
    ' ': [],
    '.': [[(5, 14), (7, 14), (7, 15), (5, 15)]],
    ',': [[(5, 12), (7, 12), (7, 14), (4, 15)]],
    ':': [[(5, 4), (7, 4), (7, 6), (5, 6)], [(5, 11), (7, 11), (7, 13), (5, 13)]],
    '-': [[(1, 8), (11, 8)]],
    '/': [[(11, 0), (1, 15)]],
    '(': [[(9, 0), (4, 5), (4, 10), (9, 15)]],
    ')': [[(3, 0), (8, 5), (8, 10), (3, 15)]],
    "'": [[(5, 0), (7, 0), (5, 5)]],
    '%': [[(1, 0), (4, 0), (4, 6), (1, 6), (1, 0)], [(11, 0), (1, 15)], [(8, 9), (11, 9), (11, 15), (8, 15), (8, 9)]],
    '&': [[(10, 1), (7, 0), (3, 1), (1, 5), (3, 8), (7, 8), (10, 11), (12, 15)], [(12, 0), (1, 15)]],
    '$': [[(10, 3), (7, 0), (3, 0), (1, 3), (1, 7), (11, 8), (11, 12), (8, 15), (4, 15), (1, 12)], [(6, 0), (6, 15)]],
    '!': [[(5, 0), (7, 0), (7, 9), (5, 9)], [(5, 13), (7, 13), (7, 15), (5, 15)]],
    '?': [[(2, 2), (5, 0), (9, 0), (11, 3), (11, 6), (7, 9), (6, 11)], [(5, 13), (7, 13), (7, 15), (5, 15)]],
}


def wrap_words(text, width):
    """Greedy word wrap; returns a list of lines, each at most `width` chars."""
    lines = []
    for raw in text.split("\n"):
        words = raw.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if len(trial) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur or not lines:
            lines.append(cur)
    return lines


class Canvas:
    """A device-space raster canvas; the final image is half its size.

    Everything is drawn at 2x resolution and averaged down when the PNG
    is written, which is what keeps the small bitmap type legible.
    """

    def __init__(self, logical_w, logical_h, scale, bg):
        self.scale = scale
        self.w = logical_w * scale
        self.h = logical_h * scale
        self.px = bytearray(self.w * self.h * 3)
        r, g, b = bg
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def _put(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = colour

    def dot(self, lx, ly, colour, thick=1):
        """One logical pixel: a full scale x scale block of device pixels."""
        s = self.scale
        for dy in range(s):
            for dx in range(s):
                self._put(lx * s + dx, ly * s + dy, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        """Bresenham segment between two logical points."""
        x0 *= self.scale
        y0 *= self.scale
        x1 *= self.scale
        y1 *= self.scale
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for oy in range(thick):
                for ox in range(thick):
                    self._put(x0 + ox, y0 + oy, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def box(self, lx, ly, w, h, colour):
        for yy in range(ly, ly + h):
            for xx in range(lx, lx + w):
                self.dot(xx, yy, colour)

    def frame(self, lx, ly, w, h, colour):
        for xx in range(lx, lx + w):
            self.dot(xx, ly, colour)
            self.dot(xx, ly + h - 1, colour)
        for yy in range(ly, ly + h):
            self.dot(lx, yy, colour)
            self.dot(lx + w - 1, yy, colour)

    def disc(self, cx, cy, radius, colour):
        rr = radius * radius
        for yy in range(cy - radius, cy + radius + 1):
            for xx in range(cx - radius, cx + radius + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= rr:
                    self.dot(xx, yy, colour)

    def ring(self, cx, cy, radius, colour, thick=1):
        for deg in range(360):
            a = math.radians(deg)
            self.dot(int(round(cx + radius * math.cos(a))),
                     int(round(cy + radius * math.sin(a))), colour, thick)

    def poly(self, points, colour):
        """Filled polygon via the even-odd rule, logical coordinates."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for yy in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    t = (yy - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for xx in range(int(math.ceil(xs[k])), int(xs[k + 1]) + 1):
                    self.dot(xx, yy, colour)

    def text5(self, lx, ly, text, colour):
        """Small bitmap type: 6 logical pixels per character cell."""
        text = text.upper()
        cx = lx
        for ch in text:
            glyph = _FACE.get(ch, _FACE[' '])
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == '1':
                        self.dot(cx + col_i, ly + row_i, colour)
            cx += 6
        return cx

    def text16(self, lx, ly, text, colour, thick=2):
        """Display stroke type: 14 logical pixels per character cell."""
        text = text.upper()
        cx = lx
        for ch in text:
            for stroke in _STROKES.get(ch, []):
                for i in range(len(stroke) - 1):
                    x0, y0 = stroke[i]
                    x1, y1 = stroke[i + 1]
                    self.line(cx + x0, ly + y0, cx + x1, ly + y1, colour, thick)
            cx += 14
        return cx

    def to_png(self, path):
        """Average each scale x scale block down and write a true-colour PNG."""
        s = self.scale
        out_w = self.w // s
        out_h = self.h // s
        raw = bytearray()
        for yy in range(out_h):
            raw.append(0)
            for xx in range(out_w):
                acc = [0, 0, 0]
                for dy in range(s):
                    base = ((yy * s + dy) * self.w + xx * s) * 3
                    for dx in range(s):
                        off = base + dx * 3
                        acc[0] += self.px[off]
                        acc[1] += self.px[off + 1]
                        acc[2] += self.px[off + 2]
                n = s * s
                raw += bytes((acc[0] // n, acc[1] // n, acc[2] // n))

        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            return out

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", out_w, out_h, 8, 2, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        png += chunk(b"IEND", b"")
        with open(path, "wb") as fh:
            fh.write(png)
        return len(png)


# ---------------------------------------------------------------- the news
# 14 lead cards. (n, section, headline, body, longitude, latitude, picture)
STORIES = [
    dict(n=1, sec="PERU", head="PERU M6.7 ROCKS ANDES, NO DEATHS",
         body="00:09 UTC, 9 km NE Carhuamayo, depth 108 km, MMI VI. Felt in Lima, anchor kept reporting live. 14 houses damaged, rockfalls, no fatalities. M5.0 aftershock 05:12 UTC.",
         lon=-76, lat=-11, pic="quake"),
    dict(n=2, sec="CLIMATE", head="COP31: STILL NO DEAL SAT MORNING",
         body="Overtime in Antalya, draft v3 due Sat morning after all-night talks. Draft drops fossil fuels and the $120bn adaptation target. Median finish: Sun night.",
         lon=30, lat=37, pic="cop"),
    dict(n=3, sec="SPORT", head="INDIA 486/4, LEAD 118 ON DAY 3",
         body="Rahul 136, Gill 98 in the final over, Pant 55 not out. India added 327/3 in Wellington, NZ 368. Six wickets left, two days to go.",
         lon=175, lat=-41, pic="cricket"),
    dict(n=4, sec="SPACE", head="BEPICOLOMBO REACHES MERCURY TONIGHT",
         body="ESA/JAXA orbiters fire thrusters 19:24 CET for 37 min, weak capture after 8 years. 2nd craft ever to orbit Mercury. Science from Apr 2027.",
         lon=8, lat=50, pic="mercury"),
    dict(n=5, sec="UKRAINE", head="KYIV BRIDGES HIT, 9 DEAD (20 NOV)",
         body="400+ drones, 110+ missiles incl. 27 ballistic. 3 Dnipro bridges damaged; Podilsko traffic restored Fri afternoon. 2 missiles fell in Poland.",
         lon=30, lat=50, pic="barrage"),
    dict(n=6, sec="GAZA", head="GAZA: 6 KILLED DESPITE CEASEFIRE",
         body="Published 21 Nov: 4 in airstrike SW of Bureij, 2 by drones at Al-Munasara and Nuseirat. Israel says it hit operatives. Toll since truce: 1,600+.",
         lon=34, lat=31, pic="tent"),
    dict(n=7, sec="ASIA", head="AKVAN GONE, RAIN LINGERS (20 NOV)",
         body="Dissipated 20 Nov after Gopalpur landfall, 70-80 km/h. 372,000 evacuated, no deaths, 1,450 babies born in evacuation. Schools shut to 21 Nov.",
         lon=85, lat=19, pic="cyclone"),
    dict(n=8, sec="MARKETS", head="WALL ST CRASH: NASDAQ -5.3% (20 NOV)",
         body="Nasdaq -10% in a week, worst since 2020; S&P -3.7%, Dow -937. VIX +33% to 37. Gold fell to a 14-month low, -9.4% in a week.",
         lon=-74, lat=41, pic="crash"),
    dict(n=9, sec="AMERICAS", head="BOLSONARO IN HOSPITAL (20 NOV)",
         body="Ex-president, 71, in Brasilia with near-complete intestinal obstruction. Stable, conscious, under observation 24h. Doctors aim to avoid surgery.",
         lon=-48, lat=-16, pic="hospital"),
    dict(n=10, sec="ASIA", head="KAMCHATKA M4.4, NO TSUNAMI",
         body="00:32 UTC, 41 km SE of Petropavlovsk-Kamchatsky, depth 89 km. Second quake of the day on the Ring of Fire after Peru.",
         lon=158, lat=53, pic="volcano"),
    dict(n=11, sec="ASIA", head="PAKISTAN: ATTACK FOILED (21 NOV)",
         body="Police in Lakki Marwat foiled a major attack, suicide bomber killed. Daesh claimed a market suicide bombing. No verified casualty toll yet.",
         lon=71, lat=33, pic="shield"),
    dict(n=12, sec="EUROPE", head="YOUTH ACTION, DAY 2 IN EUROPE",
         body="Fri walkouts in 25 nations over costs, housing, tuition. Further action planned Sat-Sun. Italy general strike, 100+ demos.",
         lon=2, lat=49, pic="crowd"),
    dict(n=13, sec="ASIA", head="N. KOREA ENRICHMENT GROWS (20 NOV)",
         body="Satellite images show Yongbyon uranium plant expanding. IAEA: extension externally complete by late Oct, serious concern. No access since 2009.",
         lon=126, lat=40, pic="atom"),
    dict(n=14, sec="SUMMIT", head="SHENZHEN PACT: NO UKRAINE DEAL (19 NOV)",
         body="Trump, Xi, Putin met 90 min, 4-point Declaration Toward Peace. No Ukraine or Iran deal, no nuclear treaty. US okays 880,000 AI chips to China.",
         lon=114, lat=22, pic="summit"),
]

ALSO = [
    "KRYVYI RIH TOLL (21 NOV): 2 DEAD, 42 HURT INCL. 4 CHILDREN IN OVERNIGHT RUSSIAN STRIKE.",
    "POLAND (20 NOV): 2 KH-101 MISSILES + JET DRONE FELL; TUSK SUSPECTS DELIBERATE PROVOCATION.",
    "UNICEF (20 NOV): 1,144 CHILDREN KILLED OR HURT IN UKRAINE JAN-OCT 2026, WORST IN 3 YEARS.",
    "UKRAINE LASER (20 NOV): FIRST AIR-DEFENCE LASER BLYSK DEPLOYED AROUND KYIV, UNPROVEN IN COMBAT.",
    "ESTONIA TO SHUT ALL RUSSIA ROAD CROSSINGS 1 DEC; EU ADOPTS 1BN EURO UKRAINE AID (20 NOV).",
    "FT (20 NOV): TRUMP WANTS KYIV PEACE DEAL BY EARLY JAN; SENATE REJECTS IRAN WAR POWERS 51-48.",
    "GAZA GROUND OP (19-20 NOV): TANKS CROSSED YELLOW LINE; 6,000 FLED; STORM FLOODED 70,000 TENTS.",
    "HORMUZ (20 NOV): TANKER STRIKE AND FIRE REPORTED 8 NM NORTH OF KHASAB, STRAIT OF HORMUZ.",
    "US SANCTIONS (20 NOV): 4 IRANIANS ADDED TO OFAC LIST OVER OIL REVENUES; COMANCHEROS HIT TOO.",
    "IRAN (19-20 NOV): NETANYAHU CALLS STRIKE UNAVOIDABLE; TRUMP SAYS NOT RUSHING ANY DECISION.",
    "NVIDIA -14% (20 NOV): $125.53 AFTER SEC PROBE REPORT; -23% IN A WEEK, -48% FROM OCT RECORD.",
    "TRUMP-XI (19-20 NOV): HUMANS MUST STAY IN AI WEAPONS LOOP; 880,000 AI CHIPS OKAYED TO CHINA.",
    "JAPAN QUAKE (20 NOV): M5.7 IN KUMAMOTO, 8 SHINKANSEN SERVICES SUSPENDED, 5,600 AFFECTED.",
    "PAKISTAN (20-21 NOV): CAR BOMB AT CHECKPOINT KILLS 5, HURTS 13; BLA CLAIMS 18 DEAD AT CAMP.",
    "TRUMP PARDONS PETE ROSE (20 NOV): POSTHUMOUS PARDON FOR BASEBALL'S HIT KING, 4,256 HITS.",
    "HYUNDAI ELANTRA (20 NOV): 2027 MODEL, 8TH GENERATION, UNVEILED AT LOS ANGELES AUTO SHOW.",
    "ECB (20 NOV): BOONE AND BRUNNERMEIER ENTER RACE FOR EXECUTIVE BOARD SUCCESSION.",
    "OCT 2026 WAS 1.8C ABOVE THE MID-1800S, BERKELEY EARTH SAYS; EL NINO BREAKS RECORDS.",
    "ICJ (19 NOV): MYANMAR FOUND GUILTY OF ROHINGYA GENOCIDE 9-6, FIRST STATE EVER CONVICTED.",
    "VAN GOGH PAINTING SOLD FOR A RECORD $190.4M (19 NOV); ACTOR STACY KEACH DIED AGED 85.",
    "GTA VI: $2.36BN DAY-ONE ESTIMATE (20 NOV UPDATE), 24.6M COPIES, NOT OFFICIAL TAKE-TWO FIGURES.",
    "PREMIER LEAGUE SAT (21 NOV): MAN CITY-FULHAM, CHELSEA-LEEDS, NEWCASTLE-ARSENAL AT 17:30 UK.",
    "CYBERATTACK (20 NOV): JPMORGAN, VISA, MASTERCARD HIT VIA VENDORS; CORE NETWORKS UNAFFECTED.",
    "UK (20 NOV): 1,000+ DRONES IN 260M POUND PACKAGE FOR UKRAINE; EU 45BN EURO LOAN PROPOSED.",
    "DENMARK RATIFIES GREENLAND SECURITY DEAL WITH US UNANIMOUSLY AFTER TAKEOVER TALK (20 NOV).",
    "WEST BANK (21 NOV): SETTLER SHOOTS DEAD PALESTINIAN NEAR RAMALLAH; UN COUNTS 400+ HARVEST ATTACKS.",
    "COP31: PANAMA VOWS TO FORMALLY OBJECT IF FINAL TEXT LACKS FINANCE AND OIL CAP (20 NOV).",
    "SOMALIA EXPELS UAE AMBASSADOR, ACCUSING ABU DHABI OF UNDERMINING ITS SOVEREIGNTY (20 NOV).",
    "GOLD -4.2% FRI, DOWN 11% IN A MONTH; IMF WARNS GLOBAL DEBT NEARS 100% OF GDP (20 NOV).",
    "ISRAEL: MOSQUE SET ON FIRE IN AL-DAHI; 8 HURT AS DRIVER RAMS PALESTINIANS IN KAFR QASIM.",
    "US SENATE PASSES ENERGY PERMITTING OVERHAUL 62-33; MUST STILL CLEAR THE HOUSE (20 NOV).",
    "WHITE HOUSE FIRES CYBER DIRECTOR CAIRNCROSS AFTER OUTAGES; KIRSTEN DAVIES TO FILL ROLE.",
    "JAPAN: CORE INFLATION HIGHEST THIS YEAR; BANK OF JAPAN SEEN ON TRACK TO RAISE RATES.",
    "BRAZIL: CENTRAL BANK SELLS $1BN TO CURB DOLLAR; REAL DOWN 18% IN A MONTH (20 NOV).",
]

SPORT = [
    "NFL (20 NOV): HOUSTON TEXANS BEAT INDIANAPOLIS COLTS 26-3 ON THURSDAY NIGHT.",
    "NBA (20 NOV): MEMPHIS BEAT CLEVELAND 124-121 IN OT, 8TH STRAIGHT ROAD WIN; HEAT BEAT HOUSTON 128-110.",
    "INDIA U17 (20 NOV): 0-0 WITH MALAYSIA, TOP GROUP E, QUALIFY FOR AFC U17 ASIAN CUP 2027.",
    "INDIA A (20 NOV): BEAT NEPAL A BY 306 RUNS, EMERGING STARS ASIA CUP; KUSHAGRA 117, YADAV FIFER.",
    "BADMINTON (20 NOV): LAKSHYA SEN AND SATWIK-CHIRAG INTO HONG KONG OPEN SEMI-FINALS.",
    "IRELAND WOMEN (21 NOV): BEAT UAE BY 61 RUNS, 171/5 VS 110/8, EMERGING NATIONS TROPHY.",
]

SOURCES = ("SOURCES: USGS, REUTERS, AP, AFP, BBC, CRICBUZZ, ESPN, IMD, "
           "ESA/JAXA, IAEA, UNICEF, UKMTO, US TREASURY.")
TOTAL = len(STORIES) + len(ALSO) + len(SPORT)

# ---------------------------------------------------------------- the map
# Coastline polygons, (longitude, latitude), hand-simplified.
LAND = [
    [(-168, 66), (-158, 71), (-140, 70), (-130, 71), (-125, 72), (-120, 69),
     (-110, 68), (-95, 69), (-85, 66), (-80, 62), (-75, 62), (-70, 62),
     (-65, 60), (-60, 55), (-65, 49), (-70, 44), (-75, 39), (-80, 32),
     (-81, 26), (-84, 30), (-90, 21), (-95, 19), (-97, 16), (-92, 15),
     (-86, 13), (-83, 9), (-79, 9), (-80, 7), (-83, 10), (-87, 14),
     (-90, 15), (-94, 16), (-97, 16), (-105, 20), (-110, 23), (-114, 28),
     (-120, 34), (-124, 40), (-124, 48), (-130, 55), (-140, 60), (-150, 61),
     (-158, 58), (-168, 66)],
    [(-79, 9), (-75, 11), (-72, 12), (-68, 11), (-64, 10), (-60, 8),
     (-58, 6), (-54, 5), (-52, 5), (-50, 0), (-44, -3), (-40, -5),
     (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-54, -34), (-58, -38),
     (-65, -41), (-68, -50), (-70, -54), (-66, -55), (-68, -50), (-70, -40),
     (-73, -37), (-73, -30), (-70, -20), (-77, -12), (-81, -6), (-81, 0),
     (-79, 7), (-79, 9)],
    [(-10, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (0, 49),
     (3, 51), (5, 53), (8, 57), (10, 59), (5, 60), (5, 62),
     (10, 64), (12, 66), (18, 69), (25, 71), (30, 71), (35, 68),
     (40, 68), (45, 68), (50, 69), (55, 68), (60, 69), (68, 73),
     (75, 73), (80, 73), (90, 75), (100, 77), (110, 76), (120, 73),
     (130, 72), (140, 72), (150, 71), (160, 70), (170, 67), (178, 65),
     (170, 60), (162, 60), (158, 53), (155, 59), (150, 60), (142, 59),
     (142, 50), (140, 45), (138, 38), (135, 35), (130, 33), (127, 35),
     (126, 40), (122, 39), (120, 32), (122, 28), (120, 23), (114, 22),
     (109, 20), (108, 12), (105, 9), (100, 8), (98, 10), (97, 16),
     (94, 17), (92, 21), (89, 22), (86, 20), (83, 18), (80, 13),
     (77, 8), (75, 15), (73, 20), (70, 21), (67, 25), (62, 25),
     (58, 25), (56, 27), (54, 26), (52, 25), (50, 27), (48, 29),
     (50, 29), (54, 28), (56, 27), (59, 22), (55, 17), (52, 15),
     (48, 14), (44, 13), (43, 12), (40, 15), (39, 21), (35, 28),
     (34, 31), (30, 36), (27, 37), (23, 36), (19, 42), (15, 44),
     (12, 44), (8, 39), (10, 37), (8, 39), (3, 42), (0, 39),
     (-2, 37), (-6, 36), (-10, 37)],
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-12, 8), (-8, 4), (-4, 5), (0, 6), (5, 4), (8, 4),
     (9, 4), (12, 5), (14, 4), (16, 4), (18, 3), (20, 0),
     (22, -2), (25, -5), (28, -10), (30, -15), (32, -20), (35, -25),
     (36, -28), (32, -29), (28, -33), (25, -34), (19, -35), (16, -30),
     (13, -25), (12, -18), (12, -12), (13, -6), (10, -2), (8, 0),
     (5, 4), (0, 6), (-5, 5), (-8, 4), (-12, 8), (-15, 11),
     (-17, 15), (-17, 21), (-15, 27), (-10, 31), (-6, 35)],
    [(95, -11), (100, -8), (105, -6), (110, -7), (115, -10), (120, -14),
     (125, -15), (130, -12), (135, -12), (140, -17), (145, -19), (150, -23),
     (153, -27), (153, -32), (150, -37), (145, -38), (140, -38), (135, -35),
     (130, -32), (125, -32), (120, -34), (115, -33), (110, -30), (105, -25),
     (100, -20), (97, -15), (95, -11)],
    [(166, -46), (168, -43), (172, -41), (174, -39), (176, -38), (178, -38),
     (176, -40), (174, -42), (171, -43), (168, -46), (166, -46)],
    [(-20, 64), (-22, 64), (-22, 66), (-18, 66), (-14, 64), (-15, 63),
     (-18, 63), (-20, 64)],
]

# Pin label nudges, keyed by story number: (dx, dy) from the pin point.
PIN_OFF = {1: (14, -14), 2: (16, -14), 3: (-18, 4), 4: (12, -14),
           5: (-20, -14), 6: (-18, 8), 7: (12, -14), 9: (-16, -12),
           10: (-18, -12), 11: (12, -14), 12: (-20, -14),
           13: (-16, 10), 14: (14, -14)}


# ------------------------------------------------------------ illustrations
def draw_pic(cv, x, y, w, h, kind):
    """One small original drawing per lead card, inside the (x, y, w, h) panel."""
    cx = x + w // 2
    cy = y + h // 2
    if kind == "quake":
        pts = [(x + 6, cy), (x + 22, cy - 14), (x + 30, cy + 12), (x + 40, cy - 18),
               (x + 50, cy + 10), (x + 62, cy - 8), (x + 76, cy + 14), (x + 92, cy - 6),
               (x + w - 6, cy)]
        for i in range(len(pts) - 1):
            cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], GOLD, 2)
        cv.disc(cx, cy, 4, RED)
        cv.line(x + 6, y + h - 10, x + w - 6, y + h - 10, FAINT, 1)
        cv.text5(x + 2, y + h - 9, "M6.7", FAINT)
    elif kind == "cop":
        cv.box(x + 10, y + 14, w - 20, h - 22, CARD)
        cv.box(x + 10, y + 14, w - 20, 3, GOLD)
        cv.box(x + 18, y + 24, w - 36, 12, RED)
        cv.text5(x + 22, y + 27, "FAILURE", PAPER)
        for fy in range(y + 42, y + h - 6, 5):
            cv.line(x + 18, fy, x + w - 18, fy, FAINT, 1)
    elif kind == "cricket":
        for sx in range(3):
            cv.line(x + 12 + sx * 5, y + h - 18, x + 12 + sx * 5, y + h - 6, PAPER, 2)
        cv.line(x + 40, y + h - 8, x + 78, y + 8, GOLD, 3)
        cv.disc(x + 88, y + 12, 4, RED)
        cv.line(x + 6, y + h - 4, x + w - 6, y + h - 4, FAINT, 1)
    elif kind == "mercury":
        cv.disc(cx - 6, cy - 4, 16, (169, 132, 103))
        cv.disc(cx - 12, cy - 10, 3, (120, 90, 70))
        cv.disc(cx + 2, cy + 2, 2, (120, 90, 70))
        cv.disc(cx - 2, cy - 12, 2, (120, 90, 70))
        cv.line(cx + 12, cy - 18, cx + 26, cy - 26, GOLD, 2)
        cv.disc(cx + 26, cy - 26, 3, GOLD)
        cv.text5(x + 2, y + h - 9, "8 YEARS", FAINT)
    elif kind == "barrage":
        for i in range(3):
            bx = x + 24 + i * 30
            cv.line(bx, y + h - 8, bx + 10, y + 8, GOLD, 2)
            cv.disc(bx + 10, y + 8, 3, RED)
            cv.line(bx - 4, y + h - 4, bx + 6, y + h - 14, FAINT, 1)
    elif kind == "tent":
        cv.poly([(cx - 26, y + h - 8), (cx, y + 8), (cx + 26, y + h - 8)], SKY)
        cv.poly([(cx - 8, y + h - 8), (cx, y + h - 26), (cx + 8, y + h - 8)], INK)
        cv.line(cx - 30, y + 6, cx - 18, y + 2, FAINT, 1)
        cv.line(cx + 18, y + 2, cx + 30, y + 6, FAINT, 1)
        cv.disc(x + 10, y + 8, 3, GOLD)
    elif kind == "cyclone":
        for rr in (18, 12, 6):
            cv.ring(cx, cy, rr, SKY, 1)
        cv.disc(cx, cy, 2, GOLD)
        cv.text5(x + 2, y + h - 9, "70-80 KM/H", FAINT)
    elif kind == "crash":
        bars = [34, 26, 18, 14, 10]
        for i, bh in enumerate(bars):
            bx = x + 8 + i * 20
            cv.box(bx, y + h - 8 - bh, 13, bh, RED)
        cv.line(x + 6, y + 6, x + w - 8, y + h - 12, GOLD, 2)
        cv.poly([(x + w - 8, y + h - 12), (x + w - 18, y + h - 14),
                 (x + w - 12, y + h - 4)], GOLD)
    elif kind == "hospital":
        cv.box(x + 8, cy - 2, w - 16, 4, LINE)
        cv.box(x + 8, cy - 2, 4, y + h - cy - 4, LINE)
        cv.box(x + w - 12, cy - 2, 4, y + h - cy - 4, LINE)
        cv.disc(x + 18, cy - 8, 5, PAPER)
        cv.box(x + 24, cy - 4, w - 44, 6, SKY)
        cv.line(x + w - 20, y + 6, x + w - 20, cy - 2, FAINT, 2)
        cv.disc(x + w - 20, y + 10, 3, RED)
        cv.box(cx - 8, y + 2, 16, 3, RED)
        cv.box(cx - 2, y - 4, 3, 16, RED)
    elif kind == "volcano":
        cv.poly([(cx - 28, y + h - 6), (cx, y + 6), (cx + 28, y + h - 6)], (90, 70, 60))
        cv.poly([(cx - 8, y + 6), (cx, y + 16), (cx + 8, y + 6)], RED)
        cv.disc(cx - 6, y + 2, 4, FAINT)
        cv.disc(cx + 6, y - 2, 3, FAINT)
        cv.line(x + 6, y + h - 6, x + w - 6, y + h - 6, FAINT, 1)
    elif kind == "shield":
        cv.poly([(cx, y + 4), (cx + 22, y + 10), (cx + 22, y + 26), (cx, y + h - 6),
                 (cx - 22, y + 26), (cx - 22, y + 10)], SKY)
        cv.line(cx - 10, cy + 2, cx - 2, cy + 10, GOLD, 3)
        cv.line(cx - 2, cy + 10, cx + 12, cy - 10, GOLD, 3)
    elif kind == "crowd":
        for i in range(4):
            hx = x + 16 + i * 28
            cv.disc(hx, y + 14, 6, GOLD if i % 2 == 0 else SKY)
            cv.box(hx - 9, y + 22, 18, h - 28, LINE)
    elif kind == "atom":
        cv.disc(cx, cy, 5, GOLD)
        cv.ring(cx, cy, 18, SKY, 2)
        cv.ring(cx, cy, 12, RED, 2)
        cv.disc(cx + 18, cy, 2, SKY)
        cv.disc(cx - 12, cy, 2, RED)
    elif kind == "summit":
        cols = [GOLD, SKY, RED]
        for i in range(3):
            fx = x + 22 + i * 34
            cv.line(fx, y + 8, fx, y + h - 8, PAPER, 2)
            cv.poly([(fx, y + 8), (fx + 22, y + 14), (fx, y + 20)], cols[i])


# ------------------------------------------------------------------- layout
def draw_card(cv, story, x, y):
    cw, ch = 138, 208
    cv.box(x, y, cw, ch, CARD)
    cv.frame(x, y, cw, ch, LINE)
    cv.text5(x + 8, y + 8, story["sec"], SKY)
    num = str(story["n"])
    cv.disc(x + cw - 16, y + 14, 9, GOLD)
    cv.text5(x + cw - 16 - 3 * len(num), y + 10, num, INK)
    px, py, pw, ph = x + 6, y + 24, cw - 12, 52
    cv.box(px, py, pw, ph, CARD2)
    draw_pic(cv, px, py, pw, ph, story["pic"])
    cv.line(x + 6, y + 80, x + cw - 6, y + 80, LINE, 1)
    hy = y + 86
    for i, ln in enumerate(wrap_words(story["head"], 21)[:3]):
        cv.text5(x + 8, hy + i * 9, ln, PAPER)
    by = hy + 3 * 9 + 4
    for i, ln in enumerate(wrap_words(story["body"], 21)[:9]):
        cv.text5(x + 8, by + i * 9, ln, FAINT)


def project(lon, lat):
    """Equirectangular projection into the map box (8..1016, 552..670)."""
    return (8 + (lon + 180) / 360.0 * 1008,
            552 + (90 - lat) / 180.0 * 118)


def draw_map(cv):
    cv.text5(8, 534, "WORLD MAP - WHERE IT HAPPENED (NUMBERS = MAIN CARDS 1-14)", GOLD)
    cv.box(8, 552, 1008, 118, SEA)
    for poly in LAND:
        pts = [(int(round(px)), int(round(py))) for (px, py) in
               (project(lon, lat) for lon, lat in poly)]
        cv.poly(pts, LANDC)
    eq_y = int(round(project(0, 0)[1]))
    cv.line(8, eq_y, 1016, eq_y, FAINT, 1)
    cv.text5(16, eq_y - 11, "EQUATOR", FAINT)
    for story in STORIES:
        px, py = project(story["lon"], story["lat"])
        px, py = int(round(px)), int(round(py))
        dx, dy = PIN_OFF.get(story["n"], (12, -14))
        lx, ly = px + dx, py + dy
        cv.disc(px, py, 3, GOLD)
        cv.line(px, py, lx + 3, ly + 3, GOLD, 1)
        cv.text5(lx, ly, str(story["n"]), GOLD)


def draw_also(cv):
    cv.text5(8, 678, "ALSO TODAY - 40 MORE STORIES", GOLD)
    items = ALSO + SPORT
    cols = [items[i::3] for i in range(3)]
    starts = [8, 344, 680]
    for ci, col in enumerate(cols):
        yy = 694
        for it in col:
            lines = wrap_words(it, 50)[:2]
            for li, ln in enumerate(lines):
                shown = "\u2022 " + ln if li == 0 else "  " + ln
                cv.text5(starts[ci], yy, shown, FAINT)
                yy += 8
            yy += 2


def build():
    cv = Canvas(1024, 1024, 2, INK)
    title = "THE WORLD TODAY"
    cv.text16((1024 - len(title) * 14) // 2, 10, title, PAPER)
    sub = "SATURDAY 21 NOVEMBER 2026  -  %d STORIES  -  6 CONTINENTS" % TOTAL
    cv.text5((1024 - len(sub) * 6) // 2, 42, sub, GOLD)
    cv.line(8, 62, 1016, 62, GOLD, 1)
    cv.text5(8, 76,
             "THE DAY IN ORDER  >  PERU M6.7 00:09 UTC  >  KAMCHATKA M4.4 00:32  >  GAZA TOLL 01:47  >  COP31 NO DEAL SAT AM  >  INDIA 486/4 DAY 3  >  BEPICOLOMBO 19:24 CET",
             GOLD)
    cv.line(8, 94, 1016, 94, LINE, 1)
    for idx, story in enumerate(STORIES):
        col, row = idx % 7, idx // 7
        draw_card(cv, story, 8 + col * (138 + 6), 102 + row * (208 + 6))
    draw_map(cv)
    draw_also(cv)
    cv.line(8, 946, 1016, 946, GOLD, 1)
    fy = 952
    for i, ln in enumerate(wrap_words(SOURCES, 165)):
        cv.text5(8, fy + i * 9, ln, FAINT)
    fy += len(wrap_words(SOURCES, 165)) * 9 + 2
    cv.frame(6, fy - 3, 1012, 36, GOLD)
    cv.text5(12, fy + 2, "DATE CHECK - 21 NOV 2026: PERU M6.7 + M5.0 AFTERSHOCK; KAMCHATKA M4.4; GAZA TOLL PUBLISHED;", PAPER)
    cv.text5(12, fy + 12, "KRYVYI RIH TOLL; COP31 STILL NO DEAL; INDIA 486/4 DAY 3; BEPICOLOMBO 19:24 CET; LAKKI MARWAT FOIL.", PAPER)
    cv.text5(12, fy + 22, "20 NOV ITEMS ARE DATED ON THEIR CARDS; 19 NOV ITEMS TOO.", PAPER)
    cv.text5(8, fy + 38, "ORIGINAL DRAWINGS  -  STDLIB PYTHON, DETERMINISTIC, NO NETWORK  -  2X SUPER-SAMPLED", FAINT)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not os.path.isdir(out_dir):
        out_dir = "./out"
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    size = cv.to_png(path)
    print("wrote %s (%d bytes, %d stories)" % (path, size, TOTAL))


if __name__ == "__main__":
    main()
