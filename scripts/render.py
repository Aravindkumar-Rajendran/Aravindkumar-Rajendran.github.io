#!/usr/bin/env python3
"""Render content/pages/*.md into the site's HTML pages.

Edit the markdown, then run:

    python3 scripts/render.py

Portfolio pages use assets/css/theme.css (floating nav, optional homepage hero).
App landing pages (layout: app) keep assets/css/style.css + apps.css.
Blog posts in content/posts/ stay markdown and are still opened from posts.html.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

try:
    import markdown
except ImportError:
    sys.exit("Install the renderer dependency first: python3 -m pip install -r scripts/requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "content" / "pages"

NAV = [
    ("home", "./", False),
    ("projects", "projects.html", False),
    ("posts", "posts.html", False),
    ("resume", "resume.html", False),
    ("contact", "contact.html", False),
]

META_RE = re.compile(r"<p><em>([^<]*)</em></p>")
NOTE_ITEM_RE = re.compile(
    r'<p><a href="([^"]*)"([^>]*)>(.*?)</a></p>\s*<p class="note-meta">(.*?)</p>',
    re.DOTALL,
)
LINK_RE = re.compile(r'<a href="([^"]*)"([^>]*)>')


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        raise SystemExit("page is missing front matter")
    end = text.find("\n---\n", 3)
    if end == -1:
        raise SystemExit("page front matter is not closed")
    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise SystemExit(f"bad front matter line: {line}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        meta[key.strip()] = value
    return meta, text[end + 5 :].lstrip("\n")


def render_markdown(body: str) -> str:
    body = re.sub(r"^\{\{posts\}\}\s*$", '<div id="notes-list"></div>', body, flags=re.MULTILINE)
    rendered = markdown.markdown(body, extensions=["extra", "sane_lists"])
    rendered = LINK_RE.sub(annotate_link, rendered)
    rendered = META_RE.sub(lambda match: f'<p class="note-meta">{match.group(1).strip()}</p>', rendered)
    return rendered


def annotate_link(match: re.Match[str]) -> str:
    href, rest = match.group(1), match.group(2)
    if href.startswith(("http://", "https://")) and "target=" not in rest:
        return f'<a href="{href}"{rest} target="_blank" rel="noopener">'
    return match.group(0)


def promote_note_items(rendered: str) -> str:
    def repl(match: re.Match[str]) -> str:
        href, attrs, label, meta = match.groups()
        return (
            f'<p class="note-item"><a href="{href}"{attrs}>{label}</a>\n'
            f'<span class="note-meta">{meta}</span></p>'
        )

    return NOTE_ITEM_RE.sub(repl, rendered)


def indent(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line else "" for line in text.strip().split("\n"))


def nav(current: str, pad: int = 6) -> str:
    lines = []
    for key, href, external in NAV:
        attrs = f' href="{href}"'
        if key == current:
            attrs += ' aria-current="page"'
        if external:
            attrs += ' target="_blank" rel="noopener"'
        lines.append(f"{' ' * pad}<a{attrs}>{key}</a>")
    return "\n".join(lines)


def theme_nav(current: str) -> str:
    return f"""  <nav class="topnav" aria-label="Primary">
    <div class="topnav-inner">
      <a class="brand" href="./" aria-label="home"><img class="brand-logo" src="assets/img/logo.png" alt="" width="32" height="32"></a>
      <div class="links">
{nav(current, 8)}
        <a class="btn-primary nav-cta" href="contact.html">get in touch</a>
      </div>
    </div>
  </nav>"""


ARROW = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M5 12h14M13 6l6 6-6 6"/></svg>'
)


def hero(meta: dict[str, str]) -> str:
    """Optional homepage hero, driven by hero_* front matter keys."""
    if "hero_title" not in meta:
        return ""
    esc = html.escape
    title = esc(meta["hero_title"])
    if accent := meta.get("hero_accent"):
        title += f'<br> <span class="blue-text">{esc(accent)}</span>'
    parts = []
    if kicker := meta.get("hero_kicker"):
        parts.append(f'<p class="hero-kicker"><span class="hero-kicker-dot"></span>{esc(kicker)}</p>')
    parts.append(f'<h1 class="display-1">{title}</h1>')
    if lede := meta.get("hero_lede"):
        parts.append(f'<p class="lede">{esc(lede)}</p>')
    actions = []
    if cta := meta.get("hero_cta"):
        href = esc(meta.get("hero_cta_href", "#"), quote=True)
        actions.append(f'<a class="btn-primary" href="{href}">{esc(cta)} {ARROW}</a>')
    if link := meta.get("hero_link"):
        href = esc(meta.get("hero_link_href", "#"), quote=True)
        actions.append(f'<a class="btn-ghost" href="{href}"><span class="ring">{ARROW}</span>{esc(link)}</a>')
    if actions:
        parts.append('<div class="hero-actions">\n' + indent("\n".join(actions), 2) + "\n</div>")
    content = indent("\n".join(parts), 8)
    return f"""  <section class="hero">
    <div class="hero-frame">
      <div class="hero-veil"></div>
      <div class="hero-grain"></div>
      <div class="hero-glow"></div>
      <div class="hero-content">
{content}
      </div>
    </div>
  </section>

