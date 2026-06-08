# Data Acquisition

## Primary Dataset

Dataset: `LBBG_ZEEBRUGGE`

Full title: *LBBG_ZEEBRUGGE - Lesser black-backed gulls (Larus fuscus, Laridae) breeding at the southern North Sea coast (Belgium and the Netherlands)*

Publisher: Research Institute for Nature and Forest (INBO)

Current version used for this project: `v1.3`

Publication date: 25 August 2025

License: CC0 1.0

Records: 1,801,214 occurrence records

IPT page:

<https://ipt.inbo.be/resource?r=lbbg_zeebrugge>

Direct Darwin Core Archive download:

<https://ipt.inbo.be/archive.do?r=lbbg_zeebrugge&v=1.3>

Movebank study:

<https://www.movebank.org/cms/webapp?gwt_fragment=page=studies,path=study985143423>

Zenodo source deposit:

<https://doi.org/10.5281/zenodo.12336021>

## Citation

Use the dataset citation from the IPT page:

Stienen E. W., Desmet P., Milotic T., Hernandez F., Deneudt K., Bouten W., Muller W., Matheve H., Lens L. (2025). *LBBG_ZEEBRUGGE - Lesser black-backed gulls (Larus fuscus, Laridae) breeding at the southern North Sea coast (Belgium and the Netherlands).* Version 1.3. Research Institute for Nature and Forest (INBO). Occurrence dataset. <https://ipt.inbo.be/resource?r=lbbg_zeebrugge&v=1.3>

## Why This Dataset

This is the best first dataset because:

1. It is current and species-specific.
2. It has a formal biodiversity-data publication page.
3. It is large enough for clustering and anomaly detection.
4. It is downsampled to the first GPS position per hour, which is manageable for trajectory analysis.
5. It is CC0, so reuse is straightforward.

## Local Data Workflow

1. Download the Darwin Core Archive into `data/raw/`.
2. Extract the archive into `data/raw/lbbg_zeebrugge/`.
3. Inspect the included metadata and occurrence table.
4. Standardize the occurrence table to:
   - `individual_id`
   - `timestamp`
   - `latitude`
   - `longitude`
   - optional `species`
5. Save the standardized file as:

`data/processed/lbbg_zeebrugge_standardized.csv`

## Notes

The IPT page states that the data have been standardized to Darwin Core using the `movepub` R package and are downsampled to the first GPS position per hour. This is useful for our paper because it gives a cleaner and more manageable trajectory table than raw high-frequency tracker data.
