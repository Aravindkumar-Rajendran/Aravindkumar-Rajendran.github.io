# Aravind Kumar - Personal Portfolio & Technical Blog

A short, type-only portfolio for **Aravind Kumar** (Senior AI & Machine Learning Engineer). Hosted natively on **GitHub Pages**.

🔗 **Live Website**: [https://aravindkumar-ai.github.io/](https://aravindkumar-ai.github.io/)  
💼 **LinkedIn**: [https://www.linkedin.com/in/aravindkumar-ai/](https://www.linkedin.com/in/aravindkumar-ai/)

---

## Key features

- **GitHub Pages native**: the site serves the generated HTML, CSS, and a small posts script.
- **Pages are Markdown**: edit `content/pages/`, then render HTML with `python3 scripts/render.py`.
- **Homepage**: a narrow column of prose, with the same links in the top bar.
- **Posts**: `posts.html` loads the Markdown posts in `content/posts/` from `content/blogs.json`.

---

## Editing a page

Home, apps, posts, projects, resume, and the notes redirect are Markdown files in `content/pages/`:

| File | Page |
| --- | --- |
| `content/pages/index.md` | `index.html` |
| `content/pages/apps.md` | `apps.html` (StanZa and Suvadi directory) |
| `content/pages/posts.md` | `posts.html` |
| `content/pages/projects.md` | `projects.html` |
| `content/pages/resume.md` | `resume.html` |
| `content/pages/notes.md` | `notes.html` (sends people to posts) |
| `content/pages/stanza.md` | `stanza.html` (StanZa landing page) |
| `content/pages/suvadi.md` | `suvadi.html` (Suvadi, English) |
| `content/pages/suvadi-ta.md` | `suvadi-ta.html` (Suvadi, Tamil) |

```bash
python3 -m pip install -r scripts/requirements.txt
python3 scripts/render.py
```

Write normal Markdown. A paragraph that is only italics, such as `*2026 · Bengaluru*`, renders as the gray meta line. On the posts page, a link on its own followed by one of those lines becomes a listed article. A line that is exactly `{{posts}}` is where the on-site essays are inserted. Each essay is still a file in `content/posts/`, registered in `content/blogs.json`.

The app pages use `layout: app` and `app: stanza` or `app: suvadi`. Their Markdown
sources include semantic HTML for the hero, screenshot figures, and native FAQ
disclosures. Edit these sources rather than generated HTML. `assets/css/apps.css`
contains the scoped app themes on top of `assets/css/style.css`. Every other page
uses `assets/css/theme.css` (Clash Display + Satoshi from Fontshare, floating nav).

The homepage hero is set in `content/pages/index.md` front matter with
`hero_kicker`, `hero_title`, `hero_accent` (the gradient phrase), `hero_lede`,
`hero_cta` / `hero_cta_href`, and `hero_link` / `hero_link_href`. Any prose page
with `hero_title` gets a hero.

Optional front matter includes `lang`, `canonical`, `image`, `icon`,
`alternate_en`, and `alternate_ta`. Canonical and social-preview URLs are resolved
against the domain in `CNAME`. Suvadi's English/Tamil switch links static pages;
it needs no JavaScript.

Artwork and screenshots come from the app projects' October 2026 listing packs.
`assets/apps/manifest.json` records source assets, output dimensions and sizes.
StanZa screenshots show sample learning data. Suvadi captures retain the real
landscape UI, including existing English control labels in Tamil screens.

---

## 📝 How to Add a New Blog Post

Adding a new blog post is simple:

1. **Create a Markdown File**  
   Add a new `.md` file inside `content/posts/`, e.g. `content/posts/my-new-article.md`.

2. **Write Your Article**  
   Write standard Markdown:

   ```markdown
   # My New Article Title

   Summary of the article...

   ```python
   def hello_agent():
       print("Hello from Claude Agent SDK!")
   ```
   ```

3. **Register in `content/blogs.json`**  
   Add an entry in `content/blogs.json`:

   ```json
   {
     "slug": "my-new-article",
     "title": "My New Article Title",
     "summary": "Short description of the note.",
     "date": "August 2026",
     "readTime": "5 min read",
     "tags": ["AIAgents", "Python", "LLMs"]
   }
   ```

4. **Push to GitHub**  
   Push to the `master` branch. GitHub Pages will deploy it automatically!

---

## 🚀 Local Development & Preview

```bash
# Preview locally using Python built-in HTTP server
python3 -m http.server 8000
```
Open `http://localhost:8000` in your web browser.
