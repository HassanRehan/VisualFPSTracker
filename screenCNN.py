import cv2
import numpy as np
import pygetwindow as gw
import pyautogui
from ultralytics import YOLO

# Load YOLOv8 model (assuming you have the model loaded as shown in Model.ipynb)
model = YOLO("yolov8n.yaml").load("yolov8n.pt")

def capture_window(title_startswith):
    target_window = None
    for window in gw.getAllTitles():
        if window.startswith(title_startswith):
            target_window = gw.getWindowsWithTitle(window)[0]
            break
    if not target_window:
        return None

    target_window.activate()
    screen = pyautogui.screenshot(region=(target_window.left, target_window.top, target_window.width, target_window.height))
    screen_np = np.array(screen)
    frame = cv2.cvtColor(screen_np, cv2.COLOR_BGR2RGB)
    return frame

def perform_inference(frame):
    # Convert frame to the format expected by the model (if necessary)
    # Perform inference
    results = model(frame)
    # Process results (e.g., draw bounding boxes, extract information)
    return results

def main():
    while True:
        frame = capture_window("Call of Duty")
        if frame is not None:
            results = perform_inference(frame)
            # Display results or perform further processing
            # For example, display the frame with detections
            cv2.imshow('Detections', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

if __name__ == "__main__":
    main()