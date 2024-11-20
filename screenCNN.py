import mss
import numpy as np
import cv2
import pygetwindow as gw
from ultralytics import YOLO

directory = "train2"

# Define colors for the two classes
class_colors = {
    0: (0, 255, 0),  # Green for class 0
    1: (0, 0, 255)   # Red for class 1
}

model = YOLO("runs/detect/" + directory + "/weights/best.pt")

def capture_window(title_startswith):
    target_window = None
    for window in gw.getAllTitles():
        if window.startswith(title_startswith):
            target_window = gw.getWindowsWithTitle(window)[0]
            break
    if not target_window:
        return None

    target_window.activate()
    with mss.mss() as sct:
        monitor = {
            "top": target_window.top,
            "left": target_window.left,
            "width": target_window.width,
            "height": target_window.height
        }
        screen = sct.grab(monitor)
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # Convert BGRA to BGR
    return frame

def perform_inference(frame):
    results = model.predict(frame)
    return results

def draw_detections(frame, results):
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            label = f"{model.names[class_id]} {box.conf[0]:.2f}"
            color = class_colors.get(class_id, (255, 255, 255))  # Default to white if class_id not found
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    return frame

def main():

    print("YOLO model classes:", model.names)

    while True:
        frame = capture_window("Call of Duty")
        if frame is not None:
            results = perform_inference(frame)
            frame_with_detections = draw_detections(frame, results)
            # Display the frame with detections
            cv2.imshow("Detections", frame_with_detections)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()