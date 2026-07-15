.PHONY: all render restore clean

all: render

## render : build hub landing + web CV + both PDFs + machine-readable JSON into output/
render:
	quarto render engine
	cp hub/index.html output/index.html
	mkdir -p output/assets && cp hub/assets/* output/assets/
	@[ -f hub/writing/posts.json ] && python3 tools/build_writing.py && rm -rf output/writing && cp -R hub/writing output/writing || true
	@[ -f tools/build_talks.py ] && python3 tools/build_talks.py && bun $(HOME)/.claude/skills/Marginalia/Tools/BuildPage.ts --in hub/talks/index.src.html --out hub/talks/index.html --fonts $(HOME)/.claude/skills/Groundtruth/Fonts.css && rm -f hub/talks/index.src.html && rm -rf output/talks && cp -R hub/talks output/talks || true
	@[ -f tools/build_profile.py ] && python3 tools/build_profile.py || true
	cp data/resume.json output/resume.json
	@rm -f engine/Rplots.pdf output/Rplots.pdf 2>/dev/null || true
	@echo "Built output/{index.html (hub), cv.html, resume.pdf, cv.pdf, resume.json}"

## restore : restore the exact pinned R environment from renv.lock
restore:
	Rscript -e 'if (!requireNamespace("renv", quietly=TRUE)) install.packages("renv"); renv::restore(lockfile="renv.lock", prompt=FALSE)'

## clean : remove build artifacts
clean:
	rm -rf output/*.html output/*.pdf output/resume.json output/assets output/writing output/talks engine/.quarto engine/*_files
