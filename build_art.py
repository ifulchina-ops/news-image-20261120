#!/usr/bin/env python3
"""Paint the Twenty-One front page for Saturday 21 November 2026.

A single 1024x1024 broadsheet page, drawn with Pillow and the DejaVu
family. The nameplate carries the date; the lead story is the
magnitude 6.8 earthquake in Junin, Peru, with an AI-generated
illustration of the reported scene as the lead photo (captioned as an
illustration); below it sit the Wall Street correction, the missiles
in Poland, Anthropic's record IPO and Cyclone Akvan, a black strip of
the day's numbers, and six briefs. Every story is as reported on
21 November 2026; nothing is invented.

Run this file to repaint entry.png next to it. The render is fully
deterministic: identical inputs give identical bytes.
"""
import pathlib

from PIL import Image
from PIL import ImageDraw, ImageFont

PAGE_W, PAGE_H = 1024, 1024
EDGE = 34
INK = (15, 15, 15)
NEWS = (252, 250, 244)
ACCENT = (165, 12, 12)
ASH = (96, 96, 96)
FONT_DIR = pathlib.Path("/usr/share/fonts/truetype/dejavu")

PAPER_NAME = "TWENTY-ONE"
DATELINE = "SATURDAY  •  21  NOVEMBER  2026"
TAGLINE = "THE WORLD IN ONE PAGE  —  NINE STORIES THAT DEFINED THE DAY"

LEAD_TAG = "LEAD STORY  •  JUNÍN, PERU"
LEAD_HEAD = "6.8 quake shakes Peru, felt in Lima"
LEAD_BODY = "A magnitude 6.8 earthquake struck the Andean region of Junín on Friday, Peru's Geophysical Institute said, shaking buildings and sending residents into the streets. Tremors were felt in the capital, Lima, around 320 km away."
LEAD_CAPTION = "Residents outside cracked adobe homes in Junín. Illustration."

MARKETS = ("NEW YORK",
           "Stocks plunge as AI sell-off deepens",
           "The S&P 500 and Dow entered correction territory; the Nasdaq fell 5.3% as Nvidia dropped about 14%.")
POLAND = ("WARSAW",
          "Russian missiles fall in Poland",
          "Two Russian missiles and a suspected drone came down in Poland. The prime minister called it a deliberate provocation; NATO called it a grave violation.")
ANTHROPIC = ("SAN FRANCISCO",
             "Anthropic IPO: $119.5bn, a record",
             "Anthropic closed the largest share debut ever at $119.5 billion, passing SpaceX's record.")
AKVAN = ("ODISHA, INDIA",
         "Cyclone Akvan makes landfall",
         "Cyclone Akvan crossed the Odisha coast near Gopalpur, bringing strong winds and heavy rain.")

NUMBERS = (
    ("6.8", "quake in Junín, Peru"),
    ("-5.3%", "Nasdaq in one day"),
    ("$119.5BN", "Anthropic IPO record"),
    ("320 KM", "tremors felt, to Lima"),
    ("$3.68BN", "Mailchimp sale price"),
)

BRIEFS = (
    "UK and EU sign deals on food, carbon and youth mobility.",
    "Intuit sells Mailchimp for $3.68bn, a third of its 2021 price.",
    "KL Rahul's ton completes the SENA set in Wellington.",
    "Four nations urge Israel to let aid reach flooded Gaza.",
    "India's NSE becomes the world's fifth-largest exchange.",
    "FBI probes suspected hack of a national crime database.",
)

FOOTER = "All stories as reported on 21 November 2026. Lead photo is an AI-generated illustration of the reported scene; drawn with PIL; no invented quotes."


def serif(size):
    return ImageFont.truetype(str(FONT_DIR / "DejaVuSerif-Bold.ttf"), size)


def sans(size):
    return ImageFont.truetype(str(FONT_DIR / "DejaVuSans.ttf"), size)


def sans_bold(size):
    return ImageFont.truetype(str(FONT_DIR / "DejaVuSans-Bold.ttf"), size)


