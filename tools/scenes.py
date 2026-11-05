# -*- coding: utf-8 -*-
"""Scenes illustrees vectorielles (SVG) pour les panneaux FHC. Chaque scene: viewBox 400x300."""
import random

OUT = "#0a1126"


def _svg(inner, vb="0 0 400 300"):
    return f'<svg class="scene" viewBox="{vb}" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">{inner}</svg>'


def _lin(i, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def _rad(i, c, a0=1, a1=0):
    return (f'<radialGradient id="{i}"><stop offset="0" stop-color="{c}" stop-opacity="{a0}"/>'
            f'<stop offset="1" stop-color="{c}" stop-opacity="{a1}"/></radialGradient>')


# ---------- personnages ----------
def man(pose="think", u="m"):
    """Buste de la mascotte (boite 300x330), contours + ombrages."""
    hand = ""
    if pose == "think":
        hand = (f'<path d="M190 268 C232 252 266 276 272 330 L190 330 Z" fill="url(#{u}h)" stroke="{OUT}" stroke-width="3"/>'
                f'<ellipse cx="176" cy="214" rx="29" ry="24" fill="url(#{u}f)" stroke="{OUT}" stroke-width="3"/>'
                '<path d="M158 208 q6 -9 13 0 M171 203 q6 -9 13 0 M184 205 q6 -9 13 2" stroke="#a46b45" stroke-width="3" fill="none"/>')
    if pose == "smile":
        mouth = ('<path d="M124 180 Q150 206 176 180 Q150 190 124 180 Z" fill="#fff" stroke="#3a1c14" stroke-width="2.5"/>')
    else:
        mouth = '<path d="M128 182 Q150 198 172 182" stroke="#f0cfb8" stroke-width="5" fill="none" stroke-linecap="round"/>'
    return f'''<defs>
<radialGradient id="{u}f" cx=".38" cy=".3" r=".85"><stop offset="0" stop-color="#e8b184"/><stop offset=".65" stop-color="#c98f66"/><stop offset="1" stop-color="#9c6540"/></radialGradient>
<linearGradient id="{u}h" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#34507f"/><stop offset=".6" stop-color="#1b2d57"/><stop offset="1" stop-color="#0e1a3a"/></linearGradient>
</defs>
<path d="M14 330 C18 258 70 234 150 234 C230 234 284 258 288 330 Z" fill="url(#{u}h)" stroke="{OUT}" stroke-width="3.5"/>
<path d="M60 300 C70 270 90 258 110 252 M240 300 C232 272 214 258 196 252" stroke="rgba(150,190,255,.35)" stroke-width="4" fill="none" stroke-linecap="round"/>
<path d="M88 244 C98 212 202 212 212 244 C192 264 108 264 88 244 Z" fill="#0e1a3a" stroke="{OUT}" stroke-width="3"/>
<path d="M132 258 L130 300 M168 258 L170 300" stroke="#e9edf7" stroke-width="3.5" stroke-linecap="round"/>
<rect x="134" y="192" width="32" height="46" rx="8" fill="#a97048" stroke="{OUT}" stroke-width="3"/>
<ellipse cx="88" cy="134" rx="10" ry="17" fill="#b9805a" stroke="{OUT}" stroke-width="3"/><ellipse cx="212" cy="134" rx="10" ry="17" fill="#b9805a" stroke="{OUT}" stroke-width="3"/>
<ellipse cx="150" cy="130" rx="63" ry="73" fill="url(#{u}f)" stroke="{OUT}" stroke-width="3.5"/>
<path d="M85 122 C78 56 122 40 162 44 C208 48 226 86 216 124 C208 98 192 86 150 88 C120 90 98 98 85 122 Z" fill="#15151d" stroke="{OUT}" stroke-width="3"/>
<path d="M104 62 C122 50 150 50 170 56" stroke="rgba(255,255,255,.28)" stroke-width="4" fill="none" stroke-linecap="round"/>
<path d="M87 134 C89 206 118 224 150 224 C182 224 211 206 213 134 C207 166 190 178 150 178 C110 178 93 166 87 134 Z" fill="#17171f" stroke="{OUT}" stroke-width="3"/>
<path d="M104 190 q10 12 22 14 M196 190 q-10 12 -22 14" stroke="rgba(255,255,255,.14)" stroke-width="3" fill="none" stroke-linecap="round"/>
<ellipse cx="108" cy="156" rx="13" ry="8" fill="rgba(224,110,90,.28)"/><ellipse cx="192" cy="156" rx="13" ry="8" fill="rgba(224,110,90,.28)"/>
<ellipse cx="124" cy="126" rx="12" ry="9.5" fill="#fff" stroke="{OUT}" stroke-width="2"/><ellipse cx="176" cy="126" rx="12" ry="9.5" fill="#fff" stroke="{OUT}" stroke-width="2"/>
<circle cx="128" cy="124" r="6" fill="#3a2214"/><circle cx="180" cy="124" r="6" fill="#3a2214"/>
<circle cx="130" cy="122" r="2" fill="#fff"/><circle cx="182" cy="122" r="2" fill="#fff"/>
<path d="M106 108 Q124 97 142 106" stroke="#14141c" stroke-width="6.5" fill="none" stroke-linecap="round"/>
<path d="M160 104 Q178 95 196 106" stroke="#14141c" stroke-width="6.5" fill="none" stroke-linecap="round"/>
<path d="M150 130 q-7 18 5 23" stroke="#955f3b" stroke-width="4" fill="none" stroke-linecap="round"/>
{mouth}{hand}'''


def man_back(u="b"):
    return f'''<defs><linearGradient id="{u}h" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2c4672"/><stop offset="1" stop-color="#0e1a3a"/></linearGradient></defs>
<path d="M30 330 C34 262 84 240 150 240 C216 240 266 262 270 330 Z" fill="url(#{u}h)" stroke="{OUT}" stroke-width="3.5"/>
<path d="M92 330 L100 252 M208 330 L200 252" stroke="#222" stroke-width="16" stroke-linecap="round"/>
<rect x="104" y="262" width="92" height="68" rx="16" fill="#1e2433" stroke="{OUT}" stroke-width="3"/>
<rect x="136" y="200" width="28" height="44" rx="8" fill="#a97048" stroke="{OUT}" stroke-width="3"/>
<ellipse cx="150" cy="146" rx="58" ry="66" fill="#15151d" stroke="{OUT}" stroke-width="3.5"/>
<ellipse cx="94" cy="156" rx="9" ry="15" fill="#b9805a" stroke="{OUT}" stroke-width="3"/><ellipse cx="206" cy="156" rx="9" ry="15" fill="#b9805a" stroke="{OUT}" stroke-width="3"/>
<path d="M104 96 C124 84 176 84 196 96" stroke="rgba(255,255,255,.22)" stroke-width="4" fill="none" stroke-linecap="round"/>'''


def kid(x, y, s, col, hair="#1a1410"):
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M-26 90 C-26 52 -14 40 0 40 C14 40 26 52 26 90 Z" fill="{col}" stroke="{OUT}" stroke-width="3"/>'
            f'<circle cx="0" cy="18" r="20" fill="{hair}" stroke="{OUT}" stroke-width="3"/></g>')


