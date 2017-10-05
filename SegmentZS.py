# # # This module is used to extract values from rasters to line segments # # #
# # # on a segment by segment basis                                       # # #


import arcpy
from arcpy.sa import *


def segmentSum(feature, raster, buf_size, temp):
    """Calculates the sum of a raster within a feature zone"""
    arcpy.env.scratchWorkspace = temp
    cell_size = arcpy.Describe(raster).meanCellWidth
    buf = temp + "/buf.shp"
    arcpy.Buffer_analysis(feature, buf, buf_size, "FULL", "FLAT", "")
    buf_raster = temp + "/buf_raster.tif"
    arcpy.PolygonToRaster_conversion(buf, "ORIG_FID", buf_raster, "", "", cell_size)
    table = temp + "/zs_sum.dbf"
    ZonalStatisticsAsTable(buf_raster, "VALUE", raster, table, "DATA", "SUM")

    sumcursor = arcpy.da.SearchCursor(table, "SUM")
    for row in sumcursor:
        sum_value = row[0]

    del row
    del sumcursor

    arcpy.Delete_management(buf_raster)

    return sum_value


def segmentArea(feature, buf_size, temp):
    """Calculates the area for each feature zone"""
    arcpy.env.scratchWorkspace = temp
    buf = temp + "/buf.shp"
    arcpy.Buffer_analysis(feature, buf, buf_size, "FULL", "FLAT", "")

    arcpy.AddField_management(buf, "Area_sqm", "DOUBLE")
    arcpy.CalculateField_management(buf, "Area_sqm", "!SHAPE.AREA@SQUAREMETERS!", "PYTHON_9.3")

    areacursor = arcpy.da.SearchCursor(buf, "Area_sqm")
    for row in areacursor:
        area_value = row[0]

    del row
    del areacursor

    return area_value

