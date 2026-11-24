#!/usr/bin/env python3
"""news-image-20261124 -- "Two Skies, One Alarm -- Tuesday 24 November 2026".

Draws one 1024x1024 PNG summing up the world news of Tuesday 24 November
2026: two hero stories (a Russian jet triggering South Korea's air-raid
alert over Ulleungdo, and a Russian drone breaching Polish airspace) around
a storm globe, plus six more stories in a grid. Pure Python 3.13 stdlib:
own bitmap font, own rasteriser, own PNG encoder. No network, no files read,
deterministic output.
"""
import binascii
import os
import struct
import sys
import zlib

# ---------------------------------------------------------------------------
# 5x7 bitmap font, written by hand for this entry.
# Each glyph is 7 rows of 5 pixels, '#' = on, '.' = off.
# ---------------------------------------------------------------------------
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}

CHAR_W = 5          # glyph columns
CHAR_H = 7          # glyph rows
CHAR_ADV = 6        # advance per character, in font units


def text_width(text, scale):
    """Pixel width of text at the given integer scale."""
    return len(text) * CHAR_ADV * scale - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    max_chars = max(1, max_width // (CHAR_ADV * scale))
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            trial = w if not cur else cur + " " + w
            if len(trial) <= max_chars or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


class Canvas:
    """An RGB raster canvas with simple vector drawing primitives."""

    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.buf = bytearray(bytes(bg) * (width * height))

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + (x1 - x0) * 3] = row

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line with square brush of `thick` pixels."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.rect(x0 - half, y0 - half, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        """Filled circle."""
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - half, cy + dy, half * 2 + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        """Circle outline, approximated by concentric discs difference."""
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            inner = int(((r - thick) ** 2 - dy * dy) ** 0.5) if abs(dy) < r - thick else -1
            if inner >= 0:
                self.rect(cx - half, cy + dy, half - inner, 1, color)
                self.rect(cx + inner + 1, cy + dy, half - inner, 1, color)
            else:
                self.rect(cx - half, cy + dy, half * 2 + 1, 1, color)

    def poly(self, points, color):
        """Filled polygon via scanline fill."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        y_lo = max(0, int(min(ys)))
        y_hi = min(self.h - 1, int(max(ys)))
        for y in range(y_lo, y_hi + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                xa = max(0, int(round(xs[j])))
                xb = min(self.w - 1, int(round(xs[j + 1])))
                if xb >= xa:
                    self.rect(xa, y, xb - xa + 1, 1, color)

    def draw_char(self, x, y, ch, scale, color):
        glyph = FONT.get(ch)
        if glyph is None:
            return
        for row in range(CHAR_H):
            bits = glyph[row]
            for col in range(CHAR_W):
                if bits[col] == '1':
                    self.rect(x + col * scale, y + row * scale,
                              scale, scale, color)

    def text(self, x, y, s, scale, color, align="left"):
        """Draw text; align left/center/right around x."""
        if align == "center":
            x -= text_width(s, scale) // 2
        elif align == "right":
            x -= text_width(s, scale)
        cx = x
        for ch in s:
            self.draw_char(cx, y, ch, scale, color)
            cx += CHAR_ADV * scale
        return x

    def text_block(self, x, y, lines, scale, color, leading=None,
                   align="left"):
        """Draw wrapped lines; returns y just below the block."""
        if leading is None:
            leading = CHAR_H * scale + scale
        for ln in lines:
            self.text(x, y, ln, scale, color, align=align)
            y += leading
        return y


# ---------------------------------------------------------------------------
# PNG encoder (stdlib only): RGB, filter 0, zlib level 9, deterministic.
# ---------------------------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    w, h = canvas.w, canvas.h
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)  # filter: none
        raw += canvas.buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
