# Introduction 

This directory contains auxiliary code as well as tutorials released as Supporting Material, which accompany the following publication:

**"How to quantify and minimise error in coral skeletal density estimates using X-ray µCT"**

(link to paper and DOI once published).

The code is distributed under the MIT license https://en.wikipedia.org/wiki/MIT_License

This project was supported by:
- [4D-Reef](https://www.4d-reef.eu/), a Marie Skłodowska-Curie Innovative Training Network funded by European Union Horizon 2020 research and innovation programme
- The [Natural History Museum](https://www.nhm.ac.uk/) Science Investment Fund. 
- [SYNTHESIS+](https://www.synthesys.info/) museum initiative transnational access.

This work was a joint effort across people from the following institutions:
<p align="center">
  <img src="https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/GIFs/LogoInstitutions.png" height="300" width="600" >
</p>


Corresponding author: Leonardo Bertini 
e-mail :  l.bertini@nhm.ac.uk  | l.bertini@bristol.ac.uk

Below, you'll find a brief description of all the directories in this repository, which might have their own 'README' files with further info.

## [AvizoTutorials](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials)

Instructions for X-ray volume operations using Avizo® on :

- How to align replicate X-ray µCT scans

- How to segment X-ray volumes and shrinkwrap them quickly

- How to export 16-bit single-binned histogram datasets for large X-ray volumes

- How to extract volume metrics (e.g., Volume and SurfaceArea for example)

- How to create a '.VolMetrics' file containing information from a respective scan

## [PhantomExtraction](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction)

Python code for extracting (or 'probing') greyscale values across an X-ray stack containing a phantom disc with embedded density standard materials :

- Semi-automated extraction across the stack by prompting user interaction to mark where extended phantom inserts are located at top and bottom slices of the stack [SemiAutomated_Extraction_Phantom.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/SemiAutomated_Extraction_Phantom.py). 

- Automated extraction of phantom density inserts using computer vision to detect regular circular features across the phantom stack [Standard_Extract.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/ExtractStandard.py)

## [CoralWeightTests](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests)
Python code for running weight tests on X-ray µCT volumes that have been previously shrinkwraped (i.e., masked. Refer to [AvizoTutorials](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials)) :

- Fitting different calibration curves to PhantomExtract results and performing weight tests [Phantom_Fittings.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/Phantom_Fittings.py)

- Producing diagnostic figures to visualize different calibration fits and how µCT histogram and phantom density standards overlap [WeightTest_DiagnosticFigures.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/WeightTest_DiagnosticFigures.py)

- A wrapper to aggregate weight test results from both an extended and an emulated normal phantom condition [ResultsAggregator.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/ResultsAggregator.py)

## [HistogramsReplicateScans](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/HistogramsReplicateScans)
Python code for generating figures of X-ray histograms of replicate scans done under varying settings:

- Plotting histogram overlays with kurtosis and skewness measurements [Histogram_overlays.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/HistogramsReplicateScans/Histogram_overlays.py)

## [RScriptsMainFiguresAndStats](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/RScriptsMainFiguresAndStats)

R code to produce all base figures used in the publication. Statistical analyses therein. 
Code written in R version 4.2.2.
Scripts are named based on the figure they generate and are self-explanatory. 


