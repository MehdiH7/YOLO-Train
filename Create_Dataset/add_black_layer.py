import cv2
import os

# Initialize variables for rectangle coordinates
x_start, y_start, x_end, y_end = 0, 0, 0, 0
drawing = False
frame_copy = None

# Mouse callback function to draw the rectangle
def draw_rectangle(event, x, y, flags, param):
    global x_start, y_start, x_end, y_end, drawing, frame, frame_copy
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x_start, y_start = x, y
        frame_copy = frame.copy()
    
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x_end, y_end = x, y
        cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 0, 0), -1)
    
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            frame_copy_temp = frame_copy.copy()
            cv2.rectangle(frame_copy_temp, (x_start, y_start), (x, y), (0, 255, 0), 1)
            cv2.imshow("Frame", frame_copy_temp)

# Read a sample frame to show and draw the rectangle on
frame = cv2.imread("/home/mehdi/YOLO_Train/Create_Dataset/sample/frame_0_2.jpg")

cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", draw_rectangle)

while True:
    cv2.imshow("Frame", frame)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()

# Add black rectangles to all frames
frame_folder = "/home/mehdi/YOLO_Train/Create_Dataset/Frames_main_copy"

for frame_file in os.listdir(frame_folder):
    if frame_file.endswith(".jpg"):
        frame_path = os.path.join(frame_folder, frame_file)
        frame = cv2.imread(frame_path)
        
        # Add the black rectangle
        cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 0, 0), -1)
        
        # Save the frame back to disk
        cv2.imwrite(frame_path, frame)

print("All frames processed.")
