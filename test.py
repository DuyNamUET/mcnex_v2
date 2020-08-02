import cv2
import os
import glob
import pickle 
from matplotlib import pyplot as plt
import numpy as np
# import serial
import time
# from picamera.array import PiRGBArray
# from picamera import PiCamera

refPt = []
cropping = False
img = None

def cameraConfig():
	camera = PiCamera()
	camera.rotation = 180
	camera.resolution = (1280, 720)	# resolution
	camera.framerate = 30			# frame rate
	camera.iso = 800				# set ISO to the desired value
	# camera.awb_mode = 'fluorescent'
	return camera

def click_and_crop(event, x, y, flags, param):

    global refPt, cropping

    if event==cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True
    elif event==cv2.EVENT_LBUTTONUP:
        refPt.append((x, y))
        cropping = False

        cv2.rectangle(img, refPt[0], refPt[1], (0, 255, 0), 2)

def get_data(img_, name_img):

    global img, refPt
    img = img_
    clone = img.copy()
    cv2.namedWindow("{}".format(name_img))
    cv2.setMouseCallback("{}".format(name_img), click_and_crop)
    idx = 0

    if not os.path.exists("{}".format(name_img)):
        os.mkdir(name_img)

    boxes = []

    while True:

        cv2.imshow("{}".format(name_img), img)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):
            break

        if len(refPt) == 2:
            roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
            boxes.append(refPt)
            img = cv2.rectangle(img, refPt[0], refPt[1], (255, 0, 0), 2)
            cv2.imwrite("{}/{}.png".format(name_img, idx), roi)
            refPt = []
            idx += 1

    cv2.destroyWindow("{}".format(name_img))
    pickle.dump(boxes, open("{}/coords.txt".format(name_img), 'wb'))

def get_data_for_all_img(top_dir, ext=["jpg", "png"]):

    all_img_paths = []
    for i in glob.glob("{}/*".format(top_dir)):
        if i.split(".")[-1] in ext:
            all_img_paths.append(i)
    
    print(all_img_paths)
    for img_path in all_img_paths:
        img = cv2.imread(img_path)
        name_img = img_path.split('/')[-1].split('.')[0]
        get_data(img, name_img)

def show_hist(top_dir, ext=["jpg", "png"], evaluate=False, thresh=95):

    all_img_paths = []

    for root, dirs, files in os.walk(top_dir):
        for name in files:
            if name.split(".")[-1] in ext:
                all_img_paths.append(os.path.join(root, name))
    print(all_img_paths)
    imgs = []
    tp = []
    fn = []
    ct = 0 # counting for true lable
    cf = 0 # counting for false label
    nt = 0 # number of true label

    for img_path in all_img_paths:
        print(img_path)
        img = cv2.imread(img_path)
        img_gray = cv2.imread(img_path, 0)
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h,w, _  = img.shape
        imgs.append(img)

        histR = cv2.calcHist(img, [0], None, [256], [0, 256])
        histG = cv2.calcHist(img, [1], None, [256], [0, 256])
        histB = cv2.calcHist(img, [2], None, [256], [0, 256])
        histgray = cv2.calcHist(img_gray, [0], None, [256], [0, 256])

        print(sum(histR[100:]), sum(histgray[95:]))

        if not evaluate:
            plt.subplot(221); plt.imshow(img, "gray")

            plt.subplot(222); plt.plot(histR)
            plt.subplot(223); plt.plot(histG)
            plt.subplot(224); plt.plot(histB)
            plt.subplot(224); plt.plot(histgray)
            plt.xlim([0,256])

            plt.show()
        else:
            label = img_path.split("/")[-1].split(".")[0].split("_")[1]
            tmp = sum(histgray[95:])
            if label == "1":
                nt += 1
            if (tmp > 0 and label=='1') or (tmp==0 and label=="0"):
                if tmp > 0 and label=='1':
                    tp.append(tmp)
                    ct += 1
            if (tmp == 0 and label=='1') or (tmp>0 and label=="0"):
                cf += 1

    print(ct, cf, nt)
    print(np.min(tp))
    #print(len(hist))

