# -*- coding: utf-8 -*-
"""
Created on Fri May 29 17:55:23 2020

@author: ejgen
"""


#%% --- Import required packages ---

import numpy as np
import pandas as pd

#%% --- Read in the datasets ---

health = pd.read_csv("../../../Data/Non-GIS Data/raw/istanbul_healthservices.csv")
airbnb = pd.read_csv("../../../Data/Non-GIS Data/raw//istanbul_airbnb.csv")

#%% ---  Get a general sense of the datasets ---

# Shape of the data 
print(health.shape) # 4072 rows, 14 cols
print(airbnb.shape) # 16251 rows, 16 cols

# First few lines

print(health.head())
print(airbnb.head())

#Not much info, let's print the columns

health_columns = health.columns
airbnb_columns = airbnb.columns

#%% --- Clean the dataset: Relevant - Irrelevant Columns ---

# Select the unwanted columns
health_unwanted_columns = ["TELEFON", "WEBSITESI", "ILCE_UAVT"]
airbnb_unwanted_columns = ["neighbourhood_group", "last_review", "number_of_reviews",
                           "minimum_nights",
                           "reviews_per_month",
                           "calculated_host_listings_count",
                           "availability_365"]

#Drop unwanted columns

for column in health_unwanted_columns:
    health.drop(column, axis = 1, inplace = True)

for column in airbnb_unwanted_columns:
    airbnb.drop(column, axis = 1, inplace = True)  
    
# Check shape now

print(health.shape) # 4072 rows, 11 cols
print(airbnb.shape) # 16251 rows, 9 cols

#%% --- Clean the dataset: Further Troubleshooting ---

#I want to be able to randomly take n samples from each dataset and then print them
#on a clean format to see the potential problems

#Random sample function

import random

def random_sample_from_dataset(dataframe,sample_size):
    #Accepts a dataframe and sample size as an argument
    #Returns a pandas series of size sample_size
    rows = [random.randrange(0,len(dataframe)) for num in range(0, sample_size)]
    selection = dataframe.iloc[rows,:]
    return selection

# Sample from the datasets
#If i had something to test for, i'd strive for somewhat of a representative sample size
#while sampling. However, i think the best to do here would be to print what i can read
#because i don't have any computational measure to test for something:
    
#!! IDEA: Make these objects so that you can call them? Dunno.    
health_sample = random_sample_from_dataset(health, 10)
airbnb_sample = random_sample_from_dataset(airbnb, 10)

# Make some kind of a sample reader function

def sample_reader(dataframe):
    #Accepts a dataframe as an argument
    #Prints out the sample dataframe into the console in a column - by - column format
    dataframe_columns = dataframe.columns
    for column in dataframe_columns:
        print("Commencing with " + column + " column of the dataframe")
        print("")
        for i in range(0,len(dataframe)):
            selection = dataframe.iloc[i]
            print(selection[column])
            print("")
            
#Read the samples
sample_reader(health_sample)
sample_reader(airbnb_sample)

#SPOTTED PROBLEMS:
# =============================================================================
#     df health column names not properly formatted
#     df health comun ILCE_ADI values not properly formatted:
#         - All upper case
#         - Turkish characters Ğ and İ do not show up
#     df health column ADI is not properly formatted:
#         - Turkish characters ğ, ı, ş, and ç do not show up
#     df health column ALT_KATEGORI is not properly formatted:
#         - Turkish characters ğ, ı, ş, and ç do not show up
#     Nan values in columns:
#         ACIL_SERVIS
#         YATAK
#         AMBULANS
#     df health column MAHALLE is not properly formatted:
#         - All upper case
#         -Turkish characters ğ, ı, ş, and ç do not show up
#         - Turkish characters Ğ and İ do not show up
#         
#     df airbnb column neigborhood is not properly formatted:
#         discrepancies with health names
#         should actually be called "district_tr"
# =============================================================================
 
#SOLUTIONS:

