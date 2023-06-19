from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2
import numpy as np
import sys

from PyQt5.QtWidgets import QWidget

def is_grayscale(image):
    return len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1)

def has_alpha_channel(image):
    return image.shape[2] == 4

def create_checkerboard_image(image_size=512, tile_size=32, tile_color_01=150, tile_color_02=225):
    # Create an empty image with the desired size
    image = np.zeros((image_size, image_size), dtype=np.uint8)
    # Generate the checkerboard pattern
    for i in range(0, image_size, tile_size):
        for j in range(0, image_size, tile_size):
            value = tile_color_01 if ((i // tile_size) + (j // tile_size)) % 2 == 0 else tile_color_02
            image[i:i+tile_size, j:j+tile_size] = value
    return image

class MainAppWindow(QMainWindow):
    def __init__(self):
        super(MainAppWindow, self).__init__()
        self.setGeometry(200, 200, 1280, 720)
        self.setWindowTitle("Channel Packer Tool")
        self.initUI()

    def initUI(self):
        self.setCentralWidget(PBRMaskGenerator())

class PBRMaskGenerator(QWidget):
    def __init__(self):
        super(PBRMaskGenerator, self).__init__()

        layout = QHBoxLayout()
        previews = QVBoxLayout()

        self.resolutionLayout = QHBoxLayout()

        self.resolutionSetting = QComboBox()
        self.resolutionSetting.addItem("Match First Texture", -1)
        self.resolutionSetting.addItem("4096x4096", 4096)
        self.resolutionSetting.addItem("2048x2048", 2048)
        self.resolutionSetting.addItem("1024x1024", 1024)
        self.resolutionSetting.addItem("512x512", 512)
        self.resolutionSetting.addItem("256x256", 256)
        self.resolutionSetting.addItem("128x128", 128)
        self.resolutionSetting.addItem("Custom", 0)

        self.resolutionSetting.currentIndexChanged.connect(self.onResolutionSettingChange)

        self.resolution = ValueSlider(128, 4096)
        self.resolution.setValue(1024)
        self.resolution.hide()

        settingsLayout = QVBoxLayout()
        self.channelDialogs = [None] * 4

        channelHeaderColors = ['red', 'green', 'blue', 'grey']

        for n, channel in enumerate(["R", "G", "B", "A"]):
            self.channelDialogs[n] = ChannelDialog(channel, channelHeaderColors[n])
            self.channelDialogs[n].valueChanged.connect(self.renderFinalResult)
            settingsLayout.addWidget(self.channelDialogs[n])

        settingsLayout.addStretch()

        previews.addWidget(QLabel("Final"))
        self.resolutionLayout.addWidget(self.resolutionSetting, 0)
        self.resolutionLayout.addWidget(self.resolution)
        self.resolutionLayout.addStretch()

        self.finalPreview = QLabel()
        self.finalPreviewBG = QLabel()
        self.finalPreview.setFixedSize(512, 512)
        self.finalPreviewBG.setFixedSize(512, 512)
        self.finalPreview.setScaledContents(True)
        self.finalPreviewBG.setScaledContents(True)

        q_bg_image = QImage(create_checkerboard_image().data, 512, 512, 512, QImage.Format_Grayscale8)
        q_pixmap = QPixmap.fromImage(q_bg_image)
        self.finalPreviewBG.setPixmap(q_pixmap)


        self.finalPreviewLayout = QStackedLayout()
        self.finalPreviewLayout.setStackingMode(QStackedLayout.StackAll)
        self.finalPreviewLayout.addWidget(self.finalPreviewBG)
        self.finalPreviewLayout.addWidget(self.finalPreview)

        self.saveButton = QPushButton("Save Result")
        self.saveButton.clicked.connect(self.saveImage)
        self.saveButtonLayout = QHBoxLayout()
        self.saveButtonLayout.addWidget(self.saveButton)
        self.saveButtonLayout.addStretch()

        previews.addLayout(self.resolutionLayout)
        previews.addLayout(self.finalPreviewLayout)
        previews.addLayout(self.saveButtonLayout)
        previews.addStretch()

        layout.addLayout(previews, 1)
        layout.addLayout(settingsLayout, 0)
        self.setLayout(layout)

    def saveImage(self):
        fname = QFileDialog.getSaveFileName(self, 'Save File', None, "Images (*.png)")[0]
        if(len(fname)<=0):
            return
        print ("Saving result to " + fname)
        cv2.imwrite(fname, self.packed_texture)



    def onResolutionSettingChange(self, value):
        data = self.resolutionSetting.currentData()
        if(data == 0):
            self.resolution.show()
        elif(data == -1):
            self.resolution.hide()

            res = 1024
            
            res = max(res, red_texture = self.channelDialogs[0].getImage().shape[0])
            res = max(res, green_texture = self.channelDialogs[1].getImage().shape[0])
            res = max(res, blue_texture = self.channelDialogs[2].getImage().shape[0])
            res = max(res, alpha_texture = self.channelDialogs[3].getImage().shape[0])

            self.resolution.setValue(res)
        else:
            self.resolution.hide()
            self.resolution.setValue(self.resolutionSetting.currentData())

    def renderFinalResult(self):
        # Load the separate textures for the channels
        red_texture = self.channelDialogs[0].getImage()
        green_texture = self.channelDialogs[1].getImage()
        blue_texture = self.channelDialogs[2].getImage()
        alpha_texture = self.channelDialogs[3].getImage()

        res = self.resolution.value()

        red_texture = cv2.resize(red_texture, (res, res))
        green_texture = cv2.resize(green_texture, (res, res))
        blue_texture = cv2.resize(blue_texture, (res, res))
        alpha_texture = cv2.resize(alpha_texture, (res, res))

        red_channel_index = self.channelDialogs[0].getChannel()
        green_channel_index = self.channelDialogs[1].getChannel()
        blue_channel_index = self.channelDialogs[2].getChannel()
        alpha_channel_index = self.channelDialogs[3].getChannel()


        red_channel = red_texture[:] if is_grayscale(red_texture) else red_texture[:, :, red_channel_index]
        green_channel = green_texture[:] if is_grayscale(green_texture) else green_texture[:, :, green_channel_index]
        blue_channel = blue_texture[:] if is_grayscale(blue_texture) else blue_texture[:, :, blue_channel_index]
        alpha_channel = alpha_texture[:] if is_grayscale(alpha_texture)  else alpha_texture[:, :, alpha_channel_index]

        channel_list = [blue_channel, green_channel, red_channel, alpha_channel]
        disp_channel_list = [red_channel, green_channel, blue_channel, alpha_channel]

        self.packed_texture = np.dstack(channel_list)

        disp_pt = np.dstack(disp_channel_list)
        
        num_channels = disp_pt.shape[2]
        bytes_per_line = res * num_channels

        q_image = QImage(disp_pt.data, res, res, bytes_per_line, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(q_image)
        self.finalPreview.setPixmap(pixmap)

class ChannelDialog(QFrame):
    valueChanged = pyqtSignal()

    def __init__(self, channel, color, parent = None):
        super(ChannelDialog, self).__init__(parent)
        
        self.layout = QHBoxLayout()
        self.optionsLayout = QVBoxLayout()

        self.colorHeader = QWidget()
        self.colorHeader.setAutoFillBackground(True)
        palette = self.colorHeader.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.colorHeader.setPalette(palette)

        self.colorHeader.setFixedWidth(30)

        self.layout.addWidget(self.colorHeader, 0)

        self.preview = QLabel()
        self.preview.setScaledContents(True)
        self.preview.setFixedWidth(150)
        self.preview.setFixedHeight(150)
        self.layout.addWidget(self.preview, 0)

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


        self.optionsLayout.addWidget(self.sourceSelectionCombo)
        self.optionsLayout.addWidget(self.valueSlider)
        self.optionsLayout.addWidget(self.imageFileDialogue)
        self.valueSlider.hide()


        self.layout.addLayout(self.optionsLayout, 1)
        self.setLayout(self.layout)
        self.updateValue(0)

    def isFileImage(self):
        return self.sourceSelectionCombo.currentIndex() == 0

    def getImage(self):
        # if a file image
        if(self.isFileImage()):
            fname = self.imageFileDialogue.getFilename()
            image = cv2.imread(fname, cv2.IMREAD_UNCHANGED) if len(fname) > 0 else None
            if(image is not None):
                if(is_grayscale(image)):
                    image = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
                invert = self.imageFileDialogue.getInvert()
                if(invert):
                    image = 255-image
                return image
            
        #else, use tone
        gray_image = np.full((512, 512), self.valueSlider.value(), dtype=np.uint8)
        return gray_image

    def getChannel(self):
        return self.imageFileDialogue.getChannel()

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
        self.valueChanged.emit()
        self.updateImageDisplay(str(value))

    def updateImageDisplay(self, str):
        if(str.isdigit()):
            integer = int(str)
            col = QColor()
            col.setRgb (integer, integer, integer)
            self.preview.clear()
            self.preview.setAutoFillBackground(True)
            palette = self.preview.palette()
            palette.setColor(QPalette.Window, col)
            self.preview.setPalette(palette)
        elif(len(str) > 0):
            self.preview.clear()

            # Load the image using OpenCV
            image = self.getImage()

            channel = self.getChannel()

            if(image is not None):
                # Convert the image to RGB color space
                # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
                # Extract a single channel (e.g., red channel)
                grayscale = is_grayscale(image)
                hasAlpha = False if(grayscale) else has_alpha_channel(image)

                if(not hasAlpha and channel == 3):
                    channel = 2

                image_channel = image if(grayscale) else image[:, :, channel]

                height, width = image_channel.shape
                channel_bytes = bytearray(image_channel.data)
                
                q_image = QImage(channel_bytes, width, height, width, QImage.Format_Indexed8)
                pixmap = QPixmap.fromImage(q_image)
                self.preview.setPixmap(pixmap)

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

    def setValue(self, value):
        self.slider.setValue(value)

    def value(self):
        return self.slider.value()
        

class ImageFileDialog(QWidget):
    valueChanged = pyqtSignal(str)

    def __init__(self, prompt, parent = None):
        super(ImageFileDialog, self).__init__(parent)

        self.channelSelectionCombo = QComboBox()
        self.channelSelectionCombo.setFixedWidth(50)
        self.channelSelectionCombo.addItem('R', 2)
        self.channelSelectionCombo.addItem('G', 1)
        self.channelSelectionCombo.addItem('B', 0)
        self.channelSelectionCombo.addItem('A', 3)
        self.channelSelectionCombo.currentIndex=0
        self.channelSelectionCombo.currentIndexChanged.connect(self.onSourceChanged)

        self.invert = QCheckBox()
        self.invert.stateChanged.connect(self.onSourceChanged)

        layout = QVBoxLayout()
        hLayout = QHBoxLayout()
        self.btn = QPushButton(prompt)
        self.btn.clicked.connect(self.getFile)
        self.lb = QLabel()
        hLayout.addWidget(self.btn)
        hLayout.addWidget(self.channelSelectionCombo)
        hLayout.addWidget(QLabel("Invert?"))
        hLayout.addWidget(self.invert)
        layout.addLayout(hLayout)
        layout.addWidget(self.lb)
        self.setLayout(layout)
        self.fname = ""

    def getChannel(self):
        return self.channelSelectionCombo.currentData()
    
    def getInvert(self):
        return self.invert.isChecked()

    def onSourceChanged(self):
        self.valueChanged.emit(self.fname)

    def getFile(self):
        nf = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\',"Image files (*.jpg *.png)")[0]
        if(nf != ""):
            self.fname = nf
            image = cv2.imread(self.fname, cv2.IMREAD_UNCHANGED) if len(self.fname) > 0 else None
            label = self.fname

            if(image is not None):
                
                if(is_grayscale(image)):
                    self.channelSelectionCombo.model().item(1).setEnabled(True)
                    self.channelSelectionCombo.model().item(1).setEnabled(False)
                    self.channelSelectionCombo.model().item(2).setEnabled(False)
                    self.channelSelectionCombo.model().item(3).setEnabled(False)
                    label += "\nGrayscale (Only take R channel)"
                elif(not has_alpha_channel(image)):
                    self.channelSelectionCombo.model().item(1).setEnabled(True)
                    self.channelSelectionCombo.model().item(1).setEnabled(True)
                    self.channelSelectionCombo.model().item(2).setEnabled(True)
                    self.channelSelectionCombo.model().item(3).setEnabled(False)
                    label += "\nNo Alpha (A channel disabled)"
                else:
                    self.channelSelectionCombo.model().item(1).setEnabled(True)
                    self.channelSelectionCombo.model().item(1).setEnabled(True)
                    self.channelSelectionCombo.model().item(2).setEnabled(True)
                    self.channelSelectionCombo.model().item(3).setEnabled(True)

            self.onSourceChanged()
            self.lb.setText(label)

    def getFilename(self):
        return self.fname
		
				
def main():
    app = QApplication(sys.argv)
    win = MainAppWindow()

    win.show()
    sys.exit(app.exec_())
	
    
main()