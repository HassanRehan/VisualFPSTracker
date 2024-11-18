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
    prev_points = None
    lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    feature_params = dict(maxCorners=10, qualityLevel=0.1, minDistance=1, blockSize=500)

    while True:
        # Capture the region
        screenshot = ImageGrab.grab(bbox=region)
        frame = np.array(screenshot)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        if prev_gray is None:
            prev_gray = gray
            prev_points = cv2.goodFeaturesToTrack(prev_gray, mask=None, **feature_params)
            continue
        
        # Calculate optical flow using Lucas-Kanade method
        next_points, status, error = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_points, None, **lk_params)

        if next_points is not None and status is not None:
            # Select good points
            good_new = next_points[status == 1]
            good_old = prev_points[status == 1]

            # Draw the tracks
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                a, b = new.ravel()
                c, d = old.ravel()
                frame = cv2.arrowedLine(frame, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)

            # Update previous frame and points
            prev_points = good_new.reshape(-1, 1, 2)
        
        # Show the frame
        cv2.imshow('Optical Flow', frame)

        # Update previous frame
        prev_gray = gray.copy()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()