# =============================================================================
# - df health tags should be snake case and in english
# - df health district / mahalle names should go through a turkish correction
# - Var / yok should be englified for ICU / ambulance
# - then, this should be kept and added alongside a englified names
# - Turkish characters should be fixed in ADI/ALT-KATEGORI      
# - neighborhood should be called "district_tr" 
# =============================================================================
#We'll work on these one by one 

#%% --- Clean the dataset: Fix the problems ---      

#%% Fix column names
health_columns_in_english = ["institution_id","district_tr", "institution_name", "institution_type", "address",
                             "icu","n#_beds","ambulance", "neighborhood_tr", "latitude", "longitude"]

airbnb_columns_in_english = ["listing_id", "name", "host_id", "host_name", "district_eng",
                             "latitude", "longitude", "room_type", "price"]

#I can use either dataframe.columns attribute to assign new columns
#or i can pass a dictionary with old names/new names into dataframe.rename()

health.columns = health_columns_in_english
airbnb.columns = airbnb_columns_in_english   

#%%

# Here, i am using in-built pandas dataframe string methods to do some text processing
health.loc[:,"district_tr"] = health.loc[:,"district_tr"].str.lower().str.capitalize()
airbnb.loc[:,"district_tr"] = airbnb.loc[:,"district_eng"].str.lower().str.capitalize()

#I wşll be using df.map() method, so i'll need two dataframes: one for existing values - tr values
#and one for exixsting values - eng values
unique_districts_health = []
unique_districts_airbnb = []

for var in health.loc[:,"district_tr"].unique():
    unique_districts_health.append(var)
    
for var in airbnb.loc[:,"district_eng"].unique():
    unique_districts_airbnb.append(var)
    
#Get rid of the nan
unique_districts_health.pop()
    
unique_districts_tr_corrected = ["Kadıköy", "Fatih", "Tuzla", "Gaziosmanpaşa",
                                 "Üsküdar", "Adalar", "Sarıyer", "Arnavutköy",
                                 "Silivri", "Çatalca", "Küçükçekmece", "Beyoğlu",
                                 "Şile", "Kartal", "Şişli", "Beşiktaş", "Kağıthane",
                                 "Esenyurt", "Bahçelievler", "Avcılar", "Başakşehir",
                                 "Sultangazi", "Maltepe", "Sancaktepe", "Beykoz",
                                 "Büyükçekmece", "Bakırköy", "Pendik", "Bağcılar",
                                 "Esenler", "Beylikdüzü", "Ümraniye", "Eyüpsultan",
                                 "Çekmeköy", "Ataşehir", "Sultanbeyli", "Zeytinburnu",
                                 "Güngören", "Bayrampaşa"]

unique_districts_eng_corrected = ["Kadikoy", "Fatih", "Tuzla", "Gaziosmanpasa",
                                 "Uskudar", "Adalar", "Sariyer", "Arnavutkoy",
                                 "Silivri", "Catalca", "Kucukcekmece", "Beyoglu",
                                 "Sile", "Kartal", "Sisli", "Besiktas", "Kagithane",
                                 "Esenyurt", "Bahcelievler", "Avcilar", "Basaksehir",
                                 "Sultangazi", "Maltepe", "Sancaktepe", "Beykoz",
                                 "Buyukcekmece", "Bakirkoy", "Pendik", "Bagcilar",
                                 "Esenler", "Beylikduzu", "Umraniye", "Eyupsultan",
                                 "Cekmekoy", "Atasehir", "Sultanbeyli", "Zeytinburnu",
                                 "Gungoren", "Bayrampasa"]

health_unique_districts_dict_tr = dict(zip(unique_districts_health,unique_districts_tr_corrected)) 
health_unique_districts_dict_eng = dict(zip(unique_districts_health, unique_districts_eng_corrected)) 

#First, duplicate the district column
health.loc[:,"district_eng"] = health.loc[:,"district_tr"]

#Map the values accordingly
health.loc[:,"district_tr"] = health.loc[:,"district_tr"].map(health_unique_districts_dict_tr)
health.loc[:,"district_eng"] = health.loc[:,"district_eng"].map(health_unique_districts_dict_eng)


