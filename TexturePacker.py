import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QCheckBox, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QSpinBox, \
    QLayout, QLabel, QPushButton, QListWidget
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, sip

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

        main_box = self.ChannelGroup
        main_box_layout = QVBoxLayout()
        main_box.setLayout(main_box_layout)
        output_list = self.OutputList

        self.BaseColorButton.clicked.connect(lambda: self.include_input("BaseColor", self.BaseColorButton, main_box, main_box_layout))
        self.NormalsButton.clicked.connect(lambda: self.include_input("Normals", self.NormalsButton, main_box, main_box_layout))
        self.RoughnessButton.clicked.connect(lambda: self.include_input("Roughness", self.RoughnessButton, main_box, main_box_layout))
        self.MetalnessButton.clicked.connect(lambda: self.include_input("Metalness", self.MetalnessButton, main_box, main_box_layout))
        self.AOButton.clicked.connect(lambda: self.include_input("AO", self.AOButton, main_box, main_box_layout))
        self.HeightButton.clicked.connect(lambda: self.include_input("Height", self.HeightButton, main_box, main_box_layout))
        self.EmissiveButton.clicked.connect(lambda: self.include_input("Emissive", self.EmissiveButton, main_box, main_box_layout))

        self.RGBButton.clicked.connect(lambda: self.include_output("RGB", output_list))
        self.RGBAButton.clicked.connect(lambda: self.include_output("RGBA", output_list))

        self.ResetInputsButton.clicked.connect(self.include_reset_inputs)
        self.ResetOutputsButton.clicked.connect(self.include_reset_outputs)

        self.BackButton.clicked.connect(self.back_to_mainmenu)

    def include_input(self, input_type="", button=QPushButton, main_box=QGroupBox, main_box_layout=QVBoxLayout):
        button.setEnabled(False)
        self.add_channels(str(input_type), main_box, main_box_layout)

    def include_output(self, output_type:"", output_list=QListWidget):
        output_list.addItem(output_type)

    def include_reset_inputs(self):
        for i in range(self.InputList.count()):
            self.InputList.takeItem(0)
            i = i + 1
        self.BaseColorButton.setEnabled(True)
        self.NormalsButton.setEnabled(True)
        self.RoughnessButton.setEnabled(True)
        self.MetalnessButton.setEnabled(True)
        self.AOButton.setEnabled(True)
        self.HeightButton.setEnabled(True)
        self.EmissiveButton.setEnabled(True)
        for QGroupBox in self.ChannelGroup.children():
            sip.delete(QGroupBox)

    def include_reset_outputs(self):
        for i in range(self.OutputList.count()):
            self.OutputList.takeItem(0)
            i = i + 1

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
        layout.addStretch()

#------------------------------------------------------

# set app
app = QApplication(sys.argv)

#initialize windows
mainmenu = MainMenu()
packtextures = PackTextures()
presetmaker = PresetMaker()

#set windows as stackedwidget
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainmenu)
widget.addWidget(packtextures)
widget.addWidget(presetmaker)

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
