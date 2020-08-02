from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import numpy as np
import sys
from picamera.array import PiRGBArray
from picamera import PiCamera
import serial

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.1)
ser.flush()

class Thread(QThread):
    global ser
    changePixmap = pyqtSignal(QImage)
    updateTable = pyqtSignal(list)
    count = 0
    def run(self):
        camera = PiCamera()
        camera.rotation = 180
        camera.resolution = (1280, 720)	# resolution
        camera.framerate = 30			# frame rate
        camera.iso = 800				# set ISO to the desired value
        camera = PiCamera()
        rawCapture = PiRGBArray(camera, size=camera.resolution)
        while True:
            if(ser.in_waiting > 0):
                cmd = ser.readline().decode('utf-8').rstrip()
                # print(cmd)
                if cmd == '1':
                    image = cv2.imread("image/{}.png".format(self.count))
                    self.count += 1
                    if self.count > 3:
                        self.count = 0

                    # camera.capture(rawCapture, format="bgr")
                    # image = rawCapture.array
                    
                    # process image
                    
                    rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 360, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "MCNEX"
        self.left = 600; self.top = 40
        self.width = 700; self.height = 700

        self.initUI()
    
    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)


        # show image
        self.cam_label = QLabel(self)
        self.cam_label.setGeometry(10,10,640,360)
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()
        self.cam_label.setStyleSheet("border-color: rgb(0, 173, 181);"
                                    "border-style: outset;"
                                    "border-width: 5px;"
                                    "border-radius: 10px;")

        self.show()
    

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.cam_label.setPixmap(QPixmap.fromImage(image))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
