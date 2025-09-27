import json
import os
import sys

from PyQt5.QtWidgets import QApplication, QCheckBox, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QSpinBox, \
    QLayout, QLabel, QPushButton, QListWidget, QSpacerItem, QSizePolicy, QWidget, QLineEdit, QComboBox, QFileDialog
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PIL import Image

#------------------------------------------------------

class MainMenu(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainMenu, self).__init__()
        loadUi("MainMenu.ui", self)
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
        loadUi("PackTextures.ui", self)

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
        for json_file in json_files:
            self.PresetChooser.addItem(json_file)

        self.PresetChooser.blockSignals(False)

    def load_preset(self, namebox=None):
        if not namebox or not namebox.currentText().endswith(".json"):
            self.show_message("Choose a .json preset >>>")
            return

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
        loadUi("PresetMaker.ui", self)

        self.all_output_dropdowns = []
        self.input_used = []
        self.all_output_names = []
        self.output_data = {}
        self.all_channels_used_in_preset = {}

        self.NameBox.clear()
        self.NameBox.addItem("Create new...")
        self.NameBox.setCurrentIndex(0)

        json_files = [f for f in os.listdir('.') if f.endswith('.json')]

        for json_file in json_files:
            self.NameBox.addItem(json_file)

        output_names_box = self.OutputNamesBox
        output_names_box.setContentsMargins(0, 0, 0, 0)

        output_names_box_layout = QVBoxLayout()
        output_names_box.setLayout(output_names_box_layout)

        output_spacer = QSpacerItem(40, 300, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # inputs buttons
        self.BaseColorButton.clicked.connect(lambda: self.include_input("BaseColor", self.BaseColorButton, ["R", "G", "B"]))
        self.NormalsButton.clicked.connect(lambda: self.include_input("Normals", self.NormalsButton, ["R", "G", "B"]))
        self.RoughnessButton.clicked.connect(lambda: self.include_input("Roughness", self.RoughnessButton, ["R"]))
        self.MetalnessButton.clicked.connect(lambda: self.include_input("Metalness", self.MetalnessButton, ["R"]))
        self.AOButton.clicked.connect(lambda: self.include_input("AO", self.AOButton, ["R"]))
        self.HeightButton.clicked.connect(lambda: self.include_input("Height", self.HeightButton, ["R"]))
        self.EmissiveButton.clicked.connect(lambda: self.include_input("Emissive", self.EmissiveButton, ["R", "G", "B"]))

        # output buttons

        self.RGBButton.clicked.connect(lambda: self.include_output(output_names_box, output_names_box_layout, ["R", "G", "B"], ""))
        self.RGBButton.clicked.connect(lambda: self.output_spacer_manager(output_names_box_layout, output_spacer))
        self.RGBAButton.clicked.connect(lambda: self.include_output( output_names_box, output_names_box_layout, ["R", "G", "B", "A"], ""))
        self.RGBAButton.clicked.connect(lambda: self.output_spacer_manager(output_names_box_layout, output_spacer))

        # reset button
        self.ResetButton.clicked.connect(lambda: self.include_reset_outputs(output_names_box_layout, output_spacer))

        # preset files dropdown - where one can create a new preset and name it or load ones from system and rename them
        self.NameBox.currentIndexChanged.connect(lambda: self.load_file(self.NameBox, output_names_box, output_names_box_layout, output_spacer))
        self.RenameButton.clicked.connect(self.open_rename_window)
        self.DeleteButton.clicked.connect(lambda: self.delete_preset(output_names_box_layout, output_spacer))

        # back to main menu button
        self.BackButton.clicked.connect(self.back_to_mainmenu)

        # save preset file button
        self.SavePresetButton.clicked.connect(self.save_preset)

    def include_input(self, input_type="", button=QPushButton, channels=[]):
        button.setEnabled(False)
        for QComboBox in self.all_output_dropdowns:
            for channel in channels:
                QComboBox.addItem(input_type + ": " + channel)

        for channel in channels:
            self.input_used.append(input_type + channel)

        self.show_message(f"Added {input_type} to inputs")

    def include_output(self, output_names_box = QGroupBox, output_box_layout = QVBoxLayout, channel_amount = [], parsed_title = str):

        global outputs
        outputs += 1

        self.add_output(output_names_box, output_box_layout, channel_amount, parsed_title)
        if channel_amount == ["R", "G", "B"]:
            self.show_message(f"Added RGB output")
        else:
            self.show_message(f"Added RGBA output")

    def add_output(self, parent=QGroupBox, layout=QVBoxLayout, channel_amount=[], parsed_title=str):

        current_output = outputs

        # dictionary to hold all dropdowns of this specific output
        output_channel_drops = {}

        # name of output
        if(parsed_title == ""):
            output_name_field = QLineEdit("", parent)
        else:
            output_name_field = QLineEdit(parsed_title, parent)

        output_name_field.setMaximumHeight(33)
        output_name_field.setContentsMargins(0, 0, 0, 0)
        output_name_field.setPlaceholderText("File Name")

        # adding the name field to a global variable that holds all output name fields
        self.all_output_names.append(output_name_field)

        # adding empty data into a dictionary - this is the final "recipe"
        self.output_data["Out " + str(outputs)] = {"Title": output_name_field.text()}

        for channel in channel_amount:
            self.output_data["Out " + str(outputs)].update({channel: None})

        # call function to update output data title text when title is renamed
        output_name_field.editingFinished.connect(lambda: self.update_output_title(self.output_data, output_name_field, current_output))

        # channel container
        output_channel_container = QGroupBox("", parent)
        output_channel_container.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        output_channel_container.setMinimumHeight(40)
        output_channel_container.setContentsMargins(0, 0, 0, 0)

        # channel container layout
        output_channel_container_layout = QHBoxLayout()
        output_channel_container_layout.setContentsMargins(0, 0, 0, 0)

        # setting the layout
        output_channel_container.setLayout(output_channel_container_layout)

        # creating the dropdowns for each channel
        for i in channel_amount:
            output = QComboBox(output_channel_container)
            output.addItem("Out " + i)
            output.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
            output.setMaximumSize(200, 50)

            for inputs in self.input_used:
                output.addItem(inputs)

            # call function to update output data dropdown text when text is changed
            output.currentTextChanged.connect(lambda: self.update_channel_dropdowns(self.output_data, output_channel_drops, current_output))

            output_channel_container_layout.addWidget(output)

            # populating the dropdown dictionary with each channel of this output
            output_channel_drops[str(i)] = output

            # populating the dropdown list with all dropdowns of all outputs for use in adding inputs
            self.all_output_dropdowns.append(output)

            for channels in self.all_channels_used_in_preset:
                output.addItem(channels)

        layout.addWidget(output_name_field)
        layout.addWidget(output_channel_container)

    def update_output_title(self, output_data, output_name_field=QLineEdit, index=int):
        output_data["Out " + str(index)].update({"Title": output_name_field.text()})
        print(output_data)

        self.show_message(f"Renamed output {index} to {output_name_field.text()}")

    def update_channel_dropdowns(self, output_data, output_channel_drops, index=int):
        for key, dropdowns in output_channel_drops.items():
                output_data["Out " + str(index)].update({key: dropdowns.currentText()})
        print(output_data)

    def include_reset_outputs(self, layout=QVBoxLayout, spacer=QSpacerItem):
        layout.removeItem(spacer)
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()
        self.all_channels_used_in_preset.clear()
        self.all_output_dropdowns.clear()
        self.output_data.clear()

        global outputs
        outputs = 0

        self.BaseColorButton.setEnabled(True)
        self.NormalsButton.setEnabled(True)
        self.RoughnessButton.setEnabled(True)
        self.MetalnessButton.setEnabled(True)
        self.AOButton.setEnabled(True)
        self.HeightButton.setEnabled(True)
        self.EmissiveButton.setEnabled(True)

    def back_to_mainmenu(self):
        widget.setCurrentIndex(0)

    def output_spacer_manager(self, output_box_layout=QVBoxLayout, spacer=QSpacerItem):
        output_box_layout.removeItem(spacer)
        output_box_layout.addSpacerItem(spacer)

    def open_rename_window(self, index=int):
        widget.setCurrentIndex(3)

    def save_preset(self):

        presetname = self.NameBox.currentText()

        with open(f"{presetname}.json", "w") as output_file:
            json.dump(self.output_data, output_file, indent=4)

        self.refresh_json_dropdown()
        self.show_message("Preset Saved")

    def delete_preset(self, output_names_box_layout=QVBoxLayout, output_spacer=QSpacerItem):

        presetname = self.NameBox.currentText()

        if os.path.exists(presetname):
            os.remove(presetname)
            self.include_reset_outputs(output_names_box_layout, output_spacer)
            self.NameBox.removeItem(self.NameBox.currentIndex())
            self.NameBox.setCurrentIndex(0)
            self.show_message("Preset Deleted")
        else:
            print("The file does not exist")

    def load_file(self, namebox=QComboBox, output_names_box=QGroupBox, output_names_box_layout=QVBoxLayout, output_spacer=QSpacerItem):

        if namebox.currentText().endswith(".json"):
            try:
                with open(namebox.currentText(), "r") as json_file:
                    parsed_data = json.load(json_file)
            except Exception as e:
                self.show_message(f"Failed to load preset: {e}")
                return

            self.input_used.clear()
            self.DeleteButton.setEnabled(True)
            self.include_reset_outputs(output_names_box_layout, output_spacer)
            parsed_channel_values = []

            for outputfile, value in parsed_data.items():
                parsed_title = value["Title"]

                parsed_channels = value
                parsed_channels.pop("Title")

                for channel in value:
                    parsed_channel_values.append(value[f"{channel}"])

                self.include_output(output_names_box, output_names_box_layout, parsed_channels, parsed_title)
                self.output_spacer_manager(output_names_box_layout, output_spacer)

                if 'BaseColor: R' in parsed_channel_values:
                    self.include_input("BaseColor", self.BaseColorButton, ["R", "G", "B"])
                if 'Normals: R' in parsed_channel_values:
                    self.include_input("Normals", self.NormalsButton, ["R", "G", "B"])
                if 'Roughness: R' in parsed_channel_values:
                    self.include_input("Roughness", self.RoughnessButton, ["R"])
                if 'Metalness: R' in parsed_channel_values:
                    self.include_input("Metalness", self.MetalnessButton, ["R"])
                if 'AO: R' in parsed_channel_values:
                    self.include_input("AO", self.AOButton, ["R"])
                if 'Height: R' in parsed_channel_values:
                    self.include_input("Height", self.HeightButton, ["R"])
                if 'Emissive: R' in parsed_channel_values:
                    self.include_input("Emissive", self.EmissiveButton, ["R", "G", "B"])

            for dropdown, channel in zip(self.all_output_dropdowns, parsed_channel_values):
                index = dropdown.findText(channel)
                if index >= 0:
                    dropdown.setCurrentIndex(index)

            self.show_message("Preset Loaded")

        else:
            self.show_message("Empty Preset Loaded")
            self.input_used.clear()
            self.DeleteButton.setEnabled(False)
            self.include_reset_outputs(output_names_box_layout, output_spacer)

    def show_message(self, message=str):
        self.Notification.setText(message)

    def refresh_json_dropdown(self):
        self.NameBox.blockSignals(True)
        self.NameBox.clear()
        self.NameBox.addItem("Create new...")
        self.NameBox.setCurrentIndex(0)

        json_files = [f for f in os.listdir('.') if f.endswith('.json')]
        for json_file in json_files:
            self.NameBox.addItem(json_file)

        self.NameBox.blockSignals(False)

#------------------------------------------------------

class RenamePreset(QtWidgets.QMainWindow):
    def __init__(self):
        super(RenamePreset, self).__init__()
        loadUi("RenamePreset.ui", self)

        presetmaker = PresetMaker()

        self.SaveNameButton.clicked.connect(lambda: self.save_name(presetmaker.NameBox))
        self.DiscardNameButton.clicked.connect(self.discard_name)

    def save_name(self, index):
        presetname = self.NameText.text()
        index = presetmaker.NameBox.currentIndex()

        presetmaker.NameBox.setItemText(index, presetname)
        widget.setCurrentIndex(2)

    def discard_name(self):
        widget.setCurrentIndex(2)

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

#set windows as stackedwidget
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainmenu)
widget.addWidget(packtextures)
widget.addWidget(presetmaker)
widget.addWidget(renamepreset)

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
