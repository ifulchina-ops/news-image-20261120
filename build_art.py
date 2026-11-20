#!/usr/bin/env python3
"""Draw the news-image-20261120 entry: one broadsheet front page that sums
up Friday 20 November 2026 in a single image.

All ten stories below were the day's most widely reported headlines as of
the morning of 20 November 2026 (Reuters, BBC, The Times of India, The
Hindu, Space, Marketscreener): the Shenzhen trilateral peace declaration,
Trump pushing the Iran war decision to 2027, the ICJ genocide ruling on
Myanmar, Voyager 1's one-light-day milestone, Cyclone Akvan, GTA VI sales,
Anthropic's market debut, Hayabusa2, the Crimean Bridge strikes, and the
migrant boat sinking off Senegal.

Deterministic, no network, PIL + DejaVu only. Writes entry.png (1024x1024)
next to this script. Every section asserts it stays inside its vertical
band, so a too-long story fails loudly instead of overlapping the next one.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MX = 34                      # side margin
BLACK = (15, 15, 15)
PAPER = (252, 250, 244)      # warm newsprint
RED = (165, 12, 12)
BLUE = (18, 52, 96)
GREY = (96, 96, 96)

FONTS = Path("/usr/share/fonts/truetype/dejavu")


def f_serif(size):
    return ImageFont.truetype(str(FONTS / "DejaVuSerif-Bold.ttf"), size)


def f_sans(size):
    return ImageFont.truetype(str(FONTS / "DejaVuSans.ttf"), size)


def f_sansb(size):
    return ImageFont.truetype(str(FONTS / "DejaVuSans-Bold.ttf"), size)


def wrap_text(d, text, font, width):
    """Greedy wrap; returns list of lines that fit `width` pixels."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, font, width, leading):
    for line in wrap_text(d, text, font, width):
        d.text((x, y), line, font=font, fill=BLACK)
        y += leading
    return y


def hline(d, y, weight=2, x0=None, x1=None):
    d.line([(MX if x0 is None else x0, y),
            (W - MX if x1 is None else x1, y)], fill=BLACK, width=weight)


def kicker(d, x, y, text):
    d.text((x, y), text, font=f_sansb(16), fill=RED)
    return y + 24


def headline(d, x, y, text, size, width, leading):
    return para(d, x, y, text, f_serif(size), width, leading)


def flag_stars(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def mini_flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=BLACK, width=1)
    sh = h / 13
    for i in range(13):
        if i % 2 == 0:
            d.rectangle([x, y + i * sh, x + w, y + (i + 1) * sh],
                        fill=(178, 34, 52))
    cw, ch = w * 0.4, h * 7 / 13
    d.rectangle([x, y, x + cw, y + ch], fill=BLUE)
    for r in range(3):
        for c in range(4):
            px = x + 7 + c * (cw - 14) / 3
            py = y + 6 + r * (ch - 12) / 2
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=PAPER)


def mini_flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16), outline=BLACK, width=1)
    flag_stars(d, x + w * 0.22, y + h * 0.30, h * 0.20, (255, 222, 0))
    for sx, sy in [(0.55, 0.16), (0.68, 0.30), (0.68, 0.50), (0.55, 0.64)]:
        flag_stars(d, x + w * sx, y + h * sy, h * 0.08, (255, 222, 0))


def mini_flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=BLACK, width=1)
    third = h / 3
    d.rectangle([x, y, x + w, y + third], fill=PAPER)
    d.rectangle([x, y + third, x + w, y + 2 * third], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * third, x + w, y + h], fill=(213, 0, 50))


