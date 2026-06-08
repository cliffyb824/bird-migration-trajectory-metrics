# Elsevier LaTeX Submission Package

This directory uses Elsevier's `elsarticle` document class with author-year
citations.

## Build

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

Expected outputs:

- `main.pdf`

## Source Files

- `main.tex`: manuscript frontmatter, declarations, and bibliography setup.
- `body.tex`: manuscript body.
- `references.bib`: BibTeX database.
- `highlights.tex`: separate highlights source.

The revised uncertainty-aware manuscript is maintained directly in LaTeX.
Main figures are referenced from the project-level `figures/` directory.
