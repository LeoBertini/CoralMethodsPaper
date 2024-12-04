#  This software was developed by Leonardo Bertini (l.bertini@nhm.ac.uk) at the Natural History Museum (London,UK).
#
#  This is released as Supporting Material as part of the following publication:
#  "XXXXXX" (link to paper and DOI once published).
#
#
#  Copyright (c) 2023.
#
#  The code is distributed under the MIT license https://en.wikipedia.org/wiki/MIT_License

import glob
import multiprocessing
import os
import time
from pathlib import PureWindowsPath
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tqdm
from scipy.ndimage import gaussian_filter1d
from sklearn.linear_model import LinearRegression


# Working functions
def load_images_from_folder(folder, format):
    """
    This function finds files in a specified path containing a target file extension.

    :param folder: Specified path of folder containing stack of X-ray tiff images representing the radiology phantom.
    :param format: Specified format of images to be loaded. (e.g., '.tif'
    :return: a list of filenames for images that satisfy the specified format.
    """
    cv_img = []
    for img in glob.glob(os.path.join(folder, "*" + f"{format}")):
        cv_img.append(img)
    # print(f"Found Phantom tif stack in {folder}")

    return cv_img


def draw_circle(event, x, y, flags, param):
    """
    This function interacts with the user and prompts the annotation of centre regions in X-ray images containing density phantom rods, to extract greyscale values within confined areas
    It runs until the pre-determined number of features to be annotated is reached and exits for image inspection and rescalling mode.

    :param event: mouse instance for tracking clicks from the user using OpenCV
    :param x: mouse click position
    :param y: mouse click position
    :return: updates global variables specified below appending to their specific dictionaries and saves a preview of the annotated image in parent directory
    """

    global mouseX, mouseY, counter, insert_list, txt, dummy_list, Color_list_dic, color_used, target_slices, item, Phantom_folder, initial_slice_tag, new_image, annotation_vals, scale_factor
    entered_list = []

    if event == cv2.EVENT_LBUTTONDOWN:
        if counter < len(insert_list):

            if counter != 0:
                print("Please inform which type of insert you are marking from the list below:")
                [print(str.lower(insert_name)) for insert_name in dummy_list]

            # validating user input
            while True:
                txt = input('Which insert have you clicked?: \n')
                if str.lower(txt) not in dummy_list or str.lower(txt) in entered_list:
                    print("Sorry, Choose from the options above")
                else:
                    #  successfully parsed!
                    # we're ready to exit the loop.
                    entered_list.append(str.lower(txt))
                    break

            # displaying the coordinates
            # on the image window with label
            cv2.circle(new_image, (x, y), int(10 * scale_factor), Color_list_dic[txt], -1)

            annotation_vals.append(txt)
            color_used.append(Color_list_dic[txt])

            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(new_image, str(x) + ',' +
                        str(y), (x, y), font, fontScale=0.2, color=(255, 255, 0), thickness=1)

            cv2.putText(new_image, txt, (x - 10, y + 20), font, fontScale=0.4, color=(255, 255, 255), thickness=1)

            print(f"Point for {txt} marked on image. Coordinates are ({x},{y})")

            # update list
            for entry in dummy_list:
                if entry == txt:
                    dummy_list.remove(entry)

            counter += 1
            mouseX.append(x)
            mouseY.append(y)
            allx.append(x)
            ally.append(y)
            print('Click on the next insert \n')

        if counter == len(insert_list):
            print("All inserts annotated. Press ESC to enter image rescaling mode.")

        cv2.imwrite(os.path.join(Phantom_folder,
                                 f"Slice_{item + initial_slice_tag}_Phantom_Scaled_Annotated_Phantom_slice.png"),
                    new_image)


def draw_circle2(event, x, y, flags, param):
    """
     This function adds a preview overlay of previously annotated density inserts to check for misalignment issues or mislabelling by the user.
     Same behaviour as draw_circle but invoked when bottom X-ray slice is brought to the user.

     Basic functionality:
     This function interacts with the user and prompts the annotation of centre regions in X-ray images containing density phantom rods, to extract greyscale values within confined areas
     It runs until the pre-determined number of features to be annotated is reached and exits for image inspection and rescalling mode.

     :param event: mouse instance for tracking clicks from the user using OpenCV
     :param x: mouse click position
     :param y: mouse click position
     :return: updates global variables specified below appending to their specific dictionaries and saves a preview of the annotated image in parent directory
     """

    global mouseX, mouseY, counter, insert_list, txt, dummy_list, Color_list_dic, color_used, target_slices, item, Phantom_folder, initial_slice_tag, new_image, allx, ally, annotation_vals, scale_factor
    entered_list = []
    # displaying the annotated circles from previous images in red

    for pair in zip(allx, ally):
        cv2.circle(new_image, pair, int(10 * scale_factor / 2), (0, 0, 255), -1)

    if event == cv2.EVENT_LBUTTONDOWN:
        if counter < len(insert_list):

            if counter != 0:
                print("Please inform which type of insert you are marking from the list below:")
                [print(str.lower(insert_name)) for insert_name in dummy_list]

            while True:
                txt = input('Which insert have you clicked?: \n')
                if str.lower(txt) not in dummy_list or str.lower(txt) in entered_list:
                    print("Sorry, Choose from the options above")
                else:
                    #  successfully parsed!
                    # we're ready to exit the loop.
                    entered_list.append(str.lower(txt))
                    break

            # displaying the coordinates
            # on the image window with label
            cv2.circle(new_image, (x, y), int(10 * scale_factor), Color_list_dic[txt], -1)

            annotation_vals.append(txt)
            color_used.append(Color_list_dic[txt])

            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(new_image, str(x) + ',' +
                        str(y), (x, y), font, fontScale=0.2, color=(255, 255, 0), thickness=1)

            cv2.putText(new_image, txt, (x - 10, y + 20), font, fontScale=0.4, color=(255, 255, 255), thickness=1)

            print(f"Point for {txt} marked on image. Coordinates are ({x},{y})")

            # update list
            for entry in dummy_list:
                if entry == txt:
                    dummy_list.remove(entry)

            counter += 1
            mouseX.append(x)
            mouseY.append(y)
            print('Click on the next insert \n')

        if counter == len(insert_list):
            print("All inserts annotated. Press ESC to enter image rescaling mode.")

        cv2.imwrite(os.path.join(Phantom_folder,
                                 f"Slice_{item + initial_slice_tag}_Phantom_Scaled_Annotated_Phantom_slice.png"),
                    new_image)


