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

This step ensures that the both the coordinate system and the voxelized structure of the orange volume are the same as those of the reference volume 

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

Attach a 'Generate Surface module'

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/ImagesVolmetrics/Picture1.png )