def fold(draw, text, font, width):
    """Split text into lines that fit inside `width` pixels, greedily."""
    out = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip() if current else word
        if draw.textlength(candidate, font=font) <= width:
            current = candidate
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def block(draw, x, top, text, font, width, step):
    """Draw a wrapped paragraph; returns the y just below it."""
    y = top
    for line in fold(draw, text, font, width):
        draw.text((x, y), line, font=font, fill=INK)
        y += step
    return y


def rule(draw, y, weight=2, left=None, right=None):
    """A horizontal rule across the page (or between two x bounds)."""
    draw.line([(EDGE if left is None else left, y),
               (PAGE_W - EDGE if right is None else right, y)],
              fill=INK, width=weight)


def tag(draw, x, top, text):
    """A small red kicker line above a headline."""
    draw.text((x, top), text, font=sans_bold(16), fill=ACCENT)
    return top + 24


def title(draw, x, top, text, size, width, step):
    """A serif headline, wrapped to `width`."""
    return block(draw, x, top, text, serif(size), width, step)


def plunge_chart(draw, x, top, width, height):
    """A small falling-line chart for the markets story."""
    draw.rectangle([x, top, x + width, top + height], outline=ASH, width=1)
    for row in range(1, 4):
        gy = top + height * row / 4
        draw.line([(x, gy), (x + width, gy)], fill=(220, 218, 208), width=1)
    trail = [(0.00, 0.12), (0.12, 0.22), (0.24, 0.18),
             (0.36, 0.38), (0.48, 0.34), (0.60, 0.55),
             (0.72, 0.62), (0.84, 0.78), (1.00, 0.92)]
    points = [(x + width * fx, top + height * fy) for fx, fy in trail]
    draw.line(points, fill=ACCENT, width=3, joint="curve")
    label = "-5.3%"
    label_w = draw.textlength(label, font=sans_bold(13))
    draw.text((x + width - label_w - 4, top + 3), label,
              font=sans_bold(13), fill=ACCENT)


def side_by_side(draw, top, left, right, limit, head_size=27,
                 head_step=30, body_size=16, body_step=21, chart=False):
    """Render two stories next to each other; returns the y below them.

    Each story is a (kicker, headline, body) triple. The block must end
    at or above `limit`, or the page layout is broken and we fail.
    """
    col = (PAGE_W - 2 * EDGE) // 2 - 14
    right_x = EDGE + col + 28
    ly = tag(draw, EDGE, top, left[0])
    ly = title(draw, EDGE, ly, left[1], head_size, col, head_step)
    ly = block(draw, EDGE, ly + 4, left[2], sans(body_size), col, body_step)
    if chart:
        plunge_chart(draw, EDGE, ly + 6, col, 44)
        ly += 56
    ry = tag(draw, right_x, top, right[0])
    ry = title(draw, right_x, ry, right[1], head_size, col, head_step)
    ry = block(draw, right_x, ry + 4, right[2], sans(body_size), col, body_step)
    bottom = max(ly, ry)
    assert bottom <= limit, f"side-by-side block runs past {limit}: {bottom}"
    return bottom


def draw_masthead(draw):
    """Nameplate, date line and tagline across the top of the page."""
    title_font = serif(76)
    title_w = draw.textlength(PAPER_NAME, font=title_font)
    draw.text(((PAGE_W - title_w) / 2, 10), PAPER_NAME,
              font=title_font, fill=INK)
    rule(draw, 106, 4)
    rule(draw, 112, 1)
    date_font = sans_bold(24)
    date_w = draw.textlength(DATELINE, font=date_font)
    draw.text(((PAGE_W - date_w) / 2, 120), DATELINE,
              font=date_font, fill=ACCENT)
    tag_font = sans(17)
    tag_w = draw.textlength(TAGLINE, font=tag_font)
    draw.text(((PAGE_W - tag_w) / 2, 152), TAGLINE, font=tag_font, fill=ASH)
    rule(draw, 180, 3)
    rule(draw, 185, 1)


