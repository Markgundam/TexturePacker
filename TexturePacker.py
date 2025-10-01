import json
import os
import sys

from PyQt5.QtWidgets import QApplication, QCheckBox, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QSpinBox, \
    QLayout, QLabel, QPushButton, QListWidget, QSpacerItem, QSizePolicy, QWidget, QLineEdit, QComboBox, QFileDialog
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, sip
from PIL import Image
from functools import partial


#------------------------------------------------------

class MainMenu(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainMenu, self).__init__()
        loadUi("UI/MainMenu.ui", self)
        self.PackPresetsButton.clicked.connect(self.pack_textures_window)
        self.PackTexturesButton.clicked.connect(self.pack_presets_window)

    def pack_presets_window(self):
        widget.setCurrentIndex(1)

    def pack_textures_window(self):
        widget.setCurrentIndex(2)

#------------------------------------------------------

class PackTextures(QtWidgets.QMainWindow):
    def __init__(self):
        super(PackTextures, self).__init__()
        loadUi("UI/PackTextures.ui", self)

        self.outputs_to_pack = {}
        self.texture_sets = {}
        self.basename = ""
        self.selected_files = []

        self.required_inputs = set()
        self.loaded_inputs = set()

        self.BackButton.clicked.connect(self.back_to_mainmenu)
        self.refresh_json_dropdown()

        self.PresetChooser.currentIndexChanged.connect(lambda: self.load_preset(self.PresetChooser))
        self.PackButton.clicked.connect(lambda: self.pack_textures(self.outputs_to_pack))

        self.LoadFilesButton.setEnabled(False)
        self.LoadFilesButton.clicked.connect(self.load_files)

        self.PackButton.setEnabled(False)

    def refresh_json_dropdown(self):
        self.PresetChooser.blockSignals(True)
        self.PresetChooser.clear()
        self.PresetChooser.addItem("Create new...")
        self.PresetChooser.setCurrentIndex(0)

        json_files = [f for f in os.listdir('.') if f.endswith('.json')]

        for file in json_files:
            if file == "InputOutputConfig.json":
                json_files.remove("InputOutputConfig.json")

        for json_file in json_files:
            self.PresetChooser.addItem(json_file)

        self.PresetChooser.blockSignals(False)

    def load_preset(self, namebox=None):
        with open(namebox.currentText(), "r") as json_file:
            parsed_data = json.load(json_file)

        self.show_message("Preset Loaded")
        self.LoadFilesButton.setEnabled(True)

        self.required_inputs.clear()
        self.outputs_to_pack.clear()

        for outputfile, value in parsed_data.items():
            parsed_title = value["Title"]
            parsed_channels = value.copy()
            parsed_channels.pop("Title", None)
            output_channels = []

            for channel_key, channel_value in parsed_channels.items():
                output_channels.append(channel_value)
                input_name = channel_value.split(":")[0].strip()
                self.required_inputs.add(input_name)

            self.outputs_to_pack[parsed_title] = {"Channels": output_channels}

        self.show_message(f"Preset Loaded. Requires: {', '.join(self.required_inputs)}")
        self.update_outputs()

    def show_message(self, message=str):
        self.Notification.setText(message)

    def back_to_mainmenu(self):
        widget.setCurrentIndex(0)

    def load_files(self):
        global basename

        self.InputList.clear()
        self.loaded_inputs.clear()
        self.texture_sets.clear()

        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Open File")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)

        if not file_dialog.exec():
            return

        selected_files = file_dialog.selectedFiles()

        for file in selected_files:
            filename = os.path.basename(file)
            self.InputList.addItem(filename)

            filename_no_ext = os.path.splitext(os.path.basename(file))[0]  # Remove .png
            if "_" in filename_no_ext:
                parts = filename_no_ext.split("_")
                basename = "_".join(parts[:-1])  # Everything except the last part (the channel suffix)
            else:
                basename = filename_no_ext

            if basename not in self.texture_sets:
                self.texture_sets[basename] = {}

            img = Image.open(file)
            R, G, B = img.getchannel("R"), img.getchannel("G"), img.getchannel("B")

            # UPDATE TO LOOP WITHIN CONFIG - ADD SUFFIX
            if filename.endswith("_B.png"):
                self.texture_sets[basename]["BaseColor"] = (R, G, B)
            elif filename.endswith("_N.png"):
                self.texture_sets[basename]["Normals"] = (R, G, B)
            elif filename.endswith("_O.png"):
                self.texture_sets[basename]["AO"] = (R, G, B)
            elif filename.endswith("_H.png"):
                self.texture_sets[basename]["Height"] = (R, G, B)
            elif filename.endswith("_R.png"):
                self.texture_sets[basename]["Roughness"] = (R, G, B)

        basenames = list(self.texture_sets.keys())
        self.show_message(f"Loaded sets: {', '.join(basenames)}")

        missing = []
        for name, channels in self.texture_sets.items():
            missing_channels = self.required_inputs - set(channels.keys())
            if missing_channels:
                missing.append(f"{name} (missing {', '.join(missing_channels)})")

        if missing:
            self.show_message("Incomplete sets:\n" + "\n".join(missing))
            self.PackButton.setEnabled(False)
        else:
            self.show_message("All sets complete. Ready to pack.")
            self.PackButton.setEnabled(True)

        self.update_outputs()

    def update_outputs(self):
        self.OutputList.clear()

        if not self.outputs_to_pack:
            return

        if not self.texture_sets:
            for key in self.outputs_to_pack.keys():
                self.OutputList.addItem(f"{key}_.png")
            return

        for basename in self.texture_sets.keys():
            for output_name in self.outputs_to_pack.keys():
                preview_filename = f"{basename}_{output_name}.png"
                item = QtWidgets.QListWidgetItem(preview_filename)

                missing_channels = self.required_inputs - set(self.texture_sets[basename].keys())
                if missing_channels:
                    item.setForeground(QtCore.Qt.red)
                    item.setToolTip(f"Missing: {', '.join(missing_channels)}")
                else:
                    item.setForeground(QtCore.Qt.darkGreen)

                self.OutputList.addItem(item)

    def pack_textures(self, outputs_to_pack=dict):
        if not hasattr(self, "texture_sets") or not self.texture_sets:
            self.show_message("No texture sets loaded!")
            return

        for basename, channels_dict in self.texture_sets.items():

            missing = self.required_inputs - set(channels_dict.keys())
            if missing:
                self.show_message(f"Skipping {basename}, missing: {', '.join(missing)}")
                continue

            for outputfiles, channels in outputs_to_pack.items():
                img_channels = []

                for channel in channels["Channels"]:
                    channel_str = str(channel)
                    base_name = channel_str[:-3]

                    if base_name not in channels_dict:
                        self.show_message(f"Missing input for channel {channel} in set {basename}")
                        break

                    if channel_str[-1:] == "R":
                        img_channel = channels_dict[base_name][0]
                    elif channel_str[-1:] == "G":
                        img_channel = channels_dict[base_name][1]
                    elif channel_str[-1:] == "B":
                        img_channel = channels_dict[base_name][2]

                    img_channels.append(img_channel)
                    print(f"{basename} | {channel}: {img_channel}")

                else:
                    try:
                        if len(img_channels) > 3:
                            image_packed = Image.merge("RGBA", tuple(img_channels))

                        else:
                            image_packed = Image.merge("RGB", tuple(img_channels))
                        image_packed.save(f"{tex_path}/{basename}_{outputfiles}.png")
                        self.show_message(f"Packed {basename}_{outputfiles}.png")

                    except Exception as e:
                        self.show_message(f"Failed to pack {basename}_{outputfiles}: {e}")

    def showEvent(self, event):
        self.refresh_json_dropdown()
        super().showEvent(event)

