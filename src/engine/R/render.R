# render.R — read the JSON Resume source and emit Quarto markdown sections.
# One source of truth (data/resume.json) drives all three outputs (web + 2 PDFs).
# Emitters produce plain Quarto/pandoc markdown so the same code works for
# HTML and Typst. Called from `results='asis'` chunks in the .qmd files.

suppressPackageStartupMessages(library(jsonlite))

`%||%` <- function(a, b) {
  if (is.null(a) || length(a) == 0) return(b)
  if (is.character(a) && length(a) == 1 && !nzchar(a)) return(b)
  a
}

# Escape pandoc-significant characters in free text. `@handle` would otherwise
# be parsed as a citation key (breaks Typst); escape it to render literally.
esc_at <- function(x) if (is.character(x)) gsub("@", "\\\\@", x) else x

cv_load <- function(path = NULL) {
  if (is.null(path)) {
    candidates <- c("../data/resume.json", "data/resume.json", "resume.json")
    hit <- candidates[file.exists(candidates)]
    if (!length(hit)) stop("resume.json not found (looked in: ", paste(candidates, collapse = ", "), ")")
    path <- hit[1]
  }
  jsonlite::fromJSON(path, simplifyVector = FALSE)
}

.daterange <- function(start, end) {
  start <- start %||% ""; end <- end %||% ""
  if (nzchar(start) && nzchar(end)) return(paste0(start, "–", end))
  if (nzchar(start) && !nzchar(end)) return(paste0(start, "–present"))
  if (!nzchar(start) && nzchar(end)) return(end)
  ""
}

# --- section emitters ------------------------------------------------------
# variant: "resume" (curated, featured-only) or "cv" (full)

emit_summary <- function(cv) {
  cat(esc_at(cv$basics$summary %||% ""), "\n\n", sep = "")
}

emit_contact_line <- function(cv, sep = " · ") {
  b <- cv$basics
  parts <- character(0)
  if (nzchar(b$email %||% "")) parts <- c(parts, sprintf("[%s](mailto:%s)", b$email, b$email))
  if (nzchar(b$phone %||% "")) parts <- c(parts, b$phone)
  for (p in b$profiles) {
    if (nzchar(p$url %||% "")) {
      parts <- c(parts, sprintf("[%s](%s)", p$network, p$url))
    } else {
      parts <- c(parts, sprintf("%s: %s", p$network, p$username))
    }
  }
  cat(paste(parts, collapse = sep), "\n\n", sep = "")
}

emit_skills <- function(cv, variant = "cv") {
  for (s in cv$skills) {
    kw <- unlist(s$keywords)
    lvl <- if (variant == "cv" && nzchar(s$level %||% "")) sprintf(" (%s)", s$level) else ""
    kws <- if (length(kw)) sprintf(" — %s", paste(kw, collapse = ", ")) else ""
    cat(sprintf("- **%s**%s%s\n", s$name, lvl, kws))
  }
  cat("\n")
}

emit_education <- function(cv, variant = "cv") {
  for (e in cv$education) {
    if (variant == "resume" && !isTRUE(e$featured)) next
    yr <- .daterange(e$startDate, e$endDate)
    cat(sprintf("**%s** — %s  \n", e$studyType, e$area))
    cat(sprintf("%s%s  \n", e$institution, if (nzchar(yr)) paste0("  ·  ", yr) else ""))
    th <- e$thesis %||% ""
    if (nzchar(th)) cat(sprintf("*Thesis:* %s  \n", th))
    cat("\n")
  }
}

emit_work <- function(cv, variant = "cv") {
  for (w in cv$work) {
    if (variant == "resume" && !isTRUE(w$featured)) next
    yr <- .daterange(w$startDate, w$endDate)
    loc <- if (nzchar(w$location %||% "")) paste0("  ·  ", w$location) else ""
    header <- sprintf("**%s** — %s%s%s", w$position, w$name, loc,
                      if (nzchar(yr)) paste0("  ·  ", yr) else "")
    block <- header
    if (nzchar(w$summary %||% "")) block <- c(block, esc_at(w$summary))
    # join header + summary with hard line breaks, close with a blank line so a
    # following bullet list is parsed as a list (not inline paragraph text)
    cat(paste(block, collapse = "  \n"), "\n\n", sep = "")
    hl <- unlist(w$highlights)
    if (length(hl)) {
      if (variant == "resume") hl <- head(hl, 3)
      for (h in hl) cat(sprintf("- %s\n", esc_at(h)))
      cat("\n")
    }
  }
}

emit_publications <- function(cv) {
  for (p in cv$publications) {
    yr <- if (nzchar(p$releaseDate %||% "")) sprintf(" (%s)", p$releaseDate) else ""
    link <- if (nzchar(p$url %||% "")) sprintf("[%s](%s)", p$doi %||% p$url, p$url) else ""
    pub <- if (nzchar(p$publisher %||% "")) sprintf("*%s*. ", p$publisher) else ""
    cat(sprintf("%s%s. **%s**. %s%s\n\n", p$authors %||% "", yr, p$name, pub, link))
  }
}

emit_conferences <- function(cv) {
  conf <- cv$meta$conferences
  if (is.null(conf) || !length(conf)) return(invisible())
  for (c in conf) {
    loc  <- if (nzchar(c$location %||% "")) sprintf(" · %s", esc_at(c$location)) else ""
    ttl  <- if (nzchar(c$title %||% "")) sprintf(" — *%s*", esc_at(c$title)) else ""
    note <- if (nzchar(c$note %||% "")) sprintf(". %s", esc_at(c$note)) else ""
    cat(sprintf("- **%s** — %s%s%s%s\n", c$year, esc_at(c$event), loc, ttl, note))
  }
  cat("\n")
}

emit_communication <- function(cv) {
  comm <- cv$meta$communication
  if (is.null(comm) || !length(comm)) return(invisible())
  for (m in comm) {
    bits <- character(0)
    for (k in c("handle", "venue", "period", "date", "role", "license")) {
      if (nzchar(m[[k]] %||% "")) bits <- c(bits, esc_at(m[[k]]))
    }
    meta <- if (length(bits)) sprintf(" — %s", paste(bits, collapse = " · ")) else ""
    title <- if (nzchar(m$url %||% "")) sprintf("[%s](%s)", esc_at(m$title), m$url) else esc_at(m$title)
    cat(sprintf("**%s**%s  \n", title, meta))
    if (nzchar(m$collaborators %||% "")) cat(sprintf("with %s  \n", esc_at(m$collaborators)))
    if (nzchar(m$summary %||% "")) cat(sprintf("%s  \n", esc_at(m$summary)))
    cat("\n")
  }
}

emit_references <- function(cv) {
  # Private overlay: full referee details only when data/references.private.json
  # is present (local builds). CI / a fresh clone lack it → "available on request".
  refs <- cv$references
  priv <- c("../data/references.private.json", "data/references.private.json")
  priv <- priv[file.exists(priv)]
  if (length(priv)) refs <- jsonlite::fromJSON(priv[1], simplifyVector = FALSE)$references
  if (is.null(refs) || !length(refs)) {
    cat("*References available on request.*\n\n")
    return(invisible())
  }
  for (r in refs) {
    org <- if (nzchar(r$organization %||% "")) sprintf(" — %s", r$organization) else ""
    cat(sprintf("**%s**%s  \n", r$name, org))
    if (nzchar(r$email %||% "")) cat(sprintf("<%s>  \n", r$email))
    cat("\n")
  }
}
