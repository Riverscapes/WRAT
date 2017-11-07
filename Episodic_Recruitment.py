# # #==================================# # #
# # # Episodic Recruitment Probability # # #
# # #==================================# # #

# Models the probability of recruitment of large woody debris as a result of episodic events such as avalanches
# or wildfires
# Version 0.1
# Created by Jordan Gilbert


import arcpy
from arcpy.sa import *
import os
import numpy as np
import NormalizedTWI
import RasterOverlap
import SegmentZS
import sys

def main(projectFolder, network, evh, evc, dem, valley, firePoly, bps, scratch):
    """"""

    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("spatial")

    # checks
    lf = arcpy.ListFields(network, "AREA")
    if len(lf) != 1:
        raise Exception("Network must contain field 'AREA'. Use individual probability output network.")

    # make sure datasets are projected

    # generate raster that is the overlap between bps lwd species and burned areas, convert to 1s and 0s
    fire_raster = fire_rasters(firePoly, bps, network, scratch)

    # summarize the above generated raster onto a table to be merged with network



def fire_rasters(firePoly, bps, network, scratch):
    """Identify areas where wildfire contributes to LWD recruitment"""

    # raster of fire polygon
    outds = scratch + "/temp_burn_raster.tif"
    cellsz = arcpy.Describe(bps).meanCellWidth
    # arcpy.env.extent = network
    arcpy.PolygonToRaster_conversion(firePoly, "FID", outds, cellsize=cellsz)
    burn_raster = scratch + "/burn_raster.tif"
    arcpy.CopyRaster_management(outds, burn_raster, nodata_value=225)
    arcpy.Delete_management(outds)

    # derive a potential lwd layer from landfire BpS
    lfevh = arcpy.ListFields(bps, "LWD")
    if len(lfevh) == 1:
        arcpy.DeleteField_management(bps, "LWD")
    arcpy.AddField_management(bps, "LWD", "SHORT")
    cursor = arcpy.da.UpdateCursor(bps, ["GROUPVEG", "LWD"])
    for row in cursor:
        if row[0] == "PerennialIce/Snow":
            row[1] = 0
        elif row[0] == "Barren-Rock/Sand/Clay":
            row[1] = 0
        elif row[0] == "Conifer":
            row[1] = 1
        elif row[0] == "Conifer-Hardwood":
            row[1] = 1
        elif row[0] == "Grassland":
            row[1] = 0
        elif row[0] == "Hardwood":
            row[1] = 1
        elif row[0] == "Hardwood-Conifer":
            row[1] = 1
        elif row[0] == "Peatland Forest":
            row[1] = 0
        elif row[0] == "Peatland non-forest":
            row[1] = 0
        elif row[0] == "Riparian":
            row[1] = 0
        elif row[0] == "Savanna":
            row[1] = 0
        elif row[0] == "Sparse":
            row[1] = 0
        else:
            row[1] = 0
        cursor.updateRow(row)
    del row
    del cursor

    bps_lookup = Lookup(bps, "LWD")
    buf_50 = scratch + "/buf_50.shp"
    arcpy.Buffer_analysis(network, buf_50, "50 Meters", "FULL", "ROUND", "ALL")
    bps_lwd_temp = ExtractByMask(bps_lookup, buf_50)
    bps_lwd_temp2 = scratch + "/bps_lwd_temp2.tif"
    arcpy.Clip_management(bps_lwd_temp, "", bps_lwd_temp2, burn_raster,
                          arcpy.Describe(bps).noDataValue, "", "MAINTAIN_EXTENT")

    bps_lwd_temp3 = SetNull(bps_lwd_temp2, bps_lwd_temp2, "VALUE = 0")

    if not os.path.exists(os.path.dirname(os.path.dirname(bps)) + "/BPS_LWD"):
        os.mkdir(os.path.dirname(os.path.dirname(bps)) + "/BPS_LWD")
    bps_lwd_raster = os.path.dirname(os.path.dirname(bps)) + "/BPS_LWD/bps_lwd.tif"
    arcpy.CopyRaster_management(bps_lwd_temp3, bps_lwd_raster, nodata_value=127)

    # raster overlap output and function
    if not os.path.exists(os.path.dirname(firePoly) + "/LWD_Burn"):
        os.mkdir(os.path.dirname(firePoly) + "/LWD_Burn")
    bps_burn_overlap = os.path.dirname(firePoly) + "/LWD_Burn/lwd_burn.tif"

    RasterOverlap.RasterOverlap(bps_lwd_raster, burn_raster, bps_burn_overlap)

    return bps_burn_overlap


