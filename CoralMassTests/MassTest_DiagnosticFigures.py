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
import time
import os
import pandas as pd
import warnings
import multiprocessing
from pynverse import inversefunc
from scipy.optimize import curve_fit
from tkinter import filedialog
from tkinter import *
from pathlib import Path, PureWindowsPath
import matplotlib.pyplot as plt


def get_scan_name(folder_name, dir_standard_names):
    # dir_standard_names = ['CWI_Cores', 'CWI_Coral_Cores', 'NHM_fossils', 'NHM_scans']
    for dir_tag in dir_standard_names:
        if dir_tag in folder_name:
            #print(dir_tag)
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
                if str.lower(target_file_type) in str.lower(
                        file):  # pass everything to lower case in case dirnames are either upper or lower case
                    print(os.path.join(dirpath, file))
                    target_dir = os.path.join(dirpath, directory, file)
                    folder_list.append(target_dir)
                    # print(f"Found Scan folder {target_dir}")

    folder_list = np.unique(folder_list).tolist()
    print(f"Found Weight files in:")
    for item in folder_list:
        print(os.path.abspath(item))

    dummy = []
    print('Checking if any of the scans have had figures exported already to then ignore \n')

    for (dirpath, dirnames, filenames) in os.walk(os.path.abspath(main_dir)):
        for directory in dirnames:
            for file in os.listdir(os.path.join(dirpath, directory)):
                if str.lower(target_skipper_file) in str.lower(
                        file):  # pass everything to lower case in case dirnames are either upper or lower case
                    dummy.append(os.path.dirname(os.path.join(dirpath, directory, file)))

    dummy = np.unique(dummy).tolist()
    if len(dummy) != 0:
        print('Diagnostic figures already extracted in:')
        for item in dummy:
            print(os.path.abspath(item))
    else:
        print(f"None of the scans in {main_dir} have had diagnostic figures produced")

    for flagged_dir in dummy:
        for long_path in folder_list:
            if flagged_dir in long_path:
                folder_list.remove(long_path)
            else:
                continue

    folder_list_paths_corrected = [os.path.abspath(item) for item in folder_list]

    return folder_list_paths_corrected, os.path.abspath(main_dir)


def filter_histogram_bell_plot(file_path):
    # Step 1: read histogram csv file from main dir
    hist_scan = pd.read_csv(os.path.join(file_path), header=None)
    # Step 2: slice histogram dataframe to get the linear count and not log scale data (export from avizo gives both)
    for index in range(len(hist_scan[0])):
        if hist_scan[0][index] == 65535:
            # print(index)
            hist_scan_filtered = hist_scan[:index + 1]
            break

    # removing outliers to make plot look nice
    q_low = hist_scan_filtered[1].quantile(0.01)
    q_hi = hist_scan_filtered[1].quantile(0.99)
    df_filtered = hist_scan_filtered[(hist_scan_filtered[1] < q_hi) & (hist_scan_filtered[1] > q_low)]

    return df_filtered


####Fit functions
def func_exponential(x, a, b, c):
    return a * np.exp(b * x) + c


def func_poly3(x, a, b, c, d):
    return a * (x ** 3) + b * (x ** 2) + c * x + d


def func_linear(x, a, b):
    return a * x + b


def func_gaussian(x, a, b, c):
    return a * np.exp(-((x - b) ** 2 / (2 * c ** 2)))


folder_list, project_folder = find_folders_by_filetype(target_file_type='Phantom_Fittings_and_Weights',
                                                       target_skipper_file="DiagnosticPlot")

project_dir_list = ['CWI_Cores', 'CWI_Coral_Cores', 'NHM_fossils', 'NHM_scans', 'Experiment_NHM_phase', 'Testing',
                    'Test']
project_dir_list.append(project_folder)

