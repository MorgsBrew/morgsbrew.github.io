#!/usr/bin/env python3
"""Generate the Fresh Rots writing section from hub/writing/posts.json.

Source of truth: hub/writing/posts.json (the cleaned, lightly copy-edited post
bodies). This script wraps each post's body HTML in the house template and builds
the index. Run from anywhere; paths are resolved relative to the repo root.
Images referenced as img/<name> must already sit in hub/writing/img/.
"""
import json
import os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (parent of tools/)
WDIR = os.path.join(ROOT, "hub", "writing")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<link rel="stylesheet" href="fonts.css">
<link rel="stylesheet" href="{css}">
</head>
<body>
<div class="wrap">
"""
FOOT = """  <footer class="foot">Fresh Rots · collected writing by Morgan Brand · <a href="../index.html">portfolio</a></footer>
</div>
</body>
</html>
"""


def post_page(p):
    parts = [HEAD.format(title=escape(p["title"]) + " — Morgan Brand", css="style.css")]
    parts.append('  <nav class="topnav"><a href="../index.html">← portfolio</a> '
                 '· <a href="index.html">writing</a></nav>\n')
    parts.append("  <article>\n")
    parts.append('    <p class="post-date">{}</p>\n'.format(escape(p["date"])))
    parts.append("    <h1>{}</h1>\n".format(escape(p["title"])))
    parts.append(p["body_html"])  # raw, already-clean HTML body
    parts.append("\n  </article>\n")
    parts.append(FOOT)
    return "".join(parts)


def index_page(posts):
    parts = [HEAD.format(title="Writing — Morgan Brand", css="style.css")]
    parts.append('  <nav class="topnav"><a href="../index.html">← portfolio</a></nav>\n')
    parts.append('  <header class="w-head">\n')
    parts.append('    <p class="kicker">// writing</p>\n')
    parts.append("    <h1>Fresh Rots</h1>\n")
    parts.append('    <p class="lede">A collection of my writing, 2010–2019 — '
                 "the land, science, and building things by hand.</p>\n")
    parts.append("  </header>\n")
    parts.append('  <ul class="post-list">\n')
    for p in posts:
        parts.append("    <li><a href=\"{slug}.html\">"
                     '<span class="pdate">{date}</span>'
                     '<span class="ptitle">{title}</span></a>'
                     '<p class="psum">{sum}</p></li>\n'.format(
                         slug=escape(p["slug"]), date=escape(p["date"]),
                         title=escape(p["title"]), sum=escape(p.get("summary", ""))))
    parts.append("  </ul>\n")
    parts.append(FOOT)
    return "".join(parts)


def main():
    with open(os.path.join(WDIR, "posts.json")) as fh:
        posts = json.load(fh)
    posts = [p for p in posts if p.get("is_real_post", True)]
    posts.sort(key=lambda p: p.get("date", ""))  # chronological, oldest first
    for p in posts:
        with open(os.path.join(WDIR, p["slug"] + ".html"), "w") as fh:
            fh.write(post_page(p))
    with open(os.path.join(WDIR, "index.html"), "w") as fh:
        fh.write(index_page(posts))
    print("Built writing/: index.html + {} post pages".format(len(posts)))


if __name__ == "__main__":
    main()
