import os

# Starting point for the 12-digit number
current_number = 100000000001

# Path to your folder containing the frames
folder_path = "/home/mehdi/YOLO_Train/Create_Dataset/Frames_rename"

# Iterate over files in the folder and rename them
for filename in sorted(os.listdir(folder_path)):
    if filename == '.DS_Store':  # Skip macOS metadata file if present
        continue

    # Construct new 12-digit unique filename
    new_filename = str(current_number) + ".jpg"  # Assuming the files are JPEGs

    # Full path to the existing and new files
    old_file_path = os.path.join(folder_path, filename)
    new_file_path = os.path.join(folder_path, new_filename)

    # Rename the file
    os.rename(old_file_path, new_file_path)

    # Increment the unique number
    current_number += 1

print("Files renamed successfully.")
