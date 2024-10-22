import requests
import re
import win32clipboard
from ItsPrompt.prompt import Prompt

### CONFIG ###
# set build id here
r = open("buildId.txt", "r")
buildId = r.read()
r.close()
# edit talentsToCompareTo.txt

### CODE ###
# ignore talents that contain these substrings
talentsToIgnore = [
    "Flamecharmer",
    "Frostdrawer",
    "Thundercaller",
    "Galebreather",
    "Shadowcaster",
    "Ironsinger",
    "Unbounded",
    "The Sound from Below"
]

def getAllTalentsFromAPI():
    print("Getting list of all talents from Deepwoken Builder API...")
    return requests.get("https://api.deepwoken.co/get?type=talent&name=all").json()['content']

def checkIfTalentToIgnore(talentName: str):
    for talentToIgnore in talentsToIgnore:
        if talentToIgnore in talentName:
            return True
    return False

def getTalentData(talentName: str):
    talentName = talentName.lower()
    if talentName in allTalentsData:
        return allTalentsData[talentName]
    else:
        for index in allTalentsData.keys():
            if talentName in index:
                return allTalentsData[index]

def getTalentRarity(talentName: str): # NotFound, Origin, Quest, Oath, Common, Rare, Advanced
    talentData = getTalentData(talentName)

    if talentData == None:
        return "NotFound"
    else:
        return talentData['rarity']

def getBuildTalents():
    url = "https://api.deepwoken.co/build?id=" + buildId

    response = requests.get(url)

    data = response.json()

    if data['status'] == "failed":
        return False

    talentsList = data['content']['talents']

    for i, talent in enumerate(talentsList):
        talentsList[i] = re.sub(r"\[.*?\]", "", talent).strip() # cant lie i dont even know how this works

    return talentsList

def checkIfTalentCanBeObtained(character: dict, talent: str):
    talentData = getTalentData(talent)
    
    talentIsExclusiveWith = talentData['exclusiveWith']

    talentReqs = talentData['reqs']

    characterAttributes = character['attributes']
    talentAttributes = {**talentReqs['base'], **talentReqs['weapon'], **talentReqs['attunement']}
    talentPower = talentReqs['power']
    talentIsFrom: str = talentReqs['from']

    if character['power'] < int(talentPower):
        return False

    for talentExclusiveWith in talentIsExclusiveWith:
        if re.sub(r"\[.*?\]", "", talentExclusiveWith).strip() in character['talents']:
            return False
    
    if talentIsFrom != "":
        for talentFrom in talentIsFrom.split(", "):
            strippedTalent = re.sub(r"\[.*?\]", "", talentFrom).strip()
            if not (strippedTalent in character['talents']) and strippedTalent.lower() in allTalentsData:
                return False
    
    if talent == "Neuroplasticity":
        if characterAttributes['Intelligence'] < 35 and characterAttributes['Willpower'] < 35 and characterAttributes['Charisma'] < 35:
            return False
    else:
        for attributeIndex in characterAttributes:
            if characterAttributes[attributeIndex] < talentAttributes[attributeIndex]:
                return False
    return True

