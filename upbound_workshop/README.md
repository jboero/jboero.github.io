# Upbound — Reveal.js + Three.js deck

A Reveal.js slide deck with a WebGL spinning-cube background (the Upbound logo,
textured on all six faces). Self-contained — no runtime CDN dependencies.

## Layout

```
index.html            Deck: cube background + slide loader + Reveal init
css/custom.css        Backdrop gradient, blurred cube layer, slide/panel styling
vendor/               Vendored libraries (self-hosted, no CDN)
  three.module.min.js   Three.js r160 (ES module) — the cube
  reveal.js             Reveal.js 5.1.0 (UMD global `Reveal`)
  reveal.css            Reveal.js 5.1.0 core styles
images/upbound_avatar.png   Cube face texture (official Upbound logo)
sections/             Slides, one SVG per slide
  <col>/<row>.svg       col = horizontal column, row = vertical slide
  1..3/                 content slides
  4/                    reusable copy-me templates
  gen_slides.py         Generator that builds all the section SVGs
LICENSE
```

## Editing

- **Cube** — tunables at the top of the module script in `index.html`
  (`UB_SIZE`, `UB_OFFSET`, `UB_DEPTH`, `UB_TILT`, `UB_SPEED`). Blur is
  `#background { filter: blur(...) }` in `css/custom.css`.
- **Background** — the `html, body` gradient in `css/custom.css`.
- **Slides** — edit `sections/gen_slides.py` and re-run it
  (`python3 sections/gen_slides.py`), or hand-edit the SVGs. To add a slide,
  copy a template, e.g. `cp sections/4/4.svg sections/2/5.svg`, then edit the
  `[ … ]` placeholders. Add a whole new column by creating `sections/5/` and
  bumping `SECTIONS` in `index.html`.

## Running

Any static file server. On this host it's served via Apache userdir at
`http://localhost/~<user>/upbound/`. After editing files that Apache serves,
make sure they're group-readable by the `apache` user
(`chgrp -R apache upbound && chmod -R g+rX upbound && restorecon -R upbound`).
