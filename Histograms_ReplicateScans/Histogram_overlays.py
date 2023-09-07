#  This software was developed by Leonardo Bertini (l.bertini@nhm.ac.uk) at the Natural History Museum (London,UK).
#
#  This is released as Supporting Material as part of the following publication:
#  "XXXXXX" (link to paper and DOI once published).
#  #
#
#  Copyright (c) 2023.
#
#  The code is distributed under the MIT license https://en.wikipedia.org/wiki/MIT_License

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
from tkinter import filedialog
from tkinter import *
import os
from pathlib import Path
import scipy.stats
from distinctipy import distinctipy

def init_fig():
    fig = plt.figure()
    fig.set_size_inches(20, 10)
    ax = plt.subplot()
    ax.grid(True)
    ax.set_xlabel('Grey Intensity bin', fontsize=18)
    ax.set_ylabel('Voxel Count', fontsize=18)
    ax.xaxis.set_minor_locator(tck.AutoMinorLocator())
    plt.rcParams['font.size'] = '18'
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    return ax, fig


def baseplot_histogram(df_filtered, ax, color, label):
    # todo make plot overlay of histograms for each colony
    Grays_hist = df_filtered[0][1:-4]
    Count_hist = df_filtered[1][1:-4]

    ske = str(scipy.stats.skew(Count_hist))[:5]
    kurt = str(scipy.stats.kurtosis(Count_hist))[:6]

    label2 = label + ' Skewness: ' + ske + ' Kurtosis: ' + kurt
    ax.plot(Grays_hist, Count_hist, color=color, label=label2)


def filter_histogram_bell_plot_2(file_path):
    # Step 1: read histogram csv file from main dir in calib_results
    hist_scan = pd.read_csv(file_path, header=None)
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


def colony_histograms(colony_tag, experiment_phase, group, color_list):
    ax,fig = init_fig()
    path_list = []
    label_list = []

    if experiment_phase == 'Phase 2':
        for item in calib_results:
            if colony_tag in item:
                print(item)
                label_dummy = str(Path(item))  # two_up
                scan_name = label_dummy.split('\\')[3].split('Histogram-')[1].split(colony_tag)[0]+ colony_tag

                if '1048' in scan_name:  # fixing
                    scan_name = scan_name.replace('Poritres', 'Porites').replace('COEL1048', 'COEL_1048')

                voltage = label_dummy.split('\\')[3].split(colony_tag)[1].split('_')[1]
                filter = label_dummy.split('\\')[3].split(colony_tag)[1].split('_')[2]
                dummy_label = 'Voltage ' + voltage + ' Filter ' + filter
                path_list.append(item)
                label_list.append(dummy_label)

        for n in range(0, len(path_list)):
            filtered = filter_histogram_bell_plot_2(path_list[n])
            baseplot_histogram(filtered, ax, color=color_list[n], label=label_list[n])

        ax.legend(loc=2, frameon=True)
        ax.set_title(scan_name)
        ax.set_ylim(-5000, 250000)
        fig.tight_layout()

    if experiment_phase == 'Phase 1' and group =='Beam_Hardening':
        for item in calib_results:
            if colony_tag in item:
                print(item)
                label_dummy = str(Path(item))  # two_up
                scan_name_dummy = label_dummy.split('\\')[3].split('Histogram-')[1].split(colony_tag)[0].split('.csv')[0]

                voltage = scan_name_dummy.split('_')[3]
                filter = scan_name_dummy.split('_')[4]
                dummy_label = 'Voltage ' + voltage + ' Filter ' + filter+'mm'
                path_list.append(item)
                label_list.append(dummy_label)

        for n in range(0, len(path_list)):
            filtered = filter_histogram_bell_plot_2(path_list[n])
            baseplot_histogram(filtered, ax, color=color_list[n], label=label_list[n])

        ax.legend(loc=0, frameon=True)
        namefinal=scan_name_dummy.split('_'+voltage)[0]
        ax.set_title(namefinal + ' Beam Hardening Correction Applied')
        ax.set_ylim(-5000, 200000)
        fig.tight_layout()

    if experiment_phase == 'Phase 1' and group =='Normal':
        for item in calib_results:
            if colony_tag in item and 'BH' not in item:
                print(item)
                label_dummy = str(Path(item))  # two_up
                scan_name_dummy = label_dummy.split('\\')[3].split('Histogram-')[1].split('.csv')[0]
                voltage = scan_name_dummy.split('_')[3]
                filter = scan_name_dummy.split('_')[4]
                dummy_label = 'Voltage ' + voltage + ' Filter ' + filter+'mm'
                path_list.append(item)
                label_list.append(dummy_label)

        for n in range(0, len(path_list)):
            filtered = filter_histogram_bell_plot_2(path_list[n])
            baseplot_histogram(filtered, ax, color=color_list[n], label=label_list[n])

        ax.legend(loc=0, frameon=True)
        namefinal=scan_name_dummy.split('_'+voltage)[0]
        ax.set_title(namefinal)
        ax.set_ylim(-5000, 200000)
        fig.tight_layout()

    if experiment_phase == 'Phase 0' and group == 'Normal':

        for item in calib_results:
            if colony_tag in item:
                print(item)
                label_dummy = str(Path(item))  # two_up
                scan_name_dummy = label_dummy.split('\\')[3].split('Histogram-')[1].split('.csv')[0]
                #voltage = scan_name_dummy.split('_')[3]
                #filter = scan_name_dummy.split('_')[4]
                #dummy_label = 'Voltage ' + voltage + ' Filter ' + filter + 'mm'
                path_list.append(item)
                label_list.append(scan_name_dummy)

        for n in range(0, len(path_list)):
            filtered = filter_histogram_bell_plot_2(path_list[n])
            baseplot_histogram(filtered, ax, color=color_list[n], label=label_list[n])

        ax.legend(loc=0, frameon=True)
        namefinal = scan_name_dummy.split('_' + voltage)[0]
        ax.set_title(namefinal)
        ax.set_ylim(-5000, 200000)
        fig.tight_layout()


