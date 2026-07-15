#!/usr/bin/env python3
"""Generate the speaking-record landing (hub/talks/) from resume.json.

Single source of truth: data/resume.json -> meta.conferences (the SAME array the
Quarto CV renders via emit_conferences). This is not a duplicate of the CV — it
is a second render of one source, exactly like resume.json -> {CV, résumé}.

Emits hub/talks/index.src.html in the house (Groundtruth) theme, with the
/*__MARGINALIA_FONTS__*/ marker so the BuildPage step embeds the same fonts as the
hub. Run from anywhere; paths resolve relative to the repo root. After this runs,
the Makefile runs BuildPage on the .src.html to produce the self-contained page.
"""
import json
import os
import re
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (parent of tools/)
TDIR = os.path.join(ROOT, "hub", "talks")

# species names get italicised wherever they appear in a talk title/note
SPECIES = ["Haliotis midae", "Ulva"]


def italicise_species(text):
    """Escape text, then wrap known species names in <em>. Order matters:
    the two-word binomial before the genus so it is not double-wrapped."""
    out = escape(text)
    for sp in SPECIES:
        out = re.sub(r"\b" + re.escape(sp) + r"\b", "<em>" + sp + "</em>", out)
    return out


HEAD = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Speaking — morgsbrew</title>
<style>
  /*__MARGINALIA_FONTS__*/
  :root {
    --ground: #0A0C0B; --panel: #141614; --ink: #E9EDE3; --muted: #A9B4AC;
    --blue: #4FA3D1; --green: #4FCE7E; --purple: #A98FE0; --coral: #E8794E;
    --link: #4FCE7E;
    --line: rgba(233,237,227,0.14); --line-soft: rgba(233,237,227,0.075);
    --sans: 'Hanken Grotesk', system-ui, -apple-system, 'Segoe UI', sans-serif;
    --mono: 'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
  }
  * { box-sizing: border-box; }
  body { background: var(--ground); color: var(--ink); font-family: var(--sans);
    font-size: 18px; line-height: 1.7; margin: 0; -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility; }
  .wrap { max-width: 760px; margin: 0 auto; padding: 0 26px 120px; }
  a { color: var(--link); text-decoration: none;
    border-bottom: 1px solid color-mix(in srgb, var(--link) 45%, transparent); }
  a:hover { border-bottom-color: var(--link); }

  .back { font-family: var(--mono); font-size: 13px; color: var(--muted);
    letter-spacing: 0.02em; padding: 30px 0 0; margin: 0 0 clamp(40px, 7vw, 68px); }
  .back a { color: var(--muted); border-bottom: 1px solid var(--line-soft); }
  .back a:hover { color: var(--link); border-bottom-color: var(--link); }

  header.thead { border-bottom: 1px solid var(--line); padding-bottom: clamp(30px, 5vw, 48px);
    margin-bottom: clamp(30px, 5vw, 50px); }
  .kicker { font-family: var(--mono); font-size: 14px; font-weight: 600; color: var(--green);
    letter-spacing: 0.06em; margin: 0 0 18px; }
  h1 { font-family: var(--sans); font-weight: 800; font-size: clamp(40px, 8vw, 76px);
    line-height: 0.98; letter-spacing: -0.03em; margin: 0 0 22px; }
  .lede { font-size: clamp(19px, 2.4vw, 23px); line-height: 1.5; color: var(--ink);
    font-weight: 400; max-width: 40ch; margin: 0; }
  .lede em { font-style: italic; }

  /* timeline of talks — year rail (green) + body */
  .talks { display: flex; flex-direction: column; }
  .talk { display: grid; grid-template-columns: 88px 1fr; gap: 0 24px;
    padding: 22px 0; border-top: 1px solid var(--line-soft); }
  .talk:first-child { border-top: 0; }
  .tyear { font-family: var(--mono); font-size: 17px; font-weight: 700; color: var(--green);
    letter-spacing: 0.01em; padding-top: 2px; }
  .tvenue { font-family: var(--mono); font-size: 12.5px; color: var(--muted);
    letter-spacing: 0.03em; text-transform: uppercase; margin: 0 0 8px; }
  .ttitle { font-family: var(--sans); font-weight: 600; font-size: 20px; line-height: 1.3;
    color: var(--ink); margin: 0; letter-spacing: -0.01em; }
  .ttitle em { font-style: italic; }
  .tnote { font-size: 15.5px; line-height: 1.55; color: color-mix(in srgb, var(--ink) 78%, var(--ground));
    margin: 9px 0 0; }
  .award { display: inline-flex; align-items: center; gap: 7px; font-family: var(--mono);
    font-size: 11.5px; font-weight: 600; letter-spacing: 0.03em; color: var(--green);
    background: color-mix(in srgb, var(--green) 12%, transparent);
    border: 1px solid color-mix(in srgb, var(--green) 30%, transparent);
    border-radius: 999px; padding: 4px 11px; margin: 10px 0 0; }

  footer.foot { margin-top: clamp(50px, 8vw, 84px); padding-top: 22px;
    border-top: 1px solid var(--line); font-family: var(--mono); font-size: 13px;
    color: var(--muted); line-height: 1.9; }
  footer.foot a { color: var(--muted); border-bottom: 1px solid var(--line-soft); }
  footer.foot a:hover { color: var(--link); }

  @media (max-width: 560px) {
    .wrap { padding: 0 18px 80px; }
    .talk { grid-template-columns: 1fr; gap: 6px 0; }
    .tyear { font-size: 15px; }
  }
