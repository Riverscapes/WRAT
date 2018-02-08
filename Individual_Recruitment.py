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
import datetime
import uuid
import projectxml


def main(projectFolder, projName, hucID, hucName, network, evh, evc, bankfull, dem, scratch):
    """Creates a network output for probability of individual LWD recruitment"""

    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("spatial")

    # scratch folder (must be folder not fgdb)
    if not os.path.exists(scratch):
        os.mkdir(scratch)

    # check that input data is projected
    networkSR = arcpy.Describe(network).spatialReference
    if networkSR.type != "Projected":
        raise Exception("Input stream network must have a projected coordinate system")
    bankfullSR = arcpy.Describe(bankfull).spatialReference
    if bankfullSR.type != "Projected":
        raise Exception("Input bankfull channel must have a projected coordinate system")

    # generate raster of individual recruitment probability
    arcpy.AddMessage("Creating probability raster")
    individual_raster = prob_raster(evh, evc, bankfull, dem, scratch)

    # create a table from raster to merge with network
    arcpy.AddMessage("Creating probability table from raster")
    rasterToTable(network, individual_raster, scratch)

    # merge table with network for final output
    arcpy.AddMessage("Merging table to netwrok")
    j = 1
    while os.path.exists(projectFolder + "/02_Analyses/Output_" + str(j)):
        j += 1
    os.mkdir(projectFolder + "/02_Analyses/Output_" + str(j))

    table = scratch + "/out_table.txt"
    out_table = projectFolder + "/02_Analyses/Output_" + str(j) + "/out_table.dbf"

    individual_raster.save(projectFolder + "/02_Analyses/Output_" + str(j) + "/probability_raster.tif")
    out_network = projectFolder + "/02_Analyses/Output_" + str(j) + "/recruitment_prob.shp"
    arcpy.CopyFeatures_management(network, out_network)

    arcpy.CopyRows_management(table, out_table)
    arcpy.JoinField_management(out_network, "FID", out_table, "ID", ["SUM", "AREA", "REL_PROB", "NORM_PROB"])

    arcpy.Delete_management(projectFolder + "/02_Analyses/Output_" + str(j) + "/out_table.dbf")

    arcpy.CheckInExtension("spatial")

    # # # Write xml file # # #

    if not os.path.exists(projectFolder + "/project.rs.xml"):
        xmlfile = projectFolder + "/project.rs.xml"

    # initiate xml file creation
    newxml = projectxml.ProjectXML(xmlfile, "WRAT", projName)

    if not hucID == None:
        newxml.addMeta("HUCID", hucID, newxml.project)
    if not hucID == None:
        idlist = [int(x) for x in str(hucID)]
        if idlist[0] == 1 and idlist[1] == 7:
            newxml.addMeta("Region", "CRB", newxml.project)
    if not hucName == None:
        newxml.addMeta("Watershed", hucName, newxml.project)

    newxml.addWRATRealization("WRAT Realization 1", rid="RZ1", dateCreated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              productVersion="1.0.0", guid=getUUID())

    # add inputs and outputs to xml file
    newxml.addProjectInput("Vector", "Stream Network", network[network.find("01_Inputs"):], iid="NETWORK1", guid=getUUID())
    newxml.addWRATInput(newxml.WRATrealizations[0], "Network", ref="NETWORK1")

    newxml.addProjectInput("Raster", "Vegetation Height", evh[evh.find("01_Inputs"):], iid="VEGHEIGHT1", guid=getUUID())
    newxml.addWRATInput(newxml.WRATrealizations[0], "Vegetation Height", ref="VEGHEIGHT1")

    newxml.addProjectInput("Raster", "Vegetation Cover", evc[evc.find("01_Inputs"):], iid="VEGCOVER1", guid=getUUID())
    newxml.addWRATInput(newxml.WRATrealizations[0], "Vegetation Cover", ref="VEGCOVER1")

    newxml.addProjectInput("Vector", "Bankfull Channel", bankfull[bankfull.find("01_Inputs"):], iid="BANKFULL1", guid=getUUID())
    newxml.addWRATInput(newxml.WRATrealizations[0], "Bankfull Channel", ref="BANKFULL1")

    newxml.addProjectInput("DEM", "DEM", dem[dem.find("01_Inputs"):], iid="DEM1", guid=getUUID())
    newxml.addWRATInput(newxml.WRATrealizations[0], "DEM", ref="DEM1")

    newxml.addWRATInput(newxml.WRATrealizations[0], "Height Rasters", "Total Height",
                        path=os.path.dirname(os.path.dirname(evh[evh.find("01_Inputs"):])) + "/Height_Rasters/total_height.tif",
                        guid=getUUID())
    newxml.addWRATInput(newxml.WRATrealizations[0], "Height Rasters", "Effective Height",
                        path=os.path.dirname(os.path.dirname(evh[evh.find("01_Inputs"):])) + "/Height_Rasters/effective_height.tif",
                        guid=getUUID())
    newxml.addWRATInput(newxml.WRATrealizations[0], "Cover Rasters", "Total Cover",
                        path=os.path.dirname(os.path.dirname(evc[evc.find("01_Inputs"):])) + "/Cover_Rasters/total_cover.tif",
                        guid=getUUID())
    newxml.addWRATInput(newxml.WRATrealizations[0], "Slope", "Slope",
                        path=os.path.dirname(dem[dem.find("01_Inputs"):]) + "/Slope/slope.tif", guid=getUUID())

    newxml.write()

    return


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


