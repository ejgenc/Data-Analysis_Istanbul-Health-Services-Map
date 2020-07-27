# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 16:22:19 2020

@author: ejgen

------ What's this file? ------
                
This script is responsible for the analysis and visualization of the distribution
of private healthcare institutions across Istanbul.

The code produces visualizations in both Turkish and English.

The visualization will be a small multiples that has two figures:
    
    -- The upmost figure is a choropleth map that shows the number of
    private health institutions per districts.
    
    -- The bottom figure is a scatterplot that shows the relationship
    in between a district's economic situation and the num. of private health institutions

--------------------------------
"""

#%% --- ENVIRONMENT CHECK ---
#The module dependencies of this script are located within my conda environment
# "mappingenv"

#%% --- Import required packages ---

import numpy as np #Required for pandas
import pandas as pd #For general data processing tasks
import matplotlib.pyplot as plt #For plotting
import matplotlib.cm as cm
import matplotlib.colors as col
import geopandas as gpd #A module built on top of pandas for geospatial analysis
from pyproj import CRS #For CRS (Coordinate Reference System) functions
from shapely.geometry import Point, MultiPoint #Required for point/polygon geometry
from shapely.ops import nearest_points #Required for nearest neighbor analysis
import contextily as ctx #Used in conjuction with matplotlib/geopandas to set a basemap
from geopy import distance #For geodesic distance calculation (radians to meters)
import os
from scipy import stats as st

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
            fontsize = 12)              # Rotate label
                             
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

font_xticks = {'family': 'sans-serif', #Modified for this plot
                   "fontname": "Arial",
                   'color':  'black',
                   'weight': 'normal',
                   'size': 12}

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


#Istanbul geospatial districts data
istanbul_districts_fp = "../../../Data/GIS data/Processed/istanbul_districts.shp"
istanbul_districts = gpd.read_file(istanbul_districts_fp)

#Istanbul districts extra data
districts_extra_fp = "../../../Data/Non-GIS Data/external/district_income.xlsx"
districts_extra = pd.read_excel(districts_extra_fp)

#%% --- Data Preparation ---

# --- Private hcare institution per district ---

#Create a boolean indexing mask
priv_mask = health.loc[:,"private_or_public"] == "Private"

#Select by mask + groupby
priv_only_grouped = health.loc[priv_mask,:].groupby("district_eng")

#Get value counts from the grouped object
priv_only_count = priv_only_grouped["private_or_public"].value_counts()

#Join with districts_extra

districts_private_and_income = pd.merge(priv_only_count,districts_extra,
                                        how = "right",
                                        on = "district_eng")

#REPLACE NAN WITH 0!

districts_private_and_income.loc[:,"private_or_public"].fillna(0, inplace = True)

#Join with geodataframe

#Fix some naming problems
extract = districts_private_and_income.loc[:,["district_eng",
                                              "private_or_public","yearly_average_household_income"]]

extract.rename(columns = {"district_eng" :"district_e",
                          "private_or_public" : "private_count"},
                           inplace = True)

istanbul_districts_merged = istanbul_districts.merge(extract,
                                               on = "district_e",
                                               how = "left")

#REPLACE NAN WITH 0!

istanbul_districts_merged.loc[:,"private_count"].fillna(0, inplace = True)
#%% ================ VERSION ONE ======================
#%% --- Visualization - English ---

# --- Figure Preparation ---

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

#Define a gridspect of 2 rows and 2 columns
gs = fig.add_gridspec(2, 2)

#The first ax will occupy all space of row 1
ax_1 = fig.add_subplot(gs[0,:])

#The second ax will occupy first place out of 2 in row 2
ax_2 = fig.add_subplot(gs[1,0])

#The third ax will occupy second place out of 2 in row 2
ax_3 = fig.add_subplot(gs[1,1])

# --- Plotting ---

#       --- Ax_1 : Map ---
istanbul_districts_merged.plot(ax = ax_1,
                    column = "private_count",
                    edgecolor = "black",
                    alpha = 1,
                    cmap = cm.YlGnBu)

ctx.add_basemap(ax_1, zoom = 11, #16
                crs='epsg:4326',
                source=ctx.providers.Esri.WorldGrayCanvas)

# --- Spine and Grid ---

ax_1.set_axis_off() # Turn off axis

# --- Map Labels ---

#Select districts that you want labels for
districts_to_label_list = ["Silivri", "Catalca", "Buyukcekmece", "Arnavutkoy", "Eyupsultan", "Sariyer",
                           "Beykoz", "Sile", "Cekmekoy", "Tuzla", "Pendik", "Maltepe", "Basaksehir"]

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

#   --- Ax_2 : Scatterplot ---

ax_2.scatter(x =  districts_private_and_income.loc[:,"yearly_average_household_income"],
             y =  districts_private_and_income.loc[:,"private_or_public"],
             s = 150, # To specify face width
             c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_2.spines['right'].set_visible(False)
ax_2.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_2.set_xlabel("Average yearly household income (thousand TL)",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_2.set_ylabel("Number of private health institutions",
              fontdict = font_axislabels,
              labelpad= 18)

# #Label certain datapoints

# districts_to_label = ["Kadikoy","Besiktas", "Bakirkoy","Adalar",
#                       "Sisli", "Sariyer","Uskudar"]

# districts_to_label_mask = districts_private_and_income.loc[:,"district_eng"].isin(districts_to_label)

# districts_to_label_xy_df = districts_private_and_income.loc[districts_to_label_mask,["district_eng","private_or_public","yearly_average_household_income"]]

# for idx, row in districts_to_label_xy_df.iterrows():
#     x = row["private_or_public"] + 3 #To align it properly
#     y = row["yearly_average_household_income"]
#     ax_2.annotate(s = row["district_eng"],
#                   xy = (x,y),
#                   horizontalalignment='left',
#                   verticalalignment = "center")

#Annotate pearson's r
    
pearson_r = st.pearsonr(districts_private_and_income.loc[:,"private_or_public"],
                        districts_private_and_income.loc[:,"yearly_average_household_income"])[0]

ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_2.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#   --- Ax_3 : Bar plot ---

#Get labels for x - axis ticks
labels = list(districts_private_and_income.sort_values(by = "private_or_public", ascending = False).loc[:,"district_eng"])

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1

#Get bar heights from data
bar_heights = districts_private_and_income.loc[:,"private_or_public"].sort_values(ascending = False).astype(int)

# --- Color Information ---

# For health data  when both graphs and maps are used.
sequential_cmap = cm.ScalarMappable(col.Normalize(0, max(bar_heights)), cm.YlGnBu)

# --- Plot Figure ---

ax_3.bar(bar_positions,bar_heights,
    width = 0.7,
    align = "center",
    color = sequential_cmap.to_rgba(bar_heights))

# --- Add color legend ---

#Import required toolkit
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

#Create an inset_axes instance with different parameters
axins1 = inset_axes(ax_3,
                    width="50%",  # width = 50% of parent_bbox width
                    height="5%",  # height : 5%
                    loc="upper right")

#Create a colormap 
cbar = plt.colorbar(sequential_cmap,
                    cax = axins1,
                    # ticks = [] Cna also set ticks like this
                    orientation = "horizontal",
                    shrink = 0.25,
                    anchor = (30,10))

cbar.set_label('Number of private healthcare institutions',
               size = 14,
               weight = "bold")


# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax_3.set_xticks(bar_positions)

#Setting x-tick labels and positions
ax_3.set_xticklabels(labels, rotation = 90)

# --- Spine and Grid ---

#Disable right and top spine
ax_3.spines['right'].set_visible(False)
ax_3.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_3.set_xlabel("District",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_3.set_ylabel("Number of private healthcare institutions",
              fontdict = font_axislabels,
              labelpad= 18)


# Add labels to the top of the bars
add_value_labels(ax_3) 

#Set xtick font info

ax_3.set_xticklabels(ax_3.get_xticklabels(),
                     font_xticks)

#Set figure title
fig.suptitle("In Istanbul, some districts have far more  \n private healthcare institutions than others" ,
             family = 'sans-serif',
             fontname = "Arial",
             color =  'black',
             weight = 'bold',
             size = 30,
             x = 0.60,
             y = 0.89) #Doesn't use fontdict for some reason

# --- Misc ---

#Make layout tighter
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

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

#Define a gridspect of 2 rows and 2 columns
gs = fig.add_gridspec(2, 2)

#The first ax will occupy all space of row 1
ax_1 = fig.add_subplot(gs[0,:])

#The second ax will occupy first place out of 2 in row 2
ax_2 = fig.add_subplot(gs[1,0])

#The third ax will occupy second place out of 2 in row 2
ax_3 = fig.add_subplot(gs[1,1])

# --- Plotting ---

#       --- Ax_1 : Map ---
istanbul_districts_merged.plot(ax = ax_1,
                    column = "private_count",
                    edgecolor = "black",
                    alpha = 1,
                    cmap = cm.YlGnBu)

ctx.add_basemap(ax_1, zoom = 11, #16
                crs='epsg:4326',
                source=ctx.providers.Esri.WorldGrayCanvas)

# --- Spine and Grid ---

ax_1.set_axis_off() # Turn off axis

# --- Map Labels ---

#Select districts that you want labels for
districts_to_label_list = ["Silivri", "Catalca", "Buyukcekmece", "Arnavutkoy", "Eyupsultan", "Sariyer",
                           "Beykoz", "Sile", "Cekmekoy", "Tuzla", "Pendik", "Maltepe", "Basaksehir"]

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

#   --- Ax_2 : Scatterplot ---

ax_2.scatter(x =  districts_private_and_income.loc[:,"yearly_average_household_income"],
             y =  districts_private_and_income.loc[:,"private_or_public"],
             s = 150, # To specify face width
             c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_2.spines['right'].set_visible(False)
ax_2.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_2.set_xlabel("Yıllık ortalama hanehalkı geliri (bin TL)",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_2.set_ylabel("Özel sağlık kuruluşu sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

#Label certain datapoints

# districts_to_label = ["Kadikoy","Besiktas", "Bakirkoy","Adalar",
#                       "Sisli", "Sariyer","Uskudar"]

# districts_to_label_mask = districts_private_and_income.loc[:,"district_eng"].isin(districts_to_label)

# districts_to_label_xy_df = districts_private_and_income.loc[districts_to_label_mask,["district_tr","private_or_public","yearly_average_household_income"]]

# for idx, row in districts_to_label_xy_df.iterrows():
#     x = row["private_or_public"] + 3 #To align it properly
#     y = row["yearly_average_household_income"]
#     ax_2.annotate(s = row["district_tr"],
#                   xy = (x,y),
#                   horizontalalignment='left',
#                   verticalalignment = "center")

#Annotate pearson's r
    
pearson_r = st.pearsonr(districts_private_and_income.loc[:,"private_or_public"],
                        districts_private_and_income.loc[:,"yearly_average_household_income"])[0]

ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_2.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#   --- Ax_3 : Bar plot ---

#Get labels for x - axis ticks
labels = list(districts_private_and_income.sort_values(by = "private_or_public", ascending = False).loc[:,"district_eng"])

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1

#Get bar heights from data
bar_heights = districts_private_and_income.loc[:,"private_or_public"].sort_values(ascending = False).astype(int)

# --- Color Information ---

# For health data  when both graphs and maps are used.
sequential_cmap = cm.ScalarMappable(col.Normalize(0, max(bar_heights)), cm.YlGnBu)

# --- Plot Figure ---

ax_3.bar(bar_positions,bar_heights,
    width = 0.7,
    align = "center",
    color = sequential_cmap.to_rgba(bar_heights))

# --- Add color legend ---

#Import required toolkit
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

#Create an inset_axes instance with different parameters
axins1 = inset_axes(ax_3,
                    width="50%",  # width = 50% of parent_bbox width
                    height="5%",  # height : 5%
                    loc="upper right")

#Create a colormap 
cbar = plt.colorbar(sequential_cmap,
                    cax = axins1,
                    # ticks = [] Cna also set ticks like this
                    orientation = "horizontal",
                    shrink = 0.25,
                    anchor = (30,10))

cbar.set_label('Özel sağlık kuruluşu sayısı',
               size = 14,
               weight = "bold")


# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax_3.set_xticks(bar_positions)

#Setting x-tick labels and positions
ax_3.set_xticklabels(labels, rotation = 90)

# --- Spine and Grid ---

#Disable right and top spine
ax_3.spines['right'].set_visible(False)
ax_3.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_3.set_xlabel("İlçe",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_3.set_ylabel("Özel sağlık kuruluşu sayısı",
              fontdict = font_axislabels,
              labelpad= 18)


# Add labels to the top of the bars
add_value_labels(ax_3) 

#Set xtick font info

ax_3.set_xticklabels(ax_3.get_xticklabels(),
                     font_xticks)

#Set figure title
fig.suptitle("İstanbul'da bazı ilçelerde diğerlerinden daha çok sayıda \n özel sağlık kuruluşu var." ,
             family = 'sans-serif',
             fontname = "Arial",
             color =  'black',
             weight = 'bold',
             size = 30,
             x = 0.60,
             y = 0.89) #Doesn't use fontdict for some reason

# --- Misc ---

#Make layout tighter
plt.tight_layout() 


# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")


# ================ VERSION ONE ======================
# #%% ================ VERSION TWO ======================
# #%% #%% --- Visualization - English ---

# # --- Figure Preparation ---

# #Create a figure
# fig = plt.figure(figsize = (19.20,19.20),
#                   constrained_layout=True) #Constrained layout to use with gridspec

# #Define a gridspect of 2 rows and 2 columns
# gs = fig.add_gridspec(2, 4)

# #The first ax will occupy all space of row 1
# ax_1 = fig.add_subplot(gs[0,:])

# #The second ax will occupy first place out of 2 in row 2
# ax_2 = fig.add_subplot(gs[1,0])

# #The third ax will occupy second place out of 2 in row 2
# ax_3 = fig.add_subplot(gs[1,1])

# ax_4 = fig.add_subplot(gs[1,2:])

# # --- Plotting ---

# #       --- Ax_1 : Map ---
# istanbul_districts_merged.plot(ax = ax_1,
#                     column = "private_count",
#                     edgecolor = "black",
#                     alpha = 1,
#                     cmap = cm.YlGnBu)

# ctx.add_basemap(ax_1, zoom = 11, #16
#                 crs='epsg:4326',
#                 source=ctx.providers.Esri.WorldGrayCanvas)

# # --- Spine and Grid ---

# ax_1.set_axis_off() # Turn off axis

# # --- Map Labels ---

# #Select districts that you want labels for
# districts_to_label_list = ["Silivri", "Catalca", "Buyukcekmece", "Arnavutkoy", "Eyupsultan", "Sariyer",
#                             "Beykoz", "Sile", "Cekmekoy", "Tuzla", "Pendik", "Maltepe", "Basaksehir"]

# #Create a boolean indexing mask checking for those districts
# labels_mask = istanbul_districts.loc[:,"district_e"].isin(districts_to_label_list)

# #Pass in the boolean mask to create a dataframe
# districts_to_label = istanbul_districts.loc[labels_mask,["district_e", "geometry"]]

# #Create a representative point within each district polygon to place the label
# districts_to_label["representative_point"] = districts_to_label.geometry.representative_point().geometry.values

# #Pass over each row label the repsentative point according to that row's name
# for idx, row in districts_to_label.iterrows():
#     ax_1.annotate(s=row["district_e"], xy=(row["representative_point"].x,row["representative_point"].y),
#                   horizontalalignment='center')

# #   --- Ax_2 : Scatterplot 1 ---

# ax_2.scatter(x = districts_private_and_income.loc[:,"private_or_public"],
#               y = districts_private_and_income.loc[:,"yearly_average_household_income"],
#               s = 150, # To specify face width
#               c = categorical_color)


# # --- Set x and y axis ticks ---


# # --- Spine and Grid ---

# #Disable right and top spine
# ax_2.spines['right'].set_visible(False)
# ax_2.spines['top'].set_visible(False)

# # --- Text ---

# #Add x axis label
# ax_2.set_xlabel("Number of private health institutions",
#               fontdict = font_axislabels,
#               labelpad= 18)

# ax_2.xaxis.set_label_coords(2, -0.1)

# # Add y axis label
# ax_2.set_ylabel("Average yearly household income (thousand TL)",
#               fontdict = font_axislabels,
#               labelpad= 18)


# #Annotate pearson's r
    
# pearson_r = st.pearsonr(districts_private_and_income.loc[:,"private_or_public"],
#                         districts_private_and_income.loc[:,"yearly_average_household_income"])[0]

# ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
#               xy = (.9, .9),
#               xycoords=ax_2.transAxes,
#               color = "black",
#               weight = "bold",
#               fontsize = 15)


# #   --- Ax_3 : Scatterplot 2 ---

# ax_3.scatter(x = districts_private_and_income.loc[:,"private_or_public"],
#               y = districts_private_and_income.loc[:,"population"],
#               s = 150, # To specify face width
#               c = categorical_color)


# # --- Set x and y axis ticks ---


# # --- Spine and Grid ---

# #Disable right and top spine
# ax_3.spines['right'].set_visible(False)
# ax_3.spines['top'].set_visible(False)

# # --- Text ---

# #Add x axis label

# # Add y axis label
# ax_3.set_ylabel("Population",
#               fontdict = font_axislabels,
#               labelpad= 2)

# #Annotate pearson's r
    
# pearson_r = st.pearsonr(districts_private_and_income.loc[:,"private_or_public"],
#                         districts_private_and_income.loc[:,"population"])[0]

# ax_3.annotate(s = "r = {:.2f}".format(pearson_r),
#               xy = (.9, .9),
#               xycoords=ax_3.transAxes,
#               color = "black",
#               weight = "bold",
#               fontsize = 15)

# #   --- Ax_4 : Bar plot ---

# #Get labels for x - axis ticks
# labels = list(districts_private_and_income.sort_values(by = "private_or_public", ascending = False).loc[:,"district_eng"])

# #Generate bar positions
# from numpy import arange
# bar_positions = arange(len(labels)) + 1

# #Get bar heights from data
# bar_heights = districts_private_and_income.loc[:,"private_or_public"].sort_values(ascending = False).astype(int)

# # --- Color Information ---

# # For health data  when both graphs and maps are used.
# sequential_cmap = cm.ScalarMappable(col.Normalize(0, max(bar_heights)), cm.YlGnBu)

# # --- Plot Figure ---

# ax_4.bar(bar_positions,bar_heights,
#     width = 0.7,
#     align = "center",
#     color = sequential_cmap.to_rgba(bar_heights))

# # --- Add color legend ---

# #Import required toolkit
# from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# #Create an inset_axes instance with different parameters
# axins1 = inset_axes(ax_4,
#                     width="50%",  # width = 50% of parent_bbox width
#                     height="5%",  # height : 5%
#                     loc="upper right")

# #Create a colormap 
# cbar = plt.colorbar(sequential_cmap,
#                     cax = axins1,
#                     # ticks = [] Cna also set ticks like this
#                     orientation = "horizontal",
#                     shrink = 0.25,
#                     anchor = (30,10))

# cbar.set_label('Number of private healthcare institutions',
#                 size = 14,
#                 weight = "bold")


# # --- Set x and y axis ticks ---

# #Setting where x-ticks should be at
# ax_4.set_xticks(bar_positions)

# #Setting x-tick labels and positions
# ax_4.set_xticklabels(labels, rotation = 90)

# # --- Spine and Grid ---

# #Disable right and top spine
# ax_4.spines['right'].set_visible(False)
# ax_4.spines['top'].set_visible(False)

# # --- Text ---

# #Add x axis label
# ax_4.set_xlabel("District",
#               fontdict = font_axislabels,
#               labelpad= 18)

# # Add y axis label
# ax_4.set_ylabel("Number of private healthcare institutions",
#               fontdict = font_axislabels,
#               labelpad= 18)


# # Add labels to the top of the bars
# add_value_labels(ax_4) 

# #Set xtick font info

# ax_4.set_xticklabels(ax_4.get_xticklabels(),
#                       font_xticks)

# #Set figure title
# fig.suptitle("In Istanbul, some districts have far more  \n private healthcare institutions than others" ,
#               family = 'sans-serif',
#               fontname = "Arial",
#               color =  'black',
#               weight = 'bold',
#               size = 30,
#               x = 0.60,
#               y = 0.95) #Doesn't use fontdict for some reason

# # --- Misc ---

# #Make layout tighter
# plt.tight_layout() 

# # --- Export Visualization ---

# #As SVG
# export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng_2.svg")
# plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

# #As png
# export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng_2.png")
# plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")

# #%% #%% --- Visualization - Turkish ---

# # --- Figure Preparation ---

# #Create a figure
# fig = plt.figure(figsize = (19.20,19.20),
#                   constrained_layout=True) #Constrained layout to use with gridspec

# #Define a gridspect of 2 rows and 2 columns
# gs = fig.add_gridspec(2, 4)

# #The first ax will occupy all space of row 1
# ax_1 = fig.add_subplot(gs[0,:])

# #The second ax will occupy first place out of 2 in row 2
# ax_2 = fig.add_subplot(gs[1,0])

# #The third ax will occupy second place out of 2 in row 2
# ax_3 = fig.add_subplot(gs[1,1])

# ax_4 = fig.add_subplot(gs[1,2:])

# # --- Plotting ---

# #       --- Ax_1 : Map ---
# istanbul_districts_merged.plot(ax = ax_1,
#                     column = "private_count",
#                     edgecolor = "black",
#                     alpha = 1,
#                     cmap = cm.YlGnBu)

# ctx.add_basemap(ax_1, zoom = 11, #16
#                 crs='epsg:4326',
#                 source=ctx.providers.Esri.WorldGrayCanvas)

# # --- Spine and Grid ---

# ax_1.set_axis_off() # Turn off axis

# # --- Map Labels ---

# #Select districts that you want labels for
# districts_to_label_list = ["Silivri", "Catalca", "Buyukcekmece", "Arnavutkoy", "Eyupsultan", "Sariyer",
#                             "Beykoz", "Sile", "Cekmekoy", "Tuzla", "Pendik", "Maltepe", "Basaksehir"]

# #Create a boolean indexing mask checking for those districts
# labels_mask = istanbul_districts.loc[:,"district_e"].isin(districts_to_label_list)

# #Pass in the boolean mask to create a dataframe
# districts_to_label = istanbul_districts.loc[labels_mask,["district_t", "geometry"]]

# #Create a representative point within each district polygon to place the label
# districts_to_label["representative_point"] = districts_to_label.geometry.representative_point().geometry.values

# #Pass over each row label the repsentative point according to that row's name
# for idx, row in districts_to_label.iterrows():
#     ax_1.annotate(s=row["district_t"], xy=(row["representative_point"].x,row["representative_point"].y),
#                   horizontalalignment='center')

# #   --- Ax_2 : Scatterplot 1 ---

# ax_2.scatter(x = districts_private_and_income.loc[:,"private_or_public"],
#               y = districts_private_and_income.loc[:,"yearly_average_household_income"],
#               s = 150, # To specify face width
#               c = categorical_color)


# # --- Set x and y axis ticks ---


# # --- Spine and Grid ---

# #Disable right and top spine
# ax_2.spines['right'].set_visible(False)
# ax_2.spines['top'].set_visible(False)

# # --- Text ---

# #Add x axis label
# ax_2.set_xlabel("Özel sağlık kuruluşu sayısı",
#               fontdict = font_axislabels,
#               labelpad= 18)

# ax_2.xaxis.set_label_coords(2, -0.1)

# # Add y axis label
# ax_2.set_ylabel("Yıllık ortalama hanehalkı geliri (bin TL)",
#               fontdict = font_axislabels,
#               labelpad= 18)


# #Annotate pearson's r
    
# pearson_r = st.pearsonr(districts_private_and_income.loc[:,"private_or_public"],
#                         districts_private_and_income.loc[:,"yearly_average_household_income"])[0]

# ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
#               xy = (.9, .9),
#               xycoords=ax_2.transAxes,
#               color = "black",
#               weight = "bold",
#               fontsize = 15)


# #   --- Ax_3 : Scatterplot 2 ---

# ax_3.scatter(x = districts_private_and_income.loc[:,"private_or_public"],
#               y = districts_private_and_income.loc[:,"population"],
#               s = 150, # To specify face width
#               c = categorical_color)


# # --- Set x and y axis ticks ---


# # --- Spine and Grid ---

# #Disable right and top spine
# ax_3.spines['right'].set_visible(False)
# ax_3.spines['top'].set_visible(False)

# # --- Text ---

# #Add x axis label

# # Add y axis label
# ax_3.set_ylabel("Nüfus",
#               fontdict = font_axislabels,
#               labelpad= 2)

# #Annotate pearson's r
    
# pearson_r = st.pearsonr(districts_private_and_income.loc[:,"private_or_public"],
#                         districts_private_and_income.loc[:,"population"])[0]

# ax_3.annotate(s = "r = {:.2f}".format(pearson_r),
#               xy = (.9, .9),
#               xycoords=ax_3.transAxes,
#               color = "black",
#               weight = "bold",
#               fontsize = 15)

# #   --- Ax_4 : Bar plot ---

# #Get labels for x - axis ticks
# labels = list(districts_private_and_income.sort_values(by = "private_or_public", ascending = False).loc[:,"district_eng"])

# #Generate bar positions
# from numpy import arange
# bar_positions = arange(len(labels)) + 1

# #Get bar heights from data
# bar_heights = districts_private_and_income.loc[:,"private_or_public"].sort_values(ascending = False).astype(int)

# # --- Color Information ---

# # For health data  when both graphs and maps are used.
# sequential_cmap = cm.ScalarMappable(col.Normalize(0, max(bar_heights)), cm.YlGnBu)

# # --- Plot Figure ---

# ax_4.bar(bar_positions,bar_heights,
#     width = 0.7,
#     align = "center",
#     color = sequential_cmap.to_rgba(bar_heights))

# # --- Add color legend ---

# #Import required toolkit
# from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# #Create an inset_axes instance with different parameters
# axins1 = inset_axes(ax_4,
#                     width="50%",  # width = 50% of parent_bbox width
#                     height="5%",  # height : 5%
#                     loc="upper right")

# #Create a colormap 
# cbar = plt.colorbar(sequential_cmap,
#                     cax = axins1,
#                     # ticks = [] Cna also set ticks like this
#                     orientation = "horizontal",
#                     shrink = 0.25,
#                     anchor = (30,10))

# cbar.set_label('Özel sağlık kuruluşu sayısı',
#                 size = 14,
#                 weight = "bold")


# # --- Set x and y axis ticks ---

# #Setting where x-ticks should be at
# ax_4.set_xticks(bar_positions)

# #Setting x-tick labels and positions
# ax_4.set_xticklabels(labels, rotation = 90)

# # --- Spine and Grid ---

# #Disable right and top spine
# ax_4.spines['right'].set_visible(False)
# ax_4.spines['top'].set_visible(False)

# # --- Text ---

# #Add x axis label
# ax_4.set_xlabel("İlçe",
#               fontdict = font_axislabels,
#               labelpad= 18)

# # Add y axis label
# ax_4.set_ylabel("Özel sağlık kuruluşu sayısı",
#               fontdict = font_axislabels,
#               labelpad= 18)


# # Add labels to the top of the bars
# add_value_labels(ax_4) 

# #Set xtick font info

# ax_4.set_xticklabels(ax_4.get_xticklabels(),
#                       font_xticks)

# #Set figure title
# fig.suptitle("İstanbul'da bazı ilçelerde diğerlerinden daha çok sayıda \n özel sağlık kuruluşu var." ,
#               family = 'sans-serif',
#               fontname = "Arial",
#               color =  'black',
#               weight = 'bold',
#               size = 30,
#               x = 0.60,
#               y = 0.95) #Doesn't use fontdict for some reason

# # --- Misc ---

# #Make layout tighter
# plt.tight_layout() 

# # --- Export Visualization ---

# #As SVG
# export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr_2.svg")
# plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

# #As png
# export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr_2.png")
# plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")

# # ==================== VERSION TWO ==============
