"""


def theme_shell(source: str, meta: dict[str, str], wrap_inner: str, scripts: str = "") -> str:
    script_block = f"\n{scripts}\n" if scripts else "\n"
    hero_html = hero(meta)
    body_attrs = ' class="has-hero"' if hero_html else ""
    return f"""<!DOCTYPE html>
<html lang="{html.escape(meta.get("lang", "en"), quote=True)}">
<!-- Generated from {source}. Edit that file, then run: python3 scripts/render.py -->

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(meta["title"])}</title>
{meta_tags(meta)}  <link rel="preconnect" href="https://api.fontshare.com" crossorigin>
  <link href="https://api.fontshare.com/v2/css?f[]=clash-display@300,400,500&display=swap" rel="stylesheet">
  <link href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700&display=swap" rel="stylesheet">
  <link rel="icon" type="image/png" href="assets/img/logo.png">
  <link rel="apple-touch-icon" href="assets/img/logo.png">
  <link rel="stylesheet" href="assets/css/theme.css">
</head>

<body{body_attrs}>
{theme_nav(meta.get("nav", ""))}

{hero_html}  <div class="wrap">
{wrap_inner}
  </div>

  <footer class="byline">aravind kumar r</footer>{script_block}</body>

</html>
"""


def meta_tags(meta: dict[str, str]) -> str:
    tags = []
    if description := meta.get("description"):
        tags.append(f'  <meta name="description" content="{html.escape(description, quote=True)}">')
    if author := meta.get("author"):
        tags.append(f'  <meta name="author" content="{html.escape(author, quote=True)}">')
    if canonical := meta.get("canonical"):
        domain = (ROOT / "CNAME").read_text(encoding="utf-8").strip()
        canonical = urljoin(f"https://{domain}/", canonical)
        tags.append(f'  <link rel="canonical" href="{html.escape(canonical, quote=True)}">')
        for property_name, value in (
            ("og:type", "website"),
            ("og:title", meta["title"]),
            ("og:description", meta.get("description", "")),
            ("og:url", canonical),
            ("og:locale", "ta_IN" if meta.get("lang") == "ta" else "en_IN"),
        ):
            tags.append(f'  <meta property="{property_name}" content="{html.escape(value, quote=True)}">')
        if image := meta.get("image"):
            image = urljoin(f"https://{domain}/", image)
            tags.append(f'  <meta property="og:image" content="{html.escape(image, quote=True)}">')
            tags.append('  <meta name="twitter:card" content="summary_large_image">')
        for language in ("en", "ta"):
            if alternate := meta.get(f"alternate_{language}"):
                alternate = urljoin(f"https://{domain}/", alternate)
                tags.append(f'  <link rel="alternate" hreflang="{language}" href="{html.escape(alternate, quote=True)}">')
                if language == "en":
                    tags.append(f'  <link rel="alternate" hreflang="x-default" href="{html.escape(alternate, quote=True)}">')
    if icon := meta.get("icon"):
        tags.append(f'  <link rel="icon" type="image/png" href="{html.escape(icon, quote=True)}">')
    return ("\n".join(tags) + "\n") if tags else ""


def page_shell(source: str, meta: dict[str, str], wrap_inner: str, scripts: str = "") -> str:
    script_block = f"\n{scripts}\n" if scripts else "\n"
    landing = meta.get("layout") == "app"
    language = html.escape(meta.get("lang", "en"), quote=True)
    app_styles = '  <link rel="stylesheet" href="assets/css/apps.css">\n' if landing else ""
    body_attrs = f' class="app-page {html.escape(meta.get("app", ""), quote=True)}"' if landing else ""
    skip_link = '  <a class="skip-link" href="#main">Skip to content</a>\n' if landing else ""
    if landing and meta.get("lang") == "ta":
        skip_link = '  <a class="skip-link" href="#main">உள்ளடக்கத்திற்குச் செல்லவும்</a>\n'
    wrap_tag = 'main id="main" tabindex="-1"' if landing else "div"
    wrap_end = "main" if landing else "div"
    byline = '<footer class="app-footer">Built by <a href="./">Aravind Kumar R</a> · <a href="mailto:aravindkumar.ai@outlook.com">Get in touch</a></footer>' if landing else '<span class="byline">aravind kumar r</span>'
    if landing and meta.get("lang") == "ta":
        byline = '<footer class="app-footer">உருவாக்கம்: <a href="./">அரவிந்த் குமார் R</a> · <a href="mailto:aravindkumar.ai@outlook.com">தொடர்புகொள்ள</a></footer>'
    return f"""<!DOCTYPE html>
