#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generateur de carrousels Finance Halal Canada (1080x1080, une image par diapositive).

Usage:  python3 tools/make_carousel.py specs/<nom>.json [dossier_sortie]
Sortie: <dossier_sortie>/<slug>-1.jpg ... <slug>-N.jpg  (1080x1080, max TikTok)

Reutilise le style de make_post.py (polices, icones Twemoji, decors, logo).
Types de diapositives: cover, cards, chips, flow, closing (voir specs/impot-strategie.json).
"""
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_post as MP
import scenes as SC

COL = {"gold": "#d99a1d", "green": "#1f8a64", "blue": "#2563c4", "purple": "#6a45c0", "teal": "#17877f", "red": "#d94c4c"}

EXTRA = """
body{background:linear-gradient(#eaf6f2,#dcefe7)}
.page{position:absolute;inset:0;display:flex;flex-direction:column}
.top{position:relative;flex:none;overflow:hidden;background:#0d1f44}
.top .hbg{position:absolute;inset:0;width:100%;height:100%}
.kick{position:absolute;left:44px;top:42px;z-index:3;font-family:'Kalam',cursive;font-weight:700;font-size:34px;color:#f6df4b;text-shadow:0 2px 8px rgba(0,0,0,.5)}
.count{position:absolute;right:40px;top:36px;z-index:3;background:#f6df4b;color:#12244a;font-weight:800;font-size:26px;padding:4px 18px;border-radius:30px;box-shadow:0 3px 8px rgba(0,0,0,.3)}
.main{flex:1;min-height:0;display:flex;flex-direction:column;justify-content:center;gap:28px;padding:34px 54px}
.card{flex:1;min-height:0;background:#f8fcfb;color:#12244a;border:4px solid var(--c);border-radius:30px;padding:24px 34px;display:flex;align-items:center;gap:28px;box-shadow:0 6px 16px rgba(10,30,60,.12);overflow:hidden}
.card.solo{flex:none}
.num{position:static;flex:none;width:96px;height:96px;border-radius:50%;background:var(--c);color:#fff;font-weight:800;font-size:52px;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 10px rgba(0,0,0,.25)}
.ct{flex:1;font-weight:600;font-size:43px;line-height:1.26}
.card.solo .ct{font-size:37px}
.ct b{font-weight:800;background:linear-gradient(transparent 62%,rgba(246,223,75,.85) 62%)}
.cic{flex:none;width:110px;height:110px}
.cover-top{height:440px}
.brushc{position:absolute;left:44px;right:44px;top:34px;z-index:2;background:rgba(8,18,44,.9);padding:26px 40px 30px;border-radius:6px 36px 6px 36px}
.ctitle{font-weight:800;font-size:56px;line-height:1.16;color:#fff}
.ctitle mark{background:#f6df4b;color:#12244a;padding:0 14px;border-radius:8px;display:inline-block;transform:rotate(-2deg);margin:2px 0}
.big-hl{align-self:flex-start;background:#f6df4b;color:#12244a;font-family:'Kalam',cursive;font-weight:700;font-size:58px;line-height:1.2;padding:12px 30px;border-radius:16px;transform:rotate(-1.5deg);box-shadow:0 5px 14px rgba(0,0,0,.25)}
.pill{align-self:flex-start;background:#12244a;color:#fff;font-weight:700;font-size:36px;padding:16px 36px;border-radius:50px}
.intro{font-weight:700;font-size:40px;line-height:1.25;color:#12244a}
.chips{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.chip{background:var(--c);color:#fff;border-radius:22px;padding:18px 22px;display:flex;align-items:center;gap:16px;font-weight:800;font-size:38px}
.chip img{width:56px;height:56px}
.chip small{display:block;font-weight:500;font-size:22px;line-height:1.2;opacity:.95}
.flow{display:flex;align-items:center;justify-content:space-between;gap:6px}
.fb{flex:1;background:#12244a;border-radius:26px;padding:34px 6px 26px;text-align:center;color:#fff;font-weight:700;font-size:27px;line-height:1.2}
.fb img{width:112px;height:112px;display:block;margin:0 auto 14px}
.plus{font-weight:800;font-size:48px;color:#12244a}
.dark{background:#12244a;color:#fff;border:3px solid rgba(246,223,75,.6);border-radius:30px;padding:26px 36px}
.dark .h{font-weight:800;font-size:46px;line-height:1.2}
.light{background:#f8fcfb;color:#12244a;border:4px solid #36a27a;border-radius:30px;padding:26px 34px;font-weight:600;font-size:32px;line-height:1.32}
.light b{font-weight:800}
.cta2{background:#f6df4b;color:#12244a;border-radius:20px;padding:14px 26px;font-family:'Kalam',cursive;font-weight:700;font-size:32px;line-height:1.2;text-align:center;transform:rotate(-1deg);box-shadow:0 4px 12px rgba(0,0,0,.25)}
.disc{font-size:20px;line-height:1.3;text-align:center;color:#3a4a66;font-weight:500}
.foot{flex:none}
.etfh{display:flex;align-items:center;gap:22px}
.tick{background:#12244a;color:#f6df4b;font-weight:800;font-size:60px;padding:6px 30px;border-radius:20px;letter-spacing:1px}
.etfn{font-weight:700;font-size:30px;line-height:1.2;color:#12244a}
.etfn small{display:block;font-weight:500;font-size:23px;opacity:.85;margin-top:4px}
.chart{position:relative;flex:1;min-height:0;background:#f8fcfb;border:4px solid #36a27a;border-radius:30px;padding:0}
.zero{position:absolute;left:28px;right:28px;height:3px;background:#12244a;opacity:.55}
.grp{position:absolute;bottom:0;top:0;width:150px}
.bar{position:absolute;width:56px;border-radius:8px}
.bv{position:absolute;width:100px;text-align:center;font-weight:800;font-size:25px;color:#12244a;line-height:1}
.bv.s{font-weight:700;font-size:20px;color:#5a6b86;width:80px}
.yl{position:absolute;bottom:12px;width:150px;text-align:center;font-weight:700;font-size:26px;color:#12244a}
.leg{display:flex;gap:30px;font-weight:600;font-size:24px;color:#12244a;align-items:center}
.leg i{display:inline-block;width:26px;height:26px;border-radius:6px;margin-right:10px;vertical-align:middle}
.note{font-size:20px;line-height:1.3;color:#3a4a66;font-weight:500}

.hook{position:absolute;left:-50px;right:-50px;top:392px;z-index:5;transform:rotate(-6deg);background:linear-gradient(180deg,#ff4d6d,#e0263f);color:#fff;font-family:'Kalam',cursive;font-weight:700;font-size:52px;line-height:1.1;text-align:center;padding:16px 90px 20px;box-shadow:0 8px 20px rgba(0,0,0,.35);outline:4px dashed rgba(255,255,255,.75);outline-offset:-12px}
.cover-main{padding-top:215px;gap:24px}
.cover-main .big-hl{font-size:46px;padding:10px 26px}
"""


def build_css(top_h):
    css = MP.CSS
    for k, v in dict(f=MP.FONTS, y=MP.YELLOW, g=MP.GOLD, tsize=40, psize=23, xsize=19, isize=64, capsize=17, hlsize=19,
                     bh=196, hh=338, fh=150, ctsize=19, cisize=76, cbsize=15.5).items():
        css = css.replace(f"%({k})s", str(v))
    css = css.replace("%%", "%")
    return css + EXTRA


def img(ch, cls=""):
    return f'<img class="{cls}" src="{MP.icon_uri(ch)}">'


def frame(inner, n, total, kicker, top_h=150, top_extra=""):
    count = f'<div class="count">{n}/{total}</div>' if n else ""
    kick = f'<div class="kick">{kicker}</div>' if kicker else ""
    return f"""<div class="page"><div class="top" style="height:{top_h}px">{SC.header_bg()}{kick}{count}{top_extra}</div>
<div class="main">{inner}</div>
<div class="foot" style="height:150px;position:relative;overflow:hidden;background:#0b3b6a">{SC.footer_bg()}<div class="glow"></div>
 <div class="in"><div class="logo"><div class="fhc">FHC{MP.LEAF}</div><div class="sep"></div><div class="ln">FINANCE<br><span class="g">HALAL</span><br>CANADA</div></div></div>
 <div class="tag">ÉPARGNER · INVESTIR · BÂTIR · UN AVENIR HALAL</div></div></div>"""


def etf_chart(years, vals, bench, ymin=-30, ymax=45, H=330, W=972):
    """Barres groupees : FNB (couleur) + S&P 500 (gris). Echelle commune pour comparer les diapos."""
    top, bot = 56, 64            # marges haute / basse du graphique (px)
    plot = H - top - bot
    def y(v): return top + (ymax - v) / (ymax - ymin) * plot
    z = y(0)
    n = len(years)
    gw = (W - 56) / n
    out = [f'<div class="zero" style="top:{z:.1f}px"></div>']
    for i, yr in enumerate(years):
        gx = 28 + i * gw + (gw - 150) / 2
        v, b = vals[i], bench[i]
        def one(val, x, cls, color):
            if val is None:
                return f'<div class="bv {cls}" style="left:{x - 20 + 28:.1f}px;top:{z - 28:.1f}px;opacity:.6">n.d.</div>'
            h = max(abs(val) / (ymax - ymin) * plot, 3)
            ty = z - h if val >= 0 else z
            ly = ty - 28 if val >= 0 else ty + h + 4
            txt = f"{val:+.1f}".replace(".", ",") + " %".replace(" ", "") if False else (f"{val:+.1f}".replace(".", ",") + "%")
            return (f'<div class="bar" style="left:{x:.1f}px;top:{ty:.1f}px;height:{h:.1f}px;width:{56 if cls == "" else 40}px;background:{color}"></div>'
                    f'<div class="bv {cls}" style="left:{x - 22 if cls == "" else x - 20:.1f}px;top:{ly:.1f}px">{txt}</div>')
        red = "#d94c4c"
        out.append(one(v, gx + 6, "", "#1f8a64" if (v or 0) >= 0 else red))
        out.append(one(b, gx + 74, "s", "#9fb0c8"))
        out.append(f'<div class="yl" style="left:{gx - 0:.1f}px">{yr}</div>')
    return "".join(out)


def slide_html(s, n, total, kicker):
    t = s["type"]
    if t == "cover":
        title = s["title"].replace("\n", "<br>")
        top_extra = f'<div class="brushc"><div class="ctitle">{title}</div></div>'
        inner = f'<div class="big-hl">{s["hook"]}</div><div class="pill">{s["swipe"]}</div>'
        h = frame(inner, 0, total, "", top_h=440, top_extra=top_extra).replace('class="top"', 'class="top cover-top"')
        if s.get("banner"):
            h = h.replace('<div class="main">', '<div class="main cover-main">').replace('<div class="foot"', f'<div class="hook">{s["banner"]}</div><div class="foot"', 1)
        return h
    if t == "cards":
        cards = "".join(
            f'<div class="card" style="--c:{COL[c["color"]]}"><div class="num">{c["num"]}</div><div class="ct">{c["text"]}</div>{img(c["icon"], "cic")}</div>'
            for c in s["cards"])
        return frame(cards, n, total, kicker)
    if t == "chips":
        c = s["card"]
        chips = "".join(
            f'<div class="chip" style="--c:{COL[x["color"]]}">{img(x["icon"])}<div>{x["name"]}<small>{x["sub"]}</small></div></div>'
            for x in s["chips"])
        inner = (f'<div class="card solo" style="--c:{COL[c["color"]]}"><div class="num">{c["num"]}</div><div class="ct">{c["text"]}</div></div>'
                 f'<div class="chips">{chips}</div>')
        return frame(inner, n, total, kicker)
    if t == "flow":
        c = s["card"]
        boxes = '<div class="plus">+</div>'.join(f'<div class="fb">{img(b["icon"])}{b["label"]}</div>' for b in s["flow"])
        inner = (f'<div class="card solo" style="--c:{COL[c["color"]]}"><div class="num">{c["num"]}</div><div class="ct">{c["text"]}</div></div>'
                 f'<div class="flow">{boxes}</div><div class="big-hl" style="font-size:56px">{s["hl"]}</div>')
        return frame(inner, n, total, kicker)
    if t == "etf":
        ch = etf_chart(s["years"], s["vals"], s["bench"])
        inner = (f'<div class="etfh"><div class="tick">{s["ticker"]}</div><div class="etfn">{s["name"]}<small>{s["desc"]}</small></div></div>'
                 f'<div class="chart">{ch}</div>'
                 f'<div class="leg"><span><i style="background:#1f8a64"></i>{s["ticker"]}</span><span><i style="background:#9fb0c8"></i>S&P 500</span></div>'
                 f'<div class="note">{s["foot"]}</div>')
        return frame(inner, n, total, s.get("kicker", kicker))
    if t == "closing":
        inner = (f'<div class="dark"><div class="h">{s["h"]}</div></div><div class="big-hl">{s["hl"]}</div>'
                 f'<div class="light">{s["text"]}</div><div class="cta2">{s["cta"]}</div><div class="disc">{s["disc"]}</div>')
        return frame(inner, n, total, s.get("kicker", kicker))
    raise ValueError(t)


def render(spec_path, out_dir="posts"):
    from playwright.sync_api import sync_playwright
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    slug = spec["slug"]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    slides, total = spec["slides"], len(spec["slides"])
    css = build_css(150)
    outs = []
    with tempfile.TemporaryDirectory() as td, sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=1)
        for i, s in enumerate(slides, 1):
            html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{slide_html(s, i, total, spec.get("kicker", ""))}</body></html>'
            hp, pp = Path(td) / f"s{i}.html", Path(td) / f"s{i}.png"
            hp.write_text(html, encoding="utf-8")
            pg.goto(f"file://{hp}")
            pg.wait_for_timeout(300)
            over = pg.evaluate("""()=>[...document.querySelectorAll('.card,.main,.brushc,.dark,.light')].filter(e=>e.scrollHeight>e.clientHeight+2||e.scrollWidth>e.clientWidth+2).map(e=>e.className+': '+(e.innerText||'').slice(0,40))""")
            inner_over = pg.evaluate("""()=>{const m=document.querySelector('.main');const f=document.querySelector('.foot');const mb=[...m.children].reduce((a,e)=>Math.max(a,e.getBoundingClientRect().bottom),0);return mb>f.getBoundingClientRect().top+1}""")
            pg.screenshot(path=str(pp))
            if over or inner_over:
                print(f"ATTENTION diapo {i}: debordement", over, "(contenu sous le pied)" if inner_over else "")
            target = out / f"{slug}-{i}.jpg"
            Image.open(pp).convert("RGB").save(target, "JPEG", quality=92, subsampling=0, optimize=True)
            outs.append(target)
        b.close()
    return outs


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "posts"):
        print(p, p.stat().st_size, "octets")
