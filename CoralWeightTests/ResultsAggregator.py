
#  This software was developed by Leonardo Bertini (l.bertini@nhm.ac.uk) at the Natural History Museum (London,UK).
#
#  This is released as Supporting Material as part of the following publication:
#  "XXXXXX" (link to paper and DOI once published).
#  #
#
#  Copyright (c) 2023.
#
#  The code is distributed under the MIT license https://en.wikipedia.org/wiki/MIT_License

import numpy as np
import os
import pandas as pd
from tkinter import filedialog
from tkinter import *
from pathlib import Path, PureWindowsPath
import matplotlib.pyplot as plt


def get_scan_name(folder_name, dir_standard_names):
    # dir_standard_names = ['CWI_Cores', 'CWI_Coral_Cores', 'NHM_fossils', 'NHM_scans']
    for dir_tag in dir_standard_names:
        if dir_tag in folder_name:
            print(dir_tag)
            scan_name = str(PureWindowsPath(folder_name)).split(dir_tag)[-1].split('\\')[
                -2]  # works on both Windows and Unix
            # scan_name = folder_name.split(dir_tag)[-1].split('\\')[1]
    return scan_name


def find_folders_by_filetype(target_file_type, target_skipper_file):
    # Selecting parent folder where scan folders are
    root = Tk()
    root.withdraw()
    main_dir = filedialog.askdirectory(title='Select the Parent folder where Scans are saved')
    root.update()

    folder_list = []
    for (dirpath, dirnames, filenames) in os.walk(os.path.abspath(main_dir)):
        for directory in dirnames:
            for file in os.listdir(os.path.join(dirpath, directory)):
                if str.lower(target_file_type) in str.lower(file):  # pass everything to lower case in case dirnames are either upper or lower case
                    print(os.path.join(dirpath, file))
                    target_dir = os.path.join(dirpath, directory, file)
                    folder_list.append(target_dir)
                    # print(f"Found Scan folder {target_dir}")

    folder_list = np.unique(folder_list).tolist()
    print(f"Found Weight files in:")
    for item in folder_list:
        print(os.path.abspath(item))

    folder_list_paths_corrected = [os.path.abspath(item) for item in folder_list]

    return folder_list_paths_corrected, os.path.abspath(main_dir)


def get_volmetrics_from_CT_filetypes(selected_project_dir, scan_folder_name, scan_name_patched):
    file_extension = '.VolMetrics'
    TargetStrings = ["RealWeight=", "SurfaceArea=", "ShapeVA3d=", "Breadth3d=", "MeanRugosity=",
                     "MeanShapeAP=", "MeanSymmetry="]
    parent_folder = os.path.join(selected_project_dir, scan_folder_name)

    # MAIN_PATH=os.path.join(Drive_Letter, main_dir)

    for root, dirs, files in os.walk(parent_folder, topdown=False):
        for name in files:
            if name.endswith(file_extension) and scan_name_patched in name:
                target_file_path = os.path.abspath(os.path.join(root, name))
        # print(f"Found config file for scan in {os.path.abspath(os.path.join(root, name))}")

    dummy_size = []
    with open(target_file_path, 'rt') as myfile:  # Open lorem.txt for reading text
        contents = myfile.read()  # Read the entire file to a string
        for each_line in contents.split("\n"):
            for metric in TargetStrings:
                if metric in each_line and 'Weight' in metric:
                    Realweight = float(each_line.split(metric)[-1])

                if metric in each_line and 'SurfaceArea' in metric:
                    SurfaceArea = float(each_line.split(metric)[-1])

                if metric in each_line and 'ShapeVA3d' in metric:
                    ShapeVA3d = float(each_line.split(metric)[-1])

                if metric in each_line and 'Breadth3d' in metric:
                    Breadth3d = float(each_line.split(metric)[-1])

                if metric in each_line and 'MeanRugosity' in metric:
                    MeanRugosity = float(each_line.split(metric)[-1])

                if metric in each_line and 'MeanShapeAP' in metric:
                    MeanShapeAP = float(each_line.split(metric)[-1])

                if metric in each_line and 'MeanSymmetry' in metric:
                    MeanSymmetry = float(each_line.split(metric)[-1])

    return Realweight, SurfaceArea, ShapeVA3d, Breadth3d, MeanRugosity, MeanShapeAP, MeanSymmetry


folder_list, project_folder = find_folders_by_filetype(target_file_type='Phantom_Fittings_and_Weights',
                                                       target_skipper_file="")

project_dir_list = ['CWI_Cores', 'CWI_Coral_Cores', 'NHM_fossils', 'NHM_scans', 'Experiment_NHM_phase', 'Testing',
                    'Test']
project_dir_list.append(project_folder)

