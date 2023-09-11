# CoralMethodsPaper

This directory contains auxiliary code as well as tutorials released as Supporting Material as part of the following publication:
"XXXXXX" (link to paper and DOI once published).
Copyright (c) 2023.

The code is distributed under the MIT license https://en.wikipedia.org/wiki/MIT_License

Corresponding author: Leonardo Bertini 
e-mail :  l.bertini@nhm.ac.uk  | l.bertini@bristol.ac.uk

Below, you'll find a brief description of all subdirectories, which might have their on 'README.md' files with further info.


## AvizoTutorials

This directory contains guided instructions using Avizo® for:

1 - How to align replicate X-ray µCT scans

2 - How to segment X-ray volumes and shrinkwrap them quickly

3 - How to export 16-bit single-binned histogram datasets for large X-ray volumes

4 - How to extract volume metrics (e.g., Volume and SurfaceArea for example)

5 - How to create a '.VolMetrics' file containing information from a respective scan


## CoralWeightTests
This directory contains code for:

1 - Fitting different calibration curves to PhantomExtract results and performing weight tests [Phantom_Fittings.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/Phantom_Fittings.py)

2 - Producing diagnostic figures to visualize different calibration fits and how µCT histogram and phantom density standards overlap [WeightTest_DiagnosticFigures.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/WeightTest_DiagnosticFigures.py)

3 - Aggregate weight test results from both an extended and an emulated normal phantom condition [ResultsAggregator.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/ResultsAggregator.py)

## PhantomExtraction
This directory contains code for:

1 - Semi-automated extraction of phantom density inserts across the stack by prompting user interaction to mark where extended phantom inserts are located at the top and bottom of the stack [SemiAutomated_Extraction_Phantom.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/SemiAutomated_Extraction_Phantom.py). 

2 - Automated extraction of phantom density inserts using computer vision to detect regular circular features across the phantom stack [Standard_Extract.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/PhantomExtraction/ExtractStandard.py)


## HistogramsReplicateScans
This directory contains code for:

1 - Plotting histogram overlays of replicate scans under different optimal settings, with curtosis and skewness measurements [Histogram_overlays.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/HistogramsReplicateScans/Histogram_overlays.py)

## RScriptsMainFiguresAndStats
This directory contains code for:

1 - R code to produce all base figures used in the publication.

