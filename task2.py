from rstcloth import RstCloth
import json
import sys
import html2text
import htmltools
import re

input_file_path = sys.argv[1]
#Uncomment line below to debug
#input_file_path = "output_task1_R3.json"
config_file_path = "Config_file.json"
output_file_path = ".\output\output_task2_R3.rst"

def replace_newline(text):
    """
    A function to replace any <br> tag with "\n|". 
    Input: A converted text from html code
    Output: The processed text
    """
    pattern = r'(?<!\n)\n(?!\n)|(?<!\n)\n\\(?!\n)'
    replaced_text = re.sub(pattern, '\n| ', text)
    replaced_text = replaced_text.replace("|\\", "| ")
    return replaced_text

def decodeHTML(htmlText):
    """
    A function to decode HTML scripts to text
    """
    text_HTML = html2text.html2text(htmlText)
    processed_text = replace_newline(text_HTML)
    lines = processed_text.split("\n") #Split the html data into different parts, separating by escape sequence "\n"
    return lines

def sortAttributes(artifact, artifactDict):
    """
    Sort all attributes of an artifact into its corresponding placement, 
    based on config (artifactDict)

    Returns: Three lists indicating value texts, content texts and sub-directive texts
    """
    valueTexts = []
    contentTexts = []
    sub_directiveTexts = []

    for attribute in artifact.keys():
        placement = artifact[attribute].get("Placement", None) #Read Placement value in config
        if placement == None or placement == "ValueText":
            valueTexts.append((attribute, artifactDict[attribute]))
        elif placement == "Content":
            str = artifactDict[attribute]
            str = decodeHTML(str) #If it is content, we need to decode HTML
            contentTexts.append(str)
        elif placement == "Sub-directive":
            sub_directiveTexts.append((attribute, artifactDict[attribute]))
    
    return valueTexts,contentTexts,sub_directiveTexts

def writeJSONtoRst(input_file_path, config_file_path, output_file_path):
    #Open neccesary files
    try:
        input_file = open(input_file_path, "r")
        config_file = open(config_file_path, "r")
        output_file = open(output_file_path, "w")
    except PermissionError:
        print("No permision to open file!")
        return False
    
    #Load json object from file
    input_json = json.load(input_file)
    config_json = json.load(config_file)
    #Initialize Rst parser
    rstData = RstCloth(output_file)

    #Write heading (First item of input)
    for headingKey, headingValue in config_json.items():
        if headingValue["MappingType"] == "1-1" or headingValue["MappingType"] == "Custom":
            if isinstance(headingValue["Source"], dict): #If item is an artifact
                str = input_json[headingKey].values()[0]
            else: #If item is specification attribute
                str = input_json[headingKey]
            rstData.title(str)
            rstData.newline()
            break
        else: #Array mapping?
            break
        
    check = 1
    #Traverse through all items (artifacts) in input json
    for key, value in config_json.items():
        if check == 1: #Just to skip the first element, which is the heading we've already written
            check = 0
            continue
        #Write sub-headings
        if value["MappingType"] == "1-1" or value["MappingType"] == "Custom":
            if isinstance(value["Source"], dict): #If source is an artifact, we take only the first attribute as sub-heading
                str = list(input_json[key].values())[0]
            else:
                str = input_json[key]
            
            str = decodeHTML(str) 
            for line in str:
                if line == '': #Skip empty lines
                    continue
                rstData.heading(line,"*")
            rstData.newline()
            continue

        #Write directives
        if value["MappingType"] == "Array":
            array_json = input_json[key]
            artifactCount = 0
            for artifact in value["Source"]:
                #Initialize three lists for three possible placements 
                valueTexts = []
                contentTexts = []
                sub_directiveTexts = []
                
                #Get config of artifact (in the form of dictionary)
                artifactDict = array_json[artifactCount]
                artifactCount += 1
                
                #Decide which attributes belong to which placement
                valueTexts, contentTexts, sub_directiveTexts = sortAttributes(artifact, artifactDict)
                
                #Write the attributes
                #Directive + value texts
                rstData.directive(name="sw_req",fields=valueTexts)
                rstData.newline()
                #HTML Content
                for value in contentTexts:
                    for line in value:
                        if line == '':
                            continue
                        rstData.content(line)
                        rstData.newline()
                #Sub-directives
                for value in sub_directiveTexts:
                    rstData.directive(name=value[0],content=value[1])
                    rstData.newline()
    print("Data migration complete.\nOutput file is at " + output_file.name)
    return True

check = writeJSONtoRst(input_file_path, config_file_path, output_file_path)