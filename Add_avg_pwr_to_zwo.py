# Tested on Apple M1 Max, OSX 14.2 Beta 
# Python 3.11.5 
import os
import shutil
import xml.etree.ElementTree as ET
import re

####### To run, put the path to your workout files in here, and run it###########
# Set the path to your original and new directories
original_directory = '/Your/path/Documents/Zwift/Workouts/SomeFolderZwiftMakes/'
new_directory = os.path.join(original_directory, 'AvgPwrMod')


def pretty_tags_element():
    # Returns a formatted string for the tags element, adjusted for spacing
    return '    <tags>\n        <tag name="Avg_pwr_edit"/>\n    </tags>\n'

def expand_intervals(workout_element):
    intervals_to_expand = []
    for elem in list(workout_element):
        if elem.tag == 'IntervalsT' and 'Repeat' in elem.attrib:
            repeat_count = int(elem.attrib['Repeat'])
            on_duration = elem.attrib['OnDuration']
            off_duration = elem.attrib['OffDuration']
            on_power = elem.attrib['OnPower']
            off_power = elem.attrib['OffPower']
            # Create new elements for the repeated intervals
            new_elems = []
            for _ in range(repeat_count):
                on_elem = ET.Element('SteadyState', Duration=on_duration, Power=on_power, pace="0")
                off_elem = ET.Element('SteadyState', Duration=off_duration, Power=off_power, pace="0")
                new_elems.extend([on_elem, off_elem])
            intervals_to_expand.append((elem, new_elems))
    # Replace IntervalsT with new elements
    for original_elem, new_elems in intervals_to_expand:
        index = list(workout_element).index(original_elem)
        workout_element.remove(original_elem)
        for new_elem in new_elems:
            workout_element.insert(index, new_elem)
            index += 1

def modify_zwo_files(directory, target_directory):
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(".zwo"):
            target_filepath = os.path.join(target_directory, filename)

            try:
                original_tree = ET.parse(file_path)
                original_root = original_tree.getroot()
            except ET.ParseError as e:
                print(f"Skipping {file_path} due to parsing error: {e}")
                continue

            try:
                # Modify workout elements, except for textevent elements
                workout_element = original_root.find('.//workout')
                if workout_element is not None:
                    expand_intervals(workout_element)
                    for elem in workout_element.iter():
                        if elem.tag not in ['workout', 'textevent', 'IntervalsT']:
                            elem.set('show_avg', '1')
            except Exception as e:
                print(f"Error modifying workout elements in {file_path}: {e}")
                continue

            try:
                # Convert the entire XML structure back to string
                xml_str = ET.tostring(original_root, encoding='unicode')
            except Exception as e:
                print(f"Error converting XML to string in {file_path}: {e}")
                continue

            try:
                # Remove existing <tags> block, if any, and empty <tags /> elements
                xml_str = re.sub(r'\s*<tags>.*?</tags>\s*', '', xml_str, flags=re.DOTALL)
                xml_str = xml_str.replace('<tags />\n', '')  # Remove empty self-closing <tags />
            except Exception as e:
                print(f"Error removing existing tags block in {file_path}: {e}")
                continue

            try:
                # Find the position after <sportType>bike</sportType>
                sport_type_pos = xml_str.find('</sportType>')
                if sport_type_pos != -1:
                    insert_position = xml_str.find('\n', sport_type_pos)
                else:
                    insert_position = xml_str.find('<workout')  # Fallback if <sportType> not found
                if insert_position == -1:
                    insert_position = len(xml_str)  # At the end if <workout> not found
                else:
                    # Adjust the insert_position to not introduce unnecessary whitespace
                    insert_position += 1
            except Exception as e:
                print(f"Error finding insert position in {file_path}: {e}")
                continue

            try:
                # Insert the pretty-printed <tags> block
                new_xml_str = xml_str[:insert_position] + pretty_tags_element() + xml_str[insert_position:]
            except Exception as e:
                print(f"Error inserting tags block in {file_path}: {e}")
                continue

            try:
                # Write the modified XML to the target file in the new directory
                with open(target_filepath, 'w', encoding='utf-8') as modified_file:
                    modified_file.write(new_xml_str)
            except Exception as e:
                print(f"Error writing modified XML to {target_filepath}: {e}")
                continue  
                
modify_zwo_files(original_directory, new_directory)
