"""Generate the MCB HR journey map used as the visual spine of every tutorial video.

Produces, at 1920x1080 (video-ready):
  map_00_master.png          - the full map, nothing highlighted
  map_v2..map_v8 .png        - same map with the current stage lit ("you are here")
Also a 'config' variant for Video 1.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path("/Data/odoo19_enterprise/custom-addons/mcb_hr/_build/screenshots/video/_maps")
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
NAVY = (31, 54, 77)
NAVY_D = (14, 30, 46)
GREY_BD = (196, 204, 212)
GREY_TX = (95, 108, 122)
WHITE = (255, 255, 255)
BG = (247, 249, 251)
GOLD = (232, 168, 36)
GREEN = (33, 138, 94)
DIM_FILL = (238, 242, 246)

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(sz, bold=False):
    return ImageFont.truetype(FB if bold else F, sz)


# stage key, number, title, who, produces
STAGES = [
    ("v2", "1", "REQUISITION",  "Project Manager → HR → CE", "Approved requisition\n+ Job Circular"),
    ("v3", "2", "RECRUITMENT",  "Recruitment Committee",              "Merit list\n+ Selected candidate"),
    ("v4", "3", "ONBOARDING",   "HR",                                  "Employee record\n+ Orientation tasks"),
    ("v5", "4", "LEAVE",        "Staff → Manager → HR",      "Approved leave\n+ Updated balance"),
    ("v6", "5", "EXPENSE / TA-DA", "Staff → HoD → Finance",  "Approved claim\n+ Donor cost"),
    ("v7", "6", "PAYROLL",      "Finance",                             "Payslip\n+ Bank transfer file"),
    ("v8", "7", "SEPARATION",   "Staff → Manager → HR → CE", "Final settlement\n+ Experience cert."),
]

ROW1, ROW2 = 4, 3
BOX_W, BOX_H = 400, 242
GAP_X, GAP_Y = 62, 92
TOP_ROW_Y = 388


def rrect(d, xy, r, fill, outline=None, width=2):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def centre(d, text, fnt, cx, y, fill):
    w = d.textbbox((0, 0), text, font=fnt)[2]
    d.text((cx - w / 2, y), text, font=fnt, fill=fill)


def box_pos(i):
    if i < ROW1:
        total = ROW1 * BOX_W + (ROW1 - 1) * GAP_X
        x0 = (W - total) // 2 + i * (BOX_W + GAP_X)
        return x0, TOP_ROW_Y
    j = i - ROW1
    total = ROW2 * BOX_W + (ROW2 - 1) * GAP_X
    x0 = (W - total) // 2 + j * (BOX_W + GAP_X)
    return x0, TOP_ROW_Y + BOX_H + GAP_Y


def arrow(d, x1, y1, x2, y2, colour=NAVY, w=5, head=15):
    d.line([(x1, y1), (x2, y2)], fill=colour, width=w)
    if x2 > x1:  # horizontal right
        d.polygon([(x2, y2), (x2 - head, y2 - head // 1.6), (x2 - head, y2 + head // 1.6)], fill=colour)
    elif y2 > y1:  # vertical down
        d.polygon([(x2, y2), (x2 - head // 1.6, y2 - head), (x2 + head // 1.6, y2 - head)], fill=colour)


def draw(active=None, config_lit=False, label=""):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # header
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.text((70, 26), "Mukti Cox's Bazar · HR on Odoo 19", font=font(38, True), fill=WHITE)
    d.text((72, 74), "One employee's journey — how every screen connects", font=font(22), fill=(186, 202, 218))
    if label:
        tw = d.textbbox((0, 0), label, font=font(24, True))[2]
        rrect(d, [W - tw - 110, 40, W - 60, 88], 24, GOLD)
        d.text((W - tw - 85, 51), label, font=font(24, True), fill=NAVY_D)

    # config band
    cy0, cy1 = 168, 300
    band_fill = (255, 249, 232) if config_lit else WHITE
    band_line = GOLD if config_lit else GREY_BD
    rrect(d, [150, cy0, W - 150, cy1], 18, band_fill, band_line, 4 if config_lit else 2)
    d.text((190, cy0 + 20), "SET UP ONCE", font=font(24, True), fill=GOLD if config_lit else GREY_TX)
    d.text((190, cy0 + 58),
           "Grades G1–G10  ·  Leave types  ·  BD public holidays  ·  Per-diem rates  ·  Roles (CE / PM / RC)",
           font=font(25), fill=NAVY if config_lit else GREY_TX)
    d.text((W - 470, cy0 + 20), "Video 1", font=font(22, True), fill=GREY_TX)
    d.text((W - 470, cy0 + 58), "Admin does this once", font=font(20), fill=GREY_TX)
    arrow(d, W // 2, cy1 + 8, W // 2, TOP_ROW_Y - 14)

    # stage boxes
    for i, (key, num, title, who, produces) in enumerate(STAGES):
        x, y = box_pos(i)
        on = (key == active)
        rrect(d, [x, y, x + BOX_W, y + BOX_H], 16,
              WHITE if on else DIM_FILL, NAVY if on else GREY_BD, 5 if on else 2)
        # number chip
        d.ellipse([x + 22, y + 22, x + 74, y + 74], fill=NAVY if on else GREY_BD)
        centre(d, num, font(27, True), x + 48, y + 33, WHITE)
        d.text((x + 92, y + 30), title, font=font(25, True), fill=NAVY if on else GREY_TX)
        d.text((x + 92, y + 64), who, font=font(17), fill=GREY_TX)
        d.line([(x + 24, y + 104), (x + BOX_W - 24, y + 104)], fill=GREY_BD, width=2)
        d.text((x + 26, y + 120), "produces", font=font(16, True), fill=GREY_TX)
        for k, ln in enumerate(produces.split("\n")):
            d.text((x + 26, y + 146 + k * 30), ln, font=font(20), fill=NAVY if on else GREY_TX)
        vlab = f"Video {int(num) + 1}"
        d.text((x + BOX_W - 96, y + BOX_H - 34), vlab, font=font(17, True),
               fill=GREEN if on else GREY_BD)

    # arrows row 1
    for i in range(ROW1 - 1):
        x, y = box_pos(i)
        arrow(d, x + BOX_W + 8, y + BOX_H // 2, x + BOX_W + GAP_X - 8, y + BOX_H // 2)
    # snake: end of row1 -> start of row2
    xe, ye = box_pos(ROW1 - 1)
    xs, ys = box_pos(ROW1)
    midy = ye + BOX_H + GAP_Y // 2
    d.line([(xe + BOX_W // 2, ye + BOX_H + 6), (xe + BOX_W // 2, midy)], fill=NAVY, width=5)
    d.line([(xe + BOX_W // 2, midy), (xs + BOX_W // 2, midy)], fill=NAVY, width=5)
    arrow(d, xs + BOX_W // 2, midy, xs + BOX_W // 2, ys - 8)
    # arrows row 2
    for i in range(ROW1, ROW1 + ROW2 - 1):
        x, y = box_pos(i)
        arrow(d, x + BOX_W + 8, y + BOX_H // 2, x + BOX_W + GAP_X - 8, y + BOX_H // 2)

    # footer note
    d.text((150, H - 58),
           "Each stage hands its record to the next — nothing is re-typed. "
           "Follow one person: Rashedul Karim, MEAL Officer.",
           font=font(23), fill=GREY_TX)
    return img


made = []
img = draw(active=None, label="THE MAP")
p = OUT / "map_00_master.png"; img.save(p); made.append(p.name)

img = draw(active=None, config_lit=True, label="YOU ARE HERE")
p = OUT / "map_v1_config.png"; img.save(p); made.append(p.name)

for key, num, title, *_ in STAGES:
    img = draw(active=key, label="YOU ARE HERE")
    p = OUT / f"map_{key}_{title.split()[0].lower().replace('/', '')}.png"
    img.save(p); made.append(p.name)

print("wrote", len(made), "maps:")
for m in made:
    print("  ", m)
