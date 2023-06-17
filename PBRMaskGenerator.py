import typing
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

from PyQt5.QtWidgets import QWidget

class MainAppWindow(QMainWindow):
    def __init__(self):
        super(MainAppWindow, self).__init__()
        self.setGeometry(200, 200, 1280, 720)
        self.setWindowTitle("File Dialog demo")
        self.initUI()

    def initUI(self):
        self.setCentralWidget(PBRMaskGenerator())

class PBRMaskGenerator(QWidget):
    def __init__(self):
        super(PBRMaskGenerator, self).__init__()

        layout = QHBoxLayout()

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        
        settingsLayout = QVBoxLayout()
        channelDialogs = [None] * 4

        for n, channel in enumerate(["R", "G", "B", "A"]):
            channelDialogs[n] = ChannelDialog(channel)
            settingsLayout.addWidget(QLabel(channel + " Channel"))
            settingsLayout.addWidget(channelDialogs[n])


        settingsLayout.addStretch()

        for n, channel in enumerate(["Final", "R", "G", "B", "A"]):
            tabs.addTab(QLabel(), channel)

        layout.addWidget(tabs)
        layout.addLayout(settingsLayout)
        self.setLayout(layout)

class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class ChannelDialog(QFrame):
    def __init__(self, channel, parent = None):
        super(ChannelDialog, self).__init__(parent)
        
        layout = QVBoxLayout()

        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        

        self.valueSlider = ValueSlider(0, 255)
        self.imageFileDialogue = ImageFileDialog("Select source for " + channel + " channel.")

        #Combo box to select the type of source
        self.sourceSelectionCombo = QComboBox()
        self.sourceSelectionCombo.addItem('Value (0-255)', self.valueSlider)
        self.sourceSelectionCombo.addItem('Image', self.imageFileDialogue)
        

        layout.addWidget(self.sourceSelectionCombo)
        layout.addWidget(self.valueSlider)

        self.setLayout(layout)

    def updateDisplay(self, index):
        

class ValueSlider(QWidget):
    def __init__(self, min, max, parent = None):
        super(ValueSlider, self).__init__(parent)
        layout = QHBoxLayout()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min)
        self.slider.setMaximum(max)
        self.lineEdit = QLineEdit()
        self.lineEdit.setValidator(QIntValidator(min, max))

        self.slider.setValue(min)
        self.lineEdit.setText(str(min))

        self.slider.valueChanged.connect(self.matchLineToSlider)
        self.lineEdit.textChanged.connect(self.matchSliderToLine)

        layout.addWidget(self.lineEdit)
        layout.addWidget(self.slider)

        self.setLayout(layout)
    
    def matchLineToSlider(self):
        self.lineEdit.setText(str(self.slider.value()))
        
    def matchSliderToLine(self):
        text = self.lineEdit.text()
        if(len(text) > 0):
            self.slider.setValue(int(text))
        

class ImageFileDialog(QWidget):
    def __init__(self, prompt, parent = None):
        super(ImageFileDialog, self).__init__(parent)

        layout = QVBoxLayout()
        self.btn = QPushButton(prompt)
        self.btn.clicked.connect(self.getFile)
        self.le = QLabel()

        layout.addWidget(self.btn)
        layout.addWidget(self.le)
        self.setLayout(layout)
		
    def getFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\',"Image files (*.jpg *.gif)")[0]
        self.le.setPixmap(QPixmap(fname))
		
				
def main():
    app = QApplication(sys.argv)
    win = MainAppWindow()

    win.show()
    sys.exit(app.exec_())
	
    
main()