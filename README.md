# night owly website

The source of https://nightowly.dev: the hub, the APrompter pages and the Dutchy pages (English and Dutch),
with each app's privacy policy and terms of use.

- `site/`: the pages, styles, images and `build.py`, which renders the legal pages from Markdown.
- `docs/PRIVACY.md`, `docs/TERMS.md`: APrompter's privacy policy and terms (Dutchy's are in `site/content/dutchy/`).
- Publishing: pushing to `main` runs `.github/workflows/pages.yml` and deploys to GitHub Pages.
  One-time setup: Settings → Pages → Source: GitHub Actions, and custom domain `nightowly.dev`.

Build locally: `pip install markdown==3.7 && python site/build.py _site`.

The apps' source code lives in separate repositories.