# Corrected function to parse attributes correctly
def parseCharacterData():
    # opening the file in read mode
    my_file = open("characterData.txt", "r")
    
    # reading the file
    data = my_file.read()
    
    # replacing end splitting the text
    # when newline ('\n') is seen.
    lines = data.split("\n")
    my_file.close()
    character_dict = {}
    
    # Parsing the character name, power, race, origin, and oath
    character_dict['name'] = lines[0]
    
    # Parse level, race, origin, oath from the second line
    character_info = lines[2].split()
    character_dict['power'] = int(character_info[1])
    character_dict['race'] = character_info[2]
    character_dict['origin'] = character_info[3]
    character_dict['oath'] = character_info[4]
    
    # Initialize Attributes
    attributesMap = {
        "STR": 'Strength',
        "FTD": 'Fortitude',
        "AGL": 'Agility',
        "INT": 'Intelligence',
        "WLL": 'Willpower',
        "CHA": 'Charisma',
        "HVY": 'Heavy Wep.',
        "MED": 'Medium Wep.',
        "LHT": 'Light Wep.',
        "FIR": 'Flamecharm',
        "ICE": 'Frostdraw',
        "LTN": 'Thundercall',
        "WND": 'Galebreathe',
        "SDW": 'Shadowcast',
        "MTL": 'Ironsing',
    }
    attributes = {
        'Strength': 0, 'Fortitude': 0, 'Agility': 0, 'Intelligence': 0, 'Willpower': 0, 'Charisma': 0,
        'Heavy Wep.': 0, 'Medium Wep.': 0, 'Light Wep.': 0,
        'Flamecharm': 0, 'Frostdraw': 0, 'Thundercall': 0, 'Galebreathe': 0, 'Shadowcast': 0, 'Ironsing': 0
    }
    
    # Function to process attribute lines and update the dictionary
    def process_attributes(attribute_line):
        attr_pairs = attribute_line.split('; ')
        for attr in attr_pairs:
            key, value = attr.split()
            if value in attributesMap:  # Ensure we only update valid keys
                attributes[attributesMap[value]] = int(key)

    # Parse the attribute sections
    process_attributes(lines[4])  # first attribute line
    process_attributes(lines[6])  # second attribute line
    process_attributes(lines[8])  # third attribute line
    
    character_dict['attributes'] = attributes
    
    # Parse the mantras section
    mantras = []
    index = lines.index('== MANTRAS ==') + 1
    while lines[index] != '== TALENTS ==':
        mantras.append(lines[index])
        index += 1
    
    character_dict['mantras'] = mantras
    
    # Parse the talents section
    talents = []
    index = lines.index('== TALENTS ==') + 1
    while index < len(lines):
        talents.append(lines[index])
        index += 1
    
    character_dict['talents'] = talents
    
    return character_dict

def importCharacterData(newCharacterData: str):
    normalized_data = newCharacterData.replace('\r\n', '\n')  # Convert Windows newlines to Unix newlines
    with open("characterData.txt", 'w', newline='\n') as f:
        f.write(normalized_data)


def compareBuildAndCharacterData():
    characterData = parseCharacterData()

    talents1 = {
        "Common": [],
        "Rare": [],
        "Advanced": [],
    }
    talents2 = {
        "Common": [],
        "Rare": [],
        "Advanced": [],
    }

    buildTalents = getBuildTalents()
    if buildTalents == False:
        return False
    characterTalents = characterData['talents']

    for i, talent in enumerate(buildTalents):
        talentRarity = getTalentRarity(talent)
        if talentRarity != "NotFound" and talentRarity != "Outfit" and talentRarity != "Murmur" and talentRarity != "Origin" and talentRarity != "Quest" and talentRarity != "Oath" and not checkIfTalentToIgnore(talent):
            talents1[talentRarity].append(talent)

    for i, talent in enumerate(characterTalents):
        talentRarity = getTalentRarity(talent)
        if talentRarity != "NotFound" and talentRarity != "Outfit" and talentRarity != "Murmur" and talentRarity != "Origin" and talentRarity != "Quest" and talentRarity != "Oath" and not checkIfTalentToIgnore(talent):
            talents2[talentRarity].append(talent)

    missingTalents = {
        "Common": [],
        "Rare": [],
        "Advanced": [],
    }
    talentsNotInBuild = {
        "Common": [],
        "Rare": [],
        "Advanced": [],
    }
    talentsInBuild = {
        "Common": [],
        "Rare": [],
        "Advanced": [],
    }
    talentsInBuildAndCanBeObtained = {
        "Common": [],
        "Rare": [],
        "Advanced": [],
    }

    for talentRarity in talents1:
        for talent in talents1[talentRarity]:
            if talent in talents2[talentRarity]:
                talentsInBuild[talentRarity].append(talent)
            else:
                missingTalents[talentRarity].append(talent)
                if checkIfTalentCanBeObtained(characterData, talent):
                    talentsInBuildAndCanBeObtained[talentRarity].append(talent)

    for talentRarity in talents2:
        for talent in talents2[talentRarity]:
            if not (talent in missingTalents[talentRarity] or talent in talentsInBuild[talentRarity]):
                talentsNotInBuild[talentRarity].append(talent)

    def printTalentsDictionary(dictionary):
        print("Common (" + str(len(dictionary['Common'])) + "):")
        print(dictionary['Common'])
        print("Rare (" + str(len(dictionary['Rare'])) + "):")
        print(dictionary['Rare'])
        print("Advanced (" + str(len(dictionary['Advanced'])) + "):")
        print(dictionary['Advanced'])

    print("\nTalents that are in the build, but the character doesn't have:")
    printTalentsDictionary(missingTalents)
    print("\nTalents that the character has, but aren't in the build:")
    printTalentsDictionary(talentsNotInBuild)
    print("\nTalents that are in the build and can be obtained, but the character doesn't have:")
    printTalentsDictionary(talentsInBuildAndCanBeObtained)
    print("\nTalents that the character has, and is in the build:")
    printTalentsDictionary(talentsInBuild)

