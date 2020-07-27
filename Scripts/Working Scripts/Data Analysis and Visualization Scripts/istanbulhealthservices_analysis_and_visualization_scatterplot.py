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

#Istanbul extra district data
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
                "Physical Therapy Center", "Gynecology and Obstetrics Clinic",
                "Medical Center", "Polyclinic","Planned Parenthood Center"]

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



#%% --- Visualization - English ---

# --- Figure Preparation ---

#Create a figure
fig = plt.figure(figsize = (19.20,19.20),
                  constrained_layout=True) #Constrained layout to use with gridspec

gs = fig.add_gridspec(3,4)

#Ax_1 is a giant scatterplot on the left side that spans all 8 rows
ax_1 = fig.add_subplot(gs[0,:])

small_axes = []
        
for j in range(1,3):
    for i in range(0,4):
         ax = fig.add_subplot(gs[j,i])
         small_axes.append(ax)
    
# --- Scatterplot Top: Income - Num. of Inst. ---

ax_1.scatter(x =  districts_private_and_income.loc[:,"yearly_average_household_income"],
             y =  districts_private_and_income.loc[:,"private_or_public"],
             s = 150, # To specify face width
             c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_1.spines['right'].set_visible(False)
ax_1.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_1.set_xlabel("Average yearly household income (thousand TL)",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_1.set_ylabel("Number of private health institutions",
              fontdict = font_axislabels,
              labelpad= 18)

#Label certain datapoints based on district

districts_to_label = ["Kadikoy","Besiktas", "Bakirkoy","Adalar",
                      "Sisli", "Sariyer","Uskudar","Atasehir",
                      "Maltepe","Fatih", "Beyoglu","Bahcelievler",
                      "Eyupsultan","Bagcilar"]

districts_to_label_mask = districts_private_and_income.loc[:,"district_eng"].isin(districts_to_label)

districts_to_label_xy_df = districts_private_and_income.loc[districts_to_label_mask,["district_eng","private_or_public","yearly_average_household_income"]]

for idx, row in districts_to_label_xy_df.iterrows():
    x = row["yearly_average_household_income"] + 2
    y = row["private_or_public"] #To align it properly
    ax_1.annotate(s = row["district_eng"],
                  xy = (x,y),
                  horizontalalignment='left',
                  verticalalignment = "center")



#Annotate pearson's r
    
pearson_r = st.pearsonr(districts_private_and_income.loc[:,"private_or_public"],
                        districts_private_and_income.loc[:,"yearly_average_household_income"])[0]

ax_1.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_1.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

# --- Scatterplots Bottom : Income - Num. of Inst for all sub-categories
institutions = ["Hospital", "Dental Health Center", "Dialysis Center",
                "Physical Therapy Center", "Gynecology and Obstetrics Clinic",
                "Medical Center", "Polyclinic","Planned Parenthood Center"]
i = 0
for ax in small_axes:
    current_inst = institutions[i]
    current_inst_label = current_inst + "_privpub_count"
    
    sorted_df = districts_private_and_income.sort_values(by = current_inst_label, ascending = False)
    
    x_values = sorted_df.loc[:,"yearly_average_household_income"]
    y_values = [x[0] for x in sorted_df.loc[:, current_inst_label]]
    
    #Calculate pearson
    
    pearson_r = st.pearsonr(x_values, y_values)[0]
    
    # Annotate those who are non-linear
    
    if pearson_r < 0.40:
        ax.scatter(x = x_values,
             y =  y_values,
             s = 30, # To specify face width
             c = "black",
             alpha = 0.2)
    else:
        ax.scatter(x = x_values,
                 y =  y_values,
                 s = 30, # To specify face width
                 c = categorical_color)


    # --- Set x and y axis ticks ---
    
    
    # --- Spine and Grid ---
    
    #Disable right and top spine
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    # --- Text ---
    
    #Add x axis label
    ax.set_xlabel("Average yearly household income (thousand TL)",
                  labelpad= 0,
                  fontweight = "bold")
    
    # Add y axis label
    ax.set_ylabel("Number of private health institutions",
                  labelpad= 0,
                  fontweight = "bold")
    
    #Set title
    
    ax.set_title(str(current_inst),
                 loc = "left",
                 fontweight = "bold")
    
    
    
    #Annotate pearson's r
    if pearson_r < 0.40:
        
        ax.annotate(s = "r = {:.2f}".format(pearson_r),
                      xy = (.9, .9),
                      xycoords=ax.transAxes,
                      color = "black",
                      alpha = 0.2,
                      weight = "bold",
                      fontsize = 15)
        
    else:
        
        ax.annotate(s = "r = {:.2f}".format(pearson_r),
                      xy = (.9, .9),
                      xycoords=ax.transAxes,
                      color = "black",
                      weight = "bold",
                      fontsize = 15)

    
    # --- Logic ---
    #Increment i by one
    
    i += 1
        
   
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

gs = fig.add_gridspec(3,4)

#Ax_1 is a giant scatterplot on the left side that spans all 8 rows
ax_1 = fig.add_subplot(gs[0,:])

small_axes = []
        
for j in range(1,3):
    for i in range(0,4):
         ax = fig.add_subplot(gs[j,i])
         small_axes.append(ax)
    
# --- Scatterplot Top: Income - Num. of Inst. ---

ax_1.scatter(x =  districts_private_and_income.loc[:,"yearly_average_household_income"],
             y =  districts_private_and_income.loc[:,"private_or_public"],
             s = 150, # To specify face width
             c = categorical_color)


# --- Set x and y axis ticks ---


# --- Spine and Grid ---

#Disable right and top spine
ax_1.spines['right'].set_visible(False)
ax_1.spines['top'].set_visible(False)

# --- Text ---

#Add x axis label
ax_1.set_xlabel("Yıllık ortalama hanehalkı geliri (bin TL)",
              fontdict = font_axislabels,
              labelpad= 18)

# Add y axis label
ax_1.set_ylabel("Özel sağlık kuruluşu sayısı",
              fontdict = font_axislabels,
              labelpad= 18)

#Label certain datapoints based on district

districts_to_label = ["Kadikoy","Besiktas", "Bakirkoy","Adalar",
                      "Sisli", "Sariyer","Uskudar","Atasehir",
                      "Maltepe","Fatih", "Beyoglu","Bahcelievler",
                      "Eyupsultan","Bagcilar"]

districts_to_label_mask = districts_private_and_income.loc[:,"district_eng"].isin(districts_to_label)

districts_to_label_xy_df = districts_private_and_income.loc[districts_to_label_mask,["district_tr","private_or_public","yearly_average_household_income"]]

for idx, row in districts_to_label_xy_df.iterrows():
    x = row["yearly_average_household_income"] + 2
    y = row["private_or_public"] #To align it properly
    ax_1.annotate(s = row["district_tr"],
                  xy = (x,y),
                  horizontalalignment='left',
                  verticalalignment = "center")



#Annotate pearson's r
    
pearson_r = st.pearsonr(districts_private_and_income.loc[:,"private_or_public"],
                        districts_private_and_income.loc[:,"yearly_average_household_income"])[0]

ax_1.annotate(s = "r = {:.2f}".format(pearson_r),
              xy = (.9, .9),
              xycoords=ax_1.transAxes,
              color = "black",
              weight = "bold",
              fontsize = 15)

# --- Scatterplots Bottom : Income - Num. of Inst for all sub-categories
institutions = ["Hospital", "Dental Health Center", "Dialysis Center",
                "Physical Therapy Center", "Gynecology and Obstetrics Clinic",
                "Medical Center", "Polyclinic","Planned Parenthood Center"]

institutions_tr = ["Hastane", "Ağız ve Diş Sağlığı M.", "Diyaliz M.",
                   "Fizik Tedavi M.", "Kadın Hastalıkları ve Sağlığı M.",
                   "Tıp Merkezi", "Poliklinik", "Ana Çocuk Sağlığı ve Aile Planlama M."]

i = 0
for ax in small_axes:
    current_inst = institutions[i]
    current_inst_tr = institutions_tr[i]
    current_inst_label = current_inst + "_privpub_count"
    
    sorted_df = districts_private_and_income.sort_values(by = current_inst_label, ascending = False)
    
    x_values = sorted_df.loc[:,"yearly_average_household_income"]
    y_values = [x[0] for x in sorted_df.loc[:, current_inst_label]]
    
    #Calculate pearson
    
    pearson_r = st.pearsonr(x_values, y_values)[0]
    
    # Annotate those who are non-linear
    
    if pearson_r < 0.40:
        ax.scatter(x = x_values,
             y =  y_values,
             s = 30, # To specify face width
             c = "black",
             alpha = 0.2)
    else:
        ax.scatter(x = x_values,
                 y =  y_values,
                 s = 30, # To specify face width
                 c = categorical_color)


    # --- Set x and y axis ticks ---
    
    
    # --- Spine and Grid ---
    
    #Disable right and top spine
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    # --- Text ---
    
    #Add x axis label
    ax.set_xlabel("Yıllık ortalama hanehalkı geliri (bin TL)",
                  labelpad= 0,
                  fontweight = "bold")
    
    # Add y axis label
    ax.set_ylabel("Özel sağlık kuruluşu sayısı",
                  labelpad= 0,
                  fontweight = "bold")
    
    #Set title
    
    ax.set_title(str(current_inst_tr),
                 loc = "left",
                 fontweight = "bold")
    
    
    
    #Annotate pearson's r
    if pearson_r < 0.40:
        
        ax.annotate(s = "r = {:.2f}".format(pearson_r),
                      xy = (.9, .9),
                      xycoords=ax.transAxes,
                      color = "black",
                      alpha = 0.2,
                      weight = "bold",
                      fontsize = 15)
        
    else:
        
        ax.annotate(s = "r = {:.2f}".format(pearson_r),
                      xy = (.9, .9),
                      xycoords=ax.transAxes,
                      color = "black",
                      weight = "bold",
                      fontsize = 15)

    
    # --- Logic ---
    #Increment i by one
    
    i += 1
        
   
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












