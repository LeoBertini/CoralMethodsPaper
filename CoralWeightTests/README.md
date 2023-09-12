A brief description of each Python script is given below:
- [Phantom_Fittings.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/Phantom_Fittings.py): this is the main script and is used for fitting different calibration curves and calculating virtual weights from X-ray datasets.
- [WeightTest_DiagnosticFigures.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/WeightTest_DiagnosticFigures.py): creates plots for visualizing calibration curves and weight test results.
- [ResultsAggregator.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/ResultsAggregator.py): a utility script that binds results into a single spreadsheet and includes .Volmetrics data to resulting dataframes. 

## Directory structure

Make sure your ProjectRoot contains individualized folders for each scans with specific subdirectories as this ensures code runs smoothly and subsequent files are saved in the right places .
The ProjectRoot can be any folder under which single-scan folders are saved. 
See example below:

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


## Usage

Configure a python environment and install all necessary libraries/packages (see [requirements.txt](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/requirements.txt)).
Make sure to run python code from terminal clients such as ***Windows PowerShell*** (code won't run from a Python Console in some platforms, due to multi-threading optimization). 

Specify your phython.exe from within your environment installation followed by the path to [Phantom_Fittings.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/Phantom_Fittings.py).

           <user> ...PythonEnvironment/path_to/python.exe CoralWeightTests/Phantom_Fittings.py

This involves: 
- fitting different calibration curves using both linear, 3rd-degree polynomial, gaussian and exponential relationships across inserts from adopted phantom (11-point Extended or 6-point narrow) with their subvariations. 
- There's up to 32 calibration adjustments already parametrized in the code and this can be adapted. 
- reverse fitting each calibration curve (finding inverse functions) to obtain density estimates for each greyscale intensity present in a specimen's histogram
- calculate the specimen's total virtual weight per fit adjustment. 

See example below:

<p align="center">
  <img src="https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/IMGs/PowerShellExample.png" >
</p>

You'll be prompted to indicate the ProjectRoot containing all the individual scan folders.
Input files used are: *ScanXX.xtekVolume*, *Histogram-ScanXX.csv* and *STANDARD_EXTRACTED_VALUES.xlsx*. These should be placed in the right sections of the directory tree.
Once the code is running, some results are printed out to the screen


<p align="center">
  <img src="https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/IMGs/PowerShellExample2.png" >
</p>


The code will run in 'parallel' across the entire project tree for all scan folders.
Runtime is ~60 min no matter how many scans are under a ProjectRoot (machine used had Intel Xeon 2.30 GHz 16-core CPU).
When the run is complete, additional files with results and diagnostic figures will have been saved on the scan's directory.
See example below (new files are highlighted)

<p align="center">
  <img src="https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/IMGs/CreatedFilesExample1.png" >
</p>


Next, you can call [WeightTest_DiagnosticFigures.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/WeightTest_DiagnosticFigures.py)
which creates diagnostic plots like the one below:

<p align="center">
  <img src="https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/IMGs/Example_Diagnostic_Plots_Scan_LB_0043.png" >
</p>


You can use [ResultsAggregator.py](https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/ResultsAggregator.py) to merge .VolMetrics data to the resulting dataframe and also go through the ProjectRoot and bind all the results into a single spreadsheet. 

In the end, you should have a scan directory populated with the highlighted files:
<p align="center">
  <img src="https://github.com/LeoBertiniNHM/CoralMethodsPaper/blob/main/CoralWeightTests/IMGs/CreatedFilesExample2.png" >
</p>