import arcpy
import WRATProject
import Individual_Recruitment
import Episodic_Recruitment
import Episodic_Recruitment2


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Wood Recruitment and Transport"
        self.alias = "Wood Recruitment and Trasnport"

        # List of tool classes associated with this toolbox
        self.tools = [WRATBuilder, Individual_Tool, Episodic_Tool, Episodic_Tool2]


class WRATBuilder(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1 Build WRAT Project"
        self.description = "Sets up a WRAT project folder and defines the inputs"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select Project Folder",
            name="projectFolder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Segmented Stream Network",
            name="network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        param1.filter.list = ["Polyline"]

        param2 = arcpy.Parameter(
            displayName="LANDFIRE EVH Layer",
            name="evh",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param3 = arcpy.Parameter(
            displayName="LANDFIRE EVC Layer",
            name="evc",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param4 = arcpy.Parameter(
            displayName="Bankfull Channel Polygon",
            name="bankfull",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        param4.filter.list = ["Polygon"]

        param5 = arcpy.Parameter(
            displayName="DEM",
            name="dem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param6 = arcpy.Parameter(
            displayName="Wildfire Polygons",
            name="wildfire",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        param6.filter.list = ["Polygon"]

        param7 = arcpy.Parameter(
            displayName="LANDFIRE BpS Layer",
            name="bps",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        param8 = arcpy.Parameter(
            displayName="Add Scratch Folder to Project",
            name="add_scratch",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""

        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(WRATProject)
        WRATProject.main(p[0].valueAsText,
                         p[1].valueAsText,
                         p[2].valueAsText,
                         p[3].valueAsText,
                         p[4].valueAsText,
                         p[5].valueAsText,
                         p[6].valueAsText,
                         p[7].valueAsText,
                         p[8].valueAsText)
        return


class Individual_Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2 Probability of Recruitment (Individual)"
        self.description = "Models LWD recruitment probability based on individual mortality"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Select Project Folder",
            name="projectFolder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param01 = arcpy.Parameter(
            displayName="Project Name",
            name="projName",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param02 = arcpy.Parameter(
            displayName="Watershed HUC ID",
            name="hucID",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        param03 = arcpy.Parameter(
            displayName="Watershed Name",
            name="hucName",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Segmented Stream Network",
            name="network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1.filter.list = ["Polyline"]

        param2 = arcpy.Parameter(
            displayName="LANDFIRE EVH Layer",
            name="evh",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="LANDFIRE EVC Layer",
            name="evc",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Bankfull Channel Polygon",
            name="bankfull",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param4.filter.list = ["Polygon"]

        param5 = arcpy.Parameter(
            displayName="DEM",
            name="dem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param6 = arcpy.Parameter(
            displayName="Select Scratch Folder",
            name="scratch",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        return [param0, param01, param02, param03, param1, param2, param3, param4, param5, param6]

    def isLicensed(self):
        """Set whether tool is license to execute."""
        return True

    def updateParamters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(Individual_Recruitment)
        Individual_Recruitment.main(p[0].valueAsText,
                                    p[1].valueAsText,
                                    p[2].valueAsText,
                                    p[3].valueAsText,
                                    p[4].valueAsText,
                                    p[5].valueAsText,
                                    p[6].valueAsText,
                                    p[7].valueAsText,
                                    p[8].valueAsText,
                                    p[9].valueAsText)
        return


class Episodic_Tool(object):
    def __init__(self):
        """Define the tool name (tool name is the name of the class)."""
        self.label = "3 Probability of Recruitment(Episodic)"
        self.description = "Models LWD recruitment probability based on fire disturbance and slides"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define paraameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Individual Probability Output Stream Network",
            name="network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["Polyline"]

        param1 = arcpy.Parameter(
            displayName="LANDFIRE EVH Layer",
            name="evh",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="LANDFIRE EVC Layer",
            name="evc",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="DEM",
            name="dem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Valley Bottom Polygon",
            name="valley",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param4.filter.list = ["Polygon"]

        param5 = arcpy.Parameter(
            displayName="Wildfire Polygon",
            name="firePoly",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param5.filter.list = ["Polygon"]

        param6 = arcpy.Parameter(
            displayName="LANDFIRE BpS Layer",
            name="bps",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param7 = arcpy.Parameter(
            displayName="Scratch Folder",
            name="scratch",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        return [param0, param1, param2, param3, param4, param5, param6, param7]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(Episodic_Recruitment)
        Episodic_Recruitment.main(p[0].valueAsText,
                                  p[1].valueAsText,
                                  p[2].valueAsText,
                                  p[3].valueAsText,
                                  p[4].valueAsText,
                                  p[5].valueAsText,
                                  p[6].valueAsText,
                                  p[7].valueAsText)
        return


class Episodic_Tool2(object):
    def __init__(self):
        """Define the tool name (tool name is the name of the class)."""
        self.label = "3 Probability of Recruitment(Episodic2)"
        self.description = "Models LWD recruitment probability based on fire disturbance and slides"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define paraameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Individual Probability Output Stream Network",
            name="network",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["Polyline"]

        param1 = arcpy.Parameter(
            displayName="LANDFIRE EVH Layer",
            name="evh",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="LANDFIRE EVC Layer",
            name="evc",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="DEM",
            name="dem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param5 = arcpy.Parameter(
            displayName="Wildfire Polygon",
            name="firePoly",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param5.filter.list = ["Polygon"]

        param6 = arcpy.Parameter(
            displayName="LANDFIRE BpS Layer",
            name="bps",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param7 = arcpy.Parameter(
            displayName="Scratch Folder",
            name="scratch",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        return [param0, param1, param2, param3, param5, param6, param7]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(Episodic_Recruitment2)
        Episodic_Recruitment2.main(p[0].valueAsText,
                                  p[1].valueAsText,
                                  p[2].valueAsText,
                                  p[3].valueAsText,
                                  p[4].valueAsText,
                                  p[5].valueAsText,
                                  p[6].valueAsText)
        return