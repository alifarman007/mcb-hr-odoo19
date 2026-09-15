"""Render an animated MP4 walkthrough of the MCB HR journey.

Composes each slide with Pillow (header + screenshot card + instruction band),
turns every slide into a short Ken-Burns segment with ffmpeg, then concatenates
them with crossfades.

Output: /Data/odoo19_enterprise/mukticox/MCB_HR_Overview_Animation.mp4
"""
import shutil
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BUILD = Path("/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
SHOT = BUILD / "screenshots" / "video"
MAPS = SHOT / "_maps"
WORK = BUILD / "_anim"
OUT = Path("/Data/odoo19_enterprise/mukticox/MCB_HR_Overview_Animation.mp4")

W, H = 1920, 1080
FPS = 30
NAVY = (31, 54, 77)
NAVY_D = (12, 26, 40)
WHITE = (255, 255, 255)
BG = (241, 245, 249)
GOLD = (232, 168, 36)
GREY_TX = (100, 112, 126)
CARD_BD = (208, 216, 224)

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(sz, bold=False):
    return ImageFont.truetype(FB if bold else F, sz)


def wrap(d, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textbbox((0, 0), trial, font=fnt)[2] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


# =============================================================================
# SLIDES:  (image, stage chip, headline, instruction, seconds)
# =============================================================================
S = [
    (None, "", "Mukti Cox's Bazar",
     "HR on Odoo 19 — how the whole system fits together", 4.5),

    (MAPS / "map_00_master.png", "THE MAP", "One journey, seven stages",
     "Every stage hands its paperwork to the next one. Nothing is typed twice.", 6.5),

    (MAPS / "map_v1_config.png", "SET UP ONCE", "First, the rules go in",
     "Grades, leave types, holidays, travel rates and roles — the administrator does this once.", 5.5),
    (SHOT / "v1_config/01_grades_list_g1_g10.png", "SET UP ONCE", "Ten grades, G1 to G10",
     "The grade is the master switch: it drives salary, leave, travel rates and overtime.", 5.5),
    (SHOT / "v1_config/03_leave_types_list.png", "SET UP ONCE", "Eight kinds of leave",
     "Each type carries its own rule — like blocking annual leave during probation.", 5.0),
    (SHOT / "v1_config/07_per_diem_rate_table.png", "SET UP ONCE", "Travel and food rates",
     "Enter TA/DA rates once. Every future claim fills in the correct amount by itself.", 5.0),

    (MAPS / "map_v2_requisition.png", "STAGE 1", "Asking for new staff",
     "A Project Manager raises a Staff Requisition — the old Form 21a on screen.", 5.0),
    (SHOT / "v2_requisition/02_requisition_form_published.png", "STAGE 1", "One form, three approvals",
     "Project Manager submits → HR reviews → Chief Executive approves. Every step is time-stamped.", 6.0),
    (SHOT / "v2_requisition/06_job_circular_pdf.png", "STAGE 1", "The circular writes itself",
     "Publish the requisition and the job circular is generated on MCB letterhead.", 5.0),

    (MAPS / "map_v3_recruitment.png", "STAGE 2", "Choosing fairly — and proving it",
     "Applications, admit cards, exams and an automatic merit list.", 5.0),
    (SHOT / "v3_recruitment/03_applicant_form_rashedul.png", "STAGE 2", "Meet Rashedul Karim",
     "Follow one candidate all the way through: MEAL Officer, Cox's Bazar, funded by UNFPA.", 5.5),
    (SHOT / "v3_recruitment/05_admit_card_pdf.png", "STAGE 2", "Admit cards, numbered",
     "Each shortlisted candidate gets a unique admit card with exam date, time and venue.", 5.0),
    (SHOT / "v3_recruitment/02_applicants_list_with_marks.png", "STAGE 2", "The merit list is computed",
     "Written 50 + Computer 20 + Oral 30. The system ranks them — nobody types the order.", 6.0),

    (MAPS / "map_v4_onboarding.png", "STAGE 3", "From candidate to colleague",
     "One button turns the selected candidate into an employee record.", 5.0),
    (SHOT / "v4_onboarding/03_employee_mcb_profile_tab.png", "STAGE 3", "The MCB profile",
     "NID, parents, service dates, probation dates and the Provident Fund nominee.", 5.5),
    (SHOT / "v4_onboarding/06_activity_plans_list.png", "STAGE 3", "Orientation starts itself",
     "Ten mandatory sessions plus ID card, email, bank details and contract signing.", 5.5),

    (MAPS / "map_v5_leave.png", "STAGE 4", "Taking leave",
     "The video most staff will watch — because everybody takes leave.", 5.0),
    (SHOT / "v5_leave/01_timeoff_dashboard_balances.png", "STAGE 4", "Balance first",
     "Your entitlement is on screen before you apply. Weekends and holidays are never counted.", 5.5),
    (SHOT / "v5_leave/03_leave_pending_approval_buttons.png", "STAGE 4", "Two approvals",
     "Line Manager approves, then HR. Compensatory leave needs a third — the Chief Executive.", 6.0),

    (MAPS / "map_v6_expense.png", "STAGE 5", "Claiming travel money",
     "TA and DA, calculated from the grade — not from an argument.", 5.0),
    (SHOT / "v6_expense/03_expense_form_ta_da.png", "STAGE 5", "The rate fills itself in",
     "62 km and an overnight stay. Click Apply Per Diem and the policy rate appears.", 6.0),

    (MAPS / "map_v7_payroll.png", "STAGE 6", "Monthly payroll",
     "Everything set up earlier quietly pays off here.", 5.0),
    (SHOT / "v7_payroll/02_structure_mcb_permanent_rules.png", "STAGE 6", "Policy written as arithmetic",
     "Provident fund, festival bonus, Baishakhi, gratuity and Bangladesh tax slabs.", 6.0),
    (SHOT / "v7_payroll/05_payslip_form.png", "STAGE 6", "Every line explainable",
     "Open any payslip and point to the rule that produced each number.", 5.5),

    (MAPS / "map_v8_separation.png", "STAGE 7", "When someone leaves",
     "Notice period, exit interview, final settlement, certificate — then access is switched off.", 5.5),
    (SHOT / "v8_separation/02_resignation_form_short_notice.png", "STAGE 7", "The rule does the arguing",
     "60 days' notice required, 20 given — the system works out the shortfall and the salary in lieu.", 6.5),

    (MAPS / "map_00_master.png", "COMPLETE", "One journey, fully recorded",
     "Every approval carries a name and a time. That is what makes it auditable.", 6.0),

    (None, "", "Ready to start?",
     "Watch the 9-part tutorial series — each stage in detail, step by step.", 5.0),
]


def make_slide(idx, img, chip, headline, instruction, path):
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)

    title_only = img is None

    # header
    d.rectangle([0, 0, W, 108], fill=NAVY)
    d.text((64, 30), "Mukti Cox's Bazar · HR on Odoo 19", font=font(32, True), fill=WHITE)
    if chip:
        f = font(22, True)
        tw = d.textbbox((0, 0), chip, font=f)[2]
        d.rounded_rectangle([W - tw - 116, 32, W - 56, 78], radius=23, fill=GOLD)
        d.text((W - tw - 86, 42), chip, font=f, fill=NAVY_D)

    if title_only:
        # centred title card
        d.rectangle([0, 108, W, H], fill=NAVY)
        f1, f2 = font(86, True), font(36)
        lines = wrap(d, headline, f1, W - 300)
        y = 380
        for ln in lines:
            tw = d.textbbox((0, 0), ln, font=f1)[2]
            d.text(((W - tw) / 2, y), ln, font=f1, fill=WHITE)
            y += 104
        d.line([(W / 2 - 90, y + 26), (W / 2 + 90, y + 26)], fill=GOLD, width=5)
        y += 66
        for ln in wrap(d, instruction, f2, W - 460):
            tw = d.textbbox((0, 0), ln, font=f2)[2]
            d.text(((W - tw) / 2, y), ln, font=f2, fill=(196, 210, 224))
            y += 52
        canvas.save(path)
        return

    # headline
    d.text((64, 138), headline, font=font(44, True), fill=NAVY)

    # instruction band (bottom)
    band_h = 150
    by0 = H - band_h
    d.rectangle([0, by0, W, H], fill=NAVY)
    fi = font(31)
    lines = wrap(d, instruction, fi, W - 260)[:2]
    ty = by0 + (band_h - len(lines) * 44) / 2
    for ln in lines:
        tw = d.textbbox((0, 0), ln, font=fi)[2]
        d.text(((W - tw) / 2, ty), ln, font=fi, fill=WHITE)
        ty += 44

    # screenshot card
    area_top, area_bot = 212, by0 - 34
    max_w, max_h = W - 200, area_bot - area_top
    im = Image.open(img).convert("RGB")
    # long full-page shots: keep the top portion so it stays readable
    if im.height > im.width * 1.15:
        im = im.crop((0, 0, im.width, int(im.width * 1.05)))
    r = min(max_w / im.width, max_h / im.height)
    nw, nh = int(im.width * r), int(im.height * r)
    im = im.resize((nw, nh), Image.LANCZOS)
    x0, y0 = (W - nw) // 2, area_top + (max_h - nh) // 2
    d.rectangle([x0 + 6, y0 + 8, x0 + nw + 6, y0 + nh + 8], fill=(214, 221, 229))
    canvas.paste(im, (x0, y0))
    d.rectangle([x0, y0, x0 + nw, y0 + nh], outline=CARD_BD, width=2)
    canvas.save(path)


def main():
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    # 1) compose slides
    segs = []
    for i, (img, chip, head, instr, dur) in enumerate(S):
        if img is not None and not Path(img).exists():
            print("  skip (missing):", img)
            continue
        sp = WORK / f"slide_{i:02d}.png"
        make_slide(i, img, chip, head, instr, sp)
        segs.append((sp, dur))
    print(f"composed {len(segs)} slides")

    # 2) each slide -> a short segment with a slow Ken-Burns zoom
    seg_files = []
    for i, (sp, dur) in enumerate(segs):
        mp4 = WORK / f"seg_{i:02d}.mp4"
        frames = int(dur * FPS)
        # zoom very gently from 1.00 to ~1.06 across the segment
        vf = (
            f"scale={W*2}:{H*2},"
            f"zoompan=z='min(1.06,1+0.06*on/{frames})':d={frames}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
            f"format=yuv420p"
        )
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(sp),
               "-t", f"{dur}", "-vf", vf, "-r", str(FPS),
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", str(mp4)]
        subprocess.run(cmd, check=True)
        seg_files.append(mp4)
    print(f"rendered {len(seg_files)} segments")

    # 3) concatenate with crossfades
    lst = WORK / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in seg_files))
    concat = WORK / "concat.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c", "copy", str(concat)], check=True)

    # gentle fade in/out on the whole film
    total = sum(d for _, d in segs)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(concat),
                    "-vf", f"fade=t=in:st=0:d=0.8,fade=t=out:st={total-1.0:.2f}:d=1.0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT)], check=True)

    size = OUT.stat().st_size
    print(f"\nWrote {OUT}")
    print(f"  {size/1_048_576:.1f} MB · {total:.0f}s (~{total/60:.1f} min) · {len(segs)} slides · {W}x{H} @ {FPS}fps")


if __name__ == "__main__":
    main()