def man_g(x, y, s, pose="think", u="m"):
    return f'<g transform="translate({x},{y}) scale({s})">{man(pose, u)}</g>'


def back_g(x, y, s, u="b"):
    return f'<g transform="translate({x},{y}) scale({s})">{man_back(u)}</g>'


# ---------- elements de decor ----------
def buildings(y, col, seed, win="#ffd36a", x0=0, x1=400, hmin=40, hmax=120):
    r = random.Random(seed)
    out, x = [], x0
    while x < x1:
        bw, bh = r.randint(20, 40), r.randint(hmin, hmax)
        out.append(f'<rect x="{x}" y="{y-bh}" width="{bw}" height="{bh}" fill="{col}"/>')
        for wy in range(y - bh + 8, y - 6, 12):
            for wx in range(x + 5, x + bw - 6, 9):
                if r.random() < .3:
                    out.append(f'<rect x="{wx}" y="{wy}" width="3.5" height="5" fill="{win}" opacity=".85"/>')
        x += bw + r.randint(0, 4)
    return "".join(out)


def cn_tower(x, y, col):
    return (f'<rect x="{x-3.5}" y="{y-190}" width="7" height="190" fill="{col}"/><ellipse cx="{x}" cy="{y-125}" rx="15" ry="7" fill="{col}"/>'
            f'<rect x="{x-1.5}" y="{y-230}" width="3" height="42" fill="{col}"/>')