# I just realized i can do the same to the airbnb column. See below:
airbnb_unique_districts_dict_tr = dict(zip(unique_districts_eng_corrected, unique_districts_tr_corrected))

airbnb.loc[:,"district_tr"] = airbnb.loc[:"district_eng"]
airbnb.loc[:,"district_tr"] = airbnb.loc[:,"district_tr"].map(airbnb_unique_districts_dict_tr)
## Whew! That's done!

#%% Correcting values in health "neighborhood" column

#Last time, i used a dictionary with df.map() method because there were 39 values
#At that amount of values, it seemed less work to me to manually map them to a dictionary
#However, i don't know all the values in the "neighborhood" column.
#Therefore, i'm better off writing a function to correct them

# Use dataframe str methods to normalize them
health.loc[:,"neighborhood_tr"] = health.loc[:,"neighborhood_tr"].str.lower().str.title()

#Take another 10 samples to see the problems:
    
health_sample = random_sample_from_dataset(health, 10)
print(health_sample.loc[:,"neighborhood_tr"])

#Problematic letters:
# ýi þş ðğ, ÞŞ Ýİ
#The problem is two-fold here: Some I's are written as İ's, I can't convert them
#without converting İ's to I's too.
#Regex would be a good solution but i don't know how to use regex.

#Once again, let's use the str methods to change these

unwanted_letters_dict = {"ý": "i", "þ": "ş", "ð": "ğ", "Þ": "Ş", "Ý": "İ"}
for key,value in unwanted_letters_dict.items():
    health.loc[:,"neighborhood_tr"] = health.loc[:,"neighborhood_tr"].str.replace(key,value)
    
#Wow, that was actually quite clean and fast. Kudos to me!

#%% Correcting values in "institution_name" and institution_type" columns
#We can use the method that we've used above!

columns_to_fix = ["institution_name", "institution_type", "address"]
for column in columns_to_fix:
    for key,value in unwanted_letters_dict.items():
        health.loc[:,column] = health.loc[:,column].str.replace(key,value)
        
#%% --- Dropping certain columns based on their value in "institution_type" column

unwanted_institution_types = ["Optik", "Medikal", "Laboratuvar",
                              "Laboratuvar Özel", "Diş Laboratuvari",
                              "İşitme Cihazi Satiş ve Uygulama Merkezi",
                              "Protez-Ortez Yapim ve Uygulama Merkezi",
                              "Protez-Ortez Yapim ve Uygulama Merkezi Özel",
                              "Ambulans"]

wanted_institution_types_mask = health.loc[:,"institution_type"].isin(unwanted_institution_types) == False

health = health.loc[wanted_institution_types_mask,:] 

        
#%% --- Seperating and Aggregating private and state-owned

#Create a regex pattern
private_pattern = r"[Öö]zel"

#Create a boolean indexing mask out of that pattern
private_mask = health.loc[:,"institution_type"].str.contains(private_pattern,
                                                              regex = True,
                                                              na = False)
#Create a boolean indexing mask that takes the opposite of that pattern
non_private_mask = private_mask == False

#Encode public - private information in another column
health.loc[private_mask,"private_or_public"] = "Private"
health.loc[non_private_mask,"private_or_public"] = "Public"

#Erasing private info
private_mask = health.loc[:,"private_or_public"] == "Private"

#Remove the "özel" str from the strings and then format the string
health.loc[private_mask, "institution_type"] = health.loc[private_mask, "institution_type"].str.replace("Özel", "").str.lstrip().str.rstrip()

# Extra: To make categories overlap with each other, format "devlet hastanesi" to be "Hastane

#Create a boolean mask
public_hospital_mask = health.loc[:,"institution_type"].str.contains("Devlet")

# Select the rows containing the desired value and re-format their value
health.loc[public_hospital_mask,"institution_type"] = (health.loc[public_hospital_mask,"institution_type"]
                                                       .str.replace("Devlet", "").str.replace("Hastanesi", "Hastane")
                                                       .str.lstrip().str.rstrip())