allTalentsData: dict = getAllTalentsFromAPI()
# this code is garbage because yeah it's garbage i wasnt making it with the intention of turning this into a user friendly CLI (and also im terrible at python)
# sorry if you're using this as reference, forking it or making a PR
print("Created by brycentjw (https://github.com/brycentjw/deepwoken-build-comparer), uses cyfiee's deepwoken builder (https://deepwoken.co/) and its API (https://api.deepwoken.co/).")

if __name__ == "__main__":
    inProgram = True
    while inProgram:
        ans = Prompt.select(
            question='Options to pick',
            options=('Print build and character data comparisons', 'Import character data from clipboard', f"Select deepwoken builder ID (currently set to '{buildId}')", 'Refresh deepwoken builder talent list', 'Exit'),
            default='Print build and character data comparisons',
        )
        if ans == 'Print build and character data comparisons':
            if compareBuildAndCharacterData() == False:
                print("There was an error getting the build, is the buildId set to an existing build?")
            else:
                print("\nRejoin when importing talents for most accurate results, there is a bug when using Shrine Of Chance that does not remove talents from talents.")
                print("""Please note that talents that are given to you by equipment or armor currently cannot be and is not differentiated.
                    (i.e: robber baron appears as a talent not in the build but is on the character when it's a talent given by a backpack)""")
        elif ans == 'Import character data from clipboard':
            win32clipboard.OpenClipboard()
            clipboard = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            verified = '== MANTRAS ==' in clipboard
            if verified:
                importCharacterData(clipboard)
                print(parseCharacterData()['talents'])
                Prompt.confirm(
                    question="""Verify if the imported talents are correct, rejoin for most accurate character import results (using shrine of chance will cause the character data to be inaccurate!)
                        If the talents are not accurate, please import character data again.""",
                    default=True,
                )
            else:
                print("The imported clipboard did not have verifiable character data information, did you copy the character data properly?")
        elif ans == f"Select deepwoken builder ID (currently set to '{buildId}')":
            ans = Prompt.input(question="Input builder ID")
            
            url = "https://api.deepwoken.co/build?id=" + ans

            response = requests.get(url)

            data = response.json()

            if data['status'] != "failed":
                buildId = ans
                r = open("buildId.txt", "w")
                r.write(ans)
                r.close()
            else:
                print(data)
                print("There was an error getting the build, is the input buildId an existing build?")
        elif ans == 'Refresh deepwoken builder talent list':
            allTalentsData = getAllTalentsFromAPI()
        elif ans == 'Exit':
            inProgram = False