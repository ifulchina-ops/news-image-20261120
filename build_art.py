#!/usr/bin/env python3
"""Draw the news-image-20261120 entry, round 3: one broadsheet front page
that sums up Saturday 21 November 2026 in a single image.

Nine stories, all as reported on 21 November 2026 (The Daily Short,
SimpleLife.news, One Turn, Global Advisors, The Paris Eye, Observer Voice):
the 6.8 Junin earthquake, the Wall Street correction, Russian missiles in
Poland, Anthropic's record IPO, Cyclone Akvan's landfall, the UK-EU deals,
the Mailchimp sale, KL Rahul's SENA century, and the Gaza aid call, plus
briefs from India and the FBI probe.

The lead story carries a photo: lead.jpg, an AI-generated illustration of
the reported quake scene in Junin, produced for this entry (no real
photograph is claimed). Everything else is drawn deterministically with
PIL + DejaVu. Writes entry.png (1024x1024) next to this script. Every
section asserts it stays inside its vertical band, so a too-long story
fails loudly instead of overlapping the next one.
"""
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


def mini_chart(d, x, y, w, h):
    """Small plunging-line chart for the markets story (drawn, no data)."""
    d.rectangle([x, y, x + w, y + h], outline=GREY, width=1)
    for i in range(1, 4):
        gy = y + h * i / 4
        d.line([(x, gy), (x + w, gy)], fill=(220, 218, 208), width=1)
    pts = [(0.00, 0.12), (0.12, 0.22), (0.24, 0.18), (0.36, 0.38),
           (0.48, 0.34), (0.60, 0.55), (0.72, 0.62), (0.84, 0.78),
           (1.00, 0.92)]
    xy = [(x + w * px, y + h * py) for px, py in pts]
    d.line(xy, fill=RED, width=3, joint="curve")
    lab = "-5.3%"
    lw = d.textlength(lab, font=f_sansb(13))
    d.text((x + w - lw - 4, y + 3), lab, font=f_sansb(13), fill=RED)