def polynomial_regression3d(x, y, z, degree):
    """
    This is a polynomial regression wrapper to predict the positions of target areas across the X-ray stack based on markings done by the user on the top and bottom X-ray slices.

    :param x, y : horizontal coordinates in the tiff images.
    :param z: position across the stack
    :param degree: adjusted based on polynomial complexity desired
    :return: a list of predicted density centres across the entire radiology phantom stack

    """
    # sort data to avoid plotting problems
    # x, y, z = zip(*sorted(zip(x, y, z)))
    z_spillover = 0  # number of extra slices where coord are to be predicted in case phantom stack contains more images
    X = np.array([y, z]).reshape(-1, 2)

    y_pred = np.linspace(min(y), max(y), max(z))  # range of y
    z_pred = np.arange(min(z), max(z) + z_spillover)  # range of z

    zz_pred, yy_pred = np.meshgrid(z_pred, y_pred)

    model_viz = np.array([yy_pred.flatten(), zz_pred.flatten()]).T

    model = LinearRegression().fit(X, x)
    predicted_x = model.predict(model_viz)
    predicted_insert_coord_XYZ = list(zip(predicted_x, y_pred, z_pred))

    return predicted_insert_coord_XYZ


def find_overlapping_range(interval_list):
    """
    Functionality to be implemented in future releases.
    Helper function used to detect positions of inflexion points on greyscale series for anomaly detection.
    It traverses through a series of greyscale values testing for inflexion points and updating itself

    :param interval_list:
    :return: start and end positions of possible inflexion points.
    """
    start, end = interval_list.pop()
    while interval_list:
        start_temp, end_temp = interval_list.pop()
        start = max(start, start_temp)
        end = min(end, end_temp)
    return [start, end]


def find_folders_with_image_stacks(target_file_type, dir_standard_types, target_skipper_file):
    """
    Function for user callbacks, defining directory tree to traverse and from which X-ray data will be fetched

    :param target_file_type: file extension of target images (e.g., '.tif')
    :param dir_standard_types: standardised directory name (e.g., Phantom_Stack)
    :param target_skipper_file: placeholder for a path containing a string to indicate data has been extracted previously (part of a filename or dir).
     It leaves the specific parent dir out of the analysis. (e.g.,STANDARD_EXTRACTED_xxx_.csv is a file generated after successfully probing greyscale intensities and used as a tag for skipping)
    :return: returns list of directories from which the extraction of density phantom values is needed.

    """

    root = Tk()
    root.withdraw()
    messagebox.showinfo(title='Select paths', message="Select the drive and parent folder where µCT scans are saved")
    drive_letter = filedialog.askdirectory(title='Select the drive where scans are saved (eg: C: or D:)')
    root.update()

    # Selecting parent folder where scan folders are
    root = Tk()
    root.withdraw()
    main_dir = filedialog.askdirectory(title='Select the Parent folder where Scans are saved')
    root.update()

    print("Traversing directories in the tree...")
    folder_scan_list = []
    for (dirpath, dirnames, filenames) in os.walk(os.path.join(drive_letter, main_dir)):
        for direct in dirnames:
            if str.lower(direct) in [str.lower(element) for element in
                                     dir_standard_types]:  # pass everything to lower case in case dirnames are either upper or lower case
                target_dir = os.path.join(dirpath, direct)
                for file in os.listdir(target_dir):
                    if target_file_type in file:
                        folder_scan_list.append(target_dir)
                # print(f"Found TIF stack with {len(os.listdir(target_dir))} images in {os.path.abspath(target_dir)}")

    folder_scan_list = np.unique(folder_scan_list).tolist()

    dummy = []
    print('Checking if any of the scans have had Phantom values extracted already to then ignore \n')
    # COMPLETE TODO FILTER FOLDERS WHICH ALREADY HAVE A "STANDARD_EXTRACTED_VALUES.xlsx"

    for (dirpath, dirnames, filenames) in os.walk(os.path.join(drive_letter, main_dir)):
        for name in filenames:
            if target_skipper_file in name:
                # print(dirpath)
                dummy.append(os.path.dirname(dirpath))

    dummy = np.unique(dummy).tolist()
    already_extracted = dummy

    for flagged_dir in dummy:
        for long_path in folder_scan_list:
            if flagged_dir in long_path:
                folder_scan_list.remove(long_path)

    # fixing path issues to work across platforms (Unix and Windows)
    folder_list_paths_corrected = [os.path.abspath(item) for item in folder_scan_list]
    already_extracted_paths_corrected = [os.path.abspath(item) for item in already_extracted]
    for dir in already_extracted_paths_corrected:
        print(f"Phantom already extracted in "f"{dir}. Movin to next folder.\n")

    return folder_list_paths_corrected, os.path.abspath(main_dir), already_extracted_paths_corrected


