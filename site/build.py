"""Builds the night owly website into an output folder.

    pip install markdown==3.7
    python site/build.py _site [--url https://example.com/base]

Copies site/ as is, then renders each app's legal pages from Markdown, so the
website shows the same text the app links to and there is one copy to edit:

  - APrompter: docs/PRIVACY.md and docs/TERMS.md (they live in this repository).
  - Dutchy: site/content/dutchy/{privacy,terms}.{en,nl}.md, in English and Dutch.
    (site/content/ is not published as files, only rendered into pages.)

--url is the address the site is served from (GitHub Pages gives it). It
fills {{SITE_URL}} in pages that need absolute links: share previews, language
alternates and the 404 page, which is served at whatever address was asked for.
"""

import html
import os
import re
import shutil
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# One entry per app and language: where its pages live and what they are called.
APPS = {
    ("aprompter", "en"): {
        "name": "APrompter",
        "home": "aprompter",
        "icons": "aprompter/img",
        "nav": ("Features", "Plans", "FAQ", "Support", "Privacy", "Terms"),
        "footer": ("Privacy policy", "Terms of use", "Support"),
        "by": "APrompter by",
        "skip": "Skip to content",
    },
    ("dutchy", "en"): {
        "name": "Dutchy",
        "home": "dutchy",
        "icons": "dutchy/img",
        "nav": ("Features", "Plans", "FAQ", "Support", "Privacy", "Terms"),
        "footer": ("Privacy statement", "Terms of use", "Support"),
        "by": "Dutchy by",
        "skip": "Skip to content",
        "alt": ("nl", "Nederlands"),
        "css": "dutchy/dutchy.css",
    },
    ("dutchy", "nl"): {
        "name": "Dutchy",
        "home": "dutchy/nl",
        "icons": "dutchy/img",
        "nav": ("Functies", "Abonnement", "Vragen", "Support", "Privacy", "Voorwaarden"),
        "footer": ("Privacyverklaring", "Gebruiksvoorwaarden", "Support"),
        "by": "Dutchy van",
        "skip": "Ga naar de inhoud",
        "alt": ("en", "English"),
        "css": "dutchy/dutchy.css",
    },
}

# Rendered pages: app, language, Markdown source, output folder, title,
# nav key and, for Dutchy, a description (APrompter's is read from its text).
PAGES = [
    dict(app="aprompter", lang="en", source="docs/PRIVACY.md", out="aprompter/privacy",
         title="APrompter Privacy Policy", nav="privacy"),
    dict(app="aprompter", lang="en", source="docs/TERMS.md", out="aprompter/terms",
         title="APrompter Terms of Use", nav="terms"),
    dict(app="dutchy", lang="en", source="site/content/dutchy/privacy.en.md", out="dutchy/privacy",
         title="Dutchy Privacy Statement", nav="privacy",
         description="What Dutchy keeps on your phone, what leaves it (the purchase check and, depending on your phone, speech recognition) and what does not."),
    dict(app="dutchy", lang="en", source="site/content/dutchy/terms.en.md", out="dutchy/terms",
         title="Dutchy Terms of Use", nav="terms",
         description="The terms for using Dutchy and its subscription: what is free, how renewal and cancelling work, and what the app is not."),
    dict(app="dutchy", lang="nl", source="site/content/dutchy/privacy.nl.md", out="dutchy/nl/privacy",
         title="Dutchy Privacyverklaring", nav="privacy",
         description="Wat Dutchy op je telefoon bewaart, wat die verlaat (de aankoopcontrole en, afhankelijk van je telefoon, spraakherkenning) en wat niet."),
    dict(app="dutchy", lang="nl", source="site/content/dutchy/terms.nl.md", out="dutchy/nl/terms",
         title="Dutchy Gebruiksvoorwaarden", nav="terms",
         description="De voorwaarden voor Dutchy en het abonnement: wat gratis is, hoe verlengen en opzeggen werken, en wat de app niet is."),
]

# Links between the Markdown files become links between the pages.
LINKS = {"PRIVACY.md": "../privacy/", "TERMS.md": "../terms/"}

BARE_URL = re.compile(r"(?<![<(\"'=])\b(https?://[^\s<>()]+[^\s<>().,;:!?])")
BARE_EMAIL = re.compile(r"(?<![<\w.@/])([\w.+-]+@[\w-]+(?:\.[\w-]+)+)(?![\w>])")

TEMPLATE = """<!doctype html>
<html lang="{lang}" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#0e1126">
<link rel="icon" href="{icons}icon-64.png" type="image/png">
<link rel="apple-touch-icon" href="{icons}icon-180.png">
<link rel="stylesheet" href="{root}assets/site.css">{extra_head}
</head>
<body>
<a class="skip" href="#main">{skip}</a>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{home}">
      <img src="{icons}icon-256.webp" alt="" width="34" height="34">
      {name}
    </a>
    <nav class="nav" aria-label="{name}">
      <a href="{home}#features">{nav_features}</a>
      <a href="{home}#plans">{nav_plans}</a>
      <a href="{home}#faq">{nav_faq}</a>
      <a href="../support/">{nav_support}</a>
      <a href="../privacy/"{privacy_current}>{nav_privacy}</a>
      <a href="../terms/"{terms_current}>{nav_terms}</a>{lang_switch}
    </nav>
  </div>
</header>

<main id="main" class="doc">
  <div class="wrap">
    <article>
{body}
    </article>
  </div>
</main>

<footer class="site-footer">
  <div class="wrap">
    <span>{by} <a href="{root}">night owly</a></span>
    <nav aria-label="Footer">
      <a href="../privacy/">{footer_privacy}</a>
      <a href="../terms/">{footer_terms}</a>
      <a href="../support/">{footer_support}</a>
    </nav>
  </div>
</footer>
</body>
</html>
"""