NAVY = (11, 30, 58)        # page background
PANEL = (18, 46, 82)       # card background
PANEL_LINE = (48, 88, 138)  # card border
GOLD = (242, 183, 5)       # masthead gold
GOLD_DIM = (201, 152, 20)
WHITE = (245, 242, 233)    # headline white
MUTED = (185, 198, 216)    # summary text
GLOBE = (27, 58, 102)      # globe sea
GLOBE_LINE = (61, 106, 168)
CLOUD = (215, 230, 245)
BOLT = (255, 210, 63)
RED = (229, 72, 77)
BLUE = (96, 165, 250)
GREEN = (74, 184, 106)
ORANGE = (240, 138, 36)
TEAL = (45, 178, 171)
SKY = (125, 190, 235)
BROWN = (198, 148, 92)
PURPLE = (178, 132, 214)


# ---------------------------------------------------------------------------
# Pictogram icons, drawn with primitives inside a square box (x, y, size).
# ---------------------------------------------------------------------------
def icon_jet(c, x, y, s, color):
    """Delta jet pointing up-right."""
    u = s / 48.0
    c.poly([(x + 44 * u, y + 4 * u), (x + 10 * u, y + 30 * u),
            (x + 18 * u, y + 32 * u), (x + 6 * u, y + 44 * u),
            (x + 22 * u, y + 38 * u), (x + 30 * u, y + 40 * u),
            (x + 40 * u, y + 26 * u)], color)
    c.line(int(x + 8 * u), int(y + 40 * u), int(x + 2 * u), int(y + 46 * u),
           color, 2)


def icon_drone(c, x, y, s, color):
    """Quadcopter drone, top view."""
    u = s / 48.0
    cx, cy = x + 24 * u, y + 24 * u
    c.line(int(x + 10 * u), int(y + 10 * u), int(x + 38 * u), int(y + 38 * u),
           color, 3)
    c.line(int(x + 38 * u), int(y + 10 * u), int(x + 10 * u), int(y + 38 * u),
           color, 3)
    c.rect(int(cx - 6 * u), int(cy - 6 * u), int(12 * u), int(12 * u), color)
    for px_, py_ in ((10, 10), (38, 10), (10, 38), (38, 38)):
        c.ring(int(x + px_ * u), int(y + py_ * u), int(7 * u), color, 2)


def icon_chart(c, x, y, s, color):
    """Rising bars with an arrow."""
    u = s / 48.0
    c.rect(int(x + 6 * u), int(y + 30 * u), int(8 * u), int(12 * u), color)
    c.rect(int(x + 18 * u), int(y + 22 * u), int(8 * u), int(20 * u), color)
    c.rect(int(x + 30 * u), int(y + 12 * u), int(8 * u), int(30 * u), color)
    c.line(int(x + 4 * u), int(y + 12 * u), int(x + 42 * u), int(y + 4 * u),
           color, 3)
    c.poly([(x + 42 * u, y + 4 * u), (x + 34 * u, y + 4 * u),
            (x + 42 * u, y + 12 * u)], color)


def icon_doc(c, x, y, s, color):
    """Document with lines (sanctions / report)."""
    u = s / 48.0
    c.rect(int(x + 12 * u), int(y + 5 * u), int(24 * u), int(38 * u), color)
    c.rect(int(x + 16 * u), int(y + 9 * u), int(16 * u), int(30 * u), NAVY)
    for i, yy in enumerate((14, 20, 26, 32)):
        c.hline(int(x + 19 * u), int(y + yy * u), int(10 * u), color, 2)


def icon_badge(c, x, y, s, color):
    """Five-point star badge (law-enforcement capture)."""
    import math
    u = s / 48.0
    cx, cy, r = x + 24 * u, y + 24 * u, 19 * u
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    c.poly(pts, color)


def icon_warn(c, x, y, s, color):
    """Warning triangle with exclamation."""
    u = s / 48.0
    c.poly([(x + 24 * u, y + 4 * u), (x + 44 * u, y + 42 * u),
            (x + 4 * u, y + 42 * u)], color)
    c.rect(int(x + 22 * u), int(y + 16 * u), int(4 * u), int(14 * u), NAVY)
    c.rect(int(x + 22 * u), int(y + 34 * u), int(4 * u), int(4 * u), NAVY)


