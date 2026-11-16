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

## About Dutchy

Dutchy is the owner's Dutch course app (A1 to C2, built on the inburgering A2/B1 and Staatsexamen NT2 I/II exams),
with Owly the owl as mascot. Free A1; Dutchy Volledig EUR 14.99 per 3 months (EUR 9.99 for a new subscriber's first
3 months). The app lives in `akhyarsadad/dutchy` (work branch `claude/app-waves`), whose `CLAUDE.md` holds the full
product context. This site's Dutchy pages copy the app's `src/content/legal.ts`: change both together.
