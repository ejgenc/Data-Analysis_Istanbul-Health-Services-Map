# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 22:14:37 2020

@author: ejgen
"""


#%% --- Import Required Packages ---

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pyproj import CRS
import geojson
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points

#%% --- GEODATA PREPARATION : Get Istanbul Shapefile

#Create a filepath for the Turkey shapefile

tr_borders_level_2_fp = "../../../Data/GIS data/Raw/Turkey_administrative_borders/tur_polbnda_adm2.shp"

#Make it into a Geodataframe

tr_borders_level_2 = gpd.read_file(tr_borders_level_2_fp)

#Check shapefile crs

print(tr_borders_level_2.crs)

#Print shapefile head

print(tr_borders_level_2.head())

#Look at shapefile columns

print(tr_borders_level_2.columns)

#I guess that i can drop the following columns: adm_1, pcode, adm0_en,
# adm0_tr, adm_0

columns_to_drop = ["adm1", "pcode", "adm0_en", "adm0_tr", "adm_0"]
tr_borders_level_2.drop(columns_to_drop, axis = 1, inplace = True)

#Great, we see that we can filter istanbul by adm1_tr == "İstanbul"

istanbul_mask = tr_borders_level_2.loc[:,"adm1_tr"] == "İSTANBUL"
istanbul_districts = tr_borders_level_2.loc[istanbul_mask, :]

# Do another level of drops

columns_to_drop = ["adm1_tr", "adm1_en"]
istanbul_districts.drop(columns_to_drop, axis = 1, inplace = True)

#Rename columns

istanbul_districts.rename(columns = {"adm2_en" : "district_eng", "adm2_tr" : "district_tr"}, inplace = True)

# Fix string formatting

istanbul_districts.loc[:,"district_eng"] = istanbul_districts.loc[:,"district_eng"].str.capitalize().str.strip()
istanbul_districts.loc[:,"district_tr"] = istanbul_districts.loc[:,"district_tr"].str.capitalize().str.strip()

#I also want to add a new column encoding which continent the district is on:

eur_districts = ["Arnavutkoy", "Avcilar", "Bagcilar",
                 "Bahcelievler", "Bakirkoy", "Basaksehir",
                 "Bayrampasa", "Besiktas", "Beylikduzu",
                 "Beyoglu", "Buyukcekmece", "Catalca",
                 "Esenler", "Esenyurt", "Eyup","Fatih",
                 "Gaziosmanpasa", "Gungoren", "Kagithane",
                 "Kucukcekmece", "Sariyer", "Silivri",
                 "Sisli","Zeytinburnu"]

anat_districts = ["Adalar", "Atasehir", "Beykoz",
                  "Cekmekoy", "Kadikoy", "Kartal",
                  "Maltepe","Pendik","Sancaktepe",
                  "Sultanbeyli","Sile","Tuzla",
                  "Umraniye", "Uskudar"]

eur_district_mask = istanbul_districts.loc[:,"district_eng"].isin(eur_districts)
anat_district_mask = istanbul_districts.loc[:,"district_eng"].isin(anat_districts)

istanbul_districts.loc[eur_district_mask, "continent"] = "eur"
istanbul_districts.loc[anat_district_mask, "continent"] = "anat"
    

#Save the shapefile

out_fp = "../../../Data/GIS data/Processed/istanbul_districts.shp"

#Commented out to prevent accidental rewriting
#istanbul_districts.to_file(out_fp, encoding = "utf-8")



