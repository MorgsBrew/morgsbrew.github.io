#!/usr/bin/env python3
"""Generate the GitHub *profile* README from resume.json.

Destination: the special `morgsbrew/morgsbrew` repo, whose README renders as the
card at github.com/MorgsBrew. GitHub sanitises HTML/CSS in READMEs, so this is
plain Markdown — no fonts, no styled cards. What it shares with the hub is VOICE
(the `//` section markers, "reached, not shouted") and its SOURCE: the volatile
facts — handle, links, degree year, talk count, the publication — are pulled from
data/resume.json, exactly like the talks page pulls meta.conferences. The prose is
the template; the facts are single-sourced. Run from anywhere.

Writes projects/cv/profile/README.md. Copy that file into the morgsbrew/morgsbrew
repo to publish it.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (parent of tools/)
OUT_DIR = os.path.join(ROOT, "profile")

SITE = "https://morgsbrew.github.io"          # the GitHub Pages keystone site
THESIS_REPO = "brand_2021"                     # the public thesis-code repo (also linked from the hub)


def profile(net):
    """Return the profile dict for a given network name, or {}."""
    for p in RESUME["basics"].get("profiles", []):
        if p.get("network", "").lower() == net.lower():
            return p
    return {}


def main():
    global RESUME
    with open(os.path.join(ROOT, "data", "resume.json")) as fh:
        RESUME = json.load(fh)

    b = RESUME["basics"]
    meta = RESUME["meta"]
    gh = profile("GitHub").get("username", "morgsbrew")
    yt = profile("YouTube").get("url", "")
    orcid = profile("ORCID").get("url", "")
    linkedin = profile("LinkedIn").get("url", "")
    x_url = profile("X").get("url", "") or profile("Twitter").get("url", "")   # sole public contact channel
    region = b.get("location", {}).get("region", "")
    tagline = meta.get("tagline", "imagine ‹ create ‹ change")
    talks = len(meta.get("conferences", []))

    # PhD year from the education entry whose studyType mentions "Doctor"
    phd_year = ""
    for e in RESUME.get("education", []):
        if "doctor" in (e.get("studyType", "") + e.get("area", "")).lower() or "phd" in e.get("studyType", "").lower():
            phd_year = (e.get("endDate", "") or "").split("-")[0]
            break

    # the single publication → short title (up to the first "?") for the record line
    pub = (RESUME.get("publications") or [{}])[0]
    pub_name = pub.get("name", "")
    pub_short = pub_name.split("?")[0] + "?" if "?" in pub_name else pub_name
    pub_year = (pub.get("releaseDate", "") or "").split("-")[0]
    pub_pub = pub.get("publisher", "")
    pub_url = pub.get("url", "")

    # YouTube video count, if the channel entry in meta.communication states it
    yt_line = "how-to videos translating hands-on science for a general audience"

    # The profile README is a DOORWAY, not a copy of the hub. Short intro → the full
    # site. GitHub renders the pinned repos natively beside this, so it doesn't
    # re-list them. (unused-below locals are kept so a fuller variant is one edit away.)
    md = f"""# {tagline}

**`{gh}`** &middot; generalist scientist &amp; grower &middot; {region} coast &nbsp;🌱

I read how a system behaves — a microbiome, a hillside, a codebase — closely enough to
work with how it already runs, and turn messy real-world data into something clear
enough to act on.

### &rarr; The full picture lives at **[morgsbrew.github.io]({SITE})**

Portfolio, work, talks, writing, and the record — one page that rebuilds itself from a
single `resume.json`. The pinned repos below are the public code.

Reach me on **[X]({x_url})**. Reached, not shouted.
"""

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "README.md"), "w") as fh:
        fh.write(md)
    print("Built profile/README.md ({} talks, PhD {}, pub {})".format(talks, phd_year, pub_year))


if __name__ == "__main__":
    main()
