
ffmpeg -f v4l2 -framerate 30 -video_size 2048x1536 -input_format mjpeg -i /dev/video0 output.mov
