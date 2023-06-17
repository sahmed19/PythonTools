from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2, imutils
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
        self.imageDisplays = [None] * 5

        for n, channel in enumerate(["R", "G", "B", "A"]):
            channelDialogs[n] = ChannelDialog(channel)
            self.imageDisplays[n] = QLabel(channel + " Channel")
            settingsLayout.addWidget(self.imageDisplays[n])
            settingsLayout.addWidget(channelDialogs[n])

        channelDialogs[0].valueChanged.connect(self.updateImageDisplayR)

        settingsLayout.addStretch()

        for n, channel in enumerate(["Final", "R", "G", "B", "A"]):
            self.imageDisplays[n] = QLabel()
            tabs.addTab(self.imageDisplays[n], channel)

        layout.addWidget(tabs, 1)
        layout.addLayout(settingsLayout, 0)
        self.setLayout(layout)

    def updateImageDisplayR(self, str):
        if(str.isdigit()):
            integer = int(str)
            col = QColor()
            col.setRgb (integer, integer, integer)
            self.imageDisplays[1].clear()
            self.imageDisplays[1].setAutoFillBackground(True)
            palette = self.imageDisplays[1].palette()
            palette.setColor(QPalette.Window, col)
            self.imageDisplays[1].setPalette(palette)
        else:
            self.imageDisplays[1].clear()

            # Load the image using OpenCV
            image = cv2.imread(str, cv2.IMREAD_COLOR)

            # Convert the image to RGB color space
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
            # Extract a single channel (e.g., red channel)
            channel = image[:, :, 0]  # Change the index to 1 or 2 for green or blue channel

            height, width = channel.shape
            channel_bytes = bytes(channel.data)
            q_image = QImage(channel_bytes, width, height, width, QImage.Format_Indexed8)

            pixmap = QPixmap.fromImage(q_image)

            self.imageDisplays[1].setPixmap(pixmap)

class Color(QWidget):

    def __init__(self, qColor):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, qColor)
        self.setPalette(palette)

class ChannelDialog(QFrame):
    valueChanged = pyqtSignal(str)

    def __init__(self, channel, parent = None):
        super(ChannelDialog, self).__init__(parent)
        
        self.layout = QVBoxLayout()

        self.setMinimumWidth(500)

        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)

        self.valueSlider = ValueSlider(0, 255)
        self.valueSlider.valueChanged.connect(self.updateValue)
        
        self.imageFileDialogue = ImageFileDialog("Select source for " + channel + " channel.")
        self.imageFileDialogue.valueChanged.connect(self.updateValue)

        #Combo box to select the type of source
        self.sourceSelectionCombo = QComboBox()
        self.sourceSelectionCombo.addItem('Image', self.imageFileDialogue)
        self.sourceSelectionCombo.addItem('Value (0-255)', self.valueSlider)

        self.sourceSelectionCombo.currentIndexChanged.connect(self.updateDisplay)

        self.layout.addWidget(self.sourceSelectionCombo)
        self.layout.addWidget(self.valueSlider)
        self.layout.addWidget(self.imageFileDialogue)
        self.valueSlider.hide()

        self.setLayout(self.layout)

    def updateDisplay(self, index):
        if(index == 0):
            self.valueSlider.hide()
            self.imageFileDialogue.show()
            self.updateValue(self.imageFileDialogue.getFilename())
        else:
            self.valueSlider.show()
            self.imageFileDialogue.hide()
            self.updateValue(self.valueSlider.value())

    def updateValue(self, value):
        self.valueChanged.emit(str(value))

class ValueSlider(QWidget):
    valueChanged = pyqtSignal(int)

    def __init__(self, min, max, parent = None):
        super(ValueSlider, self).__init__(parent)
        layout = QHBoxLayout()


        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min)
        self.slider.setMaximum(max)
        self.lineEdit = QLineEdit()
        self.lineEdit.setValidator(QIntValidator(min, max))

        self.lineEdit.setFixedWidth(30)

        self.slider.setValue(min)
        self.lineEdit.setText(str(min))

        self.slider.valueChanged.connect(self.matchLineToSlider)
        self.lineEdit.textChanged.connect(self.matchSliderToLine)

        layout.addWidget(self.lineEdit)
        layout.addWidget(self.slider)

        self.setLayout(layout)
    
    def matchLineToSlider(self):
        self.lineEdit.setText(str(self.slider.value()))
        self.valueChanged.emit(self.slider.value())
        
    def matchSliderToLine(self):
        text = self.lineEdit.text()
        if(len(text) > 0):
            self.slider.setValue(int(text))
            self.valueChanged.emit(int(text))

    def value(self):
        return self.slider.value()
        

class ImageFileDialog(QWidget):
    valueChanged = pyqtSignal(str)

    def __init__(self, prompt, parent = None):
        super(ImageFileDialog, self).__init__(parent)

        layout = QVBoxLayout()
        self.btn = QPushButton(prompt)
        self.btn.clicked.connect(self.getFile)
        self.lb = QLabel()
        layout.addWidget(self.btn)
        layout.addWidget(self.lb)
        self.setLayout(layout)
        self.fname = ""
		
    def getFile(self):
        nf = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\',"Image files (*.jpg *.png)")[0]
        if(nf != ""):
            self.fname = nf
            self.valueChanged.emit(self.fname)
            self.lb.setText(self.fname)

    def getFilename(self):
        return self.fname
		
				
def main():
    app = QApplication(sys.argv)
    win = MainAppWindow()

    win.show()
    sys.exit(app.exec_())
	
    
main()