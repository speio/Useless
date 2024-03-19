# Tested on Apple M1 Max, OSX 14.2 Beta 
# Python 3.11.5 
# To use: 
# Download the script, make sure you have python3 installed with required packages
# run it as python Add_avg_to_zwo_gui.py
# Follow onscreen prompts to select folder paths and options

import os
import shutil
import xml.etree.ElementTree as ET
import re
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QCheckBox, QProgressBar, QMessageBox

class ZwiftWorkoutModifier(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Zwift Workout Modifier')
        self.setGeometry(200, 200, 600, 300)
        layout = QVBoxLayout()

        # Input directory
        input_layout = QHBoxLayout()
        self.input_label = QLabel('Input Directory:')
        self.input_edit = QLineEdit()
        self.input_button = QPushButton('Browse')
        self.input_button.clicked.connect(self.browse_input_directory)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.input_button)
        layout.addLayout(input_layout)

        # Set default input directory
        default_input_directory = os.path.join(os.path.expanduser("~"), "Documents", "Zwift", "Workouts")
        self.input_edit.setText(default_input_directory)

        # Output directory
        output_layout = QHBoxLayout()
        self.output_label = QLabel('Output Directory: \n ("Modified Workouts" will be made at input if left blank)')
        self.output_edit = QLineEdit()
        self.output_button = QPushButton('Browse')
        self.output_button.clicked.connect(self.browse_output_directory)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(self.output_button)
        layout.addLayout(output_layout)

        # Expand intervals checkbox
        self.expand_intervals_checkbox = QCheckBox('Expand Grouped Intervals? \n (Needed to show avg power for each)')
        layout.addWidget(self.expand_intervals_checkbox)

        # Modify button
        self.modify_button = QPushButton('Modify Workouts')
        self.modify_button.clicked.connect(self.modify_workouts)
        layout.addWidget(self.modify_button)

        self.setLayout(layout)

    def browse_input_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Input Directory')
        self.input_edit.setText(directory)

    def browse_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        self.output_edit.setText(directory)

    def modify_workouts(self):
        input_directory = self.input_edit.text()
        output_directory = self.output_edit.text()

        # Set default output directory if not specified
        if not output_directory:
            output_directory = os.path.join(input_directory, "Avg_Pwr_Mod")

        expand_intervals = self.expand_intervals_checkbox.isChecked()

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Get the total number of ZWO files for progress calculation
        total_files = sum(filename.endswith(".zwo") for filename in os.listdir(input_directory))

        # Create a progress bar
        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, total_files)
        progress_bar.setValue(0)
        self.layout().addWidget(progress_bar)

        # Modify ZWO files
        modified_files = modify_zwo_files(self, input_directory, output_directory, expand_intervals, progress_bar)

        # Show a completion message with the number of modified files
        QMessageBox.information(self, "Workout Modification", f"{modified_files} out of {total_files} workout files have been successfully modified.")

def pretty_tags_element():
    # Returns a formatted string for the tags element, adjusted for spacing
    return '    <tags>\n        <tag name="Avg_pwr_edit"/>\n    </tags>\n'

def expand_intervals_func(workout_element):
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
            workout_element.insert(index, ET.Element('_newline'))  # Insert a placeholder element for newline
            index += 1

def modify_zwo_files(self, directory, target_directory, expand_intervals, progress_bar):
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    processed_files = 0
    modified_files = 0

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
                    if expand_intervals:
                        expand_intervals_func(workout_element)
                    for elem in workout_element.iter():
                        if elem.tag not in ['workout', 'textevent', 'IntervalsT']:
                            elem.set('show_avg', '1')
            except Exception as e:
                print(f"Error modifying workout elements in {file_path}: {e}")
                continue

            try:
                # Convert the entire XML structure back to string
                xml_str = ET.tostring(original_root, encoding='unicode')
                xml_str = xml_str.replace('<_newline />', '\n')
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
                modified_files += 1
            except Exception as e:
                print(f"Error writing modified XML to {target_filepath}: {e}")
                continue

            processed_files += 1
            progress_bar.setValue(processed_files)
            QApplication.processEvents()  # Update the GUI

    return modified_files

if __name__ == '__main__':
    app = QApplication([])
    window = ZwiftWorkoutModifier()
    window.show()
    app.exec_()
