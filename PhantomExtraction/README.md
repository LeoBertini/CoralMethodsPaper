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

![alt text](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/GIFs/DirectoryTreeExample.jpg)



 