def two_col_block(d, y, left_kick, left_head, left_body,
                  right_kick, right_head, right_body, band_end):
    """Two side-by-side stories; returns the y just past the block."""
    col_w = (W - 2 * MX) // 2 - 14
    rx = MX + col_w + 28
    y1 = kicker(d, MX, y, left_kick)
    y1 = headline(d, MX, y1, left_head, 27, col_w, 30)
    y1 = para(d, MX, y1 + 4, left_body, f_sans(16), col_w, 21)
    y2 = kicker(d, rx, y, right_kick)
    y2 = headline(d, rx, y2, right_head, 27, col_w, 30)
    y2 = para(d, rx, y2 + 4, right_body, f_sans(16), col_w, 21)
    end = max(y1, y2)
    assert end <= band_end, f"two-col block overflows band: {end} > {band_end}"
    return end


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- masthead (ends 225) ----------
    name = "TWENTY"
    tf = f_serif(104)
    tw = d.textlength(name, font=tf)
    d.text(((W - tw) / 2, 14), name, font=tf, fill=BLACK)
    hline(d, 140, 4)
    hline(d, 146, 1)
    dateline = "FRIDAY  •  20  NOVEMBER  2026"
    df = f_sansb(26)
    dw = d.textlength(dateline, font=df)
    d.text(((W - dw) / 2, 156), dateline, font=df, fill=RED)
    tagline = "THE WORLD IN ONE PAGE  —  TEN STORIES THAT DEFINED THE DAY"
    gf = f_sans(18)
    gw = d.textlength(tagline, font=gf)
    d.text(((W - gw) / 2, 190), tagline, font=gf, fill=GREY)
    hline(d, 220, 3)
    hline(d, 225, 1)

    # ---------- lead story: Shenzhen peace declaration (240-458) ----------
    y = 240
    y = kicker(d, MX, y, "LEAD STORY  •  SHENZHEN, CHINA")
    y = headline(d, MX, y, "Trump, Xi and Putin issue a \u2018peace declaration\u2019",
                 38, W - 2 * MX, 40)
    y = para(d, MX, y + 4,
             "The three leaders held their first-ever trilateral meeting on the "
             "APEC sidelines at Kylin Villa, then released a joint declaration "
             "on peace and global security. Agenda: Ukraine, Iran, trade, AI and "
             "nuclear arms; Europe said it is ready for talks with Russia on "
             "ending the war.",
             f_sans(18), W - 2 * MX, 22)
    assert y <= 418, f"lead body overflows: {y}"
    # flag strip: three flags in a row, centred
    fy = y + 10
    fw, fh = 150, 34
    labels = [(mini_flag_us, "UNITED STATES"),
              (mini_flag_cn, "CHINA"),
              (mini_flag_ru, "RUSSIA")]
    widths = []
    for _, label in labels:
        widths.append(fw + 10 + d.textlength(label, font=f_sansb(15)))
    total = sum(widths) + 40 * (len(labels) - 1)
    fx = (W - total) / 2
    for (draw_flag, label), wdt in zip(labels, widths):
        draw_flag(d, fx, fy, fw, fh)
        d.text((fx + fw + 10, fy + 9), label, font=f_sansb(15), fill=BLACK)
        fx += wdt + 40
    hline(d, 470, 2)

    # ---------- middle: Iran + ICJ (486-650) ----------
    y = two_col_block(
        d, 486,
        "WASHINGTON", "Iran war decision pushed to 2027",
        "President Trump said there is no rush on Iran and he will \u2018see "
        "what happens\u2019 after 1 January, pushing any decision on war into "
        "next year.",
        "THE HAGUE", "ICJ: Myanmar committed genocide",
        "The UN\u2019s top court ruled that Myanmar committed genocide against "
        "the Rohingya minority in the 2017 crackdown. The ruling cannot be "
        "appealed.",
        650)
    hline(d, 658, 1)

    # ---------- lower: Voyager + Akvan (674-812) ----------
    y = two_col_block(
        d, 674,
        "DEEP SPACE", "Voyager 1 reaches one light-day",
        "NASA confirmed the probe is one light-day from Earth \u2014 the "
        "farthest any human-made object has flown.",
        "ODISHA, INDIA", "Cyclone Akvan nears the coast",
        "Three lakh people evacuated and 423 rescue teams deployed as "
        "Cyclone Akvan bears down on Odisha.",
        812)

    # ---------- day in numbers (824-882) ----------
    ny = 824
    d.rectangle([MX, ny, W - MX, ny + 58], fill=BLACK)
    nums = [("2027", "Iran decision deferred"),
            ("1 LIGHT-DAY", "Voyager 1 from Earth"),
            ("300,000", "evacuated from Akvan"),
            ("$1.5 TRILLION", "Anthropic valuation"),
            ("$1.80 BILLION", "GTA VI passes Odyssey")]
    seg = (W - 2 * MX) / len(nums)
    for i, (big, small) in enumerate(nums):
        cx = MX + seg * i + seg / 2
        bf = f_sansb(21)
        bw = d.textlength(big, font=bf)
        d.text((cx - bw / 2, ny + 6), big, font=bf, fill=PAPER)
        sf = f_sans(12)
        sw = d.textlength(small, font=sf)
        d.text((cx - sw / 2, ny + 34), small, font=sf, fill=(210, 208, 198))
        if i:
            d.line([(MX + seg * i, ny + 10), (MX + seg * i, ny + 48)],
                   fill=(90, 90, 90), width=1)

    # ---------- the day in brief (894-986) ----------
    by = 894
    d.text((MX, by), "THE DAY IN BRIEF", font=f_sansb(19), fill=BLACK)
    hline(d, by + 26, 1)
    briefs = [
        "GTA VI sales already pass The Odyssey\u2019s $1.80 billion global run.",
        "Anthropic debuts among the world\u2019s most valuable public companies.",
        "Engine trouble ends Japan\u2019s Hayabusa2 asteroid landing plan.",
        "Ukraine hits the Crimean Bridge; Putin vows a painful reply.",
        "Migrant boat sinks off Senegal; dozens missing.",
        "South Korea\u2019s top court overturns ex-PM Han Duck-soo\u2019s conviction.",
        "US and Venezuela sign a deal to restore military cooperation.",
        "Fiji declares a national disaster as drought drains water supplies.",
    ]
    half = (W - 2 * MX) // 2
    bf = f_sans(12)
    for item in briefs:
        assert d.textlength(item, font=bf) <= half - 22, \
            f"brief too long for one line: {item}"
    iy = by + 36
    for i, item in enumerate(briefs):
        col = i % 2
        row = i // 2
        x = MX + col * half
        yy = iy + row * 15
        d.text((x, yy), "\u2022", font=f_sansb(13), fill=RED)
        d.text((x + 14, yy), item, font=bf, fill=BLACK)
    assert iy + 3 * 15 + 15 <= 1000, "briefs overflow footer"

    # ---------- footer ----------
    d.text((MX, 1002), "All stories as reported on 20 November 2026. Drawn with PIL; no photos, no invented quotes.",
           font=f_sans(11), fill=GREY)

    out = Path(__file__).resolve().parent / "entry.png"
    img.save(out, format="PNG", optimize=True)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