def icon_plane(c, x, y, s, color):
    """Airliner silhouette, side view."""
    u = s / 48.0
    c.poly([(x + 4 * u, y + 24 * u), (x + 14 * u, y + 18 * u),
            (x + 40 * u, y + 18 * u), (x + 46 * u, y + 24 * u),
            (x + 40 * u, y + 28 * u), (x + 14 * u, y + 28 * u)], color)
    c.poly([(x + 20 * u, y + 18 * u), (x + 26 * u, y + 8 * u),
            (x + 30 * u, y + 18 * u)], color)
    c.poly([(x + 22 * u, y + 28 * u), (x + 28 * u, y + 38 * u),
            (x + 32 * u, y + 28 * u)], color)
    c.poly([(x + 34 * u, y + 28 * u), (x + 40 * u, y + 38 * u),
            (x + 42 * u, y + 28 * u)], color)


def icon_smoke(c, x, y, s, color):
    """Factory stacks with smoke puffs (pollution)."""
    u = s / 48.0
    c.rect(int(x + 8 * u), int(y + 26 * u), int(10 * u), int(16 * u), color)
    c.rect(int(x + 20 * u), int(y + 20 * u), int(10 * u), int(22 * u), color)
    c.rect(int(x + 32 * u), int(y + 30 * u), int(8 * u), int(12 * u), color)
    c.disc(int(x + 13 * u), int(y + 16 * u), int(5 * u), color)
    c.disc(int(x + 25 * u), int(y + 10 * u), int(6 * u), color)
    c.disc(int(x + 33 * u), int(y + 16 * u), int(4 * u), color)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
W, H = 1024, 1024
MARGIN = 36


