"""Render every recorded click-path flow as an MP4.

Frames are STATIC — no zoompan. Zooming a UI screenshot resamples the text every
frame and reads as the screen shaking. The only movement is the cut between
steps, plus a title card, a part divider when the role changes, and an end card.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BUILD = Path("/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
FLOWS = BUILD / "flows"
OUTDIR = Path("/Data/odoo19_enterprise/mukticox/video")
W, H, FPS = 1920, 1080, 30

HOLD = 5.5          # normal step
HOLD_LOGIN = 6.5    # login screens - viewers need time to read the credentials
TITLE_SEC = 6.0
DIVIDER_SEC = 3.5
END_SEC = 4.5
BRAND = "MCB HR"   # overridden by the Accounts renderer

NAVY = (31, 54, 77)
NAVY_D = (12, 26, 40)
WHITE = (255, 255, 255)
GOLD = (240, 180, 40)
DIM = (190, 206, 222)

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(sz, bold=False):
    return ImageFont.truetype(FB if bold else F, sz)


def wrap(d, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textbbox((0, 0), t, font=fnt)[2] <= max_w:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    return lines


def letterbox(src, out):
    im = Image.open(src).convert("RGB")
    canvas = Image.new("RGB", (W, H), NAVY_D)
    r = min(W / im.width, H / im.height)
    nw, nh = int(im.width * r), int(im.height * r)
    canvas.paste(im.resize((nw, nh), Image.LANCZOS), ((W - nw) // 2, (H - nh) // 2))
    canvas.save(out)


def title_card(out, flow_no, title, summary, logins):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    d.text((120, 96), f"{BRAND}  ·  FLOW {flow_no}", font=font(26, True), fill=GOLD)

    y = 168
    for ln in wrap(d, title, font(64, True), W - 260):
        d.text((120, y), ln, font=font(64, True), fill=WHITE)
        y += 82
    d.line([(120, y + 16), (420, y + 16)], fill=GOLD, width=5)
    y += 54
    for ln in wrap(d, summary, font(30), W - 300)[:3]:
        d.text((120, y), ln, font=font(30), fill=DIM)
        y += 46

    # test logins panel
    py = max(y + 56, 640)
    ph = 132 + 62 * len(logins)
    d.rounded_rectangle([120, py, 1180, py + ph], radius=16,
                        fill=NAVY_D, outline=GOLD, width=3)
    d.text((156, py + 22), "TEST LOGINS — use these to try it yourself",
           font=font(26, True), fill=GOLD)
    ly = py + 104
    for role, u, p in logins:
        d.text((156, ly), role, font=font(24), fill=DIM)
        d.text((620, ly), u, font=font(25, True), fill=WHITE)
        d.text((900, ly), p, font=font(25, True), fill=WHITE)
        ly += 62
    d.text((620, py + 68), "username", font=font(18), fill=(140, 158, 176))
    d.text((900, py + 68), "password", font=font(18), fill=(140, 158, 176))
    img.save(out)


def divider_card(out, text, sub):
    img = Image.new("RGB", (W, H), NAVY_D)
    d = ImageDraw.Draw(img)
    f1, f2 = font(62, True), font(30)
    lines = wrap(d, text, f1, W - 300)
    y = 430 - (len(lines) - 1) * 40
    for ln in lines:
        tw = d.textbbox((0, 0), ln, font=f1)[2]
        d.text(((W - tw) / 2, y), ln, font=f1, fill=WHITE)
        y += 80
    d.line([(W / 2 - 80, y + 20), (W / 2 + 80, y + 20)], fill=GOLD, width=5)
    tw = d.textbbox((0, 0), sub, font=f2)[2]
    d.text(((W - tw) / 2, y + 56), sub, font=f2, fill=DIM)
    img.save(out)


FLOW_META = {
    "requisition": (1, "Asking for a New Staff Member",
                    "A Project Manager raises a Staff Requisition. HR checks it, the Chief Executive approves it, and the job circular is printed.",
                    [("Project Manager / HR / CE", "admin", "admin")]),
    "recruitment": (2, "Applicants, Exams and the Merit List",
                    "Candidates are shortlisted, sit the exams, and the system builds the merit list from the marks.",
                    [("Recruitment Committee / HR", "admin", "admin")]),
    "onboarding": (3, "Hiring and Onboarding",
                   "HR turns the selected candidate into an employee, fills the MCB profile and starts the orientation plan.",
                   [("HR", "admin", "admin")]),
    "leave": (4, "Applying for Leave and Getting it Approved",
              "An employee asks for 3 days off. His line manager logs in and approves it. The balance updates by itself.",
              [("Employee (Rashedul)", "rashedul", "rashedul"),
               ("Line Manager", "admin", "admin")]),
    "expense": (5, "Claiming Travel Money (TA / DA)",
                "An employee claims his field-visit allowance. The rate comes from his grade. His head of department logs in and approves it.",
                [("Employee (Rashedul)", "rashedul", "rashedul"),
                 ("Head of Department", "admin", "admin")]),
    "payroll": (6, "Running the Monthly Payroll",
                "Finance creates the month's batch, checks the payslips and produces the bank transfer file.",
                [("Finance / Payroll Officer", "admin", "admin")]),
    "separation": (7, "Resignation and Final Settlement",
                   "A staff member resigns with short notice. The system works out the shortfall, the settlement and the certificate.",
                   [("HR / Manager / CE", "admin", "admin")]),
}

END_TEXT = {
    "requisition": ("The post is now open", "Next: applications arrive — Flow 2"),
    "recruitment": ("The merit list is ready", "Next: the winner becomes an employee — Flow 3"),
    "onboarding": ("He is now a member of staff", "Next: leave, travel money and payroll"),
    "leave": ("Leave approved", "The balance dropped by itself, and the history shows who approved it"),
    "expense": ("Claim approved", "Charged to the right project and donor"),
    "payroll": ("Everybody is paid", "One bank file, generated from the system"),
    "separation": ("The file is closed", "Settlement paid, certificate issued, access switched off"),
}


def build(flow):
    src = FLOWS / flow
    if not (src / "steps.json").exists():
        print(f"  !! no capture for {flow}")
        return None
    steps = json.loads((src / "steps.json").read_text())
    no, title, summary, logins = FLOW_META[flow]

    work = BUILD / "_flowvid" / flow
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    frames = []
    tc = work / "000_title.png"
    title_card(tc, no, title, summary, logins)
    frames.append((tc, TITLE_SEC))

    prev_role = None
    for st in steps:
        p = src / st["file"]
        if not p.exists():
            continue
        role = (st.get("role") or "").split("(")[0].strip()
        # when the acting person changes, put a divider card in front
        if prev_role is not None and role and role != prev_role and st["slug"] == "login_screen":
            dv = work / f"div_{st['n']:03d}.png"
            divider_card(dv, f"Now {st['role']} takes over",
                         "They log in with their own account")
            frames.append((dv, DIVIDER_SEC))
        prev_role = role or prev_role

        f = work / f"{st['n']:03d}.png"
        letterbox(p, f)
        frames.append((f, HOLD_LOGIN if st["slug"].startswith("login") else HOLD))

    et, es = END_TEXT.get(flow, ("Done", ""))
    ec = work / "999_end.png"
    divider_card(ec, et, es)
    frames.append((ec, END_SEC))

    segs = []
    for i, (img, dur) in enumerate(frames):
        seg = work / f"seg_{i:03d}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(img),
                        "-t", f"{dur}", "-vf", f"scale={W}:{H},format=yuv420p", "-r", str(FPS),
                        "-c:v", "libx264", "-preset", "medium", "-crf", "20", str(seg)],
                       check=True)
        segs.append(seg)

    lst = work / "list.txt"
    lst.write_text("".join(f"file '{s}'\n" for s in segs))
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = OUTDIR / f"{no}_MCB_HR_{flow.capitalize()}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], check=True)
    total = sum(d for _, d in frames)
    print(f"  {out.name:34s} {out.stat().st_size/1048576:5.1f} MB · "
          f"{int(total//60)}m{int(total%60):02d}s · {len(steps)} steps")
    return out


if __name__ == "__main__":
    wanted = sys.argv[1:] or ["requisition", "recruitment", "onboarding",
                              "leave", "expense", "payroll", "separation"]
    print("Rendering flow videos (static frames — no shake):")
    for f in wanted:
        build(f)
