import io
import tkinter as tk
from PIL import Image, ImageTk
import pyautogui
import pygetwindow as gw
import threading
import time
import easyocr

# Reader instance for English
reader = easyocr.Reader(['en'])

def capture_and_display_screenshot(root, target_window, x, y, w, h, img_label, text_var, rotation):
    if target_window:
        try:
            target_window.activate()
        except gw.PyGetWindowException as e:
            print(f"Error activating window: {e}")

        screenshot = pyautogui.screenshot(region=(target_window.left + x, target_window.top + y, w, h))

        # Convert to grayscale
        screenshot = screenshot.convert('L')

        # Apply a threshold to make the image binary
        threshold = 200
        screenshot = screenshot.point(lambda p: p > threshold and 255)

        # Rotate the image by the specified rotation value
        screenshot = screenshot.rotate(rotation)

        # Process the screenshot
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        result = reader.readtext(img_byte_arr)
        text = " ".join([item[1] for item in result])

        # Safely update the GUI from the thread with OCR text
        root.after(0, lambda: text_var.set(text))

        # Convert the processed image back to a format that can be displayed in tkinter
        imgTk = ImageTk.PhotoImage(image=Image.open(io.BytesIO(img_byte_arr)))

        # Update the tkinter window to display the processed screenshot
        root.after(0, lambda: img_label.config(image=imgTk))
        root.after(0, lambda: setattr(img_label, 'image', imgTk))  # Keep a reference, prevent garbage-collection
    else:
        print("Target application window not found.")

# Find the target window
target_window = None
for window in gw.getAllTitles():
    if window.startswith("Call of Duty"):
        target_window = gw.getWindowsWithTitle(window)[0]
        break

def create_floating_window(target_window):
    # Create the floating window
    root = tk.Tk()
    root.geometry("600x600")

    # Create a list to hold the labels and text variables
    labels = []
    text_vars = []

    # Define the regions to capture
    regions = [
        (1565, 960, 70, 58),        # Bullet count
        (1520, 1030, 220, 40),      # Gun name
        (177, 953, 40, 40),          # Player score
        (177, 1010, 35, 35)          # Highest enemy score
    ]

    # Define the rotation values for each region
    rotations = [9.5, 9.5, -9.5, -9.5]

    # Create labels and text variables for each region
    for _ in regions:
        text_var = tk.StringVar()
        text_label = tk.Label(root, textvariable=text_var, font=('Helvetica', 16), fg='black', bg='white')
        text_label.pack()

        img_label = tk.Label(root)
        img_label.pack()

        labels.append((img_label, text_var))

    def update_ocr_results(target_window, regions, rotations):
        while True:
            for (x, y, w, h), rotation, (img_label, text_var) in zip(regions, rotations, labels):
                capture_and_display_screenshot(root, target_window, x, y, w, h, img_label, text_var, rotation)
            root.update()
            time.sleep(1)

    # Start the OCR update process in a separate thread
    threading.Thread(target=update_ocr_results, args=(target_window, regions, rotations), daemon=True).start()

    root.mainloop()

# Call the function to create the floating window
create_floating_window(target_window)
