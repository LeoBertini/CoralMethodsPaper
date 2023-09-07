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
from sys import platform


def get_scan_name(folder_name, dir_standard_names):
    # dir_standard_names = ['CWI_Cores', 'CWI_Coral_Cores', 'NHM_fossils', 'NHM_scans']
    for dir_tag in dir_standard_names:
        if dir_tag in folder_name:
            # print(dir_tag)
            scan_name = str(PureWindowsPath(folder_name)).split(str(PureWindowsPath(dir_tag)))[-1].split('\\')[
                1]  # works on both Windows and Unix
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
                if str.lower(file) in str.lower(
                        target_file_type):  # pass everything to lower case in case dirnames are either upper or lower case
                    # print(os.path.join(dirpath, file))
                    target_dir = os.path.join(dirpath, directory, file)
                    folder_list.append(target_dir)
                    print(f"Found Scan folder {target_dir}")

    folder_list = np.unique(folder_list).tolist()
    print(f"Found Phantom Extracted results in:")
    for item in folder_list:
        print(os.path.abspath(item))

    folder_list_paths_corrected = [os.path.abspath(item) for item in folder_list]

    # find STANDARD_EXTRACTED_VALUES files inside each folder and append to main list
    updated_folder_list = []
    for folder in folder_list:
        files = os.listdir(folder)
        for file in files:
            if file.startswith('STANDARD_EXTRACTED_VALUES'):
                updated_folder_list.append(os.path.abspath(os.path.join(folder, file)))

    return updated_folder_list, os.path.abspath(main_dir)


def get_vsize_from_CT_filetypes(folder):
    file_extensions = [".xtekct", ".xtekVolume"]
    TargetStrings = ['VoxelSizeX=', 'Voxel size = ']
    # parent_folder = os.path.dirname(folder)

    # MAIN_PATH=os.path.join(Drive_Letter, main_dir)

    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            if any([name.endswith(extension) for extension in file_extensions]):
                print(f"Found config file for scan in {os.path.abspath(os.path.join(root, name))}")
                target_file_path = os.path.abspath(os.path.join(root, name))
                ##TODO get voxelsize from xtect or CWI files or xteck volume files

    dummy_size = []
    with open(target_file_path, 'rt') as myfile:  # Open lorem.txt for reading text
        contents = myfile.read()  # Read the entire file to a string
        for each_line in contents.split("\n"):
            if any([item in each_line for item in TargetStrings]):
                # print(each_line)
                dummy_size = each_line
                break

    if TargetStrings[0] in dummy_size:
        voxelsize = float(dummy_size.split(TargetStrings[0])[-1])
    if TargetStrings[1] in dummy_size:
        voxelsize = float(dummy_size.split(TargetStrings[1])[-1])
    print(f"Voxel size is {voxelsize}")

    return voxelsize


####Fit functions
def func_exponential(x, a, b, c):
    return a * np.exp(b * x) + c


def func_poly3(x, a, b, c, d):
    return a * (x ** 3) + b * (x ** 2) + c * x + d


def func_linear(x, a, b, c, d):
    return a * x + b


def func_gaussian(x, a, b, c):
    return a * np.exp(-((x - b) ** 2 / (2 * c ** 2)))


def calibration_points_filter(DATAFRAME, points_used, GreyCI_mode, AirMod):
    x = []
    y = []

    if not GreyCI_mode and not AirMod:
        for item in points_used:
            x.append(DATAFRAME[DATAFRAME['InsertType'] == item]['Measured_Density'].item())
            y.append(DATAFRAME[DATAFRAME['InsertType'] == item]['Median_Gray_for_Calib'].item())

    if AirMod:
        for item in points_used:
            x.append(DATAFRAME[DATAFRAME['InsertType'] == item]['Measured_Density'].item())
            y.append(DATAFRAME[DATAFRAME['InsertType'] == item]['Median_Gray_for_Calib'].item())

        if AirMod=='Pos500':
            y.remove(DATAFRAME[DATAFRAME['InsertType'] == 'air']['Median_Gray_for_Calib'].item())
            y.insert(0, (DATAFRAME[DATAFRAME['InsertType'] == 'air']['Median_Gray_for_Calib'].item())+500)

        if AirMod == 'Neg500':
            y.remove(DATAFRAME[DATAFRAME['InsertType'] == 'air']['Median_Gray_for_Calib'].item())
            y.insert(0, (DATAFRAME[DATAFRAME['InsertType'] == 'air']['Median_Gray_for_Calib'].item())-500)

    if GreyCI_mode:
        for item in points_used:
            x.append(DATAFRAME[DATAFRAME['InsertType'] == item]['Measured_Density'].item())

        if GreyCI_mode == 'UpperCI':
            for item in points_used:
                y.append(DATAFRAME[DATAFRAME['InsertType'] == item]['UpperCI'].item())
        if GreyCI_mode == 'LowerCI':
            for item in points_used:
                y.append(DATAFRAME[DATAFRAME['InsertType'] == item]['LowerCI'].item())

    return x, y


