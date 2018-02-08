# # #======================# # #
# # # WRAT Project Builder # # #
# # #======================# # #

# Creates and populates the folder structure for a WRAT Project
# Version 0.1
# Created by Jordan Gilbert


# import modules
import os
import arcpy
import shutil
import sys
import string


def main(projectFolder, network, evh, evc, bankfull, dem, wildfire, bps, add_scratch):      # transportation or fragmented valley..?
    """Create a WRAT project folder and populate the inptus"""

    arcpy.env.overwriteOutput = True

    if not os.path.exists(projectFolder):
        os.mkdir(projectFolder)

    if os.getcwd() is not projectFolder:
        os.chdir(projectFolder)

    set_structure(projectFolder, add_scratch)

    # add network inputs to project
    in_network = network.split(";")
    os.chdir(projectFolder + "/01_Inputs/01_Network/")
    i = 1
    for x in range(len(in_network)):
        if not os.path.exists("Network_" + str(i)):
            os.mkdir("Network_" + str(i))
        arcpy.CopyFeatures_management(in_network[x], "Network_" + str(i) + "/" + os.path.basename(in_network[x]))
        i += 1

    # add veg height inputs to project
    in_evh = evh.split(";")
    os.chdir(projectFolder + "/01_Inputs/02_Veg_Height/")
    i = 1
    for x in range(len(in_evh)):
        if not os.path.exists("Veg_Height_" + str(i)):
            os.mkdir("Veg_Height_" + str(i))
        if not os.path.exists("Veg_Height_" + str(i) + "/" + os.path.basename(in_evh[x])):
            src = string.replace(in_evh[x], "'", "")
            shutil.copytree(src, "Veg_Height_" + str(i) + "/" + os.path.basename(in_evh[x]))
        i += 1

    # add veg cover inputs to project
    in_evc = evc.split(";")
    os.chdir(projectFolder + "/01_Inputs/03_Veg_Cover/")
    i = 1
    for x in range(len(in_evc)):
        if not os.path.exists("Veg_Cover_" + str(i)):
            os.mkdir("Veg_Cover_" + str(i))
        if not os.path.exists("Veg_Cover_" + str(i) + "/" + os.path.basename(in_evc[x])):
            src = string.replace(in_evc[x], "'", "")
            shutil.copytree(src, "Veg_Cover_" + str(i) + "/" + os.path.basename(in_evc[x]))
        i += 1

    # add bankfull channel inputs to project
    in_bankfull = bankfull.split(";")
    os.chdir(projectFolder + "/01_Inputs/04_Bankfull_Channel/")
    i = 1
    for x in range(len(in_bankfull)):
        if not os.path.exists("Bankfull_" + str(i)):
            os.mkdir("Bankfull_" + str(i))
        arcpy.CopyFeatures_management(in_bankfull[x], "Bankfull_" + str(i) + "/" + os.path.basename(in_bankfull[x]))
        i += 1

    # add dem inputs to project
    in_dem = dem.split(";")
    os.chdir(projectFolder + "/01_Inputs/05_Topo/")
    i = 1
    for x in range(len(in_dem)):
        if not os.path.exists("DEM_" + str(i)):
            os.mkdir("DEM_" + str(i))
        arcpy.CopyRaster_management(in_dem[x], "DEM_" + str(i) + "/" + os.path.basename(in_dem[x]))
        i += 1

    # add wildfire polygons to project
    in_wildfire = wildfire.split(";")
    os.chdir(projectFolder + "/01_Inputs/06_Wildfire/")
    i = 1
    for x in range(len(in_wildfire)):
        if not os.path.exists("Wildfire_" + str(i)):
            os.mkdir("Wildfire_" + str(i))
        arcpy.CopyFeatures_management(in_wildfire[x], "Wildfire_" + str(i) + "/" + os.path.basename(in_wildfire[x]))
        i += 1

    # add historic veg inputs to project
    in_bps = bps.split(";")
    os.chdir(projectFolder + "/01_Inputs/07_Historic_Veg/")
    i = 1
    for x in range(len(in_bps)):
        if not os.path.exists("Historic_Veg_" + str(i)):
            os.mkdir("Historic_Veg_" + str(i))
        if not os.path.exists("Historic_Veg_" + str(i) + "/" + os.path.basename(in_bps[x])):
            src = string.replace(in_bps[x], "'", "")
            shutil.copytree(src, "Historic_Veg_" + str(i) + "/" + os.path.basename(in_bps[x]))
        i += 1


def set_structure(projectFolder, add_scratch):
    """Builds the project folder structure"""

    if os.getcwd() is not projectFolder:
        os.chdir(projectFolder)

    if add_scratch == "true":
        os.mkdir(projectFolder + "/scratch")

    if not os.path.exists("01_Inputs"):
        os.mkdir("01_Inputs")
    if not os.path.exists("02_Analyses"):
        os.mkdir("02_Analyses")
    os.chdir("01_Inputs")
    if not os.path.exists("01_Network"):
        os.mkdir("01_Network")
    if not os.path.exists("02_Veg_Height"):
        os.mkdir("02_Veg_Height")
    if not os.path.exists("03_Veg_Cover"):
        os.mkdir("03_Veg_Cover")
    if not os.path.exists("04_Bankfull_Channel"):
        os.mkdir("04_Bankfull_Channel")
    if not os.path.exists("05_Topo"):
        os.mkdir("05_Topo")
    if not os.path.exists("06_Wildfire"):
        os.mkdir("06_Wildfire")
    if not os.path.exists("07_Historic_Veg"):
        os.mkdir("07_Historic_Veg")


if __name__ == '__main__':
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5],
        sys.argv[6],
        sys.argv[7],
        sys.argv[8],
        sys.argv[9])