def test(raw_top_dir, cropped_top_dir, thresh):
    
    for subdir in glob.glob("{}/*".format(cropped_top_dir)):
        print("{}/{}.png".format(raw_top_dir, subdir.split("/")[-1]))
        img = cv2.imread("{}/{}.png".format(raw_top_dir, subdir.split("/")[-1]))
        print(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        coords = pickle.load(open("{}/coords.txt".format(subdir), 'rb'))

        for coord in coords:
            roi = gray[coord[0][1]:coord[1][1], coord[0][0]:coord[1][0]]
            histgray = cv2.calcHist(roi, [0], None, [256], [0, 256])
            th = sum(histgray[thresh:])
            print(th)
            if th > 0:
                img = cv2.rectangle(img, coord[0], coord[1], (0, 255, 0), 1)
            else:
                img = cv2.rectangle(img, coord[0], coord[1], (0, 0, 255), 1)
        
        cv2.imshow("test", img)
        cv2.waitKey(0)

def test_kl(raw_top_dir, path_cam, path_no_cam):
    
    coords = pickle.load(open("center.txt", 'rb'))

    for path in glob.glob("{}/*".format(raw_top_dir)):
        if not os.path.isfile(path):
            continue
        img = cv2.imread(path)
        
        count = 0

        for coord in coords:
            roi = img[coord[0][1]:coord[1][1], coord[0][0]:coord[1][0]]
            th = having_cam(roi, "{}/{}".format(path_no_cam, count),\
                                "{}/{}".format(path_cam, count))
            # print(th)
            count += 1
            if th > 0:
                img = cv2.rectangle(img, coord[0], coord[1], (0, 255, 0), 1)
            else:
                img = cv2.rectangle(img, coord[0], coord[1], (0, 0, 255), 1)
        
        cv2.imshow("test", img)
        cv2.waitKey(0)

def get_data_with_fixed_coords(top_dir="data/test", coords_file="coords.txt", out_dir="cropped1", ext=["png", "jpg"], save_to_index=True):
    
    if not os.path.exists("{}".format(out_dir)):
        os.makedirs(out_dir)
    coords = pickle.load(open(coords_file, 'rb'))

    all_img_paths = []
    for i in glob.glob("{}/*".format(top_dir)):
        if i.split(".")[-1] in ext:
            all_img_paths.append(i)
    
    print(all_img_paths)
    i = 0
    for img_path in all_img_paths:
        img = cv2.imread(img_path)
        name_img = img_path.split('/')[-1].split('.')[0]
        for j, coord in enumerate(coords):
            roi = img[coord[0][1]:coord[1][1], coord[0][0]:coord[1][0]]
            if not save_to_index:
                cv2.imwrite("{}/{}.png".format(out_dir, i), roi)
            else:
                dst_dir = "{}/{}".format(out_dir, j)
                if not os.path.exists("{}".format(dst_dir)):
                    os.makedirs(dst_dir)
                cv2.imwrite("{}/{}.png".format(dst_dir, i), roi)

            i+=1

def kl_distance(dist1, dist2, norm=True):
    
    assert len(dist1)==len(dist2)
    
    normed_dist1 = dist1
    normed_dist2 = dist2
    d = 0

    if not norm:
        s1 = sum(dist1)
        normed_dist1 = dist1/s1
        s2 = sum(dist2)
        normed_dist2 = dist2/s2
    # print(normed_dist1, normed_dist2)
    #for p1, p2 in zip(normed_dist1, normed_dist2):
    #    d += p1*np.log2((p1+0.01)/(p2+0.01))
    e1 = 0
    e2 = 0
    i = 0
    
    # /mu
    for p1, p2 in zip(normed_dist1, normed_dist2):
        e1 += p1*i
        e2 += p2*i
        i += 1
    #for p1, p2 in zip(normed_dist1, normed_dist2):
    #    d += np.sqrt(p1*p2)

    return np.abs(e1-e2)

def having_cam(img, no_cam_dir, cam_dir, channel=2):
    
    if channel < 0:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img = [img[:,:,channel]]
    
    hist_img = cv2.calcHist(img, [0], None, [256], [0, 256])
    s_no_cam = 0
    s_cam = 0

    for no_cam_img in glob.glob("{}/*".format(no_cam_dir)):

        im = cv2.imread(no_cam_img)
        if channel < 0:
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        else:
            im = [im[:,:,channel]]
    
        hist_no_cam = cv2.calcHist(im, [0], None, [256], [0, 256])
        s_no_cam += kl_distance(hist_img, hist_no_cam, norm=False)
        break

    
    for cam_img in glob.glob("{}/*".format(cam_dir)):

        im = cv2.imread(cam_img)
        if channel < 0:
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        else:
            im = [im[:,:,channel]]

        hist_cam = cv2.calcHist(im, [0], None, [256], [0, 256])
        s_cam += kl_distance(hist_img, hist_cam, norm=False)
        break
    # print(s_cam, s_no_cam)
    return s_cam < s_no_cam 


def run_kl(img, path_cam, path_no_cam):
    # img = cv2.imread("{}/{}.png".format(raw_top_dir, subdir.split("/")[-1]))

    coords = pickle.load(open("coords.txt", 'rb'))

    # Initialize output to save answers
    output = np.zeros(21)
    count = 0

    for coord in coords:
        roi = img[coord[0][1]:coord[1][1], coord[0][0]:coord[1][0]]
        th = having_cam(roi, "{}/{}".format(path_no_cam, count),\
                "{}/{}".format(path_cam, count))
        # print(th)
        if th:
            img = cv2.rectangle(img, coord[0], coord[1], (0, 255, 0), 1)
            output[count] = 1
        else:
            img = cv2.rectangle(img, coord[0], coord[1], (0, 0, 255), 1)
        count += 1
    
    cv2.imshow("test", img)
    cv2.waitKey(1)
    return output

def run(img, thresh):
    # img = cv2.imread("{}/{}.png".format(raw_top_dir, subdir.split("/")[-1]))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    coords = pickle.load(open("coords.txt", 'rb'))

    # Initialize output to save answers
    output = np.zeros(21)
    count = 0

    for coord in coords:
        roi = gray[coord[0][1]:coord[1][1], coord[0][0]:coord[1][0]]
        histgray = cv2.calcHist(roi, [0], None, [256], [0, 256])
        th = sum(histgray[thresh:])
        # print(th)
        if th > 0:
            img = cv2.rectangle(img, coord[0], coord[1], (0, 255, 0), 1)
            output[count] = 1
        else:
            img = cv2.rectangle(img, coord[0], coord[1], (0, 0, 255), 1)
        count += 1
    
    cv2.imshow("test", img)
    cv2.waitKey(1)
    return output
        
# compare histogram of positive and negative image
# positive: img_1.xxx ; negative img_0.xxx
# we can use 2 averaged distribution is this function to decide which distribution will be in the future
def visualize_choosing_thresh_hist(top_dir, ext=["jpg", "png"]):
    
    neg_imgs = []
    pos_imgs = []
    num_neg_samples = 0
    num_pos_samples = 0

    for root, dirs, files in os.walk(top_dir):
        for name in files:
            if name.split(".")[-1] in ext:
                path = os.path.join(root, name)
                label = name.split(".")[0].split("_")[1]
                if label=="0":
                    neg_imgs.append(path)
                    num_neg_samples += 1
                if label=="1":
                    pos_imgs.append(path)
                    num_pos_samples += 1
    neg_hist = None
    pos_hist = None
    
    for neg in neg_imgs:
        img = cv2.imread(neg, 0)
        histgray = cv2.calcHist(img, [0], None, [256], [0, 256])
        if neg_hist is None:
            neg_hist = np.array(histgray)
        else:
            neg_hist += np.array(histgray)

    #neg_hist /= num_neg_samples

    for pos in pos_imgs:
        img = cv2.imread(pos, 0)
        histgray = cv2.calcHist(img, [0], None, [256], [0, 256])
        if pos_hist is None:
            pos_hist = np.array(histgray)
        else:
            pos_hist += np.array(histgray)

    #pos_hist /= num_pos_samples
    plt.plot(neg_hist)
    plt.plot(pos_hist)
    plt.xlim([0,256])
    plt.show()

def histogramImage(img):
    cv2.imshow("",img)
    cv2.waitKey(1)
    coords = pickle.load(open("coords.txt", 'rb'))
    for coord in coords:
        # print(coord)
        roi = img[coord[0][1]:coord[1][1], coord[0][0]:coord[1][0]]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        plt.subplot(221); plt.imshow(roi, "gray")
        histR = cv2.calcHist(roi, [0], None, [256], [0, 256])
        histG = cv2.calcHist(roi, [1], None, [256], [0, 256])
        histB = cv2.calcHist(roi, [2], None, [256], [0, 256])
        histgray = cv2.calcHist(roi_gray, [0], None, [256], [0, 256])

        print(sum(histR[100:]), sum(histgray[95:]))

        plt.subplot(222); plt.plot(histR)
        plt.subplot(223); plt.plot(histG)
        plt.subplot(224); plt.plot(histB)
        plt.subplot(224); plt.plot(histgray)
        plt.xlim([0,256])

        plt.show()


def serial_receiver(ser):
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
        return line

def captureAndGetData():
    camera = cameraConfig()
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    time.sleep(0.2)                 # allow the camera to warmup
    
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        cv2.imshow("Frame", image)      # show the frame
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)          # clear the stream in preparation for the next frame
        
        if key == ord("a"):             # save image
            path = "data/test/img-" + str(time.time()) + ".png"
            cv2.imwrite(path, image)
            #break

    #get_data_for_all_img("run/test")

