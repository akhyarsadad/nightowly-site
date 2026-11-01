# night owly website

Rules for every session in this repository.

- **Menus:** the current item of any menu or navigation bar on a page is colour-coded orange
  (`--orange` in `site/assets/site.css`, with light and dark values). Mark it with `aria-current="page"`
  and the shared `.nav` style does the rest; do not use another colour for it. Check contrast (4.5:1 or more)
  in light and dark mode.
- **One header per app:** APrompter and Dutchy pages (landing, support, privacy, terms; English and Dutch) share
  the same header and links. Change it in `site/build.py` and in each hand-written page together.
- Build and check before pushing: `pip install markdown==3.7 && python site/build.py _site`.