def slideGullies(projectFolder, network, dem, valley, scratch):
    """"""

    # create a normalized twi raster
    twi_instance = NormalizedTWI.TWI(dem, valley, scratch)

    # make sure slope and twi rasters are orthogonal and reclassify them
    twi_raster = twi_instance.twi_output
    slope_raster = os.path.dirname(dem) + "/Slope/slope_deg.tif"

    arcpy.Clip_management(slope_raster, rectangle=None, out_raster=scratch + "/slope_clip.tif",
                          in_template_dataset=twi_raster,maintain_clipping_extent="MAINTAIN_EXTENT")

    slope_clip = Raster(scratch + "/slope_clip.tif")
    slope_final = Reclassify(slope_clip, "VALUE", "0 25 NODATA; 25 90 1")
    twi_final = Reclassify(twi_raster, "VALUE", RemapRange([[0, 3.4, "NODATA"], [3.4, 10, 1]]))

    ndval1 = arcpy.Describe(slope_final).noDataValue
    ndval2 = arcpy.Describe(twi_final).noDataValue
    arcpy.CopyRaster_management(slope_final, scratch + "/slope_in.tif", nodata_value=ndval1)
    arcpy.CopyRaster_management(twi_final, scratch + "/twi_in.tif", nodata_value=ndval2)

    # find the overlap between the slope and twi input rasters
    slope_in = scratch + "/slope_in.tif"
    twi_in = scratch + "/twi_in.tif"

    RasterOverlap.RasterOverlap(slope_in, twi_in, scratch + "/overlap_out.tif")

    # convert landslide raster output to prepared landslide polygons
    landslide_raster = Raster(scratch + "/overlap_out.tif")
    ls_raster = SetNull(landslide_raster, landslide_raster, "VALUE <> 1")

    ls_poly = scratch + "/ls_poly.shp"
    arcpy.RasterToPolygon_conversion(ls_raster, ls_poly, "SIMPLIFY")
    ag_poly = scratch + "/ag_poly.shp"
    arcpy.AggregatePolygons_cartography(ls_poly, ag_poly, 70, 2500)
    arcpy.Near_analysis(ag_poly, network)

    # generate output file
    if not os.path.exists(os.path.dirname(dem) + "/Gullies"):
        os.mkdir(os.path.dirname(dem) + "/Gullies")
    output = os.path.dirname(dem) + "/Gullies/slide_gullies.shp"

    arcpy.Dissolve_management(ag_poly, output, "NEAR_FID")
    arcpy.AddField_management(output, "area_sqm", "DOUBLE")
    arcpy.CalculateField_management(output, "area_sqm", "!SHAPE.AREA@SQUAREMETERS!", "PYTHON_9.3")
    arcpy.DeleteField_management(output, "NEAR_FID")
    arcpy.Near_analysis(output, network)

    if not os.path.exists(os.path.dirname(dem) + "/TWI"):
        os.mkdir(os.path.dirname(dem) + "/TWI")
    twi_raster.save(os.path.dirname(dem) + "/TWI/twi.tif")

    arcpy.Delete_management(slope_clip)
    arcpy.Delete_management(slope_in)
    arcpy.Delete_management(twi_in)
    arcpy.Delete_management(ls_poly)
    arcpy.Delete_management(ag_poly)
    arcpy.Delete_management(scratch + "/overlap_out.tif")
    arcpy.Delete_management(scratch + "/slope.tif")
    arcpy.Delete_management(scratch + "/twi_norm.tif")

    return output


def rasterToTable(network, raster, scratch):
    """Applies the overlap raster of bps lwd and burn areas to network after conducting zonal stats"""

    # make nodata values in raster 0s
    raster = Con(IsNull(raster), 0, raster)

    # raster resolution
    rwidth = arcpy.Describe(raster).meanCellWidth
    rheight = arcpy.Describe(raster).meanCellHeight
    resolution = rwidth * rheight

    # create arrays for fields in output network
    lengtharray = np.asarray(arcpy.da.FeatureClassToNumPyArray(network, "FID"), np.int16)

    oid = np.arange(0, len(lengtharray), 1)
    sum_l = []

    # apply functions to each segment of network to get desired output field values
    cursor = arcpy.da.SearchCursor(network, "SHAPE@")
    for row in cursor:
        sval = SegmentZS.segmentSum(row[0], raster, "50 Meters", scratch)

        sum_l.append(sval)

    del row
    del cursor

    # create array for proportion burned
    sum_a = np.asarray(sum_l, np.float32)
    burn_area = np.multiply(sum_a, resolution)

    columns = np.column_stack((oid, burn_area))
    out_table = scratch + "/burn_table.txt"
    np.savetxt(out_table, columns, delimiter=",", header="ID, BURN_AREA", comments="")

    return