<html lang="{language}">
<!-- Generated from {source}. Edit that file, then run: python3 scripts/render.py -->

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(meta["title"])}</title>
{meta_tags(meta)}  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
{app_styles}</head>

<body{body_attrs}>
{skip_link}  <nav class="topnav" aria-label="Primary">
    <div class="topnav-inner">
{nav(meta.get("nav", ""))}
    </div>
  </nav>

  <{wrap_tag} class="wrap">
{wrap_inner}
  </{wrap_end}>

  {byline}{script_block}</body>

</html>
"""


def redirect_page(source: str, meta: dict[str, str]) -> str:
    target = meta.get("redirect", "posts.html")
    label = meta.get("label", "posts")
    return f"""<!DOCTYPE html>
<html lang="en">
<!-- Generated from {source}. Edit that file, then run: python3 scripts/render.py -->
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(meta["title"])}</title>
  <link rel="canonical" href="{html.escape(target, quote=True)}">
  <script>location.replace("{html.escape(target, quote=True)}" + location.hash);</script>
  <meta http-equiv="refresh" content="0; url={html.escape(target, quote=True)}">
</head>
<body>
  <p><a href="{html.escape(target, quote=True)}">{html.escape(label)}</a></p>
</body>
</html>
"""


def render_page(path: Path) -> str:
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
    if "title" not in meta or "layout" not in meta:
        raise SystemExit(f"{path.name} needs title and layout in front matter")
    source = f"content/pages/{path.name}"
    layout = meta["layout"]

    if layout == "redirect":
        return redirect_page(source, meta)

    rendered = render_markdown(body)
    if layout == "posts":
        rendered = promote_note_items(rendered)
        inner = f"    <div id=\"notes-index\">\n{indent(rendered, 6)}\n    </div>\n\n    <article id=\"note\" class=\"note\" hidden></article>"
        scripts = (
            '  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>\n'
            '  <script src="assets/js/notes.js"></script>'
        )
        return theme_shell(source, meta, inner, scripts)

    if layout == "note":
        inner = f"    <article class=\"note\">\n{indent(rendered, 6)}\n    </article>"
        return theme_shell(source, meta, inner)

    if layout == "prose":
        return theme_shell(source, meta, indent(rendered, 4))

    if layout == "app":
        if meta.get("app") not in {"stanza", "suvadi"}:
            raise SystemExit(f"{path.name} needs app: stanza or app: suvadi")
        return page_shell(source, meta, indent(rendered, 4))

    raise SystemExit(f"{path.name} has unknown layout: {layout}")


def main() -> None:
    paths = sorted(PAGES.glob("*.md"))
    if not paths:
        raise SystemExit(f"no markdown pages in {PAGES}")
    for path in paths:
        html_path = ROOT / f"{path.stem}.html"
        html_path.write_text(render_page(path), encoding="utf-8")
        print(f"{path.relative_to(ROOT)} -> {html_path.name}")


if __name__ == "__main__":
    main()
