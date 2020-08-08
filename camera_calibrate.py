from picamera.array import PiRGBArray
from picamera import PiCamera
import glob
import pickle
import os
import cv2
import numpy as np
import time

if __name__ == "__main__":
	camera = PiCamera()
	camera.rotation = 180
	camera.resolution = (2592, 1952)    # resolution
	camera.iso = 800				    # set ISO to the desired value
	rawCapture = PiRGBArray(camera, size=camera.resolution)
    
	time.sleep(0.8)
	areas = pickle.load(open("center.txt", 'rb'))
	while True:
		camera.capture(rawCapture, format="bgr")
		image = rawCapture.array
		resize_img = cv2.resize(image, (972,729))
		for area in areas:
			img = cv2.rectangle(resize_img, area[0], area[1], (0, 0, 255), 1)
		cv2.imshow("", resize_img)
		key = cv2.waitKey(0) & 0xFF
		if key == ord('q'):
			break
		rawCapture.truncate(0)