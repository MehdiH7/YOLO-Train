import requests
import numpy as np
import cv2
import subprocess
import os
from tqdm import tqdm

def process_video(M3U8_URL, url_index, output_folder):
    print(f"Processing video from URL: {M3U8_URL}")

    temp_filename = f"temp_video_{url_index}.mp4"
    cmd = f"ffmpeg -i {M3U8_URL} -t 60 {temp_filename}"
    subprocess.call(cmd, shell=True)

    # Load the video using OpenCV
    cap = cv2.VideoCapture(temp_filename)
   
    # Get the FPS and total number of frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames in the video: {total_frames}")
   
    # Generate 10 random frame numbers to extract
    random_frames = np.random.choice(total_frames, 10, replace=False)
    print(f"Randomly selected frames: {random_frames}")

    # Extract and save the frames with a progress bar
    for i in tqdm(range(total_frames), desc=f"Saving frames for URL {url_index + 1}", ncols=100):
        ret, frame = cap.read()
        if not ret:
            break
        if i in random_frames:
            filename = os.path.join(output_folder, f"frame_{url_index}_{i}.jpg")
            cv2.imwrite(filename, frame)

    # Release the video capture object and remove the temporary video
    cap.release()
    os.remove(temp_filename)

output_folder = "all_frames"
os.makedirs(output_folder, exist_ok=True)


# List of M3U8 URLs
M3U8_URLs = [
        "https://api.forzify.com/eliteserien/playlist.m3u8/6602:5043000:5068000/Manifest.m3u8",
        "https://api.forzify.com/eliteserien/playlist.m3u8/6600:4680000:4705000/Manifest.m3u8",
        "https://api.forzify.com/eliteserien/playlist.m3u8/6599:4643000:4668000/Manifest.m3u8",
        "https://api.forzify.com/eliteserien/playlist.m3u8/6601:3282000:3307000/Manifest.m3u8",
        "https://api.forzify.com/eliteserien/playlist.m3u8/6602:2850000:2875000/Manifest.m3u8",
        "https://api.forzify.com/eliteserien/playlist.m3u8/6601:1188000:1213000/Manifest.m3u8",
        "https://api.forzify.com/eliteserien/playlist.m3u8/6592:7346000:7371000/Manifest.m3u8",
        "https://api.forzify.com/eliteserien/playlist.m3u8/6590:7248000:7273000/Manifest.m3u8",
        "https://api.forzify.com/eliteserien/playlist.m3u8/6590:6203000:6228000/Manifest.m3u8",
        "https://api.forzify.com/eliteserien/playlist.m3u8/6590:5331000:5356000/Manifest.m3u8",
        "https://api.forzify.com/eliteserien/playlist.m3u8/6588:6652000:6677000/Manifest.m3u8",
        "https://api.forzify.com/eliteserien/playlist.m3u8/6586:4861000:4886000/Manifest.m3u8",
        "https://api.forzify.com/eliteserien/playlist.m3u8/6586:3016000:3041000/Manifest.m3u8"

]

for index, url in enumerate(M3U8_URLs):
    process_video(url, index, output_folder)
