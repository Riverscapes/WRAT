# # #====================================# # #
# # # Individual Recruitment Probability # # #
# # #====================================# # #

# Models the probability of recruitment of individual pieces of large wood via wind throw, bank erosion, or mortality
# Based on the equation ((He/Ht)/2) + ((0.5 - (0.5/10 ^ (1.4375 * B)))/2) + (D/4)
# Ht - Total tree height, derived from LANDFIRE EVH | He - Effective height
# B - Unitless slope | D - Density
# Modified from (source)
# Version 0.1
# Created by Jordan Gilbert


import arcpy
from arcpy.sa import *
import numpy as np
import SegmentZS
import os
import sys


def main(projectFolder, network, evh, evc, bankfull, dem, scratch):
    """Creates a network output for probability of individual LWD recruitment"""

    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("spatial")

    # scratch folder (must be folder not fgdb)
    if not os.path.exists(scratch):
        os.mkdir(scratch)                                                                                               # this might be redundant, does it need to be inside project?

    # generate raster of individual recruitment probability
    arcpy.addMessage("Creating probability raster")



def prob_raster(evh, evc, bankfull, dem, scratch):
    """Creates a raster output for probability of individual LWD recruitment"""

    # derive a 10m tree height raster from LANDFIRE EVH layer
    lfevh = arcpy.ListFields(evh, "MAX_HEIGHT")
    if len(lfevh) == 1:
        arcpy.DeleteField_management(evh, "MAX_HEIGHT")
    arcpy.AddField_management(evh, "MAX_HEIGHT", "SHORT")
    cursor = arcpy.da.UpdateCursor(evh, ["CLASSNAMES", "MAX_HEIGHT"])
    for row in cursor:
        if row[0] == "Forest Height 0 to 5 meters":
            row[1] = 5
        elif row[0] == "Forest Height 5 t0 10 meters":
            row[1] = 10
        elif row[0] == "Forest Height 10 to 25 meters":
            row[1] = 25
        elif row[0] == "Forest Height 25 to 50 meters":
            row[1] = 50
        else:
            row[1] = 0
        cursor.updateRow(row)
    del row
    del cursor

    evh_lookup = Lookup(evh, "MAX_HEIGHT")
    if not os.path.exists(os.path.dirname(os.path.dirname(evh)) + "/Height_Rasters"):
        os.mkdir(os.path.dirname(os.path.dirname(evh)) + "/Height_Rasters")
    total_height = os.path.dirname(os.path.dirname(evh)) + "/Height_Rasters/total_height.tif"
    arcpy.Resample_management(evh_lookup, total_height, 10, "BILINEAR")

    # derive an effective height raster from total height and euclidean distance
    arcpy.env.extent = total_height
    ed = EucDistance(bankfull, "", 1)
    ed_10m = scratch + "/ed_10m.tif"
    arcpy.Resample_management(ed, ed_10m, 10, "BILINEAR")                                                               # revisit - why does it need to be 1m in first place?
    euclidean = SetNull(ed_10m, ed_10m, "VALUE = 0")

    total_height = Raster(total_height)
    eh1 = total_height - euclidean
    effective_height = SetNull(eh1, eh1, "VALUE <= 0")

    # derive a tree density raster from LANDFIRE EVC
    lfevc = arcpy.ListFields(evc, "MAX_COVER")
    if len(lfevc) == 1:
        arcpy.DeleteField_management(evc, "MAX_COVER")
    arcpy.AddField_management(evc, "MAX_COVER", "SHORT")
    cursor = arcpy.da.UpdateCursor(evc, ["CLASSNAMES", "MAX_COVER"])
    for row in cursor:
        if row[0] == "Tree Cover >= 0 and < 10%":
            row[1] = 10
        elif row[0] == "Tree Cover >= 10 and < 20%":
            row[1] = 20
        elif row[0] == "Tree Cover >= 20 and < 30%":
            row[1] = 30
        elif row[0] == "Tree Cover >= 30 and < 40%":
            row[1] = 40
        elif row[0] == "Tree Cover >= 40 and < 50%":
            row[1] = 50
        elif row[0] == "Tree Cover >= 50 and < 60%":
            row[1] = 60
        elif row[0] == "Tree Cover >= 60 and < 70%":
            row[1] = 70
        elif row[0] == "Tree Cover >= 70 and < 80%":
            row[1] = 80
        elif row[0] == "Tree Cover >= 80 and < 90%":
            row[1] = 90
        elif row[0] == "Tree Cover >= 90 and < 100%":
            row[1] = 100
        else:
            row[1] = 0
        cursor.updateRow(row)
    del row
    del cursor

    evc_lookup = Lookup(evc, "MAX_COVER")
    if not os.path.exists(os.path.dirname(os.path.dirname(evc)) + "/Cover"):
        os.mkdir(os.path.dirname(os.path.dirname(evc)) + "/Cover")
    cover = os.path.dirname(os.path.dirname(evc)) + "/Cover/total_cover.tif"
    arcpy.Resample_management(evc_lookup, cover, 10, "BILINEAR")

    # generate the first term of probability eqn
    prob_term1 = ((effective_height/total_height) / 2)

    # derive the second term  of probability eqn from the unitless slope
    slope_percent = Slope(dem, "PERCENT_RISE")
    slope_10m = scratch + "/slope_10m.tif"
    arcpy.Resample_management(slope_percent, slope_10m, 10, "BILINEAR")
    slope_clip = scratch + "/slope_clip.tif"
    arcpy.Clip_management(slope_10m, "", slope_clip, prob_term1, maintain_clipping_extent="MAINTAIN_EXTENT")
    slope_clip = Raster(slope_clip)
    slope_unitless = slope_clip / 100
    if not os.path.exists(os.path.dirname(dem) + "/Slope"):
        os.mkdir(os.path.dirname(dem) + "/Slope")

    prob_term2 = (0.5 - (0.5/10**(1.4375*slope_unitless)))/2

    # generate third term of probability eqn
    cover = Raster(cover)
    prob_term3 = (cover/100.0)/4

    # final individual probability raster
    individual_probability = prob_term1 + prob_term2 + prob_term3

    effective_height.save(os.path.dirname(os.path.dirname(evh)) + "/Height_Rasters/effective_height.tif")
    slope_unitless.save(os.path.dirname(dem) + "/Slope/slope.tif")

    return individual_probability