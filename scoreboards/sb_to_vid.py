import cv2
import os
import sys
import glob
from natsort import natsorted


def export(sb_type, pps):
    global size, out
    # fps = int(fps)
    wd = os.getcwd().replace('/scoreboards','')
    images_source = f'{wd}/output/debug/{sb_type}/*.png'
    img_array = []
    img_list = glob.glob(images_source)
    img_list = natsorted(img_list)
    base_image = cv2.imread(img_list[0])
    h, w, l = base_image.shape
    size = (w, h)
    for filename in img_list:
        img = cv2.imread(filename)
        # for r in range(int(int(fps) / int(pps))):
        #     if flicker and r == int((int(fps) / int(pps))) - 1:
        #         img_array.append(base_image)
        #         break
        img_array.append(img)
    out = cv2.VideoWriter(f'{sb_type}.avi', cv2.VideoWriter_fourcc('M','J','P','G'), int(pps), size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release


if __name__ == '__main__':
    export('basketball','1')
    try:
        size = (0, 0)
        export(str(sys.argv[1]), str(sys.argv[2]))
    except Exception as e:
        print(e)