def two_col_block(d, y, left_kick, left_head, left_body,
                  right_kick, right_head, right_body, band_end,
                  head_size=27, head_leading=30,
                  body_size=16, body_leading=21, left_chart=False):
    """Two side-by-side stories; returns the y just past the block."""
    col_w = (W - 2 * MX) // 2 - 14
    rx = MX + col_w + 28
    y1 = kicker(d, MX, y, left_kick)
    y1 = headline(d, MX, y1, left_head, head_size, col_w, head_leading)
    y1 = para(d, MX, y1 + 4, left_body, f_sans(body_size), col_w, body_leading)
    if left_chart:
        mini_chart(d, MX, y1 + 6, col_w, 44)
        y1 += 56
    y2 = kicker(d, rx, y, right_kick)
    y2 = headline(d, rx, y2, right_head, head_size, col_w, head_leading)
    y2 = para(d, rx, y2 + 4, right_body, f_sans(body_size), col_w, body_leading)
    end = max(y1, y2)
    assert end <= band_end, f"two-col block overflows band: {end} > {band_end}"
    return end


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- masthead (ends 185) ----------
    name = "TWENTY-ONE"
    tf = f_serif(76)
    tw = d.textlength(name, font=tf)
    d.text(((W - tw) / 2, 10), name, font=tf, fill=BLACK)
    hline(d, 106, 4)
    hline(d, 112, 1)
    dateline = "SATURDAY  •  21  NOVEMBER  2026"
    df = f_sansb(24)
    dw = d.textlength(dateline, font=df)
    d.text(((W - dw) / 2, 120), dateline, font=df, fill=RED)
    tagline = "THE WORLD IN ONE PAGE  —  NINE STORIES THAT DEFINED THE DAY"
    gf = f_sans(17)
    gw = d.textlength(tagline, font=gf)
    d.text(((W - gw) / 2, 152), tagline, font=gf, fill=GREY)
    hline(d, 180, 3)
    hline(d, 185, 1)

    # ---------- lead story: Peru quake (195-515) ----------
    y = 195
    y = kicker(d, MX, y, "LEAD STORY  •  JUNÍN, PERU")
    lead_w = 470
    y = headline(d, MX, y, "6.8 quake shakes Peru, felt in Lima",
                 36, lead_w, 40)
    y = para(d, MX, y + 6,
             "A magnitude 6.8 earthquake struck the Andean region of Junín "
             "on Friday, Peru's Geophysical Institute said, shaking "
             "buildings and sending residents into the streets. Tremors "
             "were felt in the capital, Lima, around 320 km away.",
             f_sans(17), lead_w, 22)
    assert y <= 515, f"lead body overflows: {y}"
    # lead photo, right column
    photo = Image.open(Path(__file__).resolve().parent / "lead.jpg")
    photo = photo.convert("RGB").resize((460, 260), Image.LANCZOS)
    px, py = 530, 217
    img.paste(photo, (px, py))
    d.rectangle([px, py, px + 460, py + 260], outline=BLACK, width=2)
    d.text((px, py + 266),
           "Residents outside cracked adobe homes in Junín. Illustration.",
           font=f_sans(12), fill=GREY)
    hline(d, 522, 2)

    # ---------- middle: markets + Poland (534-740) ----------
    y = two_col_block(
        d, 534,
        "NEW YORK", "Stocks plunge as AI sell-off deepens",
        "The S&P 500 and Dow entered correction territory; the Nasdaq "
        "fell 5.3% as Nvidia dropped about 14%.",
        "WARSAW", "Russian missiles fall in Poland",
        "Two Russian missiles and a suspected drone came down in Poland. "
        "The prime minister called it a deliberate provocation; NATO "
        "called it a grave violation.",
        740, left_chart=True)
    hline(d, 748, 1)

    # ---------- lower: Anthropic + Akvan (760-884) ----------
    y = two_col_block(
        d, 760,
        "SAN FRANCISCO", "Anthropic IPO: $119.5bn, a record",
        "Anthropic closed the largest share debut ever at $119.5 "
        "billion, passing SpaceX's record.",
        "ODISHA, INDIA", "Cyclone Akvan makes landfall",
        "Cyclone Akvan crossed the Odisha coast near Gopalpur, bringing "
        "strong winds and heavy rain.",
        884, head_size=25, head_leading=28, body_size=15, body_leading=20)
    hline(d, 886, 1)

    # ---------- day in numbers (894-934) ----------
    ny = 894
    d.rectangle([MX, ny, W - MX, ny + 40], fill=BLACK)
    nums = [("6.8", "quake in Junín, Peru"),
            ("-5.3%", "Nasdaq in one day"),
            ("$119.5BN", "Anthropic IPO record"),
            ("320 KM", "tremors felt, to Lima"),
            ("$3.68BN", "Mailchimp sale price")]
    seg = (W - 2 * MX) / len(nums)
    for i, (big, small) in enumerate(nums):
        cx = MX + seg * i + seg / 2
        bf = f_sansb(19)
        bw = d.textlength(big, font=bf)
        d.text((cx - bw / 2, ny + 3), big, font=bf, fill=PAPER)
        sf = f_sans(11)
        sw = d.textlength(small, font=sf)
        d.text((cx - sw / 2, ny + 24), small, font=sf, fill=(210, 208, 198))
        if i:
            d.line([(MX + seg * i, ny + 6), (MX + seg * i, ny + 34)],
                   fill=(90, 90, 90), width=1)

    # ---------- the day in brief (942-1004) ----------
    by = 942
    d.text((MX, by), "THE DAY IN BRIEF", font=f_sansb(17), fill=BLACK)
    hline(d, by + 22, 1)
    briefs = [
        "UK and EU sign deals on food, carbon and youth mobility.",
        "Intuit sells Mailchimp for $3.68bn, a third of its 2021 price.",
        "KL Rahul's ton completes the SENA set in Wellington.",
        "Four nations urge Israel to let aid reach flooded Gaza.",
        "India's NSE becomes the world's fifth-largest exchange.",
        "FBI probes suspected hack of a national crime database.",
    ]
    half = (W - 2 * MX) // 2
    bf = f_sans(12)
    for item in briefs:
        assert d.textlength(item, font=bf) <= half - 22, \
            f"brief too long for one line: {item}"
    iy = by + 28
    for i, item in enumerate(briefs):
        col = i % 2
        row = i // 2
        x = MX + col * half
        yy = iy + row * 13
        d.text((x, yy), "\u2022", font=f_sansb(13), fill=RED)
        d.text((x + 14, yy), item, font=bf, fill=BLACK)
    assert iy + 2 * 13 + 13 <= 1010, "briefs overflow footer"

    # ---------- footer ----------
    d.text((MX, 1012), "All stories as reported on 21 November 2026. Lead photo is an AI-generated illustration of the reported scene; drawn with PIL; no invented quotes.",
           font=f_sans(10), fill=GREY)

    out = Path(__file__).resolve().parent / "entry.png"
    img.save(out, format="PNG", optimize=True)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
