"""
    Class contains function calls for Adafruit Fingerprint Sensor from PyFingerprint

    download_fingerprint() modified from example of Bastian Raschke
    PyFingerprint
    Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
    All rights reserved.
"""

from Pyfingerprint import PyFingerprint
import os
from PIL import Image

import Constants


class AdafruitHandler:
    @staticmethod
    def download_fingerprint(id_number):
        # Reads image and download it

        # Tries to initialize the sensor
        try:
            f = PyFingerprint('/dev/serial0', 57600, 0xFFFFFFFF, 0x00000000)

            if not f.verifyPassword():
                raise ValueError('The given fingerprint sensor password is wrong!')

        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            exit(1)

        # Tries to read image and download it
        try:
            image_name = Constants.FP_OUTPUT_NAME + str(id_number)

            # turn on LED for capture
            f.turnLEDon()

            print('Waiting for finger...')

            # Wait that finger is read
            while not f.readImage():
                pass

            print('Downloading image (this takes a while)...\n')
            # turn off LED after capture
            f.turnLEDoff()

            # Current image destination folder path and save to new image
            folder_path = Constants.FP_TEMP_FOLDER
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

            if image_name is None:
                image_name = 'fingerprint_' + str(len(os.listdir(folder_path)))

            # open as bitmap
            image_destination_bmp = folder_path + image_name + '.bmp'
            f.downloadImage(image_destination_bmp)

            # save as jpg
            img = Image.open(image_destination_bmp)
            image_destination_jpg = folder_path + image_name + '.jpg'
            img.save(image_destination_jpg)

            print('The image of %s was saved to %s.' % (image_name, folder_path))
            print('Finished capturing fingerprint %s.\n' % image_name)

        except Exception as e:
            print('Operation failed!')
            # print('Exception message: ' + str(e))
            raise Exception('An internal error occurred while handling the Adafruit Sensor.')
