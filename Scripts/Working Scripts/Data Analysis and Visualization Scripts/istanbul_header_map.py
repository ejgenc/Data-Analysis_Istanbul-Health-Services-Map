# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 17:02:28 2020

------ What's this file? ------

This script is responsible for the analysis and visualization of the spatial
distribution of healthcare institution across Istanbul districts.

The code produces visualizations in both Turkish and English.

The result is a big choropleth map with no labels that will serve as the header for
the Medium article
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
import geopandas as gpd #A module built on top of pandas for geospatial analysis
from pyproj import CRS #For CRS (Coordinate Reference System) functions
from shapely.geometry import Point, MultiPoint #Required for point/polygon geometry
from shapely.ops import nearest_points #Required for nearest neighbor analysis
import contextily as ctx #Used in conjuction with matplotlib/geopandas to set a basemap
from geopy import distance #For geodesic distance calculation (radians to meters)


#from matplotlib import rc
#rc('text', usetex=True)
#rc('text.latex', preamble=r'\usepackage{color}')

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

#Color emphasis

emphasis_color = cm.Set2.colors[2]


#%% --- Read in the datasets ---

#Istanbul health services data
health_fp = "../../../Data/Non-GIS Data/cleaned/istanbul_healthservices_cleaned.csv"
health = pd.read_csv(health_fp)

#Istanbul geospatial districts data
istanbul_districts_fp = "../../../Data/GIS data/Processed/istanbul_districts.shp"
istanbul_districts = gpd.read_file(istanbul_districts_fp, )

#%% --- Data Preparation ---


#Create for English
h_inst_per_district_eng = health.loc[:,"district_eng"].value_counts().sort_values(ascending = False).reset_index()
h_inst_per_district_eng.rename(columns = {"index" : "district_e",
                                       "district_eng" : "health_count"},
                                        inplace = True) 

#Merge with geodataframe
istanbul_districts = istanbul_districts.merge(h_inst_per_district_eng,
                                               on = "district_e",
                                               how = "left")

#Now, this information can be used for both TR and eng

#%% --- Visualization - English ---

# --- Figure Preparation ---

fig = plt.figure(figsize = (19.20,19.20))

ax_1 = fig.add_subplot(1,1,1)

#                            --- MAP: ---

# --- Plot Figure ---

istanbul_districts.plot(ax = ax_1,
                    column = "health_count",
                    edgecolor = "black",
                    alpha = 1,
                    cmap = cm.YlGnBu)

# --- Set Basemap ---

ctx.add_basemap(ax_1, zoom = 11, #16
                crs='epsg:4326',
                source=ctx.providers.Esri.WorldGrayCanvas)

# --- Spine and Grid ---

ax_1.set_axis_off() # Turn off axis

# --- Map Labels ---

#Select districts that you want labels for
districts_to_label_list = ["Silivri", "Catalca", "Buyukcekmece", "Arnavutkoy", "Eyupsultan", "Sariyer",
                           "Beykoz", "Sile", "Cekmekoy", "Tuzla", "Pendik", "Maltepe", "Basaksehir"]

districts_to_label_indexes = [31, 5, 16, 3, 20, 33, 13, 1, 17, 37, 30]

#Create a boolean indexing mask checking for those districts
labels_mask = istanbul_districts.loc[:,"district_e"].isin(districts_to_label_list)

#Pass in the boolean mask to create a dataframe
districts_to_label = istanbul_districts.loc[labels_mask,["district_e", "geometry"]]

#Create a representative point within each district polygon to place the label
districts_to_label["representative_point"] = districts_to_label.geometry.representative_point().geometry.values

#Pass over each row label the repsentative point according to that row's name
for idx, row in districts_to_label.iterrows():
    ax_1.annotate(s=row["district_e"], xy=(row["representative_point"].x,row["representative_point"].y),
                 horizontalalignment='center')
    
# --- Misc ---

# Remove the empty white-space around the axes
plt.tight_layout()

#--- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")


#%% --- Visualization - Turkish ---

# --- Figure Preparation ---

fig = plt.figure(figsize = (19.20,19.20))

ax_1 = fig.add_subplot(1,1,1)

#                            --- MAP: ---

# --- Plot Figure ---

istanbul_districts.plot(ax = ax_1,
                    column = "health_count",
                    edgecolor = "black",
                    alpha = 1,
                    cmap = cm.YlGnBu)

# --- Set Basemap ---

ctx.add_basemap(ax_1, zoom = 11, #16
                crs='epsg:4326',
                source=ctx.providers.Esri.WorldGrayCanvas)

# --- Spine and Grid ---

ax_1.set_axis_off() # Turn off axis

# --- Map Labels ---

#Select districts that you want labels for
districts_to_label_list = ["Silivri", "Catalca", "Buyukcekmece", "Arnavutkoy", "Eyupsultan", "Sariyer",
                           "Beykoz", "Sile", "Cekmekoy", "Tuzla", "Pendik", "Maltepe", "Basaksehir"]

districts_to_label_indexes = [31, 5, 16, 3, 20, 33, 13, 1, 17, 37, 30]

#Create a boolean indexing mask checking for those districts
labels_mask = istanbul_districts.loc[:,"district_e"].isin(districts_to_label_list)

#Pass in the boolean mask to create a dataframe
districts_to_label = istanbul_districts.loc[labels_mask,["district_t", "geometry"]]

#Create a representative point within each district polygon to place the label
districts_to_label["representative_point"] = districts_to_label.geometry.representative_point().geometry.values

#Pass over each row label the repsentative point according to that row's name
for idx, row in districts_to_label.iterrows():
    ax_1.annotate(s=row["district_t"], xy=(row["representative_point"].x,row["representative_point"].y),
                 horizontalalignment='center')

# --- Misc ---

# Remove the empty white-space around the axes
plt.tight_layout()

# --- Export Visualization ---

#As svg
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")






