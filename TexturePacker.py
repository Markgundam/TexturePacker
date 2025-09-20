import sys

from PyQt5.QtWidgets import QApplication, QCheckBox, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QSpinBox, \
    QLayout, QLabel, QPushButton, QListWidget, QSpacerItem, QSizePolicy, QWidget, QLineEdit, QComboBox
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore

#------------------------------------------------------

#class OutputRGBMap(OutputType="RGB", R=bool, G=bool, B=bool):
 #   def __init__(self):
  #    super(OutputRGBMap, self).__init__()

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

        output_names_box = self.OutputNamesBox
        output_names_box.setContentsMargins(0, 0, 0, 0)

        output_names_box_layout = QVBoxLayout()
        output_names_box.setLayout(output_names_box_layout)

        output_spacer = QSpacerItem(40, 300, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.BaseColorButton.clicked.connect(lambda: self.include_input("BaseColor", self.BaseColorButton, ["R", "G", "B"]))

        self.NormalsButton.clicked.connect(lambda: self.include_input("Normals", self.NormalsButton, ["R", "G", "B"]))

        self.RoughnessButton.clicked.connect(lambda: self.include_input("Roughness", self.RoughnessButton, ["R"]))

        self.MetalnessButton.clicked.connect(lambda: self.include_input("Metalness", self.MetalnessButton, ["R"]))

        self.AOButton.clicked.connect(lambda: self.include_input("AO", self.AOButton, ["R"]))

        self.HeightButton.clicked.connect(lambda: self.include_input("Height", self.HeightButton, ["R"]))

        self.EmissiveButton.clicked.connect(lambda: self.include_input("Emissive", self.EmissiveButton, ["R", "G", "B"]))

        self.RGBButton.clicked.connect(lambda: self.include_output("RGB", output_names_box, output_names_box_layout, channel_amount=3))
        self.RGBButton.clicked.connect(lambda: self.output_spacer_manager(output_names_box_layout, output_spacer))

        self.RGBAButton.clicked.connect(lambda: self.include_output("RGBA", output_names_box, output_names_box_layout, channel_amount=4))
        self.RGBAButton.clicked.connect(lambda: self.output_spacer_manager(output_names_box_layout, output_spacer))

        self.ResetButton.clicked.connect(lambda: self.include_reset_outputs(output_names_box_layout, output_spacer))

        self.NameBox.currentIndexChanged.connect(self.open_rename_window)
        self.RenameButton.clicked.connect(self.open_rename_window)

        self.BackButton.clicked.connect(self.back_to_mainmenu)

        self.SavePresetButton.clicked.connect(self.save_preset)

    def include_input(self, input_type="", button=QPushButton, channels=[]):
        button.setEnabled(False)
        self.add_channels(input_type, channels)

    def add_channels(self, labeltext="", channels=[]):
        for QComboBox in output_dropdowns:
            for channel in channels:
                QComboBox.addItem(labeltext + ": " + channel)

    def include_output(self, labeltext="", output_names_box=QGroupBox, output_box_layout=QVBoxLayout, channel_amount=int):
        self.add_output(labeltext, output_names_box, output_box_layout, channel_amount)
        self.BaseColorButton.setEnabled(True)
        self.NormalsButton.setEnabled(True)
        self.RoughnessButton.setEnabled(True)
        self.MetalnessButton.setEnabled(True)
        self.AOButton.setEnabled(True)
        self.HeightButton.setEnabled(True)
        self.EmissiveButton.setEnabled(True)


    def add_output(self, labeltext="", parent=QGroupBox, layout=QVBoxLayout, channel_amount=int):

        global output_amount
        output_amount +=1

        for i in range(output_amount):
            out



        output_channels = ["R", "G", "B", "A"]

        #name of output
        output_name_field = QLineEdit("", parent)
        output_name_field.editingFinished.connect(lambda: self.update_output_data(output_name_field.text(), labeltext, channel_amount))
        output_name_field.setMaximumHeight(33)
        output_name_field.setContentsMargins(0, 0, 0, 0)
        output_name_field.setPlaceholderText("File Name")

        #channel container
        output_channel_container = QGroupBox("", parent)
        output_channel_container.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        output_channel_container.setMinimumHeight(40)
        output_channel_container.setContentsMargins(0, 0, 0, 0)

        #channel container layout
        output_channel_container_layout = QHBoxLayout()
        output_channel_container_layout.setContentsMargins(0, 0, 0, 0)

        output_channel_container.setLayout(output_channel_container_layout)

        for i in range(channel_amount):
            output = QComboBox(output_channel_container)
            output.addItem("Out " + output_channels[i])
            output.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
            output.setMaximumSize(200, 50)

            output_channel_container_layout.addWidget(output)

            output_dropdowns.append(output)

        layout.addWidget(output_name_field)
        layout.addWidget(output_channel_container)

    def update_output_data(self, text="", output_type="", channel_amount=int):

        output_channels = ["R", "G", "B", "A"]

        output_dict[text] = {text: output_type}

        for i in range(channel_amount):
            output_dict[output_channels[i]] = None

    def include_reset_outputs(self, layout=QVBoxLayout, spacer=QSpacerItem):
        layout.removeItem(spacer)
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()
        output_dict.clear()
        output_dropdowns.clear()
        self.BaseColorButton.setEnabled(False)
        self.NormalsButton.setEnabled(False)
        self.RoughnessButton.setEnabled(False)
        self.MetalnessButton.setEnabled(False)
        self.AOButton.setEnabled(False)
        self.HeightButton.setEnabled(False)
        self.EmissiveButton.setEnabled(False)

    def back_to_mainmenu(self):
        widget.setCurrentIndex(0)

    def output_spacer_manager(self, output_box_layout=QVBoxLayout, spacer=QSpacerItem):
        output_box_layout.removeItem(spacer)
        output_box_layout.addSpacerItem(spacer)

    def open_rename_window(self):
        widget.setCurrentIndex(3)

    def save_preset(self):
        print("Saving Preset")
        #update output_dict with dropdown text for R G B A

#------------------------------------------------------

class RenamePreset(QtWidgets.QMainWindow):
    def __init__(self):
        super(RenamePreset, self).__init__()
        loadUi("RenamePreset.ui", self)

        self.SaveNameButton.clicked.connect(self.save_name)
        self.DiscardNameButton.clicked.connect(self.discard_name)

    def save_name(self):
        widget.setCurrentIndex(2)

    def discard_name(self):
        widget.setCurrentIndex(2)

# ------------------------------------------------------

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

# set app
app = QApplication(sys.argv)

output_amount = 0
output_dropdowns = []
output_dict = dict()

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
