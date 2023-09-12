# 1. Aligning replicate µCT scans


See below a step-by-step guide using Avizo® 2022.2

We adopt a high-contrast scan as the 'reference volume'. 
In the animation below, the reference volume is shown with 'grey' colormapping. 

The target volume (shown with 'orange' colormapping) is a scan of the same specimen, but still not segmented and containing the phantom disc. 

You'll want to give a computer a headstart first, by manually manipulating the orange volume, so that it is closely matching with the grey volume. Otherwise, this process can take a couple of hours. 

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/Step1.gif )

# 2. Repeat

Apply the image registration step from (1) again to ensure a perfect match. 

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/Step2.gif )

# 3. Voxel resampling and fixing coordinate system

This step ensures that the both the coordinate system and the voxelized structure of the orange volume are the same as those of the reference volume.

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/Step3.gif )

# 4. Volume Segmentation

The segmentation editor is powerful and a binarized mask of the coral volume can be generated quickly if you use the 'magic wand' tool. 

Make sure you have 'all slices' toggled off whilst testing things out and deciding on the greyscale range, otherwise it will try
to expand the selection across the entire slice stack every single time you adjust the range. 

Once you are happy with the selected portions of the volume, this can be added to a material.
In this case the material is called 'Inside'. 

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/Step4.gif )

This creates a binary mask that is linked to the coral volume on the Project View panel. 

# 5. Volume masking and histogram export

This step 'masks' the volume based on the binary mask created before, so we can generate a histogram of the
16-bit µCT dataset containing only voxel intensities and counts from the shrinkwrapped volume. 

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/Step5.gif )

# 6. Extracting surface area and other volume metrics 

Using the masked shrinkwrapped volume, we now can extract a range of metrics.

## Step 1: Generate volume surface from binary mask object

Attach a 'Generate Surface module' to the label field.

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/ImagesVolmetrics/Picture1.png )

## Step 2: Simplify surface 

Reduce the number of faces of the rendered surface by a factor of 100, to smooth it out and 
make calculations run a lot faster. 

This overwrites the surface object, so if you want to see a Before/After then duplicate and simplify on the copied surface object instead. 
- Preserve slice structure and you can also hit fast

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/ImagesVolmetrics/Picture2.png )

## Step 3: Smooth surface 

Attach a Smooth Surface module to the simplified surface object (set iterations to 3)

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/ImagesVolmetrics/Picture3.png )


## Step 4: Get general volume statistics

Attach a Surface Area Vol object and see statistics table for surface area

### Optional: Get different measures in 2D 

Attach a Global Analysis module to the binary label field and load the masked greyscale volume
Set interpretation to **XY planes**
Measure Group should be a default or a saved group that includes for example the following 2-dimensional measures: Rugosity, Shape_AP and Symmetry

Look at the ‘.analysis’ object for results table

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/ImagesVolmetrics/Picture4.png )

### Optional: Get different measures in 3D 

Attach a Global Analysis module to the binary label field and also load the masked greyscale volume
Set interpretation to **3D**
Measure Group should be a default or a saved group that includes for example the following 3-dimensional measures: Breadth3D, Shape_VA3D

Look at the ‘.analysis’ object for results table.

## Step 5 - Save information in a '.VolMetrics' file

Open any text editor (e.g., Notepad or TextEdit) and insert volume information alogside the specimen's RealWeight as displayed below:

<img src="https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/ImagesVolmetrics/Picture5.png" height="400" width="600" >

Then save with extension '.VolMetrics' into the respective scan folder.

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/ImagesVolmetrics/Picture6.png )


## Project Directory structure

The following folder structure is advised as this ensures code runs smoothly and subsequent files are saved in the right places .
The ProjectRoot can be any folder under which single-scan folders are saved. See example below:

![alt text](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/GIFs/DirectoryTreeExample.jpg)

**Inside the scan folder, the following files can be found:**

- X-ray volume and reconstruction configuration files (respectively ***.raw***, ***.vgi*** and ***.xtekVolume*** extensions)
- a text file containing information about the specimen and additional volumetric measurements (***.VolMetrics*** extension)
- the histogram of the shrinkwraped masked volume (***.csv*** extension)
- the results from weight tests (***.xlsx*** extension) - created after running [Phantom_Fittings.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests)
- diagnostic plots from calibration curves and respective weight tests (***.png*** extension) - created after running [WeightTest_DiagnosticFigures.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests)

Additionally, scan folders should have secondary directories containing:

- a .tif image stack of the X-ray scan  (***'TIFF'***), which can be exported through Avizo® or using Fiji/ImageJ.
- density standard extraction (***'STANDARD_EXTRACT'*** ). Refer to [PhantomExtraction](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction) for more info