def exponential_fit(DATAFRAME, points_used, FitType, GreyCI_mode, AirMod):
    Density = DATAFRAME['Measured_Density']
    Greys = DATAFRAME['Median_Gray_for_Calib']

    Density_f, Greys_f = calibration_points_filter(DATAFRAME, points_used, GreyCI_mode, AirMod)

    # find Insert_type and Insert_color
    ins_grey, ins_name, ins_color = find_insertnamecolor(DATAFRAME, Density_f)

    a, b, c, d = "", "", "", ""

    try:
        popt, pcov = curve_fit(func_exponential, Density_f, Greys_f, p0=[70539035, 0.000225, -70530211], maxfev=5000)
        # p0 based on cases where gausian worked to give simpy.curve_fit some hope in finding coefficients quicker
        a, b, c = popt[0], popt[1], popt[2] # coefficients
        coefficients = [a, b, c, d]
    except RuntimeError as e:
        print('No polynomial fit found. Assigning dummy coefficients')
        a, b, c = [1e-05, 1e-05, 1e-05]  # coefficients
        coefficients = [a, b, c, d]

    finally:

        func_e = (
            lambda x, a, b, c: a * np.exp(b * x) + c)  # define function to find inverse with the coefficients found
        # find inverse to get density estimate from gray value in domain of curve
        inverse_func = inversefunc(func_e, args=(a, b, c))

        residuals = list(np.array(Greys_f) - func_e(np.array(Density_f), a, b, c))
        LSS_residuals = sum([item ** 2 for item in list(residuals)])
        total_sum_of_squares = sum([item ** 2 for item in list(np.array(Greys_f) - np.mean(np.array(Greys_f)))])

        R2 = 1 - (LSS_residuals / total_sum_of_squares)  # finding R2

        FitTypeMod = 'Exponential_' + FitType + '_n' + str(len(points_used))


    return func_e, coefficients, inverse_func, residuals, LSS_residuals, R2, Density_f, Greys_f, ins_name, ins_color, FitTypeMod


def gaussian_fit(DATAFRAME, points_used, FitType, GreyCI_mode, AirMod):

    Density = DATAFRAME['Measured_Density']
    Greys = DATAFRAME['Median_Gray_for_Calib']

    Density_f, Greys_f = calibration_points_filter(DATAFRAME, points_used, GreyCI_mode, AirMod)

    # find Insert_type and Insert_color
    ins_grey, ins_name, ins_color = find_insertnamecolor(DATAFRAME, Density_f)

    a, b, c, d = "", "", "", ""

    try:
        popt, pcov = curve_fit(func_gaussian, Density_f, Greys_f, p0=[50000, 2.9, 1.6], maxfev=5000)
        # p0 based on cases where gausian worked to give simpy.curve_fit some hope in finding coefficients quicker
        a, b, c = popt[0], popt[1], popt[2]  # coefficients
        coefficients = [a, b, c, d]
    except RuntimeError as e:
        print('No gaussian fit found. Assigning dummy coefficients')
        a, b, c = [1e-05, 1e-05, 1e-05]  # coefficients
        coefficients = [a, b, c, d]
    finally:

        func_g = (lambda x, a, b, c: a * np.exp(
            -((x - b) ** 2 / (2 * c ** 2))))  # define function to find inverse with the coefficients found
        # find inverse to get density estimate from gray value in domain of curve
        inverse_func = inversefunc(func_g, args=(a, b, c))

        residuals = list(np.array(Greys_f) - func_g(np.array(Density_f), a, b, c))
        LSS_residuals = sum([item ** 2 for item in list(residuals)])
        total_sum_of_squares = sum([item ** 2 for item in list(np.array(Greys_f) - np.mean(np.array(Greys_f)))])

        R2 = 1 - (LSS_residuals / total_sum_of_squares)  # finding R2

        FitTypeMod = 'Gaussian_' + FitType + '_n' + str(len(points_used))

    return func_g, coefficients, inverse_func, residuals, LSS_residuals, R2, Density_f, Greys_f, ins_name, ins_color, FitTypeMod


def poly3_fit(DATAFRAME, points_used, FitType, GreyCI_mode, AirMod):
    Density = DATAFRAME['Measured_Density']
    Greys = DATAFRAME['Median_Gray_for_Calib']

    Density_f, Greys_f = calibration_points_filter(DATAFRAME, points_used, GreyCI_mode, AirMod)

    # find Insert_type and Insert_color
    ins_grey, ins_name, ins_color = find_insertnamecolor(DATAFRAME, Density_f)

    a, b, c, d = "", "", "", ""
    popt, pcov = curve_fit(func_poly3, Density_f, Greys_f, maxfev=5000)
    a, b, c, d= popt[0], popt[1], popt[2], popt[3]  # coefficients
    coefficients = [a, b, c, d]

    func_p = (
        lambda x, a, b, c, d: a * (x ** 3) + b * (
                x ** 2) + c * x + d)  # define function to find inverse with the coefficients found
    # find inverse to get density estimate from gray value in domain of curve
    inverse_func = inversefunc(func_p, args=(a, b, c, d))

    residuals = list(np.array(Greys_f) - func_p(np.array(Density_f), a, b, c, d))
    LSS_residuals = sum([item ** 2 for item in list(residuals)])
    total_sum_of_squares = sum([item ** 2 for item in list(np.array(Greys_f) - np.mean(np.array(Greys_f)))])

    R2 = 1 - (LSS_residuals / total_sum_of_squares)  # finding R2

    FitTypeMod = 'Poly3_' + FitType + '_n' + str(len(points_used))

    return func_p, coefficients, inverse_func, residuals, LSS_residuals, R2, Density_f, Greys_f, ins_name, ins_color, FitTypeMod

