from bs4 import BeautifulSoup
from reqif.parser import ReqIFParser
import json
import sys



#input_file_path = sys.argv[1]
input_file_path = "Requirements.reqif"
config_file_path = "testconfig.json"
data = {}


def getArtifactAttributeByName(reqif_bundle, obj, attributeName, customValues=None):
    value = ""
    for attribute in obj.attributes:
            ref = attribute.definition_ref
            name = reqif_bundle.lookup.spec_types_lookup[obj.spec_object_type].attribute_map[ref].long_name
            if name == attributeName:
                if attribute.attribute_type.name == "ENUMERATION": #Nếu attribute là enum
                    Ref = attribute.definition_ref
                    ValueRef = attribute.value[0]
                    T_Ref = reqif_bundle.lookup.spec_types_lookup[obj.spec_object_type].attribute_map[Ref].datatype_definition
                    value = reqif_bundle.lookup.data_types_lookup[T_Ref].values_map[ValueRef].long_name
                else:
                    value = attribute.value

    if customValues != None:
        if value in customValues.keys():
            value = customValues[value]
        else:
            value = ""
    return value

def getArtifactAttributes(reqif_bundle, obj, config:dict): #FIXX
    attributeDict = {}
    for key, value in config.items(): 
        if value["Source"] == "ArtifactType": #Trường hợp đặc biệt, vì type của artifacts không thuộc các attributes
            attributeDict[key] = reqif_bundle.get_spec_object_type_by_ref(obj.spec_object_type).long_name
            continue
        if value["MappingType"] == "1-1":
            attributeDict[key] = getArtifactAttributeByName(reqif_bundle, obj, value["Source"])
            continue
        if value["MappingType"] == "Custom":
            customValues = value.get("CustomValues")
            attributeDict[key] = getArtifactAttributeByName(reqif_bundle, obj, value["Source"],customValues)
    return attributeDict
    try:
       file = open(config_file_path,"r")
    except PermissionError:
        print("No permission!")
        return None
    except FileNotFoundError:
        print("Config file not found!")
        return None
    
    configStructure = json.load(file)
    attributeNames = {}
    displayNames = []
    for key, value in configStructure:
        if value["MappingType"] == "1-1":
            displayNames.append(key)
            attributeNames[value["Source"]] = 0
        if value["MappingType"] == "Custom":
            displayNames.append(key)
            attributeNames[value["Source"]] = 1
        if value["MappingType"] == "Array":
            displayNames.append(key)
            attributeNames[value["Source"]] = 0

def getModuleAttributeByName(reqif_bundle, obj, name, customValues=None):
    if name == "ModuleName":
        value = obj.long_name
    if name == "ModuleType":
        value = reqif_bundle.lookup.spec_types_lookup[obj.specification_type].long_name
    if name == "ModuleID":
        value = obj.identifier
    
    if customValues != None:
        if value in customValues.keys():
            value = customValues[value]
        else:
            value = ""
    return value

def reqIFtoJSON(input_file_path, config_file_path):
    try:
       file = open(config_file_path,"r")
    except PermissionError:
        print("No permission!")
        return None
    except FileNotFoundError:
        print("Config file not found!")
        return None
    
    configStructure = json.load(file)
    reqif_bundle = ReqIFParser.parse(input_file_path)
    jsonObj = {}

    for specification in reqif_bundle.core_content.req_if_content.specifications:
        for key, value in configStructure.items():
            if value["MappingType"] == "1-1":
                jsonObj[key] = getModuleAttributeByName(reqif_bundle,specification, value["Source"])
            
            if value["MappingType"] == "Custom":
                customValues = value.get("CustomValues")
                jsonObj[key] = getModuleAttributeByName(reqif_bundle,specification, value["Source"], customValues)
            
            if value["MappingType"] == "Array": #Artifacts
                hierachy = reqif_bundle.iterate_specification_hierarchy(specification)
                ArtifactList = []
                artifactCount = 0
                for h2 in hierachy:
                    obj = reqif_bundle.get_spec_object_by_ref(h2.spec_object)
                    config = value["Source"][artifactCount]
                    attributesDict = getArtifactAttributes(reqif_bundle, obj, config)
                    ArtifactList.append(attributesDict)
                    artifactCount += 1
                jsonObj[key] = ArtifactList

    jsonData = json.dumps(jsonObj, indent=2)
    return jsonData

data = reqIFtoJSON(input_file_path, config_file_path)
try:
    with open("output_task1_R3.json", "w") as f:
        f.write(data)
        print("Data Migration complete.\nOutput file is at " + f.name)
except PermissionError:
    print("No permission to open file!")

