from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import time

if __name__ == "__main__":
    camera = PiCamera()
    camera.rotation = 180
    camera.resolution = (2592, 1952)    # resolution
    camera.iso = 800				    # set ISO to the desired value
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    count = 0
    time.sleep(1)
    while True:
        camera.capture(rawCapture, format="bgr")
        image = rawCapture.array
        resize_img = cv2.resize(image, (972,729))
        cv2.imshow("", resize_img)
        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite('image/{}.png'.format(count), resize_img)
            count += 1
        rawCapture.truncate(0)