def mainWithoutSerial():
    # Setup camera pi
    camera = cameraConfig()
    rawCapture = PiRGBArray(camera)
    time.sleep(0.2)  

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array

        # out = run(image, thresh=100)
        out = run_kl(image, path_no_cam="cropped1/no_cam",\
             path_cam="cropped1/cam")

        # Initialize message
        data = ""
        for i in out:
            data = data + str(int(i))
        data = data + "\n"
        print(data) 
            
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)                  # clear the stream
        if key == ord("q"):                             # quit
            break

def main():
    # Setup camera pi
    camera = cameraConfig()
    rawCapture = PiRGBArray(camera)
    time.sleep(0.2)

    # Serial setup
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.1)
    ser.flush()    

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array

        cmd = ""
        cmd = serial_receiver(ser)
        print(cmd)
        # out = run(image, thresh=100)
        out = run_kl(image, path_no_cam="cropped1/no_cam", path_cam="cropped1/cam")

        # Initialize message
        data = ""
        for i in out:
            data = data + str(int(i))
        data = data + "e"
        # print(data) 

        # print(cmd)
        # Send message
        if(cmd == '9'):
            ser.write(data.encode('utf-8'))
            print(data)
            # time.sleep(0.1)
            
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)                  # clear the stream
        if key == ord("q"):                             # quit
            break

# if __name__=="__main__":
    # get_data_for_all_img("data/test")
    # show_hist("cropped1/no_cam") 
    # visualize_choosing_thresh_hist("cropped/train")
    # test_kl(raw_top_dir="data/test", path_no_cam="new_cropped/no_cam",\
    #         path_cam="new_cropped/cam")
    # get_data_with_fixed_coords(top_dir="data/test/origin_cam", out_dir="new_cropped/cam")
    # get_data_with_fixed_coords(top_dir="data/test/origin_no_cam", out_dir="new_cropped/no_cam")
    
    # View histogram
    # img = cv2.imread("data/test/img-1594952145.9028916.png")
    # histogramImage(img)
    
    # Get data mode
    # captureAndGetData()

    # Test model without serial
    # mainWithoutSerial()

    # Run mode
    # main()
