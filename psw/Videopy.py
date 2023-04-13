import os
import time
import datetime
import requests
import cv2
from moviepy.editor import *

while 1:
    # Turn on the cam.
    cap = cv2.VideoCapture(0)

    # Check if the cam is opened normally.
    if not cap.isOpened():
        print("Could not open camera.")
        exit()

    # Specify the path and file name to save.
    now = datetime.datetime.now()
    save_path = "videos"
    filename = now.strftime("%Y%m%d_%H%M%S") + ".mp4"

    # Create the path if it doesn't exist.
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Combine the path to save with the file name.
    save_file = os.path.join(save_path, filename)

    # Set the video codec.
    fourcc = "mp4v"

    # Set the fps.
    fps = 20.0

    # Set the resolution.
    resolution = (640, 480)

    # Create an object to store the video file.
    out = cv2.VideoWriter(save_file, cv2.VideoWriter_fourcc(*fourcc), fps, resolution)

    # Capture and save video for specified number of seconds.
    start_time = time.time()
    while (time.time() - start_time) < 15:  # Capture for 5 minutes.
        ret, frame = cap.read()  # Capture the video.

        # Save the captured video.
        if ret == True:
            out.write(frame)

            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break

    # Close the cam and file storage objects.
    cap.release()
    out.release()

    # Use MoviePy to change the codec to h264 and save the video with mp4 extension.
    video = VideoFileClip(save_file)
    video.write_videofile(save_file.replace(".mp4", "_h264.mp4"), codec="h264")

# Close the window.
cv2.destroyAllWindows()
