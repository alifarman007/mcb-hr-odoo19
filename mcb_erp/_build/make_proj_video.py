"""Render the 10 Project module click-path flows as MP4s.

Static frames only — no zoom/pan, so the picture never shakes.
"""
import sys
from pathlib import Path

sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_erp/_build")

import make_flow_video as V   # noqa: E402
from proj_meta import META, END, SHORT  # noqa: E402

V.FLOW_META.update(META)
V.END_TEXT.update(END)
V.OUTDIR = Path("/Data/odoo19_enterprise/mukticox/video_project")
V.BRAND = "MCB PROJECT"


def build(flow):
    out = V.build(flow)
    if out:
        no = META[flow][0]
        nice = out.with_name(f"R{no:02d}_MCB_Project_{SHORT[flow]}.mp4")
        out.rename(nice)
        print(f"    -> {nice.name}")
    return out


if __name__ == "__main__":
    wanted = sys.argv[1:] or [k for k, *_ in
                              sorted(META.items(), key=lambda kv: kv[1][0])]
    print("Rendering Project flow videos (static frames — no shake):")
    for f in wanted:
        build(f)
