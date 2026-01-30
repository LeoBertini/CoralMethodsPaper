## Introduction

This repository contains Supporting Material with code, data processing tutorials and links to datasets that accompany the following publication:

    **"How to quantify and minimise error in coral skeletal density estimates using X-ray µCT"**

                        (link to paper and DOI once published).
                        
                        Corresponding author: Leonardo Bertini
                        
                        e-mail : l.bertini@nhm.ac.uk | l.bertini@bristol.ac.uk 

      The code is distributed under the MIT license https://en.wikipedia.org/wiki/MIT_License


This project was supported by:
- [4D-Reef](https://www.4d-reef.eu/), a Marie Skłodowska-Curie Innovative Training Network funded by European Union Horizon 2020 research and innovation programme
- The [Natural History Museum](https://www.nhm.ac.uk/) Science Investment Fund. 
- [SYNTHESIS+](https://www.synthesys.info/) museum initiative transnational access.
- The [University of Bristol](https://www.bristol.ac.uk/earthsciences/) Covid Recovery Fund. 


This work was a joint effort across people from the following institutions:
<p align="center">
<img src="./PhantomExtraction/GIFs/LogoInstitutions.png" alt="drawing" height="300" width="600"/>
</p>

Below, you'll find a brief description of all the directories in this repository, which might have their own 'README' files with further info.

## [AvizoTutorials](AvizoTutorials)

Instructions for X-ray volume operations using Avizo® covering :

- How to align replicate X-ray µCT scans

- How to segment X-ray volumes and shrinkwrap them quickly

- How to export 16-bit single-binned histogram datasets for large X-ray volumes

- How to extract volume metrics (e.g., Volume and SurfaceArea for example)

- How to create a '.VolMetrics' file containing information from a respective scan

## [PhantomExtraction](PhantomExtraction)

Python code for extracting greyscale values from an X-ray stack containing a phantom disc with embedded density standard materials (i.e., 'greyscale probing'):

-[SemiAutomated_Extraction_Phantom.py](PhantomExtraction/SemiAutomated_Extraction_Phantom.py): Extraction across the stack by prompting user interaction to mark density standard materials embedded in or attached around a radiology phantom.  

- [ExtractStandard.py](PhantomExtraction/ExtractStandard.py): Automated extraction of phantom density inserts using computer vision to detect regular circular features across the phantom stack. 

## [CoralMassTests](CoralMassTests)
Python code for density calibration and mass tests on X-ray µCT volumes that have been previously shrinkwraped (Refer to [AvizoTutorials](AvizoTutorials)) :

- [Phantom_Fittings.py](CoralMassTests/Phantom_Fittings.py): Fitting different calibration curves to PhantomExtract results and performing mass tests.

-  [MassTest_DiagnosticFigures.py](CoralMassTests/MassTest_DiagnosticFigures.py): Producing diagnostic figures to visualize different calibration fits and how µCT histogram and phantom density standards overlap.

-  [ResultsAggregator.py](CoralMassTests/ResultsAggregator.py): A wrapper to aggregate and bind mass test results across the ProjectRoot. This also appends volume and area measurements to resulting dataframes. 

## [HistogramsReplicateScans](HistogramsReplicateScans)
Python code for generating figures of X-ray histograms of replicate scans done under varying settings

- [Histogram_overlays.py](HistogramsReplicateScans/Histogram_overlays.py)
- 
## [R_ScriptsMainFiguresAndStats](R_ScriptsMainFiguresAndStats)

R code to produce all base figures used in the publication. Statistical analyses therein. 
Code written in R version 4.2.2.
Scripts are named based on the figure they generate and are self-explanatory. 

## [Data](Data)
Data used in the paper and figures.