def mosque(cx, y, col, w=100):
    h = w * .5
    return (f'<rect x="{cx-w/2}" y="{y-h}" width="{w}" height="{h}" fill="{col}"/>'
            f'<path d="M{cx-w*.42} {y-h} A{w*.42} {w*.42} 0 0 1 {cx+w*.42} {y-h} Z" fill="{col}"/>'
            f'<rect x="{cx-2}" y="{y-h-w*.42-16}" width="4" height="18" fill="{col}"/>'
            f'<rect x="{cx-w/2-12}" y="{y-h*2.2}" width="9" height="{h*2.2}" fill="{col}"/><path d="M{cx-w/2-14} {y-h*2.2} L{cx-w/2-7.5} {y-h*2.2-16} L{cx-w/2-1} {y-h*2.2} Z" fill="{col}"/>'
            f'<rect x="{cx+w/2+3}" y="{y-h*2.2}" width="9" height="{h*2.2}" fill="{col}"/><path d="M{cx+w/2+1} {y-h*2.2} L{cx+w/2+7.5} {y-h*2.2-16} L{cx+w/2+14} {y-h*2.2} Z" fill="{col}"/>')


def pines(y, xs, col="#14503a", s=1.0):
    return "".join(f'<path d="M{x} {y} L{x+14*s} {y-52*s} L{x+28*s} {y} Z M{x+3*s} {y-20*s} L{x+14*s} {y-66*s} L{x+25*s} {y-20*s} Z" fill="{col}"/>' for x in xs)


def sunset_bg(u, sx=280, sy=185):
    return (f'<defs>{_lin(u+"sk", [(0, "#26306b"), (.42, "#7b4c9e"), (.78, "#f08c4e"), (1, "#ffd37e")])}{_rad(u+"sun", "#fff3b0")}</defs>'
            f'<rect width="400" height="300" fill="url(#{u}sk)"/><circle cx="{sx}" cy="{sy}" r="95" fill="url(#{u}sun)"/>'
            f'<circle cx="{sx}" cy="{sy}" r="20" fill="#fff6c8"/>')


def water(u, y, c1="#27457c", c2="#0c1f45"):
    return (f'<defs>{_lin(u+"w", [(0, c1), (1, c2)])}</defs><rect y="{y}" width="400" height="{300-y}" fill="url(#{u}w)"/>'
            f'<g stroke="#ffd98a" stroke-opacity=".5" stroke-width="2"><path d="M230 {y+10} h70 M245 {y+22} h45 M255 {y+36} h28"/></g>')


def stack(x, y, n, u):
    s = ""
    for i in range(n):
        yy = y - i * 9
        s += (f'<ellipse cx="{x}" cy="{yy+4}" rx="22" ry="8" fill="#a37a2c"/><rect x="{x-22}" y="{yy-5}" width="44" height="9" fill="url(#{u}g)"/>'
              f'<ellipse cx="{x}" cy="{yy-5}" rx="22" ry="8" fill="#f4d77a" stroke="#a37a2c" stroke-width="1.5"/>')
    return s


def gold_def(u):
    return f'<defs>{_lin(u+"g", [(0, "#f6dd86"), (1, "#b98a30")], 0, 0, 1, 0)}</defs>'


# ---------- scenes ----------
def mosque_city(u):
    return _svg(sunset_bg(u, 290) + buildings(235, "#1a2152", 5, hmax=90, x1=240) + cn_tower(95, 235, "#1a2152")
                + mosque(290, 238, "#121a45", 92) + water(u, 235))


def city_back(u):
    return _svg(sunset_bg(u, 205, 180) + buildings(222, "#1c2556", 2, hmax=100, x1=400) + cn_tower(300, 222, "#1c2556")
                + water(u, 222) + f'<rect y="262" width="400" height="38" fill="#0b1228"/>' + back_g(118, 92, .72, u + "b"))


