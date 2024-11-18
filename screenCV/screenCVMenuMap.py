import pygetwindow as gw
from PIL import ImageGrab
import cv2
import numpy as np
import time

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
    region = (left + 840, top + 370, left + 1600, top + 700)
    
    # Preprocess the template image
    player_arrow_template = cv2.imread('player_arrow.png', 0)
    
    if player_arrow_template is None:
        print("Error: Template image not found or cannot be read.")
    else:
        
        # Apply Canny edge detection to the template image
        player_arrow_template = cv2.Canny(player_arrow_template, 50, 150)
        
        while True:
            # Capture the region
            screenshot = ImageGrab.grab(bbox=region)
            
            # Convert the screenshot to a format suitable for OpenCV
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
            
            # Apply Canny edge detection to the screenshot
            screenshot_edges = cv2.Canny(screenshot_gray, 50, 150)
           
            # Perform template matching
            result = cv2.matchTemplate(screenshot_edges, player_arrow_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Define the bounding box for the matched region
            h, w = player_arrow_template.shape
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            
            # Draw a rectangle around the matched region on the screenshot
            cv2.rectangle(screenshot_np, top_left, bottom_right, (0, 255, 0), 2)
            
            # Display the screenshot with the rectangle
            cv2.imshow('Matched Region', screenshot_np)
            cv2.imshow('Template', player_arrow_template)


            
            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()