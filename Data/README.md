Below is a brief description of files and subfolders in this directory.

### [MP_CompleteDataset_SuppMat.xlsx](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/Data/MP_CompleteDataset_SuppMat.xlsx) is a spreadsheet with :
 - X-ray µCT scans metadata for single and replicate scans
 - Calibration and weight test results for single and replicate scans
 - Calibration and weight test results for the crossover experiment (internal vs. external calibration)
 - Bulk correction results for replicate scans

**Units**:
- Weight Offsets : [\%]
- Weights : [g]
- Voxel size: [mm]
- Specimen volume : [cm<sup>3</sup>]
- SurfaceArea : [mm<sup>2</sup>]
- AreaOverVol: [cm<sup>-1</sup>]
- Density: [g cm<sup>-3</sup>]


### [ROI_AnalysesBulkCorrection](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/Data/ROI_AnalysesBulkCorrection) includes:
 - µCT X-ray images of replicate scans of 2 specimens situated at lower and upper end of colony density range (purple points in Fig.1A)
 - Fiji/ImageJ zipped objects containing polygons that delimit selected low- and high-density regions of interest (ROIs), 
from which greyscale values were extracted and converted. (See tab "*5_ROI_DensityEstimates*" on 
[MP_CompleteDataset_SuppMat.xlsx](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/Data/MP_CompleteDataset_SuppMat.xlsx) )

### [CoralHistograms](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/Data/CoralHistograms) includes:

Zipped files of all X-ray µCT scans used in this study after being aligned, resampled and shrinkwrapped. 
Each histogram is a *.csv* file, where the first column represents voxel greyscale instensity and the second column  is the voxel count. Please refer to [AvizoTutorials- Step 5](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/509f82eb5d21461247551fc28c7af863f605924e/AvizoTutorials/README.md) to learn more about how histograms were generated.

- [Histograms_REPLICATE_SCANS_RAW.zip](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/Data/CoralHistograms/Histograms_REPLICATE_SCANS_RAW.zip) 
- [Histograms_REPLICATE_SCANS_BH.zip](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/Data/CoralHistograms/Histograms_REPLICATE_SCANS_BH.zip)
- [Histograms_SINGLE_SCANS.zip](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/Data/CoralHistograms/Histograms_SINGLE_SCANS.zip) 

Data is given in absolute and log scale. First 2<sup>16</sup> rows show raw data.