def link_bare_addresses(text: str) -> str:
    """Turns bare URLs and email addresses into Markdown autolinks, leaving
    ones that are already inside a link alone."""
    out = []
    for line in text.splitlines(keepends=True):
        line = BARE_URL.sub(r"<\1>", line)
        line = BARE_EMAIL.sub(r"<\1>", line)
        out.append(line)
    return "".join(out)


def rel(target: str, start: str) -> str:
    """A relative link from the folder `start` to the folder `target`."""
    path = os.path.relpath(target, start)
    return "./" if path == "." else path.rstrip("/") + "/"


def render(page: dict) -> str:
    app = APPS[(page["app"], page["lang"])]
    out = page["out"]
    depth = len(out.split("/"))
    root = "../" * depth
    text = (ROOT / page["source"]).read_text(encoding="utf-8")
    text = link_bare_addresses(text)
    body = markdown.markdown(
        text,
        extensions=["tables", "toc", "sane_lists"],
        extension_configs={"toc": {"permalink": False}},
        output_format="html",
    )
    for name, href in LINKS.items():
        body = body.replace(f'href="{name}"', f'href="{href}"')
    # Wide tables scroll inside their own box on phones.
    body = body.replace(
        "<table>",
        '<div class="table-scroll" tabindex="0" role="region" '
        'aria-label="Table, scrolls sideways"><table>',
    )
    body = body.replace("</table>", "</table></div>")
    plain = re.sub(r"<[^>]+>", " ", body)
    first = re.search(r"Short version:(.*?)(?:\.|$)", plain, re.S) or re.search(
        r"These terms (.*?)\.", plain, re.S
    )
    description = page.get("description") or " ".join(
        (first.group(0) if first else page["title"]).split()
    )[:155]

    lang_switch, extra_head = "", ""
    if "css" in app:
        folder, _, sheet = app["css"].rpartition("/")
        extra_head += f'\n<link rel="stylesheet" href="{rel(folder, out)}{sheet}">'
    if "alt" in app:
        alt_lang, alt_label = app["alt"]
        alt_out = out.replace("dutchy/nl/", "dutchy/") if alt_lang == "en" else out.replace(
            "dutchy/", "dutchy/nl/", 1
        )
        lang_switch = (
            f'\n      <a class="lang-switch" href="{rel(alt_out, out)}" hreflang="{alt_lang}" '
            f'lang="{alt_lang}">{alt_label}</a>'
        )
        en_out = out if page["lang"] == "en" else alt_out
        nl_out = out if page["lang"] == "nl" else alt_out
        extra_head += (
            f'\n<link rel="canonical" href="{{{{SITE_URL}}}}/{out}/">'
            f'\n<link rel="alternate" hreflang="en" href="{{{{SITE_URL}}}}/{en_out}/">'
            f'\n<link rel="alternate" hreflang="nl" href="{{{{SITE_URL}}}}/{nl_out}/">'
        )
    labels = app["nav"]
    footer = app["footer"]
    return TEMPLATE.format(
        lang=page["lang"],
        title=html.escape(page["title"]),
        description=html.escape(description, quote=True),
        icons=rel(app["icons"], out),
        root=root,
        extra_head=extra_head,
        skip=app["skip"],
        home=rel(app["home"], out),
        name=app["name"],
        nav_features=labels[0],
        nav_plans=labels[1],
        nav_faq=labels[2],
        nav_support=labels[3],
        nav_privacy=labels[4],
        nav_terms=labels[5],
        privacy_current=' aria-current="page"' if page["nav"] == "privacy" else "",
        terms_current=' aria-current="page"' if page["nav"] == "terms" else "",
        lang_switch=lang_switch,
        body=body,
        by=app["by"],
        footer_privacy=footer[0],
        footer_terms=footer[1],
        footer_support=footer[2],
    )


def main() -> None:
    args = sys.argv[1:]
    site_url = ""
    if "--url" in args:
        i = args.index("--url")
        if i + 1 >= len(args):
            sys.exit("usage: python site/build.py OUTPUT_DIR [--url SITE_URL]")
        site_url = args[i + 1].rstrip("/")
        del args[i : i + 2]
    if len(args) != 1:
        sys.exit("usage: python site/build.py OUTPUT_DIR [--url SITE_URL]")
    out = Path(args[0]).resolve()
    if out == SITE or SITE in out.parents:
        sys.exit("pick an output folder outside site/")
    if out.exists():
        # Only ever replace a folder this script built (it leaves .nojekyll).
        if any(out.iterdir()) and not (out / ".nojekyll").exists():
            sys.exit(f"{out} is not empty and was not built by this script: pick a new folder")
        shutil.rmtree(out)
    shutil.copytree(
        SITE, out, ignore=shutil.ignore_patterns("build.py", "__pycache__", "content")
    )
    for page in PAGES:
        target = out / page["out"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(page), encoding="utf-8")
    for page in out.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        if "{{SITE_URL}}" in text:
            page.write_text(text.replace("{{SITE_URL}}", site_url), encoding="utf-8")
    # GitHub Pages: serve files as they are (no Jekyll processing).
    (out / ".nojekyll").write_text("")
    print(f"Built {out}")


if __name__ == "__main__":
    main()
