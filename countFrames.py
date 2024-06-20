import cv2
import threading
import queue
import os
import time

class FrameCapture:
    def __init__(self, folder, fps, res, duration):
        self.folder = folder
        self.fps = fps
        self.res = res
        self.duration = duration
        self.frame_queue = queue.Queue()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.res[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.res[1])
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        os.makedirs(self.folder, exist_ok=True)
        self.running = True
        self.capture_thread = threading.Thread(target=self.capture_frames)
        self.write_thread = threading.Thread(target=self.save_frames)

    def capture_frames(self):
        start_time = time.time()
        frame_count = 0
        while self.running and time.time() - start_time < self.duration:
            ret, frame = self.cap.read()
            if ret:
                self.frame_queue.put((frame_count, frame))
                frame_count += 1
            else:
                print("Frame capture failed.")
            # Add a small delay to match the desired frame rate
            time.sleep(1 / self.fps)
        self.running = False
        print(f"Total frames captured: {frame_count}")

    def save_frames(self):
        saved_count = 0
        while self.running or not self.frame_queue.empty():
            try:
                frame_count, frame = self.frame_queue.get(timeout=1)
                frame_filename = os.path.join(self.folder, f'frame_{frame_count:04d}.jpg')
                cv2.imwrite(frame_filename, frame)
                saved_count += 1
            except queue.Empty:
                continue
        print(f"Total frames saved: {saved_count}")

    def start(self):
        self.capture_thread.start()
        self.write_thread.start()

    def stop(self):
        self.running = False
        self.capture_thread.join()
        self.write_thread.join()
        self.cap.release()
        cv2.destroyAllWindows()

# Configuration
frame_folder = 'frames'
fps = 30.0
res = (2048, 1536)
duration = 30  # seconds

# Start capturing frames
frame_capture = FrameCapture(frame_folder, fps, res, duration)
frame_capture.start()

# Wait for the capture duration
time.sleep(duration + 1)  # Extra second to ensure all frames are processed

frame_capture.stop()

# Encode the frames using FFmpeg
subprocess.run([
    'ffmpeg', '-framerate', str(int(fps)), '-i', f'{frame_folder}/frame_%04d.jpg',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', 'output.mp4'
])
