Below is a brief description of files and subfolders in this directory.

### [MP_CompleteDataset_SuppMat.xlsx](MP_CompleteDataset_SuppMat.xlsx) is a spreadsheet with :
 - X-ray µCT scans metadata for single and replicate scans
 - Calibration and mass test results for single and replicate scans
 - Calibration and mass test results for the crossover experiment (internal vs. external calibration)
 - Bulk correction results for replicate scans

**Units**:
- Mass Offsets : [\%]
- Mass (Weights) : [g]
- Voxel size: [mm]
- Specimen volume : [cm<sup>3</sup>]
- SurfaceArea : [mm<sup>2</sup>]
- AreaOverVol: [cm<sup>-1</sup>]
- Density: [g cm<sup>-3</sup>]


### [ROI_AnalysesBulkCorrection](ROI_AnalysesBulkCorrection) includes:
 - µCT X-ray images of replicate scans of 2 specimens situated at lower and upper end of colony density range (purple points in Fig.2A, also clearly indicated in Fig.6a)
 - Fiji/ImageJ zipped objects containing polygons that delimit selected low- and high-density regions of interest (ROIs), 
from which greyscale values were extracted and converted. (See tab "*5_ROI_DensityEstimates*" on 
[MP_CompleteDataset_SuppMat.xlsx](MP_CompleteDataset_SuppMat.xlsx) )

### [CoralHistograms](CoralHistograms) includes:

Zipped files of all X-ray µCT scans used in this study after being aligned, resampled and shrinkwrapped. 
Each histogram is a *.csv* file, where the first column represents voxel greyscale intensity and the second column  is the voxel count. Please refer to [AvizoTutorials - Step 5](../AvizoTutorials)  to learn more about how histograms were generated.

- [Histograms_REPLICATE_SCANS_RAW.zip](CoralHistograms/Histograms_REPLICATE_SCANS_RAW.zip)
- [Histograms_REPLICATE_SCANS_BH.zip](CoralHistograms/Histograms_REPLICATE_SCANS_BH.zip)
- [Histograms_SINGLE_SCANS.zip](CoralHistograms/Histograms_SINGLE_SCANS.zip)

Data is given in absolute and log scale. First 2<sup>16</sup> rows show absolute count data.

### µCT datasets
- Low-resolution µCT scans (i.e. down-sampled datasets) are deposited on [MorphoSource](https://www.morphosource.org/) for easy visualisation.
- High-resolution µCT scans are deposited on the [Bristol Research Data Repository](https://data.bris.ac.uk/data/). Each coral scan takes ~50Gb of disk space.