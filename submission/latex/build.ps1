$ErrorActionPreference = "Stop"

$latexDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $latexDir

pdflatex -interaction=nonstopmode -halt-on-error main.tex
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
bibtex main
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Built main.pdf"
