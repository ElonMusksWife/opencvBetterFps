import cv2
import numpy as np
import threading
import queue
import time
import os

# Configuration
filename = 'video.avi'
frames_per_second = 30.0
res = '2048p'
capture_duration = 30  # seconds

# Standard Video Dimensions Sizes
STD_DIMENSIONS = {
    "1080p": (1920, 1080),
    "480p": (640, 480),
    "768p": (1024, 768),
    "720p": (1280, 720),
    "1024p": (1280, 1024),
    "2048p": (2048, 1536),
}

def get_dims(res='1080p'):
    width, height = STD_DIMENSIONS["1080p"]
    if res in STD_DIMENSIONS:
        width, height = STD_DIMENSIONS[res]
    return width, height

VIDEO_TYPE = {
    'MJPG': cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
    'avi': cv2.VideoWriter_fourcc(*'XVID'),
    'mp4': cv2.VideoWriter_fourcc(*'XVID'),
}

def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
        return VIDEO_TYPE[ext]
    return VIDEO_TYPE['avi']

class VideoRecorder:
    def __init__(self, filename, fps, res):
        self.filename = filename
        self.fps = fps
        self.width, self.height = get_dims(res)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
        self.out = cv2.VideoWriter(self.filename, get_video_type(filename), fps, (self.width, self.height))
        self.frame_queue = queue.Queue()
        self.capture_thread = threading.Thread(target=self.capture_frames)
        self.write_thread = threading.Thread(target=self.write_frames)
        self.running = True
        self.total_frames = 0
        self.start_time = time.time()

    def capture_frames(self):
        while self.running:
            start_time = time.time()
            ret, frame = self.cap.read()
            if ret:
                self.frame_queue.put(frame)
                self.total_frames += 1
            elapsed_time = time.time() - start_time
            sleep_time = max(1 / self.fps - elapsed_time, 0)
            time.sleep(sleep_time)

    def write_frames(self):
        while self.running or not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get(timeout=1)
                self.out.write(frame)
            except queue.Empty:
                continue

    def start(self):
        self.capture_thread.start()
        self.write_thread.start()

    def stop(self):
        self.running = False
        self.capture_thread.join()
        self.write_thread.join()
        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()
        total_time = time.time() - self.start_time
        average_fps = self.total_frames / total_time
        print(f"Average FPS over recording period: {average_fps:.2f}")

video_recorder = VideoRecorder(filename, frames_per_second, res)
video_recorder.start()

# Run for a specific duration or condition
time.sleep(capture_duration)
video_recorder.stop()
