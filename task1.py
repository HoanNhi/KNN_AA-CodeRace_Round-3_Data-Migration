from bs4 import BeautifulSoup
from reqif.parser import ReqIFParser
import json
import sys



input_file_path = sys.argv[1]
config_file_path = sys.argv[2]
#Uncomment lines below to debug
#input_file_path = "Requirements.reqif"
#config_file_path = "Config_file.json"
data = {}


def getArtifactAttributeByName(reqif_bundle, obj, attributeName, customValues=None):
    """
    Return value of an artifact's attribute
    """
    value = ""
    #Traverse through all attributes
    for attribute in obj.attributes:
            ref = attribute.definition_ref #Get reference 
            name = reqif_bundle.lookup.spec_types_lookup[obj.spec_object_type].attribute_map[ref].long_name #Get name of attribute
            if name == attributeName:
                if attribute.attribute_type.name == "ENUMERATION": #If the attribute type is Enum
                    Ref = attribute.definition_ref
                    ValueRef = attribute.value[0]
                    T_Ref = reqif_bundle.lookup.spec_types_lookup[obj.spec_object_type].attribute_map[Ref].datatype_definition
                    value = reqif_bundle.lookup.data_types_lookup[T_Ref].values_map[ValueRef].long_name
                else: #If the attribute type is anything else
                    value = attribute.value

    if customValues != None: #If there were specified custom values
        if value in customValues.keys():
            value = customValues[value]
        else:
            value = ""
    return value

def getArtifactAttributes(reqif_bundle, obj, config:dict):
    """
    Return a dictionary object containing all required attributes of an artifact.\n
    The required attributes to extract are read from config.
    """
    attributeDict = {}
    for key, value in config.items(): 
        if value["Source"] == "ArtifactType": #Artifact type is a special case, because it is not an attribute
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

def getModuleAttributeByName(reqif_bundle, obj, attributeName, customValues=None):
    """
    Return value of a specification(module)'s attribute."""
    if attributeName == "ModuleName": #Special case
        value = obj.long_name
    if attributeName == "ModuleType": #Special case
        value = reqif_bundle.lookup.spec_types_lookup[obj.specification_type].long_name

    for attribute in obj.values:
            ref = attribute.definition_ref
            name = reqif_bundle.lookup.spec_types_lookup[obj.specification_type].spec_attribute_map[ref]
            if name == attributeName:
                if attribute.attribute_type.name == "ENUMERATION": #If attribute type is enum
                    Ref = attribute.definition_ref
                    ValueRef = attribute.value[0]
                    T_Ref = reqif_bundle.lookup.spec_types_lookup[obj.spec_object_type].attribute_map[Ref].datatype_definition
                    value = reqif_bundle.lookup.data_types_lookup[T_Ref].values_map[ValueRef].long_name
                else:
                    value = attribute.value
    
    if customValues != None: #If there were custom values specified
        if value in customValues.keys():
            value = customValues[value]
        else:
            value = ""
    return value

def reqIFtoJSON(input_file_path, config_file_path):

    #Opening config file
    try:
       file = open(config_file_path,"r")
    except PermissionError:
        print("No permission!")
        return None
    except FileNotFoundError:
        print("Config file not found!")
        return None
    #Load json object from config file
    configStructure = json.load(file)
    #Get reqif object from the parser
    reqif_bundle = ReqIFParser.parse(input_file_path)
    jsonObj = {}

    for specification in reqif_bundle.core_content.req_if_content.specifications:
        #Get the hierachy including all artifacts
        hierachy = reqif_bundle.iterate_specification_hierarchy(specification)

        for key, value in configStructure.items():
            if value["MappingType"] == "1-1":
                if isinstance(value["Source"], dict): #Get attributes of artifact
                    config = value["Source"]
                    hierachy_obj = next(hierachy, None)
                    if hierachy_obj == None: #There are no more artifacts left in this specification
                        break
                    obj = reqif_bundle.get_spec_object_by_ref(hierachy_obj.spec_object)
                    attributesDict = getArtifactAttributes(reqif_bundle, obj, config)
                    jsonObj[key] = attributesDict
                else: #Get attribute of specification
                    jsonObj[key] = getModuleAttributeByName(reqif_bundle,specification, value["Source"])
            
            if value["MappingType"] == "Custom":
                customValues = value.get("CustomValues")
                jsonObj[key] = getModuleAttributeByName(reqif_bundle,specification, value["Source"], customValues)
            
            if value["MappingType"] == "Array": #Artifacts
                ArtifactList = []
                for artifactCount in range(len(value["Source"])):
                    hierachy_obj = next(hierachy, None)
                    if hierachy_obj == None: #There are no more artifacts left in this specification
                        break
                    obj = reqif_bundle.get_spec_object_by_ref(hierachy_obj.spec_object)
                    config = value["Source"][artifactCount] #Get config of current artifact
                    attributesDict = getArtifactAttributes(reqif_bundle, obj, config)
                    ArtifactList.append(attributesDict)
                jsonObj[key] = ArtifactList

    jsonData = json.dumps(jsonObj, indent=2)
    return jsonData

data = reqIFtoJSON(input_file_path, config_file_path)
try:
    with open(".\output\output_task1_R3.json", "w") as f:
        f.write(data)
        print("Data Migration complete.\nOutput file is at " + f.name)
except PermissionError:
    print("No permission to open file!")

