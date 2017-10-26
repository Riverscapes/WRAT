# # # Create a topographic wetness index from an input DEM # # #

import os
import arcpy
from arcpy.sa import *
from pygeoprocessing.routing import *


class TWI:
    """This class creates a normalized (1 - 10) topographic wetness index (TWI) raster
    dataset using an input DEM and a valley bottom polygon"""

    def __init__(self, dem, valley, scratch):
        self.dem = dem
        self.valley = valley
        self.scratch = scratch
        self.da_input = self.drainarea(self.dem, self.scratch)
        self.slope_input = self.slope(self.dem, self.scratch)

        self.twi_output = self.twi(self.da_input, self.slope_input, self.valley, self.scratch)

    def drainarea(self, dem, scratch):
        """Calculates the drainage area in square km from input DEM"""

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

        return dr_area

    def slope(self, dem, scratch):
        """Calculates the slope in radians with no 0 values from input DEM"""

        slope_deg = Slope(dem, "DEGREE")
        tan_rad = Tan((slope_deg * 1.570796) / 90)
        slope = Con(tan_rad== 0.0001, tan_rad)
        # arcpy.CopyRaster_management(slope_deg, )

        return slope

    if __name__ == '__main__':
        def twi(self, da, slope, valley, scratch):
            """Uses the calculated drainage area and slope to derive a normalized TWI raster """

            # calculate twi, remove values that are within the valley bottom, then normalize from 1 to 10
            ti_init = Ln(da / slope)
            ti_network = ExtractByMask(ti_init, valley)
            ti150 = Con(ti_network, 150)
            tireclass = Reclassify(ti150, "VALUE", "150 150; NODATA 0")
            titemp = ti_init + tireclass
            tinonnorm = SetNull(titemp, titemp, "VALUE>100")
            ti_norm = 1 + (tinonnorm - tinonnorm.minimum) * 9 / (tinonnorm.maximum - tinonnorm.minimum)
            # there was a line here to save the output to the scratch..

            return ti_norm