def draw_masthead(c):
    """Date is the biggest element on the page."""
    c.hline(MARGIN, 26, W - 2 * MARGIN, GOLD, 4)
    c.text(W // 2, 42, "TUESDAY", 10, GOLD, align="center")
    c.text(W // 2, 120, "24 NOVEMBER 2026", 8, WHITE, align="center")
    c.hline(MARGIN, 190, W - 2 * MARGIN, GOLD, 4)


def draw_bolt(c, x0, y0, x1, y1, color):
    """A jagged lightning bolt from (x0, y0) to (x1, y1)."""
    mx = (x0 + x1) // 2
    my = (y0 + y1) // 2
    w = 9
    pts = [
        (x0 - w, y0), (mx + 14, my - 26), (mx + 2, my - 4),
        (x1 + w, y1), (x1 - w, y1 + 6), (mx - 2, my + 8),
        (mx - 16, my + 30), (x0 + w, y0 + 4),
    ]
    c.poly(pts, color)


def draw_globe(c, cx, cy, r):
    """Storm globe: sea, meridians, cloud swirls, two lightning bolts."""
    c.disc(cx, cy, r, GLOBE)
    c.ring(cx, cy, r, GOLD, 4)
    # meridians and parallels
    import math
    for k in range(1, 4):
        off = r * k / 4
        c.line(int(cx - off), int(cy - r + 6), int(cx - off), int(cy + r - 6),
               GLOBE_LINE, 2)
        c.line(int(cx + off), int(cy - r + 6), int(cx + off), int(cy + r - 6),
               GLOBE_LINE, 2)
    for k in (-1, 0, 1):
        yy = cy + k * r // 2
        half = int((r * r - (yy - cy) ** 2) ** 0.5) - 4
        c.hline(cx - half, yy, half * 2, GLOBE_LINE, 2)
    # cloud swirls
    c.disc(cx - r // 2, cy - r // 3, 26, CLOUD)
    c.disc(cx - r // 2 + 26, cy - r // 3 + 8, 20, CLOUD)
    c.disc(cx + r // 3, cy + r // 4, 30, CLOUD)
    c.disc(cx + r // 3 + 28, cy + r // 4 - 10, 18, CLOUD)
    c.disc(cx - 10, cy + r // 2, 18, CLOUD)
    # two lightning bolts striking down out of the globe, kept in the
    # free central column so they never touch the hero text
    draw_bolt(c, cx - 58, cy + 62, cx - 96, cy + 148, BOLT)
    draw_bolt(c, cx + 58, cy + 62, cx + 96, cy + 148, BOLT)


def draw_hero(c, x, y, w, chip, chip_color, icon, headline, summary):
    """One hero story block: country chip, headline, one-line summary."""
    c.text(x, y, chip, 4, chip_color)
    c.rect(x, y + 34, w, 3, chip_color)
    lines = wrap_text(headline, 4, w)
    yy = c.text_block(x, y + 48, lines, 4, WHITE, leading=34)
    slines = wrap_text(summary, 3, w)
    c.text_block(x, yy + 8, slines, 3, MUTED, leading=24)


def draw_cell(c, x, y, w, h, chip_color, icon, headline, summary):
    """One grid story cell: colour chip, icon, headline, summary."""
    c.rect(x, y, w, h, PANEL)
    c.rect(x, y, w, 2, chip_color)
    c.rect(x, y, 2, h, chip_color)
    c.rect(x + w - 2, y, 2, h, chip_color)
    c.rect(x, y + h - 2, w, 2, chip_color)
    icon(c, x + 14, y + 16, 40, chip_color)
    tx = x + 66
    tw = w - 66 - 14
    lines = wrap_text(headline, 4, tw)
    yy = c.text_block(tx, y + 14, lines, 4, WHITE, leading=34)
    slines = wrap_text(summary, 3, tw)
    c.text_block(tx, yy + 4, slines, 3, MUTED, leading=24)


def build():
    c = Canvas(W, H, NAVY)
    # thin gold frame
    c.rect(0, 0, W, 4, GOLD)
    c.rect(0, H - 4, W, 4, GOLD)
    c.rect(0, 0, 4, H, GOLD)
    c.rect(W - 4, 0, 4, H, GOLD)

    draw_masthead(c)

    # --- hero zone: storm globe between the two named stories ---
    draw_globe(c, W // 2, 356, 112)
    draw_hero(c, MARGIN, 206, 320, "KOREA", RED, icon_jet,
              "RUSSIAN JET TRIGGERS AIR-RAID ALERT",
              "07:52 ALERT OVER ULLEUNGDO; JETS SCRAMBLED; LIFTED 07:55")
    draw_hero(c, W - MARGIN - 320, 206, 320, "POLAND", BLUE, icon_drone,
              "RUSSIAN DRONE BREACHES POLISH AIRSPACE",
              "DRONE INCURSION DURING STRIKES ON UKRAINE; NATO SENDS AWACS")

    c.hline(MARGIN, 528, W - 2 * MARGIN, PANEL_LINE, 2)
    c.text(W // 2, 542, "THE REST OF THE DAY", 3, GOLD, align="center")

    # --- grid: 2 columns x 3 rows, six more stories ---
    # Copy is kept tight on purpose: every headline wraps to at most
    # 2 lines at scale 4 and every summary to at most 2 lines at scale 3,
    # so nothing overflows its 134px cell.
    stories = [
        (GREEN, icon_chart, "NVIDIA SOARS 31.5% IN A DAY",
         "+$952BN AS JENSEN HUANG RETURNS AS CEO"),
        (PURPLE, icon_doc, "IRAN: 74 LASHES FOR SINGER",
         "US SANCTIONS IRAN SHADOW BANKING"),
        (ORANGE, icon_badge, "MEXICO CAPTURES 'CHAPO ISIDRO'",
         "ELITE FORCES SEIZE CARTEL BOSS"),
        (TEAL, icon_warn, "GAZA AIR, SOIL, WATER POISONED",
         "OXFAM: METALS, ASBESTOS, DIOXINS"),
        (SKY, icon_plane, "O'HARE GROUND STOP",
         "STAFF SHORTAGE HALTS FLIGHTS 10:40-12:15"),
        (BROWN, icon_smoke, "LAHORE: MOST POLLUTED CITY",
         "AQI OVER 500; QUAKE 4.0 NEAR BORDER"),
    ]
    gx, gy = MARGIN, 576
    cw, chh = 468, 134
    gap = 16
    for i, (color, icon, head, summ) in enumerate(stories):
        col = i % 2
        row = i // 2
        draw_cell(c, gx + col * (cw + gap), gy + row * (chh + 10),
                  cw, chh, color, icon, head, summ)

    c.hline(MARGIN, 1008, W - 2 * MARGIN, GOLD, 2)
    return c


def main():
    # Keep script dir on sys.path (grader runs from /tmp with -P -s).
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
