# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 16:22:19 2020

@author: ejgen

------ What's this file? ------
                
This script contains some helper functions and definitions that i can
use across my actual analysis and visualization scripts.

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

#Istanbul districts extra data
districts_extra_fp = "../../../Data/Non-GIS Data/external/district_income.xlsx"
districts_extra = pd.read_excel(districts_extra_fp)

#%% --- Data Preparation ---
# =======================================================================
# --- IMPORTANT!: The below code is not my proudest piece of code.
# I know that it contains many redundancies and it is not he cleanest code.
# However, i wrote this in a time where i was quite stressed so please do
# excuse me. I will return to re-factor it when i have time
# =======================================================================

#Create a list of institutions that you want to include in your analysis
institutions = ["Hospital", "Dental Health Center", "Dialysis Center",
                     "Physical Therapy Center", "Gynecology and Obstetrics Clinic"]

#Create a mask based on that list
institutions_mask = health.loc[:,"institution_type_eng"].isin(institutions)

#Select health institutions that are only in the boolean mask
selected = health.loc[institutions_mask, ["district_tr", "district_eng",
                                          "institution_type", "institution_type_eng",
                                          "private_or_public"]]

#Create a list of districts
#This will exclude districts that do not have any of the health institutions
#i have listed above.
districts = selected.loc[:,"district_eng"].value_counts().index.tolist()

#Groupby per district
selected_groupby_dist = selected.groupby("district_eng")

#For district in list of districts
for district in districts:

    #Make current group district
    current_district = selected_groupby_dist.get_group(str(district))
    
    current_district_grouped = current_district.groupby("institution_type_eng")
    
    #Create a mask for the current district
    current_district_mask = districts_extra.loc[:,"district_eng"] == str(district)

    #For inst in list of institutions
    for inst in institutions:
        #Make current institution institution
        try:
            current_institution = current_district_grouped.get_group(str(inst))
        except:
            pass

        #Value counts to get private and state info

        info = current_institution.loc[:,"private_or_public"].value_counts()
            
        info_indexes = info.index.tolist()
        
        info_data = []
        
        if "Private" in info_indexes:
            info_data.append(info["Private"])
        if "Private" not in info_indexes:
            info_data.append(int(0))
        if "Public" in info_indexes:
            info_data.append(info["Public"])
        else:
            info_data.append(int(0))
        
        #Pass mask to districts extra and assign values
        districts_extra.loc[current_district_mask,str(inst) + "_private"] = info_data[0]
        districts_extra.loc[current_district_mask,str(inst) + "_public"] = info_data[1]

#Fill nan values with a tuple of 0,0
districts_extra.fillna(0, inplace = True)

#For each institution in institutions 
for institution in institutions:
    
    #Recreate districts_extra dataframe keys
    institution_priv_str = institution + "_private"
    institution_pub_str = institution + "_public"
    
    #Zip dataframe values as a tuple
    list_zip = list(zip(districts_extra.loc[:,institution_priv_str], districts_extra.loc[:,institution_pub_str]))
    
    #Assign the tuple to the corresponding column
    districts_extra[str(institution + "_privpub_count")] = list_zip
    
    #Drop the original two columns and leave only the tuple columns
    districts_extra.drop(columns = [institution_priv_str, institution_pub_str],
                         axis = 1,
                         inplace = True)
    
#Finally, fill nan values with a tuple of 0,0


#%%FIGURE -- HOSPITAL
selected_inst = "Hospital"
selected_inst_label = selected_inst + "_privpub_count"
#%% --- Visualization - English ---

# --- Figure Preparation ---

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

#Define a gridspect of 2 rows and 2 columns
gs = fig.add_gridspec(2, 2)

#The first ax will occupy all half of row 1
ax_1 = fig.add_subplot(gs[0,:])

#The second ax will occupy the second half of row 1
ax_2 = fig.add_subplot(gs[1,0])

#The third ax will occupy first place out of 4 in row 2
ax_3 = fig.add_subplot(gs[1,1])

# --- Plot Figure: Hospital---

#       --- Ax 1: Bar plot ---

#Sort DF
sorted_df = districts_extra.sort_values(by = selected_inst_label, ascending = False)

#Get labels for x - axis ticks
labels = list(sorted_df.loc[:,"district_tr"].values)

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1
bar_positions_2 = [x + 0.20 for x in bar_positions]

#Get bar heights from data
bar_heights_priv = [int(x[0]) for x in sorted_df.loc[:,selected_inst_label]]
bar_heights_pub = [int(x[1]) for x in sorted_df.loc[:,selected_inst_label]]

# --- Plot Figure ---

ax_1.bar(bar_positions,bar_heights_priv,
    width = 0.40,
    align = "center",
    color = categorical_color)

ax_1.bar(bar_positions_2,bar_heights_pub,
    width = 0.30,
    align = "center",
    color = categorical_color_2)

# --- Add Legend ---

ax_1.legend(["Private Hosp.", "Public Hosp."],loc=1,prop={'size': 30})

# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax_1.set_xticks([x + 0.20 / 2 for x in bar_positions])