#%% --- Fixing rows with institution_name value "Fizik Tedavi Rehabilitasyon Merkezi"

#Create a boolean mask to select by string pattern
fizik_ted_mask = health.loc[:,"institution_type"].str.contains("Fizik Tedavi")

#Override values to be "Fizik Tedavi Merkezi"
health.loc[fizik_ted_mask,"institution_type"] = "Fizik Tedavi Merkezi"

#%%  --- Fixing rows with institution_name value "Ağiz Diş Sağliği Merkezleri"

diş_mask = health.loc[:,"institution_type"] == "Ağiz Diş Sağliği Merkezleri"

health.loc[diş_mask,"institution_type"] = "Ağiz ve Diş Sağliği Merkezi"


#%% --- Determine institutions that are related to health tourism ---
#Aka beauty center, health transplant center etc.

possible_patterns = [r"[Ee]st", r"[Pp]lastik"]

for pattern in possible_patterns:
    
    #Create a boolean mask
    pat_mask = health.loc[:,"institution_name"].str.contains(pattern,
                                         regex = True,
                                         na = False)
    pat_only = health.loc[pat_mask,:]
    
    health.loc[pat_mask, "related_to_htourism"] = "Yes"
    
health.loc[health.loc[:,"related_to_htourism"] != "Yes", "related_to_htourism"] = "No"
    

#%% --- Correcting and translating institution_type column

#Get values
inst_type_values = health.loc[:,"institution_type"].value_counts().index

#Create an abbreviation list and translation list

inst_type_full_eng = ["Family Health Center", "Dental Health Center",
                      "Doctor's Office", "Veterinary Clinic",
                      "Polyclinic", "Hospital",
                      "First Aid Station", "Medical Center",
                      "Dialysis Center", "Elderly Care Facility",
                      "Screening Center", "Health Cabin",
                      "Public Health Center", "Planned Parenthood Center",
                      "Nursing House", "Training and Research Hospital",
                      "Other", "Ophthalmology Center",
                      "Tuberculosis Dispensary",
                      "Early Diagnosis and Therapy Center",
                      "Turkish Red Crescent",
                      "Physical Therapy Center",
                      "Primary Health Care Center",
                      "University Hospital",
                      "Gynecology and Obstetrics Clinic",
                      "General Clinic", "Reproductory Health Center",
                      "Rehabilitation and Family Counseling Center",
                      "Domiciliary Care Center",
                      "Municipality Health Center",
                      "Blood Bank", "Maternity Hospital", "Military Hospital"]

inst_type_abbreviation_tr = ["Aile Sağlığı M.", "Ağız Diş Sağlığı M.",
                             "Muayenehane", "Veteriner", "Poliklinik",
                             "Hastane", "Acil Yardım İst.", "Tıp M.",
                             "Diyaliz M.", "Huzurevi", "Görüntüleme M.",
                             "Sağlık Kabini", "Toplum Sağlığı M.",
                             "Aile Planlama M.", "Bakımevi",
                             "Eğitim Araştırma H.", "Sağlık Diğer",
                             "Göz M.", "Verem Savaş Disp.", "Tanı Tedavi M.",
                             "Kızılay", "Fizik Tedavi M.", "Sağlık Evi",
                             "Üniversite H.", "Kadın Hastalıkları ve Sağlığı M.",
                             "Klinikler", "Üremeye Yardımcı Tedavi M.",
                             "Rehabilitasyon ve Aile Danışma M.",
                             "Evde Bakım M.", "Belediye Sağlık M.",
                             "Kan M.", "Kadın Doğum ve Çocuk H.",
                             "Askeri H."]

