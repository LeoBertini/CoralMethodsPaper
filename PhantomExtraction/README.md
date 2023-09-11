# Density calibration curve via semi-automated extraction of phantom inserts

Below is a guide on how to perform the semi-automated extraction of density standards within and also attached to the phantom disc.

## Step 1 - Select phantom range from X-ray stack 

**a** Generate a .tif stack containing slices of the entire scan. You can use Avizo® to export a image stack of the entire volume or 
Fiji/ImageJ using the utility plugin provided [Vol2Any.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/Vol_2Any_LEO.py)
This utility plugin creates a TIFF folder containing the XY stack within each scan directory saved under a root directory. 

**b** Select only part of the stack containing the phantom and where all inserts are visible (including attached materials).
Make sure both the top and bottom slices have all the materials as you'll be prompted to mark them. 

**c** Copy the slice range to ProjecRoot/ScanXX/STANDARD_EXTRACT/PhantomStack. 

See example below:

![alt text](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/GIFs/PhantomExtract1.gif)



**A general representation of the directory tree showing the folder structure is as follows:**

ProjectRoot/
├── Scan1
├── Scan2
├── Scan3
├── Scan4/
│   ├── TIFF/
│   │   ├── Scan4_Slice_xy_0001.tif ...
│   │   └── Scan4_Slice_xy_0002.tif ...
│   ├── STANDARD_EXTRACT/
│   │   ├── PhantomStack
│   │   ├── Overlay_Extracted_Vals_Scan4.png
│   │   └── PhantomMasks/
│   │       └── Phantom_mask_slice_0001.png ...
│   ├── Scan4.vgi
│   ├── Scan4.xtekCT
│   ├── Scan4.raw
│   ├── Scan4.VolMetrics
│   ├── Histogram-Scan4.csv
│   └── Phantom_Fittings_and_Weights.xlsx
├── Scan5
└── ...




 