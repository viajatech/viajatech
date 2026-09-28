#!/usr/bin/env python3
"""
build_assets.py — genera TODOS los SVG del README de perfil de github.com/viajatech.

Diseño "OBSIDIAN FORGE × Isabella": obsidiana + oro fundido + una brasa ámbar (NUNCA cian/teal/neón azul,
ni circuitos/cerebros/binario/hexágonos — reglas de marca de David). El texto se convierte a TRAZOS con las
fuentes del sitio (IBM Plex Sans/Mono, SIL OFL) usando HarfBuzz → se ve idéntico en cualquier dispositivo y
no depende de fuentes instaladas ni de CSP. Animaciones con SMIL (funcionan dentro de <img> en GitHub).

Uso:   python3 tools/build_assets.py            (requiere: pip install --user fonttools brotli uharfbuzz)
Fuentes: JT_FONTS=<carpeta con sans-300.woff2 y mono-400/500.woff2 de IBM Plex>  (default: tools/fonts/, ignorada por git)
Salida: assets/*.svg  — editar TEXTOS/COLORES aquí arriba y volver a correr.
"""
import io
import os
import sys

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
FONT_DIR = os.environ.get("JT_FONTS", os.path.join(ROOT, "tools", "fonts"))  # IBM Plex (no se versiona)

# ── Paleta OBSIDIAN FORGE ────────────────────────────────────────────────────────────────────────
OBS0, OBS1 = "#060607", "#0E0D0B"          # obsidiana
GOLD, GOLD_HI, GOLD_DEEP = "#D8B15F", "#F0D890", "#9C7A33"
EMBER = "#FF7A1A"                           # brasa (con moderación)
IVORY, WARM, DIM = "#F2EDE4", "#8A8478", "#4A463F"
# variantes para el tema CLARO de GitHub (encabezados y pie)
L_GOLD, L_INK, L_WARM = "#8A6420", "#1F1B14", "#6B645A"

# ── Textos (editar aquí) ─────────────────────────────────────────────────────────────────────────
NAME = "David Ruiz"
HANDLE = "@viajatech"
LABEL = "/ 001 — VIAJATECH · JETTRENDY"
HEADLINE = "CREATIVE TECHNOLOGIST · AI ARCHITECT · DIGITAL STRATEGIST"
PROMPT = "$ whoami"
MANIFESTO = "one human. an army of AIs. zero limits."
STATUS = "LIVE — MEXICO CITY"
DOMAIN = "jettrendy.com"

