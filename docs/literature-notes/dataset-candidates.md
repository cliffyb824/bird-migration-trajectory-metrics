# Dataset Candidates

## Primary Candidate: LifeWatch INBO Gull Tracking Data

**Dataset type:** GPS tracking data for gulls.

**Species:** Start with lesser black-backed gulls (*Larus fuscus*), then optionally add herring gulls (*Larus argentatus*).

**Why this is the best first choice**

- It is directly relevant to bird movement and migration.
- It has a published data paper, which makes citation and methodological justification easier.
- The data are open and have been released through biodiversity data infrastructure.
- The dataset is large enough for route clustering and abnormal-route detection.

**Useful facts to cite**

- The ZooKeys data paper describes GPS tracking data for lesser black-backed gulls and herring gulls breeding at the southern North Sea coast.
- The dataset version described in the paper contains close to 2.5 million occurrences from 101 GPS trackers on 75 lesser black-backed gulls and 26 herring gulls.
- The project is part of the LifeWatch GPS tracking network for large birds and uses UvA-BiTS GPS trackers.
- The original combined dataset has been superseded by newer species-specific datasets, including `LBBG_ZEEBRUGGE`.
- `LBBG_ZEEBRUGGE` is a current occurrence dataset for lesser black-backed gulls breeding at the southern North Sea coast and contains more than 1.8 million occurrence records.
- The data are released under CC0 1.0.

**Main source**

- Stienen et al. (2016), *GPS tracking data of Lesser Black-backed Gulls and Herring Gulls breeding at the southern North Sea coast*, ZooKeys.
- DOI: https://doi.org/10.3897/zookeys.555.6173

**Dataset access leads**

- LifeWatch INBO bird tracking project.
- Movebank public data access.
- GBIF / Darwin Core archive links associated with the LifeWatch INBO gull dataset.
- INBO `bird-tracking` GitHub repository documents publication workflows and dataset tables.
- Current `LBBG_ZEEBRUGGE` IPT page: https://ipt.inbo.be/resource?r=lbbg_zeebrugge
- OBIS page for `LBBG_ZEEBRUGGE`: https://obis.org/dataset/aac5ca81-638a-4335-9aa7-5c2bda67a362

## Dataset Choice for First Manuscript

Use `LBBG_ZEEBRUGGE` as the primary dataset for the first manuscript.

Reasons:

1. It is current and not the deprecated combined dataset.
2. It focuses on one species, which reduces ecological confounding in the first paper.
3. It is large enough for clustering and anomaly detection.
4. It is standardized through Darwin Core / biodiversity data infrastructure.
5. It is CC0, which simplifies reuse.

## Secondary Candidate: Kaggle Three-Gull Dataset

**Dataset type:** Small CSV with GPS tracks for three gulls: Eric, Nico, and Sanne.

**Why it is useful**

- Very easy for a first code prototype.
- Small enough to debug plotting, preprocessing, and SRVF transforms quickly.

**Why it is not enough for the journal paper**

- Only three birds.
- Better suited for teaching or prototyping than publication-scale evaluation.
- Use only as a sandbox, not the main dataset.

## Dataset Decision

Use `LBBG_ZEEBRUGGE` as the paper dataset.

Use the smaller three-gull CSV only if a quick prototype is needed before handling the larger open dataset.

## Immediate Data Tasks

1. Locate the most convenient downloadable version of `LBBG_ZEEBRUGGE`.
2. Confirm license and citation requirements.
3. Download a manageable subset first.
4. Extract columns needed for the first prototype:
   - individual ID;
   - timestamp;
   - latitude;
   - longitude;
   - species;
   - optional altitude or speed if available.
5. Build one clean trajectory per bird and migration season.
