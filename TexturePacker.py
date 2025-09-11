import sys

from PyQt5.QtWidgets import QApplication, QCheckBox, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QSpinBox, \
    QLayout, QLabel, QPushButton, QListWidget, QSpacerItem, QSizePolicy, QWidget, QLineEdit
from PyQt5.sip import delete
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, sip, QtGui

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

        self.output_amount = 0

        main_box = self.ChannelGroup

        main_box_layout = QVBoxLayout()
        main_box.setLayout(main_box_layout)

        output_names_box = self.OutputNamesBox
        output_names_box.setContentsMargins(0, 0, 0, 0)

        output_names_box_layout = QVBoxLayout()
        output_names_box.setLayout(output_names_box_layout)

        input_spacer = QSpacerItem(40, 300, QSizePolicy.Expanding, QSizePolicy.Minimum)
        output_spacer = QSpacerItem(40, 300, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.BaseColorButton.clicked.connect(lambda: self.include_input("BaseColor", self.BaseColorButton, main_box, main_box_layout))
        self.BaseColorButton.clicked.connect(lambda: self.input_spacer_manager(main_box_layout, input_spacer))

        self.NormalsButton.clicked.connect(lambda: self.include_input("Normals", self.NormalsButton, main_box, main_box_layout))
        self.NormalsButton.clicked.connect(lambda: self.input_spacer_manager(main_box_layout, input_spacer))

        self.RoughnessButton.clicked.connect(lambda: self.include_input("Roughness", self.RoughnessButton, main_box, main_box_layout))
        self.RoughnessButton.clicked.connect(lambda: self.input_spacer_manager(main_box_layout, input_spacer))

        self.MetalnessButton.clicked.connect(lambda: self.include_input("Metalness", self.MetalnessButton, main_box, main_box_layout))
        self.MetalnessButton.clicked.connect(lambda: self.input_spacer_manager(main_box_layout, input_spacer))

        self.AOButton.clicked.connect(lambda: self.include_input("AO", self.AOButton, main_box, main_box_layout))
        self.AOButton.clicked.connect(lambda: self.input_spacer_manager(main_box_layout, input_spacer))

        self.HeightButton.clicked.connect(lambda: self.include_input("Height", self.HeightButton, main_box, main_box_layout))
        self.HeightButton.clicked.connect(lambda: self.input_spacer_manager(main_box_layout, input_spacer))

        self.EmissiveButton.clicked.connect(lambda: self.include_input("Emissive", self.EmissiveButton, main_box, main_box_layout))
        self.EmissiveButton.clicked.connect(lambda: self.input_spacer_manager(main_box_layout, input_spacer))

        self.RGBButton.clicked.connect(lambda: self.include_output("Output RGB:", output_names_box, output_names_box_layout))
        self.RGBButton.clicked.connect(lambda: self.output_spacer_manager(output_names_box_layout, output_spacer))

        self.RGBAButton.clicked.connect(lambda: self.include_output("Output RGBA:", output_names_box, output_names_box_layout))
        self.RGBAButton.clicked.connect(lambda: self.output_spacer_manager(output_names_box_layout, output_spacer))

        self.ResetInputsButton.clicked.connect(lambda: self.include_reset_inputs(main_box_layout, input_spacer))
        self.ResetOutputsButton.clicked.connect(lambda: self.include_reset_outputs(output_names_box_layout, output_spacer))

        self.NameBox.currentIndexChanged.connect(self.open_rename_window)
        self.RenameButton.clicked.connect(self.open_rename_window)

        self.BackButton.clicked.connect(self.back_to_mainmenu)

    def include_input(self, input_type="", button=QPushButton, main_box=QGroupBox, main_box_layout=QVBoxLayout):
        button.setEnabled(False)
        self.add_channels(str(input_type), main_box, main_box_layout)

    def include_output(self, output_type:"", output_names_box=QGroupBox, output_box_layout=QVBoxLayout):
        self.add_output(output_type, output_names_box, output_box_layout)

    def include_reset_inputs(self, layout=QVBoxLayout, spacer=QSpacerItem):
        self.BaseColorButton.setEnabled(True)
        self.NormalsButton.setEnabled(True)
        self.RoughnessButton.setEnabled(True)
        self.MetalnessButton.setEnabled(True)
        self.AOButton.setEnabled(True)
        self.HeightButton.setEnabled(True)
        self.EmissiveButton.setEnabled(True)
        layout.removeItem(spacer)
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

    def include_reset_outputs(self, layout=QVBoxLayout, spacer=QSpacerItem):
        layout.removeItem(spacer)
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()
        self.output_amount = 0

    def back_to_mainmenu(self):
        widget.setCurrentIndex(0)

    def add_channels(self, labeltext="", parent=QGroupBox, layout=QVBoxLayout):
        channel_box = QGroupBox("", parent)
        channel_box_layout = QHBoxLayout()
        channel_box.setMaximumHeight(33)
        channel_box.setContentsMargins(0,0,0,0)

        channel_label = QLabel(str(labeltext), channel_box)
        r_checkbox = QCheckBox("R:")
        r_checkbox.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        r_checkbox.setMaximumSize(32, 20)
        g_checkbox = QCheckBox("G:")
        g_checkbox.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        g_checkbox.setMaximumSize(32, 20)
        b_checkbox = QCheckBox("B:")
        b_checkbox.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        b_checkbox.setMaximumSize(32, 20)
        a_checkbox = QCheckBox("A:")
        a_checkbox.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        a_checkbox.setMaximumSize(32, 20)

        channel_box_layout.setContentsMargins(0,0,0,0)
        channel_box_layout.addWidget(channel_label)
        channel_box_layout.addWidget(r_checkbox)
        channel_box_layout.addWidget(g_checkbox)
        channel_box_layout.addWidget(b_checkbox)
        channel_box_layout.addWidget(a_checkbox)
        channel_box_layout.addStretch()

        channel_box.setLayout(channel_box_layout)

        layout.addWidget(channel_box)

    def add_output(self, labeltext="", parent=QGroupBox, layout=QVBoxLayout):
        input_field = QLineEdit("", parent)
        input_field.setMaximumHeight(33)
        input_field.setContentsMargins(0, 0, 0, 0)
        input_field.setPlaceholderText("File Name")
        label = QLabel("[" + str(self.output_amount) + "] " + labeltext, parent)

        self.output_amount += 1

        layout.addWidget(label)
        layout.addWidget(input_field)

    def input_spacer_manager(self, main_box_layout=QVBoxLayout, spacer=QSpacerItem):
        main_box_layout.removeItem(spacer)
        main_box_layout.addSpacerItem(spacer)

    def output_spacer_manager(self, output_box_layout=QVBoxLayout, spacer=QSpacerItem):
        output_box_layout.removeItem(spacer)
        output_box_layout.addSpacerItem(spacer)

    def open_rename_window(self):
        widget.setCurrentIndex(3)


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