# for each scan folder
for scan_folder in folder_list:

    scan_name = get_scan_name(folder_name=scan_folder,
                              dir_standard_names=project_dir_list)

    # Find and read each histogram csv data for selected scan, then calculate virtual weight

    path_for_csvs = os.path.abspath(os.path.join(scan_folder.split(scan_name)[0], scan_name))
    Weight_Fittings = []
    csv_files = []

    # get histogram for that scan and also weight file
    for file in os.listdir(path_for_csvs):
        if 'Histogram' in file:
            # print(file)
            csv_files.append(os.path.join(path_for_csvs, file))  # list of csv histogram datasets

        if 'Phantom_Fittings_and_Weights' in file:
            Weight_Fittings.append(os.path.join(path_for_csvs, file))  # list of xlsx dataframe

    Weight_Fittings = list(set(Weight_Fittings))  # removes duplicate values grabed by loop

    # initialise empty dataframe to collect all the best fits inside each of the Phantom_Fittings files
    df_all = pd.DataFrame(columns=['Scan_name',
                                   'Calibration_File_From',
                                   'FitType',
                                   'Density_vals',
                                   'Gray_vals',
                                   'Insert_type',
                                   'Insert_color',
                                   'Coefficients_High_Low_Order',
                                   'R2',
                                   'Predicted_Values',
                                   'Residuals',
                                   'Least_Square_Sum_Residuals',
                                   'RMSE',
                                   'Weight_estimate',
                                   'Volume_estimate'])

    if Weight_Fittings:  # not if empty list

        for csv_file in csv_files:  # each csv inside scanfolder

            # patch scan_name to assume name given on Histogram File to account for multiple different corals inside same scan folder
            scan_name_patched = csv_file.split('Histogram-')[-1].split('.csv')[0]

            for weight_file in Weight_Fittings:
                if scan_name_patched in weight_file:  # this is added so that matching Histo and Phantom Phintings are grabbed and others are skipped

                    print(weight_file)
                    rawdata = pd.read_excel(weight_file)

                    # Sort multiple columns by lowest RMSE without any type of air mod
                    # sorted = rawdata.sort_values(['RMSE'], ascending=[True])
                    # # get unique Fits without 'AirMod' label and then 'NoAir' label
                    # sorted2 = sorted[sorted["FitType"].str.contains("AirMod") == False]
                    # sorted3 = sorted2[sorted2["FitType"].str.contains("NoAir") == False]
                    # sorted3 = sorted3.reset_index(drop=True)
                    MainFits = rawdata.sort_values(["FitType"])

                    MainFits.reset_index(inplace=True)

                    df_all = df_all.append(MainFits)

    df_all = df_all.drop(columns=['index'], axis=1)

    # TODO append a coral's volume metrics metadata from Volmetrics text file:
    # Volume metrics
    # RealWeight =
    # SurfaceArea =
    # ShapeVA3d =
    # Breadth3d =
    # MeanRugosity =
    # MeanShapeAP =
    # MeanSymmetry =

    # dummy lists  to append to aggregated dataframe
    RealWeight_dummy = []
    SurfaceArea_dummy = []
    ShapeVA3d_dummy = []
    Breadth3d_dummy = []
    MeanRugosity_dummy = []
    MeanShapeAP_dummy = []
    MeanSymmetry_dummy = []
    RealColonyDensity_dummy = []

    # calculating additional metrics
    Offset = []
    AreaOverVol = []
    VirtualDensity = []
    RealColonyDensity = []

    for row_number in range(0,len(df_all)):

        coralVol = df_all['Volume_estimate'].iloc[row_number]

        Realweight, SurfaceArea, ShapeVA3d, Breadth3d, MeanRugosity, MeanShapeAP, MeanSymmetry = get_volmetrics_from_CT_filetypes(
        selected_project_dir=project_folder, scan_folder_name=scan_name, scan_name_patched=df_all['Scan_name'].iloc[row_number])
        Offset.append((df_all['Weight_estimate'].iloc[row_number] - Realweight) / Realweight)
        VirtualDensity.append(df_all['Weight_estimate'].iloc[row_number] / df_all['Volume_estimate'].iloc[row_number])

        AreaOverVol.append((SurfaceArea/100) / coralVol)

        RealColonyDensity.append(Realweight / df_all['Volume_estimate'].iloc[row_number])

        # dummy lists of repeats
        RealWeight_dummy.append(Realweight)
        SurfaceArea_dummy.append(SurfaceArea)
        ShapeVA3d_dummy.append(ShapeVA3d)
        Breadth3d_dummy.append(Breadth3d)
        MeanRugosity_dummy.append(MeanRugosity)
        MeanShapeAP_dummy.append(MeanShapeAP)
        MeanSymmetry_dummy.append(MeanSymmetry)

        # TODO apppend new columns to dataset

    df_all['WeightOffset'] = Offset
    df_all['VirtualDensity'] = VirtualDensity
    df_all['AreaOverVol'] = AreaOverVol

    df_all['RealWeight'] = RealWeight_dummy
    df_all['SurfaceArea'] = SurfaceArea_dummy
    df_all['ShapeVA3d'] = ShapeVA3d_dummy
    df_all['Breadth3d'] = Breadth3d_dummy
    df_all['MeanRugosity'] = MeanRugosity_dummy
    df_all['MeanShapeAP'] = MeanShapeAP_dummy
    df_all['MeanSymmetry'] = MeanSymmetry_dummy
    df_all['RealColonyDensity'] = RealColonyDensity

    # TODO Save as XSLX
    df_all.to_excel(os.path.join(project_folder, scan_name, f"AggregatedResults_{scan_name}.xlsx"))
# #
# # # TODO combine all aggregated files into one single big file
# input_file_path='D:\\PhD\\CORAL_RECONS_RAW\\ToBind\\'
#
# # create a new, blank dataframe, to handle the excel file imports
# df = pd.DataFrame()
# # Run a for loop to loop through each file in the list
# files= os.listdir(input_file_path)
# for excel_file in files:
#     # check for .xlsx suffix files only
#     if excel_file.endswith(".xlsx") and not excel_file.startswith("._"):
#         if excel_file.startswith('Aggregated'):
#             print(excel_file)
#             # create a new dataframe to read/open each Excel file from the list of files created above
#             df1 = pd.read_excel(input_file_path + excel_file, engine='openpyxl')
#         # append each file into the original empty dataframe
#         df = df.append(df1)
# # transfer final output to an Excel (xlsx) file on the output path
# df.to_excel(input_file_path + "\\Consolidated_file.xlsx")
# #

