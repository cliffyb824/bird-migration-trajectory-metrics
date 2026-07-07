# Literature Notes

## Dataset and Animal Tracking Data Infrastructure

### LBBG_ZEEBRUGGE Dataset

Use this as the primary data citation:

Stienen, E. W., Desmet, P., Milotic, T., Hernandez, F., Deneudt, K., Bouten, W., Muller, W., Matheve, H., & Lens, L. (2025). *LBBG_ZEEBRUGGE - Lesser black-backed gulls (Larus fuscus, Laridae) breeding at the southern North Sea coast (Belgium and the Netherlands).* Version 1.3. Research Institute for Nature and Forest (INBO). Occurrence dataset. https://ipt.inbo.be/resource?r=lbbg_zeebrugge&v=1.3

Project links:

- IPT page: https://ipt.inbo.be/resource?r=lbbg_zeebrugge
- Direct archive: https://ipt.inbo.be/archive.do?r=lbbg_zeebrugge&v=1.3
- Zenodo deposit: https://doi.org/10.5281/zenodo.12336021

### Movebank

Useful for data infrastructure context:

Kays, R., Davidson, S. C., Berger, M., Bohrer, G., Fiedler, W., Flack, A., Hirt, J., Hahn, C., Gauggel, D., Russell, B., et al. (2022). The Movebank system for studying global animal movement and demography. *Methods in Ecology and Evolution*, 13(2), 419-431. https://doi.org/10.1111/2041-210X.13767

Movebank citation guidelines also list:

Kranstauber, B., Cameron, A., Weinzierl, R., Fountain, T., Tilak, S., Wikelski, M., & Kays, R. (2011). The Movebank data model for animal tracking. *Environmental Modelling & Software*, 26(6), 834-835. https://doi.org/10.1016/j.envsoft.2010.12.005

## SRVF and Elastic Shape Analysis

### Core SRVF Reference

Srivastava, A., Klassen, E., Joshi, S. H., & Jermyn, I. H. (2011). Shape analysis of elastic curves in Euclidean spaces. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 33(7), 1415-1428. https://doi.org/10.1109/TPAMI.2010.184

Important points:

- Introduces the square-root velocity representation for curve shape analysis.
- Under SRVF, the elastic metric simplifies to an L2 metric.
- Reparameterization acts by isometries under the SRVF framework.
- Useful citation for the mathematical basis of our route representation.

### Earlier Elastic Curve Shape Analysis

Mio, W., Srivastava, A., & Joshi, S. (2007). On shape of plane elastic curves. *International Journal of Computer Vision*, 73, 307-324. https://doi.org/10.1007/s11263-006-9968-0

Useful for general elastic shape-analysis background.

### Shape-Preserving Transformations

Joshi, S. H., Klassen, E., Srivastava, A., & Jermyn, I. (2007). Removing shape-preserving transformations in square-root elastic (SRE) framework for shape analysis of curves. *Energy Minimization Methods in Computer Vision and Pattern Recognition*, 387-398. https://doi.org/10.1007/978-3-540-74198-5_30

Useful for discussing transformations and shape analysis under the square-root elastic framework.

## Dynamic Time Warping

Classic DTW citation:

Sakoe, H., & Chiba, S. (1978). Dynamic programming algorithm optimization for spoken word recognition. *IEEE Transactions on Acoustics, Speech, and Signal Processing*, 26(1), 43-49. https://doi.org/10.1109/TASSP.1978.1163055

Use for:

- DTW alignment in SRVF-DTW.
- General temporal alignment motivation.

## Movement Ecology and Analysis Platforms

Kölzsch, A., Davidson, S. C., Gauggel, D., Hahn, C., Hirt, J., Kays, R., Lang, I., Lohr, A., Russell, B., Scharf, A. K., et al. (2022). MoveApps: a serverless no-code analysis platform for animal tracking data. *Movement Ecology*, 10, 30. https://doi.org/10.1186/s40462-022-00327-4

Useful context:

- Bio-logging and animal tracking datasets are growing in volume and complexity.
- There is a need for accessible analysis workflows and tools.

## Animal Movement Trajectory Similarity

### Directly Relevant Ecology Paper

Cleasby, I. R., Wakefield, E. D., Morrissey, B. J., Bodey, T. W., Votier, S. C., Bearhop, S., & Hamer, K. C. (2019). Using time-series similarity measures to compare animal movement trajectories in ecology. *Behavioral Ecology and Sociobiology*, 73, 151. https://doi.org/10.1007/s00265-019-2761-1

Important points:

- Introduces time-series similarity measures for animal movement trajectories.
- Discusses DTW, LCSS, EDR, Fréchet distance, and nearest-neighbour distance.
- Notes that many similarity measures developed outside ecology remain underused in ecological movement analysis.
- Useful for motivating why trajectory similarity and temporal alignment matter in movement ecology.

### Interdisciplinary Movement Analysis Review

Demšar, U., Buchin, K., Cagnacci, F., Safi, K., Speckmann, B., Van de Weghe, N., Weiskopf, D., & Weibel, R. (2015). Analysis and visualisation of movement: an interdisciplinary review. *Movement Ecology*, 3, 5. https://doi.org/10.1186/s40462-015-0032-y

Important points:

- Reviews movement analysis across ecology, GIScience, and visualization.
- Discusses similarity and clustering as major tasks in trajectory analysis.
- Notes that similarity measures may use spatial, temporal, and movement-attribute information.
- Useful for placing this paper in a broader movement-analysis context.

## Geographic and Spherical Distance Context

### Great-Circle Navigation

Tseng, W.-K., & Lee, H.-S. (2007). The vector function for distance travelled in great circle navigation. *The Journal of Navigation*, 60(1), 158-164. https://doi.org/10.1017/S0373463307214122

Useful for:

- Basic support that great-circle/geodesic reasoning is natural for movement over a spherical Earth model.
- We do not need this heavily, because our spherical embedding is elementary, but it can support the non-planar geographic framing.

### Geographic Context in Trajectory Similarity

Buchin, M., Dodge, S., & Speckmann, B. (2014). Similarity of trajectories taking into account geographic context. *Journal of Spatial Information Science*, 9, 101-124. https://doi.org/10.5311/JOSIS.2014.9.160

Important points:

- Movement trajectories are embedded in geographic context.
- Similarity analysis can combine spatial and contextual distances.
- Useful for arguing that movement comparison should be sensitive to the structure of geographic space, not only raw coordinate sequences.

## How These References Fit the Paper

Introduction:

- Cite Kays et al. 2022 or Kranstauber et al. 2011 for growth and standardization of animal tracking data.
- Cite Kölzsch et al. 2022 for the increasing complexity of bio-logging data and the need for analysis workflows.
- Cite Cleasby et al. 2019 for trajectory similarity in ecology.
- Cite Demšar et al. 2015 for interdisciplinary movement analysis and trajectory clustering.

Data:

- Cite Stienen et al. 2025 dataset.

Methods:

- Cite Srivastava et al. 2011 for SRVF.
- Cite Sakoe and Chiba 1978 for DTW.

Related Work:

- Group references into animal tracking, trajectory comparison, SRVF/elastic shape analysis, and alignment methods.
