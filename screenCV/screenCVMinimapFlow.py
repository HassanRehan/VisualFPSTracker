import pygetwindow as gw
from PIL import ImageGrab
import cv2
import numpy as np
import time
import tkinter as tk
from PIL import Image, ImageTk  # Add this import for handling images


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

            # Load the background image
            self.bg_image = Image.open("map_overview.png")
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)

            # Set the canvas size to the image size
            self.canvas = tk.Canvas(root, width=self.bg_image.width, height=self.bg_image.height)
            self.canvas.pack()

            # Set the window size to the image size
            self.root.geometry(f"{self.bg_image.width}x{self.bg_image.height}")

            self.current_x, self.current_y = self.bg_image.width // 2, self.bg_image.height // 2  # Starting point in the middle of the canvas
            self.scale_factor = 0.4  # Scale factor to reduce the distance

            # Create the background image on the canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_photo)

        def update_canvas(self, new_x, new_y):
            scaled_x = self.current_x + (new_x - self.current_x) * self.scale_factor
            scaled_y = self.current_y + (new_y - self.current_y) * self.scale_factor
            self.canvas.create_line(self.current_x, self.current_y, scaled_x, scaled_y, fill="white", width=2)
            self.current_x, self.current_y = scaled_x, scaled_y

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
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

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
        # current_time = time.strftime("%H:%M:%S", time.localtime())
        # print(f"{current_time}, {average_angle}")
        
        if flow_detected:
            direction = ""
            # if 0 <= average_angle < np.pi / 8 or 15 * np.pi / 8 <= average_angle < 2 * np.pi:
            if 0 <= average_angle < 1.5:
                direction = "Right"
                # print(f"Right: 0, {average_angle} , {np.pi / 8} or {15 * np.pi / 8}, {average_angle} , {2 * np.pi}")
            elif np.pi / 8 <= average_angle < 3 * np.pi / 8:
                direction = "Down-Right"
                # print(f"Down-Right: {np.pi / 8}, {average_angle} , {3 * np.pi / 8}")
            elif 3 * np.pi / 8 <= average_angle < 5 * np.pi / 8:
                direction = "Down"
                # print(f"Down: {3 * np.pi / 8}, {average_angle} , {5 * np.pi / 8}")
            elif 5 * np.pi / 8 <= average_angle < 7 * np.pi / 8:
                direction = "Down-Left"
                # print(f"Down-Left: {5 * np.pi / 8}, {average_angle} , {7 * np.pi / 8}")
            elif 7 * np.pi / 8 <= average_angle < 9 * np.pi / 8:
                direction = "Left"
                # print(f"Left: {7 * np.pi / 8}, {average_angle} , {9 * np.pi / 8}")
            elif 9 * np.pi / 8 <= average_angle < 11 * np.pi / 8:
                direction = "Up-Left"
                # print(f"Up-Left: {9 * np.pi / 8}, {average_angle} , {11 * np.pi / 8}")
            elif 11 * np.pi / 8 <= average_angle < 13 * np.pi / 8:
                direction = "Up"
                # print(f"Up: {11 * np.pi / 8}, {average_angle} , {13 * np.pi / 8}")
            elif 13 * np.pi / 8 <= average_angle < 15 * np.pi / 8:
                direction = "Up-Right"
                # print(f"Up-Right: {13 * np.pi / 8}, {average_angle} , {15 * np.pi / 8}")

            # Put the direction text on the image
            cv2.putText(bgr_flow, f"Direction: {direction}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

        # Display the flow
        cv2.imshow('Optical Flow', bgr_flow)

        if flow_detected:
            # Update the canvas with the new direction (inverse)
            new_x = app.current_x - int(np.cos(average_angle) * 10)
            new_y = app.current_y - int(np.sin(average_angle) * 10)
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

        if flow_detected:
            if direction == "Right":
                end_point = (start_point[0] - length, start_point[1])
            elif direction == "Down-Right":
                end_point = (start_point[0] - length, start_point[1] - length)
            elif direction == "Down":
                end_point = (start_point[0], start_point[1] - length)
            elif direction == "Down-Left":
                end_point = (start_point[0] + length, start_point[1] - length)
            elif direction == "Left":
                end_point = (start_point[0] + length, start_point[1])
            elif direction == "Up-Left":
                end_point = (start_point[0] + length, start_point[1] + length)
            elif direction == "Up":
                end_point = (start_point[0], start_point[1] + length)
            elif direction == "Up-Right":
                end_point = (start_point[0] - length, start_point[1] + length)
        else:
            start_point = (0,0)
            end_point = (0,0)

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