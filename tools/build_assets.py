#!/usr/bin/env python3
"""
build_assets.py — genera TODOS los SVG del README de perfil de github.com/viajatech.   (v2 · 2026-10-12)

Diseño "OBSIDIAN FORGE · el núcleo de viajatech.com": obsidiana + oro fundido + una brasa ámbar (NUNCA cian/teal/azul
neón, ni circuitos/cerebros/binario/hexágonos: reglas de marca de David). La portada de viajatech.com es un núcleo con siete
satélites (uno por sección, cada uno con su color) y un cometa que baja hasta la marca; este banner es la misma idea en
SVG: núcleo, órbita con los ocho satélites, una sinapsis que recorre cada satélite y el cometa que aterriza en viajatech.com.

Tipografía "Forja", la del sitio (D-019 de viajatech-web): Unbounded (display), Space Grotesk (texto), JetBrains Mono
(datos), todas SIL OFL. El texto se convierte a TRAZOS con HarfBuzz → se ve idéntico en cualquier dispositivo y no depende
de fuentes instaladas ni de CSP. Animaciones SMIL (funcionan dentro de <img> en GitHub; CSS y JS no).

Uso:     python3 tools/build_assets.py            (requiere: pip install --user fonttools brotli uharfbuzz)
Fuentes: tools/fonts/ (ignorada por git) = copia de viajatech-web/public/fonts: unbounded-latin.woff2,
         space-grotesk-latin.woff2, jetbrains-mono-latin.woff2 y sus licencias. Otra carpeta: JT_FONTS=<ruta>.
Salida:  assets/*.svg — textos, colores, satélites y botones se editan aquí arriba y se vuelve a correr. Build determinista.
"""
import io
import math
import os
import sys

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
FONT_DIR = os.environ.get("JT_FONTS", os.path.join(ROOT, "tools", "fonts"))

# ── Paleta OBSIDIAN FORGE (la de viajatech.com, DESIGN.md §2) ───────────────────────────────────
OBS0, OBS1 = "#060607", "#0E0D0B"          # obsidiana
GOLD, GOLD_HI, GOLD_DEEP = "#D8B15F", "#F0D890", "#9C7A33"
EMBER = "#FF7A1A"                           # brasa (con moderación)
IVORY, WARM, DIM = "#F2EDE4", "#8A8478", "#4A463F"
L_GOLD, L_INK, L_WARM = "#8A6420", "#1F1B14", "#6B645A"   # tema CLARO de GitHub (encabezados y pie)
# Los ocho satélites de viajatech.com con su color propio (shared/satellites.ts → ACCENTS). Orden de la órbita.
SATELLITES = [
    ("isabella", "#8B5CF6"),   # violeta: solo Isabella
    ("sitios", "#5B9DFF"),     # azul eléctrico (D-050 bis; antes oro, idéntico al orbe)
    ("mundos", "#4ADE80"),     # verde vida: Mundos (viajatech.com/mundos, D-049)
    ("tienda", "#FF7A1A"),     # brasa
    ("codigo", "#B8C4D6"),     # acero
    ("stories", "#F472B6"),    # rosa
    ("perfil", "#FFFFFF"),     # blanco: en el sitio Perfil es el eclipse del orbe (corona blanca; D-050)
    ("canales", "#FBBF24"),    # ámbar
]

# ── Textos (editar aquí) ─────────────────────────────────────────────────────────────────────────
NAME = "David Ruiz"
HANDLE = "@viajatech"
LABEL = "/ 001 — VIAJATECH.COM"
HEADLINE = "CREATIVE TECHNOLOGIST · CREATOR OF WORLDS · AI · MARKETING · WEB"
PROMPT = "$ whoami"
MANIFESTO = "one human. an army of AIs. zero limits."
STATUS = "LIVE — MEXICO CITY"
DOMAIN = "viajatech.com"

