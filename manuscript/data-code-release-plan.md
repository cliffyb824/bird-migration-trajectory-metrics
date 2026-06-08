# Data and Code Release Plan

## Data

The raw GPS tracking data should not be redistributed inside the project repository unless necessary. The source dataset is already public and citable:

`LBBG_ZEEBRUGGE`, version 1.3, INBO.

Dataset page:

<https://ipt.inbo.be/resource?r=lbbg_zeebrugge>

Direct archive:

<https://ipt.inbo.be/archive.do?r=lbbg_zeebrugge&v=1.3>

License:

CC0 1.0

## Code

The analysis code can be released under the MIT License.

Local license file:

`LICENSE`

## Recommended Repository Contents

Include:

- `src/`
- `manuscript/`
- `references/`
- `figures/`
- `requirements.txt`
- `reproducibility.md`
- `README.md`
- `REPOSITORY_README.md`
- `LICENSE`

Do not include large raw data files:

- `data/raw/lbbg_zeebrugge/occurrence.txt`
- `data/raw/lbbg_zeebrugge_v1_3_dwca.zip`

Optional:

- include small processed summaries;
- include generated result CSVs needed to reproduce tables;
- include scripts to regenerate all processed outputs from the public source archive.

## `.gitignore`

Implemented at:

`.gitignore`

Current contents exclude raw data, generated processed CSV files, Python caches, virtual environments, and OS/editor noise.

## Suggested `.gitignore`

```gitignore
data/raw/
data/processed/*.csv
src/__pycache__/
*.pyc
```

If result CSVs are needed for review, place selected small files in a separate `results/` folder rather than committing all processed data.

## Code Availability Text

Current public repository:

<https://github.com/cliffyb824/bird-migration-trajectory-metrics>

If archived with Zenodo:

> A versioned archive of the code is available at [DOI].

## Before Submission

1. Create a Git repository.
2. Remove or ignore large raw data files.
3. Add a clean README with reproduction commands.
4. Add repository URL to the manuscript. Completed.
5. Optionally archive a release on Zenodo and add DOI.
