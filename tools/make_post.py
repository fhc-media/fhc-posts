#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generateur de visuels Finance Halal Canada (1080x1920, gabarit cercle marine/or).

Usage:  python3 tools/make_post.py specs/<nom>.json [dossier_sortie]
Sortie: <dossier_sortie>/<slug>.jpg   (par defaut: posts/)

Prerequis: wkhtmltoimage, Pillow, police Poppins installee.
Format de la spec: voir README.md.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

CSS = """
@page { margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  width: 1080px; height: 1920px;
  font-family: 'Poppins', sans-serif;
  background:
    radial-gradient(circle at 15% 8%, rgba(180,205,235,0.55), rgba(180,205,235,0) 35%),
    radial-gradient(circle at 88% 92%, rgba(190,210,235,0.55), rgba(190,210,235,0) 35%),
    linear-gradient(160deg, #dfeafc 0%, #eef5fc 35%, #f8fbfe 65%, #ffffff 100%);
  position: relative; overflow: hidden;
}
.gold-ring {
  width: 1000px; height: 1000px; border-radius: 50%;
  background: linear-gradient(135deg, #f3e0ab 0%, #cda75f 45%, #9c7935 100%);
  position: absolute; left: 50%; top: 288px; transform: translateX(-50%);
  box-shadow: 0 30px 70px rgba(20,25,45,0.28);
}
.navy-circle {
  width: 976px; height: 976px; border-radius: 50%;
  background: radial-gradient(circle at 30% 16%, #2a4070 0%, #16223f 55%, #0e1830 100%);
  position: absolute; left: 50%; top: 300px; transform: translateX(-50%);
  display: flex; flex-direction: column; align-items: center;
  padding: 74px 92px 56px 92px; overflow: hidden;
}
.title {
  color: #d9b874; font-weight: 800; font-size: 50px; line-height: 1.18;
  text-align: center; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 26px;
}
.intro { color: #f3f2ee; font-weight: 400; font-size: 26px; line-height: 1.4; text-align: center; margin-bottom: 20px; }
.intro b { font-weight: 700; color: #ffffff; }
.dots { color: #cda75f; font-size: 22px; letter-spacing: 3px; margin-bottom: 22px; }
.tagline {
  color: #d9b874; font-weight: 700; font-size: 29px; text-align: center; text-transform: uppercase;
  letter-spacing: 0.3px; line-height: 1.3; margin-top: auto; margin-bottom: 26px; padding: 0 20px;
}
.gold-line { width: 340px; height: 2px; background: linear-gradient(90deg, transparent, #cda75f, transparent); margin-bottom: 22px; }
.logo-row { display: flex; align-items: center; gap: 18px; }
.logo-badge {
  width: 76px; height: 76px; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #f3e0ab, #cda75f 60%, #9c7935 100%);
  display: flex; align-items: center; justify-content: center;
  color: #16223f; font-weight: 800; font-size: 26px; letter-spacing: 0.5px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}
.logo-text { line-height: 1.02; }
.logo-text .l1 { color: #fff; font-weight: 700; font-size: 30px; letter-spacing: 1px; }
.logo-text .l2 { color: #fff; font-weight: 800; font-size: 30px; letter-spacing: 1px; }
.logo-text .l3 { color: #d9b874; font-weight: 800; font-size: 30px; letter-spacing: 1px; }

.corner-accent { position: absolute; left: 108px; top: 268px; width: 90px; height: 90px; z-index: 5; }
.corner-accent .d { position: absolute; width: 34px; height: 34px; background: linear-gradient(135deg,#f3e0ab,#b8934a); transform: rotate(45deg); border-radius: 4px; box-shadow: 0 6px 14px rgba(20,25,45,0.25); }
.corner-accent .d1 { left: 0; top: 30px; }
.corner-accent .d2 { left: 28px; top: 2px; width: 26px; height: 26px; opacity: 0.85; }
.corner-accent .d3 { left: 28px; top: 58px; width: 22px; height: 22px; opacity: 0.7; }

.pendant { position: absolute; left: 50%; top: 1294px; transform: translateX(-50%); text-align: center; }
.pendant .diamond { width: 30px; height: 30px; background: linear-gradient(135deg,#f3e0ab,#9c7935); margin: 0 auto; transform: rotate(45deg); border-radius: 4px; box-shadow: 0 6px 16px rgba(20,25,45,0.2); }
.pendant .tri { width: 0; height: 0; margin: 10px auto 0 auto; border-left: 26px solid transparent; border-right: 26px solid transparent; border-top: 34px solid #cda75f; }

.footer-src { position: absolute; left: 0; right: 0; top: 1462px; text-align: center; color: #1b2a4a; font-size: 26px; line-height: 1.55; }
.footer-src b { font-weight: 700; }

/* blocs */
.callout { width: 100%; border: 2px solid #cda75f; border-radius: 18px; padding: 22px 20px; margin-bottom: 20px; background: rgba(201,163,92,0.08); }
.co-line { color: #fff; font-size: 25px; font-weight: 600; text-align: center; line-height: 1.4; }
.co-result { color: #d9b874; font-size: 30px; font-weight: 800; text-align: center; margin-top: 14px; }
.stat-row { display: flex; width: 100%; margin-bottom: 20px; }
.stat-card { flex: 1; border: 1px solid rgba(201,163,92,0.55); border-radius: 14px; padding: 16px 10px; text-align: center; margin: 0 8px; }
.stat-card .k { color: #cda75f; font-size: 19px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 6px; }
.stat-card .v { color: #fff; font-size: 26px; font-weight: 800; }
.note { color: #f3f2ee; font-size: 23px; text-align: center; line-height: 1.5; margin-bottom: 6px; }
.note-box { width: 100%; border-radius: 14px; background: rgba(201,163,92,0.1); border: 1px solid rgba(201,163,92,0.4); padding: 14px 18px; text-align: center; color: #f0efe9; font-size: 19px; line-height: 1.4; margin: 14px 0 4px 0; }
.li { display: flex; align-items: flex-start; width: 100%; margin-bottom: 20px; text-align: left; }
.li-num { flex-shrink: 0; width: 44px; height: 44px; border-radius: 50%; margin-right: 18px; background: linear-gradient(135deg,#f3e0ab,#9c7935); display: flex; align-items: center; justify-content: center; color: #16223f; font-weight: 800; font-size: 22px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
.li-title { color: #d9b874; font-weight: 700; font-size: 25px; margin-bottom: 4px; letter-spacing: 0.3px; }
.li-text { color: #f0efe9; font-weight: 400; font-size: 22px; line-height: 1.36; }
.li-text b { color: #fff; font-weight: 700; }
.li-only { padding-top: 6px; }
.cmp { display: flex; width: 100%; margin-bottom: 14px; }
.cmp-col { flex: 1; padding: 0 20px; }
.cmp-col.left { border-right: 1px solid rgba(201,163,92,0.45); }
.cmp-badge { border: 1.5px solid #cda75f; border-radius: 30px; padding: 7px 10px; text-align: center; color: #f3e0ab; font-weight: 700; font-size: 18px; text-transform: uppercase; margin-bottom: 14px; letter-spacing: 0.3px; }
.cmp-line { color: #e6e4dc; font-size: 19px; text-align: center; line-height: 1.42; margin-bottom: 8px; }
.cmp-verdict { color: #d9b874; font-weight: 800; font-size: 20px; text-align: center; margin-top: 6px; padding-top: 10px; border-top: 1px solid rgba(201,163,92,0.35); }
"""