def rasterToTable(network, raster, scratch):
    """Applies the raster output for individual recruitment probability to a network"""

    # make 0s in probability raster no data
    raster = Con(IsNull(raster), 0, raster)

    # create arrays for fields in output network
    lengtharray = np.asarray(arcpy.da.FeatureClassToNumPyArray(network, "FID"), np.int16)

    oid = np.arange(0, len(lengtharray), 1)
    sum_l = []
    area_l = []

    # apply segmentZS functions to each segment of network to extract field values from raster
    cursor = arcpy.da.SearchCursor(network, "SHAPE@")
    for row in cursor:
        sval = SegmentZS.segmentSum(row[0], raster, "50 Meters", scratch)
        aval = SegmentZS.segmentArea(row[0], "50 Meters", scratch)

        sum_l.append(sval)
        area_l.append(aval)

    del row
    del cursor

    # create and populate probability array
    sum_a = np.asarray(sum_l, np.float32)
    area_a = np.asarray(area_l, np.float32)
    div_a = np.divide(sum_a, area_a)
    div_amax = div_a.max()
    div_amin = div_a.min()
    rel_prob_a = np.zeros(len(div_a))
    norm_prob_a = np.multiply(div_a, 100)

    for x in range(len(div_a)):
        rel_prob_a[x] = (div_a[x] - div_amin)/(div_amax - div_amin)

    # generate output table to merge to network
    columns = np.column_stack((oid, sum_a))
    columns2 = np.column_stack((columns, area_a))
    columns3 = np.column_stack((columns2, rel_prob_a))
    columns4 = np.column_stack((columns3, norm_prob_a))
    out_table = scratch + "/out_table.txt"
    np.savetxt(out_table, columns4, delimiter=",", header="ID, SUM, AREA, REL_PROB, NORM_PROB", comments="")

    del sum_a, area_a, div_a, rel_prob_a, norm_prob_a, columns, columns2, columns3, columns4

    return

def getUUID():
    return str(uuid.uuid4()).upper()


if __name__ == '__main__':
    main(sys.argv[1],
         sys.argv[2],
         sys.argv[3],
         sys.argv[4],
         sys.argv[5],
         sys.argv[6],
         sys.argv[7],
         sys.argv[8],
         sys.argv[9],
         sys.argv[10])
