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
    # region = (left + 21, top + 50, left + 414, top + 270)

    crop_side = 80
    crop_top = 0

    region = (left + 21 + crop_side, top + 70 + crop_top, left + 414 - crop_side, top + 150 - crop_top)
    
    # Preprocess the template image
    template = cv2.imread('map_overview.png', 0)
    template_color = cv2.imread('map_overview.png')  # Read the template in color for overlay
    template = cv2.GaussianBlur(template, (5, 5), 0)
    template_edges = cv2.Canny(template, 50, 150)

    
    if template is None:
        print("Error: Template image not found or cannot be read.")
    else:
        while True:
            # Capture the region
            screenshot = ImageGrab.grab(bbox=region)
            
            # Convert the screenshot to a format suitable for OpenCV
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to the screenshot
            screenshot_blur = cv2.GaussianBlur(screenshot_gray, (5, 5), 0)
            
            # Detect edges in the screenshot
            screenshot_edges = cv2.Canny(screenshot_blur, 50, 150)

            # Show the preprocessed screenshot
            cv2.imshow('Preprocessed Screenshot', screenshot_edges)
            
            # Perform template matching
            result = cv2.matchTemplate(screenshot_edges, template_edges, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Define the bounding box for the matched region
            h, w = screenshot_gray.shape
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            
            # Draw a rectangle around the matched region on the screenshot
            cv2.rectangle(screenshot_np, top_left, bottom_right, (0, 255, 0), 2)
            
            # Overlay the matched region on the template image
            overlay = template_color.copy()
            cv2.rectangle(overlay, top_left, bottom_right, (0, 255, 0), 2)

            overlay2 = template_edges.copy()
            cv2.rectangle(overlay2, top_left, bottom_right, (0, 255, 0), 2)
            
            # Display the result
            cv2.imshow('Matched Result', screenshot_np)
            cv2.imshow('Overlay on Map Overview', overlay)
            cv2.imshow('Overlay on Map Edges', overlay2)

            
            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()