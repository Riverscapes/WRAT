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
from pygeoprocessing.routing import *
import numpy as np
import RasterOverlap
import sys

def main(network, evh, evc, dem, firePoly, bps, scratch):
    """"""

    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("spatial")

    # checks
    lf = arcpy.ListFields(network, "AREA")
    if len(lf) != 1:
        raise Exception("Network must contain field 'AREA'. Use individual probability output network.")

    # make sure datasets are projected
    fireSR = arcpy.Describe(firePoly).spatialReference
    if fireSR.type != "Projected":
        raise Exception("Input wildfire polygon must have a projected coordinate system")

    # create thiessen polygons for analyses
    midpoints = scratch + "/midpoints.shp"
    arcpy.FeatureVerticesToPoints_management(network, midpoints, "MID")
    thiessen = scratch + "/thiessen.shp"
    arcpy.CreateThiessenPolygons_analysis(midpoints, thiessen)
    buf_50 = scratch + "/buf_50.shp"
    arcpy.Buffer_analysis(network, buf_50, "50 Meters", "", "FLAT")
    thiessen_buf = scratch + "/thiessen_buf.shp"
    arcpy.Clip_analysis(thiessen, buf_50, thiessen_buf)

    # generate raster that is the overlap between bps lwd species and burned areas, convert to 1s and 0s
    arcpy.AddMessage("fire raster")
    fire_raster = fire_rasters(firePoly, bps, thiessen_buf, scratch)

    # summarize the above generated raster onto a table to be merged with network
    arcpy.AddMessage("fire raster to table")
    rasterToTable(network, fire_raster, thiessen_buf)

    arcpy.AddField_management(network, "BURN_PROP", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(network, ["BURN_AREA", "AREA", "BURN_PROP"])
    for row in cursor:
        row[2] = row[0] / row[1]
        cursor.updateRow(row)
        if row[2] > 1:
            row[2] = 1
        cursor.updateRow(row)
    del row
    del cursor

    # identify slide gullies
    arcpy.AddMessage("gullies")
    slideGullies(dem, network, scratch)

    # get stats within the gullies
    arcpy.AddMessage("gully stats")
    gullies = os.path.dirname(dem) + "/Gullies/slide_gullies.shp"
    height = os.path.dirname(os.path.dirname(evh)) + "/Height_Rasters/total_height.tif"
    cover = os.path.dirname(os.path.dirname(evc)) + "/Cover/total_cover.tif"
    gulliesSum(gullies, height, cover, scratch)

    # merge table onto network
    arcpy.AddMessage("merge gully table")
    gully_table = scratch + "/gully_table.txt"
    gully_table_out = scratch + "/gully_table_out.dbf"
    arcpy.CopyRows_management(gully_table, gully_table_out)
    arcpy.JoinField_management(network, "FID", gully_table_out, "ID", "GULLIES")

    arcpy.CheckInExtension('spatial')

    return


def fire_rasters(firePoly, bps, thiessen_buf, scratch):
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
    bps_lwd_temp = ExtractByMask(bps_lookup, thiessen_buf)
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


def rasterToTable(network, raster, thiessen_buf):
    """Applies the overlap raster of bps lwd and burn areas to network after conducting zonal stats"""

    # make nodata values in raster 0s
    raster = Con(IsNull(raster), 0, raster)

    # raster resolution
    rwidth = arcpy.Describe(raster).meanCellWidth
    rheight = arcpy.Describe(raster).meanCellHeight
    resolution = rwidth * rheight

    # zonal stats
    burn_sum_t = ZonalStatisticsAsTable(thiessen_buf, "Input_FID", raster, "burn_sum_t", statistics_type="SUM")
    arcpy.AddField_management(burn_sum_t, "BURN_AREA", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(burn_sum_t, ["SUM", "BURN_AREA"])
    for row in cursor:
        row[1] = row[0] * resolution
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.JoinField_management(network, "FID", burn_sum_t, "Input_FID", "BURN_AREA")

    return


def slideGullies(dem, network, scratch):
    """"""

    # find input DEM resolution
    cellHeight = arcpy.Describe(dem).meanCellHeight
    cellWidth = arcpy.Describe(dem).meanCellWidth
    resolution = cellHeight * cellWidth
    ndvalue = arcpy.Describe(dem).noDataValue

    # derive d-infinity flow accumulation raster from DEM
    filledDEM = Fill(dem)
    arcpy.CopyRaster_management(filledDEM, scratch + "/fill.tif", nodata_value=ndvalue)

    fill = scratch + "/fill.tif"
    fd = scratch + "/fd.tif"
    fa = scratch + "/fa.tif"

    flow_direction_d_inf(fill, fd)
    flow_accumulation(fd, fill, fa)

    # convert the flow accumulation raster into drainage area raster
    fa = Raster(scratch + "/fa.tif")
    dr_area = fa * resolution / 1000000
    if not os.path.exists(os.path.dirname(dem) + "/Flow"):
        os.mkdir(os.path.dirname(dem) + "/Flow")
    dr_area.save(os.path.dirname(dem) + "/Flow/DrainArea_sqkm.tif")

    # find slope
    slope_deg = Slope(dem, "DEGREE")

    if not os.path.exists(os.path.dirname(dem) + "/Slope"):
        os.mkdir(os.path.dirname(dem) + "/Slope")
    arcpy.CopyRaster_management(slope_deg, os.path.dirname(dem) + "/Slope/slope_deg.tif",
                                nodata_value=arcpy.Describe(dem).noDataValue)

    # reclassify dr area and slope to threshold values
    dr_area_thresh = Reclassify(dr_area, "VALUE", "0 0.045 NODATA; 0.045 100000 1")
    slope_thresh = Reclassify(slope_deg, "VALUE", "0 20 NODATA; 20 90 1")
    arcpy.CopyRaster_management(dr_area_thresh, scratch + "/dr_area_thresh.tif", nodata_value=-128)
    arcpy.CopyRaster_management(slope_thresh, scratch + "/slope_thresh.tif", nodata_value=-128)

    # clip to extent of whichever is smaller (always same from same DEM?) might also need to get rid of VBs here

    # find overlap
    in1 = scratch + "/dr_area_thresh.tif"
    in2 = scratch + "/slope_thresh.tif"
    RasterOverlap.RasterOverlap(in1, in2, scratch + "/overlap.tif")

    # convert landslide raster output to prepared landslide polygons
    landslide_raster = Raster(scratch + "/overlap.tif")
    ls_raster = SetNull(landslide_raster, landslide_raster, "VALUE <> 1")

    ls_poly = scratch + "/ls_poly.shp"
    arcpy.RasterToPolygon_conversion(ls_raster, ls_poly, "SIMPLIFY")
    ag_poly = scratch + "/ag_poly.shp"
    arcpy.AggregatePolygons_cartography(ls_poly, ag_poly, 70, 5000)
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

    return output

def gulliesSum(gullies, height, cover, scratch):
    """Stats for the variables within the slide gullies"""

    arcpy.MakeFeatureLayer_management(gullies, "gullies_lyr")
    arcpy.SelectLayerByAttribute_management("gullies_lyr", "NEW_SELECTION", '"NEAR_DIST" <= 250')
    final_gullies = scratch + "/final_gullies.shp"
    arcpy.CopyFeatures_management("gullies_lyr", final_gullies)

    height_t = ZonalStatisticsAsTable(final_gullies, "NEAR_FID", height, "height_t", statistics_type="MEAN")
    arcpy.JoinField_management(final_gullies, "NEAR_FID", height_t, "NEAR_FID", "MEAN")
    arcpy.AddField_management(final_gullies, "VH_MEAN", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(final_gullies, ["MEAN", "VH_MEAN"])
    for row in cursor:
        row[1] = row[0]
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(final_gullies, "MEAN")

    cover_t = ZonalStatisticsAsTable(final_gullies, "NEAR_FID", cover, "cover_t", statistics_type="MEAN")
    arcpy.JoinField_management(final_gullies, "NEAR_FID", cover_t, "NEAR_FID", "MEAN")
    arcpy.AddField_management(final_gullies, "VC_MEAN", "DOUBLE")
    cursor = arcpy.da.UpdateCursor(final_gullies, ["MEAN", "VC_MEAN"])
    for row in cursor:
        row[1] = row[0]
        cursor.updateRow(row)
    del row
    del cursor
    arcpy.DeleteField_management(final_gullies, "MEAN")

    area_array = np.asarray(arcpy.da.FeatureClassToNumPyArray(final_gullies, "area_sqm"), np.float32)
    area_norm = (area_array - area_array.min())/(area_array.max() - area_array.min())

    dist_array = np.asarray(arcpy.da.FeatureClassToNumPyArray(final_gullies, "NEAR_DIST"), np.float32)
    dist_norm = (dist_array - dist_array.min())/(dist_array.max() - dist_array.min())

    vh_array = np.asarray(arcpy.da.FeatureClassToNumPyArray(final_gullies, "VC_MEAN"), np.float32)
    vh_norm = (vh_array - vh_array.min())/(vh_array.max() - vh_array.min())

    vc_array = np.asarray(arcpy.da.FeatureClassToNumPyArray(final_gullies, "VC_MEAN"), np.float32)
    vc_norm = (vc_array - vc_array.min())/(vc_array.max() - vc_array.min())

    final_a = (area_norm + dist_norm + vh_norm + vc_norm) / 4

    near_fid_a = np.asarray(arcpy.da.FeatureClassToNumPyArray(final_gullies, "NEAR_FID"), np.int32)

    columns = np.column_stack((near_fid_a, final_a))
    out_table = scratch + "/gully_table.txt"
    np.savetxt(out_table, columns, delimiter=",", header="ID, GULLIES", comments="")

    return


if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6],
        sys.argv[7])