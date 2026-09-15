"""Click-path recorder.

Walks a real user journey in the browser. Before every click it screenshots the
page AND records the exact position of the element that must be clicked, then
draws a marker on it (ring + cursor + step number + instruction band).

Output per flow:  _build/flows/<flow>/NN_<slug>.png   (annotated, 1440x900)
                  _build/flows/<flow>/steps.json      (captions for docx/video)
"""
import json
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8069"
DB = "mcb_demo"
ROOT = Path("/Data/odoo19_enterprise/custom-addons/mcb_hr/_build/flows")

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
RED = (214, 45, 45)
NAVY = (31, 54, 77)
WHITE = (255, 255, 255)
GOLD = (240, 180, 40)


def font(sz, bold=False):
    return ImageFont.truetype(FB if bold else F, sz)


# ---------------------------------------------------------------- browser ---
def clean(page):
    try:
        page.evaluate(
            "document.querySelectorAll('.database_expiration_panel')"
            ".forEach(e=>{const o=e.closest('div[style*=\"position: absolute\"]')||e;o.remove();})")
    except Exception:
        pass


def find(page, selectors):
    """Return the first visible locator from a list of candidate selectors."""
    for sel in selectors:
        try:
            if sel.startswith("text="):
                loc = page.get_by_text(sel[5:], exact=False).first
            elif sel.startswith("role="):
                _, role, name = sel.split("=", 2)
                loc = page.get_by_role(role, name=name).first
            else:
                loc = page.locator(sel).first
            if loc.count() and loc.is_visible():
                return loc
        except Exception:
            continue
    return None


# -------------------------------------------------------------- annotate ---
def creds_panel(d, W, H, user, pw):
    """Show the test login on screen so viewers can try it themselves."""
    bw, bh = 430, 132
    x0, y0 = 28, H - bh - 26
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=12,
                        fill=(12, 26, 40, 238), outline=GOLD, width=3)
    d.text((x0 + 20, y0 + 14), "TEST LOGIN — try it yourself", font=font(17, True), fill=GOLD)
    d.text((x0 + 20, y0 + 50), "Email / Username", font=font(16), fill=(168, 186, 204))
    d.text((x0 + 210, y0 + 48), user, font=font(19, True), fill=WHITE)
    d.text((x0 + 20, y0 + 88), "Password", font=font(16), fill=(168, 186, 204))
    d.text((x0 + 210, y0 + 86), pw, font=font(19, True), fill=WHITE)


def annotate(png, box, step_no, headline, instruction, role, out, creds=None,
             total=None):
    im = Image.open(png).convert("RGB")
    W, H = im.size
    BAND = 118
    canvas = Image.new("RGB", (W, H + BAND), NAVY)
    canvas.paste(im, (0, 0))
    d = ImageDraw.Draw(canvas, "RGBA")
    if creds:
        creds_panel(d, W, H, creds[0], creds[1])

    # marker on the click target
    if box:
        x, y, w, h = box["x"], box["y"], box["width"], box["height"]
        pad = 8
        x0, y0, x1, y1 = x - pad, y - pad, x + w + pad, y + h + pad
        # soft glow then solid ring
        for i, alpha in ((10, 45), (6, 90)):
            d.rounded_rectangle([x0 - i, y0 - i, x1 + i, y1 + i], radius=12 + i,
                                outline=(RED[0], RED[1], RED[2], alpha), width=4)
        d.rounded_rectangle([x0, y0, x1, y1], radius=10, outline=RED, width=4)
        # cursor arrow just below-right of the target
        cx, cy = x + w * 0.62, y + h + 12
        if cy > H - 60:
            cy = y - 46
        d.polygon([(cx, cy), (cx, cy + 30), (cx + 8, cy + 22),
                   (cx + 14, cy + 34), (cx + 20, cy + 30), (cx + 14, cy + 19),
                   (cx + 24, cy + 18)], fill=WHITE, outline=(20, 20, 20))
        # step badge on the ring
        bx, by = x0 - 20, y0 - 20
        bx, by = max(18, bx), max(18, by)
        d.ellipse([bx - 20, by - 20, bx + 20, by + 20], fill=RED)
        t = str(step_no)
        tw = d.textbbox((0, 0), t, font=font(22, True))[2]
        d.text((bx - tw / 2, by - 14), t, font=font(22, True), fill=WHITE)

    # role chip (top-right of the screenshot area)
    if role:
        f = font(19, True)
        tw = d.textbbox((0, 0), role, font=f)[2]
        d.rounded_rectangle([W - tw - 76, 14, W - 24, 56], radius=21, fill=GOLD)
        d.text((W - tw - 50, 24), role, font=f, fill=(30, 30, 30))

    # instruction band
    d.rectangle([0, H, W, H + BAND], fill=NAVY)
    lbl = f"STEP {step_no}" + (f" / {total}" if total else "")
    d.text((30, H + 18), lbl, font=font(19, True), fill=GOLD)
    d.text((162, H + 16), headline, font=font(26, True), fill=WHITE)
    d.text((30, H + 62), instruction, font=font(22), fill=(196, 212, 228))
    canvas.save(out)


