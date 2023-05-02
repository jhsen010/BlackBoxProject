import os
import time

# Set the directory path where the video files are stored
dir_path = "videos"

while True:
    # Get the remaining storage space of the Raspberry Pi
    remaining_space = os.statvfs("/").f_bfree * os.statvfs("/").f_frsize

    # If remaining storage space is less than 1GB, delete the oldest video file
    if remaining_space < 1e9:
        # Get the list of video files in the directory
        video_files = os.listdir(dir_path)

        # Sort the video files by their creation time
        video_files.sort(key=lambda x: os.stat(os.path.join(dir_path, x)).st_ctime)

        # Delete the oldest video file
        os.remove(os.path.join(dir_path, video_files[0]))

    # Wait for 10 minutes before checking again
    time.sleep(60)
