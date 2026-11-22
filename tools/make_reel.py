#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Générateur de Reels Finance Halal Canada (9:16, 1080x1920, 30 fps), gabarit v4 « plein cadre ».

Usage :
  python3 tools/make_reel.py specs/reels/<nom>.json [dossier_sortie] [--preview] [--no-qa]

Étapes : voix off (Piper, voix fr-siwis) -> horodatage des mots -> page HTML unique pilotée
par un temps global (Chromium/Playwright) -> un MP4 par scène -> concat -> mixage
(voix, anachid avec ducking, « ding ») -> contrôles qualité automatiques.
Grille, couleurs et règles : docs/STYLE.md, section « Reels 9:16 ».
"""
import json, math, os, re, subprocess, sys, tempfile, unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scenes as SC
from make_post import icon_uri, jagged, LEAF, FONTS

W, H, FPS = 1080, 1920, 30
PIPER_MODEL = os.environ.get("FHC_PIPER_MODEL", "/home/claude/vo/model/fr-siwis-medium.onnx")
Y, G, NAVY, RED = "#f6df4b", "#d9b24f", "#12244a", "#d94c4c"
SENT_GAP, SCENE_LEAD, TAIL, LOOP, MAX_PAUSE = 0.18, 0.12, 0.08, 0.4, 0.20


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def dur(path):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).stdout)


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9']", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


# ---------------------------------------------------------------- voix + horodatage
def tokens(sentence):
    """Mots avec la ponctuation française détachée (« un : », « intérêts ? ») recollée au mot précédent."""
    out = []
    for t in sentence.split():
        if out and not re.search(r"\w", t):
            out[-1] += "\u00a0" + t
        else:
            out.append(t)
    return out


def syll(w):
    return max(1, len(re.findall(r"[aeiouyàâäéèêëîïôöûùü]+", w.lower()))) + 0.3


def synth_sentence(text, out_wav, tmp):
    raw = tmp / (out_wav.stem + "_raw.wav")
    subprocess.run(["piper", "-m", PIPER_MODEL, "--length-scale", "0.92", "--sentence-silence", "0", "-f", str(raw)],
                   input=text, text=True, check=True, capture_output=True)
    trim = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,areverse,"
            "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", trim, "-ar", "22050", str(out_wav)])
    def detect():
        log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(out_wav), "-af", "silencedetect=n=-40dB:d=0.09",
                              "-f", "null", "-"], capture_output=True, text=True).stderr
        st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
        en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
        dd = dur(out_wav)
        return dd, [(a, b) for a, b in zip(st, en) if 0.05 < a < dd - 0.05]
    d, pauses = detect()
    long = [(a, b) for a, b in pauses if b - a > MAX_PAUSE + 0.02]
    if long:  # on raccourcit les pauses internes trop longues
        import wave, numpy as np
        with wave.open(str(out_wav)) as wf:
            prm = wf.getparams(); x = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        sr, keep, last = prm.framerate, [], 0
        for a, b in long:
            cut0, cut1 = int((a + MAX_PAUSE / 2) * sr), int((b - MAX_PAUSE / 2) * sr)
            keep.append(x[last:cut0]); last = cut1
        keep.append(x[last:])
        with wave.open(str(out_wav), "wb") as wf:
            wf.setparams(prm); wf.writeframes(np.concatenate(keep).astype(np.int16).tobytes())
        d, pauses = detect()
    if False:
     log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(out_wav), "-af", "silencedetect=n=-40dB:d=0.09",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    toks = tokens(text)
    groups, cur = [], []
    for t in toks:
        cur.append(t)
        if re.search(r"[,:;]\s*$", t.replace("\u00a0", " ")) and t is not toks[-1]:
            groups.append(cur); cur = []
    if cur: groups.append(cur)
    spans = []
    if len(pauses) == len(groups) - 1:
        edges = [0.0] + [x for p in pauses for x in p] + [d]
        spans = [(edges[2 * i], edges[2 * i + 1]) for i in range(len(groups))]
    else:  # repli : un seul groupe
        groups, spans = [toks], [(0.0, d)]
    words = []
    for g, (a, b) in zip(groups, spans):
        tot = sum(syll(w) for w in g); t = a
        for w in g:
            e = t + (b - a) * syll(w) / tot
            words.append({"w": w, "s": round(t, 3), "e": round(e, 3)})
            t = e
    return d, words


# ---------------------------------------------------------------- timeline
def build_timeline(spec, tmp):
    T, scenes, words, clips = 0.0, [], [], []
    for i, sc in enumerate(spec["scenes"]):
        lead = 0.05 if i == 0 else SCENE_LEAD
        t, sw = T + lead, []
        for j, sent in enumerate(sc["voice"]):
            wav = tmp / f"s{i}_{j}.wav"
            d, ws = synth_sentence(sent, wav, tmp)
            clips.append((wav, t))
            for w in ws:
                sw.append({"w": w["w"], "s": round(t + w["s"], 3), "e": round(t + w["e"], 3), "scene": i})
            t += d + SENT_GAP
        voice_end = t - SENT_GAP
        end = voice_end + (0.05 if sc["type"] == "end" else TAIL)
        scenes.append({"s": round(T, 3), "e": round(end, 3), "voice_end": round(voice_end, 3)})
        words += sw
        T = end
    return scenes, words, clips, round(T, 3)


def word_time(words, scene_i, key, after=0.0):
    if key is None:
        return None
    if isinstance(key, (int, float)):
        return key
    if isinstance(key, str) and key.startswith("+"):
        return after + float(key[1:])
    k = norm(key)
    for w in words:
        if w["scene"] == scene_i and w["s"] - 0.10 > after + 0.01 and norm(w["w"]).startswith(k):
            return w["s"] - 0.10
    for w in words:
        if w["scene"] == scene_i and norm(w["w"]).startswith(k):
            return w["s"] - 0.10
    raise ValueError(f"mot d'ancrage introuvable dans la scène {scene_i + 1}: {key!r}")


def typo(x):
    """Apostrophe typographique (hors balises HTML)."""
    return re.sub(r"(?<=\w)'(?=\w)", "’", x)


NUMS = {"un": "1", "deux": "2", "trois": "3", "quatre": "4", "cinq": "5"}


def display_word(w, prev, disp):
    m = re.match(r"^([\w'’\-]+)(.*)$", w, re.S)
    if not m:
        return w
    core, rest = m.group(1), m.group(2)
    n = norm(core)
    if prev is not None and norm(prev) == "etape" and n in NUMS:
        core = NUMS[n]
    elif n in disp:
        core = disp[n]
    return typo(core) + rest


# ---------------------------------------------------------------- HTML
CSS = """
@font-face{font-family:'Kalam';font-weight:700;src:url('file://FONTS/kalam-latin-700-normal.woff2')}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden;font-family:'Poppins',sans-serif;color:#fff;background:#0b1a3c}
.abs{position:absolute}
#world{position:absolute;inset:0;transform-origin:540px 700px}
.sky{left:0;top:0;width:1080px;height:820px;background:linear-gradient(180deg,#0b1a3c 0%,#1d3f86 55%,#2d63b8 100%)}
.star{width:7px;height:7px;border-radius:50%;background:#fff;box-shadow:0 0 10px #fff}
.strip{left:0;top:470px;width:1240px;height:340px;-webkit-mask-image:linear-gradient(transparent 0,#000 120px);mask-image:linear-gradient(transparent 0,#000 120px)}
.strip svg{width:100%;height:100%}
.mascot{left:720px;top:446px;width:340px;height:374px;transform-origin:170px 374px;z-index:2}
.mascot svg{position:absolute;inset:0;width:100%;height:100%;display:none}
.eyes{transform-box:fill-box;transform-origin:center}
.bubble{left:940px;top:380px;z-index:7;font-family:'Kalam',cursive;font-weight:700;font-size:56px;color:NAVY;background:Y;
  padding:0 18px;border-radius:24px;transform:rotate(8deg);box-shadow:0 6px 14px rgba(0,0,0,.35);opacity:0}
.brush{left:40px;top:252px;width:790px;height:350px;background:rgba(8,18,44,.92);z-index:4}
.ttl{left:72px;top:262px;width:728px;height:330px;z-index:5;display:flex;flex-direction:column;justify-content:center;opacity:0}
.ttl .t{font-weight:800;font-size:80px;line-height:1.22;letter-spacing:-1px;text-shadow:0 3px 10px rgba(0,0,0,.35)}
.ttl.hook .t{font-size:88px;line-height:1.1}
.ttl mark{position:relative;background:Y;color:NAVY;padding:0 16px;border-radius:12px;display:inline-block;text-shadow:none;margin:4px 6px;transform:rotate(-2deg)}
.ttl.hook mark{font-size:100px;text-transform:uppercase}
.ttl mark:after{content:'';position:absolute;left:10px;right:10px;bottom:-8px;height:6px;border-radius:3px;background:RED;transform-origin:left;transform:scaleX(var(--u,0))}
.pill{left:64px;top:612px;z-index:5;display:flex;align-items:center;gap:14px;background:NAVY;border:2px solid rgba(246,223,75,.5);
  padding:8px 18px;border-radius:14px;font-weight:800;font-size:28px;letter-spacing:2px;opacity:0}
.pill i{display:inline-block;width:56px;height:10px;border-radius:5px;background:rgba(255,255,255,.25)}
.pill i.f{background:Y}
.sheet{left:0;top:780px;width:1080px;height:800px;background:#f8fcfb;border-radius:56px 56px 0 0;box-shadow:0 -12px 32px rgba(10,30,60,.25);z-index:3}
.content{left:76px;top:830px;width:826px;height:500px;z-index:4;display:none;transform-origin:413px 250px}
.cc{left:64px;top:1350px;width:876px;min-height:160px;z-index:4;display:flex;flex-wrap:wrap;justify-content:center;align-content:center;
  gap:4px 14px;padding:14px 26px;border-radius:24px;background:rgba(18,36,74,.92);font:800 60px/1.05 Poppins;color:#fff;opacity:0}
.cc .k{color:Y}
.cc .on{background:Y;color:NAVY;border-radius:10px;padding:0 10px;display:inline-block;transform:scale(1.08)}
.disc{left:64px;top:1250px;width:876px;z-index:4;text-align:center;color:#3c5170;font-weight:500;font-size:32px;line-height:1.3;display:none}
.foot{left:0;top:1540px;width:1080px;height:380px;background:NAVY;overflow:hidden;z-index:5}
.foot svg{position:absolute;left:0;top:0;width:1150px;height:100%}
.flogo{left:0;right:0;top:56px;display:flex;align-items:center;justify-content:center;gap:16px;z-index:2;opacity:.92}
.fhc{font-family:'Lora',serif;font-weight:700;font-size:72px;line-height:1;letter-spacing:-2px;color:#fff;position:relative}
.fhc:after{content:'';position:absolute;top:26px;height:6px;left:38px;right:42px;background:#e23b3b;transform:rotate(-16deg);border-radius:3px}
.fhc .leaf{width:28px;height:28px;position:absolute;left:97px;top:19px}
.sep{width:3px;height:72px;background:rgba(255,255,255,.7)}
.ln{font-weight:800;font-size:26px;line-height:1.02;letter-spacing:.6px}
.ln .g{color:G}
.band{left:-1400px;top:780px;width:1400px;height:760px;background:Y;transform:skewX(-12deg);z-index:9;display:none}
/* blocs */
.card{background:#fff;border-radius:32px;box-shadow:0 16px 40px rgba(0,0,0,.25);display:flex;align-items:center;gap:26px;padding:26px 34px;color:NAVY}
.notif{position:absolute;left:28px;top:30px;width:820px;height:240px;opacity:0}
.notif img{width:110px;height:110px}
.notif .lb{font-weight:600;font-size:40px;line-height:1.2;color:#51627e}
.notif .amt,.notif .amt0{font-weight:800;font-size:72px;line-height:1.05;color:#1f9d55}
.stamp{position:absolute;left:520px;top:120px;border:6px solid RED;color:RED;font-weight:800;font-size:72px;padding:0 20px;border-radius:14px;
  transform:rotate(-8deg);opacity:0;background:rgba(255,255,255,.88)}
.promise{position:absolute;left:0;right:0;top:330px;margin:auto;width:max-content;max-width:826px;background:Y;color:NAVY;font-family:'Kalam',cursive;
  font-weight:700;font-size:50px;line-height:1.15;padding:14px 30px;border-radius:18px;box-shadow:0 6px 14px rgba(0,0,0,.2);opacity:0;display:flex;gap:16px;align-items:center}
.promise .ar{display:inline-block}
.stat{position:absolute;left:0;top:0;width:826px;height:330px;background:NAVY;border:3px solid rgba(246,223,75,.6);border-radius:32px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;opacity:0}
.stat img{width:110px;height:110px}
.stat .lb{font-weight:700;font-size:52px}
.stat .val{font-weight:800;font-size:120px;line-height:1;color:Y;opacity:0}
.kpill{position:absolute;left:0;right:0;top:370px;margin:auto;width:max-content;max-width:826px;background:Y;color:NAVY;font-family:'Kalam',cursive;
  font-weight:700;font-size:46px;padding:12px 28px;border-radius:18px;opacity:0;text-align:center}
.rows{display:flex;flex-direction:column;gap:20px;height:100%}
.row{flex:1;display:flex;align-items:center;gap:26px;padding:0 30px;background:#fff;border:4px solid #36a27a;border-radius:28px;color:NAVY;opacity:0}
.row.x{border-color:RED}
.row.warn{border-color:RED;background:#fff6f5}
.row img{width:96px;height:96px;flex:none}
.row .tx{flex:1;font-weight:700;font-size:52px;line-height:1.1}
.row.small .tx{font-size:40px;font-weight:600}
.row.small img{width:72px;height:72px}
.row .end{width:72px;height:72px;flex:none}
.cards{display:flex;gap:20px;height:320px}
.cd{flex:1;border-radius:28px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;text-align:center;padding:20px;opacity:0}
.cd img{width:110px;height:110px}
.cd .tx{font-weight:700;font-size:52px;line-height:1.1}
.c-green{background:linear-gradient(160deg,#27a05a,#14633a)}
.c-blue{background:linear-gradient(160deg,#2457b4,#16346e)}
.c-purple{background:linear-gradient(160deg,#6a4cc0,#3b2780)}
.banner{margin-top:24px;background:Y;color:NAVY;font-family:'Kalam',cursive;font-weight:700;font-size:54px;text-align:center;padding:18px 26px;
  border-radius:20px;box-shadow:0 6px 14px rgba(0,0,0,.22);opacity:0}
.endb{position:relative;height:100%}
.bm{position:absolute;left:363px;top:-6px;width:100px;height:107px;opacity:0;transform-origin:80px 0}
.q{position:absolute;left:0;right:0;top:110px;margin:auto;width:max-content;max-width:826px;background:Y;color:NAVY;font-family:'Kalam',cursive;font-weight:700;
  font-size:46px;line-height:1.15;text-align:center;padding:10px 28px;border-radius:18px;opacity:0}
.q b{color:RED}
.elogo{position:absolute;left:0;right:0;top:252px;display:flex;flex-direction:column;align-items:center;gap:8px;opacity:0}
.elogo .lg{display:flex;align-items:center;gap:20px;background:NAVY;padding:10px 28px;border-radius:22px}
.elogo .fhc{font-size:72px}.elogo .fhc:after{top:26px;left:38px;right:42px;height:6px}.elogo .fhc .leaf{left:97px;top:19px;width:28px;height:28px}
.elogo .ln{font-size:30px}
.elogo .tag{font-weight:800;font-size:32px;letter-spacing:1px;color:#7a5f12}
.elogo .hd{font-weight:700;font-size:40px;line-height:1.1;color:NAVY}
"""

JS = r"""
const S=DATA.scenes, TT=DATA.T, C=x=>Math.max(0,Math.min(1,x)), EO=x=>1-Math.pow(1-C(x),3), EI=x=>Math.pow(C(x),3);
const BK=x=>{x=C(x);const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
const CB=(x)=>{x=C(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2};
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
function anim(el,t){ // data-in / data-k / data-d
  const t0=+el.dataset.in, d=+(el.dataset.d||0.4), k=el.dataset.k||'up', p=(t-t0)/d, base=el.dataset.b||'';
  if(t<t0){el.style.opacity=el.dataset.ghost&&t>=+el.dataset.ghost?0.25:0;el.style.transform=base;return;}
  const e=EO(p);
  if(k==='up'){el.style.opacity=e;el.style.transform=base+` translateY(${(1-e)*60}px)`;}
  else if(k==='left'){el.style.opacity=e;el.style.transform=base+` translateX(${(1-e)*-90}px)`;}
  else if(k==='pop'){el.style.opacity=C(p*3);el.style.transform=base+` scale(${p>=1?1:BK(p)})`;}
  else if(k==='drop'){el.style.opacity=e;el.style.transform=base+` translateY(${(1-e)*-160}px)`;}
  else if(k==='stamp'){el.style.opacity=C(p*4);el.style.transform=base+` scale(${p>=1?1:2.2-1.2*BK(p)})`;}
  else el.style.opacity=e;
  if(el.dataset.pulse){const q=(t-+el.dataset.pulse)/0.3; if(q>0&&q<1) el.style.transform+=` scale(${1+0.06*Math.sin(Math.PI*q)})`;}
}
function scene(t){for(let i=0;i<S.length;i++) if(t<S[i].e) return i; return S.length-1;}
window.T=(t)=>{
  const si=scene(t), sc=S[si], loop=t>=TT-DATA.loop;
  // monde : punch d'ouverture
  $('#world').style.transform=`scale(${t>TT-0.2?1+0.04*EO((t-(TT-0.2))/0.2):1+0.04*(1-EO(t/0.35))})`;
  // ciel
  const PX=Math.sin(Math.PI*t/TT); $('.strip').style.transform=`translateX(${-140*PX}px)`;$('.foot svg').style.transform=`translateX(${-70*PX}px)`;
  $('.flogo').style.opacity=(t>=DATA.flogo_off&&t<TT-DATA.loop)?0:0.92;
  $$('.star').forEach((s,i)=>s.style.opacity=0.3+0.7*(0.5+0.5*Math.sin(t*(2.2+i*0.37)+i*1.7)));
  // titres : entrée 0.3 s (sauf image 0), sortie 0.15 s
  $$('.ttl').forEach(el=>{
    const a=+el.dataset.in, b=+el.dataset.out;
    if(t<a||t>=b){el.style.opacity=0;return;}
    let o=1,y=0;
    if(a>0){const p=EO((t-a)/0.3);o=p;y=(1-p)*40;}
    if(t>b-0.15){const q=EI((t-(b-0.15))/0.15);o*=1-q;y-=40*q;}
    el.style.opacity=o;el.style.transform=`translateY(${y}px)`;
    const m=el.querySelector('mark');
    if(m&&el.dataset.pulse){const p=(t-+el.dataset.pulse)/0.3;
      const s=p>0&&p<1?1+0.06*Math.sin(Math.PI*p):1; m.style.transform=`rotate(-2deg) scale(${s})`;
      m.style.setProperty('--u',EO((t-+el.dataset.pulse)/0.25));}
  });
  // pastille d'étape
  $$('.pill').forEach(el=>{const a=+el.dataset.in,b=+el.dataset.out; if(t<a||t>=b){el.style.opacity=0;return;}
    let o=EO((t-a)/0.3); if(t>b-0.15) o*=1-EI((t-(b-0.15))/0.15); el.style.opacity=o;});
  // contenu de la feuille : bascule au milieu du balayage
  $$('.content').forEach(el=>{const a=+el.dataset.in,b=+el.dataset.out, on=t>=a&&t<b;
    el.style.display=on?'block':'none';
    if(on){el.style.transform=`scale(${1+0.03*C((t-a)/(b-a))})`; el.querySelectorAll('[data-in]').forEach(x=>anim(x,t));}});
  // notification : compteur, secousse
  const amt=$('.amt'); if(amt){const p=EO((t-0.1)/0.6); amt.textContent='+'+(DATA.amount*p).toFixed(2).replace('.',',')+'\u00a0$';
    const st=$('.stamp'); const k=(t-+st.dataset.in)/0.2; const n=$('.notif');
    if(k>0.4&&k<1.4&&n) n.style.transform=`translateX(${6*Math.sin(k*40)}px)`;}
  $$('.ar').forEach(a=>a.style.transform=`translateX(${8*Math.sin(t*2*Math.PI/0.6)}px)`);
  const bm=$('.bm'); if(bm&&+bm.style.opacity>0) bm.style.transform=`rotate(${4*Math.sin(t*3)}deg) `+bm.style.transform.replace(/rotate\([^)]*\)\s*/,'');
  // balayage jaune
  let band=null; for(const b of DATA.cuts){ if(Math.abs(t-b)<0.18) band=b; }
  const bd=$('.band'); if(band===null) bd.style.display='none'; else {bd.style.display='block';
    const p=CB((t-(band-0.18))/0.36); bd.style.left=(-1400+2480*p)+'px';}
  // sous-titres
  const cc=$('.cc'); let chunk=null;
  for(const c of DATA.chunks){ if(t>=c.a&&t<c.b) chunk=c; }
  if(!chunk){cc.style.opacity=0;} else {
    cc.innerHTML=chunk.w.map((w,j)=>{const nx=chunk.w[j+1];const on=t>=w.s-0.04&&t<(nx?nx.s-0.04:w.e);return `<span class="${w.k?'k':''} ${on?'on':''}">${w.d}</span>`;}).join(' ');
    const p=EO((t-chunk.a)/0.15); cc.style.opacity=p; cc.style.transform=`translateY(${(1-p)*20}px)`;}
  $('.disc').style.display=(t>=DATA.disc[0]&&t<DATA.disc[1])?'block':'none';
  // mascotte : pose, respiration, flottement, clignement, rebond
  let pose='think', pt=-9; for(const [pt0,pz] of DATA.poses){ if(t>=pt0){pose=pz;pt=pt0;} }
  if(loop){pose=DATA.poses[0][1];pt=TT-DATA.loop;}
  $$('.mascot svg').forEach(s=>s.style.display=s.dataset.pose===pose?'block':'none');
  const bq=(t-pt)/0.25, bounce=bq>0&&bq<1?(bq<.4?1-0.08*Math.sin(bq/.4*Math.PI/2):1+0.04*Math.sin((bq-.4)/.6*Math.PI)):1;
  const ma=$('.mascot'); const K1=Math.max(1,Math.round(TT/Math.PI)), K2=Math.max(1,Math.round(TT/2));
  ma.style.transform=`translateY(${12*Math.sin(2*Math.PI*K1*t/TT)}px) scaleY(${(1+0.015*Math.sin(2*Math.PI*K2*t/TT))*bounce})`;
  const bl=(t%3.6), ey=bl<0.12?1-0.9*Math.sin(bl/0.12*Math.PI):1;
  $$('.eyes').forEach(e=>e.style.transform=`scaleY(${ey})`);
  $('.bubble').style.opacity=pose==='surprised'?EO((t-pt)/0.2):0;
  $('.bubble').style.transform=`rotate(8deg) scale(${pose==='surprised'?BK((t-pt)/0.3):1})`;
};
"""


def mascot_svgs():
    out = []
    for pose in ("think", "smile", "surprised"):
        base = "think" if pose == "think" else "smile"
        s = SC.man(base, "m" + pose[:2])
        lines = s.split("\n")
        eyes = [l for l in lines if 'cy="126" rx="12"' in l or 'cy="124" r="6"' in l or 'cy="122" r="2"' in l]
        brows = [l for l in lines if "M106 108" in l or "M160 104" in l]
        rest = [l for l in lines if l not in eyes and l not in brows]
        body = "\n".join(rest)
        eyes_g = f'<g class="eyes">{"".join(eyes)}</g>'
        brow_g = "".join(brows)
        if pose == "surprised":
            brow_g = f'<g transform="translate(0,-7)">{brow_g}</g>'
            eyes_g = f'<g transform="translate(150 126) scale(1.15) translate(-150 -126)">{eyes_g}</g>'
            body = re.sub(r'<path d="M124 180 Q150 206 176 180[^>]*/>',
                          '<ellipse cx="150" cy="190" rx="13" ry="16" fill="#3a1c14" stroke="#0a1126" stroke-width="2.5"/>', body)
        out.append(f'<svg data-pose="{pose}" viewBox="0 0 300 330">{body}{eyes_g}{brow_g}</svg>')
    return "".join(out)


def bookmark_svg():
    return ('<svg class="bm" data-in="{t}" data-k="pop" data-d="0.4" viewBox="0 0 160 170">'
            '<path d="M22 8 h116 a12 12 0 0 1 12 12 v142 l-70 -42 l-70 42 v-142 a12 12 0 0 1 12 -12z" fill="#f6df4b" stroke="#12244a" stroke-width="8" stroke-linejoin="round"/>'
            '<path d="M52 58 l20 20 l38 -40" stroke="#12244a" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def end_icon(kind):
    c = RED if kind == "x" else "#1f9d55"
    mark = ('<path d="M24 24 L48 48 M48 24 L24 48" stroke="#fff" stroke-width="8" stroke-linecap="round"/>' if kind == "x" else
            '<path d="M20 37 L31 48 L52 25" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return f'<svg class="end" viewBox="0 0 72 72"><circle cx="36" cy="36" r="34" fill="{c}"/>{mark}</svg>'


def block_html(i, sc, words, scenes, spec):
    b, s0 = sc["block"], scenes[i]["s"]
    k = b["kind"]
    if k == "notif":
        pt = max(1.5, word_time(words, i, b.get("promise_at"), s0))
        return (f'<div class="card notif" data-in="-1" data-k="drop" data-d="0.4"><img src="{icon_uri("🏦")}">'
                f'<div><div class="lb">{typo(b["label"])}</div><div class="amt">+0,00&nbsp;$</div></div></div>'
                f'<div class="stamp" data-in="0.9" data-k="stamp" data-d="0.25" data-b="rotate(-8deg)">{b["stamp"]}</div>'
                f'<div class="promise" data-in="{pt:.2f}" data-k="pop" data-d="0.35">{typo(b["promise"])} <span class="ar">→</span></div>')
    if k == "stat":
        a = s0 + 0.35
        vt = word_time(words, i, b.get("value_at"), s0)
        pt = word_time(words, i, b.get("pill_at"), s0)
        return (f'<div class="stat" data-in="{a:.2f}" data-k="up"><img src="{icon_uri(b["icon"])}"><div class="lb">{typo(b["label"])}</div>'
                f'<div class="val" data-in="{vt:.2f}" data-k="pop" data-d="0.35">{b["value"]}</div></div>'
                f'<div class="kpill" data-in="{pt:.2f}" data-k="pop" data-d="0.35"' + (f' data-pulse="{word_time(words, i, b["pill_pulse_at"], s0) + 0.1:.2f}"' if b.get("pill_pulse_at") else "") + f'>{typo(b["pill"])}</div>')
    if k == "rows":
        out, prev = [], s0
        for it in b["items"]:
            t = word_time(words, i, it["at"], prev); prev = t
            cls = "row " + ("x " if it.get("end") == "x" else "") + ("warn " if it.get("tone") == "warn" else "") + ("small" if it.get("small") else "")
            end = end_icon(it["end"]) if it.get("end") else ""
            pl = f' data-pulse="{word_time(words, i, it["pulse_at"], s0) + 0.1:.2f}"' if it.get("pulse_at") else ""
            out.append(f'<div class="{cls}" data-in="{t:.2f}" data-k="left" data-ghost="{s0 + 0.35:.2f}"{pl}><img src="{icon_uri(it["icon"])}"><div class="tx">{typo(it["text"])}</div>{end}</div>')
        return f'<div class="rows">{"".join(out)}</div>'
    if k == "cards":
        cards = []
        for j, it in enumerate(b["items"]):
            t = word_time(words, i, it["at"], s0) + 0.12 * j
            cards.append(f'<div class="cd c-{it["color"]}" data-in="{t:.2f}" data-k="up" data-ghost="{s0 + 0.35:.2f}"><img src="{icon_uri(it["icon"])}"><div class="tx">{typo(it["text"])}</div></div>')
        bt = word_time(words, i, b["banner"]["at"], s0)
        return f'<div class="cards">{"".join(cards)}</div><div class="banner" data-in="{bt:.2f}" data-k="pop" data-d="0.35">{typo(b["banner"]["text"])}</div>'
    if k == "end":
        a = s0 + 0.3
        return (f'<div class="endb">{bookmark_svg().replace("{t}", f"{a:.2f}")}'
                f'<div class="q" data-in="{a + 0.9:.2f}" data-k="pop" data-d="0.35">{b["question"].replace(" ? ", " ?<br>").replace("OUI / NON", "<b>OUI / NON</b>")}</div>'
                f'<div class="elogo" data-in="{a + 2.4:.2f}" data-k="up"><div class="lg"><div class="fhc">FHC{LEAF}</div><div class="sep"></div>'
                f'<div class="ln">FINANCE<br><span class="g">HALAL</span><br>CANADA</div></div>'
                f'<div class="tag">ÉPARGNER · INVESTIR · BÂTIR · UN AVENIR HALAL</div></div></div>')
    raise ValueError(k)


def chunks_for(words, spec, scenes):
    kw = {norm(k) for k in spec.get("keywords", [])}
    disp = {norm(k): v for k, v in spec.get("display", {}).items()}
    out = []
    for i, sc in enumerate(spec["scenes"]):
        ws = [w for w in words if w["scene"] == i]
        phrase = []
        for j, w in enumerate(ws):
            phrase.append(w)
            if re.search(r"[,.:;?!…]$", w["w"].replace("\u00a0", "")) or j == len(ws) - 1:
                L = len(" ".join(x["w"] for x in phrase))
                k = max(math.ceil(L / 30), math.ceil(len(phrase) / 5), 1)
                size = math.ceil(len(phrase) / k)
                for a in range(0, len(phrase), size):
                    out.append(phrase[a:a + size])
                phrase = []
    res, prev_w = [], {}
    flat = [w for c in out for w in c]
    for a, b in zip(flat, flat[1:]):
        prev_w[id(b)] = a["w"]
    for n, c in enumerate(out):
        sc_e = scenes[c[0]["scene"]]["e"] if c[0]["scene"] < len(scenes) - 1 else scenes[-1]["e"] - LOOP + 0.18
        nxt_a = out[n + 1][0]["s"] - 0.05 if n + 1 < len(out) and out[n + 1][0]["scene"] == c[0]["scene"] else sc_e - 0.18
        res.append({"a": round(c[0]["s"] - 0.05, 3), "b": round(min(nxt_a, c[-1]["e"] + 0.6, sc_e - 0.18), 3),
                    "w": [{"d": display_word(w["w"], c[j - 1]["w"] if j else prev_w.get(id(w)), disp), "s": w["s"], "e": w["e"],
                          "k": norm(w["w"]) in kw} for j, w in enumerate(c)]})
    return res


def build_html(spec, scenes, words, T):
    n = len(spec["scenes"])
    steps_total = max([sc.get("step", 0) for sc in spec["scenes"]] + [0])
    ttl, pills, contents, poses = [], [], [], []
    for i, sc in enumerate(spec["scenes"]):
        s, e = scenes[i]["s"], scenes[i]["e"]
        out = e if i < n - 1 else T - LOOP
        m = re.search(r"<mark>(.*?)</mark>", sc["title"])
        pulse = word_time(words, i, re.sub(r"&[^;]+;|[^\w'’-]", " ", m.group(1)).split()[0], s) + 0.1 if m else None
        cls = "ttl hook" if sc["type"] == "hook" else "ttl"
        pa = f' data-pulse="{pulse:.2f}"' if pulse else ""
        ttl.append(f'<div class="{cls}" data-in="{s if i else 0:.2f}" data-out="{out:.2f}"{pa}><div class="t">{typo(sc["title"])}</div></div>')
        if sc.get("step"):
            bars = "".join(f'<i class="{"f" if k < sc["step"] else ""}"></i>' for k in range(steps_total))
            pills.append(f'<div class="abs pill" data-in="{s:.2f}" data-out="{e:.2f}">ÉTAPE {sc["step"]} / {steps_total} {bars}</div>')
        cout = e if i < n - 1 else T - LOOP
        contents.append(f'<div class="abs content" data-in="{s:.2f}" data-out="{cout:.2f}">{block_html(i, sc, words, scenes, spec)}</div>')
        for at, pz in sc.get("poses", [[0, "think"]]):
            t = s + at if isinstance(at, (int, float)) else word_time(words, i, at, s)
            poses.append([round(t, 3), pz])
    # boucle : la notification d'ouverture (à +0,00 $) revient sur les 0,15 dernières secondes
    nb = next((sc["block"] for sc in spec["scenes"] if sc["block"]["kind"] == "notif"), None)
    if nb:
        contents.append(f'<div class="abs content" data-in="{T - 0.15:.3f}" data-out="{T + 1:.2f}"><div class="card notif" data-in="-1" data-k="fade">'
                        f'<img src="{icon_uri("🏦")}"><div><div class="lb">{typo(nb["label"])}</div><div class="amt0">+0,00&nbsp;$</div></div></div></div>')
    # boucle : le titre d'ouverture revient pendant les 0,4 dernières secondes
    hook = spec["scenes"][0]
    ttl.append(f'<div class="ttl hook" data-in="{T - LOOP:.3f}" data-out="{T + 1:.2f}"><div class="t">{typo(hook["title"])}</div></div>')
    end_i = n - 1
    data = {"scenes": scenes, "T": T, "loop": LOOP, "cuts": [sc["s"] for sc in scenes[1:]] + [round(T - LOOP, 3)],
            "chunks": chunks_for(words, spec, scenes), "poses": poses,
            "disc": [scenes[end_i]["s"] + 0.3, T - LOOP], "flogo_off": scenes[end_i]["s"] + 0.3 + 2.4,
            "amount": next((sc["block"].get("amount", 0) for sc in spec["scenes"] if sc["block"]["kind"] == "notif"), 0)}
    disclaimer = spec["scenes"][end_i]["block"].get("disclaimer", "")
    stars = "".join(f'<div class="abs star" style="left:{x}px;top:{y}px"></div>' for x, y in
                    [(90, 90), (300, 160), (520, 70), (650, 200), (880, 120), (980, 260), (180, 230), (760, 40)])
    css = (CSS.replace("FONTS", str(FONTS)).replace("NAVY", NAVY).replace("RED", RED).replace("Y;", Y + ";").replace("Y}", Y + "}")
           .replace(":Y", ":" + Y).replace(" G}", " " + G + "}").replace("color:G", "color:" + G))
    clip = jagged(790, 350, 3)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
<div id="world">
 <div class="abs sky"></div>{stars}
 <div class="abs strip">{SC.header_bg("hb").replace('preserveAspectRatio="xMidYMid slice"', 'preserveAspectRatio="xMidYMax slice"')}</div>
 <div class="abs sheet"></div>
 <div class="abs mascot">{mascot_svgs()}</div>
 <div class="abs bubble">?!</div>
 <div class="abs brush" style="clip-path:{clip}"></div>
 {''.join(a.replace('class="ttl', 'class="abs ttl') for a in ttl)}
 {''.join(pills)}
 {''.join(contents)}
 <div class="abs cc"></div>
 <div class="abs disc">{disclaimer}</div>
 <div class="abs foot">{SC.footer_bg("fb")}<div class="abs flogo"><div class="fhc">FHC{LEAF}</div><div class="sep"></div>
  <div class="ln">FINANCE<br><span class="g">HALAL</span><br>CANADA</div></div></div>
 <div class="abs band"></div>
</div>
<script>const DATA={json.dumps(data, ensure_ascii=False)};{JS}</script></body></html>""", data


# ---------------------------------------------------------------- audio
def ding(path):
    expr = "0.55*sin(2*PI*1318.5*t)*exp(-9*t)+0.35*sin(2*PI*1975.5*t)*exp(-11*t)+0.25*sin(2*PI*2637*t)*exp(-14*t)*gt(t\\,0.09)"
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"aevalsrc='{expr}':s=44100:d=0.7", "-af", "afade=t=out:st=0.5:d=0.2",
        "-ac", "2", str(path)])


def mix_audio(spec, clips, T, tmp, out_wav):
    inputs, chains = [], []
    for n, (wav, t) in enumerate(clips):
        inputs += ["-i", str(wav)]
        chains.append(f"[{n}]adelay={int(t * 1000)}:all=1,aresample=44100,aformat=channel_layouts=stereo[v{n}]")
    vm = "".join(f"[v{n}]" for n in range(len(clips)))
    voice = tmp / "voice.wav"
    sh(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
        ";".join(chains) + f";{vm}amix=inputs={len(clips)}:normalize=0,apad,atrim=0:{T},loudnorm=I=-16:TP=-2:LRA=11[o]",
        "-map", "[o]", "-ar", "44100", str(voice)])
    bg = tmp / "bg.wav"
    sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(spec.get("music_start", 0)), "-i", spec["music"], "-t", str(T), "-af",
        f"loudnorm=I=-22:TP=-4:LRA=7,afade=t=in:st=0:d=0.3,afade=t=out:st={T - 0.3:.2f}:d=0.3,aresample=44100,aformat=channel_layouts=stereo",
        str(bg)])
    dg = tmp / "ding.wav"; ding(dg)
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", str(voice), "-i", str(bg), "-i", str(dg), "-filter_complex",
        "[0]asplit=2[vo][sc];[1][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[bgd];"
        "[2]adelay=100:all=1,volume=0.35[dg];[vo][bgd][dg]amix=inputs=3:normalize=0:duration=first,"
        f"loudnorm=I=-14:TP=-1.5:LRA=9,aresample=44100,apad=whole_dur={T},atrim=0:{T}[o]", "-map", "[o]", str(out_wav)])
    return voice


# ---------------------------------------------------------------- rendu
def render(spec_path, out_dir=None, preview=False, qa=True):
    from playwright.sync_api import sync_playwright
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    slug = spec["slug"]
    out = Path(out_dir or f"/home/claude/reel/{slug}")
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "work"; tmp.mkdir(exist_ok=True)
    scenes, words, clips, T = build_timeline(spec, tmp)
    html, data = build_html(spec, scenes, words, T)
    hp = tmp / "reel.html"; hp.write_text(html, encoding="utf-8")
    (out / "timeline.json").write_text(json.dumps({"T": T, "scenes": scenes, "words": words, "data": data}, ensure_ascii=False, indent=1))
    print(f"durée {T:.2f} s, scènes : " + ", ".join(f"{s['e'] - s['s']:.2f}" for s in scenes), flush=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(f"file://{hp}"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        if preview:
            pts = [0.0, 1.2, 2.2] + [s["s"] + (s["e"] - s["s"]) * 0.85 for s in scenes[1:]] + [scenes[1]["s"], T - 0.2]
            for k, t in enumerate(pts):
                pg.evaluate(f"T({t})"); pg.screenshot(path=str(out / f"prev_{k:02d}_{t:05.2f}.jpg"), type="jpeg", quality=85)
            b.close(); return out
        files = []
        for i, s in enumerate(scenes):
            f0, f1 = round(s["s"] * FPS), round(s["e"] * FPS)
            name, tmpf = out / f"scene{i + 1}.mp4", out / f"scene{i + 1}.tmp.mp4"
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg",
                                   "-i", "-", "-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                                   "-pix_fmt", "yuv420p", "-r", str(FPS), str(tmpf)], stdin=subprocess.PIPE)
            for fr in range(f0, f1):
                pg.evaluate(f"T({fr / FPS})")
                ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
            ff.stdin.close()
            if ff.wait() != 0: sys.exit(f"scène {i + 1} en échec")
            os.replace(tmpf, name); files.append(name); print("ok", name.name, flush=True)
        qa_dom = qa_layout(pg, data, T) if qa else None
        b.close()
    lst = tmp / "list.txt"; lst.write_text("".join(f"file '{f}'\n" for f in files))
    vid = tmp / "video_only.mp4"
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vid)])
    mix = tmp / "mix.wav"; mix_audio(spec, clips, T, tmp, mix)
    final = out / f"FHC_reel_{slug}.mp4"
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vid), "-i", str(mix), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", f"apad=whole_dur={T}", "-c:a", "aac",
        "-b:a", "192k", "-t", f"{round(T * FPS) / FPS:.3f}", "-movflags", "+faststart", str(final)])
    if qa:
        report = qa_report(final, T, data, qa_dom)
        (out / "qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
        print(json.dumps(report["summary"], ensure_ascii=False, indent=1))
    return final


# ---------------------------------------------------------------- contrôles qualité
def qa_layout(pg, data, T):
    """Zones sûres, tailles mini, débordements : on échantillonne toutes les 0,25 s."""
    issues, seen = [], set()
    js = r"""()=>{const out=[];
     document.querySelectorAll('.ttl .t,.ttl mark,.pill,.cc span,.disc,.content *,.bubble').forEach(el=>{
       const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden')return;
       let o=1,p=el; while(p&&p!==document.body){o*=+getComputedStyle(p).opacity; if(getComputedStyle(p).display==='none')return; p=p.parentElement;}
       if(o<0.6)return; if(el.dataset&&el.dataset.in&&+el.dataset.in>window.__t-0.45)return;
       const own=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());
       if(!own)return; const r=el.getBoundingClientRect();
       out.push({cls:el.className.baseVal!==undefined?'svg':el.className,txt:el.textContent.trim().slice(0,30),
         fs:parseFloat(cs.fontSize),x0:r.left,y0:r.top,x1:r.right,y1:r.bottom,
         over:el.scrollWidth>el.clientWidth+2&&cs.overflow!=='visible'});});
     return out;}"""
    small_ok = ("pill", "disc", "tag", "ln", "lb", "g")
    t = 0.0
    while t < T:
        pg.evaluate(f"window.__t={t};T({t})")
        for e in pg.evaluate(js):
            key = (e["txt"], e["cls"])
            prob = []
            if e["y0"] < 250: prob.append("haut <250")
            if e["x1"] > 942 and e["y1"] > 1000 and e["y0"] < 1800: prob.append("colonne droite")
            if e["y1"] > 1540 and "foot" not in e["cls"]: prob.append("sous y1540")
            if e["fs"] < 40 and not any(s in str(e["cls"]) for s in small_ok): prob.append(f"police {e['fs']:.0f}px")
            if prob and key not in seen:
                seen.add(key); issues.append({"t": round(t, 2), "txt": e["txt"], "cls": e["cls"], "pb": prob,
                                              "box": [round(e["x0"]), round(e["y0"]), round(e["x1"]), round(e["y1"])]})
        t += 0.25
    return issues


def qa_report(final, T, data, dom):
    info = json.loads(sh(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate:format=duration",
                          "-of", "json", str(final)]).stdout)
    # mouvement : plus longue plage figée
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(final), "-vf", "scale=108:192,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    n = 108 * 192
    fr = [raw[i:i + n] for i in range(0, len(raw) - n + 1, n)]
    still, longest, start, spans = 0, 0, 0, []
    for i in range(1, len(fr)):
        diff = sum(abs(a - b) for a, b in zip(fr[i][::5], fr[i - 1][::5])) / (n / 5)
        if diff < 0.35:
            still += 1
        else:
            if still / FPS > 1.0: spans.append((round(start / FPS, 2), round(i / FPS, 2)))
            longest = max(longest, still); still = 0; start = i
    longest = max(longest, still)
    ebur = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(final), "-af", "ebur128=peak=true", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", ebur)[-1]); TP = float(re.findall(r"Peak:\s+(-?[0-9.]+) dBFS", ebur)[-1])
    sil = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(final), "-af", "silencedetect=n=-45dB:d=0.3", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summary = {
        "durée_s": round(float(info["format"]["duration"]), 2),
        "flux": [f'{s["codec_name"]} {s.get("width", "")}x{s.get("height", "")} {s["r_frame_rate"]}' for s in info["streams"]],
        "plus_longue_image_figée_s": round(longest / FPS, 2),
        "plages_figées_>1s": spans,
        "loudness_LUFS": I, "true_peak_dBFS": TP,
        "silences_>0.3s": len(re.findall("silence_start", sil)),
        "problèmes_mise_en_page": len(dom or []),
    }
    return {"summary": summary, "layout": dom}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args: sys.exit(__doc__)
    render(args[0], args[1] if len(args) > 1 else None, preview="--preview" in sys.argv, qa="--no-qa" not in sys.argv)