def get_scan_name(folder_name, dir_standard_names):
    """
    This function is used to obtain the X-ray dataset name

    :param folder_name: Directory containing the X-ray data for a single scan
    :param dir_standard_names: optional arg used to bypass user selection  of parent directories when testing
           E.g., dir_standard_names = ['CWI_Cores', 'CWI_Coral_Cores', 'NHM_fossils', 'NHM_scans']
    :return: The X-ray dataset name adopted
    """

    project_folder = dir_standard_names[-1]
    scan_name = str(PureWindowsPath(folder_name.split(project_folder)[-1])).split('STANDARD_EXTRACT')[0].split('\\')[
        1]  # works on both Windows and Unix and uses 'STANDARD_EXTRACT' as splitter
    return scan_name


def get_vsize_from_CT_filetypes(selected_project_dir, scan_name):
    """
    This function reads different types of text files from different micro-CT scanners, containing configuration data.
    It locates fields where the resolution of the scan is mentioned. This is the size in mm of any pixel in 2D, and the thickness of a µCT slice in 3D

    :param selected_project_dir: the X-ray scan directory  indicated by the user on a graphical prompt
    :param scan_name: the X-ray dataset name
    :return: the voxel size of the scan being processed, which is later appended to a dataframe containing the scan metadata and the calibration greyscale probing results
    """

    file_extensions = [".xtekCT", ".xtekVolume", 'xtekct']
    TargetStrings = ['VoxelSizeX=', 'Voxel size = ']
    parent_folder = os.path.join(selected_project_dir, scan_name)

    # MAIN_PATH=os.path.join(Drive_Letter, main_dir)

    for root, dirs, files in os.walk(parent_folder, topdown=False):
        for name in files:
            if any([name.endswith(extension) for extension in file_extensions]):
                print(f"Found config file for scan in {os.path.abspath(os.path.join(root, name))}")
                target_file_path = os.path.abspath(os.path.join(root, name))

    dummy_size = []
    with open(target_file_path, 'rt') as myfile:  # Open for reading text
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


def get_grey_inside_circles(coral_img, img_real_idx, x_centres, y_centres, z_centres, radius, colors, insert_names,
                            out_dir):
    """
    This function extracts the greyscale values within marked areas by the used across the entire image stack

    :param coral_img: X-ray slice
    :param img_real_idx: absolute index of slice on the stack
    :param x_centres: predicted horizontal for a density rod inside the radiology phantom
    :param y_centres: predicted horizontal for a density rod inside the radiology phantom
    :param z_centres: predicted vertical for a density rod inside the radiology phantom
    :param radius: the size of the circular buffer area around centre points from which greyscale probing will be done
    :param colors: dictionary of predetermined values for each density rod inside the radiology phantom (used for plots and creating masked images)
    :param insert_names: list to indicate the number of inserts existing in the radiology phantom
    :param out_dir: path where masked slices are saved
    :return: a nested list containing density insert names, their respective colour, z_centre, and greyscale values extracted
    """

    mean_grey_all_inserts = []
    coral_img = cv2.imread(coral_img, -1)
    mask_img = np.zeros((coral_img.shape[0], coral_img.shape[1], 3), dtype=np.uint8)

    for insert_idx in range(0, len(insert_names)):

        cv2.circle(mask_img,
                   (x_centres[insert_idx], y_centres[insert_idx]),
                   radius,
                   colors[insert_idx],
                   -1)
        out_img_name = os.path.join(out_dir, f"Phantom_mask_slice_{img_real_idx}.png")
        # Get X and Y coordinates of all pixels of certain color
        Y_in_circle, X_in_circle = np.where(np.all(mask_img == colors[insert_idx], axis=2))

        gray_values_for_insert_area = []

        for idx in range(0, len(Y_in_circle)):  # pixels_of_interest:
            grey_dummy = coral_img[Y_in_circle[idx], X_in_circle[idx]]
            gray_values_for_insert_area.append(grey_dummy)

        # mean grey intensity
        mean_grey_inside_circle = round(np.mean(gray_values_for_insert_area), 2)
        mean_grey_all_inserts.append(mean_grey_inside_circle)

    cv2.imwrite(out_img_name, mask_img)  # COMPLETE TODO save image of all inserts at once to speed up the loop

    return [insert_names, colors, z_centres, mean_grey_all_inserts]


