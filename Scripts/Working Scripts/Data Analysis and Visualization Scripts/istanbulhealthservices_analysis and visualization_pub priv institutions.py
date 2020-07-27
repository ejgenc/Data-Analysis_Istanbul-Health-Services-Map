# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 17:02:28 2020

------ What's this file? ------

This script is responsible for the analysis and visualization of private and
public healthcare institutions that can be found across Istanbul.

The code produces visualizations in both Turkish and English.

The visualization will be a stacked bar chart that shows
the number of both public and private institutions per institution type.

--------------------------------

@author: ejgen
"""

#%% --- Import required packages ---
import numpy as np #Required for pandas
import pandas as pd #For general data processing tasks
import matplotlib.pyplot as plt #For plotting
import matplotlib.cm as cm
import matplotlib.colors as col
import os

#%% --- Dynamically create a directory named after the file for outputs ---

#Get the absolute filepath
dirname = os.path.dirname(__file__)

#Split by \ to make it into relative
dirname_intermediary = dirname.split("\\")

#Join in a way that would make it relative
separator = r"/"
dirname_final = separator.join(dirname_intermediary[0:5])

#Craft a filepath without the final folder to which the plot will be exported
incomplete_output_directory = dirname_final + "/Data Analysis_Istanbul Health Services Map/Media/Plots/"

#Get the name of the script
filename = os.path.basename(__file__)

#Split by _
filename_split = filename.split("_")

#Get the last to get the last folder name
filename_final = filename_split[-1]

#Remove the .py suffix
filename_final_processed = filename_final.split(".")[0]

#Craft the complete output directory
complete_output_directory = incomplete_output_directory + filename_final_processed

#Create the directory using os.mkdir.
try:
    os.mkdir(complete_output_directory)
except:
    pass

#%% --- Helper functions and definitions ---

# Helper function: Add labels to the top of a bar chart.
def add_value_labels(ax, spacing=5):
    """Add labels to the end of each bar in a bar chart.

    Arguments:
        ax (matplotlib.axes.Axes): The matplotlib object containing the axes
            of the plot to annotate.
        spacing (int): The distance between the labels and the bars.
    """

    # For each bar: Place a label
    for rect in ax.patches:
        # Get X and Y placement of label from rect.
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2

        # Number of points between bar and label. Change to your liking.
        space = spacing
        # Vertical alignment for positive values
        va = 'bottom'

        # If value of bar is negative: Place label below bar
        if y_value < 0:
            # Invert space to place label below
            space *= -1
            # Vertically align label at top
            va = 'top'

        # Use Y value as label and format number with one decimal place
        label = "{:}".format(y_value) #Remove .1f if you don't want one decimal place

        # Create annotation
        ax.annotate(
            label,                      # Use `label` as label
            (x_value, y_value),         # Place label at end of the bar
            xytext=(0, space),          # Vertically shift label by `space`
            textcoords="offset points", # Interpret `xytext` as offset in points
            ha='center',                # Horizontally center label
            va=va,                      # Vertically align label differently for  positive and negative values.
            rotation = 90,
            fontsize = 15)              # Rotate label
                             
# Helper definitions --- Set dictionaries for fonts

# Set font info
font_title = {'family': 'sans-serif',
              "fontname": "Arial",
              'color':  'black',
              'weight': 'bold',
              'size': 30}

#Gill Sans MT doesn't work for Turkish charset.
font_axislabels = {'family': 'sans-serif',
                   "fontname": "Arial",
                   'color':  'black',
                   'weight': 'bold',
                   'size': 20}

font_xticks = {'family': 'sans-serif',
                   "fontname": "Arial",
                   'color':  'black',
                   'weight': 'bold',
                   'size': 16}

font_yticks = {'family': 'sans-serif',
                   "fontname": "Arial",
                   'color':  'black',
                   'weight': 'normal',
                   'size': 16}

font_figtitle = {'family': 'sans-serif',
              "fontname": "Arial",
              'color':  'black',
              'weight': 'bold',
              'size': 90}

    
# Helper definitions --- Set color for graphs

#Color quantitative sequential

def sequential_color_mapper(value):
    sequential_cmap = cm.ScalarMappable(col.Normalize(0, max(value)), cm.YlGnBu)
    return sequential_cmap

#Color categorical

categorical_color = cm.Set2.colors[0]
categorical_color_2 = cm.Set2.colors[3]

#Color emphasis

emphasis_color = cm.Set2.colors[2]


#%% --- Read in the datasets ---

#Istanbul health services data
health_fp = "../../../Data/Non-GIS Data/cleaned/istanbul_healthservices_cleaned.csv"
health = pd.read_csv(health_fp)


#%% --- Data Preparation ---

#Group by private and public
grouped_by_privpublic = health.groupby("private_or_public")

#Get public - private groups
health_public = grouped_by_privpublic.get_group("Public")
health_private = grouped_by_privpublic.get_group("Private")

#Get the institution_types vcounts private institutions
health_private_vcounts_eng = health_private.loc[:,"institution_type_eng"].value_counts()
health_private_vcounts_tr = health_private.loc[:,"institution_type"].value_counts()

#Create a mask out of hinstitutions that are private
health_private_instype_mask = health_public.loc[:,"institution_type"].isin(health_private_vcounts_tr.index)

#Select public institutions that also have a priv counterpart
health_public_pubcountepart = health_public.loc[health_private_instype_mask,:]

#TR - Get the institution_types vcounts for public instiutions
health_public_pubcountepart_vcounts_tr = health_public_pubcountepart.loc[:,"institution_type"].value_counts()
#ENG - Get the institution_types vcounts for public instiutions
health_public_pubcountepart_vcounts_eng = health_public_pubcountepart.loc[:,"institution_type_eng"].value_counts()

#Merge datsets
health_merged_eng = pd.merge(left = health_private_vcounts_eng.reset_index(),
                             right = health_public_pubcountepart_vcounts_eng.reset_index(),
                             on = "index",
                             suffixes = ("_priv", "_pub"))

health_merged_tr = pd.merge(left = health_private_vcounts_tr.reset_index(),
                             right = health_public_pubcountepart_vcounts_tr.reset_index(),
                             on = "index",
                             suffixes = ("_priv", "_pub"))

#%% --- Visualization - English ---

# --- Figure Preparation ---

fig = plt.figure(figsize = (25.60,14.40))

ax = fig.add_subplot(1,1,1)

# --- Data Selection ---

#Get labels for x - axis ticks
labels = list(health_merged_eng.loc[:,"index"])

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1
bar_positions_2 = [x + 0.45 for x in bar_positions]

#Get bar heights from data
bar_heights_priv = health_merged_eng.loc[:,"institution_type_eng_priv"]
bar_heights_pub = health_merged_eng.loc[:,"institution_type_eng_pub"]


# --- Plot Figure ---

ax.bar(bar_positions,bar_heights_priv,
    width = 0.45,
    align = "center",
    color = categorical_color)

ax.bar(bar_positions_2,bar_heights_pub,
    width = 0.45,
    align = "center",
    color = categorical_color_2)

# --- Add Legend ---

plt.legend(["Private Inst.", "Public Inst."],loc=1,prop={'size': 30})

# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax.set_xticks([x + 0.45 / 2 for x in bar_positions])

#Setting x-tick labels and positions
ax.set_xticklabels(labels, rotation = 40)

# Setting custom y-axis tick intervals
start, end = ax.get_ylim()
ax.yaxis.set_ticks(np.arange(start,end, 25))


# --- Spine and Grid ---

#Disable right and top spine
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# --- Text ---

ax.set_title("Out of 33 types, 8 types of healtcare institutions are also operated by the private sector.\n There are more institutions operated by the private sector in general in the categories they are allowed to.",
             fontdict = font_title,
             pad = 20)


#Add x axis label
ax.set_xlabel("Types of healthcare institutions",
              fontdict = font_axislabels,
              labelpad = -10)

# Add y axis label
ax.set_ylabel("Number of health institutions",
              fontdict = font_axislabels,
              labelpad= 18)

#Set xtick font info

ax.set_xticklabels(ax.get_xticklabels(),
                     font_xticks)


# Add labels to the top of the bars
add_value_labels(ax)

#
plt.tight_layout() 

# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")

#%% --- Visualization - Turkish ---

# --- Figure Preparation ---

fig = plt.figure(figsize = (25.60,14.40))

ax = fig.add_subplot(1,1,1)

# --- Data Selection ---

#Get labels for x - axis ticks
labels = list(health_merged_tr.loc[:,"index"])

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1
bar_positions_2 = [x + 0.45 for x in bar_positions]

#Get bar heights from data
bar_heights_priv = health_merged_tr.loc[:,"institution_type_priv"]
bar_heights_pub = health_merged_tr.loc[:,"institution_type_pub"]


# --- Plot Figure ---

ax.bar(bar_positions,bar_heights_priv,
    width = 0.45,
    align = "center",
    color = categorical_color)

ax.bar(bar_positions_2,bar_heights_pub,
    width = 0.45,
    align = "center",
    color = categorical_color_2)

# --- Add Legend ---

plt.legend(["Özel", "Devlet"],loc=1,prop={'size': 30})

# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax.set_xticks([x + 0.45 / 2 for x in bar_positions])

#Setting x-tick labels and positions
ax.set_xticklabels(labels, rotation = 40)

# Setting custom y-axis tick intervals
start, end = ax.get_ylim()
ax.yaxis.set_ticks(np.arange(start,end, 25))


# --- Spine and Grid ---

#Disable right and top spine
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# --- Text ---

ax.set_title("33 tür sağlık kuruluşundan 8'i özel sektör tarafından da işletilebiliyor. \n Bu 8 tür kuruluş içinde özel işletme sayısı devletten genelde daha fazla.",
             fontdict = font_title,
             pad = 20)


#Add x axis label
ax.set_xlabel("Sağlık Kuruluşu Türü",
              fontdict = font_axislabels,
              labelpad = -10)

# Add y axis label
ax.set_ylabel("Sağlık kuruluşu sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

#Set xtick font info

ax.set_xticklabels(ax.get_xticklabels(),
                     font_xticks)


# Add labels to the top of the bars
add_value_labels(ax)

#
plt.tight_layout() 

# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")















