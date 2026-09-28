# tools/ — cómo está hecho este perfil (guía para agentes)

Este repo (`viajatech/viajatech`) es el **README de perfil** de github.com/viajatech: es **público** por diseño.
Nunca pongas aquí datos privados, rutas locales, nombres de repos privados ni secretos.

## Diseño: "OBSIDIAN FORGE × Isabella"

- **Paleta:** obsidiana `#060607` · oro fundido `#D8B15F` / `#F0D890` / `#9C7A33` · brasa `#FF7A1A` (poca) ·
  marfil `#F2EDE4` · gris cálido `#8A8478`. Tema claro de GitHub: oro profundo `#8A6420`.
- **Prohibido por la marca de David:** cian, teal, turquesa, azul neón, morado/rosa pastel, degradados holográficos
  arcoíris, y los clichés de "circuitos", cerebros de alambre, código binario o rejillas de hexágonos.
- **Motivo:** el orbe de Isabella (esfera negra, bisel de oro que gira) con nodos en órbita = "one human. an army of AIs."
- **Tipografía:** IBM Plex Sans (300) y IBM Plex Mono (400/500), convertidas a **trazos** con HarfBuzz → se ve idéntico
  en cualquier dispositivo y no depende de fuentes instaladas. Animaciones con **SMIL** (funcionan dentro de `<img>`).

## Archivos

| Archivo | Qué es |
|---|---|
| `README.md` | El perfil. Texto real en Markdown (legible en celular e indexable); las imágenes van con `<picture>` para tema claro/oscuro |
| `assets/hero.svg` | Banner animado (nombre, titular, orbe con órbitas, tecleo del manifiesto, chispas de forja) |
| `assets/cta-chat.svg`, `cta-voice.svg` | Botones grandes para hablar con Isabella (chat en jettrendy.com, voz en /about) |
| `assets/sec-*-dark.svg` / `-light.svg` | Encabezados de sección para cada tema |
| `assets/btn-*.svg` | Botones de contacto |
| `assets/footer-dark.svg` / `-light.svg` | Pie de terminal animado |
| `tools/build_assets.py` | **Genera todos los SVG.** Textos, colores y secciones se editan arriba del archivo |

**No edites los SVG a mano:** cambia `tools/build_assets.py` y regenera.

## Regenerar

```bash
python3 -m pip install --user fonttools brotli uharfbuzz
JT_FONTS=<carpeta con sans-300.woff2, mono-400.woff2 y mono-500.woff2 de IBM Plex> python3 tools/build_assets.py
```
(Por default busca las fuentes en `tools/fonts/`, que git ignora.)

## Antes de publicar

1. Vista previa real: `gh api -X POST markdown` con el README (modo `gfm`, contexto `viajatech/viajatech`) y revisar en
   tema oscuro, claro y a 390 px de ancho (celular).
2. Verificar que no haya información privada en el diff.
3. Commit a `main` → el perfil se actualiza al instante. Para deshacer: `git revert <commit>`.

## Historial

- 2026-09-27 — rediseño completo "OBSIDIAN FORGE × Isabella" (Claude Opus 5.5). El README anterior está en el
  historial de git (commit `79f08e9`); la imagen `VIAJA TECH WALL.png` se conserva en el repo.
