#!/usr/bin/env bash
# Reproducible one-command build: render every CV surface from data/resume.json.
set -euo pipefail
cd "$(dirname "$0")/.."          # repo root

quarto render engine
cp hub/index.html output/index.html          # Groundtruth portfolio hub → landing page
mkdir -p output/assets && cp hub/assets/* output/assets/   # hub images (KZN map, …)
if [ -f hub/writing/posts.json ]; then                     # Fresh Rots writing section
  python3 tools/build_writing.py
  rm -rf output/writing && cp -R hub/writing output/writing
fi
cp data/resume.json output/resume.json
rm -f engine/Rplots.pdf output/Rplots.pdf 2>/dev/null || true

echo "Built:"
echo "  output/index.html   (portfolio hub — Groundtruth theme)"
echo "  output/cv.html      (detailed web CV)"
echo "  output/resume.pdf   (1-page résumé)"
echo "  output/cv.pdf       (academic CV)"
echo "  output/resume.json  (machine-readable, JSON Resume schema)"