def build_iterator_for_parallelism(Dataframe, Phantom_folder):
    """
    This function builds a nested list iterator to be passed to multiprocessing to allow for parallel computing across the stack on a slice-wise fashion
    :param Dataframe: reads a pandas dataframe containing X-ray metadata,  information for each of the slices across the stack, density insert parameters (predicted positions, associated colours for plotting)

    :param Phantom_folder: used to indicate the output dir of masked density phantom images
    :return:
    """
    iterator = []
    # build iterator tuple
    out_dir = os.path.join(Phantom_folder, 'Phantom_Masks')
    img_dir = os.path.dirname(Dataframe['Slice_path'][0][0])

    # first slice tag number
    initial_slice_tag = int(Dataframe['Slice_path'][0][0].split(".tif")[0].split("_")[-1])

    # build iterator for parallel loop

    for i in range(0, len(Dataframe['Predicted_Circle_Centers_XYZ'][0])):  # '-initial_slice_tag+1):  # each slice
        x_centres = []
        y_centres = []
        z_centres = []
        colors = []
        insert_names = []
        for j in range(0, len(Dataframe['InsertType'])):  # each insert type
            color = Dataframe['Color_of_insert'][j]
            insert_name = Dataframe['InsertType'][j]
            radius = Dataframe['Radius'][j]
            x_centre = int(round(Dataframe['Predicted_Circle_Centers_XYZ'][j][i][0]))
            y_centre = int(Dataframe['Predicted_Circle_Centers_XYZ'][j][i][1])
            z_centre = int(Dataframe['Predicted_Circle_Centers_XYZ'][j][i][2])
            image_list = load_images_from_folder(img_dir, format='.tif')

            coral_img = image_list[i]
            img_real_idx = str(initial_slice_tag + i).zfill(6)

            x_centres.append(x_centre)
            y_centres.append(y_centre)
            z_centres.append(z_centre)
            colors.append(color)
            insert_names.append(insert_name)

        iterator.append(
            (coral_img, img_real_idx, x_centres, y_centres, z_centres, radius, colors, insert_names, out_dir))

    return iterator


def DF_update(Dataframe):
    """
    Function to be released as future update
    :param Dataframe:
    :return: greyscale values extracted based on bootstrapping for error analysis.
    """

    print('This functionality needs to be implemented in the future.')

    # # COMPLETE : TODO append to Dataframe start_position and end_position for series extraction based on series inflexions or visual
    # infls_dummy_list = []
    # # find inflexion points
    # for insert in range(0, len(Dataframe['InsertType'])):
    #     infls_tested = []
    #     series = literal_eval(Dataframe['Extracted_Grays'][insert])
    #     # smooth
    #     smooth = gaussian_filter1d(series, len(series) * 0.2)
    #     # compute second derivative
    #     smooth_d2 = np.gradient(np.gradient(smooth))
    #     # find switching points
    #     infls = np.where(np.diff(np.sign(smooth_d2)))[0]
    #
    #     if len(infls) < 2:
    #         infls_tested = [0, len(series)]
    #     if len(infls) >= 2:
    #         infls_tested = [min(infls), max(infls)]
    #
    #     infls_dummy_list.append(infls_tested)
    #
    # Dataframe['Slice_range'] = ''
    # Dataframe['Median_Gray_for_Calib'] = ''
    # Dataframe['Median_CI_95'] = ''
    # Dataframe['Median_StdError'] = ''
    # Dataframe['Scan_name'] = ''
    # Dataframe['Phantom_type'] = ''
    #
    # initial_slice_tag = literal_eval(Dataframe['XYZ'][0])[0][-1]
    # for insert in range(0, len(Dataframe['InsertType'])):
    #     Dataframe['Slice_range'][insert] = [item + initial_slice_tag for item in infls_dummy_list[insert]]
    #
    #     series = literal_eval(Dataframe['Extracted_Grays'][insert])
    #     ranged = series[infls_dummy_list[insert][0]:
    #                     infls_dummy_list[insert][1]]
    #
    #     # COMPLETE TODO append median gray for insert inside selected envelope
    #     Dataframe['Median_Gray_for_Calib'][insert] = round(np.median(ranged), 2)
    #     Dataframe['Scan_name'] = scan_name
    #
    #     # applying bootstrapping of median
    #     # create 95% confidence interval for population median based on bootstrapping
    #     np.random.seed(13)
    #     boot_sample_medians = []
    #     std_error = []
    #     number_iterations = 10000
    #
    #     sample_1 = np.random.choice(series,
    #                                 size=int(
    #                                     len(series)))  # flag numbers in population to randomly change
    #
    #     for i in range(number_iterations):
    #         boot_sample = np.random.choice(sample_1, replace=True, size=int(len(series)))
    #         boot_median = np.median(boot_sample)
    #         boot_sample_medians.append(boot_median)
    #
    #     # stand error and confidence interval of the median
    #     # std
    #     std_error = np.std(boot_sample_medians)
    #     # the average value of repeated samples' median values
    #     # C.I.
    #     boot_median_CI = np.percentile(boot_sample_medians, [2.5, 97.5])
    #     CI = boot_median_CI.tolist()
    #
    #     Dataframe['Median_CI_95'][insert] = CI
    #     Dataframe['Median_StdError'][insert] = std_error
    #     if len(Dataframe['InsertType']) <= 7:
    #         answer = 'narrow'
    #     else:
    #         answer = 'extended'
    #
    #     Dataframe['Phantom_type'][insert] = answer.lower()