LOGO = """<div class="logo-row"><div class="logo-badge">FHC</div>
<div class="logo-text"><div class="l1">FINANCE</div><div class="l2">HALAL</div><div class="l3">CANADA</div></div></div>"""


def block_html(b):
    t = b["type"]
    if t == "intro":
        return f'<div class="intro">{b["text"]}</div>'
    if t == "dots":
        return '<div class="dots">&bull;&bull;&bull;</div>'
    if t == "callout":
        lines = "".join(f'<div class="co-line">{x}</div>' for x in b.get("lines", []))
        res = f'<div class="co-result">{b["result"]}</div>' if b.get("result") else ""
        return f'<div class="callout">{lines}{res}</div>'
    if t == "stats":
        cards = "".join(
            f'<div class="stat-card"><div class="k">{i["label"]}</div><div class="v">{i["value"]}</div></div>'
            for i in b["items"]
        )
        return f'<div class="stat-row">{cards}</div>'
    if t == "note":
        return f'<div class="note">{b["text"]}</div>'
    if t == "notebox":
        return f'<div class="note-box">{b["text"]}</div>'
    if t == "list":
        rows = []
        for n, it in enumerate(b["items"], 1):
            if it.get("title"):
                body = f'<div><div class="li-title">{it["title"]}</div><div class="li-text">{it.get("text", "")}</div></div>'
            else:
                body = f'<div class="li-text li-only">{it["text"]}</div>'
            rows.append(f'<div class="li"><div class="li-num">{n}</div>{body}</div>')
        return "".join(rows)
    if t == "compare":
        def col(c, cls):
            lines = "".join(f'<div class="cmp-line">{x}</div>' for x in c.get("lines", []))
            verdict = f'<div class="cmp-verdict">{c["verdict"]}</div>' if c.get("verdict") else ""
            return f'<div class="cmp-col {cls}"><div class="cmp-badge">{c["badge"]}</div>{lines}{verdict}</div>'
        return f'<div class="cmp">{col(b["left"], "left")}{col(b["right"], "")}</div>'
    raise ValueError(f"type de bloc inconnu: {t}")


def build_html(spec):
    title = spec["title"].replace("\n", "<br>")
    blocks = "".join(block_html(b) for b in spec.get("blocks", []))
    tagline = f'<div class="tagline">{spec["tagline"].replace(chr(10), "<br>")}</div>' if spec.get("tagline") else ""
    footer = spec.get("footer", "Source: <b>@financehalalcanada</b><br>TikTok: <b>@financehalalcanada</b>")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="gold-ring"></div>
<div class="corner-accent"><div class="d d1"></div><div class="d d2"></div><div class="d d3"></div></div>
<div class="navy-circle"><div class="title">{title}</div>{blocks}{tagline}<div class="gold-line"></div>{LOGO}</div>
<div class="pendant"><div class="diamond"></div><div class="tri"></div></div>
<div class="footer-src">{footer}</div>
</body></html>"""


def render(spec_path, out_dir="posts"):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    slug = spec.get("slug") or Path(spec_path).stem
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        html_path = Path(td) / "post.html"
        png_path = Path(td) / "post.png"
        html_path.write_text(build_html(spec), encoding="utf-8")
        subprocess.run(
            ["wkhtmltoimage", "--quiet", "--width", "1080", "--height", "1920", "--format", "png",
             str(html_path), str(png_path)],
            check=True,
        )
        im = Image.open(png_path).convert("RGB")
        if im.size[1] > 1920:
            im = im.crop((0, 0, 1080, 1920))
        target = out / f"{slug}.jpg"
        im.save(target, "JPEG", quality=92, subsampling=0, optimize=True)
    return target


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "posts")
    print(path, path.stat().st_size, "octets")