def cabin(u):
    return _svg(f'<defs>{_lin(u+"sk", [(0, "#4b8fd6"), (.6, "#b9dcf2"), (1, "#ffd9a0")])}{_rad(u+"s", "#fff2c0")}{_lin(u+"l", [(0, "#2f78b8"), (1, "#123a70")])}</defs>'
                f'<rect width="400" height="300" fill="url(#{u}sk)"/><circle cx="330" cy="120" r="90" fill="url(#{u}s)"/>'
                '<path d="M0 190 L70 100 L120 160 L180 80 L260 190 Z" fill="#6c86b8"/><path d="M70 100 L88 125 L70 118 L56 126 Z M180 80 L205 118 L186 108 L168 120 Z" fill="#fff"/>'
                '<path d="M120 200 L210 120 L300 200 L400 130 L400 200 Z" fill="#46689a"/>'
                f'<rect y="195" width="400" height="105" fill="url(#{u}l)"/><path d="M0 195 Q200 180 400 195 L400 210 L0 210 Z" fill="#245c97"/>'
                + pines(205, [-10, 14, 40, 330, 356, 378], s=1.25) +
                '<rect x="250" y="160" width="70" height="42" fill="#7a4a2a" stroke="#2b1a10" stroke-width="3"/><path d="M242 162 L285 128 L328 162 Z" fill="#4b2f1c" stroke="#2b1a10" stroke-width="3"/>'
                '<rect x="262" y="172" width="14" height="14" fill="#ffd36a"/><rect x="292" y="172" width="14" height="14" fill="#ffd36a"/>'
                '<path d="M240 210 H330" stroke="#4b2f1c" stroke-width="5"/><g stroke="#fff" stroke-opacity=".35" stroke-width="2"><path d="M60 230 h90 M90 246 h60 M280 232 h80"/></g>')


def desk_night(u):
    return _svg(f'<defs>{_lin(u+"bg", [(0, "#0a1228"), (1, "#18284d")])}{_rad(u+"lamp", "#ffd98a", .55, 0)}</defs>'
                f'<rect width="400" height="300" fill="url(#{u}bg)"/>'
                '<rect x="262" y="26" width="120" height="130" rx="6" fill="#0e1b3d" stroke="#2c4272" stroke-width="4"/>'
                + buildings(150, "#233b70", 9, hmax=70, x0=266, x1=380, hmin=20) +
                f'<circle cx="330" cy="170" r="130" fill="url(#{u}lamp)"/>'
                '<path d="M350 40 L375 40 L360 80 Z" fill="#2a2f45"/>'
                '<rect x="0" y="236" width="400" height="64" fill="#51321f"/><rect y="236" width="400" height="5" fill="#7a4d30"/>'
                + man_g(-6, 52, .66, "think", u + "m") +
                '<path d="M150 236 L250 236 L240 246 L160 246 Z" fill="#9aa3b5" stroke="#0a1126" stroke-width="2.5"/>'
                '<path d="M158 162 L246 162 L250 236 L150 236 Z" fill="#1b2a4a" stroke="#0a1126" stroke-width="3"/>'
                '<path d="M166 172 L240 172 L243 228 L160 228 Z" fill="#8ec5ff" opacity=".9"/><path d="M174 214 L196 196 L210 206 L232 182" stroke="#20c070" stroke-width="4" fill="none"/>'
                '<rect x="300" y="214" width="24" height="24" rx="4" fill="#e9edf7" stroke="#0a1126" stroke-width="2.5"/>')


def thinker(u):
    books = ""
    cols = ["#d94c4c", "#e9b43c", "#3ca06a", "#4c7ad9", "#9b59b6", "#e9edf7"]
    r = random.Random(4)
    for row in (86, 136):
        x = 14
        for _ in range(7):
            bw, bh = r.randint(9, 14), r.randint(30, 44)
            books += f'<rect x="{x}" y="{row-bh}" width="{bw}" height="{bh}" fill="{r.choice(cols)}" stroke="{OUT}" stroke-width="1.5"/>'
            x += bw + 1
        books += f'<rect x="8" y="{row}" width="116" height="5" fill="#6b4226"/>'
    return _svg(f'<defs>{_lin(u+"bg", [(0, "#1d2f58"), (1, "#0d1836")])}{_rad(u+"lamp", "#ffcf7a", .6, 0)}</defs>'
                f'<rect width="400" height="300" fill="url(#{u}bg)"/>{books}'
                f'<circle cx="360" cy="90" r="120" fill="url(#{u}lamp)"/>'
                '<path d="M352 40 L376 40 L368 70 L360 70 Z" fill="#e9b43c" stroke="#0a1126" stroke-width="2.5"/><rect x="361" y="70" width="5" height="60" fill="#0a1126"/>'
                '<rect y="262" width="400" height="38" fill="#12203f"/>' + man_g(150, 78, .72, "think", u + "m"))