#------------------------------------------------------

class PresetMaker(QtWidgets.QMainWindow):
    def __init__(self):
        super(PresetMaker, self).__init__()
        loadUi("UI/PresetMaker.ui", self)

        self.outputs = 0
        self.all_output_dropdowns = []
        self.input_used = []
        self.all_output_names = []
        self.output_data = {}
        self.all_channels_used_in_preset = {}

        self.input_buttons = {}
        self.output_buttons = {}

        self.refresh_json_dropdown()

        self.OutputTypesBox.setContentsMargins(0, 0, 0, 0)

        self.spacer = QSpacerItem(40, 300, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.OpenConfigButton.clicked.connect(self.open_config)

        self.setup_config()

        # reset button
        self.ResetButton.clicked.connect(lambda: self.include_reset_outputs(self.OutputNamesBoxLayout, spacer))

        # preset files dropdown - where one can create a new preset and name it or load ones from system and rename them
        self.NameBox.currentIndexChanged.connect(lambda: self.load_file(self.NameBox, spacer))
        self.RenameButton.clicked.connect(self.open_rename_window)
        self.DeleteButton.clicked.connect(lambda: self.delete_preset(spacer))

        # back to main menu button
        self.BackButton.clicked.connect(self.back_to_mainmenu)

        # save preset file button
        self.SavePresetButton.clicked.connect(self.save_preset)

    def include_input(self, input_name, button, channels):
        button.setEnabled(False)
        for combo in self.all_output_dropdowns:
            for channel in channels:
                combo.addItem(f"{input_name}: {channel}")

        for channel in channels:
            self.input_used.append(f"{input_name}: {channel}")

        self.show_message(f"Added {input_name} to inputs")

    def include_output(self, channel_list, parsed_title="", spacer=None):
        self.outputs += 1
        self.add_output(self.OutputTypesBox, self.OutputNamesBoxLayout, channel_list, parsed_title)

        if spacer:
            self.spacer_manager(self.OutputNamesBoxLayout, spacer)

        display_name = parsed_title if parsed_title else f"Output {self.outputs}"
        self.show_message(f"Added {display_name} output")

    def add_output(self, parent=QGroupBox, layout=QVBoxLayout, channel_amount=[], parsed_title=""):

        current_output = self.outputs
        output_channel_drops = {}

        # --- Output name field ---
        output_name_field = QLineEdit(parsed_title, parent)
        output_name_field.setMaximumHeight(33)
        output_name_field.setPlaceholderText("File Name")
        self.all_output_names.append(output_name_field)

        # Initialize output data dictionary
        self.output_data[f"Out {current_output}"] = {"Title": parsed_title}
        for ch in channel_amount:
            self.output_data[f"Out {current_output}"][ch] = None

        # Update title dynamically
        output_name_field.editingFinished.connect(
            partial(self.update_output_title, self.output_data, output_name_field, current_output)
        )

        # --- Channel container ---
        output_channel_container = QGroupBox(parent)
        output_channel_container.setLayoutDirection(QtCore.Qt.LeftToRight)
        output_channel_container.setMinimumHeight(40)
        layout_container = QHBoxLayout()
        layout_container.setDirection(QHBoxLayout.LeftToRight)
        output_channel_container.setLayout(layout_container)

        # --- Dropdowns for each channel ---
        for ch in channel_amount:
            combo = QComboBox(output_channel_container)
            combo.addItem(f"Out: {ch}")
            combo.setMaximumSize(200, 50)

            # Add existing inputs
            for used_input in self.input_used:
                combo.addItem(used_input)

            # Update output data when dropdown changes
            combo.currentTextChanged.connect(
                partial(self.update_channel_dropdowns, self.output_data, output_channel_drops, current_output)
            )

            layout_container.addWidget(combo)
            output_channel_drops[ch] = combo
            self.all_output_dropdowns.append(combo)

            # Optionally, add previously used channels
            for used_channel in self.all_channels_used_in_preset:
                combo.addItem(used_channel)

        layout.addWidget(output_name_field)
        layout.addWidget(output_channel_container)

    def update_output_title(self, output_data, output_name_field=QLineEdit, index=int):
        output_data["Out " + str(index)].update({"Title": output_name_field.text()})

        self.show_message(f"Renamed output {index} to {output_name_field.text()}")

    def update_channel_dropdowns(self, output_data, output_channel_drops, index=int):
        for key, dropdowns in output_channel_drops.items():
                output_data["Out " + str(index)].update({key: dropdowns.currentText()})

    def include_reset_outputs(self, layout=QVBoxLayout, spacer=QSpacerItem):
        layout.removeItem(spacer)

        # delete all widgets in the layout
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

        # clear dynamic lists/dictionaries
        self.all_channels_used_in_preset.clear()
        self.all_output_dropdowns.clear()
        self.output_data.clear()
        self.input_used.clear()
        self.all_output_names.clear()
        self.outputs = 0  # reset counter

        # enable all input buttons dynamically
        for button in self.input_buttons.values():
            button.setEnabled(True)

    def back_to_mainmenu(self):
        widget.setCurrentIndex(0)

    def spacer_manager(self, layout=QVBoxLayout, spacer=QSpacerItem):
        layout.removeItem(spacer)
        layout.addSpacerItem(spacer)

    def open_rename_window(self, index=int):
        renamepreset.NameText.setText("")
        renamepreset.NameText.setPlaceholderText(self.NameBox.currentText())
        widget.setCurrentIndex(3)

    def save_preset(self):

        presetname = self.NameBox.currentText()

        with open(presetname, "w") as output_file:
            json.dump(self.output_data, output_file, indent=4)
            for file in renamepreset.renamedfiles:
                if file != "Create new...":
                    os.remove(file)

        self.refresh_json_dropdown()
        self.show_message("Preset Saved")

    def delete_preset(self, spacer=QSpacerItem):

        presetname = self.NameBox.currentText()

        if os.path.exists(presetname):
            os.remove(presetname)
            self.include_reset_outputs(self.OutputNamesBoxLayout, spacer)
            self.NameBox.removeItem(self.NameBox.currentIndex())
            self.NameBox.setCurrentIndex(0)
            self.show_message("Preset Deleted")
        else:
            print("The file does not exist")

    def load_file(self, namebox=QComboBox, spacer=QSpacerItem):

        if namebox.currentText().endswith(".json"):
            try:
                with open(namebox.currentText(), "r") as json_file:
                    parsed_data = json.load(json_file)
            except Exception as e:
                self.show_message(f"Failed to load preset: {e}")
                return

            # Reset everything first
            self.input_used.clear()
            self.include_reset_outputs(self.OutputNamesBoxLayout, spacer)
            self.DeleteButton.setEnabled(True)

            # Keep track of which inputs need to be enabled
            used_inputs = {}

            # Recreate outputs dynamically
            for output_key, value in parsed_data.items():
                title = value.get("Title", "")
                channels = {channel: value for channel, value in value.items() if channel != "Title"}
                self.include_output(list(channels.keys()), title, spacer)

                # mark inputs that appear in this output
                for channel_val in channels.values():
                    if channel_val:
                        input_name = channel_val.split(": ")[0]
                        input_channel = channel_val.split(": ")[1]
                        if input_name not in used_inputs:
                            used_inputs[input_name] = set()
                        used_inputs[input_name].add(input_channel)

            # Enable inputs used in preset
            for input_name, channels in used_inputs.items():
                if input_name in self.input_buttons:
                    self.include_input(input_name, self.input_buttons[input_name], list(channels))

            # Set dropdowns to the values in the preset
            output_dropdowns = [dropdown for dropdown in self.all_output_dropdowns if dropdown.count() > 1]
            channel_values = []
            for output in parsed_data.values():
                for channel, value in output.items():
                    if channel != "Title" and value:
                        channel_values.append(value)

            for dropdown, value in zip(output_dropdowns, channel_values):
                index = dropdown.findText(value)
                if index >= 0:
                    dropdown.setCurrentIndex(index)

            self.show_message("Preset Loaded")

        else:
            self.show_message("Empty Preset Loaded")
            self.input_used.clear()
            self.DeleteButton.setEnabled(False)
            self.include_reset_outputs(self.OutputNamesBoxLayout, spacer)

    def show_message(self, message=str):
        self.Notification.setText(message)

    def refresh_json_dropdown(self):
        self.NameBox.blockSignals(True)
        self.NameBox.clear()
        self.NameBox.addItem("Create new...")
        self.NameBox.setCurrentIndex(0)

        json_files = [f for f in os.listdir('.') if f.endswith('.json')]
        json_files.remove("InputOutputConfig.json")
        for json_file in json_files:
            self.NameBox.addItem(json_file)

        self.NameBox.blockSignals(False)

    def open_config(self):
        widget.setCurrentIndex(4)

    def clear_layout(self, layout=QVBoxLayout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def setup_config(self):

        self.clear_layout(self.InputTypesBoxLayout)
        self.clear_layout(self.OutputTypesBoxLayout)

        try:
            with open(f"InputOutputConfig.json", "r") as json_file:
                config = json.load(json_file)
        except Exception as e:
            self.show_message(f"Failed to load config: {e}")
            return

        for input_name, channels in config.get("Inputs", {}).items():
            self.input_buttons[input_name] = QPushButton(input_name)

            # get only active channels
            active_channels = [ch for ch, enabled in channels.items() if enabled]

            # connect dynamically
            self.input_buttons[input_name].clicked.connect(
                partial(self.include_input, input_name, self.input_buttons[input_name], active_channels)
            )

            self.InputTypesBoxLayout.addWidget(self.input_buttons[input_name])
            self.spacer_manager(self.InputTypesBoxLayout, self.spacer)

        for output_type, channels in config.get("Outputs", {}).items():
            self.output_buttons[output_type] = QPushButton(output_type)

            active_channels = [ch for ch, enabled in channels.items() if enabled]

            self.output_buttons[output_type].clicked.connect(
                partial(self.include_output, active_channels, "", self.spacer)
            )

            self.OutputTypesBoxLayout.addWidget(self.output_buttons[output_type])
            self.spacer_manager(self.OutputTypesBoxLayout, self.spacer)

#------------------------------------------------------

class RenamePreset(QtWidgets.QMainWindow):
    def __init__(self):
        super(RenamePreset, self).__init__()
        loadUi("UI/RenamePreset.ui", self)

        presetmaker = PresetMaker()
        self.renamedfiles = []

        self.SaveNameButton.clicked.connect(self.save_name)
        self.DiscardNameButton.clicked.connect(self.discard_name)

    def save_name(self):
        presetname = self.NameText.text()
        index = presetmaker.NameBox.currentIndex()
        old_file_list = []
        new_file_list = []

        for i in range(presetmaker.NameBox.count()):
            old_file_list.append(presetmaker.NameBox.itemText(i))

        presetmaker.NameBox.setItemText(index, f"{presetname}.json")

        for i in range(presetmaker.NameBox.count()):
            new_file_list.append(presetmaker.NameBox.itemText(i))

        self.renamedfiles = list(set(old_file_list) - (set(new_file_list)))

        widget.setCurrentIndex(2)

    def discard_name(self):
        widget.setCurrentIndex(2)

# ------------------------------------------------------

class ConfigBuilder(QtWidgets.QMainWindow):
    def __init__(self):
        super(ConfigBuilder, self).__init__()
        loadUi("UI/ConfigBuilder.ui", self)

        self.spacer = QSpacerItem(40, 300, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.all_input_titles = []
        self.all_input_suffixes = []
        self.all_input_checkboxes = []

        self.all_output_titles = []
        self.all_output_checkboxes = []

        self.input_data = {}
        self.input_amount = 0

        self.output_data = {}
        self.output_amount = 0

        self.InputTypesBox.setContentsMargins(0, 0, 0, 0)

        self.BackButton.clicked.connect(self.back_to_presetmaker)
        self.AddInputButton.clicked.connect(lambda: self.create_input(self.InputTypesBox, self.InputTypesBoxLayout, "", {"R": False, "G": False, "B": False, "A": False}))
        self.AddInputButton.clicked.connect(lambda: self.spacer_manager(self.InputTypesBoxLayout, self.spacer))
        self.AddOutputButton.clicked.connect(lambda: self.create_output(self.OutputTypesBox, self.OutputTypesBoxLayout, "", {"R": False, "G": False, "B": False, "A": False}))
        self.AddOutputButton.clicked.connect(lambda: self.spacer_manager(self.OutputTypesBoxLayout, self.spacer))

        self.UpdateConfigButton.clicked.connect(self.update_config)

        self.load_config()

    def back_to_presetmaker(self):
        widget.setCurrentIndex(2)

    def spacer_manager(self, layout=QVBoxLayout, spacer=QSpacerItem):
        layout.removeItem(spacer)
        layout.addSpacerItem(spacer)

    def create_input(self, parent=QGroupBox, layout=QVBoxLayout, title="", channels={}):

        self.input_amount += 1

        channel_checkboxes = []

        input_group = QGroupBox()
        input_group.setMaximumHeight(40)
        input_group.setFixedHeight(40)
        input_group.setContentsMargins(0, 0, 0, 0)
        input_group_layout = QHBoxLayout()

        input_group.setLayout(input_group_layout)

        input_title = QLineEdit()
        input_title.setMaximumHeight(30)
        input_title.setContentsMargins(0, 0, 0, 0)
        input_title.setPlaceholderText("Input Title")

        input_suffix = QLineEdit()
        input_suffix.setMaximumHeight(30)
        input_suffix.setFixedWidth(50)
        input_suffix.setContentsMargins(0, 0, 0, 0)
        input_suffix.setPlaceholderText("Suffix")

        if title != "":
            input_title.setText(title)

        if "Suffix" in channels:
            input_suffix.setText(channels["Suffix"])

        self.all_input_titles.append(input_title)
        self.all_input_suffixes.append(input_suffix)

        input_channel_container = QGroupBox("", parent)
        input_channel_container.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        input_channel_container.setMaximumHeight(20)
        input_channel_container.setContentsMargins(0, 0, 0, 0)

        input_channel_container_layout = QHBoxLayout()
        input_channel_container_layout.setContentsMargins(0, 0, 0, 0)

        input_channel_container.setLayout(input_channel_container_layout)

        input_group_layout.addWidget(input_title)
        input_group_layout.addWidget(input_suffix)

        for channel, value in channels.items():
            if channel == "Suffix":
                continue
            input_checkbox = QCheckBox(f"{channel}: ", input_channel_container)
            input_checkbox.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
            input_checkbox.setMaximumSize(50, 50)

            input_checkbox.setChecked(value)

            input_group_layout.addWidget(input_checkbox)
            channel_checkboxes.append(input_checkbox)

        self.all_input_checkboxes.append(channel_checkboxes)

        delete_button = QPushButton("X")
        delete_button.setMaximumSize(20, 20)
        delete_button.clicked.connect(lambda: self.delete_input(input_group, 1))
        input_group_layout.addWidget(delete_button)

        layout.addWidget(input_group)

    def create_output(self, parent=QGroupBox, layout=QVBoxLayout, title="", channels={}):

        self.output_amount += 1

        channel_checkboxes = []

        output_group = QGroupBox()
        output_group.setMaximumHeight(40)
        output_group.setFixedHeight(40)
        output_group.setContentsMargins(0, 0, 0, 0)
        output_group_layout = QHBoxLayout()

        output_group.setLayout(output_group_layout)

        output_title = QLineEdit()
        output_title.setMaximumHeight(30)
        output_title.setContentsMargins(0, 0, 0, 0)
        output_title.setPlaceholderText("Output Title")

        if title != "":
            output_title.setText(title)

        self.all_output_titles.append(output_title)

        output_channel_container = QGroupBox("", parent)
        output_channel_container.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        output_channel_container.setMaximumHeight(20)
        output_channel_container.setContentsMargins(0, 0, 0, 0)

        output_channel_container_layout = QHBoxLayout()
        output_channel_container_layout.setContentsMargins(0, 0, 0, 0)

        output_channel_container.setLayout(output_channel_container_layout)

        output_group_layout.addWidget(output_title)

        for channel, value in channels.items():
            output_checkbox = QCheckBox(f"{channel}: ", output_channel_container)
            output_checkbox.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
            output_checkbox.setMaximumSize(50, 50)

            output_checkbox.setChecked(value)

            output_group_layout.addWidget(output_checkbox)
            channel_checkboxes.append(output_checkbox)

        self.all_output_checkboxes.append(channel_checkboxes)

        delete_button = QPushButton("X")
        delete_button.setMaximumSize(20, 20)
        delete_button.clicked.connect(lambda: self.delete_input(output_group, 0))
        output_group_layout.addWidget(delete_button)

        layout.addWidget(output_group)

    def delete_input(self, group=QGroupBox, input=bool):
        if(input == 1):
            self.input_amount -= 1
        else:
            self.output_amount -= 1

        group.deleteLater()
        print(f"Inputs: {self.input_amount}, Outputs: {self.output_amount}")

    def save_config(self):
        print("Save Config")

        final_data = {}
        final_data["Inputs"] = self.input_data
        final_data["Outputs"] = self.output_data

        with open(f"InputOutputConfig.json", "w") as output_file:
            json.dump(final_data, output_file, indent=5)

    def is_alive(widget):
        return isinstance(widget, QWidget) and not sip.isdeleted(widget)

    def update_config(self):

        for title, suffix, checkbox_set in zip(self.all_input_titles, self.all_input_suffixes, self.all_input_checkboxes):
            if title is None or sip.isdeleted(title):
                continue
            if suffix is None or sip.isdeleted(suffix):
                continue
            if any(cb is None or sip.isdeleted(cb) for cb in checkbox_set):
                continue

            title_str = str(title.text()).strip()
            self.input_data[title_str] = {
                "Suffix": suffix.text(),
                "R": checkbox_set[0].isChecked(),
                "G": checkbox_set[1].isChecked(),
                "B": checkbox_set[2].isChecked(),
                "A": checkbox_set[3].isChecked(),
            }

            print(f"Updated {title_str}: {self.input_data[title_str]}")

        for title, checkbox_set in zip(self.all_output_titles, self.all_output_checkboxes):
            if title is None or sip.isdeleted(title):
                continue
            if any(cb is None or sip.isdeleted(cb) for cb in checkbox_set):
                continue

            title_str = str(title.text()).strip()
            self.output_data[title_str] = {
                "R": checkbox_set[0].isChecked(),
                "G": checkbox_set[1].isChecked(),
                "B": checkbox_set[2].isChecked(),
                "A": checkbox_set[3].isChecked(),
            }

            print(f"Updated {title_str}: {self.output_data[title_str]}")

        self.save_config()

        presetmaker.setup_config()

    def load_config(self):
        try:
            with open("InputOutputConfig.json", "r") as json_file:
                config = json.load(json_file)
        except Exception as e:
            print(f"Failed to load config: {e}")
            return

        print(config)

        def to_bool(val):
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.strip().lower() == "true"
            return False

        for data_type, data_title in config.items():
            if data_type == "Inputs":
                for title, values in data_title.items():
                    # Convert all R,G,B,A to booleans
                    values["R"] = to_bool(values.get("R"))
                    values["G"] = to_bool(values.get("G"))
                    values["B"] = to_bool(values.get("B"))
                    values["A"] = to_bool(values.get("A"))
                    self.create_input(self.InputTypesBox, self.InputTypesBoxLayout, title, values)
                    self.spacer_manager(self.InputTypesBoxLayout, self.spacer)

            elif data_type == "Outputs":
                for title, values in data_title.items():
                    values["R"] = to_bool(values.get("R"))
                    values["G"] = to_bool(values.get("G"))
                    values["B"] = to_bool(values.get("B"))
                    values["A"] = to_bool(values.get("A"))
                    self.create_output(self.OutputTypesBox, self.OutputTypesBoxLayout, title, values)
                    self.spacer_manager(self.OutputTypesBoxLayout, self.spacer)

# ------------------------------------------------------

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

# set app
app = QApplication(sys.argv)

path_to_json = os.path.dirname(os.path.abspath(__file__))
dir_path = os.path.dirname(os.path.abspath(__file__))
tex_path = os.path.dirname(os.path.abspath(__file__))

#initialize windows
mainmenu = MainMenu()
packtextures = PackTextures()
presetmaker = PresetMaker()
renamepreset = RenamePreset()
configbuilder = ConfigBuilder()

#set windows as stackedwidget
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainmenu)
widget.addWidget(packtextures)
widget.addWidget(presetmaker)
widget.addWidget(renamepreset)
widget.addWidget(configbuilder)

#show main menu
widget.setFixedHeight(mainmenu.height())
widget.setFixedWidth(mainmenu.width())
widget.show()

sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook

#exit function
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