#Setting x-tick labels and positions
ax_1.set_xticklabels(labels, rotation = 90)

start, end = ax_1.get_ylim()
ax_1.yaxis.set_ticks(np.arange(start,end, 1))

# --- Spine and Grid ---

#Disable right and top spine
ax_1.spines['right'].set_visible(False)
ax_1.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_1.set_xlabel("District",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_1.set_ylabel("Number of hospitals",
              fontdict = font_axislabels,
              labelpad= 18)

#Set xtick font info

ax_1.set_xticklabels(ax_1.get_xticklabels(),
                      font_xticks)

#       --- Ax 2: Scatterplot ---

ax_2.scatter(x = sorted_df.loc[:,"yearly_average_household_income"], # Remember that i took that info before?
             y = bar_heights_priv,
             s = 150, # To specify face width
             c = categorical_color)

# --- Spine and Grid ---

#Disable right and top spine
ax_2.spines['right'].set_visible(False)
ax_2.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_2.set_ylabel("Number of private hospitals",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_2.set_xlabel("Average yearly household income (thousand TL)",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"yearly_average_household_income"],
                        bar_heights_priv)[0]
ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_2.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#       --- Ax 3: Scatterplot ---

ax_3.scatter(x = sorted_df.loc[:,"population"], # Remember that i took that info before?
              y = bar_heights_priv,
              s = 150, # To specify face width
              c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_3.spines['right'].set_visible(False)
ax_3.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_3.set_ylabel("Number of private hospitals",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_3.set_xlabel("Population",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"population"],
                        bar_heights_priv)[0]

ax_3.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_3.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

fig.suptitle("Distribution of private and public hospitals \n across districts." ,
             family = 'sans-serif',
             fontname = "Arial",
             color =  'black',
             weight = 'bold',
             size = 30,
             x = 0.50,
             y = 0.98) #Doesn't use fontdict for some reason

# # --- Misc ---
#Make layout tighter
plt.tight_layout() 

# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng_1.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng_1.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")

#%% --- Visualization - Turkish ---

# --- Figure Preparation ---

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

#Define a gridspect of 2 rows and 2 columns
gs = fig.add_gridspec(2, 2)

#The first ax will occupy all half of row 1
ax_1 = fig.add_subplot(gs[0,:])

#The second ax will occupy the second half of row 1
ax_2 = fig.add_subplot(gs[1,0])

#The third ax will occupy first place out of 4 in row 2
ax_3 = fig.add_subplot(gs[1,1])

# --- Plot Figure: Hospital---

#       --- Ax 1: Bar plot ---

#Sort DF
sorted_df = districts_extra.sort_values(by = selected_inst_label, ascending = False)

#Get labels for x - axis ticks
labels = list(sorted_df.loc[:,"district_tr"].values)

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1
bar_positions_2 = [x + 0.20 for x in bar_positions]

#Get bar heights from data
bar_heights_priv = [int(x[0]) for x in sorted_df.loc[:,selected_inst_label]]
bar_heights_pub = [int(x[1]) for x in sorted_df.loc[:,selected_inst_label]]

# --- Plot Figure ---

ax_1.bar(bar_positions,bar_heights_priv,
    width = 0.40,
    align = "center",
    color = categorical_color)

ax_1.bar(bar_positions_2,bar_heights_pub,
    width = 0.30,
    align = "center",
    color = categorical_color_2)

# --- Add Legend ---

ax_1.legend(["Özel H.", "Devlet H."],loc=1,prop={'size': 30})

# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax_1.set_xticks([x + 0.20 / 2 for x in bar_positions])

#Setting x-tick labels and positions
ax_1.set_xticklabels(labels, rotation = 90)

start, end = ax_1.get_ylim()
ax_1.yaxis.set_ticks(np.arange(start,end, 1))

# --- Spine and Grid ---

#Disable right and top spine
ax_1.spines['right'].set_visible(False)
ax_1.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_1.set_xlabel("İlçe",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_1.set_ylabel("Hastane sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

#Set xtick font info

ax_1.set_xticklabels(ax_1.get_xticklabels(),
                      font_xticks)

#       --- Ax 2: Scatterplot ---

ax_2.scatter(x = sorted_df.loc[:,"yearly_average_household_income"], # Remember that i took that info before?
             y = bar_heights_priv,
             s = 150, # To specify face width
             c = categorical_color)

# --- Spine and Grid ---

#Disable right and top spine
ax_2.spines['right'].set_visible(False)
ax_2.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_2.set_ylabel("Özel Hastane sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_2.set_xlabel("Yıllık ortalama hanehalkı geliri (bin TL)",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"yearly_average_household_income"],
                        bar_heights_priv)[0]

ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_2.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#       --- Ax 3: Scatterplot ---

ax_3.scatter(x = sorted_df.loc[:,"population"], # Remember that i took that info before?
              y = bar_heights_priv,
              s = 150, # To specify face width
              c = categorical_color)

# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_3.spines['right'].set_visible(False)
ax_3.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_3.set_ylabel("Özel hastane sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_3.set_xlabel("Nüfus",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"population"],
                        bar_heights_priv)[0]

ax_3.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_3.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#Set figure title
fig.suptitle("Özel hastane ve devlet hastanelerinin \n ilçelere göre dağılımı" ,
             family = 'sans-serif',
             fontname = "Arial",
             color =  'black',
             weight = 'bold',
             size = 30,
             x = 0.50,
             y = 0.98) #Doesn't use fontdict for some reason

# # --- Misc ---
#Make layout tighter
plt.tight_layout() 

# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr_1.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr_1.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")

#%%FIGURE -- DENTAL HEALTH CENTER
selected_inst = "Dental Health Center"
selected_inst_label = selected_inst + "_privpub_count"
#%% --- Visualization - English ---

# --- Figure Preparation ---

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

#Define a gridspect of 2 rows and 2 columns
gs = fig.add_gridspec(2, 2)

#The first ax will occupy all half of row 1
ax_1 = fig.add_subplot(gs[0,:])

#The second ax will occupy the second half of row 1
ax_2 = fig.add_subplot(gs[1,0])

#The third ax will occupy first place out of 4 in row 2
ax_3 = fig.add_subplot(gs[1,1])

# --- Plot Figure: Hospital---

#       --- Ax 1: Bar plot ---

#Sort DF
sorted_df = districts_extra.sort_values(by = selected_inst_label, ascending = False)

#Get labels for x - axis ticks
labels = list(sorted_df.loc[:,"district_tr"].values)

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1
bar_positions_2 = [x + 0.20 for x in bar_positions]

#Get bar heights from data
bar_heights_priv = [int(x[0]) for x in sorted_df.loc[:,selected_inst_label]]
bar_heights_pub = [int(x[1]) for x in sorted_df.loc[:,selected_inst_label]]

# --- Plot Figure ---

ax_1.bar(bar_positions,bar_heights_priv,
    width = 0.40,
    align = "center",
    color = categorical_color)

ax_1.bar(bar_positions_2,bar_heights_pub,
    width = 0.30,
    align = "center",
    color = categorical_color_2)

# --- Add Legend ---

ax_1.legend(["Private", "Public"],loc=1,prop={'size': 30})

# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax_1.set_xticks([x + 0.20 / 2 for x in bar_positions])

#Setting x-tick labels and positions
ax_1.set_xticklabels(labels, rotation = 90)

start, end = ax_1.get_ylim()
ax_1.yaxis.set_ticks(np.arange(start,end, 5))

# --- Spine and Grid ---

#Disable right and top spine
ax_1.spines['right'].set_visible(False)
ax_1.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_1.set_xlabel("District",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_1.set_ylabel("Number of dental health centers",
              fontdict = font_axislabels,
              labelpad= 18)

#Set xtick font info

ax_1.set_xticklabels(ax_1.get_xticklabels(),
                      font_xticks)

#       --- Ax 2: Scatterplot ---

ax_2.scatter(x = sorted_df.loc[:,"yearly_average_household_income"], # Remember that i took that info before?
             y = bar_heights_priv,
             s = 150, # To specify face width
             c = categorical_color)

# --- Spine and Grid ---

#Disable right and top spine
ax_2.spines['right'].set_visible(False)
ax_2.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_2.set_ylabel("Number of dental health c.",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_2.set_xlabel("Average yearly household income (thousand TL)",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"yearly_average_household_income"],
                        bar_heights_priv)[0]

ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_2.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#       --- Ax 3: Scatterplot ---

ax_3.scatter(x = sorted_df.loc[:,"population"], # Remember that i took that info before?
              y = bar_heights_priv,
              s = 150, # To specify face width
              c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_3.spines['right'].set_visible(False)
ax_3.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_3.set_ylabel("Number of dental health c.",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_3.set_xlabel("Population",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"population"],
                        bar_heights_priv)[0]

ax_3.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_3.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

fig.suptitle("Distribution of private and public dental health centers \n across districts." ,
             family = 'sans-serif',
             fontname = "Arial",
             color =  'black',
             weight = 'bold',
             size = 30,
             x = 0.50,
             y = 0.98) #Doesn't use fontdict for some reason

# # --- Misc ---
#Make layout tighter
plt.tight_layout() 

# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng_2.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng_2.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")

#%% --- Visualization - Turkish ---

# --- Figure Preparation ---

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

#Define a gridspect of 2 rows and 2 columns
gs = fig.add_gridspec(2, 2)

#The first ax will occupy all half of row 1
ax_1 = fig.add_subplot(gs[0,:])

#The second ax will occupy the second half of row 1
ax_2 = fig.add_subplot(gs[1,0])

#The third ax will occupy first place out of 4 in row 2
ax_3 = fig.add_subplot(gs[1,1])

# --- Plot Figure: Hospital---

#       --- Ax 1: Bar plot ---

#Sort DF
sorted_df = districts_extra.sort_values(by = selected_inst_label, ascending = False)

#Get labels for x - axis ticks
labels = list(sorted_df.loc[:,"district_tr"].values)

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1
bar_positions_2 = [x + 0.20 for x in bar_positions]

#Get bar heights from data
bar_heights_priv = [int(x[0]) for x in sorted_df.loc[:,selected_inst_label]]
bar_heights_pub = [int(x[1]) for x in sorted_df.loc[:,selected_inst_label]]

# --- Plot Figure ---

ax_1.bar(bar_positions,bar_heights_priv,
    width = 0.40,
    align = "center",
    color = categorical_color)

ax_1.bar(bar_positions_2,bar_heights_pub,
    width = 0.30,
    align = "center",
    color = categorical_color_2)

# --- Add Legend ---

ax_1.legend(["Özel", "Devlet"],loc=1,prop={'size': 30})

# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax_1.set_xticks([x + 0.20 / 2 for x in bar_positions])

#Setting x-tick labels and positions
ax_1.set_xticklabels(labels, rotation = 90)

start, end = ax_1.get_ylim()
ax_1.yaxis.set_ticks(np.arange(start,end, 5))

# --- Spine and Grid ---

#Disable right and top spine
ax_1.spines['right'].set_visible(False)
ax_1.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_1.set_xlabel("İlçe",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_1.set_ylabel("Ağız ve diş sağlığı m. sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

#Set xtick font info

ax_1.set_xticklabels(ax_1.get_xticklabels(),
                      font_xticks)

#       --- Ax 2: Scatterplot ---

ax_2.scatter(x = sorted_df.loc[:,"yearly_average_household_income"], # Remember that i took that info before?
             y = bar_heights_priv,
             s = 150, # To specify face width
             c = categorical_color)

# --- Spine and Grid ---

#Disable right and top spine
ax_2.spines['right'].set_visible(False)
ax_2.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_2.set_ylabel("Özel ağız ve diş sağlığı m. sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_2.set_xlabel("Yıllık ortalama hanehalkı geliri (bin TL)",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"yearly_average_household_income"],
                        bar_heights_priv)[0]

ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_2.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#       --- Ax 3: Scatterplot ---

ax_3.scatter(x = sorted_df.loc[:,"population"], # Remember that i took that info before?
              y = bar_heights_priv,
              s = 150, # To specify face width
              c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_3.spines['right'].set_visible(False)
ax_3.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_3.set_ylabel("Özel ağız ve diş sağlığı m. sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_3.set_xlabel("Nüfus",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"population"],
                        bar_heights_priv)[0]

ax_3.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_3.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#Set figure title
fig.suptitle("Ağız ve diş sağlığı merkezlerinin \n ilçelere göre dağılımı" ,
             family = 'sans-serif',
             fontname = "Arial",
             color =  'black',
             weight = 'bold',
             size = 30,
             x = 0.50,
             y = 0.98) #Doesn't use fontdict for some reason

# # --- Misc ---
#Make layout tighter
plt.tight_layout() 

# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr_2.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr_2.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")

#%%FIGURE -- DIALYSIS CENTER
selected_inst = "Dialysis Center"
selected_inst_label = selected_inst + "_privpub_count"
#%% --- Visualization - English ---

# --- Figure Preparation ---

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

#Define a gridspect of 2 rows and 2 columns
gs = fig.add_gridspec(2, 2)

#The first ax will occupy all half of row 1
ax_1 = fig.add_subplot(gs[0,:])

#The second ax will occupy the second half of row 1
ax_2 = fig.add_subplot(gs[1,0])

#The third ax will occupy first place out of 4 in row 2
ax_3 = fig.add_subplot(gs[1,1])

# --- Plot Figure: Hospital---

#       --- Ax 1: Bar plot ---

#Sort DF
sorted_df = districts_extra.sort_values(by = selected_inst_label, ascending = False)

#Get labels for x - axis ticks
labels = list(sorted_df.loc[:,"district_tr"].values)

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1
bar_positions_2 = [x + 0.20 for x in bar_positions]

#Get bar heights from data
bar_heights_priv = [int(x[0]) for x in sorted_df.loc[:,selected_inst_label]]
bar_heights_pub = [int(x[1]) for x in sorted_df.loc[:,selected_inst_label]]

# --- Plot Figure ---

ax_1.bar(bar_positions,bar_heights_priv,
    width = 0.40,
    align = "center",
    color = categorical_color)

ax_1.bar(bar_positions_2,bar_heights_pub,
    width = 0.30,
    align = "center",
    color = categorical_color_2)

# --- Add Legend ---

ax_1.legend(["Private", "Public"],loc=1,prop={'size': 30})

# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax_1.set_xticks([x + 0.20 / 2 for x in bar_positions])

#Setting x-tick labels and positions
ax_1.set_xticklabels(labels, rotation = 90)

start, end = ax_1.get_ylim()
ax_1.yaxis.set_ticks(np.arange(start,end, 1))

# --- Spine and Grid ---

#Disable right and top spine
ax_1.spines['right'].set_visible(False)
ax_1.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_1.set_xlabel("District",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_1.set_ylabel("Number of dialysis c.",
              fontdict = font_axislabels,
              labelpad= 18)

#Set xtick font info

ax_1.set_xticklabels(ax_1.get_xticklabels(),
                      font_xticks)

#       --- Ax 2: Scatterplot ---

ax_2.scatter(x = sorted_df.loc[:,"yearly_average_household_income"], # Remember that i took that info before?
             y = bar_heights_priv,
             s = 150, # To specify face width
             c = categorical_color)

# --- Spine and Grid ---

#Disable right and top spine
ax_2.spines['right'].set_visible(False)
ax_2.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_2.set_ylabel("Number of dialysis c.",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_2.set_xlabel("Average yearly household income (thousand TL)",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"yearly_average_household_income"],
                        bar_heights_priv)[0]

ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_2.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#       --- Ax 3: Scatterplot ---

ax_3.scatter(x = sorted_df.loc[:,"population"], # Remember that i took that info before?
              y = bar_heights_priv,
              s = 150, # To specify face width
              c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_3.spines['right'].set_visible(False)
ax_3.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_3.set_ylabel("Number of dialysis c.",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_3.set_xlabel("Population",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"population"],
                        bar_heights_priv)[0]

ax_3.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_3.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

fig.suptitle("Distribution of private and public dialysis centers \n across districts." ,
             family = 'sans-serif',
             fontname = "Arial",
             color =  'black',
             weight = 'bold',
             size = 30,
             x = 0.50,
             y = 0.98) #Doesn't use fontdict for some reason

# # --- Misc ---
#Make layout tighter
plt.tight_layout() 

# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng_3.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng_3.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")

#%% --- Visualization - Turkish ---

# --- Figure Preparation ---

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

#Define a gridspect of 2 rows and 2 columns
gs = fig.add_gridspec(2, 2)

#The first ax will occupy all half of row 1
ax_1 = fig.add_subplot(gs[0,:])

#The second ax will occupy the second half of row 1
ax_2 = fig.add_subplot(gs[1,0])

#The third ax will occupy first place out of 4 in row 2
ax_3 = fig.add_subplot(gs[1,1])

# --- Plot Figure: Hospital---

#       --- Ax 1: Bar plot ---

#Sort DF
sorted_df = districts_extra.sort_values(by = selected_inst_label, ascending = False)

#Get labels for x - axis ticks
labels = list(sorted_df.loc[:,"district_tr"].values)

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1
bar_positions_2 = [x + 0.20 for x in bar_positions]

#Get bar heights from data
bar_heights_priv = [int(x[0]) for x in sorted_df.loc[:,selected_inst_label]]
bar_heights_pub = [int(x[1]) for x in sorted_df.loc[:,selected_inst_label]]

# --- Plot Figure ---

ax_1.bar(bar_positions,bar_heights_priv,
    width = 0.40,
    align = "center",
    color = categorical_color)

ax_1.bar(bar_positions_2,bar_heights_pub,
    width = 0.30,
    align = "center",
    color = categorical_color_2)

# --- Add Legend ---

ax_1.legend(["Özel.", "Devlet"],loc=1,prop={'size': 30})

# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax_1.set_xticks([x + 0.20 / 2 for x in bar_positions])

#Setting x-tick labels and positions
ax_1.set_xticklabels(labels, rotation = 90)

start, end = ax_1.get_ylim()
ax_1.yaxis.set_ticks(np.arange(start,end, 1))

# --- Spine and Grid ---

#Disable right and top spine
ax_1.spines['right'].set_visible(False)
ax_1.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_1.set_xlabel("İlçe",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_1.set_ylabel("Diyaliz m. sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

#Set xtick font info

ax_1.set_xticklabels(ax_1.get_xticklabels(),
                      font_xticks)

#       --- Ax 2: Scatterplot ---

ax_2.scatter(x = sorted_df.loc[:,"yearly_average_household_income"], # Remember that i took that info before?
             y = bar_heights_priv,
             s = 150, # To specify face width
             c = categorical_color)

# --- Spine and Grid ---

#Disable right and top spine
ax_2.spines['right'].set_visible(False)
ax_2.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_2.set_ylabel("Diyaliz m. sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_2.set_xlabel("Yıllık ortalama hanehalkı geliri (bin TL)",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"yearly_average_household_income"],
                        bar_heights_priv)[0]

ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_2.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#       --- Ax 3: Scatterplot ---

ax_3.scatter(x = sorted_df.loc[:,"population"], # Remember that i took that info before?
              y = bar_heights_priv,
              s = 150, # To specify face width
              c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_3.spines['right'].set_visible(False)
ax_3.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_3.set_ylabel("Diyaliz m. sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_3.set_xlabel("Nüfus",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"population"],
                        bar_heights_priv)[0]

ax_3.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_3.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#Set figure title
fig.suptitle("Diyaliz merkezlerinin \n ilçelere göre dağılımı" ,
             family = 'sans-serif',
             fontname = "Arial",
             color =  'black',
             weight = 'bold',
             size = 30,
             x = 0.50,
             y = 0.98) #Doesn't use fontdict for some reason

# # --- Misc ---
#Make layout tighter
plt.tight_layout() 

# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr_3.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr_3.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")

#%%FIGURE -- Physical Therapy Center
selected_inst = "Physical Therapy Center"
selected_inst_label = selected_inst + "_privpub_count"
#%% --- Visualization - English ---

# --- Figure Preparation ---

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

#Define a gridspect of 2 rows and 2 columns
gs = fig.add_gridspec(2, 2)

#The first ax will occupy all half of row 1
ax_1 = fig.add_subplot(gs[0,:])

#The second ax will occupy the second half of row 1
ax_2 = fig.add_subplot(gs[1,0])

#The third ax will occupy first place out of 4 in row 2
ax_3 = fig.add_subplot(gs[1,1])

# --- Plot Figure: Hospital---

#       --- Ax 1: Bar plot ---

#Sort DF
sorted_df = districts_extra.sort_values(by = selected_inst_label, ascending = False)

#Get labels for x - axis ticks
labels = list(sorted_df.loc[:,"district_tr"].values)

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1
bar_positions_2 = [x + 0.20 for x in bar_positions]

#Get bar heights from data
bar_heights_priv = [int(x[0]) for x in sorted_df.loc[:,selected_inst_label]]
bar_heights_pub = [int(x[1]) for x in sorted_df.loc[:,selected_inst_label]]

# --- Plot Figure ---

ax_1.bar(bar_positions,bar_heights_priv,
    width = 0.40,
    align = "center",
    color = categorical_color)

ax_1.bar(bar_positions_2,bar_heights_pub,
    width = 0.30,
    align = "center",
    color = categorical_color_2)

# --- Add Legend ---

ax_1.legend(["Private", "Public"],loc=1,prop={'size': 30})

# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax_1.set_xticks([x + 0.20 / 2 for x in bar_positions])

#Setting x-tick labels and positions
ax_1.set_xticklabels(labels, rotation = 90)

start, end = ax_1.get_ylim()
ax_1.yaxis.set_ticks(np.arange(start,end, 1))

# --- Spine and Grid ---

#Disable right and top spine
ax_1.spines['right'].set_visible(False)
ax_1.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_1.set_xlabel("District",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_1.set_ylabel("Number of physical therapy c.",
              fontdict = font_axislabels,
              labelpad= 18)

#Set xtick font info

ax_1.set_xticklabels(ax_1.get_xticklabels(),
                      font_xticks)

#       --- Ax 2: Scatterplot ---

ax_2.scatter(x = sorted_df.loc[:,"yearly_average_household_income"], # Remember that i took that info before?
             y = bar_heights_priv,
             s = 150, # To specify face width
             c = categorical_color)

# --- Spine and Grid ---

#Disable right and top spine
ax_2.spines['right'].set_visible(False)
ax_2.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_2.set_ylabel("Number of physical therapy c.",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_2.set_xlabel("Average yearly household income (thousand TL)",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"yearly_average_household_income"],
                        bar_heights_priv)[0]

ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_2.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#       --- Ax 3: Scatterplot ---

ax_3.scatter(x = sorted_df.loc[:,"population"], # Remember that i took that info before?
              y = bar_heights_priv,
              s = 150, # To specify face width
              c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_3.spines['right'].set_visible(False)
ax_3.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_3.set_ylabel("Number of physical therapy c.",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_3.set_xlabel("Population",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"population"],
                        bar_heights_priv)[0]

ax_3.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_3.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

fig.suptitle("Distribution of private and public physical therapy centers \n across districts." ,
             family = 'sans-serif',
             fontname = "Arial",
             color =  'black',
             weight = 'bold',
             size = 30,
             x = 0.50,
             y = 0.98) #Doesn't use fontdict for some reason

# # --- Misc ---
#Make layout tighter
plt.tight_layout() 

# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng_4.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng_4.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")

#%% --- Visualization - Turkish ---

# --- Figure Preparation ---

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

#Define a gridspect of 2 rows and 2 columns
gs = fig.add_gridspec(2, 2)

#The first ax will occupy all half of row 1
ax_1 = fig.add_subplot(gs[0,:])

#The second ax will occupy the second half of row 1
ax_2 = fig.add_subplot(gs[1,0])

#The third ax will occupy first place out of 4 in row 2
ax_3 = fig.add_subplot(gs[1,1])

# --- Plot Figure: Hospital---

#       --- Ax 1: Bar plot ---

#Sort DF
sorted_df = districts_extra.sort_values(by = selected_inst_label, ascending = False)

#Get labels for x - axis ticks
labels = list(sorted_df.loc[:,"district_tr"].values)

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1
bar_positions_2 = [x + 0.20 for x in bar_positions]

#Get bar heights from data
bar_heights_priv = [int(x[0]) for x in sorted_df.loc[:,selected_inst_label]]
bar_heights_pub = [int(x[1]) for x in sorted_df.loc[:,selected_inst_label]]

# --- Plot Figure ---

ax_1.bar(bar_positions,bar_heights_priv,
    width = 0.40,
    align = "center",
    color = categorical_color)

ax_1.bar(bar_positions_2,bar_heights_pub,
    width = 0.30,
    align = "center",
    color = categorical_color_2)

# --- Add Legend ---

ax_1.legend(["Özel.", "Devlet"],loc=1,prop={'size': 30})

# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax_1.set_xticks([x + 0.20 / 2 for x in bar_positions])

#Setting x-tick labels and positions
ax_1.set_xticklabels(labels, rotation = 90)

start, end = ax_1.get_ylim()
ax_1.yaxis.set_ticks(np.arange(start,end, 1))

# --- Spine and Grid ---

#Disable right and top spine
ax_1.spines['right'].set_visible(False)
ax_1.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_1.set_xlabel("İlçe",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_1.set_ylabel("Fizik tedavi m. sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

#Set xtick font info

ax_1.set_xticklabels(ax_1.get_xticklabels(),
                      font_xticks)

#       --- Ax 2: Scatterplot ---

ax_2.scatter(x = sorted_df.loc[:,"yearly_average_household_income"], # Remember that i took that info before?
             y = bar_heights_priv,
             s = 150, # To specify face width
             c = categorical_color)

# --- Spine and Grid ---

#Disable right and top spine
ax_2.spines['right'].set_visible(False)
ax_2.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_2.set_ylabel("Fizik tedavi m. sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_2.set_xlabel("Yıllık ortalama hanehalkı geliri (bin TL)",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"yearly_average_household_income"],
                        bar_heights_priv)[0]

ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_2.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#       --- Ax 3: Scatterplot ---

ax_3.scatter(x = sorted_df.loc[:,"population"], # Remember that i took that info before?
              y = bar_heights_priv,
              s = 150, # To specify face width
              c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_3.spines['right'].set_visible(False)
ax_3.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_3.set_ylabel("Fizik tedavi m. sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_3.set_xlabel("Nüfus",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"population"],
                        bar_heights_priv)[0]

ax_3.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_3.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#Set figure title
fig.suptitle("Fizik tedavi merkezlerinin \n ilçelere göre dağılımı" ,
             family = 'sans-serif',
             fontname = "Arial",
             color =  'black',
             weight = 'bold',
             size = 30,
             x = 0.50,
             y = 0.98) #Doesn't use fontdict for some reason

# # --- Misc ---
#Make layout tighter
plt.tight_layout() 

# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr_4.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr_4.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")

#%%FIGURE -- Gynecology and Obstetrics Clinic
selected_inst = "Gynecology and Obstetrics Clinic"
selected_inst_label = selected_inst + "_privpub_count"
#%% --- Visualization - English ---

# --- Figure Preparation ---

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

#Define a gridspect of 2 rows and 2 columns
gs = fig.add_gridspec(2, 2)

#The first ax will occupy all half of row 1
ax_1 = fig.add_subplot(gs[0,:])

#The second ax will occupy the second half of row 1
ax_2 = fig.add_subplot(gs[1,0])

#The third ax will occupy first place out of 4 in row 2
ax_3 = fig.add_subplot(gs[1,1])

# --- Plot Figure: Hospital---

#       --- Ax 1: Bar plot ---

#Sort DF
sorted_df = districts_extra.sort_values(by = selected_inst_label, ascending = False)

#Get labels for x - axis ticks
labels = list(sorted_df.loc[:,"district_tr"].values)

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1
bar_positions_2 = [x + 0.20 for x in bar_positions]

#Get bar heights from data
bar_heights_priv = [int(x[0]) for x in sorted_df.loc[:,selected_inst_label]]
bar_heights_pub = [int(x[1]) for x in sorted_df.loc[:,selected_inst_label]]

# --- Plot Figure ---

ax_1.bar(bar_positions,bar_heights_priv,
    width = 0.40,
    align = "center",
    color = categorical_color)

ax_1.bar(bar_positions_2,bar_heights_pub,
    width = 0.30,
    align = "center",
    color = categorical_color_2)

# --- Add Legend ---

ax_1.legend(["Private", "Public"],loc=1,prop={'size': 30})

# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax_1.set_xticks([x + 0.20 / 2 for x in bar_positions])

#Setting x-tick labels and positions
ax_1.set_xticklabels(labels, rotation = 90)

start, end = ax_1.get_ylim()
ax_1.yaxis.set_ticks(np.arange(start,end, 1))

# --- Spine and Grid ---

#Disable right and top spine
ax_1.spines['right'].set_visible(False)
ax_1.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_1.set_xlabel("District",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_1.set_ylabel("Number of gyn. and obstetrics c.",
              fontdict = font_axislabels,
              labelpad= 18)

#Set xtick font info

ax_1.set_xticklabels(ax_1.get_xticklabels(),
                      font_xticks)

#       --- Ax 2: Scatterplot ---

ax_2.scatter(x = sorted_df.loc[:,"yearly_average_household_income"], # Remember that i took that info before?
             y = bar_heights_priv,
             s = 150, # To specify face width
             c = categorical_color)

# --- Spine and Grid ---

#Disable right and top spine
ax_2.spines['right'].set_visible(False)
ax_2.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_2.set_ylabel("Number of gyn. and obstetrics c.",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_2.set_xlabel("Average yearly household income (thousand TL)",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"yearly_average_household_income"],
                        bar_heights_priv)[0]

ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_2.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#       --- Ax 3: Scatterplot ---

ax_3.scatter(x = sorted_df.loc[:,"population"], # Remember that i took that info before?
              y = bar_heights_priv,
              s = 150, # To specify face width
              c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_3.spines['right'].set_visible(False)
ax_3.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_3.set_ylabel("Number of gyn. and obstetrics c.",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_3.set_xlabel("Population",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"population"],
                        bar_heights_priv)[0]

ax_3.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_3.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

fig.suptitle("Distribution of private and public gyn. and obstetrics c. \n across districts." ,
             family = 'sans-serif',
             fontname = "Arial",
             color =  'black',
             weight = 'bold',
             size = 30,
             x = 0.50,
             y = 0.98) #Doesn't use fontdict for some reason

# # --- Misc ---
#Make layout tighter
plt.tight_layout() 

# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng_5svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_eng_5.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")

#%% --- Visualization - Turkish ---

# --- Figure Preparation ---

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

#Define a gridspect of 2 rows and 2 columns
gs = fig.add_gridspec(2, 2)

#The first ax will occupy all half of row 1
ax_1 = fig.add_subplot(gs[0,:])

#The second ax will occupy the second half of row 1
ax_2 = fig.add_subplot(gs[1,0])

#The third ax will occupy first place out of 4 in row 2
ax_3 = fig.add_subplot(gs[1,1])

# --- Plot Figure: Hospital---


# --- Data Selection ---
# --- Data Selection ---
#Sort DF
sorted_df = districts_extra.sort_values(by = selected_inst_label, ascending = False)

#Get labels for x - axis ticks
labels = list(sorted_df.loc[:,"district_tr"].values)

#Generate bar positions
from numpy import arange
bar_positions = arange(len(labels)) + 1
bar_positions_2 = [x + 0.20 for x in bar_positions]

#Get bar heights from data
bar_heights_priv = [int(x[0]) for x in sorted_df.loc[:,selected_inst_label]]
bar_heights_pub = [int(x[1]) for x in sorted_df.loc[:,selected_inst_label]]

# --- Plot Figure ---

#       --- Ax 1: Bar plot ---

ax_1.bar(bar_positions,bar_heights_priv,
    width = 0.40,
    align = "center",
    color = categorical_color)

ax_1.bar(bar_positions_2,bar_heights_pub,
    width = 0.30,
    align = "center",
    color = categorical_color_2)

# --- Add Legend ---

ax_1.legend(["Özel.", "Devlet"],loc=1,prop={'size': 30})

# --- Set x and y axis ticks ---

#Setting where x-ticks should be at
ax_1.set_xticks([x + 0.20 / 2 for x in bar_positions])

#Setting x-tick labels and positions
ax_1.set_xticklabels(labels, rotation = 90)

start, end = ax_1.get_ylim()
ax_1.yaxis.set_ticks(np.arange(start,end, 1))

# --- Spine and Grid ---

#Disable right and top spine
ax_1.spines['right'].set_visible(False)
ax_1.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_1.set_xlabel("İlçe",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_1.set_ylabel("Kadın hast. ve sağlığı m. sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

#Set xtick font info

ax_1.set_xticklabels(ax_1.get_xticklabels(),
                      font_xticks)

#       --- Ax 2: Scatterplot ---

ax_2.scatter(x = sorted_df.loc[:,"yearly_average_household_income"], # Remember that i took that info before?
             y = bar_heights_priv,
             s = 150, # To specify face width
             c = categorical_color)

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
ax_2.set_ylabel("Kadın hast. ve sağlığı m. sayısı",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"yearly_average_household_income"],
                        bar_heights_priv)[0]

ax_2.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_2.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#       --- Ax 3: Scatterplot ---

ax_3.scatter(x = sorted_df.loc[:,"population"], # Remember that i took that info before?
              y = bar_heights_priv,
              s = 150, # To specify face width
              c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_3.spines['right'].set_visible(False)
ax_3.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_3.set_ylabel("Kadın hast. ve sağlığı m. sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_3.set_xlabel("Nüfus",
              fontdict = font_axislabels,
              labelpad= 18)


#Annotate pearson's r
    
pearson_r = st.pearsonr(sorted_df.loc[:,"population"],
                        bar_heights_priv)[0]

ax_3.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_3.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

#Set figure title
fig.suptitle("Kadın hastalıkları ve sağlığı merkezlerinin \n ilçelere göre dağılımı" ,
             family = 'sans-serif',
             fontname = "Arial",
             color =  'black',
             weight = 'bold',
             size = 30,
             x = 0.50,
             y = 0.98) #Doesn't use fontdict for some reason

# # --- Misc ---
#Make layout tighter
plt.tight_layout() 

# --- Export Visualization ---

#As SVG
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr_5.svg")
plt.savefig(export_path, format = "svg", dpi = 1200, bbox_inches="tight")

#As png
export_path = complete_output_directory +  r"/" + (filename_final_processed + "_tr_5.png")
plt.savefig(export_path, format = "png", dpi = 300, bbox_inches="tight")