# for each scan folder
for scan_folder in folder_list:

    scan_name = get_scan_name(folder_name=scan_folder,
                              dir_standard_names=project_dir_list)

    # Find and read each histogram csv data for selected scan, then calculate virtual weight


    path_for_csvs = os.path.abspath(os.path.join(scan_folder.split(scan_name)[0], scan_name))
    csv_files = []
    Weight_Fittings = []
    # get histogram for that scan and also weight file
    for file in os.listdir(path_for_csvs):
        if 'Histogram' in file:
            # print(file)
            csv_files.append(os.path.join(path_for_csvs, file))  # list of csv histogram datasets

        if 'Phantom_Fittings_and_Weights' in file:
            Weight_Fittings.append(os.path.join(path_for_csvs, file))  # list of xlsx dataframe


    #Complete : TODO go through entire three. at the moment only picking up the first directory
    if csv_files and Weight_Fittings:  # not if empty list

        for csv_file in csv_files:  # each csv inside scanfolder

            # patch scan_name to assume name given on Histogram File to account for multiple different corals inside same scan folder
            scan_name_patched = csv_file.split('Histogram-')[-1].split('.csv')[0]

            #phantom_calib_being_used = scan_folder.split('STANDARD_EXTRACTED_VALUES_')[-1].split('.xlsx')[0]
            print('Histograms found... importing data from csv files...')
            print(csv_file)
            Histogram_key_scan = 'Y'
            hist_scan_filtered = filter_histogram_bell_plot(csv_file)  # filtering histogram to remove outliers and get nice plot
            Grays_hist = hist_scan_filtered[0][0:]
            Count_hist = hist_scan_filtered[1][0:]


            for weight_file in Weight_Fittings:

               if scan_name_patched in weight_file: #this is added so that matching Histo and Phantom Phintings are grabbed and others are skipped

                    # run plot function
                    fig = plt.figure(figsize=(11.69, 8.27), constrained_layout=TRUE)
                    grid = plt.GridSpec(8, 4, wspace=0.4, hspace=0.3)

                    rawdata = pd.read_excel(weight_file)

                    # Sort multiple columns by lowest RMSE without any type of air mod
                    sorted = rawdata.sort_values(['RMSE'], ascending=[True])

                    # get unique Fits without 'AirMod' label and then 'NoAir' label
                    sorted2 = sorted[sorted["FitType"].str.contains("AirMod") == False]
                    sorted3 = sorted2[sorted2["FitType"].str.contains("NoAir") == False]
                    sorted3 = sorted3.reset_index(drop=True)
                    MainFits = sorted3[sorted3["FitType"].str.contains("Complete") == True]
                    if len(MainFits) == 0: #this means phantom was normal and not with extra inserts

                        MainFits = sorted3[sorted3["FitType"].str.contains("Raw") == True ]
                        MainFits = MainFits[MainFits["FitType"].str.contains("Upper") == False ]
                        MainFits = MainFits[MainFits["FitType"].str.contains("Lower") == False ]

                    MainFits.reset_index(inplace=True)

                    # for each fit type make a plot, starting from Linear, then Poly, then Guassian then Exponential
                    # first ordering dataframe
                    for i in range(0, len(MainFits)):

                        if 'Linear' in MainFits['FitType'][i]:
                            MainFits['index'][i] = 1
                        if 'Poly' in MainFits['FitType'][i]:
                            MainFits['index'][i] = 2
                        if 'Gaussian' in MainFits['FitType'][i]:
                            MainFits['index'][i] = 3
                        if 'Exp' in MainFits['FitType'][i]:
                            MainFits['index'][i] = 4

                    #now sort dataframe
                    MainFits = MainFits.sort_values(by=['index'], ascending=True)
                    MainFits.reset_index(inplace=True)


                    Boundaries = sorted3[sorted3["FitType"].str.contains("AllPoints_n11") == False]
                    Boundaries.reset_index(inplace=True)
                    # values of x for y's to be evaluated
                    xvalues = np.linspace(0, 4, 20)
                    max_x = 3
                    min_x = -1
                    min_y = 0
                    max_y = 80000
                    best_fit = sorted3['FitType'][0]

                    # figure title
                    Phantom_Used = MainFits['Calibration_File_From'][0]
                    scan_name_mod = scan_name_patched.replace('_', '\_') #this was added so that '_' is not interpreted as 'subscript'
                    Phantom_Used_mod =Phantom_Used.replace('_', '\_') #this was added so that '_' is not interpreted as 'subscript'
                    fig.suptitle("Diagnostic plots for scan " + r"$\bf{" + scan_name_mod + "}$" + "  | Calib. data from " +  r"$\bf{" + Phantom_Used_mod + "}$", fontsize=12)


                    for indx in range(0, len(MainFits)):

                        if 'Poly' in MainFits['FitType'][indx]:
                            a, b, c, d = pd.eval(MainFits['Coefficients_High_Low_Order'][indx])
                            predicted = func_poly3(xvalues, a, b, c, d)
                            FitName = 'Polynomial 3'

                            for indx2 in range(0, len(Boundaries)):
                                if 'Poly' in Boundaries['FitType'][indx2] and 'LowerBnd' in Boundaries['FitType'][indx2]:
                                    a, b, c, d = pd.eval(Boundaries['Coefficients_High_Low_Order'][indx2])
                                    predicted_lower = func_poly3(xvalues, a, b, c, d)

                                if 'Poly' in Boundaries['FitType'][indx2] and 'UpperBnd' in Boundaries['FitType'][indx2]:
                                    a, b, c, d = pd.eval(Boundaries['Coefficients_High_Low_Order'][indx2])
                                    predicted_upper = func_poly3(xvalues, a, b, c, d)

                                else:
                                    continue

                        if 'Linear' in MainFits['FitType'][indx]:
                            a, b, c, d = pd.eval(MainFits['Coefficients_High_Low_Order'][indx])
                            predicted = func_linear(xvalues, a, b)
                            FitName = 'Linear'

                            for indx2 in range(0, len(Boundaries)):
                                if 'Linear' in Boundaries['FitType'][indx2] and 'LowerBnd' in Boundaries['FitType'][indx2]:
                                    a, b, c, d= pd.eval(Boundaries['Coefficients_High_Low_Order'][indx2])
                                    predicted_lower = func_linear(xvalues, a, b)

                                if 'Linear' in Boundaries['FitType'][indx2] and 'UpperBnd' in Boundaries['FitType'][indx2]:
                                    a, b, c, d = pd.eval(Boundaries['Coefficients_High_Low_Order'][indx2])
                                    predicted_upper = func_linear(xvalues, a, b)

                                else:
                                    continue

                        if 'Gaussian' in MainFits['FitType'][indx]:
                            a, b, c, d = pd.eval(MainFits['Coefficients_High_Low_Order'][indx])
                            predicted = func_gaussian(xvalues, a, b, c)
                            FitName = 'Guassian'

                            for indx2 in range(0, len(Boundaries)):
                                if 'Guassian' in Boundaries['FitType'][indx2] and 'LowerBnd' in Boundaries['FitType'][indx2]:
                                    a, b, c, c = pd.eval(Boundaries['Coefficients_High_Low_Order'][indx2])
                                    predicted_lower = func_gaussian(xvalues, a, b, c)

                                if 'Guassian' in Boundaries['FitType'][indx2] and 'UpperBnd' in Boundaries['FitType'][indx2]:
                                    a, b, c, c = pd.eval(Boundaries['Coefficients_High_Low_Order'][indx2])
                                    predicted_upper = func_gaussian(xvalues, a, b, c)

                                else:
                                    continue

                        if 'Exp' in MainFits['FitType'][indx]:
                            a, b, c, d = pd.eval(MainFits['Coefficients_High_Low_Order'][indx])
                            predicted = func_exponential(xvalues, a, b, c)
                            FitName = 'Exponential'

                            for indx2 in range(0, len(Boundaries)):
                                if 'Exp' in Boundaries['FitType'][indx2] and 'LowerBnd' in Boundaries['FitType'][indx2]:
                                    a, b, c, d = pd.eval(Boundaries['Coefficients_High_Low_Order'][indx2])
                                    predicted_lower = func_exponential(xvalues, a, b, c)

                                if 'Exp' in Boundaries['FitType'][indx2] and 'UpperBnd' in Boundaries['FitType'][indx2]:
                                    a, b, c, d = pd.eval(Boundaries['Coefficients_High_Low_Order'][indx2])
                                    predicted_upper = func_exponential(xvalues, a, b, c)

                                else:
                                    continue

                        # residuals and RMSE
                        residuals = pd.eval(MainFits['Residuals'][indx])
                        RMSE = pd.eval(MainFits['RMSE'][indx])
                        phantom_vals_x = pd.eval(MainFits['Density_vals'][indx])
                        phantom_vals_y = pd.eval(MainFits['Gray_vals'][indx])
                        Weight_estimate = pd.eval(MainFits['Weight_estimate'][indx])
                        Colony_volume = pd.eval(MainFits['Volume_estimate'][indx])
                        color = pd.eval(MainFits['Insert_color'][indx])
                        res_min = round(abs(min(min(pd.eval(MainFits['Residuals'])))))
                        res_max = round(abs(max(max(pd.eval(MainFits['Residuals'])))))

                        if res_max >= res_min:
                            res_axlim = [-(round(res_max, -2) + 200), (round(res_max, -2) + 200)]
                        if res_max <= res_min:
                            res_axlim = [-(round(res_min, -2) + 200), (round(res_min, -2) + 200)]

                        ax_residuals = fig.add_subplot(grid[0, indx])
                        ax_residuals.plot(residuals, linestyle=':', color='k')

                        # unpacking color list and making bgr conversion for matplotlib
                        color1 = [list(eval(item)) for item in color] #read text to color
                        color1_new = []
                        for item in color1:
                            red = item[0]
                            green = item[1]
                            blue = item[2]
                            bgr_color = [blue,green,red]
                            color1_new.append(bgr_color)
                        color2 = []
                        for item in color1_new:
                            dummy_color = [RGB / 255 for RGB in item]
                            if dummy_color == [1, 1, 1]:  # fix one of the colours being white so dot on plot does not show on white background. Making it light grey
                                dummy_color = [211 / 255, 211 / 255, 211 / 255]
                            color2.append([dummy_color])

                        ax_residuals.set_title(f"{FitName}\n RMSE = {round(RMSE)}", fontsize=10)
                        ax_residuals.scatter(np.arange(len(residuals)), residuals, linestyle='-', c=color2)
                        ax_residuals.axhline(y=0, color='r', linestyle='-')
                        ax_residuals.set_ylim(res_axlim[0], res_axlim[1])
                        ax_residuals.set_xlabel('Insert #', fontsize=8)
                        if indx == 0:
                            ax_residuals.set_ylabel('Residual', fontsize=8)

                        # predicted fits
                        ax_predicted_fit = fig.add_subplot(grid[2:5, indx])
                        ax_predicted_fit.set_title(f"Virtual weight = {round(Weight_estimate,2)} g \n Virtual density = {round(Weight_estimate/Colony_volume,2)} g/cm3", fontsize=9)
                        ax_predicted_fit.set_xlabel('Density (g/cm3)')
                        if indx == 0:
                            ax_predicted_fit.set_ylabel('Grey value')

                        ax_predicted_fit.plot(xvalues, predicted, 'k', linewidth=0.5)
                        ax_predicted_fit.legend(['Predicted Fit'], loc='upper left', fontsize=8)
                        #ax_predicted_fit.plot(xvalues, predicted_lower, 'r', linewidth=0.25)
                        #ax_predicted_fit.plot(xvalues, predicted_upper, 'b', linewidth=0.25)
                        ax_predicted_fit.fill_between(xvalues, predicted_lower, predicted_upper, alpha=0.8)
                        # TODO add here line plots for the confidence interval fits
                        ax_predicted_fit.set_xlim(-0.1, 3)
                        ax_predicted_fit.set_ylim(0, 70000)
                        ax_predicted_fit.grid(True)

                        for pair in list(zip(phantom_vals_x, phantom_vals_y, color2)):
                            x_dummy = pair[0]
                            y_dummy = pair[1]
                            color_dummy = pair[2]
                            #bgr = (color_dummy[0][-1], color_dummy[0][2], color_dummy[0][0]) #this makes the color BGR so matplotlib displays right color
                            ax_predicted_fit.scatter(x_dummy, y_dummy, marker='o', color = color_dummy)

                        #colony histogram
                        histo_axis = fig.add_subplot(grid[6:, :])
                        histo_axis.plot(Grays_hist, Count_hist, 'k')
                        histo_axis.set_ylim(0, max(Count_hist) + 20000)
                        histo_axis.set_xlabel('Grey Intensity (0-65535)')
                        histo_axis.set_ylabel('Voxel Count')
                        histo_axis.set_title('Coral greyscale histogram and insert values')

                        # overlay of insert values to see if 'under the bell-shaped curve'
                        phantom_greys = pd.eval(MainFits['Gray_vals'][0])
                        for indx3 in range(0, len(phantom_greys)):
                            histo_axis.scatter(phantom_greys[indx3], max(Count_hist) / 2, color=color2[indx3][0])

                        legend_list = pd.eval(MainFits['Insert_type'][0])
                        legend_list.insert(0,'CT Histogram')

                        # Shrink current axis's height by 10% on the bottom
                        box = histo_axis.get_position()
                        histo_axis.set_position([box.x0, box.y0 + box.height * 0.1,
                                         box.width, box.height * 0.9])

                        # Put a legend below current axis
                        histo_axis.legend(legend_list, loc='upper center', bbox_to_anchor=(0.5, -0.4),
                                  fancybox=True, shadow=True, ncol=6, fontsize = 8)
                        histo_axis.grid(True)
                        histo_axis.ticklabel_format(axis='y', style='sci', scilimits=(3, 3))

                    # saving figure
                    outdir=os.path.join(project_folder, scan_name)
                    plt.savefig(os.path.join(outdir, 'Diagnostic_Plots_Scan_' + scan_name_patched + '_based_on_Phantom_' + Phantom_Used + '.png'), dpi=300)