def money(u):
    return _svg(f'<defs>{_rad(u+"gl", "#7fd0ff", .6, 0)}{_lin(u+"bg", [(0, "#1c4a72"), (1, "#0a1b38")])}</defs>'
                + gold_def(u) + f'<rect width="400" height="300" fill="url(#{u}bg)"/><circle cx="200" cy="150" r="170" fill="url(#{u}gl)"/>'
                + stack(95, 250, 6, u) + stack(150, 262, 3, u) + stack(300, 255, 5, u) + stack(350, 266, 2, u) +
                f'<path d="M200 252 C150 252 156 170 176 150 C186 138 178 128 172 116 L228 116 C222 128 214 138 224 150 C244 170 250 252 200 252 Z" fill="#14203f" stroke="{OUT}" stroke-width="4"/>'
                '<path d="M164 112 Q200 92 236 112 L226 130 L174 130 Z" fill="#e9b43c" stroke="#0a1126" stroke-width="3"/>'
                '<text x="200" y="212" font-family="Poppins" font-weight="800" font-size="62" fill="#f6df4b" text-anchor="middle">$</text>'
                '<path d="M200 100 C196 70 170 58 150 64 C154 90 176 102 200 100 Z" fill="#35b26a" stroke="#0a1126" stroke-width="3"/>'
                '<path d="M200 100 C204 62 232 48 256 54 C250 84 228 100 200 100 Z" fill="#4cc97e" stroke="#0a1126" stroke-width="3"/>')


def bills(u):
    return _svg(f'<defs>{_lin(u+"bg", [(0, "#1f4a8c"), (1, "#0d2350")])}</defs><rect width="400" height="300" fill="url(#{u}bg)"/>'
                '<rect x="40" y="130" width="130" height="110" fill="#f2e2c0" stroke="#0a1126" stroke-width="4"/><path d="M28 134 L105 70 L182 134 Z" fill="#b5523b" stroke="#0a1126" stroke-width="4"/>'
                '<rect x="92" y="180" width="26" height="60" fill="#6b4226" stroke="#0a1126" stroke-width="3"/><rect x="54" y="150" width="26" height="26" fill="#8ec5ff" stroke="#0a1126" stroke-width="3"/><rect x="130" y="150" width="26" height="26" fill="#8ec5ff" stroke="#0a1126" stroke-width="3"/>'
                '<g transform="rotate(6 280 150)"><rect x="215" y="48" width="130" height="190" rx="8" fill="#fff" stroke="#0a1126" stroke-width="4"/>'
                '<text x="280" y="82" font-family="Poppins" font-weight="800" font-size="17" fill="#12244a" text-anchor="middle">FACTURES</text>'
                + "".join(f'<rect x="232" y="{100+i*34}" width="16" height="16" rx="3" fill="#35b26a"/><path d="M235 {108+i*34} l4 5 l7 -10" stroke="#fff" stroke-width="3" fill="none"/><rect x="258" y="{104+i*34}" width="70" height="8" rx="4" fill="#b8c4dc"/>' for i in range(4)) +
                '</g>' + '<rect y="262" width="400" height="38" fill="#0a1a3c"/>')


