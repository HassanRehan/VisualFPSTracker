import pygetwindow as gw
from PIL import ImageGrab
import cv2
import numpy as np

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
    crop = 60
    region = (left + 21 + crop, top + 50 + crop, left + 414 - crop, top + 270 - crop)
    
    # Initialize variables for optical flow
    prev_gray = None
    dis = cv2.DISOpticalFlow_create()

    while True:
        # Capture the region
        screenshot = ImageGrab.grab(bbox=region)
        frame = np.array(screenshot)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        if prev_gray is None:
            prev_gray = gray
            continue
        
        # Calculate dense optical flow using DIS method
        flow = dis.calc(prev_gray, gray, None)
        
        # Compute the magnitude and angle of the flow
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        
        # Calculate the average angle
        avg_angle = np.mean(angle)
        
        # Determine the direction based on the average angle
        if avg_angle < np.pi / 4 or avg_angle > 7 * np.pi / 4:
            direction = "Right"
        elif np.pi / 4 <= avg_angle < 3 * np.pi / 4:
            direction = "Down"
        elif 3 * np.pi / 4 <= avg_angle < 5 * np.pi / 4:
            direction = "Left"
        else:
            direction = "Up"
        
        print(f"Direction of movement: {direction}")
        
        # Create an HSV image
        hsv = np.zeros_like(frame)
        hsv[..., 1] = 255
        
        # Set the hue and value according to the flow
        hsv[..., 0] = angle * 180 / np.pi / 2
        hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        
        # Convert HSV to BGR
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Display the result
        cv2.imshow('Dense Optical Flow', bgr)
        
        # Update previous frame
        prev_gray = gray
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()