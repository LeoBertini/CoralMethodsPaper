# 1. Aligning replicate µCT scans:


See below a step-by-step guide using Avizo® 2022.2

We adopt a high-contrast scan as the 'reference volume'. 
In the animation below, the reference volume is shown with 'grey' colormapping. 

The target volume (shown with 'orange' colormapping) is a scan of the same specimen, but still not segmented and containing the phantom disc. 

You'll want to give a computer a headstart first, by manually manipulating the orange volume, so that it is closely matching with the grey volume. Otherwise, this process can take a couple of hours. 

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/Step1.gif  "Logo Title Text 1")

# 2. Repeat

Apply the image registration step from again to ensure a perfect match. 

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/Step2.gif  "Logo Title Text 1")

# 3. Voxel resampling and fixing coordinate system

This step ensures that the both the coordinate system and the voxelized structure of the orange volume are the same as those of the reference volume 

![alt text]( https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials/GIF_images/Step3.gif  "Logo Title Text 1")

#4. Volume Segmentation