def scale(u):
    return _svg(f'<defs>{_lin(u+"sk", [(0, "#a9d4ee"), (1, "#fbe7c0")])}{_rad(u+"s", "#fff2b0")}</defs><rect width="400" height="300" fill="url(#{u}sk)"/>'
                '<path d="M0 220 L60 140 L110 190 L170 120 L240 220 Z" fill="#7b97c4"/><path d="M200 220 L280 150 L340 200 L400 160 L400 220 Z" fill="#5d7fb2"/>'
                + gold_def(u) + '<rect y="238" width="400" height="62" fill="#1d4f86"/>'
                '<path d="M170 262 L230 262 L218 240 L182 240 Z" fill="#14203f" stroke="#0a1126" stroke-width="3"/><rect x="194" y="96" width="12" height="146" fill="#1b2a4f" stroke="#0a1126" stroke-width="2.5"/>'
                '<rect x="60" y="92" width="280" height="9" rx="4" fill="#1b2a4f" stroke="#0a1126" stroke-width="2.5"/><circle cx="200" cy="96" r="11" fill="#e9b43c" stroke="#0a1126" stroke-width="3"/>'
                '<path d="M70 100 L40 170 M70 100 L100 170 M330 100 L300 170 M330 100 L360 170" stroke="#1b2a4f" stroke-width="2.5"/>'
                '<path d="M30 170 H110 Q100 188 70 188 Q40 188 30 170 Z" fill="#14203f" stroke="#0a1126" stroke-width="3"/>'
                '<path d="M290 170 H370 Q360 188 330 188 Q300 188 290 170 Z" fill="#14203f" stroke="#0a1126" stroke-width="3"/>'
                f'<circle cx="330" cy="130" r="48" fill="url(#{u}s)"/>'
                '<path d="M52 170 C46 152 54 144 62 138 L78 138 C86 144 94 152 88 170 Z" fill="#14203f" stroke="#0a1126" stroke-width="3"/><text x="70" y="164" font-family="Poppins" font-weight="800" font-size="22" fill="#f6df4b" text-anchor="middle">$</text>'
                + kid(312, 92, .42, "#4c7ad9") + kid(332, 82, .6, "#14203f") + kid(352, 92, .42, "#e88aa8") +
                '<text x="70" y="214" font-family="Poppins" font-weight="800" font-size="17" fill="#fff" text-anchor="middle" stroke="#0a1126" stroke-width="3" paint-order="stroke">ARGENT</text>'
                '<text x="330" y="214" font-family="Poppins" font-weight="800" font-size="17" fill="#fff" text-anchor="middle" stroke="#0a1126" stroke-width="3" paint-order="stroke">TEMPS</text>')


def shield(u):
    return _svg(f'<defs>{_lin(u+"bg", [(0, "#1d7a52"), (1, "#0b3a36")])}{_lin(u+"sh", [(0, "#4c9bff"), (1, "#1a4a9c")])}</defs>' + gold_def(u) +
                f'<rect width="400" height="300" fill="url(#{u}bg)"/>'
                f'<path d="M110 60 L200 40 L290 60 C290 150 250 210 200 240 C150 210 110 150 110 60 Z" fill="url(#{u}sh)" stroke="{OUT}" stroke-width="5"/>'
                '<path d="M150 130 L188 168 L252 96" stroke="#fff" stroke-width="16" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                '<ellipse cx="320" cy="238" rx="52" ry="38" fill="#f4a3b8" stroke="#0a1126" stroke-width="4"/><ellipse cx="364" cy="232" rx="14" ry="11" fill="#e9839f" stroke="#0a1126" stroke-width="3"/>'
                '<path d="M300 204 L308 186 L322 202 Z" fill="#e9839f" stroke="#0a1126" stroke-width="3"/><rect x="306" y="200" width="30" height="6" rx="3" fill="#0a1126"/>'
                '<circle cx="348" cy="228" r="3.5" fill="#0a1126"/><rect x="290" y="268" width="12" height="16" rx="4" fill="#e9839f" stroke="#0a1126" stroke-width="3"/><rect x="336" y="268" width="12" height="16" rx="4" fill="#e9839f" stroke="#0a1126" stroke-width="3"/>'
                '<rect x="40" y="218" width="76" height="58" rx="8" fill="#fff" stroke="#0a1126" stroke-width="4"/><path d="M78 228 v38 M59 247 h38" stroke="#d93a3a" stroke-width="12"/>'
                + stack(140, 282, 3, u))


def house(u):
    return _svg(sunset_bg(u, 80, 150) + pines(250, [10, 36, 340, 366], "#0f3a35", 1.4) +
                '<rect y="248" width="400" height="52" fill="#0d1a2f"/>'
                '<rect x="130" y="150" width="150" height="100" fill="#2a2f52" stroke="#0a1126" stroke-width="4"/><path d="M116 154 L205 88 L294 154 Z" fill="#3a2a46" stroke="#0a1126" stroke-width="4"/>'
                '<rect x="244" y="96" width="18" height="40" fill="#2a2f52" stroke="#0a1126" stroke-width="3"/>'
                '<rect x="150" y="172" width="32" height="32" fill="#ffd36a" stroke="#0a1126" stroke-width="3"/><rect x="228" y="172" width="32" height="32" fill="#ffd36a" stroke="#0a1126" stroke-width="3"/>'
                '<rect x="190" y="196" width="30" height="54" fill="#ffb347" stroke="#0a1126" stroke-width="3"/>'
                '<circle cx="64" cy="268" r="14" fill="none" stroke="#e9b43c" stroke-width="7"/><rect x="76" y="265" width="46" height="7" fill="#e9b43c"/><rect x="108" y="272" width="7" height="12" fill="#e9b43c"/>')


