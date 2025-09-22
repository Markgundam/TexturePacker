import json
import os
import sys
from ftplib import all_errors

from PyQt5.QtWidgets import QApplication, QCheckBox, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QSpinBox, \
    QLayout, QLabel, QPushButton, QListWidget, QSpacerItem, QSizePolicy, QWidget, QLineEdit, QComboBox
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore

#------------------------------------------------------

class OutputRGBMap():
    def __init__(self, OutputType="RGB", R=bool, G=bool, B=bool):
        super(OutputRGBMap, self).__init__()
        self.OutputType = OutputType
        self.R = R
        self.G = G
        self.B = B

        output_name_field = QLineEdit("", parent)
        output_name_field.setMaximumHeight(33)
        output_name_field.setContentsMargins(0, 0, 0, 0)
        output_name_field.setPlaceholderText("File Name")

# ------------------------------------------------------

#class OutputRGBAMap(OutputType="RGBA", R=bool, G=bool, B=bool, A=bool):
 #   def __init__(self):
  #    super(OutputRGBAMap, self).__init__()

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

    def back_to_mainmenu(self):
        widget.setCurrentIndex(0)

#------------------------------------------------------

class PresetMaker(QtWidgets.QMainWindow):
    def __init__(self):
        super(PresetMaker, self).__init__()
        loadUi("PresetMaker.ui", self)

        path_to_json = os.path.dirname(os.path.abspath(__file__))
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        print(json_files)

        output_names_box = self.OutputNamesBox
        output_names_box.setContentsMargins(0, 0, 0, 0)

        output_names_box_layout = QVBoxLayout()
        output_names_box.setLayout(output_names_box_layout)

        output_spacer = QSpacerItem(40, 300, QSizePolicy.Expanding, QSizePolicy.Minimum)

        for json_file in json_files:
            json_file = str.removesuffix(json_file, '.json')
            self.NameBox.addItem(json_file)

        # inputs buttons
        self.BaseColorButton.clicked.connect(lambda: self.include_input("BaseColor", self.BaseColorButton, ["R", "G", "B"]))
        self.NormalsButton.clicked.connect(lambda: self.include_input("Normals", self.NormalsButton, ["R", "G", "B"]))
        self.RoughnessButton.clicked.connect(lambda: self.include_input("Roughness", self.RoughnessButton, ["R"]))
        self.MetalnessButton.clicked.connect(lambda: self.include_input("Metalness", self.MetalnessButton, ["R"]))
        self.AOButton.clicked.connect(lambda: self.include_input("AO", self.AOButton, ["R"]))
        self.HeightButton.clicked.connect(lambda: self.include_input("Height", self.HeightButton, ["R"]))
        self.EmissiveButton.clicked.connect(lambda: self.include_input("Emissive", self.EmissiveButton, ["R", "G", "B"]))

        # output buttons
        self.RGBButton.clicked.connect(lambda: self.include_output(output_names_box, output_names_box_layout, ["R", "G", "B"]))
        self.RGBButton.clicked.connect(lambda: self.output_spacer_manager(output_names_box_layout, output_spacer))
        self.RGBAButton.clicked.connect(lambda: self.include_output( output_names_box, output_names_box_layout, ["R", "G", "B", "A"]))
        self.RGBAButton.clicked.connect(lambda: self.output_spacer_manager(output_names_box_layout, output_spacer))

        # reset button
        self.ResetButton.clicked.connect(lambda: self.include_reset_outputs(output_names_box_layout, output_spacer))

        # preset files dropdown - where one can create a new preset and name it or load ones from system and rename them
        self.NameBox.currentIndexChanged.connect(lambda: self.load_file(json_file))
        self.RenameButton.clicked.connect(self.open_rename_window)

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
            all_channels_used.append(input_type + ": " + channel)

        print(all_channels_used)

    def include_output(self, output_names_box=QGroupBox, output_box_layout=QVBoxLayout, channel_amount=[]):

        global outputs
        outputs += 1

        self.add_output( output_names_box, output_box_layout, channel_amount)

    def add_output(self, parent=QGroupBox, layout=QVBoxLayout, channel_amount=[]):

        current_output = outputs

        # dictionary to hold all dropdowns of this specific output
        output_channel_drops = {}

        # name of output
        output_name_field = QLineEdit("", parent)
        output_name_field.setMaximumHeight(33)
        output_name_field.setContentsMargins(0, 0, 0, 0)
        output_name_field.setPlaceholderText("File Name")

        # adding the name field to a global variable that holds all output name fields
        all_output_names.append(output_name_field)

        # adding empty data into a dictionary - this is the final "recipe"
        output_data["Out " + str(outputs)] = {"Title": output_name_field.text()}
        for channel in channel_amount:
            output_data["Out " + str(outputs)].update({channel: None})
        print(output_data)

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

            # call function to update output data dropdown text when text is changed
            output.currentTextChanged.connect(lambda: self.update_channel_dropdowns(output_data, output_channel_drops, current_output))

            output_channel_container_layout.addWidget(output)

            # populating the dropdown dictionary with each channel of this output
            output_channel_drops[str(i)] = output

            # populating the dropdown list with all dropdowns of all outputs for use in adding inputs
            all_output_dropdowns.append(output)

            for channels in all_channels_used:
                output.addItem(channels)

        layout.addWidget(output_name_field)
        layout.addWidget(output_channel_container)

    def update_output_title(self, output_data, output_name_field=QLineEdit, index=int):
        output_data["Out " + str(index)].update({"Title": output_name_field.text()})
        print(output_data)

    def update_channel_dropdowns(self, output_data, output_channel_drops, index=int):
        for key, dropdowns in output_channel_drops.items():
                output_data["Out " + str(index)].update({key: dropdowns.currentText()})
        print(output_data)

    def include_reset_outputs(self, layout=QVBoxLayout, spacer=QSpacerItem):
        layout.removeItem(spacer)
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()
        all_channels_used.clear()
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
        print(index)

    def save_preset(self):
        presetname = self.NameBox.currentText()
        output_data_str = ", ".join(f"{k}:{v}" for k, v in output_data.items())

        print(f"File: {presetname}: {os.linesep} {output_data_str}")

        output_file = open(f"{presetname}.json", "w")
        json.dump(output_data, output_file)
        output_file.close()

    def load_file(self, filename):
        print("Loading file")

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
all_output_names = []
all_output_dropdowns = []
all_channels_used = []

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
