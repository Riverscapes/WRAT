import xml, os
import uuid
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import string

class ProjectXML:
    """creates an instance of a project xml file"""

    def __init__(self, filepath, projType, name):
        self.logFilePath = filepath

        # Initialize the tree
        self.projectTree = ET.ElementTree(ET.Element("Project"))
        self.project = self.projectTree.getroot()

        # Set up a root Project node
        self.project.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.project.set("xsi:noNamespaceSchemaLocation", "https://raw.githubusercontent.com/Riverscapes/Program/master/Project/XSD/V1/Project.xsd")

        # Set up the <Name> and <ProjectType> tags
        self.name = ET.SubElement(self.project, "Name")
        self.name.text = name
        self.projectType = ET.SubElement(self.project, "ProjectType")
        self.projectType.text = projType

        # Add some containers we will fill out later
        self.meta = ET.SubElement(self.project, "MetaData")
        self.Inputs = ET.SubElement(self.project, "Inputs")
        self.realizations = ET.SubElement(self.project, "Realizations")
        self.WRATrealizations = []

    def addMeta(self, name, value, parentNode):
        """adds metadata tags to the project xml document"""
        metaNode = parentNode.find("MetaData")
        if metaNode is None:
            metaNode = ET.SubElement(parentNode, "MetaData")

        node = ET.SubElement(metaNode, "Meta")
        node.set("name", name)
        node.text = str(value)

    def addProjectInput(self, itype, name, path, project="", iid="", guid="", ref=""):
        typeNode = ET.SubElement(self.Inputs, itype)
        if iid is not "":
            typeNode.set("id", iid)
        if guid is not "":
            typeNode.set("guid", guid)
        if ref is not "":
            typeNode.set("ref", ref)
        nameNode = ET.SubElement(typeNode, "Name")
        nameNode.text = str(name)
        pathNode = ET.SubElement(typeNode, "Path")
        pathNode.text = str(path)
        if project is not "":
            projectNode = ET.SubElement(typeNode, "Project")
            projectNode.text = str(project)

    def addWRATInput(self, parentNode, type, name="", path="", project="", iid="", guid="", ref=""):
        """adds input tags to the project xml document"""
        inputsNode = parentNode.find("Inputs")
        if inputsNode is None:
            inputsNode = ET.SubElement(parentNode, "Inputs")
        if type == "Network":
            dnNode = inputsNode.find("DrainageNetworks")
            if dnNode is None:
                dnNode = ET.SubElement(inputsNode, "DrainageNetworks")
            networkNode = ET.SubElement(dnNode, "Network")
            if name is not "":
                nameNode = ET.SubElement(networkNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(networkNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(networkNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                networkNode.set("id", iid)
            if guid is not "":
                networkNode.set("guid", guid)
            if ref is not "":
                networkNode.set("ref", ref)
        if type == "Vegetation Height":
            heightNode = inputsNode.find("VegetationHeight")
            if heightNode is None:
                heightNode = ET.SubElement(inputsNode, "VegetationHeight")
            if name is not "":
                nameNode = ET.SubElement(heightNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(heightNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(heightNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                heightNode.set("id", iid)
            if guid is not "":
                heightNode.set("guid", guid)
            if ref is not "":
                heightNode.set("ref", ref)
        if type == "Vegetation Cover":
            coverNode = inputsNode.find("VegetationCover")
            if coverNode is None:
                coverNode = ET.SubElement(inputsNode, "VegetationCover")
            if name is not "":
                nameNode = ET.SubElement(coverNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(coverNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(coverNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                coverNode.set("id", iid)
            if guid is not "":
                coverNode.set("guid", guid)
            if ref is not "":
                coverNode.set("ref", ref)
        if type == "Bankfull Channel":
            bfNode = inputsNode.find("BankfullChannel")
            if bfNode is None:
                bfNode = ET.SubElement(inputsNode, "BankfullChannel")
            if name is not "":
                nameNode = ET.SubElement(bfNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(bfNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(bfNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                bfNode.set("id", iid)
            if guid is not "":
                bfNode.set("guid", guid)
            if ref is not "":
                bfNode.set("ref", ref)
        if type == "DEM":
            topoNode = inputsNode.find("Topography")
            if topoNode is None:
                topoNode = ET.SubElement(inputsNode, "Topography")
            demNode = ET.SubElement(topoNode, "DEM")
            if name is not "":
                nameNode = ET.SubElement(demNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(demNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(demNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                demNode.set("id", iid)
            if guid is not "":
                demNode.set("guid", guid)
            if ref is not "":
                demNode.set("ref", ref)
        if type == "Valley":
            vbNode = inputsNode.find("ValleyBottom")
            if vbNode is None:
                vbNode = ET.SubElement(inputsNode, "ValleyBottom")
            if name is not "":
                nameNode = ET.SubElement(vbNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(vbNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(vbNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                vbNode.set("id", iid)
            if guid is not "":
                vbNode.set("guid", guid)
            if ref is not "":
                vbNode.set("ref", ref)
        if type == "Wildfire":
            fireNode = inputsNode.find("Wildfire")
            if fireNode is None:
                fireNode = ET.SubElement(inputsNode, "Wildfire")
            if name is not "":
                nameNode = ET.SubElement(fireNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(fireNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(fireNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                fireNode.set("id", iid)
            if guid is not "":
                fireNode.set("guid", guid)
            if ref is not "":
                fireNode.set("ref", ref)
        if type == "Historic Vegetation":
            histNode = inputsNode.find("HistoricVegetation")
            if histNode is None:
                histNode = ET.SubElement(inputsNode, "HistoricVegetation")
            if name is not "":
                nameNode = ET.SubElement(histNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(histNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(histNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                histNode.set("id", iid)
            if guid is not "":
                histNode.set("guid", guid)
            if ref is not "":
                histNode.set("ref", ref)
        if type == "Height Raster":
            heightNode = inputsNode.Find("VegetationHeight")
            if heightNode is None:
                heightNode = ET.SubElement(inputsNode, "VegetationHeight")
            htrNode = heightNode.find("HeightRasters")
            if htrNode is None:
                htrNode = ET.SubElement(heightNode, "HeightRasters")
            rasterNode = ET.SubElement(htrNode, "Raster")
            if name is not "":
                nameNode = ET.SubElement(rasterNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(rasterNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(rasterNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                rasterNode.set("id", iid)
            if guid is not "":
                rasterNode.set("guid", guid)
            if ref is not "":
                rasterNode.set("ref", ref)
        if type == "Cover Rasters":
            coverNode = inputsNode.find("VegetationCover")
            if coverNode is None:
                coverNode = ET.SubElement(inputsNode, "VegetationCover")
            cvrNode = coverNode.find("CoverRasters")
            if cvrNode is None:
                cvrNode = ET.SubElement(coverNode, "CoverRasters")
            rasterNode = ET.SubElement(cvrNode, "Raster")
            if name is not "":
                nameNode = ET.SubElement(rasterNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(rasterNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(rasterNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                rasterNode.set("id", iid)
            if guid is not "":
                rasterNode.set("guid", guid)
            if ref is not "":
                rasterNode.set("ref", ref)
        if type == "Flow":
            topoNode = inputsNode.find("Topography")
            if topoNode is None:
                topoNode = ET.SubElement(inputsNode, "Topography")
            flowNode = ET.SubElement(topoNode, "Flow")
            if name is not "":
                nameNode = ET.SubElement(flowNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(flowNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(flowNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                flowNode.set("id", iid)
            if guid is not "":
                flowNode.set("guid", guid)
            if ref is not "":
                flowNode.set("ref", ref)
        if type == "Slope":
            topoNode = inputsNode.find("Topography")
            if topoNode is None:
                topoNode = ET.SubElement(inputsNode, "Topography")
            slopeNode = ET.SubElement(topoNode, "Slope")
            if name is not "":
                nameNode = ET.SubElement(slopeNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(slopeNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(slopeNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                slopeNode.set("id", iid)
            if guid is not "":
                slopeNode.set("guid", guid)
            if ref is not "":
                slopeNode.set("ref", ref)
        if type == "Gullies":
            topoNode = inputsNode.find("Topography")
            if topoNode is None:
                topoNode = ET.SubElement(inputsNode, "Topography")
            gulliesNode = topoNode.find("Gullies")
            if gulliesNode is None:
                gulliesNode = ET.SubElement(topoNode, "Gullies")
            vectorNode = ET.SubElement(gulliesNode, "Vector")
            if name is not "":
                nameNode = ET.SubElement(vectorNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(vectorNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(vectorNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                vectorNode.set("id", iid)
            if guid is not "":
                vectorNode.set("guid", guid)
            if ref is not "":
                vectorNode.set("ref", ref)
        if type == "LWD Burns":
            fireNode = inputsNode.find("Wildfire")
            if fireNode is None:
                fireNode = ET.SubElement(inputsNode, "Wildfire")
            lwdbNode = fireNode.find("LWDBurns")
            if lwdbNode is None:
                lwdbNode = ET.SubElement(fireNode, "LWDBurns")
            rasterNode = ET.SubElement(lwdbNode, "Raster")
            if name is not "":
                nameNode = ET.SubElement(rasterNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(rasterNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(rasterNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                rasterNode.set("id", iid)
            if guid is not "":
                rasterNode.set("guid", guid)
            if ref is not "":
                rasterNode.set("ref", ref)
        if type == "Historic LWD":
            histNode = inputsNode.find("HistoricVegetation")
            if histNode is None:
                histNode = ET.SubElement(inputsNode, "HistoricVegetation")
            histrNode = histNode.find("HistoricRasters")
            if histrNode is None:
                histrNode = ET.SubElement(histNode, "HistoricRasters")
            rasterNode = ET.SubElement(histrNode, "Raster")
            if name is not "":
                nameNode = ET.SubElement(rasterNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(rasterNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(rasterNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                rasterNode.set("id", iid)
            if guid is not "":
                rasterNode.set("guid", guid)
            if ref is not "":
                rasterNode.set("ref", ref)

    def addParameter(self, name, value, parentNode):
        """adds parameter tags to the project xml document"""
        paramNode = parentNode.find("Parameters")
        if paramNode is None:
            paramNode = ET.SubElement(paramNode, "Parameters")

        node = ET.SubElement(paramNode, "Param")
        node.set("name", name)
        node.text = str(value)

    def addOutput(self, aname, otype, name, path, parentNode, project="", oid="", guid="", ref=""):
        """adds an output tag to an analysis tag in the project xml document"""
        analysesNode = parentNode.find("Analyses")
        if analysesNode is None:
            analysesNode = ET.SubElement(parentNode, "Analyses")
        analysisNode = analysesNode.find("Analysis")
        if analysisNode is None:
            analysisNode = ET.SubElement(analysesNode, "Analysis")
            ET.SubElement(analysisNode, "Name").text = str(aname)
        outputsNode = analysisNode.find("Outputs")
        if outputsNode is None:
            outputsNode = ET.SubElement(analysisNode, "Outputs")

        typeNode = ET.SubElement(outputsNode, otype)
        if oid is not "":
            typeNode.set("id", oid)
        if guid is not "":
            typeNode.set("guid", guid)
        if ref is not "":
            typeNode.set("ref", ref)
        nameNode = ET.SubElement(typeNode, "Name")
        nameNode.text = str(name)
        pathNode = ET.SubElement(typeNode, "Path")
        pathNode.text = str(path)

        if project is not "":
            projectNode = ET.SubElement(typeNode, "Project")
            projectNode.text = str(project)

    def addWRATRealization(self, name, rid="", promoted="", dateCreated="", productVersion="", guid=""):
        """adds a WRAT realization tag to the project xml document"""
        node = ET.SubElement(self.realizations, "WRAT")
        if rid is not "":
            node.set("id", rid)
        if promoted is not "":
            node.set("promoted", promoted)
        if dateCreated is not "":
            node.set("dateCreated", dateCreated)
        if productVersion is not "":
            node.set("productVersion", productVersion)
        if guid is not "":
            node.set("guid", guid)
        nameNode = ET.SubElement(node, "Name")
        nameNode.text = str(name)
        self.WRATrealizations.append(node)

    def write(self):
        """
        Return a pretty-printed XML string for the Element.
        Then write it out to the expected file.
        """
        rough_string = ET.tostring(self.project, encoding='utf-8', method='xml')
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="\t")
        pretty = string.replace(pretty, "\\", "/")
        f = open(self.logFilePath, "wb")
        f.write(pretty)
        f.close()

    def getUUID(self):
        return str(uuid.uuid4()).upper()


class ExistingXML:
    """opens an existing project xml file to edit it"""

    def __init__(self, filepath):

        self.filepath = filepath
        self.tree = ET.parse(filepath)
        self.root = self.tree.getroot()
        self.rz = self.root.find("Realizations")

        self.WRATrealizations = []

    def addMeta(self, name, value, parentNode):
        """adds metadata tags to the project xml document"""
        metaNode = parentNode.find("MetaData")
        if metaNode is None:
            metaNode = ET.SubElement(parentNode, "MetaData")

        node = ET.SubElement(metaNode, "Meta")
        node.set("name", name)
        node.text = str(value)

    def addProjectInput(self, itype, name, path, project="", iid="", guid="", ref=""):
        typeNode = ET.SubElement(self.Inputs, itype)
        if iid is not "":
            typeNode.set("id", iid)
        if guid is not "":
            typeNode.set("guid", guid)
        if ref is not "":
            typeNode.set("ref", ref)
        nameNode = ET.SubElement(typeNode, "Name")
        nameNode.text = str(name)
        pathNode = ET.SubElement(typeNode, "Path")
        pathNode.text = str(path)
        if project is not "":
            projectNode = ET.SubElement(typeNode, "Project")
            projectNode.text = str(project)

    def addWRATInput(self, parentNode, type, name="", path="", project="", iid="", guid="", ref=""):
        """adds input tags to the project xml document"""
        inputsNode = parentNode.find("Inputs")
        if inputsNode is None:
            inputsNode = ET.SubElement(parentNode, "Inputs")
        if type == "Network":
            dnNode = inputsNode.find("DrainageNetworks")
            if dnNode is None:
                dnNode = ET.SubElement(inputsNode, "DrainageNetworks")
            networkNode = ET.SubElement(dnNode, "Network")
            if name is not "":
                nameNode = ET.SubElement(networkNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(networkNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(networkNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                networkNode.set("id", iid)
            if guid is not "":
                networkNode.set("guid", guid)
            if ref is not "":
                networkNode.set("ref", ref)
        if type == "Vegetation Height":
            heightNode = inputsNode.find("VegetationHeight")
            if heightNode is None:
                heightNode = ET.SubElement(inputsNode, "VegetationHeight")
            if name is not "":
                nameNode = ET.SubElement(heightNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(heightNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(heightNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                heightNode.set("id", iid)
            if guid is not "":
                heightNode.set("guid", guid)
            if ref is not "":
                heightNode.set("ref", ref)
        if type == "Vegetation Cover":
            coverNode = inputsNode.find("VegetationCover")
            if coverNode is None:
                coverNode = ET.SubElement(inputsNode, "VegetationCover")
            if name is not "":
                nameNode = ET.SubElement(coverNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(coverNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(coverNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                coverNode.set("id", iid)
            if guid is not "":
                coverNode.set("guid", guid)
            if ref is not "":
                coverNode.set("ref", ref)
        if type == "Bankfull Channel":
            bfNode = inputsNode.find("BankfullChannel")
            if bfNode is None:
                bfNode = ET.SubElement(inputsNode, "BankfullChannel")
            if name is not "":
                nameNode = ET.SubElement(bfNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(bfNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(bfNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                bfNode.set("id", iid)
            if guid is not "":
                bfNode.set("guid", guid)
            if ref is not "":
                bfNode.set("ref", ref)
        if type == "DEM":
            topoNode = inputsNode.find("Topography")
            if topoNode is None:
                topoNode = ET.SubElement(inputsNode, "Topography")
            demNode = ET.SubElement(topoNode, "DEM")
            if name is not "":
                nameNode = ET.SubElement(demNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(demNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(demNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                demNode.set("id", iid)
            if guid is not "":
                demNode.set("guid", guid)
            if ref is not "":
                demNode.set("ref", ref)
        if type == "Valley":
            vbNode = inputsNode.find("ValleyBottom")
            if vbNode is None:
                vbNode = ET.SubElement(inputsNode, "ValleyBottom")
            if name is not "":
                nameNode = ET.SubElement(vbNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(vbNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(vbNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                vbNode.set("id", iid)
            if guid is not "":
                vbNode.set("guid", guid)
            if ref is not "":
                vbNode.set("ref", ref)
        if type == "Wildfire":
            fireNode = inputsNode.find("Wildfire")
            if fireNode is None:
                fireNode = ET.SubElement(inputsNode, "Wildfire")
            if name is not "":
                nameNode = ET.SubElement(fireNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(fireNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(fireNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                fireNode.set("id", iid)
            if guid is not "":
                fireNode.set("guid", guid)
            if ref is not "":
                fireNode.set("ref", ref)
        if type == "Historic Vegetation":
            histNode = inputsNode.find("HistoricVegetation")
            if histNode is None:
                histNode = ET.SubElement(inputsNode, "HistoricVegetation")
            if name is not "":
                nameNode = ET.SubElement(histNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(histNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(histNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                histNode.set("id", iid)
            if guid is not "":
                histNode.set("guid", guid)
            if ref is not "":
                histNode.set("ref", ref)
        if type == "Height Raster":
            heightNode = inputsNode.Find("VegetationHeight")
            if heightNode is None:
                heightNode = ET.SubElement(inputsNode, "VegetationHeight")
            htrNode = heightNode.find("HeightRasters")
            if htrNode is None:
                htrNode = ET.SubElement(heightNode, "HeightRasters")
            rasterNode = ET.SubElement(htrNode, "Raster")
            if name is not "":
                nameNode = ET.SubElement(rasterNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(rasterNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(rasterNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                rasterNode.set("id", iid)
            if guid is not "":
                rasterNode.set("guid", guid)
            if ref is not "":
                rasterNode.set("ref", ref)
        if type == "Cover Rasters":
            coverNode = inputsNode.find("VegetationCover")
            if coverNode is None:
                coverNode = ET.SubElement(inputsNode, "VegetationCover")
            cvrNode = coverNode.find("CoverRasters")
            if cvrNode is None:
                cvrNode = ET.SubElement(coverNode, "CoverRasters")
            rasterNode = ET.SubElement(cvrNode, "Raster")
            if name is not "":
                nameNode = ET.SubElement(rasterNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(rasterNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(rasterNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                rasterNode.set("id", iid)
            if guid is not "":
                rasterNode.set("guid", guid)
            if ref is not "":
                rasterNode.set("ref", ref)
        if type == "Flow":
            topoNode = inputsNode.find("Topography")
            if topoNode is None:
                topoNode = ET.SubElement(inputsNode, "Topography")
            flowNode = ET.SubElement(topoNode, "Flow")
            if name is not "":
                nameNode = ET.SubElement(flowNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(flowNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(flowNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                flowNode.set("id", iid)
            if guid is not "":
                flowNode.set("guid", guid)
            if ref is not "":
                flowNode.set("ref", ref)
        if type == "Slope":
            topoNode = inputsNode.find("Topography")
            if topoNode is None:
                topoNode = ET.SubElement(inputsNode, "Topography")
            slopeNode = ET.SubElement(topoNode, "Slope")
            if name is not "":
                nameNode = ET.SubElement(slopeNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(slopeNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(slopeNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                slopeNode.set("id", iid)
            if guid is not "":
                slopeNode.set("guid", guid)
            if ref is not "":
                slopeNode.set("ref", ref)
        if type == "Gullies":
            topoNode = inputsNode.find("Topography")
            if topoNode is None:
                topoNode = ET.SubElement(inputsNode, "Topography")
            gulliesNode = topoNode.find("Gullies")
            if gulliesNode is None:
                gulliesNode = ET.SubElement(topoNode, "Gullies")
            vectorNode = ET.SubElement(gulliesNode, "Vector")
            if name is not "":
                nameNode = ET.SubElement(vectorNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(vectorNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(vectorNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                vectorNode.set("id", iid)
            if guid is not "":
                vectorNode.set("guid", guid)
            if ref is not "":
                vectorNode.set("ref", ref)
        if type == "LWD Burns":
            fireNode = inputsNode.find("Wildfire")
            if fireNode is None:
                fireNode = ET.SubElement(inputsNode, "Wildfire")
            lwdbNode = fireNode.find("LWDBurns")
            if lwdbNode is None:
                lwdbNode = ET.SubElement(fireNode, "LWDBurns")
            rasterNode = ET.SubElement(lwdbNode, "Raster")
            if name is not "":
                nameNode = ET.SubElement(rasterNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(rasterNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(rasterNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                rasterNode.set("id", iid)
            if guid is not "":
                rasterNode.set("guid", guid)
            if ref is not "":
                rasterNode.set("ref", ref)
        if type == "Historic LWD":
            histNode = inputsNode.find("HistoricVegetation")
            if histNode is None:
                histNode = ET.SubElement(inputsNode, "HistoricVegetation")
            histrNode = histNode.find("HistoricRasters")
            if histrNode is None:
                histrNode = ET.SubElement(histNode, "HistoricRasters")
            rasterNode = ET.SubElement(histrNode, "Raster")
            if name is not "":
                nameNode = ET.SubElement(rasterNode, "Name")
                nameNode.text = str(name)
            if path is not "":
                pathNode = ET.SubElement(rasterNode, "Path")
                pathNode.text = str(path)
            if project is not "":
                projectNode = ET.SubElement(rasterNode, "Project")
                projectNode.text = str(project)
            if iid is not "":
                rasterNode.set("id", iid)
            if guid is not "":
                rasterNode.set("guid", guid)
            if ref is not "":
                rasterNode.set("ref", ref)

    def addParameter(self, name, value, parentNode):
        """adds parameter tags to the project xml document"""
        paramNode = parentNode.find("Parameters")
        if paramNode is None:
            paramNode = ET.SubElement(paramNode, "Parameters")

        node = ET.SubElement(paramNode, "Param")
        node.set("name", name)
        node.text = str(value)

    def addOutput(self, aname, otype, name, path, parentNode, project="", oid="", guid="", ref=""):
        """adds an output tag to an analysis tag in the project xml document"""
        analysesNode = parentNode.find("Analyses")
        if analysesNode is None:
            analysesNode = ET.SubElement(parentNode, "Analyses")
        analysisNode = analysesNode.find("Analysis")
        if analysisNode is None:
            analysisNode = ET.SubElement(analysesNode, "Analysis")
            ET.SubElement(analysisNode, "Name").text = str(aname)
        outputsNode = analysisNode.find("Outputs")
        if outputsNode is None:
            outputsNode = ET.SubElement(analysisNode, "Outputs")

        typeNode = ET.SubElement(outputsNode, otype)
        if oid is not "":
            typeNode.set("id", oid)
        if guid is not "":
            typeNode.set("guid", guid)
        if ref is not "":
            typeNode.set("ref", ref)
        nameNode = ET.SubElement(typeNode, "Name")
        nameNode.text = str(name)
        pathNode = ET.SubElement(typeNode, "Path")
        pathNode.text = str(path)

        if project is not "":
            projectNode = ET.SubElement(typeNode, "Project")
            projectNode.text = str(project)

    def addWRATRealization(self, name, rid="", promoted="", dateCreated="", productVersion="", guid=""):
        """adds a WRAT realization tag to the project xml document"""
        node = ET.SubElement(self.realizations, "WRAT")
        if rid is not "":
            node.set("id", rid)
        if promoted is not "":
            node.set("promoted", promoted)
        if dateCreated is not "":
            node.set("dateCreated", dateCreated)
        if productVersion is not "":
            node.set("productVersion", productVersion)
        if guid is not "":
            node.set("guid", guid)
        nameNode = ET.SubElement(node, "Name")
        nameNode.text = str(name)
        self.WRATrealizations.append(node)

    def write(self):
        """
        Return a pretty-printed XML string for the Element.
        Then write it out to the expected file.
        """
        rough_string = ET.tostring(self.root, encoding='utf-8', method='xml')
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="\t")
        while string.find(pretty, "\n\t\n") > 0:
            pretty = string.replace(pretty, "\n\t\t\t\t\t\t\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\t\t\t\t\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\t\t\t\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\t\t\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\t\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\t\n", "\n")
            pretty = string.replace(pretty, "\n\t\n", "\n")
            pretty = string.replace(pretty, "\n\n", "\n")
            pretty = string.replace(pretty, "\n\n\n", "\n")
            pretty = string.replace(pretty, "\\", "/")
        f = open(self.filepath, "wb")
        f.write(pretty)
        f.close()

    def getUUID(self):
        return str(uuid.uuid4()).upper()