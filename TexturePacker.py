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

        self.BackButton.clicked.connect(self.back_to_mainmenu)
        self.PresetChooser.clear()
        self.PresetChooser.addItem("Create new...")
        self.PresetChooser.setCurrentIndex(0)

        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

        for json_file in json_files:
            self.PresetChooser.addItem(json_file)

        self.PresetChooser.currentIndexChanged.connect(lambda: self.load_preset(self.PresetChooser, outputs_to_pack))

        self.LoadFilesButton.clicked.connect(self.load_files)

    def load_preset(self, namebox=QComboBox, outputs_to_pack=None):
        if namebox.currentText().endswith(".json"):
            with open(namebox.currentText(), "r") as json_file:
                data = json_file.read()
                parsed_data = json.loads(data)

            self.show_message("Preset Loaded")

            for outputfile, value in parsed_data.items():

                parsed_title = value["Title"]

                parsed_channels = value
                parsed_channels.pop("Title")

                output_channels = []

                for channel in value:
                    output_channels.append(value[f"{channel}"])

                output = {"Suffix": parsed_title, "Channels": output_channels}

                print(output)

        else:
            self.show_message("Choose a .json preset >>>")

    def show_message(self, message=str):
        self.Notification.setText(message)

    def back_to_mainmenu(self):
        widget.setCurrentIndex(0)

    def load_files(self):
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle("Open File")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)

        dir_path = r"C:/Users/Mark/Documents/GitHub/TexturePacker/"

        all_image_channels = {}

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            for filename in selected_files:
                filename = filename.removeprefix(dir_path)
                self.InputList.addItem(filename)

        for file in selected_files:
            img = Image.open(file)
            image_r = img.getchannel("R")
            image_g = img.getchannel("G")
            image_b = img.getchannel("B")

            if "_A" in file:
                all_image_channels["BaseColor"] = image_r, image_g, image_b
            elif "_N" in file:
                all_image_channels["Normals"] = image_r, image_g, image_b
            elif "_O" in file:
                all_image_channels["Occlusion"] = image_r, image_g, image_b
            elif "_H" in file:
                all_image_channels["Height"] = image_r, image_g, image_b
            elif "_R" in file:
                all_image_channels["Roughness"] = image_r, image_g, image_b

        for key, image_channels in all_image_channels.items():
            print(key + ":" + str(image_channels))

#------------------------------------------------------

class PresetMaker(QtWidgets.QMainWindow):
    def __init__(self):
        super(PresetMaker, self).__init__()
        loadUi("PresetMaker.ui", self)

        self.NameBox.clear()
        self.NameBox.addItem("Create new...")
        self.NameBox.setCurrentIndex(0)

        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        print(json_files)

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
        for QComboBox in all_output_dropdowns:
            for channel in channels:
                QComboBox.addItem(input_type + ": " + channel)

        for channel in channels:
            inputs_used.append(input_type + channel)

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
        all_output_names.append(output_name_field)

        # adding empty data into a dictionary - this is the final "recipe"
        output_data["Out " + str(outputs)] = {"Title": output_name_field.text()}

        for channel in channel_amount:
            output_data["Out " + str(outputs)].update({channel: None})

        # call function to update output data title text when title is renamed
        output_name_field.editingFinished.connect(lambda: self.update_output_title(output_data, output_name_field, current_output))

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

            for inputs in inputs_used:
                output.addItem(inputs)

            # call function to update output data dropdown text when text is changed
            output.currentTextChanged.connect(lambda: self.update_channel_dropdowns(output_data, output_channel_drops, current_output))

            output_channel_container_layout.addWidget(output)

            # populating the dropdown dictionary with each channel of this output
            output_channel_drops[str(i)] = output

            # populating the dropdown list with all dropdowns of all outputs for use in adding inputs
            all_output_dropdowns.append(output)

            for channels in all_channels_used_in_preset:
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
        all_channels_used_in_preset.clear()
        all_output_dropdowns.clear()
        output_data.clear()

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

        output_file = open(f"{presetname}.json", "w")
        json.dump(output_data, output_file, indent=4)
        output_file.close()

        path_to_json = os.path.dirname(os.path.abspath(__file__))
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

        self.NameBox.clear()
        self.NameBox.addItem("Create new...")
        self.NameBox.setCurrentIndex(0)

        for json_file in json_files:
            self.NameBox.addItem(json_file)

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
            with open(namebox.currentText(), "r") as json_file:
                data = json_file.read()
                parsed_data = json.loads(data)

            inputs_used.clear()
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

            for dropdown, channel in zip(all_output_dropdowns, parsed_channel_values):
                index = dropdown.findText(channel)
                if index >= 0:
                    dropdown.setCurrentIndex(index)

            self.show_message("Preset Loaded")

        else:
            self.show_message("Empty Preset Loaded")
            inputs_used.clear()
            self.DeleteButton.setEnabled(False)
            self.include_reset_outputs(output_names_box_layout, output_spacer)

    def show_message(self, message=str):
        self.Notification.setText(message)

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

outputs = 0
output_data = {}
inputs_used = []
all_output_names = []
all_output_dropdowns = []
all_channels_used_in_preset = {}

path_to_json = os.path.dirname(os.path.abspath(__file__))

outputs_to_pack = 0

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
