import requests
import re
from ItsPrompt.prompt import Prompt
from packaging import version
import os
from platform import system

# Check for the Windows operating system for clipboard operations
is_windows = True if system() == "Windows" else False

if is_windows:
    import win32clipboard
else:
    # Alternate clipboard utility for Linux/Mac (untested on Mac systems)
    import pyperclip

# Utility to get clipboard data across multiple operating systems
def get_clipboard_data():
    if is_windows:
        win32clipboard.OpenClipboard()
        clipboardData = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return clipboardData
    else:
        return pyperclip.paste()

# Utility to clear the console window without relying on Windows-exclusive commands
def system_clear():
    if is_windows:
        os.system("cls")
    else:
        os.system("clear")

CURRENT_VERSION = "1.2.2" # Update this version when you release new versions
GITHUB_REPO = "brycentjw/deepwoken-build-comparer"

# Function to fetch the latest release version from GitHub
def get_latest_version_from_github(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        response = requests.get(url)
        response.raise_for_status()
        latest_release = response.json()
        return latest_release["tag_name"].lstrip('v')  # Remove 'v' prefix from the version tag
    except requests.RequestException as e:
        print(f"Error fetching latest version: {e}")
        return None

# Function to check for updates and notify the user
def check_for_updates():
    latest_version = get_latest_version_from_github(GITHUB_REPO)
    if latest_version:
        # Use packaging.version to compare semantic versions properly
        local_ver = version.parse(CURRENT_VERSION)
        latest_ver = version.parse(latest_version)

        if local_ver < latest_ver:
            print(f"Warning: You are using an older version ({CURRENT_VERSION}). The latest version is {latest_version}.")
            print("Please update the script to the latest version on https://github.com/brycentjw/deepwoken-build-comparer/releases.")
        elif local_ver > latest_ver:
            print(f"You are using a newer version ({CURRENT_VERSION}) than the latest release ({latest_version}).")
            print("This might be a development or pre-release version.")
        else:
            print(f"You are using the latest version ({CURRENT_VERSION}).")
    else:
        print("Could not check for updates.")

# Utility to create a file if it does not exist
def create_file_if_not_exists(file_name):
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            file.write("")

# Initialize necessary files
create_file_if_not_exists("buildId.txt")
create_file_if_not_exists("characterData.txt")
create_file_if_not_exists("equipmentTalents.txt")

with open("equipmentTalents.txt", "r") as file:
    equipmentTalents = [line.strip() for line in file.readlines() if line.strip()]

# Read build ID from file
with open("buildId.txt", "r") as file:
    buildId = file.read()

# Initialize talents to ignore
talentsToIgnore = [
    "Flamecharmer", "Frostdrawer", "Thundercaller", 
    "Galebreather", "Shadowcaster", "Ironsinger", 
    "Unbounded", "The Sound from Below"
]

# Retrieve all talents from the Deepwoken Builder API
def get_all_talents_from_api():
    print("Fetching list of all talents from Deepwoken Builder API...")
    return requests.get("https://api.deepwoken.co/get?type=talent&name=all").json()['content']

# Initialize all_talents_data
all_talents_data = get_all_talents_from_api()

# Check if a talent should be ignored based on its name
def should_ignore_talent(talent_name: str, characterOrBuild: str):
    return any(ignored in talent_name for ignored in talentsToIgnore) or (characterOrBuild == "character" and talent_name in equipmentTalents)

# Retrieve talent data by name
def get_talent_data(talent_name: str, all_talents_data: dict):
    talent_name = talent_name.lower()
    return all_talents_data.get(talent_name, None)

# Determine the rarity of a talent
def get_talent_rarity(talent_name: str, all_talents_data: dict):
    talent_data = get_talent_data(talent_name, all_talents_data)
    return "NotFound" if not talent_data else talent_data['rarity']

# Get talents from a build using its ID
def get_build_talents(build_id: str):
    url = f"https://api.deepwoken.co/build?id={build_id}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == "failed":
            return False

        talents = [re.sub(r"\[.*?\]", "", talent).strip() for talent in data['content']]
        return talents
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False

# Check if a talent can be obtained by a character
def can_obtain_talent(character: dict, talent: str, all_talents_data: dict):
    talent_data = get_talent_data(talent, all_talents_data)
    
    if not talent_data:
        return False

    character_attributes = character['attributes']
    talent_reqs = {**talent_data['reqs']['base'], **talent_data['reqs']['weapon'], **talent_data['reqs']['attunement']}
    talent_power = talent_data['reqs']['power']
    
    # Check for attribute and power level requirements
    if character['power'] < int(talent_power):
        return False
    if talent == "Neuroplasticity":
        return all(character_attributes[attr] >= 35 for attr in ['Intelligence', 'Willpower', 'Charisma'])
    return all(character_attributes[attr] >= req for attr, req in talent_reqs.items())

# Parse character data from the file
def parse_character_data():
    with open("characterData.txt", "r") as file:
        data = file.read()

    if not '== MANTRAS ==' in data:
        return False
    
    # replacing end splitting the text
    # when newline ('\n') is seen.
    lines = data.split("\n")
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
    attributes_map = {
        "STR": 'Strength', "FTD": 'Fortitude', "AGL": 'Agility', "INT": 'Intelligence', 
        "WLL": 'Willpower', "CHA": 'Charisma', "HVY": 'Heavy Wep.', "MED": 'Medium Wep.',
        "LHT": 'Light Wep.', "FIR": 'Flamecharm', "ICE": 'Frostdraw', "LTN": 'Thundercall',
        "WND": 'Galebreathe', "SDW": 'Shadowcast', "MTL": 'Ironsing'
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
            if value in attributes_map:  # Ensure we only update valid keys
                attributes[attributes_map[value]] = int(key)

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
        if lines[index] in talents or should_ignore_talent(lines[index], "character"):
            index += 1
            continue
        else:
            talents.append(lines[index])
            index += 1
    
    character_dict['talents'] = talents
    
    return character_dict

# Import character data from clipboard
def import_character_data_from_clipboard():
    clipboard_data = get_clipboard_data()

    if '== MANTRAS ==' in clipboard_data:
        with open("characterData.txt", "w") as file:
            normalized_data = clipboard_data.replace('\r\n', '\n')  # Convert Windows newlines to Unix newlines
            file.write(normalized_data)
        return True
    return False

# Function to find talent in all_talents_data by case-insensitive search
def find_talent_case_insensitive(talent_name: str, all_talents_data: dict):
    for talent in all_talents_data:
        if talent.lower() == talent_name.lower():
            return all_talents_data[talent]['name']  # Return the correctly cased talent name
    return None

# Function to modify equipment talents ignore list
def modify_equipment_talents():
    system_clear()
    print("Current Equipment Talents to Ignore:", equipmentTalents)
    
    option = Prompt.select(
        question="What would you like to do?",
        options=("Add a talent to ignore", "Remove a talent from ignore list", "Clear the entire ignore list", "Back to main menu"),
        default="Add a talent to ignore"
    )
    system_clear()
    
    if option == "Add a talent to ignore":
        new_talent = Prompt.input("Enter the talent name to ignore:").strip()  # Keep original input
        matching_talent = find_talent_case_insensitive(new_talent, all_talents_data)  # Check against all_talents_data

        if matching_talent and matching_talent not in equipmentTalents:
            equipmentTalents.append(matching_talent)  # Add the correctly cased talent
            with open("equipmentTalents.txt", "a") as file:
                file.write(matching_talent + "\n")
            print(f"{matching_talent} added to the ignore list.\n")
        else:
            if matching_talent:
                print(f"The talent '{matching_talent}' already exists in the ignore list.\n")
            else:
                print(f"The talent '{new_talent}' does not exist in the talent database.\n")
    
    elif option == "Remove a talent from ignore list":
        remove_talent = Prompt.input("Enter the talent name to remove from ignore list:").strip()  # Keep original input
        matching_talent = find_talent_case_insensitive(remove_talent, all_talents_data)

        if matching_talent and matching_talent in equipmentTalents:
            equipmentTalents.remove(matching_talent)  # Remove the correctly cased talent
            with open("equipmentTalents.txt", "w") as file:
                file.writelines([talent + "\n" for talent in equipmentTalents])
            print(f"{matching_talent} removed from the ignore list.\n")
        else:
            print("Talent not found in the ignore list.\n")
    
    elif option == "Clear the entire ignore list":
        confirmation = Prompt.confirm("Are you sure you want to clear the entire ignore list?", default=False)
        if confirmation:
            equipmentTalents.clear()
            with open("equipmentTalents.txt", "w") as file:
                file.write("")  # Clear the file
            print("The entire ignore list has been cleared.\n")
        else:
            print("Clearing the ignore list was canceled.\n")

# Compare build and character data
def compare_build_and_character_data():
    character_data = parse_character_data()
    if not character_data:
        return False

    build_talents = get_build_talents(buildId)
    if not build_talents:
        return False

    # Classify talents by rarity (Common, Rare, Advanced)
    def classify_talents(talents, characterOrBuild):
        classified = {'Common': [], 'Rare': [], 'Advanced': []}
        for talent in talents:
            rarity = get_talent_rarity(talent, all_talents_data)
            if rarity not in ['NotFound', 'Quest', 'Outfit', 'Oath', 'Unique', 'Origin', 'Equipment', 'Murmur'] and not should_ignore_talent(talent, characterOrBuild):
                classified[rarity].append(talent)
        return classified

    # Talents in build and character
    build_talents_classified = classify_talents(build_talents, "build")
    character_talents_classified = classify_talents(character_data['talents'], "character")

    # Talents that are missing in character but in the build
    missing_talents = {rarity: [] for rarity in ['Common', 'Rare', 'Advanced']}
    talents_in_both = {rarity: [] for rarity in ['Common', 'Rare', 'Advanced']}
    obtainable_talents = {rarity: [] for rarity in ['Common', 'Rare', 'Advanced']}

    for rarity in build_talents_classified:
        for talent in build_talents_classified[rarity]:
            if talent in character_talents_classified[rarity]:
                talents_in_both[rarity].append(talent)
            else:
                missing_talents[rarity].append(talent)
                if can_obtain_talent(character_data, talent, all_talents_data):
                    obtainable_talents[rarity].append(talent)

    # Talents that the character has but are not in the build
    extra_talents = {rarity: [] for rarity in ['Common', 'Rare', 'Advanced']}
    for rarity in character_talents_classified:
        for talent in character_talents_classified[rarity]:
            if talent not in build_talents_classified[rarity]:
                extra_talents[rarity].append(talent)

    # Function to print talents classified by rarity
    def print_talents(title, talents_dict):
        print(title)
        for rarity in ['Common', 'Rare', 'Advanced']:
            print(f"{rarity} ({len(talents_dict[rarity])}):")
            print(talents_dict[rarity])

    system_clear()
    # Print results
    # print("obtainable:", obtainable_talents)
    # print("missing from character:",missing_talents)
    # print("are in both:",talents_in_both)
    # print("extra:",extra_talents)
    print_talents("Talents that the character has, and is also in the build:", talents_in_both)
    print_talents("\n\nTalents that are in the build, but the character doesn't have:", missing_talents)
    print_talents("\n\nTalents that the character has, but aren't in the build:", extra_talents)
    print_talents("\n\nTalents that are in the build and can be obtained, but the character doesn't have:", obtainable_talents)
    print()


system_clear()
# Main loop for the CLI interaction
if __name__ == "__main__":
    while True:
        character_data = parse_character_data()
        imported_talents = len(character_data['talents']) if character_data else 0

        # Display the ignored talents in the menu (empty if none)
        ignored_talents_str = f"[{', '.join(f'\'{talent}\'' for talent in equipmentTalents)}]" if equipmentTalents else "None"

        print("Created by brycentjw (https://github.com/brycentjw/deepwoken-build-comparer)")
        print("Uses cyfiee's deepwoken builder (https://deepwoken.co/) and its API (https://api.deepwoken.co/)")
        check_for_updates()
        
        selected_option = Prompt.select(
            question='Select an option',
            options=(
                "Print build and character data comparisons",
                f"Import character data from clipboard ({imported_talents} {imported_talents > 1 and "talents" or "talent"} imported)",
                f"Import Deepwoken builder ID from clipboard (currently set to '{buildId}')",
                f"Modify equipment talents ignore list (currently: {ignored_talents_str})",
                "Refresh Deepwoken builder talent list",
                "Exit"
            ),
            default="Print build and character data comparisons"
        )
        system_clear()

        if selected_option == "Print build and character data comparisons":
            verified = True
            with open("characterData.txt", "r") as file:
                if not "== TALENTS ==" in file.read():
                    print("Character data was not imported correctly, please import the character data.")
                    print("If you do not know how to, please refer to the README on the github (https://github.com/brycentjw/deepwoken-build-comparer) and look for the 'How do I import character data? | What's character data?' question in the FAQ.\n")
                    verified = False
            with open("buildId.txt", "r") as file:
                if file.read() == '':
                    print("There was no buildId provided, please set the buildId to compare the character to.\n")
                    verified = False
            if compare_build_and_character_data() == False:
                print("There was an error with the build comparison.\n")
        elif selected_option.startswith("Import character data"):
            if import_character_data_from_clipboard():
                character_data = parse_character_data()
                print(f"Imported talents: {character_data and character_data['talents'] or 0}\n")
            else:
                print("Character data was not imported correctly, please import the character data again.")
                print("If you do not know how to, please refer to the README on the github (https://github.com/brycentjw/deepwoken-build-comparer) and look for the 'How do I import character data? | What's character data?' question in the FAQ.\n")
        elif selected_option.startswith("Import Deepwoken builder ID"):
            clipboard_data = get_clipboard_data()
            new_build_id = clipboard_data.strip().replace("https://deepwoken.co/builder?id=", "")
            if new_build_id and get_build_talents(new_build_id):
                buildId = new_build_id
                with open("buildId.txt", "w") as file:
                    file.write(buildId)
                print("Build ID successfully updated.\n")
            else:
                print("There was an error with the build ID.\nIt should look like 'https://deepwoken.co/builder?id=IxoCRuz6', or you can also input the id itself like 'IxoCRuz6'.\n")
        elif selected_option.startswith("Modify equipment talents ignore list"):
            modify_equipment_talents()
        elif selected_option == "Refresh Deepwoken builder talent list":
            all_talents_data = get_all_talents_from_api()
            system_clear()
            print('All talents have been refreshed.\n')
        elif selected_option == "Exit":
            break
