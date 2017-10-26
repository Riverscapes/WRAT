# # # Creates a single value raster that represents the overlap between two input rasters # # #

# the twi and slope input rasters must be concurrent and orthongonal

from osgeo import gdal
import numpy as np


class RasterOverlap:
    """This class takes two input rasters and creates an output raster that represents
        the overlap between the twi inputs"""

    def __init__(self, raster1, raster2, output):
        self.in1 = raster1
        self.in2 = raster2
        self.out = output
        self.findOverlap()

    def findOverlap(self):
        # read input rasters, create output raster and apply to funtion to populate it
        in1DS = gdal.Open(self.in1)
        in2DS = gdal.Open(self.in2)
        nodatavalue = in1DS.GetRasterBand(1).GetNoDataValue()
        nodatavalue2 = in2DS.GetRasterBand(1).GetNoDataValue()
        driver = gdal.GetDriverByName('GTiff')
        outDS = driver.Create(self.out, in1DS.RasterXSize, in1DS.RasterYSize, 1, gdal.GDT_Int16)
        outDS.SetProjection(in1DS.GetProjection())
        outDS.SetGeoTransform(in1DS.GetGeoTransform())
        outDS.GetRasterBand(1).SetNoDataValue(nodatavalue)

        overlap_func = np.vectorize(self.func)

        for i in range(in1DS.RasterYSize):
            array1 = in1DS.GetRasterBand(1).ReadAsArray(0, i, in1DS.RasterXSize, 1)
            array2 = in2DS.GetRasterBand(1).ReadAsArray(0, i, in2DS.RasterXSize, 1)
            result = overlap_func(array1, array2, nodatavalue, nodatavalue2)
            outDS.GetRasterBand(1).WriteArray(result, 0, i)

        return outDS

    def func(self, in1, in2, nodata, nodata2):
        # simple function returns 1 if there is overlap between two raster inputs and nodata if there is no overlap
        if (in1 != nodata and in1 != nodata2) and (in2 != nodata and in2 != nodata2):
            return 1
        else:
            return nodata