# ------------------------------------------------------------------ run ----
def run_flow(flow_name, steps, login_as=("admin", "admin")):
    out_dir = ROOT / flow_name
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = out_dir / "_raw"
    raw.mkdir(exist_ok=True)
    meta = []

    # a login-bearing step is expanded into 3 captured screens
    total = sum(3 if s.get("login") else 1 for s in steps)

    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        page = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
        n = 0

        def capture(slug, headline, instruction, role, target, creds=None,
                    note="", scroll=True):
            """Screenshot the current page, ring the target, write the meta row."""
            nonlocal n
            n += 1
            clean(page)
            box, loc = None, (find(page, target) if target else None)
            if loc:
                if scroll:
                    try:
                        loc.scroll_into_view_if_needed(timeout=4000)
                        time.sleep(0.8)
                    except Exception:
                        pass
                try:
                    box = loc.bounding_box()
                    if box and (box["y"] < 0 or box["y"] > 880):
                        box = None
                except Exception:
                    box = None
            if target and not box:
                print(f"  step {n}: target NOT found -> {target[:1]}")
            rawp = raw / f"{n:02d}.png"
            page.screenshot(path=str(rawp))
            outp = out_dir / f"{n:02d}_{slug}.png"
            annotate(rawp, box, n, headline, instruction, role, outp,
                     creds=creds, total=total)
            meta.append(dict(n=n, slug=slug, file=outp.name, headline=headline,
                             instruction=instruction, role=role, note=note,
                             found=bool(box), creds=list(creds) if creds else None))
            print(f"  {n:02d} {slug:34s} {'marked' if box else 'no-marker'}")
            return loc

        for st in steps:
            if st.get("login"):
                # Switching user needs a fresh browser context (own cookies);
                # logging out bounces to the database selector.
                u, p = st["login"]
                who = st.get("role", "")
                ctx2 = b.new_context(viewport={"width": 1440, "height": 900})
                page = ctx2.new_page()
                page.goto(f"{BASE}/web/login?db={DB}", wait_until="domcontentloaded")
                time.sleep(2.2)

                capture("login_screen",
                        st.get("login_headline", "Open the system and log in"),
                        st.get("login_instruction",
                               "This is the login page. Type your email and password."),
                        who, ["input[name='login']"], creds=(u, p), scroll=False)

                try:
                    page.fill("input[name='login']", u)
                    page.fill("input[name='password']", p)
                except Exception as e:
                    print("  login fill warn:", str(e)[:60])
                time.sleep(1.0)

                capture("login_click",
                        "Click Log in",
                        f"Signed in as {u}. Click the Log in button.",
                        who, ["button[type='submit']"], creds=(u, p), scroll=False)

                try:
                    page.click("button[type='submit']")
                    page.wait_for_url(lambda x: "/web/login" not in x, timeout=30000)
                except Exception:
                    pass
                time.sleep(3)

            if st.get("goto"):
                try:
                    page.goto(BASE + st["goto"], wait_until="domcontentloaded", timeout=30000)
                except Exception as e:
                    print(f"  goto warn: {e}")
            time.sleep(st.get("wait", 2.8))

            loc = capture(st["slug"], st["headline"], st["instruction"],
                          st.get("role", ""), st.get("target"), note=st.get("note", ""))

            # perform the click / typing that moves the flow on
            if loc and st.get("click", True):
                try:
                    loc.click(timeout=6000)
                    time.sleep(st.get("after", 2.2))
                except Exception as e:
                    print(f"  click warn: {str(e)[:70]}")
            for act in st.get("then", []):
                try:
                    act(page)
                    time.sleep(1.2)
                except Exception as e:
                    print(f"  then warn: {str(e)[:70]}")

        b.close()

    (out_dir / "steps.json").write_text(json.dumps(meta, indent=2))
    print(f"  -> {len(meta)} steps written to {out_dir}")
    return meta