inst_type_abbreviation_eng = ["Family Health C.","Dental Health C.",
                              "Doctor's Office", "Veterinary Cli.",
                              "Polyclinic", "Hospital","First Aid Station",
                              "Medical C.", "Dialysis C.","Elderly Care Fac.",
                              "Screening C." , "HealtH Cabin",
                              "Public Health C.", "Planned Parenthood C.",
                              "Nursing House", "Training and Research H.",
                              "Other", "Ophthalmology C.",
                              "Tuberculosis Dispensary",
                              "Early Diagnosis and Therapy C.",
                              "Turkish Red Crescent", "Physical Therapy C.",
                              "Primary Health Care C.",
                              "University H.",
                              "Gynecology and Obstetrics C.",
                              "General Clinic",
                              "Reproductory Health C.",
                              "Rehabilitation and Family Counseling C.",
                              "Domiciliary Care C.", "Municipality Health C.",
                              "Blood Bank", "Maternity H.", "Military H."]

i = 0
for inst_type in inst_type_values:
    mask = health.loc[:,"institution_type"] == inst_type
    health.loc[mask,"institution_type_eng"] = inst_type_full_eng[i]
    health.loc[mask, "institution_type_abbrv_tr"] = inst_type_abbreviation_tr[i]
    health.loc[mask, "institution_type_abbrv_eng"] = inst_type_abbreviation_eng[i]
    
    i += 1
#%% --- Correcting "Yok/Var" in icu and ambulance rows

correction_dict = {"Var" : "Yes", "Yok": "No" }

columns_to_fix = ["icu", "ambulance"]

for column in columns_to_fix:
    health.loc[:,column] = health.loc[:,column].map(correction_dict)
    
#%% --- Fix "Eğitim Araştırma Hastanesi" to be just "Hospital"

egitim_mask = health.loc[:,"institution_type"] == "Eğitim Araştirma Hastanesi"

health.loc[egitim_mask, ["institution_type_eng", "institution_type_abbrv_eng"]] = "Hospital"
health.loc[egitim_mask, ["institution_type", "institution_type_abbrv_tr"]] = "Hastane"

#%% -- Add "level of care" information

#Create levels of care

low_level_care = ["Aile Sağliği Merkezi","Sağlik Kabini",
                  "Toplum Sağliği Merkezi","Ana Çocuk Sağliği ve Aile Planlama Merkezi",
                  "Belediye Sağlik Merkezi", "Evde Bakim Merkezleri"]

hospital_level_care = ["Hastane", "Poliklinik", "Tip Merkezi", "Üniversite Hastanesi",
                  "Klinikler", "Askeri Hastane", "Kadin Doğum ve Çocuk Hastanesi"]

specialized_care = ["Ağiz ve Diş Sağliği Merkezi", "Diyaliz Merkezi",
                    "Görüntüleme Merkezi", "Göz Merkezi",
                    "Verem Savaş Dispanseri", "Tani Tedavi Merkezleri",
                    "Fizik Tedavi Merkezi","Kadin Hastalikleri ve Sağliği Merkezi",
                    "Klinikler", "Üremeye Yardimci Tedavi Merkezi", "Rehabilitasyon ve Aile Danişma Merkezi"]

#Create list of cares
care_types = [low_level_care, hospital_level_care, specialized_care]
care_type_name = ["low level", "hospital level", "specialized"]

i = 0
#For care type in care types, create a mask
for care_type in care_types:
    care_type_mask = health.loc[:,"institution_type"].isin(care_type)
    
    #Access dataframe based on mask and populate column with care type
    health.loc[care_type_mask,"care_type"] = care_type_name[i]
    i += 1
    
#Fill na values with "not specified"

health.loc[:,"care_type"].fillna("not specified", inplace = True)




#%% --- Exporting ---

#That's about it! The cleaning that we have done here was not that crucial to data
#quality. However, we have in our hand a more readable dataset devoit of any
#extra information we do not want.
#Let's now export them:
    
#Commented out to prevent accidental re-writing

#health.to_csv("../../../Data/Non-GIS Data/cleaned/istanbul_healthservices_cleaned.csv", encoding='utf-8-sig', index = False)
#airbnb.to_csv("../../../Data/Non-GIS Data/cleaned/istanbul_airbnb_cleaned.csv", encoding='utf-8-sig', index = False)

#Let's move on to the analysis and visualization part!




                                 
 
    
