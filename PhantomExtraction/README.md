# Density calibration curves via semi-automated extraction of phantom inserts

Below is a guide on how to perform the semi-automated extraction of density standards within and also attached to the phantom disc.

## Step 1 - Select phantom range from X-ray stack 

### 1.1 Export X-ray stack
Generate a .tif stack containing slices of the entire scan. You can use Avizo® to export a image stack of the entire volume or 
[Fiji/ImageJ](https://imagej.net/software/fiji/) using the utility plugin provided [Vol2Any.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/Vol_2Any_LEO.py)
This utility plugin creates a TIFF folder containing the XY stack within each scan directory saved under a root directory. 

See example below:

![alt text](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/GIFs/PhantomExtract1.gif)

### 1.2 Select phantom range
Select only part of the stack containing the phantom and where all inserts are visible (including attached materials).
Make sure both the top and bottom slices have all the materials as you'll be prompted to mark them. 

![alt text](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/GIFs/PhantomExtract2.gif)


### 1.3 Copy phantom slice range to the right directory 
Copy the slice range to ProjecRoot/ScanXX/STANDARD_EXTRACT/PhantomStack. 

**A general representation of the directory tree showing the folder structure is as follows:**

![alt text](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/GIFs/DirectoryTreeExample.jpg)


## Step 2 - Run Phantom Extraction code 
 
Run [SemiAutomated_Extraction_Phantom.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/SemiAutomated_Extraction_Phantom.py) by
specifying a phyton install from an environment in which all [requirements.txt](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/requirements.txt) have been installed. 

You will be prompted to specify the ProjectRoot, then you will be asked to mark phantom inserts on all scans inside ProjectRoot.

Next, you will be asked to enter which type of phantom design you are adopting (Extended or Normal).
After this, you'll click on the centre of each insert and type their names in the screen (as shown below)

![alt text](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/GIFs/PhantomExtract3.gif)

