import time
import requests
import cv2
import numpy as np
from threading import Thread, Lock
import settings
import os
import darknet as dn
from log import Logger
import secrets
import concurrent.futures
import asyncio
from process_camera_grab import grab_http, rtsp_reader, grab_rtsp
import websockets
import json
from utils import get_conf
import queue


class ProcessCamera(Thread):

    def __init__(self, cam, tlock):
        Thread.__init__(self)
        self.a = []
        self.cam = cam
        self.key = get_conf('key')
        self.running = False
        self.thread_running = False
        self.loop = asyncio.new_event_loop()
        self.logger = Logger('process_camera_thread__' + str(self.cam["id"]) + '--' + self.cam["name"],
                             level=settings.PROCESS_CAMERA_LOG).run()
        self.img_bytes = None
        self.vcap = None
        # self.queue = asyncio.Queue(maxsize=10)

    def run(self):

        self.logger.info('running Thread')
        self.thread_running = True
        asyncio.set_event_loop(self.loop)
        while self.thread_running:
            self.running = True
            if self.cam['stream']:
                if not self.vcap or not self.vcap.isOpened():
                    rtsp = self.cam['rtsp']
                    rtsp_login = 'rtsp://' + self.cam['username'] + ':' + self.cam['password'] + '@' + rtsp.split('//')[1]
                    self.vcap = cv2.VideoCapture(rtsp_login)
                    self.logger.warning(f'openning videocapture {self.vcap} is {self.vcap.isOpened()}')
                task = [self.task1(), self.task2(), self.task3(), self.task4()]
            else:
                task = [self.task1(), self.task3(), self.task4() ]
            self.loop.run_until_complete(asyncio.gather(*task))
            if self.cam['stream']:
                self.vcap.release()
                self.logger.warning('VideoCapture close on {}'.format(self.cam['name']))
            time.sleep(5)

    async def task1(self):
        bad_read = 0
        while self.running:
            t = time.time()
            if self.cam['stream']:
                frame = await grab_rtsp(self.vcap, self.loop, self.logger, self.cam)
                if frame is False:
                    self.logger.warning(f"Bad rtsp read on {self.cam['name']} videocapture is {self.vcap.isOpened()}")
                    bad_read += 1
                    if bad_read > 10:
                        self.running = False
                else:
                    bad_read = 0
                self.running = self.vcap.isOpened()
            else:
                self.logger.debug(f"before grab_http on {self.cam['name']}")
                frame = await grab_http(self.cam, self.logger)
            self.logger.info(f"ecriture de la frame {self.cam['name']} {time.strftime('%Y-%m-%d-%H-%M-%S')}"
                             f" en {time.time() - t}s")
            if bad_read == 0:
                self.img_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
                # try:
                #     asyncio.run_coroutine_threadsafe(self.queue.put(img_bytes), self.loop)
                # except asyncio.QueueFull:
                #     pass
                # asyncio.run_coroutine_threadsafe(self.queue.put(img_bytes), self.loop)
                # self.loop.call_soon_threadsafe(self.queue.put, img_bytes)
                # await self.queue.put(img_bytes)
                self.logger.warning(f"queue img bytes {len(self.img_bytes)}")

    async def task2(self):
        while self.running:
            await rtsp_reader(self.vcap, self.loop, self.logger)

    async def task3(self):
        while self.running:
            try:
                async with websockets.connect(settings.SERVER_WS + 'ws_run_cam') as ws_cam:
                    self.logger.debug(f'the key is {self.key}')
                    await ws_cam.send(json.dumps({'key': self.key}))
                    while True:
                        await asyncio.sleep(1)
                        img_bytes = self.img_bytes
                        if img_bytes:
                            await ws_cam.send(img_bytes)
                            self.logger.info(f'--------------------> sending img bytes in task 3 {len(img_bytes)}')
                            self.img_bytes = None
            except (websockets.exceptions.ConnectionClosedError, OSError, ConnectionResetError,
                    websockets.exceptions.InvalidMessage)as ex:
                self.logger.error(f'socket _send_cam disconnected !! / except-->{ex} / name-->{type(ex).__name__}')
                await asyncio.sleep(1)
                continue

    async def task4(self):
        while self.running:
            while True:
                img_bytes = self.img_bytes
                if img_bytes:
                    self.logger.debug(f'>>>>>>>>>>>>>>>>>>>>  img_bytes in task 4 is {len(img_bytes)}')
                await asyncio.sleep(2)
                # img_bytes = asyncio.run_coroutine_threadsafe(self.queue.get_nowait(), self.loop).result()
                    # img_bytes = self.queue.get_nowait()

                # else:
                #     self.logger.warning(f'getting img_bytes size : {len(img_bytes)}')

