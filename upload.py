# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 16:14:52 2019

@author: julien
"""
import requests
import settings
from log import Logger
import time
import json
from utils import get_conf

logger = Logger(__name__, level=settings.UPLOAD_LOG).run()


def uploadImageRealTime(Q):
    logger.warning('starting upload real time image')
    while True:
        cam, result, img, resize_factor = Q.get()
        logger.info('get image from queue real on cam  : {}'.format(cam))
        files = {'myFile': img}
        imgJson = {'key': get_conf('key'), 'img_name': 'temp_img_cam_'+str(cam), 'cam': cam,
                   'result': json.dumps([(r[0], r[1], r[2]) for r in result]), 'real_time': True,
                   'resize_factor': resize_factor}
        try:
            r = requests.post(settings.SERVER+"uploadimage", files=files, data=imgJson,  timeout=40)
            logger.warning('send json image real : {}'.format(r.status_code))
        except (requests.exceptions.ConnectionError, requests.Timeout):
            logger.warning('uploadImageRealTime Can not find the remote server')
            time.sleep(5)
            pass


def upload_image(Q):
    server = True
    logger.warning('starting upload image')
    while True:
        if server:
            cam, img_name, result, img = Q.get()
            logger.info('get image from queue : {}'.format(img_name))
            files = {'myFile': img}
            imgJson = {'key': get_conf('key'), 'img_name': img_name, 'cam': cam,
                       'result': json.dumps([(r[0], r[1], r[2]) for r in result]), 'real_time': False}
        try:
            r = requests.post(settings.SERVER+"uploadimage", files=files, data=imgJson,  timeout=40)
            server = True
            logger.info('send json image : {}'.format(imgJson))
            logger.warning(f'send image to server  : {r.status_code} answer : {r.text}')
        except (requests.exceptions.ConnectionError, requests.Timeout):
            server = False
            logger.warning('uploadImage Can not find the remote server')
            time.sleep(5)
            pass


def upload_result(Q, E_video):
    from video import RecCamera
    # recCamera  = RecCamera(E_video)
    server = True
    logger.warning('starting upload result')
    while True:
        if server:
            img, cam, result_filtered, result_darknet, correction = Q.get()
            logger.info('get result from queue : {}'.format((img, cam, result_filtered, result_darknet, correction)))
            result_filtered, result_darknet = [(r[0], r[1], r[2]) for r in result_filtered],\
                                              [(r[0], r[1], r[2]) for r in result_darknet]
            # set video record for this result
            #video = recCamera.rec_cam(cam)
            video = 'None'
            logger.info('get video token : {}'.format(video))
            result_json = {'key': get_conf('key'), 'img' : img, 'cam' : cam, 'result_filtered' : result_filtered, 'result_darknet' : result_darknet, 'video' : video, 'correction' : correction }
        try :
            r = requests.post(settings.SERVER+"uploadresult", json=result_json,  timeout= 40)
            server = True
            logger.info('send json : {}'.format(result_json))
            logger.warning('send result to server  : {}'.format(r.text))
        except (requests.exceptions.ConnectionError, requests.Timeout) :
            server = False
            logger.warning('uploadResult Can not find the remote server')
            time.sleep(5)
            pass
