# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 15:06:16 2019

@author: julien
"""
import logging

LOG = logging.ERROR
MAIN_LOG = logging.ERROR
VIDEO_LOG = logging.ERROR
UPLOAD_LOG = logging.ERROR
SCAN_LOG = logging.ERROR
PROCESS_CAMERA_LOG = logging.ERROR
SOCKET_LOG = logging.ERROR


#  Darknet conf
DARKNET_PATH = '/NNvision/darknet'

# If using tensorRT
LIB_PATH = '/NNvision/tkDNN/build'

DARKNET_CONF = {
        #'all': {
        #        'CFG': 'cfg/yolov3.cfg',
        #        'WEIGHTS': '../weights/yolov3.weights',
        #        'DATA':'/NNvision/python_client/coco_docker.data',
        #        'RESTRICT':('pottedplant', 'oven', 'bowl',)},
        'all_RT':{
                'WEIGHTS': '/NNvision/tkDNN/build/room_detector_fp16.rt',
                'RESTRICT':('toothbrush',)},
        # 'car': {
        #         'CFG': '../weights/protecia.cfg',
        #         'WEIGHTS':  '../weights/car.weights',
        #         'DATA': '/NNvision/weights/car_docker.data'},
        # 'person': {
        #         'CFG': '../weights/protecia.cfg',
        #         'WEIGHTS': '../weights/person.weights',
        #         'DATA': '/NNvision/weights/person_docker.data'},
        }

# hardware conf
INSTALL_PATH = '/NNvision/python_client'
FFMPEG = '/usr/local/bin/ffmpeg'
HARDWARE = 'nano'
UUID = '/NNvision/uuid/uuid'  # on nano
# UUID = '/proc/device-tree/chosen/ecid' on xavier

# python conf
PYTHON = 'python3'
THREATED_REQUESTS = True
SERVER = 'https://dev.protecia.com/'
SERVER_WS = 'wss://dev.protecia.com/'
VIDEO_REC_TIME = 10
VIDEO_SPACE = 30  # Go
QUEUE_SIZE = 10  # number of images to queue at max
SCAN_INTERVAL = 60  # seconds between each scan of the network to find onvif camera
RECORDED_DELAY = 2  # nb of days to store on backup video

# remote conf
SSH_SERVER_PORT = 2223
SSH_USER = 'tunnel'

# client conf
INIT_PASS = 'jznsjoa3z54d'