SECTIONS = {  # archivo → (número, título)
    "ship": ("002", "WHAT I SHIP"),
    "live": ("003", "LIVE — PROOF OF WORK"),
    "stack": ("004", "STACK"),
    "repos": ("005", "SIGNATURE REPOS"),
    "books": ("006", "BOOKS"),
    "agents": ("007", "FOR AI AGENTS"),
    "connect": ("008", "CONNECT"),
}
BUTTONS = {  # archivo → etiqueta
    "viajatech": "VIAJATECH.COM",
    "viajatech-xyz": "VIAJATECH.XYZ",
    "jettrendy": "JETTRENDY.COM",
    "email": "EMAIL",
    "youtube": "YOUTUBE",
    "instagram": "INSTAGRAM",
    "tiktok": "TIKTOK",
    "x": "X",
    "threads": "THREADS",
    "facebook": "FACEBOOK",
}


# ── Tipografía → trazos ──────────────────────────────────────────────────────────────────────────
class Face:
    def __init__(self, filename, wght=None):
        tt = TTFont(os.path.join(FONT_DIR, filename))
        if wght is not None and "fvar" in tt:
            tt = instantiateVariableFont(tt, {"wght": wght})
        tt.flavor = None
        buf = io.BytesIO()
        tt.save(buf)
        self.data = buf.getvalue()
        self.tt = TTFont(io.BytesIO(self.data))
        self.upem = self.tt["head"].unitsPerEm
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.hb = hb.Font(hb.Face(self.data))

    def run(self, text, size, x, y, tracking=0.0):
        """(d, ancho, [x de cada carácter]) — tracking en em; y = línea base."""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": False})
        s = size / self.upem
        pen, parts, xs = 0.0, [], []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            xs.append(x + pen * s)
            sp = SVGPathPen(self.gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
            tp = TransformPen(sp, (s, 0, 0, -s, x + (pen + pos.x_offset) * s, y - pos.y_offset * s))
            self.gs[self.order[info.codepoint]].draw(tp)
            d = sp.getCommands()
            if d:
                parts.append(d)
            pen += pos.x_advance + tracking * self.upem
        width = (pen - tracking * self.upem) * s if buf.glyph_infos else 0.0
        xs.append(x + width)
        return " ".join(parts), width, xs


try:
    DISPLAY = Face("unbounded-latin.woff2", wght=600)      # nombre
    SANS = Face("space-grotesk-latin.woff2", wght=500)     # handle, texto
    MONO = Face("jetbrains-mono-latin.woff2", wght=400)    # prompt, manifiesto, pie
    MONO_MED = Face("jetbrains-mono-latin.woff2", wght=500)  # etiquetas, botones
except Exception as e:  # noqa: BLE001
    sys.exit(f"No pude cargar las fuentes de {FONT_DIR}: {e}\n(copia tools/fonts/ desde viajatech-web/public/fonts o define JT_FONTS)")


def text_path(face, text, size, x, y, fill, tracking=0.0, opacity=None, extra=""):
    d, w, _ = face.run(text, size, x, y, tracking)
    op = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return f'<path d="{d}" fill="{fill}"{op}{extra}/>', w


def f1(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def write(name, svg):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  {name:<28} {len(svg.encode()) / 1024:6.1f} KB")


def window(k, n, fade=0.012):
    """Ventana [k/n, (k+1)/n) de un ciclo, como lista (keyTime, valor 0/1) con fundidos; sin keyTimes repetidos."""
    a, b = k / n, (k + 1) / n
    pts = [(0.0, 0), (a, 0), (min(a + fade, b), 1), (max(b - fade, a), 1), (b, 0), (1.0, 0)]
    out = []
    for t, v in pts:
        t = min(max(t, 0.0), 1.0)
        if out and t <= out[-1][0]:
            if v != out[-1][1] and t == out[-1][0]:
                out[-1] = (t, v)
            continue
        out.append((t, v))
    if out[-1][0] < 1.0:
        out.append((1.0, out[-1][1]))
    return out


def anim(attr, pts, lo, hi, dur, extra=""):
    """<animate> lineal: cada valor 0/1 de la ventana se escala a lo..hi."""
    kt = ";".join("%.4f" % t for t, _ in pts)
    vals = ";".join(f1(lo + (hi - lo) * v) for _, v in pts)
    return f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"{extra}/>'


# ── HERO (banner animado 1280×480): el núcleo, sus satélites, la sinapsis y el cometa ───────────
def hero():
    W, H = 1280, 480
    cx, cy = 1012, 214  # centro del núcleo
    R = 98
    lx = 66
    label, _ = text_path(MONO_MED, LABEL, 13, lx, 84, WARM, tracking=0.32)
    # el nombre en Unbounded: se encoge si no cabe antes del núcleo
    size = 92
    while True:
        _, nw, _ = DISPLAY.run(NAME, size, lx - 4, 196)
        if nw <= cx - R - 70 - lx or size <= 64:
            break
        size -= 2
    name, _ = text_path(DISPLAY, NAME, size, lx - 4, 196, IVORY, tracking=-0.015)
    handle, _ = text_path(SANS, HANDLE, 40, lx - 1, 252, GOLD, opacity=0.92)
    headline, _ = text_path(MONO_MED, HEADLINE, 13, lx, 320, GOLD, tracking=0.2)
    prompt, pw = text_path(MONO, PROMPT, 21, lx, 376, WARM)
    mx = lx + pw + 16
    md, mw, mxs = MONO.run(MANIFESTO, 21, mx, 376)
    status, _ = text_path(MONO_MED, STATUS, 12, lx + 22, 451, WARM, tracking=0.3)
    _, dom_w, _ = MONO_MED.run(DOMAIN, 12, 0, 451, 0.3)
    domain, _ = text_path(MONO_MED, DOMAIN, 12, cx - dom_w / 2, 451, GOLD, tracking=0.3, opacity=0.9)

    # tecleo del manifiesto: el clip crece carácter por carácter y el cursor lo sigue
    n = len(MANIFESTO)
    widths = [mxs[i] - mx for i in range(n + 1)]
    wvals = ";".join(f1(w) for w in widths)
    cvals = ";".join(f1(mx + w + 3) for w in widths)
    kt = ";".join("%.4f" % (i / n) for i in range(n + 1))
    type_dur, type_begin = 2.6, 1.0

    # ── órbita con los ocho satélites (como en la portada de viajatech.com) ──
    rx, ry, rot = 236, 76, -14
    T, N, S = 26.0, 88, len(SATELLITES)          # periodo, muestras por vuelta (88 = múltiplo de 8)
    pts = [(rx * math.cos(2 * math.pi * i / N), ry * math.sin(2 * math.pi * i / N)) for i in range(N)]
    ring = f'M {-rx} 0 A {rx} {ry} 0 1 1 {rx} 0 A {rx} {ry} 0 1 1 {-rx} 0'
    back, front = [], []
    back.append(f'<path d="{ring}" fill="none" stroke="{GOLD}" stroke-opacity="0.22" stroke-width="1" stroke-dasharray="2 7"/>')
    front.append(f'<path d="M {-rx} 0 A {rx} {ry} 0 0 0 {rx} 0" fill="none" stroke="{GOLD}" stroke-opacity="0.34" stroke-width="1" stroke-dasharray="2 7"/>')
    for k, (sid, col) in enumerate(SATELLITES):
        off = k * N // S
        xs = [pts[(i + off) % N][0] for i in range(N + 1)]
        ys = [pts[(i + off) % N][1] for i in range(N + 1)]
        xv, yv = ";".join(f1(v) for v in xs), ";".join(f1(v) for v in ys)
        move = (f'<animate attributeName="{{a}}" values="{{v}}" dur="{T}s" repeatCount="indefinite" calcMode="linear"/>')
        mv_c = move.format(a="cx", v=xv) + move.format(a="cy", v=yv)
        mv_l = move.format(a="x2", v=xv) + move.format(a="y2", v=yv)
        win = window(k, S)
        # sinapsis: hilo del núcleo al satélite, solo en su ventana; las rayas corren hacia el satélite (el impulso)
        thread = (f'<line x1="0" y1="0" x2="{f1(xs[0])}" y2="{f1(ys[0])}" stroke="{col}" stroke-width="1.7" stroke-linecap="round" '
                  f'stroke-dasharray="5 15" stroke-opacity="0">{mv_l}{anim("stroke-opacity", win, 0, 0.9, T)}'
                  f'<animate attributeName="stroke-dashoffset" from="20" to="0" dur="0.7s" repeatCount="indefinite"/></line>')
        glow = (f'<circle r="16" fill="{col}" opacity="0" filter="url(#soft)">{mv_c}{anim("opacity", win, 0, 0.5, T)}</circle>')
        node = (f'<circle r="5" fill="{col}">{mv_c}{anim("r", win, 5, 7.4, T)}</circle>')
        halo = f'<circle r="11" fill="{col}" opacity="0.2" filter="url(#soft)">{mv_c}</circle>'
        piece = thread + halo + glow + node
        back.append(piece)
        front.append(f'<g clip-path="url(#lower)">{piece}</g>')  # mitad delantera, encima de la esfera

    # ── el cometa (Acto I): nace del vientre del núcleo, baja por el hilo y aterriza en viajatech.com ──
    C, hy0, hy1 = 7.5, cy + R + 8, 406   # ciclo, inicio y fin del viaje
    comet = (
        f'<line x1="{cx}" y1="{hy0}" x2="{cx}" y2="{hy1}" stroke="{GOLD}" stroke-width="1" stroke-dasharray="1 5" stroke-opacity="0.4">'
        f'<animate attributeName="stroke-opacity" values="0.4;0.4;1;0.4;0.4" keyTimes="0;0.02;0.27;0.42;1" dur="{C}s" repeatCount="indefinite"/></line>'
        f'<ellipse cx="{cx}" cy="{hy1 + 3}" rx="70" ry="5" fill="{EMBER}" opacity="0" filter="url(#soft)">'
        f'<animate attributeName="opacity" values="0;0;0.85;0;0" keyTimes="0;0.27;0.3;0.55;1" dur="{C}s" repeatCount="indefinite"/></ellipse>'
        f'<circle cx="{cx}" cy="{hy1}" r="0" fill="none" stroke="{GOLD_HI}" stroke-width="1.6" opacity="0">'
        f'<animate attributeName="r" values="0;0;34;34" keyTimes="0;0.27;0.46;1" dur="{C}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;0;0.9;0;0" keyTimes="0;0.27;0.28;0.46;1" dur="{C}s" repeatCount="indefinite"/></circle>'
        f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.04;0.25;0.28;1" dur="{C}s" repeatCount="indefinite"/>'
        f'<line x1="{cx}" y1="{hy0}" x2="{cx}" y2="{hy0 - 26}" stroke="{GOLD_HI}" stroke-width="2.4" stroke-linecap="round" stroke-opacity="0.75">'
        f'<animate attributeName="y1" values="{hy0};{hy1};{hy1}" keyTimes="0;0.27;1" dur="{C}s" repeatCount="indefinite"/>'
        f'<animate attributeName="y2" values="{hy0 - 8};{hy1 - 34};{hy1 - 34}" keyTimes="0;0.27;1" dur="{C}s" repeatCount="indefinite"/></line>'
        f'<circle cx="{cx}" cy="{hy0}" r="9" fill="{EMBER}" opacity="0.45" filter="url(#soft)"><animate attributeName="cy" values="{hy0};{hy1};{hy1}" keyTimes="0;0.27;1" dur="{C}s" repeatCount="indefinite"/></circle>'
        f'<circle cx="{cx}" cy="{hy0}" r="3.4" fill="{GOLD_HI}"><animate attributeName="cy" values="{hy0};{hy1};{hy1}" keyTimes="0;0.27;1" dur="{C}s" repeatCount="indefinite"/>'
        f'<animate attributeName="r" values="2.2;3.8;3.8" keyTimes="0;0.27;1" dur="{C}s" repeatCount="indefinite"/></circle></g>'
    )

    # chispas de forja que suben del horizonte (brasas)
    sparks = []
    for j, (x, rise, dur, beg, r, col) in enumerate([
        (700, 70, 6.5, 0.0, 1.6, EMBER), (790, 118, 8.0, 2.1, 1.2, GOLD_HI), (880, 92, 7.2, 4.0, 1.8, EMBER),
        (1120, 128, 8.6, 5.1, 1.2, GOLD_HI), (1205, 84, 6.8, 2.7, 1.5, EMBER),
    ]):
        sparks.append(
            f'<circle cx="{x}" cy="408" r="{r}" fill="{col}" opacity="0">'
            f'<animate attributeName="cy" values="408;{408 - rise}" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cx" values="{x};{x + (9 if j % 2 else -9)};{x}" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.9;0.5;0" keyTimes="0;0.2;0.7;1" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
            f'</circle>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{NAME} — {HANDLE} — Creative Technologist · AI in production · Digital marketing · Web — {MANIFESTO}">
<title>{NAME} — {HANDLE} — viajatech.com</title>
<defs>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <radialGradient id="forge" cx="0.74" cy="1.08" r="0.78">
    <stop offset="0" stop-color="{GOLD}" stop-opacity="0.26"/>
    <stop offset="0.35" stop-color="{EMBER}" stop-opacity="0.07"/>
    <stop offset="1" stop-color="{OBS0}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{GOLD}" stop-opacity="0.30"/>
    <stop offset="0.55" stop-color="{GOLD}" stop-opacity="0.07"/>
    <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="sphere" cx="0.36" cy="0.30" r="0.78">
    <stop offset="0" stop-color="#3a3322"/>
    <stop offset="0.42" stop-color="#15120c"/>
    <stop offset="0.74" stop-color="#070604"/>
    <stop offset="1" stop-color="#000"/>
  </radialGradient>
  <radialGradient id="spec" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#FFF4D6" stop-opacity="0.62"/>
    <stop offset="1" stop-color="#FFF4D6" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="bezel" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{GOLD_HI}"/>
    <stop offset="0.5" stop-color="{GOLD}"/>
    <stop offset="1" stop-color="{GOLD_DEEP}"/>
  </linearGradient>
  <linearGradient id="horizon" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{GOLD}" stop-opacity="0"/>
    <stop offset="0.35" stop-color="{GOLD}" stop-opacity="0.55"/>
    <stop offset="0.55" stop-color="{EMBER}" stop-opacity="0.75"/>
    <stop offset="0.75" stop-color="{GOLD_HI}" stop-opacity="0.55"/>
    <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-0.35 0;0.35 0;-0.35 0" dur="9s" repeatCount="indefinite"/>
  </linearGradient>
  <clipPath id="lower"><rect x="-340" y="0" width="680" height="200"/></clipPath>
  <filter id="soft" x="-2" y="-2" width="5" height="5"><feGaussianBlur stdDeviation="3"/></filter>
  <filter id="blur1"><feGaussianBlur stdDeviation="0.8"/></filter>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.94  0 0 0 0 0.85  0 0 0 0 0.62  0 0 0 0.06 0"/>
  </filter>
  <clipPath id="typeclip"><rect x="{mx}" y="348" height="40" width="0">
    <animate attributeName="width" values="{wvals}" keyTimes="{kt}" calcMode="discrete" dur="{type_dur}s" begin="{type_begin}s" fill="freeze"/>
  </rect></clipPath>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{OBS0}"/>
  <rect width="{W}" height="{H}" fill="url(#forge)"/>
  <rect width="{W}" height="{H}" filter="url(#grain)"/>
  <rect x="0" y="409" width="{W}" height="1.4" fill="url(#horizon)"/>
  <rect x="0" y="410" width="{W}" height="18" fill="url(#horizon)" opacity="0.10" filter="url(#soft)"/>
  {comet}

  <g transform="translate({cx} {cy})">
    <circle r="190" fill="url(#halo)"><animate attributeName="opacity" values="0.65;1;0.65" dur="4.5s" repeatCount="indefinite"/></circle>
    <g transform="rotate({rot})">{"".join(back)}</g>
    <circle r="{R}" fill="url(#sphere)"/>
    <circle r="{R - 1}" fill="none" stroke="{GOLD}" stroke-opacity="0.22"/>
    <g><circle r="{R + 3}" fill="none" stroke="url(#bezel)" stroke-width="3.2" stroke-linecap="round" stroke-dasharray="52 16 118 30 64 22 90 44" opacity="0.92"/>
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="9s" repeatCount="indefinite"/></g>
    <g><circle r="{R + 11}" fill="none" stroke="{GOLD}" stroke-opacity="0.35" stroke-width="0.8" stroke-dasharray="1 9"/>
      <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="31s" repeatCount="indefinite"/></g>
    <ellipse cx="-32" cy="-44" rx="30" ry="17" fill="url(#spec)" transform="rotate(-24 -32 -44)" filter="url(#blur1)"/>
    <g transform="rotate({rot})">{"".join(front)}</g>
  </g>
  {"".join(sparks)}

  {label}
  {name}
  {handle}
  <rect x="{lx}" y="280" width="92" height="1" fill="{GOLD}" opacity="0.5"/>
  {headline}
  {prompt}
  <path d="{md}" fill="{IVORY}" clip-path="url(#typeclip)"/>
  <rect x="{mx + 3}" y="358" width="11" height="23" fill="{GOLD}">
    <animate attributeName="x" values="{cvals}" keyTimes="{kt}" calcMode="discrete" dur="{type_dur}s" begin="{type_begin}s" fill="freeze"/>
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.05s" repeatCount="indefinite"/>
  </rect>

  <circle cx="{lx + 6}" cy="447" r="4" fill="{EMBER}"><animate attributeName="opacity" values="1;0.35;1" dur="2.4s" repeatCount="indefinite"/></circle>
  {status}
  {domain}
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="21.5" fill="none" stroke="{GOLD}" stroke-opacity="0.22"/>
</svg>
'''


def arrow_ne(x, y, s, color, width=1.6):
    """Flecha ↗ dibujada (las fuentes latin no la traen). (x, y) = esquina inferior izquierda."""
    return (f'<path d="M {x} {y} L {x + s} {y - s} M {x + s * 0.35} {y - s} L {x + s} {y - s} L {x + s} {y - s * 0.65}" '
            f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')


# ── Encabezado de sección (560×60, fondo transparente; variante oscura y clara) ─────────────────
def section(num, title, dark=True):
    W, H = 560, 60
    c_num, c_title, c_line = (WARM, GOLD, GOLD) if dark else (L_WARM, L_GOLD, L_GOLD)
    pre, pw = text_path(MONO_MED, f"/ {num} — ", 19, 2, 39, c_num, tracking=0.18)
    ttl, tw = text_path(MONO_MED, title, 19, 2 + pw + 19 * 0.18, 39, c_title, tracking=0.18)
    x0 = min(2 + pw + tw + 30, W - 60)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{num} — {title}">
<title>{title.title()}</title>
<defs><linearGradient id="ln" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{c_line}" stop-opacity="0.7"/><stop offset="1" stop-color="{c_line}" stop-opacity="0"/>
</linearGradient><filter id="g" x="-3" y="-3" width="7" height="7"><feGaussianBlur stdDeviation="2.2"/></filter></defs>
{pre}{ttl}
<rect x="{x0}" y="32.5" width="{W - x0}" height="1" fill="url(#ln)"/>
<circle cx="{x0}" cy="33" r="5" fill="{EMBER if dark else L_GOLD}" opacity="0.35" filter="url(#g)"><animate attributeName="opacity" values="0.15;0.5;0.15" dur="2.8s" repeatCount="indefinite"/></circle>
<circle cx="{x0}" cy="33" r="2.4" fill="{EMBER if dark else L_GOLD}"/>
</svg>
'''


# ── Botones grandes (CTA, 60 px) — oscuros en ambos temas (objeto de marca) ─────────────────────
def cta(label, icon):
    H = 60
    _, lw, _ = MONO_MED.run(label, 14, 0, 0, 0.2)
    W = int(24 + 36 + 14 + lw + 18 + 12 + 26)
    lab, _ = text_path(MONO_MED, label, 14, 74, 35, IVORY, tracking=0.2)
    ax = 74 + lw + 18
    if icon == "orb":  # mini núcleo de Isabella con bisel que gira y rim violeta
        ic = f'''<g transform="translate(42 30)">
  <circle r="17" fill="url(#halo)"/>
  <circle r="11.5" fill="url(#sph)"/>
  <circle r="11.5" fill="none" stroke="#8B5CF6" stroke-opacity="0.55" stroke-width="1"/>
  <g><circle r="13.2" fill="none" stroke="{GOLD}" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="14 5 22 8 12 6"/>
  <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="7s" repeatCount="indefinite"/></g>
  <ellipse cx="-3.5" cy="-4.5" rx="3.6" ry="2" fill="#FFF4D6" opacity="0.55" transform="rotate(-24 -3.5 -4.5)"/>
</g>'''
    elif icon == "wave":  # onda de voz animada (rosa orquídea, el orbe de voz de Isabella)
        bars = []
        for k, (h1, h2, d) in enumerate([(6, 16, 0.9), (10, 24, 1.1), (16, 8, 0.8), (8, 20, 1.0), (5, 13, 1.2)]):
            x = 29 + k * 6.2
            bars.append(f'<rect x="{x:.1f}" y="{30 - h1 / 2}" width="3" height="{h1}" rx="1.5" fill="#F472B6">'
                        f'<animate attributeName="height" values="{h1};{h2};{h1}" dur="{d}s" repeatCount="indefinite"/>'
                        f'<animate attributeName="y" values="{30 - h1 / 2};{30 - h2 / 2};{30 - h1 / 2}" dur="{d}s" repeatCount="indefinite"/></rect>')
        ic = "".join(bars)
    elif icon == "portal":  # portal del taxi entre mundos: anillo verde vida y la chispa que lo cruza (viajatech.com/mundos)
        ic = f'''<g transform="translate(42 30)">
  <circle r="17" fill="url(#halo)"/>
  <ellipse rx="13" ry="7.5" fill="none" stroke="#4ADE80" stroke-width="1.6" stroke-opacity="0.9"/>
  <ellipse rx="8" ry="4.6" fill="none" stroke="#4ADE80" stroke-width="1" stroke-opacity="0.5"/>
  <circle r="2.6" fill="{GOLD_HI}"><animate attributeName="cx" values="-16;0;16" dur="2.2s" repeatCount="indefinite"/><animate attributeName="r" values="1.4;3.2;1.4" dur="2.2s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;0" dur="2.2s" repeatCount="indefinite"/></circle>
</g>'''
    else:  # cometa que aterriza (sitios web para negocios)
        ic = f'''<g transform="translate(42 30)">
  <circle r="16" fill="url(#halo)"/>
  <line x1="-13" y1="-11" x2="4" y2="4" stroke="{GOLD}" stroke-width="2.2" stroke-linecap="round" stroke-opacity="0.75"/>
  <circle cx="4" cy="4" r="4.2" fill="{GOLD_HI}"/>
  <circle cx="4" cy="4" r="4" fill="none" stroke="{GOLD_HI}" stroke-width="1.2" opacity="0">
    <animate attributeName="r" values="4;13" dur="2.4s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.8;0" dur="2.4s" repeatCount="indefinite"/></circle>
</g>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label.title()}">
<title>{label.title()}</title>
<defs>
  <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{GOLD}" stop-opacity="0.35"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>
  <radialGradient id="sph" cx="0.36" cy="0.3" r="0.8"><stop offset="0" stop-color="#3a3322"/><stop offset="0.5" stop-color="#14110b"/><stop offset="1" stop-color="#000"/></radialGradient>
  <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#15130F"/><stop offset="1" stop-color="{OBS0}"/></linearGradient>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{(H - 2) / 2}" fill="url(#fill)" stroke="{GOLD}" stroke-width="1.4"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{(H - 2) / 2}" fill="none" stroke="{GOLD_HI}" stroke-opacity="0.18" stroke-width="5">
  <animate attributeName="stroke-opacity" values="0.06;0.24;0.06" dur="3.2s" repeatCount="indefinite"/></rect>
{ic}
{lab}
{arrow_ne(ax, 36, 10, GOLD, 1.8)}
</svg>
'''


# ── Botones de contacto (altura 40) ─────────────────────────────────────────────────────────────
def button(label):
    H = 40
    _, lw, _ = MONO_MED.run(label, 12, 0, 0, 0.22)
    W = int(20 + lw + 14 + 9 + 18)
    lab, _ = text_path(MONO_MED, label, 12, 20, 24.5, IVORY, tracking=0.22)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
<title>{label}</title>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="{(H - 1.5) / 2}" fill="{OBS1}" stroke="{GOLD}" stroke-opacity="0.6" stroke-width="1"/>
{lab}
{arrow_ne(20 + lw + 14, 25, 8, GOLD, 1.5)}
</svg>
'''


# ── Pie de terminal (560×78, transparente; variante oscura y clara) ─────────────────────────────
def footer(dark=True):
    W, H = 560, 78
    c_prompt, c_cmd, c_sub, c_caret = (GOLD, IVORY, WARM, GOLD) if dark else (L_GOLD, L_INK, L_WARM, L_GOLD)
    pr, pw = text_path(MONO, "guest@viajatech:~$", 18, 2, 30, c_prompt, opacity=0.8)
    cx0 = 2 + pw + 11
    cmd = "join --revolution"
    cd, cw, cxs = MONO.run(cmd, 18, cx0, 30)
    n = len(cmd)
    widths = [cxs[i] - cx0 for i in range(n + 1)]
    kt = ";".join("%.4f" % (i / n) for i in range(n + 1))
    sub, _ = text_path(MONO, "made in mexico city · one human + an army of AIs · viajatech.com", 12.5, 2, 63, c_sub, tracking=0.05)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="guest@viajatech:~$ join --revolution — made in mexico city · viajatech.com">
<title>join --revolution</title>
<defs><clipPath id="t"><rect x="{cx0}" y="10" height="30" width="0">
  <animate attributeName="width" values="{";".join(f1(w) for w in widths)}" keyTimes="{kt}" calcMode="discrete" dur="1.7s" begin="0.8s" fill="freeze"/></rect></clipPath></defs>
{pr}
<path d="{cd}" fill="{c_cmd}" clip-path="url(#t)"/>
<rect x="{cx0 + 2}" y="14" width="10" height="21" fill="{c_caret}">
  <animate attributeName="x" values="{";".join(f1(cx0 + w + 2) for w in widths)}" keyTimes="{kt}" calcMode="discrete" dur="1.7s" begin="0.8s" fill="freeze"/>
  <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.05s" repeatCount="indefinite"/></rect>
{sub}
</svg>
'''


if __name__ == "__main__":
    print(f"fuentes: {FONT_DIR}\nsalida:  {OUT}")
    write("hero.svg", hero())
    for key, (num, title) in SECTIONS.items():
        write(f"sec-{key}-dark.svg", section(num, title, dark=True))
        write(f"sec-{key}-light.svg", section(num, title, dark=False))
    write("cta-chat.svg", cta("CHAT WITH ISABELLA", "orb"))
    write("cta-voice.svg", cta("TALK TO HER · VOICE", "wave"))
    write("cta-sitios.svg", cta("A WEBSITE FOR YOUR BUSINESS", "comet"))
    write("cta-mundos.svg", cta("ENTER A WORLD", "portal"))
    for key, label in BUTTONS.items():
        write(f"btn-{key}.svg", button(label))
    write("footer-dark.svg", footer(dark=True))
    write("footer-light.svg", footer(dark=False))
