# Generate a fully commit-pinned Nix environment for building this CV.
#
# This is the reproducibility CEILING. `renv.lock` pins the R packages; Nix
# additionally pins the R interpreter itself and all system libraries to an
# exact nixpkgs revision, giving a bit-reproducible build on any machine, now
# or years from now.
#
# It is a GENERATOR, not a hand-written default.nix: {rix} looks up the exact
# nixpkgs snapshot that carried these package versions, so the emitted
# default.nix is deterministic and honest (no guessed hashes).
#
#   install.packages("rix")        # once
#   Rscript nix/generate_env.R     # writes ./default.nix
#   nix-shell                      # drop into the pinned env, then: make render
#
# See: https://docs.ropensci.org/rix/

library(rix)

rix(
  date       = "2025-01-06",                         # pins the nixpkgs snapshot
  r_pkgs     = c("jsonlite", "knitr", "rmarkdown"),
  system_pkgs = "quarto",
  ide        = "none",
  project_path = ".",
  overwrite  = TRUE
)

cat("Wrote ./default.nix — run `nix-shell` then `make render`.\n")
