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

def update_ocr_results():
    while True:
        target_window = None
        for window in gw.getAllTitles():
            if window.startswith("Call of Duty"):
                target_window = gw.getWindowsWithTitle(window)[0]
                break

        if target_window:
            target_window.activate()

            screenshot1 = pyautogui.screenshot(region=(target_window.left + 1565, target_window.top + 960, 70, 58))
            screenshot2 = pyautogui.screenshot(region=(target_window.left + 1520, target_window.top + 1030, 220, 40))

            # Convert to grayscale
            screenshot1 = screenshot1.convert('L')
            screenshot2 = screenshot2.convert('L')

            # Apply a threshold to make the image binary
            threshold = 200
            screenshot1 = screenshot1.point(lambda p: p > threshold and 255)
            screenshot2 = screenshot2.point(lambda p: p > threshold and 255)

            # Increase the image size
            # img = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)

            # Rotate the image by 9.5 degrees
            screenshot1 = screenshot1.rotate(9.5)
            screenshot2 = screenshot2.rotate(9.5)

            # Process first screenshot
            img_byte_arr1 = io.BytesIO()
            screenshot1.save(img_byte_arr1, format='PNG')
            img_byte_arr1 = img_byte_arr1.getvalue()
            result1 = reader.readtext(img_byte_arr1)
            text1 = " ".join([item[1] for item in result1])

            # Process second screenshot
            img_byte_arr2 = io.BytesIO()
            screenshot2.save(img_byte_arr2, format='PNG')
            img_byte_arr2 = img_byte_arr2.getvalue()
            result2 = reader.readtext(img_byte_arr2)
            text2 = " ".join([item[1] for item in result2])

            # Safely update the GUI from the thread with OCR text for both screenshots
            root.after(0, lambda: text_var.set(text1 + " | " + text2))

            # Convert the processed images back to formats that can be displayed in tkinter
            imgTk1 = ImageTk.PhotoImage(image=Image.open(io.BytesIO(img_byte_arr1)))
            imgTk2 = ImageTk.PhotoImage(image=Image.open(io.BytesIO(img_byte_arr2)))

            # Update the tkinter window to display the processed screenshots
            root.after(0, lambda: img_label.config(image=imgTk1))
            root.after(0, lambda: setattr(img_label, 'image', imgTk1))  # Keep a reference, prevent garbage-collection

            root.after(0, lambda: img_label2.config(image=imgTk2))
            root.after(0, lambda: setattr(img_label2, 'image', imgTk2))  # Keep a reference, prevent garbage-collection
        else:
            print("Target application window not found.")
            break

        root.update()
        time.sleep(1)

# Create the floating window
root = tk.Tk()
root.geometry("600x600")

text_var = tk.StringVar()
text_label = tk.Label(root, textvariable=text_var, font=('Helvetica', 16), fg='black', bg='white')
text_label.pack()

# Create a label for displaying the image
img_label = tk.Label(root)
img_label.pack()

# Create a second label for displaying the image
img_label2 = tk.Label(root)
img_label2.pack()

# Start the OCR update process in a separate thread
threading.Thread(target=update_ocr_results, daemon=True).start()

root.mainloop()