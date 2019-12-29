"""Example cli program to drive the cameras, intended for testing only."""
import argparse
import cv2
import numpy as np
from camera_py import (camera_init, sSO2Parameters, config,
                       camera_autosetExposure, camera_get, camera_uninit)


def main():
    parser = argparse.ArgumentParser(description='Camera example program')
    parser.add_argument('camid', help='camera identifier, <a|b>')
    parser.add_argument('filename', help='output filename')
    args = parser.parse_args()

    cam = sSO2Parameters()
    cam.identifier = args.camid

    conf = config()
    conf.dBufferlength = 1376256
    conf.dFixTime = 0
    conf.dExposureTime_a = 250000
    conf.dExposureTime_b = 250000

    # testing functions
    stat = camera_init(cam)
    if stat:
        print("failed to init camera")
        return -1

    # autoset exposure
    stat = camera_autosetExposure(cam, conf)
    if stat:
        print("failed to find exposure")
        return -1

    generate_png = 1

    # trigger image and wait for result
    stat = camera_get(cam, 1)
    if stat:
        print("failed to get image from camera")
        return -1

    if args.filename:
        filename = args.filename
    else:
        filename = "outfile.{}".format("png" if generate_png else "raw")

    width, height = 1344, 1024

    if generate_png:
        # create new image to hold the loaded data
        img = np.zeros((width, height, 1), np.uint16)

        arr = []
        for i in range(width * height):
            arr.append(cam.getBuffer(i))

        arrarr = np.array(arr)
        img = np.reshape(arrarr, (height, width, 1)).astype(np.uint16)

        # rotate image
        # img = np.flip(img, 1)

        # upsample image to use full 16bit range (the image will be very dark
        # otherwise)
        img *= 16

        cv2.imwrite(filename, img)
    else:
        import array
        import sys

        # Create an array of 16-bit signed integers

        arr = []
        for i in range(width * height):
            arr.append(cam.getBuffer(i))

        a = array.array("h", arr)

        # Write to file in big endian order
        if sys.byteorder == "little":
            a.byteswap()
        with open("data", "wb") as f:
            a.tofile(f)

        with open(filename, 'wb') as file:

            arrarr = np.array(arr)
            arrarr.tofile(file)
            # imgdata = bytearray(arrarr)
            # file.write(imgdata)
            print("IMAGE: {} saved successful".format(filename))

    stat = camera_uninit(cam)
    print("end test programm")
    return 0


if __name__ == "__main__":
    main()