def linear_fit(DATAFRAME, points_used, FitType, GreyCI_mode, AirMod):
    Density = DATAFRAME['Measured_Density']
    Greys = DATAFRAME['Median_Gray_for_Calib']

    Density_f, Greys_f = calibration_points_filter(DATAFRAME, points_used, GreyCI_mode, AirMod)

    # find Insert_type and Insert_color
    ins_grey, ins_name, ins_color = find_insertnamecolor(DATAFRAME, Density_f)

    a, b, c, d = "", "", "", ""
    popt, pcov = curve_fit(func_linear, Density_f, Greys_f, maxfev=5000)
    a, b = popt[0], popt[1]  # coefficients
    coefficients = [a, b, c, d]

    func_l = (lambda x, a, b: a * x + b)  # define function to find inverse with the coefficients found
    # find inverse to get density estimate from gray value in domain of curve
    inverse_func = inversefunc(func_l, args=(a, b))

    residuals = list(np.array(Greys_f) - func_l(np.array(Density_f), a, b))
    LSS_residuals = sum([item ** 2 for item in list(residuals)])
    total_sum_of_squares = sum([item ** 2 for item in list(np.array(Greys_f) - np.mean(np.array(Greys_f)))])

    R2 = 1 - (LSS_residuals / total_sum_of_squares)  # finding R2

    FitTypeMod = 'Linear_' + FitType + '_n' + str(len(points_used))

    return func_l, coefficients, inverse_func, residuals, LSS_residuals, R2, Density_f, Greys_f, ins_name, ins_color, FitTypeMod


def get_predicted_greys(function_fitted, inserts_density,
                        coefficients):  # todo make coefficient object return list including empty vals

    inserts_density = np.array(inserts_density)
    a, b, c, d = coefficients

    if not c and not d:
        grey_pred = function_fitted(inserts_density, a, b)
    elif not d:
        grey_pred = function_fitted(inserts_density, a, b, c)
    else:
        grey_pred = function_fitted(inserts_density, a, b, c, d)

    return list(grey_pred)

def find_insertnamecolor(DATAFRAME, Density_f):
    grey_used = []
    insert_used_name = []
    insert_used_color = []

    for item in Density_f:
        grey_used.append(DATAFRAME[DATAFRAME['Measured_Density'] == item]['Median_Gray_for_Calib'].item())
        insert_used_name.append(DATAFRAME[DATAFRAME['Measured_Density'] == item]['InsertType'].item())
        insert_used_color.append(DATAFRAME[DATAFRAME['Measured_Density'] == item]['Color_of_insert'].item())

    return grey_used, insert_used_name, insert_used_color


def bundle_results(dictionary, results):
    for key in dictionary:
        # print(key)
        if key == 'Function':
            dictionary[key].append(results[0])
        if key == 'Coefficients':
            dictionary[key].append(results[1])
        if key == 'Inverse_Function':
            dictionary[key].append(results[2])
        if key == 'Residuals':
            dictionary[key].append(results[3])
        if key == 'Least_Square_Sum_Residuals':
            dictionary[key].append(results[4])
        if key == 'R2':
            dictionary[key].append(results[5])
        if key == 'Predicted_Vals':
            dictionary[key].append(get_predicted_greys(function_fitted=results[0],
                                                       inserts_density=results[6],
                                                       coefficients=results[1]))
        if key == 'Density_vals':
            dictionary[key].append(results[6])

        if key == 'Gray_vals':
            dictionary[key].append(results[7])
        if key == 'Insert_type':
            dictionary[key].append(results[8])
        if key == 'Insert_color':
            dictionary[key].append(results[9])
        if key == 'FitType':
            dictionary[key].append(results[10])

    # Function.append(results[0])
    # Coefficients.append(results[1])
    # Inverse_Function.append(results[2])
    # Residuals.append(results[3])
    # Least_Square_Sum_Residuals.append(results[4])
    # R2.append(results[5])
    # Predicted_Vals.append(get_predicted_greys(function_fitted=results[0],
    #                                           inserts_density=results[6],
    #                                           coefficients=results[1]))
    #
    # Density_vals.append(results[6])
    # Gray_vals.append(results[7])
    # Insert_type.append(results[8])
    # Insert_color.append(results[9])

    return dictionary

