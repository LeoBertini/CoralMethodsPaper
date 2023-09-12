# CoralMethodsPaper

This directory contains auxiliary code as well as tutorials released as Supporting Material as part of the following publication:

"XXXXXX" (link to paper and DOI once published).

The code is distributed under the MIT license https://en.wikipedia.org/wiki/MIT_License

Corresponding author: Leonardo Bertini 
e-mail :  l.bertini@nhm.ac.uk  | l.bertini@bristol.ac.uk

Below, you'll find a brief description of all subdirectories, which might have their own 'README' files with further info.


## [AvizoTutorials](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials)

This directory contains instructions for X-ray volume operations using Avizo® on :

1 - How to align replicate X-ray µCT scans

2 - How to segment X-ray volumes and shrinkwrap them quickly

3 - How to export 16-bit single-binned histogram datasets for large X-ray volumes

4 - How to extract volume metrics (e.g., Volume and SurfaceArea for example)

5 - How to create a '.VolMetrics' file containing information from a respective scan

## [PhantomExtraction](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction)
This directory contains code for extracting (or 'probing') greyscale values across an X-ray stack containing a phantom disc with embedded density standard materials :

1 - Semi-automated extraction across the stack by prompting user interaction to mark where extended phantom inserts are located at top and bottom slices of the stack [SemiAutomated_Extraction_Phantom.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/SemiAutomated_Extraction_Phantom.py). 

2 - Automated extraction of phantom density inserts using computer vision to detect regular circular features across the phantom stack [Standard_Extract.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/ExtractStandard.py)

## [CoralWeightTests](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests)
This directory contains code for running weight tests on X-ray µCT volumes that have been previously shrinkwraped (i.e., masked. Refer to [AvizoTutorials](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/AvizoTutorials)) :

1 - Fitting different calibration curves to PhantomExtract results and performing weight tests [Phantom_Fittings.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/Phantom_Fittings.py)

2 - Producing diagnostic figures to visualize different calibration fits and how µCT histogram and phantom density standards overlap [WeightTest_DiagnosticFigures.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/WeightTest_DiagnosticFigures.py)

3 - A wrapper to aggregate weight test results from both an extended and an emulated normal phantom condition [ResultsAggregator.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/ResultsAggregator.py)

## [HistogramsReplicateScans](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/HistogramsReplicateScans)
This directory contains code for generating figures of X-ray histograms of replicate scans done under varying settings:

1 - Plotting histogram overlays with curtosis and skewness measurements [Histogram_overlays.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/HistogramsReplicateScans/Histogram_overlays.py)

## [RScriptsMainFiguresAndStats](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/RScriptsMainFiguresAndStats)
This directory contains code to produce all base figures used in the publication statistical analyses therein. Code was written in R version 4.2.2.
Scripts are named based on the figure they generate and are self-explanatory. 


