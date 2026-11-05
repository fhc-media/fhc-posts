#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generateur de visuels Finance Halal Canada - style illustre "cercle" (v2).

Usage:  python3 tools/make_post.py specs/<nom>.json [dossier_sortie]
Sortie: <dossier_sortie>/<slug>.jpg  (1350x1350, defaut: posts/)

Rendu par Chromium (Playwright). Polices: Poppins (systeme) + Kalam (tools/fonts).
Icones: emojis convertis en SVG Twemoji (tools/icons, copies depuis le paquet npm
@twemoji/svg si absentes). Format de la spec et regles de style: docs/STYLE.md.
"""
import base64
import json
import random
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
ICONS = HERE / "icons"
NPM_TWEMOJI = [Path("/tmp/claude-0/fonts/node_modules/@twemoji/svg"), Path("node_modules/@twemoji/svg")]

NAVY, NAVY2, YELLOW, GOLD = "#12244a", "#0c1a38", "#f6df4b", "#d9b24f"

CSS = """
@font-face{font-family:'Kalam';font-weight:400;src:url('file://%(f)s/kalam-latin-400-normal.woff2')}
@font-face{font-family:'Kalam';font-weight:700;src:url('file://%(f)s/kalam-latin-700-normal.woff2')}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1080px;overflow:hidden;font-family:'Poppins',sans-serif;color:#fff}
body{background:radial-gradient(circle at 20% 15%,#f3fbf8,#e3f3ec 60%,#dcefe7)}
.circle{position:absolute;left:20px;top:20px;width:1040px;height:1040px;border-radius:50%;
  border:8px solid #f6df4b;overflow:hidden;display:flex;flex-direction:column;background:#eaf6f2;
  box-shadow:0 10px 30px rgba(10,30,60,.18)}
/* en-tete */
.head{position:relative;height:338px;flex:none;background:linear-gradient(100deg,#0d1f44 0%%,#173568 48%%,#4a8fd0 100%%);overflow:hidden}
.head svg.sky{position:absolute;right:0;bottom:0}
.title{position:absolute;left:190px;top:104px;width:520px;font-weight:800;font-size:%(tsize)spx;line-height:1.2;letter-spacing:-.3px;z-index:3;text-shadow:0 2px 8px rgba(0,0,0,.35)}
.title mark{background:%(y)s;color:#12244a;padding:0 14px;border-radius:7px;display:inline-block;transform:rotate(-2deg);text-shadow:none;margin:3px 0}
.sub{position:absolute;left:176px;font-family:'Kalam',cursive;font-weight:700;font-size:25px;color:%(y)s;z-index:3;text-shadow:0 2px 6px rgba(0,0,0,.4)}
.mascot{position:absolute;right:104px;bottom:0;width:236px;height:260px;z-index:2}
.bubble{position:absolute;right:62px;top:38px;width:250px;text-align:center;font-family:'Kalam',cursive;font-weight:700;font-size:21px;line-height:1.25;color:#fff;z-index:3;text-shadow:0 2px 6px rgba(0,0,0,.45)}
.bubble:after{content:'';display:block;width:120px;height:5px;margin:6px auto 0;border-radius:4px;background:%(y)s;transform:rotate(-2deg)}
/* corps */
.body{flex:1;display:flex;flex-direction:column;gap:10px;padding:12px 62px 14px;background:linear-gradient(#eaf6f2,#dff0ea)}
.row{display:flex;gap:10px;min-height:0}
.p{flex:1;border-radius:18px;padding:12px 16px;display:flex;flex-direction:column;justify-content:center;gap:5px;overflow:hidden;position:relative;min-width:0}
.p.navy{background:linear-gradient(160deg,#17306000,#12244a);background:#12244a;border:2px solid rgba(246,223,75,.55)}
.p.light{background:#f8fcfb;color:#12244a;border:2px solid #36a27a}
.p.light.warn{border-color:#d94c4c}
.p.c-blue{background:linear-gradient(160deg,#2457b4,#16346e)}
.p.c-green{background:linear-gradient(160deg,#27a05a,#14633a)}
.p.c-orange{background:linear-gradient(160deg,#f0a63a,#c06a14)}
.p.c-purple{background:linear-gradient(160deg,#6a4cc0,#3b2780)}
.p.c-red{background:linear-gradient(160deg,#e0553f,#9c2a1f)}
.p.center{align-items:center;text-align:center}
.p.hrow{flex-direction:row;align-items:center;gap:14px}
.p .col{display:flex;flex-direction:column;gap:5px;min-width:0}
.t{font-weight:700;font-size:%(psize)spx;line-height:1.2}
.t.big{font-size:30px;font-weight:800}
.x{font-weight:500;font-size:%(xsize)spx;line-height:1.32;opacity:.96}
.x b{font-weight:800}
.p.navy .t em,.p.c-blue .t em{color:%(y)s;font-style:normal}
.light .t em{color:#1f8a4c;font-style:normal}
.note{font-family:'Kalam',cursive;font-weight:400;font-size:17px;line-height:1.25;opacity:.9}
.hl{align-self:flex-start;background:%(y)s;color:#12244a;font-family:'Kalam',cursive;font-weight:700;font-size:21px;line-height:1.2;padding:2px 12px;border-radius:7px;transform:rotate(-1.5deg)}
.center .hl{align-self:center}
.stat{font-weight:800;font-size:46px;line-height:1;color:%(y)s}
.light .stat{color:#12244a}
.num{position:absolute;left:10px;top:8px;width:42px;height:42px;border-radius:50%%;background:#fff;color:#12244a;font-weight:800;font-size:22px;display:flex;align-items:center;justify-content:center;box-shadow:0 3px 8px rgba(0,0,0,.3)}
.p.hasnum{padding-top:56px}
.ico{width:%(isize)spx;height:%(isize)spx;flex:none}
.ico.sm{width:44px;height:44px}
.ico.xl{width:86px;height:86px}
/* pied */
.foot{position:relative;height:176px;flex:none;background:linear-gradient(#0f2a55,#0b3b6a 70%%,#0a4a63);overflow:hidden}
.foot svg.skyl{position:absolute;left:0;bottom:0}
.foot .in{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:26px;padding:0 120px 40px;z-index:2}
.logo{display:flex;align-items:center;gap:14px}
.fhc{font-family:'Lora',serif;font-weight:700;font-size:62px;line-height:1;letter-spacing:-2px;color:#fff;position:relative}
.fhc:after{content:'';position:absolute;left:2px;right:2px;top:22px;height:5px;left:34px;right:36px;background:#e23b3b;transform:rotate(-16deg);border-radius:3px}
.leaf{width:24px;height:24px;position:absolute;left:84px;top:16px}
.sep{width:2px;height:62px;background:rgba(255,255,255,.7)}
.ln{font-weight:800;font-size:23px;line-height:1.02;letter-spacing:.5px}
.ln .g{color:%(g)s}
.tag{position:absolute;left:0;right:0;bottom:24px;text-align:center;font-weight:600;font-size:12.5px;letter-spacing:1px;color:%(g)s;z-index:2}
.cta{background:%(y)s;color:#12244a;font-family:'Kalam',cursive;font-weight:700;font-size:20px;line-height:1.2;padding:12px 18px;border-radius:14px;max-width:330px;transform:rotate(-2deg);box-shadow:0 4px 12px rgba(0,0,0,.3)}
"""

LEAF = ('<svg class="leaf" viewBox="0 0 24 24"><path fill="#d9b24f" d="M12 1l2.2 4.3 2.8-1-1 5.4 3.2-2.2.8 2.3 2.6-.3-1.3 4 1.6 1'
        '-5.6 3.3.4 1.6-4.6-.8.1 5.4h-1.2l.1-5.4-4.6.8.4-1.6-5.6-3.3 1.6-1-1.3-4 2.6.3.8-2.3 3.2 2.2-1-5.4 2.8 1z"/></svg>')


def icon_uri(ch):
    """Emoji -> data URI SVG (Twemoji)."""
    code = "-".join(f"{ord(c):x}" for c in ch if ord(c) != 0xFE0F)
    ICONS.mkdir(exist_ok=True)
    f = ICONS / f"{code}.svg"
    if not f.exists():
        for base in NPM_TWEMOJI:
            if (base / f"{code}.svg").exists():
                shutil.copy(base / f"{code}.svg", f)
                break
        else:
            raise FileNotFoundError(f"icone introuvable pour {ch!r} ({code}.svg)")
    return "data:image/svg+xml;base64," + base64.b64encode(f.read_bytes()).decode()


def skyline(w, h, seed, base="#10294f", win="#f6df4b", tower_x=None, dome_x=None, trees=False, alpha=1.0):
    rnd = random.Random(seed)
    parts, x = [], 0
    while x < w:
        bw = rnd.randint(28, 58)
        bh = rnd.randint(int(h * .25), int(h * .62))
        parts.append(f'<rect x="{x}" y="{h-bh}" width="{bw}" height="{bh}" fill="{base}"/>')
        for wy in range(h - bh + 8, h - 6, 14):
            for wx in range(x + 6, x + bw - 6, 11):
                if rnd.random() < .25:
                    parts.append(f'<rect x="{wx}" y="{wy}" width="4" height="6" fill="{win}" opacity=".7"/>')
        x += bw + rnd.randint(0, 6)
    if tower_x is not None:
        th = int(h * .97)
        parts.append(f'<rect x="{tower_x-4}" y="{h-th}" width="8" height="{th}" fill="{base}"/>')
        parts.append(f'<ellipse cx="{tower_x}" cy="{h-int(th*.66)}" rx="20" ry="8" fill="{base}"/>')
        parts.append(f'<rect x="{tower_x-1.5}" y="{h-th-26}" width="3" height="30" fill="{base}"/>')
    if dome_x is not None:
        parts.append(f'<rect x="{dome_x-30}" y="{h-80}" width="60" height="80" fill="{base}"/>')
        parts.append(f'<path d="M{dome_x-36} {h-80} A36 36 0 0 1 {dome_x+36} {h-80} Z" fill="{base}"/>')
        parts.append(f'<rect x="{dome_x+44}" y="{h-120}" width="9" height="120" fill="{base}"/>')
        parts.append(f'<path d="M{dome_x+42} {h-120} L{dome_x+48.5} {h-140} L{dome_x+55} {h-120} Z" fill="{base}"/>')
    if trees:
        for i in range(0, w, 34):
            th = rnd.randint(40, 80)
            parts.append(f'<path d="M{i} {h} L{i+17} {h-th} L{i+34} {h} Z" fill="#1d6b4a" opacity=".9"/>')
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" opacity="{alpha}">{"".join(parts)}</svg>'


def mascot(pose="think"):
    hand = ""
    if pose == "think":
        hand = ('<path d="M196 262 C232 250 262 270 268 330 L196 330 Z" fill="#1b2d57"/>'
                '<ellipse cx="178" cy="214" rx="28" ry="23" fill="#c98f66"/>'
                '<path d="M160 206 q6 -8 12 0 M172 202 q6 -8 12 0 M184 204 q6 -8 12 2" stroke="#a97048" stroke-width="3" fill="none"/>')
    smile = '<path d="M128 182 Q150 200 172 182" stroke="#f0cfb8" stroke-width="5" fill="none" stroke-linecap="round"/>'
    return f'''<svg class="mascot" viewBox="0 0 300 330">
<path d="M18 330 C20 262 70 238 150 238 C230 238 282 262 284 330 Z" fill="#1b2d57"/>
<path d="M92 246 C100 214 200 214 208 246 C190 262 110 262 92 246 Z" fill="#0f1c3d"/>
<rect x="136" y="196" width="28" height="40" fill="#b87f58"/>
<ellipse cx="88" cy="132" rx="10" ry="16" fill="#b87f58"/><ellipse cx="212" cy="132" rx="10" ry="16" fill="#b87f58"/>
<ellipse cx="150" cy="128" rx="62" ry="72" fill="#c98f66"/>
<path d="M86 120 C80 58 120 42 160 46 C206 50 224 86 214 122 C206 96 190 86 150 88 C120 90 98 98 86 120 Z" fill="#14141c"/>
<path d="M88 134 C90 204 118 220 150 220 C182 220 210 204 212 134 C206 164 190 176 150 176 C110 176 94 164 88 134 Z" fill="#17171f"/>
<ellipse cx="124" cy="126" rx="11" ry="9" fill="#fff"/><ellipse cx="176" cy="126" rx="11" ry="9" fill="#fff"/>
<circle cx="128" cy="124" r="5.5" fill="#2a1a10"/><circle cx="180" cy="124" r="5.5" fill="#2a1a10"/>
<path d="M108 108 Q124 98 140 106" stroke="#14141c" stroke-width="6" fill="none" stroke-linecap="round"/>
<path d="M162 104 Q178 96 194 106" stroke="#14141c" stroke-width="6" fill="none" stroke-linecap="round"/>
<path d="M150 130 q-6 18 4 22" stroke="#a97048" stroke-width="4" fill="none" stroke-linecap="round"/>
{smile}{hand}</svg>'''


def panel(p):
    cls = ["p", p.get("tone", "navy")]
    if p.get("color"):
        cls = ["p", "c-" + p["color"]]
    if p.get("warn"):
        cls.append("warn")
    if p.get("center"):
        cls.append("center")
    if p.get("num") is not None:
        cls.append("hasnum")
    side = bool(p.get("icon")) and p.get("iconpos") == "left"
    if side:
        cls.append("hrow")
    ico = ""
    if p.get("icon"):
        size = p.get("isize", "")
        ico = f'<img class="ico {size}" src="{icon_uri(p["icon"])}">'
    num = f'<div class="num">{p["num"]}</div>' if p.get("num") is not None else ""
    bits = []
    if p.get("title"):
        bits.append(f'<div class="t{" big" if p.get("big_title") else ""}">{p["title"]}</div>')
    if p.get("stat"):
        bits.append(f'<div class="stat">{p["stat"]}</div>')
    if p.get("text"):
        bits.append(f'<div class="x">{p["text"]}</div>')
    if p.get("note"):
        bits.append(f'<div class="note">{p["note"]}</div>')
    if p.get("hl"):
        bits.append(f'<div class="hl">{p["hl"]}</div>')
    inner = "".join(bits)
    style = f' style="flex:{p["w"]}"' if p.get("w") else ""
    if side:
        return f'<div class="{" ".join(cls)}"{style}>{num}{ico}<div class="col">{inner}</div></div>'
    return f'<div class="{" ".join(cls)}"{style}>{num}{ico if not p.get("icon_after") else ""}{inner}{ico if p.get("icon_after") else ""}</div>'


def build_html(spec):
    title = spec["title"].replace("\n", "<br>")
    sub = spec.get("subtitle", "")
    sub_html = f'<div class="sub" style="top:{spec.get("sub_top", 236)}px">{sub}</div>' if sub else ""
    bubble = f'<div class="bubble">{spec["bubble"]}</div>' if spec.get("bubble") else ""
    rows = []
    for r in spec["rows"]:
        h = r.get("h", 1)
        ins = f';margin:0 {r["inset"]}px' if r.get("inset") else ""
        rows.append(f'<div class="row" style="flex:{h} 1 0{ins}">{"".join(panel(p) for p in r["panels"])}</div>')
    cta = f'<div class="cta">{spec["cta"]}</div>' if spec.get("cta") else ""
    css = CSS
    for k, v in dict(f=FONTS, y=YELLOW, g=GOLD, tsize=spec.get("tsize", 50), psize=spec.get("psize", 23),
                     xsize=spec.get("xsize", 19), isize=spec.get("isize", 64)).items():
        css = css.replace(f"%({k})s", str(v))
    css = css.replace("%%", "%")
    sky = skyline(520, 170, 7, base="#1c4585", tower_x=180, dome_x=380, trees=True)
    foot_sky = skyline(1024, 120, 3, base="#143a6e", tower_x=130, dome_x=900, trees=True, alpha=.8)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
<div class="circle">
 <div class="head"><svg class="sky" style="display:none"></svg>{sky.replace('<svg ', '<svg class="sky" ', 1)}
  <div class="title">{title}</div>{sub_html}{bubble}{mascot(spec.get("pose", "think"))}</div>
 <div class="body">{"".join(rows)}</div>
 <div class="foot">{foot_sky.replace('<svg ', '<svg class="skyl" ', 1)}
  <div class="in"><div class="logo"><div class="fhc">FHC{LEAF}</div><div class="sep"></div>
  <div class="ln">FINANCE<br><span class="g">HALAL</span><br>CANADA</div></div>{cta}</div>
  <div class="tag">ÉPARGNER · INVESTIR · BÂTIR · UN AVENIR HALAL</div></div>
</div></body></html>"""


def render(spec_path, out_dir="posts"):
    from playwright.sync_api import sync_playwright
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    slug = spec.get("slug") or Path(spec_path).stem
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        html_path, png_path = Path(td) / "post.html", Path(td) / "post.png"
        html_path.write_text(build_html(spec), encoding="utf-8")
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=1.25)
            pg.goto(f"file://{html_path}")
            pg.wait_for_timeout(300)
            # controle de debordement: un panneau dont le contenu depasse est signale
            over = pg.evaluate("""()=>[...document.querySelectorAll('.p')].filter(e=>e.scrollHeight>e.clientHeight+2||e.scrollWidth>e.clientWidth+2).map(e=>(e.innerText||'').slice(0,40))""")
            pg.screenshot(path=str(png_path))
            b.close()
        if over:
            print("ATTENTION debordement dans:", over)
        target = out / f"{slug}.jpg"
        Image.open(png_path).convert("RGB").save(target, "JPEG", quality=90, subsampling=0, optimize=True)
    return target


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "posts")
    print(path, path.stat().st_size, "octets")