def narrow_case(DATA, scan_folder, project_dir_list):
    ResultDict = {"Function": [],
                  "Inverse_Function": [],
                  "Coefficients": [],
                  "R2": [],
                  "Predicted_Vals": [],
                  "Residuals": [],
                  "Least_Square_Sum_Residuals": [],
                  "Density_vals": [],
                  "Gray_vals": [],
                  "Insert_type": [],
                  "Insert_color": [],
                  "FitType": []}

    # DOING DIFFERENT FITS AND RESIDUALS AND LEAST SQUARE SUM OF RESIDUALS PER FIT TYPE
    fitnames = ['Narrow_Raw',
                'Narrow_WithAir',
                'Narrow_NoAirNoEpoxy',
                'Narrow_WithAirNoInsert5']

    list_of_points = [
        ['epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5'],
        ['air', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5'],
        ['insert1', 'insert2', 'insert3', 'insert4', 'insert5'],
        ['air', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4']
    ]

    # linear
    for points, fitname in zip(list_of_points, fitnames):
        Results_from_single_fit = linear_fit(DATAFRAME=DATA, points_used=points,
                                             FitType=fitname, GreyCI_mode=False,
                                             AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    # poly3
    for points, fitname in zip(list_of_points, fitnames):
        Results_from_single_fit = poly3_fit(DATAFRAME=DATA, points_used=points,
                                            FitType=fitname, GreyCI_mode=False,
                                            AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    # exponential
    for points, fitname in zip(list_of_points, fitnames):
        Results_from_single_fit = exponential_fit(DATAFRAME=DATA, points_used=points,
                                                  FitType=fitname, GreyCI_mode=False,
                                                  AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    # gaussian
    for points, fitname in zip(list_of_points, fitnames):

        Results_from_single_fit = gaussian_fit(DATAFRAME=DATA, points_used=points,
                                               FitType=fitname, GreyCI_mode=False,
                                               AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        # TODO fit types based on upper and lower CIs of median grey from extracted inserts

        # doing simulations in chunks of neg and postivive transformations of median signal
        # Todo import CI boundaries
        CIs = DATA['Median_CI_95'].astype('O')
        Lower = []
        Upper = []
        for line in CIs:
            Lower.append(pd.eval(line)[0])
            Upper.append(pd.eval(line)[1])

        # Complete TODO fitting Lower Boundary CI
        # Complete TODO fitting Upper Boundary CI

        DATA['UpperCI'] = pd.Series(Upper)
        DATA['LowerCI'] = pd.Series(Lower)

    # LOWER AND UPPER CI bounds for extracted values

    list_of_points = [
        ['epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5'],
        ['air', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5']
    ]

    fittypes = ['Narrow_Raw_LowerBnd', 'Narrow_WithAir_LowerBnd']

    for points, fitname in zip(list_of_points, fittypes):
        Results_from_single_fit = linear_fit(DATAFRAME=DATA, points_used=points,
                                             FitType=fitname, GreyCI_mode='LowerCI',
                                             AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = poly3_fit(DATAFRAME=DATA, points_used=points,
                                            FitType=fitname, GreyCI_mode='LowerCI',
                                            AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = gaussian_fit(DATAFRAME=DATA, points_used=points,
                                               FitType=fitname, GreyCI_mode='LowerCI',
                                               AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = exponential_fit(DATAFRAME=DATA, points_used=points,
                                                  FitType=fitname, GreyCI_mode='LowerCI',
                                                  AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    fittypes = ['Narrow_Raw_UpperBnd', 'Narrow_WithAir_UpperBnd']

    for points, fitname in zip(list_of_points, fittypes):
        Results_from_single_fit = linear_fit(DATAFRAME=DATA, points_used=points,
                                             FitType=fitname, GreyCI_mode='UpperCI',
                                             AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = poly3_fit(DATAFRAME=DATA, points_used=points,
                                            FitType=fitname, GreyCI_mode='UpperCI',
                                            AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = gaussian_fit(DATAFRAME=DATA, points_used=points,
                                               FitType=fitname, GreyCI_mode='UpperCI',
                                               AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = exponential_fit(DATAFRAME=DATA, points_used=points,
                                                  FitType=fitname, GreyCI_mode='UpperCI',
                                                  AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    # Change gray from air +_500 units to check sensitivity (simulating scatter noise from scatter tests)
    Scatter_Noise = [-500, 500]
    Scatter_Noise.sort()  # IMPORTANT TO LIST NEGATIVE FIRST
    Air_Mod_Fit_Names = []

    fittypes = ['Narrow_WithAir_AirMod_Pos500']
    list_of_points = [
        ['air', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5']
    ]

    for points, fitname in zip(list_of_points, fittypes):
        Results_from_single_fit = linear_fit(DATAFRAME=DATA, points_used=points,
                                             FitType=fitname, GreyCI_mode=False,
                                             AirMod='Pos500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = poly3_fit(DATAFRAME=DATA, points_used=points,
                                            FitType=fitname, GreyCI_mode=False,
                                            AirMod='Pos500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = gaussian_fit(DATAFRAME=DATA, points_used=points,
                                               FitType=fitname, GreyCI_mode=False,
                                               AirMod='Pos500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = exponential_fit(DATAFRAME=DATA, points_used=points,
                                                  FitType=fitname, GreyCI_mode=False,
                                                  AirMod='Pos500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    fittypes = ['Narrow_WithAir_AirMod_Neg500']
    list_of_points = [
        ['air', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5']
    ]
    for points, fitname in zip(list_of_points, fittypes):
        Results_from_single_fit = linear_fit(DATAFRAME=DATA, points_used=points,
                                             FitType=fitname, GreyCI_mode=False,
                                             AirMod='Neg500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = poly3_fit(DATAFRAME=DATA, points_used=points,
                                            FitType=fitname, GreyCI_mode=False,
                                            AirMod='Neg500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = gaussian_fit(DATAFRAME=DATA, points_used=points,
                                               FitType=fitname, GreyCI_mode=False,
                                               AirMod='Neg500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = exponential_fit(DATAFRAME=DATA, points_used=points,
                                                  FitType=fitname, GreyCI_mode=False,
                                                  AirMod='Neg500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    # BUILDING DICTIONARY WITH RESULTS TO FACILITATE PLOTTING

    Fit_dic = {'Scan_name': [],
               'Calibration_File_From': [],
               'FitType': [],
               'Density_vals': [],
               'Gray_vals': [],
               'Insert_type': [],
               'Insert_color': [],
               'Coefficients_High_Low_Order': [],
               'R2': [],
               'Predicted_Values': [],
               'Residuals': [],
               'Least_Square_Sum_Residuals': [],
               'RMSE': [],
               'Weight_estimate': [],
               'Volume_estimate': []
               }

    scan_name = get_scan_name(folder_name=scan_folder,
                              dir_standard_names=project_dir_list)

    for idx in range(0, len(ResultDict['FitType'])):
        Fit_dic['Scan_name'].append(scan_name)
        Fit_dic['Calibration_File_From'].append('NaN')
        Fit_dic['FitType'].append(ResultDict['FitType'][idx])
        Fit_dic['Density_vals'].append(ResultDict['Density_vals'][idx])
        Fit_dic['Gray_vals'].append(ResultDict['Gray_vals'][idx])
        Fit_dic['Insert_type'].append(ResultDict['Insert_type'][idx])
        Fit_dic['Insert_color'].append(ResultDict['Insert_color'][idx])
        Fit_dic['Coefficients_High_Low_Order'].append(ResultDict['Coefficients'][idx])
        Fit_dic['R2'].append(ResultDict['R2'][idx])
        Fit_dic['Predicted_Values'].append(ResultDict['Predicted_Vals'][idx])
        Fit_dic['Residuals'].append(ResultDict['Residuals'][idx])
        Fit_dic['Least_Square_Sum_Residuals'].append(ResultDict['Least_Square_Sum_Residuals'][idx])
        Fit_dic['RMSE'].append(np.sqrt(ResultDict['Least_Square_Sum_Residuals'][idx]))
        Fit_dic['Weight_estimate'].append(0)
        Fit_dic['Volume_estimate'].append(0)

    Dataframe = pd.DataFrame(Fit_dic)

    # CALCULATE VIRTUAL WEIGHT FROM Histogram applying different functions
    # for each histogram in scanfolder

    # Find and read each histogram csv data for selected scan, then calculate virtual weight
    csv_files = []

    path_for_csvs = os.path.abspath(os.path.join(scan_folder.split(scan_name)[0], scan_name))
    for file in os.listdir(path_for_csvs):
        if 'Histogram' in file:
            # print(file)
            csv_files.append(os.path.join(path_for_csvs, file))  # list of csv histogram datasets

    if csv_files:  # not if empty list

        for csv_file in csv_files:  # each csv inside scanfolder
            scan_name_patched = csv_file.split('Histogram-')[-1].split('.csv')[0]

            phantom_calib_being_used = scan_folder.split('STANDARD_EXTRACTED_VALUES_')[-1].split('.xlsx')[0]
            print('Histograms found... importing data from csv files...')
            print(csv_file)
            print(f"Calculating coral weight based on {phantom_calib_being_used}")
            Histogram_key_scan = 'Y'

            # slice histogram dataframe to get the linear count and not log scale data (export from avizo gives both)
            hist_scan = pd.read_csv(csv_file, header=None)
            for index in range(len(hist_scan[0])):
                if hist_scan[0][index] == 65535:
                    # print(index)
                    hist_scan_filtered = hist_scan[:index + 1]
                    break

            ##Getting the weight per bin
            # reference scan
            col_names = hist_scan_filtered.columns

            voxel_size = get_vsize_from_CT_filetypes(path_for_csvs)
            voxel_volume = (voxel_size ** 3) / 1000  # in cm3

            for item in range(0, len(ResultDict['FitType'])):  # for each fit type in the Dataframe
                print('\nCalculating virtual weight for the following fit type:')
                print(Dataframe['FitType'][item])
                weight = []
                vol = []
                for line in range(1, len(hist_scan_filtered[col_names[0]])):
                    grey = int(np.floor(hist_scan_filtered[col_names[0]][line]))
                    count = hist_scan_filtered[col_names[1]][line]

                    # find density prediction from grey (essentially the inverted fit)
                    density_estimate = ResultDict['Inverse_Function'][item](
                        grey)  # Inverse_Function contains a list of inverted functions in memory
                    # They are arranged in same order as the ones in the dictionary
                    # no need to feed coefficients

                    weight_bin = density_estimate * abs(count) * voxel_volume
                    weight.append(weight_bin)

                    vol_bin = abs(count) * voxel_volume
                    vol.append(vol_bin)

                print('Total estimated weight')
                print(sum(weight))
                print('Total estimated volume')
                print(sum(vol))
                Dataframe.at[item, 'Scan_name'] = scan_name_patched
                Dataframe.at[item, 'Weight_estimate'] = sum(weight)
                Dataframe.at[item, 'Volume_estimate'] = (sum(vol))
                Dataframe.at[item, 'Calibration_File_From'] = phantom_calib_being_used

            # TODOD remove NoAlu_n6 for normal phantom - this is removing densest insert of phantom and not the Alu attachment.
            Dataframe.to_excel(
                os.path.join(path_for_csvs,
                             'Phantom_Fittings_and_Weights_' + scan_name_patched + '_BasedOn_' + phantom_calib_being_used + '.xlsx'),
                index=False)

def extended_case(DATA, scan_folder, project_dir_list):
    ResultDict = {"Function": [],
                  "Inverse_Function": [],
                  "Coefficients": [],
                  "R2": [],
                  "Predicted_Vals": [],
                  "Residuals": [],
                  "Least_Square_Sum_Residuals": [],
                  "Density_vals": [],
                  "Gray_vals": [],
                  "Insert_type": [],
                  "Insert_color": [],
                  "FitType": []}

    # DOING DIFFERENT FITS AND RESIDUALS AND LEAST SQUARE SUM OF RESIDUALS PER FIT TYPE
    fitnames = ['Ext_Complete',
                'Narrow_Raw',
                'Ext_NoAlu',
                'Ext_NoAir',
                'Ext_NoAluNoAir',
                'Narrow_NoAirWithAlu',
                'Narrow_NoAluWithAir',
                'Narrow_WithAirWithAlu']

    list_of_points_ext = [
        ['air', 'sugar', 'coffee', 'oil', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5', 'aluminum'],
        ['epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5'],

        ['air', 'sugar', 'coffee', 'oil', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5'],
        ['sugar', 'coffee', 'oil', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5', 'aluminum'],

        ['sugar', 'coffee', 'oil', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5'],

        ['epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5', 'aluminum'],
        ['air', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5'],
        ['air', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5', 'aluminum'],
    ]

    # linear
    for points, fitname in zip(list_of_points_ext, fitnames):
        Results_from_single_fit = linear_fit(DATAFRAME=DATA, points_used=points,
                                             FitType=fitname, GreyCI_mode=False,
                                             AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    # poly3
    for points, fitname in zip(list_of_points_ext, fitnames):
        Results_from_single_fit = poly3_fit(DATAFRAME=DATA, points_used=points,
                                            FitType=fitname, GreyCI_mode=False,
                                            AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    # exponential
    for points, fitname in zip(list_of_points_ext, fitnames):
        Results_from_single_fit = exponential_fit(DATAFRAME=DATA, points_used=points,
                                                  FitType=fitname, GreyCI_mode=False,
                                                  AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    # gaussian
    for points, fitname in zip(list_of_points_ext, fitnames):

        Results_from_single_fit = gaussian_fit(DATAFRAME=DATA, points_used=points,
                                               FitType=fitname, GreyCI_mode=False,
                                               AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        # TODO fit types based on upper and lower CIs of median grey from extracted inserts

        # doing simulations in chunks of neg and postivive transformations of median signal
        # Todo import CI boundaries
        CIs = DATA['Median_CI_95'].astype('O')
        Lower = []
        Upper = []
        for line in CIs:
            Lower.append(pd.eval(line)[0])
            Upper.append(pd.eval(line)[1])

        # Complete TODO fitting Lower Boundary CI
        # Complete TODO fitting Upper Boundary CI

        DATA['UpperCI'] = pd.Series(Upper)
        DATA['LowerCI'] = pd.Series(Lower)

    # LOWER AND UPPER CI bounds for extracted values

    list_of_points_ext = [
        ['air', 'sugar', 'coffee', 'oil', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5', 'aluminum'],
        ['epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5']]

    fittypes = ['Ext_AllPoints_LowerBnd', 'Narrow_AllPoints_LowerBnd']

    for points, fitname in zip(list_of_points_ext, fittypes):
        Results_from_single_fit = linear_fit(DATAFRAME=DATA, points_used=points,
                                             FitType=fitname, GreyCI_mode='LowerCI',
                                             AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = poly3_fit(DATAFRAME=DATA, points_used=points,
                                            FitType=fitname, GreyCI_mode='LowerCI',
                                            AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = gaussian_fit(DATAFRAME=DATA, points_used=points,
                                               FitType=fitname, GreyCI_mode='LowerCI',
                                               AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = exponential_fit(DATAFRAME=DATA, points_used=points,
                                                  FitType=fitname, GreyCI_mode='LowerCI',
                                                  AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    fittypes = ['Ext_AllPoints_UpperBnd', 'Narrow_AllPoints_UpperBnd']

    for points, fitname in zip(list_of_points_ext, fittypes):
        Results_from_single_fit = linear_fit(DATAFRAME=DATA, points_used=points,
                                             FitType=fitname, GreyCI_mode='UpperCI',
                                             AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = poly3_fit(DATAFRAME=DATA, points_used=points,
                                            FitType=fitname, GreyCI_mode='UpperCI',
                                            AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = gaussian_fit(DATAFRAME=DATA, points_used=points,
                                               FitType=fitname, GreyCI_mode='UpperCI',
                                               AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = exponential_fit(DATAFRAME=DATA, points_used=points,
                                                  FitType=fitname, GreyCI_mode='UpperCI',
                                                  AirMod=False)  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    # Change gray from air +_500 units to check sensitivity (simulating scatter noise from scatter tests)
    Scatter_Noise = [-500, 500]
    Scatter_Noise.sort()  # IMPORTANT TO LIST NEGATIVE FIRST
    Air_Mod_Fit_Names = []

    fittypes = ['Ext_AllPoints_AirMod_Pos500', 'Narrow_AllPoints_AirMod_Pos500']
    list_of_points_ext = [
        ['air', 'sugar', 'coffee', 'oil', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5', 'aluminum'],
        ['air', 'epoxy', 'insert1', 'insert2', 'insert3', 'insert4', 'insert5']]

    for points, fitname in zip(list_of_points_ext, fittypes):
        Results_from_single_fit = linear_fit(DATAFRAME=DATA, points_used=points,
                                             FitType=fitname, GreyCI_mode=False,
                                             AirMod='Pos500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = poly3_fit(DATAFRAME=DATA, points_used=points,
                                            FitType=fitname, GreyCI_mode=False,
                                            AirMod='Pos500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = gaussian_fit(DATAFRAME=DATA, points_used=points,
                                               FitType=fitname, GreyCI_mode=False,
                                               AirMod='Pos500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = exponential_fit(DATAFRAME=DATA, points_used=points,
                                                  FitType=fitname, GreyCI_mode=False,
                                                  AirMod='Pos500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    fittypes = ['Ext_AllPoints_AirMod_Neg500', 'Narrow_AllPoints_AirMod_Neg500']

    for points, fitname in zip(list_of_points_ext, fittypes):
        Results_from_single_fit = linear_fit(DATAFRAME=DATA, points_used=points,
                                             FitType=fitname, GreyCI_mode=False,
                                             AirMod='Neg500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = poly3_fit(DATAFRAME=DATA, points_used=points,
                                            FitType=fitname, GreyCI_mode=False,
                                            AirMod='Neg500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = gaussian_fit(DATAFRAME=DATA, points_used=points,
                                               FitType=fitname, GreyCI_mode=False,
                                               AirMod='Neg500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

        Results_from_single_fit = exponential_fit(DATAFRAME=DATA, points_used=points,
                                                  FitType=fitname, GreyCI_mode=False,
                                                  AirMod='Neg500')  # RETURNS func, coefficients, inverse_func, residuals, LSS_residuals, R2
        ResultDict = bundle_results(dictionary=ResultDict, results=Results_from_single_fit)

    # BUILDING DICTIONARY WITH RESULTS TO FACILITATE PLOTTING

    Fit_dic = {'Scan_name': [],
               'Calibration_File_From': [],
               'FitType': [],
               'Density_vals': [],
               'Gray_vals': [],
               'Insert_type': [],
               'Insert_color': [],
               'Coefficients_High_Low_Order': [],
               'R2': [],
               'Predicted_Values': [],
               'Residuals': [],
               'Least_Square_Sum_Residuals': [],
               'RMSE': [],
               'Weight_estimate': [],
               'Volume_estimate': []
               }

    scan_name = get_scan_name(folder_name=scan_folder,
                              dir_standard_names=project_dir_list)

    for idx in range(0, len(ResultDict['FitType'])):
        Fit_dic['Scan_name'].append(scan_name)
        Fit_dic['Calibration_File_From'].append('NaN')
        Fit_dic['FitType'].append(ResultDict['FitType'][idx])
        Fit_dic['Density_vals'].append(ResultDict['Density_vals'][idx])
        Fit_dic['Gray_vals'].append(ResultDict['Gray_vals'][idx])
        Fit_dic['Insert_type'].append(ResultDict['Insert_type'][idx])
        Fit_dic['Insert_color'].append(ResultDict['Insert_color'][idx])
        Fit_dic['Coefficients_High_Low_Order'].append(ResultDict['Coefficients'][idx])
        Fit_dic['R2'].append(ResultDict['R2'][idx])
        Fit_dic['Predicted_Values'].append(ResultDict['Predicted_Vals'][idx])
        Fit_dic['Residuals'].append(ResultDict['Residuals'][idx])
        Fit_dic['Least_Square_Sum_Residuals'].append(ResultDict['Least_Square_Sum_Residuals'][idx])
        Fit_dic['RMSE'].append(np.sqrt(ResultDict['Least_Square_Sum_Residuals'][idx]))
        Fit_dic['Weight_estimate'].append(0)
        Fit_dic['Volume_estimate'].append(0)

    Dataframe = pd.DataFrame(Fit_dic)

    # CALCULATE VIRTUAL WEIGHT FROM Histogram applying different functions
    # for each histogram in scanfolder

    # Find and read each histogram csv data for selected scan, then calculate virtual weight
    csv_files = []

    path_for_csvs = os.path.abspath(os.path.join(scan_folder.split(scan_name)[0], scan_name))
    for file in os.listdir(path_for_csvs):
        if 'Histogram' in file:
            # print(file)
            csv_files.append(os.path.join(path_for_csvs, file))  # list of csv histogram datasets

    if csv_files:  # not if empty list

        for csv_file in csv_files:  # each csv inside scanfolder
            scan_name_patched = csv_file.split('Histogram-')[-1].split('.csv')[0]

            phantom_calib_being_used = scan_folder.split('STANDARD_EXTRACTED_VALUES_')[-1].split('.xlsx')[0]
            print('Histograms found... importing data from csv files...')
            print(csv_file)
            print(f"Calculating coral weight based on {phantom_calib_being_used}")
            Histogram_key_scan = 'Y'

            # slice histogram dataframe to get the linear count and not log scale data (export from avizo gives both)
            hist_scan = pd.read_csv(csv_file, header=None)
            for index in range(len(hist_scan[0])):
                if hist_scan[0][index] == 65535:
                    # print(index)
                    hist_scan_filtered = hist_scan[:index + 1]
                    break

            ##Getting the weight per bin
            # reference scan
            col_names = hist_scan_filtered.columns

            voxel_size = get_vsize_from_CT_filetypes(path_for_csvs)
            voxel_volume = (voxel_size ** 3) / 1000  # in cm3

            for item in range(0, len(ResultDict['FitType'])):  # for each fit type in the Dataframe
                print('\nCalculating virtual weight for the following fit type:')
                print(Dataframe['FitType'][item])
                weight = []
                vol = []
                for line in range(1, len(hist_scan_filtered[col_names[0]])):
                    grey = int(np.floor(hist_scan_filtered[col_names[0]][line]))
                    count = hist_scan_filtered[col_names[1]][line]

                    # find density prediction from grey (essentially the inverted fit)
                    density_estimate = ResultDict['Inverse_Function'][item](
                        grey)  # Inverse_Function contains a list of inverted functions in memory
                    # They are arranged in same order as the ones in the dictionary
                    # no need to feed coefficients

                    weight_bin = density_estimate * abs(count) * voxel_volume
                    weight.append(weight_bin)

                    vol_bin = abs(count) * voxel_volume
                    vol.append(vol_bin)

                print('Total estimated weight')
                print(sum(weight))
                print('Total estimated volume')
                print(sum(vol))
                Dataframe.at[item, 'Scan_name'] = scan_name_patched
                Dataframe.at[item, 'Weight_estimate'] = sum(weight)
                Dataframe.at[item, 'Volume_estimate'] = (sum(vol))
                Dataframe.at[item, 'Calibration_File_From'] = phantom_calib_being_used

            # TODOD remove NoAlu_n6 for normal phantom - this is removing densest insert of phantom and not the Alu attachment.
            Dataframe.to_excel(
                os.path.join(path_for_csvs,
                             'Phantom_Fittings_and_Weights_' + scan_name_patched + '_BasedOn_' + phantom_calib_being_used + '.xlsx'),
                index=False)


def save_weigths(scan_folder, project_dir_list):
    warnings.filterwarnings("ignore")

    DATA = pd.read_excel(scan_folder)
    DATA = DATA.sort_values(by='Measured_Density')  # sorting so that values are in ascending order (easy to exclude air)

    # find Normal phantom pairing and skip
    if 'PNormal' in scan_folder or len(DATA) <=7:
        print('Assuming a narrow phantom for file')
        print(scan_folder)
        print('Make sure you have used the "narrow_case" function to calculate weights')
        narrow_case(DATA, scan_folder, project_dir_list)

    if 'PNormal' not in scan_folder or len(DATA) > 7:
        print('Assuming an extended phantom for file')
        print(scan_folder)
        print('Make sure you have used the "extended_case" function to calculate weights')
        extended_case(DATA, scan_folder, project_dir_list)



if __name__ == '__main__':

    if platform == "darwin":
        print('This is a Mac')
        multiprocessing.set_start_method(
            'fork')  # Changing this to "fork" (on MAc platforms) otherwise miltiprocessing won't run

    startTime = time.time()

    folder_list, project_folder = find_folders_by_filetype(target_file_type='STANDARD_EXTRACTED_VALUES',
                                                           target_skipper_file="Phantom_Fittings_and_Weights")

    project_dir_list = ['CWI_Cores', 'CWI_Coral_Cores', 'NHM_fossils', 'NHM_scans', 'Experiment_NHM_phase', 'Testing',
                        'Test']
    project_dir_list.append(project_folder)

    iterable = []
    for each in folder_list:
        iterable.append([each, project_dir_list])

    if len(folder_list) != 0:
        with multiprocessing.Pool(processes=40) as p:
            p.starmap(save_weigths, iterable)
    else:
        ('All Scans have had their weight estimates extracted')

    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))