SECTIONS = {  # archivo → (número, título)
    "ship": ("002", "WHAT I SHIP"),
    "live": ("003", "LIVE — PROOF OF WORK"),
    "stack": ("004", "STACK"),
    "repos": ("005", "SIGNATURE REPOS"),
    "books": ("006", "BOOKS"),
    "connect": ("007", "CONNECT"),
}
BUTTONS = {  # archivo → etiqueta
    "jettrendy": "JETTRENDY.COM",
    "viajatech-xyz": "VIAJATECH.XYZ",
    "youtube": "YOUTUBE",
    "instagram": "INSTAGRAM",
    "tiktok": "TIKTOK",
    "x": "X",
    "threads": "THREADS",
    "facebook": "FACEBOOK",
    "email": "EMAIL",
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
    SANS_LIGHT = Face("sans-300.woff2", wght=300)
    MONO = Face("mono-400.woff2")
    MONO_MED = Face("mono-500.woff2")
except Exception as e:  # noqa: BLE001
    sys.exit(f"No pude cargar las fuentes de {FONT_DIR}: {e}\n(define JT_FONTS o instala fonttools/brotli/uharfbuzz)")


def text_path(face, text, size, x, y, fill, tracking=0.0, opacity=None, extra=""):
    d, w, _ = face.run(text, size, x, y, tracking)
    op = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return f'<path d="{d}" fill="{fill}"{op}{extra}/>', w


def write(name, svg):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  {name:<28} {len(svg.encode()) / 1024:6.1f} KB")


# ── HERO (banner animado 1280×480) ───────────────────────────────────────────────────────────────
def hero():
    W, H = 1280, 480
    cx, cy = 1012, 214  # centro del orbe
    lx = 72
    label, _ = text_path(MONO_MED, LABEL, 14, lx, 88, WARM, tracking=0.32)
    name, _ = text_path(SANS_LIGHT, NAME, 112, lx - 6, 200, IVORY, tracking=-0.01)
    handle, _ = text_path(SANS_LIGHT, HANDLE, 46, lx - 1, 258, GOLD, opacity=0.9)
    headline, _ = text_path(MONO_MED, HEADLINE, 14, lx, 326, GOLD, tracking=0.24)
    prompt, pw = text_path(MONO, PROMPT, 21, lx, 378, WARM)
    mx = lx + pw + 16
    md, mw, mxs = MONO.run(MANIFESTO, 21, mx, 378)
    status, _ = text_path(MONO_MED, STATUS, 12, lx + 22, 451, WARM, tracking=0.3)
    dom_d, dom_w, _ = MONO_MED.run(DOMAIN, 12, 0, 451, 0.3)
    domain, _ = text_path(MONO_MED, DOMAIN, 12, W - 64 - dom_w, 451, GOLD, tracking=0.3, opacity=0.85)

    # tecleo: el clip crece carácter por carácter y el cursor lo sigue
    n = len(MANIFESTO)
    widths = [mxs[i] - mx for i in range(n + 1)]
    wvals = ";".join("%.1f" % w for w in widths)
    cvals = ";".join("%.1f" % (mx + w + 3) for w in widths)
    kt = ";".join("%.4f" % (i / n) for i in range(n + 1))
    type_dur, type_begin = 2.6, 1.0

    # nodos en órbita = "un ejército de IAs"
    orbits = [  # rx, ry, rot, opacidad, [(dur, color, r, fase, sentido)]
        (212, 64, -14, 0.26, [(18, GOLD_HI, 3.6, 0.0, 1), (18, GOLD, 2.6, 0.5, 1)]),
        (162, 47, 16, 0.22, [(12, EMBER, 3.0, 0.2, -1), (12, GOLD_HI, 2.2, 0.7, -1)]),
        (252, 80, 4, 0.18, [(27, GOLD, 2.8, 0.35, 1), (27, GOLD_HI, 2.0, 0.85, 1), (27, EMBER, 2.2, 0.1, 1)]),
    ]
    orbit_back, orbit_front = [], []
    for i, (rx, ry, rot, op, nodes) in enumerate(orbits):
        pid = f"orb{i}"
        ring = (f'M {-rx} 0 A {rx} {ry} 0 1 1 {rx} 0 A {rx} {ry} 0 1 1 {-rx} 0')
        # anillo completo detrás de la esfera + mitad inferior delante (efecto planeta con anillos)
        orbit_back.append(f'<path id="{pid}" d="{ring}" fill="none" stroke="{GOLD}" stroke-opacity="{op}" '
                          f'stroke-width="1" stroke-dasharray="2 7" transform="rotate({rot})"/>')
        orbit_front.append(f'<path d="M {-rx} 0 A {rx} {ry} 0 0 0 {rx} 0" fill="none" stroke="{GOLD}" '
                           f'stroke-opacity="{op * 1.5:.2f}" stroke-width="1" stroke-dasharray="2 7" transform="rotate({rot})"/>')
        for dur, col, r, phase, sense in nodes:
            kp = "1;0" if sense < 0 else "0;1"
            mot = (f'<animateMotion dur="{dur}s" begin="-{phase * dur:.1f}s" repeatCount="indefinite" '
                   f'keyPoints="{kp}" keyTimes="0;1" calcMode="linear"><mpath xlink:href="#{pid}"/></animateMotion>')
            node = (f'<circle r="{r * 2.8:.1f}" fill="{col}" opacity="0.22" filter="url(#soft)">{mot}</circle>'
                    f'<circle r="{r}" fill="{col}">{mot}</circle>')
            orbit_back.append(f'<g transform="rotate({rot})">{node}</g>')
            # copia delantera recortada a la mitad inferior de su órbita (en coordenadas de la órbita)
            orbit_front.append(f'<g transform="rotate({rot})" clip-path="url(#lower)">{node}</g>')

    # chispas de forja que suben del horizonte (brasas)
    sparks = []
    for j, (x, rise, dur, beg, r, col) in enumerate([
        (700, 70, 6.5, 0.0, 1.6, EMBER), (782, 118, 8.0, 2.1, 1.2, GOLD_HI), (868, 92, 7.2, 4.0, 1.8, EMBER),
        (955, 140, 9.0, 1.2, 1.3, GOLD), (1046, 104, 7.6, 3.3, 1.7, EMBER), (1134, 128, 8.6, 5.1, 1.2, GOLD_HI),
        (1210, 84, 6.8, 2.7, 1.5, EMBER), (1000, 60, 5.8, 6.0, 1.1, GOLD_HI),
    ]):
        sparks.append(
            f'<circle cx="{x}" cy="408" r="{r}" fill="{col}" opacity="0">'
            f'<animate attributeName="cy" values="408;{408 - rise}" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cx" values="{x};{x + (9 if j % 2 else -9)};{x}" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.9;0.5;0" keyTimes="0;0.2;0.7;1" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
            f'</circle>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{NAME} — {HANDLE} — Creative Technologist, AI Architect, Digital Strategist — {MANIFESTO}">
<title>{NAME} — {HANDLE}</title>
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
  <clipPath id="lower"><rect x="-320" y="0" width="640" height="200"/></clipPath>
  <filter id="soft" x="-2" y="-2" width="5" height="5"><feGaussianBlur stdDeviation="3"/></filter>
  <filter id="blur1"><feGaussianBlur stdDeviation="0.8"/></filter>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.94  0 0 0 0 0.85  0 0 0 0 0.62  0 0 0 0.06 0"/>
  </filter>
  <clipPath id="typeclip"><rect x="{mx}" y="350" height="40" width="0">
    <animate attributeName="width" values="{wvals}" keyTimes="{kt}" calcMode="discrete" dur="{type_dur}s" begin="{type_begin}s" fill="freeze"/>
  </rect></clipPath>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{OBS0}"/>
  <rect width="{W}" height="{H}" fill="url(#forge)"/>
  <rect width="{W}" height="{H}" filter="url(#grain)"/>
  <rect x="0" y="409" width="{W}" height="1.4" fill="url(#horizon)"/>
  <rect x="0" y="410" width="{W}" height="18" fill="url(#horizon)" opacity="0.10" filter="url(#soft)"/>

  <g transform="translate({cx} {cy})">
    <circle r="190" fill="url(#halo)"><animate attributeName="opacity" values="0.65;1;0.65" dur="4.5s" repeatCount="indefinite"/></circle>
    {"".join(orbit_back)}
    <circle r="98" fill="url(#sphere)"/>
    <circle r="97" fill="none" stroke="{GOLD}" stroke-opacity="0.22"/>
    <g><circle r="101" fill="none" stroke="url(#bezel)" stroke-width="3.2" stroke-linecap="round" stroke-dasharray="52 16 118 30 64 22 90 44" opacity="0.92"/>
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="9s" repeatCount="indefinite"/></g>
    <ellipse cx="-32" cy="-44" rx="30" ry="17" fill="url(#spec)" transform="rotate(-24 -32 -44)" filter="url(#blur1)"/>
    {"".join(orbit_front)}
  </g>
  {"".join(sparks)}

  {label}
  {name}
  {handle}
  <rect x="{lx}" y="286" width="92" height="1" fill="{GOLD}" opacity="0.5"/>
  {headline}
  {prompt}
  <path d="{md}" fill="{IVORY}" clip-path="url(#typeclip)"/>
  <rect x="{mx + 3}" y="360" width="11" height="23" fill="{GOLD}">
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
    """Flecha ↗ dibujada (la fuente no trae flechas). (x, y) = esquina inferior izquierda."""
    return (f'<path d="M {x} {y} L {x + s} {y - s} M {x + s * 0.35} {y - s} L {x + s} {y - s} L {x + s} {y - s * 0.65}" '
            f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')


# ── Encabezado de sección (560×56, fondo transparente; variante oscura y clara) ─────────────────
def section(num, title, dark=True):
    W, H = 560, 60
    c_num, c_title, c_line = (WARM, GOLD, GOLD) if dark else (L_WARM, L_GOLD, L_GOLD)
    pre, pw = text_path(MONO_MED, f"/ {num} — ", 20, 2, 39, c_num, tracking=0.2)
    ttl, tw = text_path(MONO_MED, title, 20, 2 + pw + 20 * 0.2, 39, c_title, tracking=0.2)
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


# ── Botones grandes de Isabella (CTA) — oscuros en ambos temas (objeto de marca) ──────────────────
def cta(label, icon):
    H = 60
    lab_d, lw, _ = MONO_MED.run(label, 14, 0, 0, 0.2)
    W = int(24 + 36 + 14 + lw + 18 + 12 + 26)
    lab, _ = text_path(MONO_MED, label, 14, 74, 35, IVORY, tracking=0.2)
    ax = 74 + lw + 18
    if icon == "orb":  # mini orbe de Isabella con bisel que gira
        ic = f'''<g transform="translate(42 30)">
  <circle r="17" fill="url(#halo)"/>
  <circle r="11.5" fill="url(#sph)"/>
  <g><circle r="13.2" fill="none" stroke="{GOLD}" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="14 5 22 8 12 6"/>
  <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="7s" repeatCount="indefinite"/></g>
  <ellipse cx="-3.5" cy="-4.5" rx="3.6" ry="2" fill="#FFF4D6" opacity="0.55" transform="rotate(-24 -3.5 -4.5)"/>
</g>'''
    else:  # onda de voz animada
        bars = []
        for k, (h1, h2, d) in enumerate([(6, 16, 0.9), (10, 24, 1.1), (16, 8, 0.8), (8, 20, 1.0), (5, 13, 1.2)]):
            x = 29 + k * 6.2
            bars.append(f'<rect x="{x:.1f}" y="{30 - h1 / 2}" width="3" height="{h1}" rx="1.5" fill="{GOLD}">'
                        f'<animate attributeName="height" values="{h1};{h2};{h1}" dur="{d}s" repeatCount="indefinite"/>'
                        f'<animate attributeName="y" values="{30 - h1 / 2};{30 - h2 / 2};{30 - h1 / 2}" dur="{d}s" repeatCount="indefinite"/></rect>')
        ic = "".join(bars)
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
    sub, _ = text_path(MONO, "made in mexico city · one human + an army of AIs", 13, 2, 63, c_sub, tracking=0.06)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="guest@viajatech:~$ join --revolution — made in mexico city">
<title>join --revolution</title>
<defs><clipPath id="t"><rect x="{cx0}" y="10" height="30" width="0">
  <animate attributeName="width" values="{";".join("%.1f" % w for w in widths)}" keyTimes="{kt}" calcMode="discrete" dur="1.7s" begin="0.8s" fill="freeze"/></rect></clipPath></defs>
{pr}
<path d="{cd}" fill="{c_cmd}" clip-path="url(#t)"/>
<rect x="{cx0 + 2}" y="14" width="10" height="21" fill="{c_caret}">
  <animate attributeName="x" values="{";".join("%.1f" % (cx0 + w + 2) for w in widths)}" keyTimes="{kt}" calcMode="discrete" dur="1.7s" begin="0.8s" fill="freeze"/>
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
    for key, label in BUTTONS.items():
        write(f"btn-{key}.svg", button(label))
    write("footer-dark.svg", footer(dark=True))
    write("footer-light.svg", footer(dark=False))
