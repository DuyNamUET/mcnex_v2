import glob
import pickle
import os
import cv2
import numpy as np
import test

drawing = False 
rec = []
def draw_rectange(event, x, y, flags, param):
    global drawing, rec
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        rec = [(x,y)]
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rec.append((x,y))

def get_mask(img_path):
    global rec
    areas = []

    img = cv2.imread(img_path)
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_rectange)

    while(True):
        if len(rec) == 2:
            cv2.rectangle(img, rec[0], rec[1], (0,255,0), 2)
            areas.append(rec)
            rec = []

        cv2.imshow('image',img)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
    cv2.destroyAllWindows()
    # print(areas)
    pickle.dump(areas, open("center.txt", 'wb'))

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

    for cam_img in glob.glob("{}/*".format(cam_dir)):

        im = cv2.imread(cam_img)
        if channel < 0:
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        else:
            im = [im[:,:,channel]]

        hist_cam = cv2.calcHist(im, [0], None, [256], [0, 256])
        s_cam += kl_distance(hist_img, hist_cam, norm=False)
    # print(s_cam, s_no_cam)
    return s_cam < s_no_cam 

def get_data_with_fixed_coords(top_dir="data/test", coords_file="center.txt", out_dir="cropped1", ext=["png", "jpg"], save_to_index=True):
    
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

def testWithImage(dir, ext=["png", "jpg"]):
    areas = pickle.load(open("center.txt", 'rb'))
    all_img_paths = []
    for i in glob.glob("{}/*".format(dir)):
        if i.split(".")[-1] in ext:
            all_img_paths.append(i)

    for img_path in all_img_paths:
        img = cv2.imread(img_path)
        data = []  # data of center 
        count = 0
        for area in areas:
            roi = img[area[0][1]:area[1][1], area[0][0]:area[1][0]]
            th = having_cam(roi, "new_cropped/no_cam/{}".format(count),\
                                "new_cropped/cam/{}".format(count))
            if th > 0:
                img = cv2.rectangle(img, area[0], area[1], (0, 255, 0), 1)
                data.append(1)
            else:
                img = cv2.rectangle(img, area[0], area[1], (0, 0, 255), 1)
                data.append(0)
            count += 1
        # print(data)
        cv2.imshow("", img)
        cv2.waitKey(0)
        # return data

def runDetectImage(img):
    areas = pickle.load(open("center.txt", 'rb'))
    data = np.array([])  # data of center 
    count = 0
    for area in areas:
        roi = img[area[0][1]:area[1][1], area[0][0]:area[1][0]]
        th = having_cam(roi, "new_cropped/no_cam/{}".format(count),\
                            "new_cropped/cam/{}".format(count))
        if th > 0:
            # img = cv2.rectangle(img, area[0], area[1], (0, 255, 0), 1)
            data = np.append(data, np.array([1]))
        else:
            # img = cv2.rectangle(img, area[0], area[1], (0, 0, 255), 1)
            data = np.append(data, np.array([0]))
        count += 1
    return data

# if __name__ == "__main__":    
    # WARNING - Get area to processing
    # get_mask("image/cam/0.png")
    # get_data_with_fixed_coords(top_dir="image/cam", out_dir="new_cropped/cam")
    # get_data_with_fixed_coords(top_dir="image/no_cam", out_dir="new_cropped/no_cam")
    
    # out = 
    # testWithImage("image/cam")
    # print(out)
