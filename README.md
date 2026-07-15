# morgsbrew.github.io

Source and build for **[morgsbrew.github.io](https://morgsbrew.github.io)** — my portfolio, CV, talks, and writing.

Everything is generated from a single source of truth, [`src/data/resume.json`](src/data/resume.json):

- the **web CV** and two **PDFs** (résumé + academic CV) render via [Quarto](https://quarto.org) (`src/engine/`), pinned with `renv.lock`
- the **hub**, **talks**, and **writing** pages build from `src/hub/` + `src/tools/`
- the published site is the repository root (served by GitHub Pages)

Rebuild: `cd src && make render`, then publish the built files at the repo root.

*imagine ‹ create ‹ change*