def draw_lead(sheet, draw):
    """The quake story: headline and body left, photo right."""
    top = 195
    top = tag(draw, EDGE, top, LEAD_TAG)
    text_w = 470
    top = title(draw, EDGE, top, LEAD_HEAD, 36, text_w, 40)
    top = block(draw, EDGE, top + 6, LEAD_BODY, sans(17), text_w, 22)
    assert top <= 515, f"lead story runs past its band: {top}"
    here = pathlib.Path(__file__).resolve().parent
    photo = Image.open(here / "lead.jpg")
    photo = photo.convert("RGB")
    photo = photo.resize((460, 260), Image.LANCZOS)
    px, py = 530, 217
    sheet.paste(photo, (px, py))
    draw.rectangle([px, py, px + 460, py + 260], outline=INK, width=2)
    draw.text((px, py + 266), LEAD_CAPTION, font=sans(12), fill=ASH)
    rule(draw, 522, 2)


def draw_numbers(draw):
    """Black band: five figures from the day, side by side."""
    top = 894
    draw.rectangle([EDGE, top, PAGE_W - EDGE, top + 40], fill=INK)
    slot = (PAGE_W - 2 * EDGE) / len(NUMBERS)
    for idx, (big, small) in enumerate(NUMBERS):
        centre = EDGE + slot * idx + slot / 2
        big_font = sans_bold(19)
        big_w = draw.textlength(big, font=big_font)
        draw.text((centre - big_w / 2, top + 3), big,
                  font=big_font, fill=NEWS)
        small_font = sans(11)
        small_w = draw.textlength(small, font=small_font)
        draw.text((centre - small_w / 2, top + 24), small,
                  font=small_font, fill=(210, 208, 198))
        if idx:
            draw.line([(EDGE + slot * idx, top + 6),
                       (EDGE + slot * idx, top + 34)],
                      fill=(90, 90, 90), width=1)


def draw_briefs(draw):
    """Six one-line briefs in two columns under a heading."""
    top = 942
    draw.text((EDGE, top), "THE DAY IN BRIEF", font=sans_bold(17), fill=INK)
    rule(draw, top + 22, 1)
    half = (PAGE_W - 2 * EDGE) // 2
    brief_font = sans(12)
    for item in BRIEFS:
        assert draw.textlength(item, font=brief_font) <= half - 22, \
            f"brief does not fit on one line: {item}"
    first = top + 28
    for pos, item in enumerate(BRIEFS):
        col, row = pos % 2, pos // 2
        x = EDGE + col * half
        y = first + row * 13
        draw.text((x, y), "\u2022", font=sans_bold(13), fill=ACCENT)
        draw.text((x + 14, y), item, font=brief_font, fill=INK)
    assert first + 2 * 13 + 13 <= 1010, "briefs run into the footer"


def paint():
    """Draw the whole page and return the finished image."""
    sheet = Image.new("RGB", (PAGE_W, PAGE_H), NEWS)
    draw = ImageDraw.Draw(sheet)
    draw_masthead(draw)
    draw_lead(sheet, draw)
    side_by_side(draw, 534, MARKETS, POLAND, 740, chart=True)
    rule(draw, 748, 1)
    side_by_side(draw, 760, ANTHROPIC, AKVAN, 884,
                 head_size=25, head_step=28, body_size=15, body_step=20)
    rule(draw, 886, 1)
    draw_numbers(draw)
    draw_briefs(draw)
    draw.text((EDGE, 1012), FOOTER, font=sans(10), fill=ASH)
    return sheet


def main():
    here = pathlib.Path(__file__).resolve().parent
    page = paint()
    target = here / "entry.png"
    page.save(target, format="PNG", optimize=True)
    size = target.stat().st_size
    assert size <= 1_048_576, f"entry.png is {size} bytes, over the 1 MiB ceiling"
    print(f"Painted {target} ({size} bytes)")


if __name__ == "__main__":
    main()
