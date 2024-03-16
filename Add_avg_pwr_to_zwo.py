import os
import xml.etree.ElementTree as ET
import re

def pretty_tags_element():
    # Returns a formatted string for the tags element, adjusted for spacing
    return '    <tags>\n        <tag name="Avg_pwr_edit"/>\n    </tags>\n'

def modify_zwo_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".zwo"):
            filepath = os.path.join(directory, filename)
            original_tree = ET.parse(filepath)
            original_root = original_tree.getroot()

            # Modify workout elements, except for textevent elements
            workout_element = original_root.find('.//workout')
            if workout_element is not None:
                for elem in workout_element.iter():
                    # Skip textevent elements
                    if elem.tag not in ['workout', 'textevent']:
                        elem.set('show_avg', '1')

            # Convert the entire XML structure back to string
            xml_str = ET.tostring(original_root, encoding='unicode')
            
            # Remove existing <tags> block, if any, and empty <tags /> elements
            xml_str = re.sub(r'\s*<tags>.*?</tags>\s*', '', xml_str, flags=re.DOTALL)
            xml_str = xml_str.replace('<tags />\n', '')  # Remove empty self-closing <tags />

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

            # Insert the pretty-printed <tags> block
            new_xml_str = xml_str[:insert_position] + pretty_tags_element() + xml_str[insert_position:]

            # Write the modified XML back to the file
            with open(filepath, 'w', encoding='utf-8') as modified_file:
                modified_file.write(new_xml_str)

# add path to workout files here
modify_zwo_files('yourepath/Zwift/Workouts/512412431/')
