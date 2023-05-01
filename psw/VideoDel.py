import os
import glob

os.chdir("psw")

# Set maximum storage space in bytes
max_storage = 1000000000  # 1GB

# Set path to video folder
video_folder = "videos"
while True:
    # Get total size of video folder in bytes
    total_size = sum(
        os.path.getsize(f) for f in glob.glob(os.path.join(video_folder, "*"))
    )

    # Check if storage is full
    if total_size > max_storage:
        # Get list of videos sorted by creation time
        video_list = sorted(
            glob.glob(os.path.join(video_folder, "*.mp4")), key=os.path.getctime
        )

        # Delete oldest videos until storage is under maximum
        while total_size > max_storage and video_list:
            oldest_video = video_list.pop(0)
            os.remove(oldest_video)
            total_size -= os.path.getsize(oldest_video)
