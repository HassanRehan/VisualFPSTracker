import mss
import numpy as np
import cv2
import pygetwindow as gw
from ultralytics import YOLO

directory = "train"

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
        screen_np = np.array(screen)
        frame = cv2.cvtColor(screen_np, cv2.COLOR_BGRA2RGB)
    return frame

def perform_inference(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model.predict(frame_rgb)
    return results

def draw_detections(frame, results):
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = f"{model.names[int(box.cls[0])]} {box.conf[0]:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
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