#generating color pallete
#colors= distinctipy.get_colors(15)
list_of_colors = [(0.02186354632925891, 0.9972302321526076, 0.1554268791065041), (1.0, 0.0, 1.0), (0.0, 0.5, 1.0), (1.0, 0.5, 0.0), (0.5, 0.25, 0.5), (0.5625693631056269, 0.7871173336963213, 0.525162401425188), (0.2215537438868661, 0.003711526387561004, 0.9802429387466912), (0.8845026145659524, 0.5040877770333716, 0.9915446989632718), (0.1758588405513144, 0.50912102141811, 0.06660434613732791), (1.0, 0.0, 0.0), (0.0, 1.0, 1.0), (1.0, 1.0, 0.0), (0.0, 0.0, 0.5), (0.02354152449655922, 0.6245371615702314, 0.5024523061047984), (0.9990032742451534, 0.2674079610613883, 0.5562901660307321)]

#Selecting parent folder where scan folders are
root = Tk()
root.withdraw()
top_dir = filedialog.askdirectory(title='Select the Parent folder where Phase 2 Histograms are')
target_name = "Histogram-LB"

calib_results = []
for (dirpath, dirnames, filenames) in os.walk(top_dir):
    for f in filenames:
        if target_name in f:
            print(f"Found histogram in {os.path.join(dirpath, f)}")
            calib_results.append(os.path.join(dirpath, f))
print('\n')

#get histograms for each scan of phase 2
colony_histograms(colony_tag='10165',experiment_phase='Phase 2', group='Normal', color_list=list_of_colors)
plt.savefig('Histograms_Colony_10165.png')

colony_histograms(colony_tag='6781', experiment_phase='Phase 2', group='Normal',  color_list=list_of_colors)
plt.savefig('Histograms_Colony_6781.png')

colony_histograms(colony_tag='6785', experiment_phase='Phase 2', group='Normal', color_list=list_of_colors)
plt.savefig('Histograms_Colony_6785.png')

colony_histograms(colony_tag='1048', experiment_phase='Phase 2', group='Normal', color_list=list_of_colors)
plt.savefig('Histograms_Colony_1048.png')


#get histograms for each scan of phase 1
#Selecting parent folder where scan folders are
root = Tk()
root.withdraw()
top_dir = filedialog.askdirectory(title='Select the Parent folder where Phase 1 Histograms are')
target_name = "Histogram"

calib_results = []
for (dirpath, dirnames, filenames) in os.walk(top_dir):
    for f in filenames:
        if target_name in f:
            print(f"Found histogram in {os.path.join(dirpath, f)}")
            calib_results.append(os.path.join(dirpath, f))
print('\n')

calib_results.sort()
colony_histograms(colony_tag='perc_BH', experiment_phase='Phase 1', group='Beam_Hardening', color_list=list_of_colors)
plt.savefig('Histograms_Colony_1981_Beam_Hardening.png')
colony_histograms(colony_tag='1981-3-5', experiment_phase='Phase 1', group='Normal', color_list=list_of_colors)
plt.savefig('Histograms_Colony_1981.png')

colony_histograms(colony_tag='RS', experiment_phase='Phase 0', group='Normal', color_list=list_of_colors)