</style>

<div class="wrap">
  <nav class="back">&#8592; <a href="../index.html">morgsbrew</a> &nbsp;/&nbsp; speaking</nav>
"""

FOOT = """  <footer class="foot">morgsbrew &middot; the talks are also in <a href="../cv.html">the CV</a> &middot; rendered from one <code>resume.json</code></footer>
</div>
"""


def talk_row(t):
    venue = escape(t["event"]) + " &middot; " + escape(t["location"])
    title = italicise_species(t["title"])
    parts = ['  <article class="talk">']
    parts.append('    <div class="tyear">{}</div>'.format(escape(str(t["year"]))))
    parts.append('    <div class="tbody">')
    parts.append('      <p class="tvenue">{}</p>'.format(venue))
    parts.append('      <h2 class="ttitle">{}</h2>'.format(title))
    note = (t.get("note") or "").strip()
    if note:
        low = note.lower()
        if "best presentation" in low:
            # split the award out into a coral pill; keep the rest as a note
            rest = re.sub(r"awarded best presentation[;.]?\s*", "", note, flags=re.I).strip()
            parts.append('      <span class="award">&#9733; best presentation</span>')
            if rest:
                parts.append('      <p class="tnote">{}</p>'.format(italicise_species(rest[0].upper() + rest[1:])))
        else:
            parts.append('      <p class="tnote">{}</p>'.format(italicise_species(note)))
    parts.append("    </div>")
    parts.append("  </article>")
    return "\n".join(parts)


def main():
    with open(os.path.join(ROOT, "data", "resume.json")) as fh:
        resume = json.load(fh)
    talks = resume["meta"]["conferences"]
    talks = sorted(talks, key=lambda t: t.get("date") or str(t.get("year", "")))  # chronological
    years = [int(t["year"]) for t in talks if str(t.get("year", "")).isdigit()]
    span = "{}–{}".format(min(years), max(years)) if years else ""

    parts = [HEAD]
    parts.append('  <header class="thead">')
    parts.append('    <p class="kicker">// speaking</p>')
    parts.append("    <h1>{} talks</h1>".format(_words(len(talks)).capitalize()))
    parts.append('    <p class="lede">Conference talks, {span} &mdash; abalone, '
                 "<em>Ulva</em>, and reproducible science, across three continents.</p>".format(span=span))
    parts.append("  </header>")
    parts.append('  <div class="talks">')
    parts.extend(talk_row(t) for t in talks)
    parts.append("  </div>")
    parts.append(FOOT)

    os.makedirs(TDIR, exist_ok=True)
    with open(os.path.join(TDIR, "index.src.html"), "w") as fh:
        fh.write("\n".join(parts) + "\n")
    print("Built talks/index.src.html ({} talks, {})".format(len(talks), span))


def _words(n):
    names = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
             7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    return names.get(n, str(n))


if __name__ == "__main__":
    main()
