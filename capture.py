from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import sys
import time

class Thread(QThread):
    img = pyqtSignal(np.ndarray)
    
    def run(self):
        # Camera Pi config
        self.camera = PiCamera()
        self.camera.rotation = 180
        self.camera.resolution = (2592, 1944)   # resolution
        self.camera.iso = 800				    # set ISO to the desired value
        self.rawCapture = PiRGBArray(self.camera, size=self.camera.resolution)

        # time to get camera warm up
        time.sleep(1)
        while True:
            self.camera.capture(self.rawCapture, format="bgr")
            image = self.rawCapture.array
            resize_img = cv2.resize(image, (972,729))

            self.img.emit(resize_img)
            time.sleep(1)
            self.rawCapture.truncate(0)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "MCNEX"
        self.left = 80; self.top = 200
        self.width = 1530; self.height = 880

        self.initUI()
    
    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setStyleSheet("background-color: rgb(171, 171, 171);")

        # show image
        self.cam_name = QLabel("CAMERA", self)
        self.cam_name.setGeometry(40, 40, 972, 55)
        self.cam_name.setAlignment(Qt.AlignCenter)
        self.cam_name.setStyleSheet("background-color: rgb(50, 130, 184);"
                                    "color: rgb(255, 255, 255);"
                                    "font: bold 14pt;")
        self.cam_label = QLabel(self)
        self.cam_label.setGeometry(40,95,972,729)
        th = Thread(self)
        th.img.connect(self.updateImage)
        th.start()
        self.cam_label.setStyleSheet("border-color: rgb(50, 130, 184);"
                                    "border-style: inset;"
                                    "border-width: 5px;")
        
        # Logo
        self.mcnex_logo = QLabel(self)
        self.mcnex_pixmap = QPixmap('logo/mcnex.png').scaled(273,130,Qt.KeepAspectRatio)
        self.mcnex_logo.setPixmap(self.mcnex_pixmap)
        self.mcnex_logo.setGeometry(1043, 40, 273, 130)
        self.uet_logo = QLabel(self)
        self.uet_pixmap = QPixmap('logo/uet.png').scaled(128,130,Qt.KeepAspectRatio)
        self.uet_logo.setPixmap(self.uet_pixmap)
        self.uet_logo.setGeometry(1337, 40, 128, 130)

        # Information
        self.info_label = QLabel(self)
        self.info_label.setGeometry(1050,264,420,240)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("background-color: rgb(50, 130, 184);"
                                    "color: rgb(255, 255, 255);"
                                    "font: bold 20pt;")

        # Capture button
        self.info_label = QPushButton("CAPTURE", self)
        self.info_label.setGeometry(1050,544,420,120)
        self.info_label.clicked.connect(self.clickCaptureButton)
        self.info_label.setStyleSheet("background-color: rgb(50, 130, 184);"
                                    "color: rgb(255, 255, 255);"
                                    "font: bold 20pt;")

        # Accept button
        self.start_button = QPushButton("ACCEPT",self)
        self.start_button.setGeometry(1050, 704, 180, 120)
        self.start_button.clicked.connect(self.clickAcceptButton)
        self.start_button.setStyleSheet("background-color: rgb(67, 138, 94);"
                                        "font: bold 20px;"
                                        "color:rgb(255, 255, 255);"
                                        "border-width: 5px;"
                                        "border-color: rgb(67, 138, 94);"
                                        "border-radius: 5px;")

        # Deny button
        self.start_button = QPushButton("Deny",self)
        self.start_button.setGeometry(1290, 704, 180, 120)
        self.start_button.clicked.connect(self.clickDenyButton)
        self.start_button.setStyleSheet("background-color: rgb(232, 80, 91);"
                                        "font: bold 20px;"
                                        "color:rgb(255, 255, 255);"
                                        "border-width: 5px;"
                                        "border-color: rgb(232, 80, 91);"
                                        "border-radius: 5px;")

        self.show()
    
    @pyqtSlot(np.ndarray)
    def updateImage(self, img):
        rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(972, 729, Qt.KeepAspectRatio)
        self.cam_label.setPixmap(QPixmap.fromImage(p))
    
    def clickCaptureButton(self):
        pass
    def clickAcceptButton(self):
        pass
    def clickDenyButton(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
