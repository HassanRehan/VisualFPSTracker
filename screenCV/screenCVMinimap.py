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
    region = (left + 21, top + 50, left + 414, top + 270)
    
    # Preprocess the template image
    template = cv2.imread('player_arrow.png', 0)
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
            screenshot_gray = cv2.GaussianBlur(screenshot_gray, (5, 5), 0)
            screenshot_edges = cv2.Canny(screenshot_gray, 50, 150)
            
            best_match = None
            best_val = -np.inf
            
            # Multi-scale template matching
            for scale in np.linspace(0.5, 1.5, 20):
                resized_template = cv2.resize(template_edges, (0, 0), fx=scale, fy=scale)
                if resized_template.shape[0] > screenshot_edges.shape[0] or resized_template.shape[1] > screenshot_edges.shape[1]:
                    continue
                
                result = cv2.matchTemplate(screenshot_edges, resized_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val > best_val:
                    best_val = max_val
                    best_match = (max_loc, resized_template.shape)
            
            if best_match:
                top_left, (h, w) = best_match
                bottom_right = (top_left[0] + w, top_left[1] + h)
                cv2.rectangle(screenshot_np, top_left, bottom_right, (0, 255, 0), 2)
            
            # Display the result
            cv2.imshow('Matched Result', screenshot_np)
            
            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
else:
    print("Target window not found.")