def stocks(u):
    bars = ""
    for i, h in enumerate([40, 62, 54, 90, 118, 150]):
        x = 36 + i * 42
        bars += f'<rect x="{x}" y="{250-h}" width="30" height="{h}" rx="4" fill="url(#{u}b)" stroke="{OUT}" stroke-width="2.5"/>'
    return _svg(f'<defs>{_lin(u+"bg", [(0, "#10305a"), (1, "#081530")])}{_lin(u+"b", [(0, "#5ee09a"), (1, "#1a8a55")])}</defs>' + gold_def(u) +
                f'<rect width="400" height="300" fill="url(#{u}bg)"/><g stroke="#ffffff" stroke-opacity=".08" stroke-width="2">'
                + "".join(f'<path d="M0 {y} H400"/>' for y in range(60, 260, 40)) + '</g>' + bars +
                '<path d="M40 190 L100 160 L150 176 L206 120 L250 96 L296 50" stroke="#f6df4b" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                '<path d="M270 44 L306 44 L306 80" stroke="#f6df4b" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                + stack(350, 262, 4, u) + '<rect y="256" width="400" height="44" fill="#06102a" opacity=".6"/>')


def family(u):
    return _svg(sunset_bg(u, 200, 150) + '<path d="M0 200 L70 130 L130 190 L200 110 L280 200 L340 150 L400 200 L400 300 L0 300 Z" fill="#3a3270" opacity=".85"/>'
                + water(u, 205, "#3c4f8c", "#14214a") + pines(215, [-6, 20, 350, 374], "#102c4a", 1.2) +
                '<rect y="250" width="400" height="50" fill="#0b1228"/>'
                '<g transform="translate(0,-30)"><path d="M110 300 C110 244 140 232 160 232 C180 232 210 244 210 300 Z" fill="#162a55" stroke="#0a1126" stroke-width="3.5"/><circle cx="160" cy="208" r="24" fill="#15151d" stroke="#0a1126" stroke-width="3.5"/>'
                '<path d="M60 300 C60 262 78 254 92 254 C106 254 120 262 120 300 Z" fill="#2c5bd0" stroke="#0a1126" stroke-width="3"/><circle cx="92" cy="236" r="17" fill="#15151d" stroke="#0a1126" stroke-width="3"/>'
                '<path d="M200 300 C200 262 218 254 232 254 C246 254 260 262 260 300 Z" fill="#e88aa8" stroke="#0a1126" stroke-width="3"/><circle cx="232" cy="236" r="17" fill="#2a1a10" stroke="#0a1126" stroke-width="3"/>'
                '<path d="M218 226 C216 262 226 270 236 268" stroke="#2a1a10" stroke-width="10" fill="none" stroke-linecap="round"/></g>')


SCENES = dict(mosque=mosque_city, city=city_back, cabin=cabin, desk=desk_night, thinker=thinker, money=money,
              bills=bills, scale=scale, shield=shield, house=house, stocks=stocks, family=family)


def scene(name, uid):
    return SCENES[name](uid)


# ---------- decors d'en-tete et de pied (1024 x H) ----------
def header_bg(u="hd"):
    return (f'<svg class="hbg" viewBox="0 0 1024 338" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg"><defs>'
            f'{_lin(u+"sk", [(0, "#0c1c42"), (.5, "#1c4585"), (.82, "#4f93d6"), (1, "#ffd9a0")], 0, 0, 1, 0)}{_rad(u+"s", "#fff2c0", .9, 0)}{_lin(u+"l", [(0, "#2f78b8"), (1, "#123a70")])}</defs>'
            f'<rect width="1024" height="338" fill="url(#{u}sk)"/><circle cx="880" cy="215" r="150" fill="url(#{u}s)"/>'
            '<path d="M560 300 L680 150 L760 240 L860 120 L1000 300 Z" fill="#3a63a0"/><path d="M860 120 L890 165 L862 152 L838 168 Z M680 150 L700 182 L680 172 L664 186 Z" fill="#fff" opacity=".9"/>'
            + buildings(300, "#13306a", 21, hmax=130, x0=0, x1=560, hmin=40) + cn_tower(300, 300, "#13306a") + mosque(470, 300, "#0e2456", 90) +
            f'<rect y="290" width="1024" height="48" fill="url(#{u}l)"/>'
            + pines(300, [560, 596, 640, 940, 976], "#14503a", 1.5) + '</svg>')


