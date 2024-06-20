import cv2
import os
import time

frames_per_second = 30.0
res = (2048, 1536)
capture_duration = 30  # seconds

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
cap.set(cv2.CAP_PROP_FPS, frames_per_second)

frames_folder = 'frames'
os.makedirs(frames_folder, exist_ok=True)

start_time = time.time()
frame_count = 0

while time.time() - start_time < capture_duration:
    ret, frame = cap.read()
    if ret:
        frame_filename = os.path.join(frames_folder, f'frame_{frame_count:04d}.jpg')
        cv2.imwrite(frame_filename, frame)
        frame_count += 1

cap.release()
cv2.destroyAllWindows()
