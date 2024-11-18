import pygetwindow as gw
from PIL import ImageGrab
import cv2
import numpy as np
import time
import tkinter as tk

# Find the target window
target_window = None
for window in gw.getAllTitles():
    if window.startswith("Call of Duty"):
        target_window = gw.getWindowsWithTitle(window)[0]
        break

if target_window:
    # Get the window's bounding box
    left, top, right, bottom = target_window.left, target_window.top, target_window.right, target_window.bottom
    
    # Define the region you want to capture (left, top, right, bottom)
    # region = (left + 21, top + 50, left + 414, top + 270)
    crop = 60
    region = (left + 21 + crop, top + 50 + crop, left + 414 - crop, top + 270 - crop)
    
    # Initialize variables for optical flow
    prev_gray = None
    hsv_mask = np.zeros((region[3] - region[1], region[2] - region[0], 3), dtype=np.uint8)
    hsv_mask[..., 1] = 255

    class MovementTraceApp:
        def __init__(self, root):
            self.root = root
            self.canvas = tk.Canvas(root, width=800, height=600)
            self.canvas.pack()
            self.current_x, self.current_y = 400, 300  # Starting point in the middle of the canvas

        def update_canvas(self, new_x, new_y):
            self.canvas.create_line(self.current_x, self.current_y, new_x, new_y, fill="black")
            self.current_x, self.current_y = new_x, new_y

    # Create the main window
    root = tk.Tk()
    app = MovementTraceApp(root)

    prev_gray = None
    hsv_mask = np.zeros((600, 800, 3), dtype=np.uint8)
    hsv_mask[..., 1] = 255

    while True:
        # Capture the region
        screenshot = ImageGrab.grab(bbox=region)
        frame = np.array(screenshot)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if prev_gray is None:
            prev_gray = gray
            continue
        
        # Calculate optical flow
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 60, 3, 5, 1.2, 0)

        # Compute magnitude and angle of the flow
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # Check for significant flow
        if np.mean(magnitude) < 1:  # Adjust the threshold as needed
            flow_detected = False
        else:
            flow_detected = True            

        # Resize hsv_mask to match the shape of the angle array
        hsv_mask = np.zeros_like(frame)
        hsv_mask[..., 1] = 255

        # Set HSV mask values
        hsv_mask[..., 0] = angle * 180 / np.pi / 2
        hsv_mask[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)

        # Convert HSV to BGR
        bgr_flow = cv2.cvtColor(hsv_mask, cv2.COLOR_HSV2BGR)

        # Calculate the average angle to determine the direction
        average_angle = np.mean(angle)

        # Update the canvas with the new direction
        new_x = app.current_x + int(np.cos(average_angle) * 10)
        new_y = app.current_y + int(np.sin(average_angle) * 10)
        app.update_canvas(new_x, new_y)

        prev_gray = gray

        root.update_idletasks()
        root.update()

        # Create a new window to draw the line
        line_window = np.zeros_like(bgr_flow)

        # Define the start and end points for the line based on the direction
        start_point = (line_window.shape[1] // 2, line_window.shape[0] // 2)
        length = 50  # Length of the line
        end_point = start_point

        # if flow_detected:
        #     if direction == "Right":
        #         end_point = (start_point[0] - length, start_point[1])
        #     elif direction == "Down-Right":
        #         end_point = (start_point[0] - length, start_point[1] - length)
        #     elif direction == "Down":
        #         end_point = (start_point[0], start_point[1] - length)
        #     elif direction == "Down-Left":
        #         end_point = (start_point[0] + length, start_point[1] - length)
        #     elif direction == "Left":
        #         end_point = (start_point[0] + length, start_point[1])
        #     elif direction == "Up-Left":
        #         end_point = (start_point[0] + length, start_point[1] + length)
        #     elif direction == "Up":
        #         end_point = (start_point[0], start_point[1] + length)
        #     elif direction == "Up-Right":
        #         end_point = (start_point[0] - length, start_point[1] + length)
        # else:
        #     start_point = (0,0)
        #     end_point = (0,0)

        # Draw the line on the new window
        cv2.line(line_window, start_point, end_point, (0, 255, 0), 2)

        # Show the new window with the line
        cv2.imshow('Movement Direction', line_window)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    root.mainloop()
else:
    print("Target window not found.")