# night owly website

Rules for every session in this repository.

## Menus in chat

- When you offer a choice as a menu or option list in chat, colour-code it orange: start every option line with 🟠.
  Chat cannot show real colours, so the orange circle is the colour code. Put the recommended option first
  and mark it "(Recommended)".
- When you tell the owner where to click (a menu, setting or button in GitHub, a store console or any app), mark
  every name they must click with 🟠, e.g. `aprompter → 🟠 Settings → 🟠 Pages`. Same reason: no real colours in chat.

## One header per app

APrompter and Dutchy pages (landing, support, privacy, terms; English and Dutch) share the same header and links.
Change it in `site/build.py` and in each hand-written page together.
Build before pushing: `pip install markdown==3.7 && python site/build.py _site`.