if __name__ == "__main__":

    start_time = time.time()
    ############# - #initialize dictionaries - ##################

    # this is a list in RGB (be aware sometimes matplotlib does bgr, so check plots down the line)
    Color_list_dic = {'air': (255, 255, 255),
                      'epoxy': (0, 0, 255),
                      'insert1': (0, 255, 0),
                      'insert2': (255, 0, 0),
                      'insert3': (0, 255, 255),
                      'insert4': (255, 255, 0),
                      'insert5': (255, 0, 255),
                      'sugar': (0, 0, 128),
                      'oil': (0, 128, 128),
                      'coffee': (128, 128, 0),
                      'aluminum': (0, 128, 0)}

    Density_list_dic = {'air': 0.001225,
                        'epoxy': 1.13,
                        'insert1': 1.26,
                        'insert2': 1.44,
                        'insert3': 1.65,
                        'insert4': 1.77,
                        'insert5': 1.92,
                        'sugar': 0.1261,
                        'oil': 0.904,
                        'coffee': 0.26,
                        'aluminum': 2.7
                        }

    ############# - MAIN CODE - ##################

    # find all dirs with phantom stacks
    folder_list, selected_project_dir, already_extracted = find_folders_with_image_stacks(target_file_type='.tif',
                                                                                          dir_standard_types=['Phantom_Stack'],
                                                                                          target_skipper_file="STANDARD_EXTRACTED")

    project_dir_list = [selected_project_dir]
    # project_dir_list = ['CWI_Cores', 'CWI_Coral_Cores', 'NHM_fossils', 'NHM_scans', 'Experiment_NHM_phase', 'Testing', 'Test']  # default project dirnames used before, during testing

    if folder_list:  #
        for folder in folder_list:  # looping over scan folders in main dir

            scan_name = get_scan_name(folder_name=folder,
                                      dir_standard_names=project_dir_list)

            voxel_size = get_vsize_from_CT_filetypes(selected_project_dir, scan_name)

            image_list = load_images_from_folder(folder, format='.tif')
            image_list.sort()  # sorting to make sure

            target_slices = [0, len(image_list) - 1]  # doing 2 images #start, and #end of stack

            Phantom_folder = os.path.join(selected_project_dir, scan_name, 'STANDARD_EXTRACT')

            # showing first image to user to define type of phantom (Extended or Narrow phantom)
            first_image = cv2.imread(image_list[0])
            print("Original shape: ", first_image.shape)

            # We want the new image to be 60% of the original image
            scale_factor = 0.4
            new_height = int(first_image.shape[0] * scale_factor)
            new_width = int(first_image.shape[1] * scale_factor)
            dimensions = (new_width, new_height)
            first_image_rzise = cv2.resize(first_image, dimensions, interpolation=cv2.INTER_LINEAR)

            cv2.imshow("Resized image", first_image_rzise)
            print(f'Displaying top slice of phantom stack...\n {image_list[0]}')
            print("Look at the Phantom Image Displayed, then Press ESC to go back to cmd line")
            cv2.waitKey(0)

            while True:
                try:

                    answer = input("Type in what kind of phantom was used (Extended or Narrow)?: \n")
                    if answer.lower() == 'extended':
                        insert_list = ["Air", "Sugar", "Coffee", "Oil", "Aluminum", "Epoxy",
                                       "Insert1", "Insert2", "Insert3", "Insert4", "Insert5"]
                        print(f"Phantom type is {answer}. Sample image window closed")
                        break
                    if answer.lower() == 'narrow':
                        insert_list = ["Air", "Epoxy", "Insert1", "Insert2", "Insert3", "Insert4", "Insert5"]
                        print(f"Phantom type is {answer}. Sample image window closed")
                        break

                    else:
                        print("Sorry, type in a valid option")
                except ValueError:
                    print("Sorry, type in a valid option")

            cv2.destroyAllWindows()  # when ESC is pressed
            # Phantom type has been defined

            dictionary = {'Slice_path': [],
                          'X': [],
                          'Y': [],
                          'Z': [],
                          'InsertType': [],
                          'Color_of_insert': [],
                          'Radius': [],
                          'VoxelSize': []}

            # annotate manually on images to find displacement of centre of inserts
            allx = []
            ally = []
            loop_no = 0

            # this is the main interactive loop to mark slices
            # getting real slice index to append to mask name and make accurate predictions
            initial_slice_tag = int(image_list[0].split(".tif")[0].split("_")[-1])

            for item in target_slices:  # range(0, #len(target_slices)): #looping over selected slices from stack

                param = insert_list
                annotation_vals = []
                mouseX = []
                mouseY = []
                color_used = []

                image = cv2.imread(image_list[item])
                # print("Original shape: ", image.shape)

                height = image.shape[0]
                width = image.shape[1]

                # We want the new image to be 60% of the original image
                scale_factor = 0.4
                new_height = int(height * scale_factor)
                new_width = int(width * scale_factor)
                dimensions = (new_width, new_height)
                new_image = cv2.resize(image, dimensions, interpolation=cv2.INTER_LINEAR)

                # print("New shape:", new_image.shape)

                # cv2.imshow("Resized image", new_image)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()

                cv2.namedWindow(winname="Resized image")
                counter = 0

                dummy_list = [str.lower(insert_name) for insert_name in insert_list]

                if loop_no != 0:
                    print(
                        "\n ============ \n "
                        "The bottom slice of the phantom stack is displayed next \n"
                        "Positions marked on the top slice will be overlaid as red dots")

                    input("Press Enter to continue marking inserts \n "
                          "============")

                print("You'll be marking inserts from the list below:")
                [print(str.lower(insert_name)) for insert_name in insert_list]
                print(f"Click on centre point of one of the inserts you want to annotate:")

                if item == 0:
                    cv2.setMouseCallback("Resized image", draw_circle)
                else:
                    cv2.setMouseCallback("Resized image", draw_circle2)

                while True:
                    cv2.imshow("Resized image", new_image)
                    if cv2.waitKey(10) & 0xFF == 27:
                        print(
                            "Look at the real size of sampled areas. If too small, you'll be able to increase circular sampling areas in the next step.\nPress ESC.")
                        break
                cv2.destroyAllWindows()  # when ESC is pressed

                # getting orinal position on full-size image
                OriginalX = [int((coordx / new_width) * width) for coordx in mouseX]
                OriginalY = [int((coordy / new_height) * height) for coordy in mouseY]

                # Growing dictionary with values
                dictionary['Slice_path'].append(image_list[item])
                dictionary['X'].append(OriginalX)
                dictionary['Y'].append(OriginalY)
                dictionary['Z'].append(item + initial_slice_tag)
                dictionary['InsertType'].append(annotation_vals)
                dictionary['Color_of_insert'].append(color_used)
                dictionary['VoxelSize'].append(voxel_size)

                # draw filled circle in white on black background as mask
                mask = np.zeros((height, width, 3), dtype=np.uint8)
                radius = int(10 * scale_factor)

                for iteration in range(0, len(dictionary['X'])):
                    for idx in range(0, len(dictionary['X'][iteration])):
                        image_overlay = cv2.circle(image,
                                                   (dictionary['X'][iteration][idx], dictionary['Y'][iteration][idx]),
                                                   radius,
                                                   dictionary['Color_of_insert'][iteration][idx],
                                                   -1)

                        mask = cv2.circle(mask,
                                          (dictionary['X'][iteration][idx], dictionary['Y'][iteration][idx]),
                                          radius,
                                          dictionary['Color_of_insert'][iteration][idx],
                                          -1)

                # displaying
                cv2.namedWindow("Resized image", cv2.WINDOW_KEEPRATIO)
                cv2.imshow("Resized image", image_overlay)
                # cv2.resizeWindow("Resized image", 400, 400)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

                # saving overlay and mask
                cv2.imwrite(os.path.join(Phantom_folder,
                                         f"Slice_{item + initial_slice_tag}_MASK_Phantom_Original_Annotated_Phantom_slice.png"),
                            mask)
                cv2.imwrite(os.path.join(Phantom_folder,
                                         f"Slice_{item + initial_slice_tag}_Phantom_Original_Annotated_Phantom_slice.png"),
                            image_overlay)

                print('Do you want to grow the circles by what percentage?')
                # validating user input
                while True:
                    try:
                        pct = int(input("type a number between 200-300 \n"))
                        print('If satisfactory sampling areas are marked, press ESC.')
                        break
                    except ValueError:
                        print("Type in a valid number")

                radius = int(radius * (1 + pct / 100))
                mask = np.zeros((height, width, 3), dtype=np.uint8)
                dictionary['Radius'].append(radius)  # append updated radius to dictionary

                for iteration in range(0, len(dictionary['X'])):
                    for idx in range(0, len(dictionary['X'][iteration])):
                        image_overlay = cv2.circle(image,
                                                   (dictionary['X'][iteration][idx], dictionary['Y'][iteration][idx]),
                                                   radius,
                                                   dictionary['Color_of_insert'][iteration][idx],
                                                   -1)

                        mask = cv2.circle(mask,
                                          (dictionary['X'][iteration][idx], dictionary['Y'][iteration][idx]),
                                          radius,
                                          dictionary['Color_of_insert'][iteration][idx],
                                          -1)

                # displaying
                cv2.namedWindow("Resized image", cv2.WINDOW_KEEPRATIO)
                cv2.imshow("Resized image", image_overlay)
                # cv2.resizeWindow("Resized image", 400, 400)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

                cv2.imwrite(os.path.join(Phantom_folder,
                                         f"Slice_{item + initial_slice_tag}_MASK_Phantom_Original_Annotated_Phantom_slice.png"),
                            mask)
                cv2.imwrite(os.path.join(Phantom_folder,
                                         f"Slice_{item + initial_slice_tag}_Phantom_Original_Annotated_Phantom_slice.png"),
                            image_overlay)

                cv2.destroyAllWindows()
                loop_no += 1

            print("============")
            print("Initiating Phantom Extraction for scan in multithreading...\n")
            # COMPLETE : TODO save overlay of image original and coloured inserts
            # COMPLETE: TODO for each insert with (X,Y,Z) pairs fit a 3D vertical linear model and get positions through the stack for insert centres

            # reorganizing ditionary
            reorg_dic = {'Slice_path': [],
                         'XYZ': [],
                         'InsertType': [],
                         'Color_of_insert': [],
                         'Radius': [],
                         'VoxelSize': []}

            for element in insert_list:  # for each main insert
                position_list = []
                slice_list = []
                for iteration in range(0, len(dictionary['X'])):
                    index = dictionary['InsertType'][iteration].index(str.lower(element))  # find position in dictionary

                    x = dictionary['X'][iteration][index]
                    y = dictionary['Y'][iteration][index]
                    z = dictionary['Z'][iteration]
                    position_list.append([x, y, z])
                    colordummy = dictionary['Color_of_insert'][iteration][index]
                    slice_list.append(dictionary['Slice_path'][iteration])
                    radius_dummy = dictionary['Radius'][iteration]

                reorg_dic['XYZ'].append(position_list)
                reorg_dic['Slice_path'].append(slice_list)
                reorg_dic['VoxelSize'].append(voxel_size)
                reorg_dic['Color_of_insert'].append(colordummy)
                reorg_dic['Radius'].append(radius_dummy)
                reorg_dic['InsertType'].append(str.lower(element))

            DF = pd.DataFrame(reorg_dic)  # turning dictionary into pandas dataframe

            iteration_seq = []
            DF['Predicted_Circle_Centers_XYZ'] = " "
            DF['Measured_Density'] = " "

            for insert_number in range(0, len(DF['InsertType'])):
                XYZ = np.array(DF['XYZ'][insert_number])
                x = XYZ[:, 0]
                y = XYZ[:, 1]
                z = XYZ[:, 2]
                Color = np.array(DF['Color_of_insert'][insert_number])
                predicted_centres = polynomial_regression3d(x, y, z, 2)
                iteration_seq.append(predicted_centres)
            print("Insert Centre positions predicted for the rest of the Phantom Stack...\n")

            pd.options.mode.chained_assignment = None  # default='warn' --> this supress the warning
            # COMPLETE: TODO append positions of centre circles to dataframe and prescribed densities
            for df_row in range(0, len(iteration_seq)):
                DF['Predicted_Circle_Centers_XYZ'][df_row] = iteration_seq[df_row]
                DF['Measured_Density'][df_row] = Density_list_dic.get(DF['InsertType'][df_row])

            # COMPLETE: TODO function generate circle masks at each position across the stack for each insert - each image is an overlay of all predicted positions

            home_dir = Phantom_folder
            out_dir = os.path.join(home_dir, 'Phantom_Masks')
            if not os.path.isdir(out_dir):
                os.mkdir(out_dir)

            print("Exporting Phantom insert masks for visualization...")
            print(f"Phantom masks will be exported to {out_dir} \n")

            # get bounding box image dimensions
            image_example = cv2.imread(DF['Slice_path'][0][0]).shape
            # initiate numpy rgb mask
            mask = np.zeros((image_example[0], image_example[1], image_example[2]), dtype=np.uint8)
            gray_series = []

            print('Building iterator for parallelism...')

            start_time2 = time.time()
            iterator = build_iterator_for_parallelism(Dataframe=DF, Phantom_folder=Phantom_folder)
            extracted_grays = []
            print(f'--- Iterator created in {int(time.time() - start_time2)} seconds ---\n')

            ########### Paralelized  loop START  ############################
            print(f"Multithreading began. This may take up to 3 min to complete")
            with multiprocessing.Pool(processes=20) as p:
                # EXTRACTED_GRAYS_MASTER = p.starmap(get_grey_inside_circles, iterator)
                EXTRACTED_GRAYS_MASTER = p.starmap(get_grey_inside_circles, tqdm.tqdm(iterator, total=len(iterator)))

            ########### Parallel loop END  ############################
            print('Masks exported.')
            print('============\n')
            print('Saving results and diagnostic plots...')
            # unpack GRAYS AND ADD TO DF FOR PLOTTING
            DF['Extracted_Grays'] = ''
            # # COMPLETE: TODO append mean_gray_series to each insert in dataframe
            for insert_number in range(0, len(DF['InsertType'])):
                dummy_list = []
                for slice in range(0, len(EXTRACTED_GRAYS_MASTER)):
                    dummy_list.append(EXTRACTED_GRAYS_MASTER[slice][3][insert_number])
                DF['Extracted_Grays'][insert_number] = dummy_list

            # Saving Dataframe logfile, so if needed to update phantom final file there's no need to click on inserts and do manual extraction again, simply read this file in update mode
            DF.to_excel(os.path.join(Phantom_folder, f"PhantomLogFile_{scan_name}.xlsx"), index=False)

            # COMPLETE : TODO append to DF start_position and end_position for series extraction based on series inflexions
            # APPENDING EXTRA COLUMNS (BELOW IS SIMILAR TO DF_UPDATE function)
            infls_dummy_list = []
            # find inflexion points
            for insert in range(0, len(DF['InsertType'])):
                infls_tested = []
                series = DF['Extracted_Grays'][insert]
                # smooth
                smooth = gaussian_filter1d(series, len(series) * 0.2)
                # compute second derivative
                smooth_d2 = np.gradient(np.gradient(smooth))
                # find switching points
                infls = np.where(np.diff(np.sign(smooth_d2)))[0]

                if len(infls) < 2:
                    infls_tested = [0, len(series)]
                if len(infls) >= 2:
                    infls_tested = [min(infls), max(infls)]

                infls_dummy_list.append(infls_tested)

            DF['Slice_range'] = ''
            DF['Median_Gray_for_Calib'] = ''
            DF['Median_CI_95'] = ''
            DF['Median_StdError'] = ''
            DF['Scan_name'] = ''
            DF['Phantom_type'] = ''

            for insert in range(0, len(DF['InsertType'])):
                DF['Slice_range'][insert] = [item + initial_slice_tag for item in infls_dummy_list[insert]]

                series = DF['Extracted_Grays'][insert]
                ranged = series[infls_dummy_list[insert][0]:
                                infls_dummy_list[insert][1]]

                # COMPLETE TODO append median gray for insert inside selected envelope
                DF['Median_Gray_for_Calib'][insert] = round(np.median(ranged), 2)
                DF['Scan_name'] = scan_name

                # applying bootstrapping of median
                # create 95% confidence interval for population median based on bootstrapping
                np.random.seed(13)
                boot_sample_medians = []
                std_error = []
                number_iterations = 10000

                sample_1 = np.random.choice(series,
                                            size=int(len(series)))  # flag numbers in population to randomly change

                for i in range(number_iterations):
                    boot_sample = np.random.choice(sample_1, replace=True, size=int(len(series)))
                    boot_median = np.median(boot_sample)
                    boot_sample_medians.append(boot_median)

                # stand error and confidence interval of the median
                # std
                std_error = np.std(boot_sample_medians)
                # the average value of repeated samples' median values
                # C.I.
                boot_median_CI = np.percentile(boot_sample_medians, [2.5, 97.5])
                CI = boot_median_CI.tolist()

                DF['Median_CI_95'][insert] = CI
                DF['Median_StdError'][insert] = std_error
                DF['Phantom_type'][insert] = answer.lower()

            # TODO plot figure function
            fig, ax = plt.subplots()
            plt.rcParams['axes.facecolor'] = 'white'  # this is if you want to change plot background color
            label_list = []

            for insert in range(0, len(DF['InsertType'])):
                series = DF['Extracted_Grays'][insert]

                labeldummy = DF['InsertType'][insert]
                label_list.append(labeldummy)
                colordummy = []
                colordummy = [round(x / 255, 1) for x in DF['Color_of_insert'][insert]]
                b = colordummy[0]
                g = colordummy[1]
                r = colordummy[2]
                # swap positions to make it rgb
                colordummy = [r, g, b]
                colordummy.append(1)
                if labeldummy == 'air':  # change to gray so color shows on a white background
                    colordummy = [211 / 255, 211 / 255, 211 / 255]

                ax.plot(
                    list(range(initial_slice_tag, initial_slice_tag + len(series))),
                    series,
                    color=colordummy,
                    linestyle='solid',
                    linewidth=1,
                    alpha=0.3,
                    label=DF['InsertType'][insert])

                labeldummy = DF['InsertType'][insert] + "_median"

                label_list.append(labeldummy)
                ax.hlines(y=DF['Median_Gray_for_Calib'][insert],
                          xmin=initial_slice_tag,
                          xmax=initial_slice_tag + len(series),
                          colors=colordummy,
                          linestyles='-',
                          linewidth=0.5,
                          alpha=0.6,
                          lw=1,
                          label=DF['InsertType'][insert] + "_median"
                          )

                # ax.set_xticklabels(range(initial_slice_tag, initial_slice_tag + len(series)))
                # ax.axvspan(max(DF['Slice_range'][insert])+initial_slice_tag, min(DF['Slice_range'][insert])+initial_slice_tag, alpha=0.1, color='grey') #if you want to plot a filled area of the ideal range

            # shade between inflexions
            # find common interval
            # overlap_range = find_overlapping_range(infls_dummy_list)
            # ax.axvspan(max(overlap_range), min(overlap_range), alpha=0.1, color='magenta', fill=('/'))

            ax.set_ylim([0, 70000])
            # Shrink current axis by 20%
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            # Put a legend to the right of the current axis
            ax.legend(label_list, loc='center left', bbox_to_anchor=(1, 0.5))
            ax.grid('on')
            # ax.legend(loc='upper right')
            ax.set_xlabel('Slice number')
            ax.set_ylabel('Grey value')
            ax.set_title(f"{scan_name} \n - Extracted values from phantom inserts")
            # plt.show()

            #  COMPLETE todo save figure inside STANDARD_EXTRACT
            plt.savefig(os.path.join(Phantom_folder, f"Overlay_Extracted_Vals_{scan_name}.png"), dpi=300)

            # COMPLETE todo convert Dataframe to CSV spreadsheet
            DF.to_excel(os.path.join(Phantom_folder, f"STANDARD_EXTRACTED_VALUES_{scan_name}.xlsx"), index=False)

            if answer.lower() == 'extended':  # if extended phantom, then also save a file with just the 5 inserts and epoxy --> for comparisson on how the fit improves when having extended phantom
                df = DF
                # df.drop(df[df['InsertType'] == 'air'].index, inplace=True)
                df.drop(df[df['InsertType'] == 'sugar'].index, inplace=True)
                df.drop(df[df['InsertType'] == 'oil'].index, inplace=True)
                df.drop(df[df['InsertType'] == 'coffee'].index, inplace=True)
                df.drop(df[df['InsertType'] == 'aluminum'].index, inplace=True)
                df.to_excel(os.path.join(Phantom_folder, f"STANDARD_EXTRACTED_VALUES_{scan_name}_PNarrow.xlsx"))

            print('Density phantom extraction finished!')

    if already_extracted:  # all files extracted and we have items in 'already_extracted'
        userInput = ''
        while userInput.lower() not in ['y', 'yes', 'n', 'no']:
            userInput = input('Would you like to perform a file update on Phantom Files? (Y/N): ')
            userInput = userInput.lower()

        if userInput == 'y' or userInput == 'yes':
            print('Entered file update mode')

            for folder in already_extracted:
                # TODO append median confidence interval for each insert in STANDARD_EXTRACT_FILE
                scan_name = get_scan_name(folder_name=folder,
                                          dir_standard_names=project_dir_list)

                Phantom_folder = os.path.join(selected_project_dir, scan_name, 'STANDARD_EXTRACT')

                for file in glob.glob(os.path.join(Phantom_folder, 'STANDARD_EXTRACTED') + '*.xlsx'):
                    print('Located the following file to update')
                    print(file)
                    DF = pd.read_excel(file, index_col=0)  # importing data form excel file

                    # TODO: amend with updates on DF

                    ##### HERE'S WHERE UPDATES HAPPEN
                    # TODO existing phantom files need to be replaced following bootstrapping reanalyses of greyscale probing
                    DF_update(Dataframe=DF)
                    # COMPLETE overwrite spreadsheet
                    print('Overwriting file...')
                    DF.to_excel(file, index=False)

            print('All files updated')

        elif userInput == 'n' or userInput == 'no':
            print('Exiting file update mode...')

    print(f"Runtime {int((time.time() - start_time))} seconds")
