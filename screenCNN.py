import io
import mss
import numpy as np
import cv2
import pygetwindow as gw
from ultralytics import YOLO
from PIL import Image, ImageTk
import easyocr
from openpyxl import Workbook
import time
import tkinter as tk

UPDATE_INTERVAL = 800  # in milliseconds

def save_to_excel(enemy_in_sight):
    """Save results to an Excel file."""
    # elapsed_time = round(time.time() - start_time, 1)
    elapsed_time = int(time.time() - start_time)
    ws.append([elapsed_time, enemy_in_sight])
    wb.save("cnn_data.xlsx")

def find_game_window(title_start="Call of Duty"):
    """Find and return the target game window."""
    for window in gw.getAllTitles():
        if window.startswith(title_start):
            return gw.getWindowsWithTitle(window)[0]
    return None

def capture_region(region, window):
    """Capture a specific region of the screen."""
    x, y, w, h = region
    with mss.mss() as sct:
        monitor = {
            "left": window.left + x,
            "top": window.top + y,
            "width": w,
            "height": h
        }
        screen = sct.grab(monitor)
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # Convert BGRA to BGR
    return frame

def perform_inference(frame):
    """Run YOLO inference on a given frame."""
    return model.predict(frame, stream=True, verbose=False)


def draw_detections(frame, results, middle_region):
    """Draw detection boxes and highlight middle region matches."""
    enemy_detected = False
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            confidence = box.conf[0]
            label = f"{model.names[class_id]} {confidence:.2f}"
            color = class_colors.get(class_id, (255, 255, 255))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Check if the box is within the middle region
            mx1, my1, mx2, my2 = middle_region
            if mx1 < x1 < mx2 and my1 < y1 < my2 and mx1 < x2 < mx2 and my1 < y2 < my2:
                enemy_detected = True
    return frame, enemy_detected


def extract_text_from_region(region, window, threshold=190):
    """Capture and OCR a specific region of the screen."""
    img = capture_region(region, window)
    img_pil = Image.fromarray(img).convert('L').point(lambda p: p > threshold and 255)
    result = reader.readtext(np.array(img_pil))
    extracted_text = " ".join([item[1] for item in result])
    return extracted_text, np.array(img_pil)

def update_frame():
    """Main update loop to capture frames and update UI."""
    window = find_game_window()
    if not window:
        root.after(1000, update_frame)
        return

    frame = capture_region((60, 40, 1900, 900), window)
    results = perform_inference(frame)
    frame_with_detections, enemy_in_sight = draw_detections(frame, results, middle_region)

    # Extract and process middle region
    mx1, my1, mx2, my2 = middle_region
    middle_frame = frame_with_detections[my1:my2, mx1:mx2]

    save_to_excel(enemy_in_sight)

    # Update GUI with processed frames
    frame_resized = cv2.resize(frame_with_detections, (0, 0), fx=0.3, fy=0.3)
    middle_resized = cv2.resize(middle_frame, (0, 0), fx=0.5, fy=0.5)

    full_frame_img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)))
    middle_frame_img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(middle_resized, cv2.COLOR_BGR2RGB)))

    full_frame_label.config(image=full_frame_img)
    full_frame_label.image = full_frame_img

    middle_region_label.config(image=middle_frame_img)
    middle_region_label.image = middle_frame_img

    root.after(UPDATE_INTERVAL, update_frame)


# Initialize YOLO model
model_path = "runs/detect/60epochs/weights/best.pt"
model = YOLO(model_path).to('cuda')
class_colors = {0: (0, 255, 0), 1: (0, 0, 255)}  # Green and Red for classes

# Initialize OCR reader
reader = easyocr.Reader(['en'])

# Initialize Excel workbook
wb = Workbook()
ws = wb.active
ws.title = "CNN Data"
ws.append(["Elapsed Time (s)", "Enemy in Sight"])
start_time = time.time()


# Tkinter GUI setup
root = tk.Tk()
root.geometry("800x800")
root.title("CNN Tracker")

full_frame_label = tk.Label(root)
full_frame_label.pack()
middle_region_label = tk.Label(root)
middle_region_label.pack()

# Middle region coordinates
middle_region = (800, 400, 1020, 740)



# Start Tkinter loop
update_frame()
root.mainloop()