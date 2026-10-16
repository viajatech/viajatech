# tools/ — cómo está hecho este perfil (guía para agentes)

Este repo (`viajatech/viajatech`) es el **README de perfil** de github.com/viajatech: es **público** por diseño.
Nunca pongas aquí datos privados, rutas locales, nombres de repos privados ni secretos.

## Diseño: "OBSIDIAN FORGE · el núcleo de viajatech.com" (v2, 12-oct-2026)

- **Fuente de verdad de los textos:** viajatech.com (`/perfil`, `/sitios`, `/codigo`, `/canales`). El perfil dice lo mismo que
  el sitio y nada que no esté publicado ahí (sin hotelería, sin cifras no verificables).
- **Paleta:** obsidiana `#060607` · oro fundido `#D8B15F` / `#F0D890` / `#9C7A33` · brasa `#FF7A1A` (poca) · marfil `#F2EDE4` ·
  gris cálido `#8A8478`. Tema claro de GitHub: oro profundo `#8A6420`. Los ocho satélites llevan el color de su sección en
  viajatech.com: Isabella violeta, Sitios oro, Tienda brasa, Código azul eléctrico, Stories rosa, Perfil marfil, Canales ámbar.
- **Prohibido por la marca de David:** cian, teal, turquesa, azul neón, morado/rosa pastel, degradados holográficos
  arcoíris, y los clichés de "circuitos", cerebros de alambre, código binario o rejillas de hexágonos.
- **Motivo:** la portada de viajatech.com en SVG: el núcleo (esfera de obsidiana con bisel de oro que gira), la órbita con los
  ocho satélites, una **sinapsis** que recorre cada satélite (hilo con impulso), y el **cometa** que nace del núcleo, baja por
  su hilo y aterriza sobre `viajatech.com` (el Acto I del sitio). Tecleo del manifiesto *"one human. an army of AIs. zero limits."*
- **Tipografía Forja**, la del sitio: Unbounded (nombre), Space Grotesk (@handle), JetBrains Mono (etiquetas y datos), SIL OFL,
  convertidas a **trazos** con HarfBuzz → se ve idéntico en cualquier dispositivo. Animaciones con **SMIL** (funcionan dentro de
  `<img>`); CSS y JS no.

## Archivos

| Archivo | Qué es |
|---|---|
| `README.md` | El perfil. Texto real en Markdown (legible en celular e indexable); las imágenes van con `<picture>` para tema claro/oscuro |
| `assets/hero.svg` | Banner animado 1280×480 (nombre, titular, núcleo con órbita y satélites, sinapsis, cometa, tecleo, chispas) |
| `assets/cta-chat.svg`, `cta-voice.svg`, `cta-sitios.svg` | Botones grandes: hablar con Isabella (texto / voz en viajatech.com/isabella) y «a website for your business» (viajatech.com/sitios) |
| `assets/sec-*-dark.svg` / `-light.svg` | Encabezados de sección 002–008 para cada tema |
| `assets/btn-*.svg` | Botones de contacto (viajatech.com, viajatech.xyz, jettrendy.com, email, redes) |
| `assets/footer-dark.svg` / `-light.svg` | Pie de terminal animado (`join --revolution`) |
| `tools/build_assets.py` | **Genera todos los SVG.** Textos, colores, satélites y botones se editan arriba del archivo |
| `tools/fonts/` | Las tres fuentes `.woff2` + licencias (ignorada por git; copia de `viajatech-web/public/fonts`) |

**No edites los SVG a mano:** cambia `tools/build_assets.py` y regenera.

## Regenerar

```bash
python3 -m pip install --user fonttools brotli uharfbuzz
# fuentes: tools/fonts/unbounded-latin.woff2, space-grotesk-latin.woff2, jetbrains-mono-latin.woff2 (o JT_FONTS=<carpeta>)
python3 tools/build_assets.py
```

## Antes de publicar

1. Vista previa real: `preview_perfil_github.py --build` (script del hub privado de viajatech, fuera de este repo) (renderiza el README con la API de
   GitHub y captura oscuro / claro / celular; falla si hay imágenes rotas o desborde). Mirar las capturas.
2. Commit + push a `main` (nunca force). Verificar publicado: `preview_perfil_github.py --live`.
3. Auditoría de exposición: `auditoria_publica.py` (también del hub privado).