def footer_bg(u="ft"):
    return (f'<svg class="fbg" viewBox="0 0 1024 176" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg"><defs>'
            f'{_lin(u+"sk", [(0, "#0a2552"), (.6, "#1a5a96"), (1, "#3f9bb0")])}{_lin(u+"l", [(0, "#1d6aa8"), (1, "#0a3a5e")])}</defs>'
            f'<rect width="1024" height="176" fill="url(#{u}sk)"/>'
            '<path d="M0 120 L60 70 L120 112 L170 120 Z" fill="#2c6aa5"/><path d="M700 120 L790 36 L880 110 L960 50 L1024 110 L1024 120 Z" fill="#2c6aa5"/>'
            '<path d="M790 36 L812 66 L792 58 L774 68 Z" fill="#fff" opacity=".25"/>'
            + buildings(130, "#0f3a6a", 31, hmax=70, x0=300, x1=700, hmin=25) + cn_tower(140, 130, "#0b2f5c") + mosque(900, 130, "#0b2f5c", 60) +
            f'<rect y="126" width="1024" height="50" fill="url(#{u}l)"/>'
            + pines(136, [0, 30, 60, 90, 940, 970, 1000], "#0e4a36", 1.5) + pines(140, [200, 232, 780, 812], "#14603f", 1.1) +
            '<g stroke="#ffd98a" stroke-opacity=".35" stroke-width="2"><path d="M360 150 h120 M560 156 h100 M440 164 h160"/></g></svg>')


def workspace(u="wk"):
    """Bureau (sans personnage): portable avec graphique, tasse, pile de livres, plante. viewBox 420x200."""
    books = ""
    for i, (txt, col) in enumerate([("INVESTIR", "#1b3a78"), ("ÉPARGNER", "#16305f"), ("PLANIFIER", "#1b3a78"), ("RÉUSSIR", "#16305f")]):
        y = 78 + i * 18
        books += (f'<rect x="{292+(i%2)*6}" y="{y}" width="108" height="17" rx="3" fill="{col}" stroke="{OUT}" stroke-width="2.5"/>'
                  f'<text x="{346+(i%2)*6}" y="{y+12.5}" font-family="Poppins" font-weight="700" font-size="10" fill="#f6df4b" text-anchor="middle">{txt}</text>')
    return f"""<svg class="wk" viewBox="0 0 420 200" xmlns="http://www.w3.org/2000/svg"><defs>{_lin(u+"d", [(0, "#9a6338"), (1, "#6b3f22")])}</defs>
<rect x="0" y="150" width="420" height="50" fill="url(#{u}d)" stroke="{OUT}" stroke-width="3"/><rect x="0" y="150" width="420" height="5" fill="#c58a56"/>
<path d="M24 150 C20 128 26 112 34 104 C40 116 44 130 40 150 Z M40 150 C44 124 56 110 66 106 C66 124 60 138 54 150 Z" fill="#35b26a" stroke="{OUT}" stroke-width="2.5"/>
<rect x="22" y="144" width="40" height="8" rx="2" fill="#c9693c" stroke="{OUT}" stroke-width="2"/>
<rect x="84" y="108" width="42" height="42" rx="6" fill="#fff" stroke="{OUT}" stroke-width="3"/><path d="M126 118 q16 0 16 14 q0 14 -16 14" stroke="{OUT}" stroke-width="3" fill="none"/>
<text x="105" y="126" font-family="Poppins" font-weight="700" font-size="9" fill="#12244a" text-anchor="middle">Petit pas</text><text x="105" y="138" font-family="Poppins" font-weight="700" font-size="9" fill="#12244a" text-anchor="middle">Grands projets</text>
<path d="M164 150 L274 150 L266 160 L172 160 Z" fill="#aab3c4" stroke="{OUT}" stroke-width="3"/>
<rect x="170" y="52" width="98" height="98" rx="7" fill="#1d2a44" stroke="{OUT}" stroke-width="3.5"/><rect x="178" y="60" width="82" height="82" fill="#8ec5ff"/>
<path d="M184 128 L204 108 L218 118 L252 76" stroke="#20c070" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M238 74 L254 74 L254 90" stroke="#20c070" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
{books}</svg>"""
