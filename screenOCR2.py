import difflib
import tkinter as tk
from PIL import Image, ImageTk
import io
import pygetwindow as gw
import mss
import easyocr
import cv2
import numpy as np

reader = easyocr.Reader(['en'])

weapons = {
    "Assault Rifles": [
        "KN-44",
        "XR-2",
        "HVK-30",
        "ICR-1",
        "Man-O-War",
        "Sheiva",
        "M8A7",
        "Peacekeeper MK2",
        "FFAR",
        "MX Garand"
    ],
    "Submachine Guns": [
        "Kuda",
        "VMP",
        "Weevil",
        "Vesper",
        "Pharo",
        "Razorback",
        "HG 40"
    ],
    "Light Machine Guns": [
        "BRM",
        "Dingo",
        "Gorgon",
        "48 Dredge",
        "R70 Ajax"
    ],
    "Sniper Rifles": [
        "Drakon",
        "Locus",
        "SVG-100",
        "P-06",
        "RSA Interdiction"
    ],
    "Shotguns": [
        "KRM-262",
        "205 Brecci",
        "Haymaker 12",
        "Argus",
        "Banshii"
    ],
    "Pistols": [
        "MR6",
        "RK5",
        "L-CAR 9",
        "1911"
    ],
    "Launchers": [
        "XM-53",
        "BlackCell"
    ],
    "Melee Weapons": [
        "Fists",
        "Combat Knife",
        "Butterfly Knife",
        "Wrench",
        "Brass Knuckles",
        "Iron Jim",
        "Fury's Song",
        "MVP",
        "Malice",
        "Carver",
        "Skull Splitter",
        "Slash 'n Burn",
        "Nightbreaker",
        "Buzz Cut",
        "Nunchucks",
        "Raven's Eye",
        "Ace of Spades",
        "Path of Sorrows"
    ],
    "Special Weapons": [
        "NX ShadowClaw",
        "Ballistic Knife",
        "D13 Sector",
        "Rift E9"
    ]
}

def find_closest_weapon_name(gun_name):
    for category, weapon_list in weapons.items():
        closest_matches = difflib.get_close_matches(gun_name, weapon_list, n=1, cutoff=0.4)
        if closest_matches:
            return category, closest_matches[0]
    return ''

def capture_screen_region(region):
    x, y, w, h = region
    with mss.mss() as sct:
        monitor = {
            "left": target_window.left + x,
            "top": target_window.top + y,
            "width": w,
            "height": h
        }
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
    return img

def capture_and_detect_tactical_grenade():
    region = (1617, 907, 50, 50)
    rotation = 9.5
    capture_and_detect_edge(region, rotation, tactical_grenade_text_var, tactical_grenade_img_label, "Tactical Grenade")

def capture_and_detect_lethal_grenade():
    region = (1680, 907, 50, 50)
    rotation = 9.5
    capture_and_detect_edge(region, rotation, lethal_grenade_text_var, lethal_grenade_img_label, "Lethal Grenade")

def capture_and_ocr_bullet_count():
    region = (1565, 960, 70, 58)
    rotation = 9.5
    threshold = 190
    capture_and_ocr_numeric(region, rotation, bullet_count_text_var, bullet_count_img_label, threshold)

def capture_and_ocr_gun_name():
    region = (1520, 1030, 220, 40)
    rotation = 9.5
    threshold = 190
    capture_and_ocr_text(region, rotation, gun_name_text_var, gun_name_img_label, threshold)

def capture_and_ocr_player_score():
    region = (177, 953, 40, 40)
    rotation = -9.5
    threshold = 190
    capture_and_ocr_numeric(region, rotation, player_score_text_var, player_score_img_label, threshold)

def capture_and_ocr_enemy_score():
    region = (177, 1010, 35, 35)
    rotation = -9.5
    threshold = 120
    capture_and_ocr_numeric(region, rotation, highest_enemy_score_text_var, highest_enemy_score_img_label, threshold)

def capture_and_ocr_text(region, rotation, text_var, img_label, threshold):
    img = capture_screen_region(region)
    img = img.rotate(rotation, expand=True)
    img = img.convert('L')
    img = img.point(lambda p: p > threshold and 255)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    result = reader.readtext(img_byte_arr)
    text = " ".join([item[1] for item in result])

    temp = find_closest_weapon_name(text)
    # print(">>>", text, "--->", temp)
    if temp != '':
        text_var.set(temp)
    
    imgTk = ImageTk.PhotoImage(image=Image.open(io.BytesIO(img_byte_arr)))
    img_label.config(image=imgTk)
    img_label.image = imgTk
    img_label.imgTk = imgTk

def capture_and_ocr_numeric(region, rotation, text_var, img_label, threshold):
    img = capture_screen_region(region)
    img = img.rotate(rotation, expand=True)
    img = img.convert('L')
    img = img.point(lambda p: p > threshold and 255)
    
    # Resize image to be twice as large
    img = img.resize((img.width * 2, img.height * 2))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    result = reader.readtext(img_byte_arr, allowlist='0123456789')
    text = " ".join([item[1] for item in result])

    text_var.set(text)
    imgTk = ImageTk.PhotoImage(image=Image.open(io.BytesIO(img_byte_arr)))
    img_label.config(image=imgTk)
    img_label.image = imgTk
    img_label.imgTk = imgTk

def capture_and_detect_edge(region, rotation, text_var, img_label, type=""):
    img = capture_screen_region(region)
    img = img.rotate(rotation, expand=True)
    img = img.convert('L')
    
    # Convert PIL image to OpenCV format
    img_cv = np.array(img)
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_GRAY2BGR)
    
    # Apply Canny edge detection
    edges = cv2.Canny(img_cv, threshold1=400, threshold2=400)

    # Check if the middle section of the region has any white pixels
    mid_x_start, mid_x_end = edges.shape[1] // 3, 2 * edges.shape[1] // 3
    mid_y_start, mid_y_end = edges.shape[0] // 3, 2 * edges.shape[0] // 3
    middle_section = edges[mid_y_start:mid_y_end, mid_x_start:mid_x_end]
    
    if np.any(middle_section == 255):
        text_var.set(type + " Slot Occupied")
    else:
        text_var.set(type + " Slot Empty")

    # Convert back to PIL format
    img_pil = Image.fromarray(edges)
    
    img_byte_arr = io.BytesIO()
    img_pil.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    imgTk = ImageTk.PhotoImage(image=Image.open(io.BytesIO(img_byte_arr)))
    img_label.config(image=imgTk)
    img_label.image = imgTk
    img_label.imgTk = imgTk

def create_floating_window(target_window):
    global root
    root = tk.Tk()
    root.geometry("600x600")

    global bullet_count_text_var, gun_name_text_var, player_score_text_var, highest_enemy_score_text_var, tactical_grenade_text_var, lethal_grenade_text_var
    global bullet_count_img_label, gun_name_img_label, player_score_img_label, highest_enemy_score_img_label, tactical_grenade_img_label, lethal_grenade_img_label

    bullet_count_text_var = tk.StringVar(value="Bullet Count: N/A")
    bullet_count_text_label = tk.Label(root, textvariable=bullet_count_text_var)
    bullet_count_text_label.grid(row=0, column=0, padx=1, pady=1)

    bullet_count_img_label = tk.Label(root)
    bullet_count_img_label.grid(row=0, column=1, padx=1, pady=1)

    gun_name_text_var = tk.StringVar(value="Gun Name: N/A")
    gun_name_text_label = tk.Label(root, textvariable=gun_name_text_var)
    gun_name_text_label.grid(row=1, column=0, padx=1, pady=1)

    gun_name_img_label = tk.Label(root)
    gun_name_img_label.grid(row=1, column=1, padx=1, pady=1)

    player_score_text_var = tk.StringVar(value="Player Score: N/A")
    player_score_text_label = tk.Label(root, textvariable=player_score_text_var)
    player_score_text_label.grid(row=2, column=0, padx=1, pady=1)

    player_score_img_label = tk.Label(root)
    player_score_img_label.grid(row=2, column=1, padx=1, pady=1)

    highest_enemy_score_text_var = tk.StringVar(value="Highest Enemy Score: N/A")
    highest_enemy_score_text_label = tk.Label(root, textvariable=highest_enemy_score_text_var)
    highest_enemy_score_text_label.grid(row=3, column=0, padx=1, pady=1)

    highest_enemy_score_img_label = tk.Label(root)
    highest_enemy_score_img_label.grid(row=3, column=1, padx=1, pady=1)

    tactical_grenade_text_var = tk.StringVar(value="Tactical Grenade: N/A")
    tactical_grenade_text_label = tk.Label(root, textvariable=tactical_grenade_text_var)
    tactical_grenade_text_label.grid(row=4, column=0, padx=1, pady=1)

    tactical_grenade_img_label = tk.Label(root)
    tactical_grenade_img_label.grid(row=4, column=1, padx=1, pady=1)

    lethal_grenade_text_var = tk.StringVar(value="Lethal Grenade: N/A")
    lethal_grenade_text_label = tk.Label(root, textvariable=lethal_grenade_text_var)
    lethal_grenade_text_label.grid(row=5, column=0, padx=1, pady=1)

    lethal_grenade_img_label = tk.Label(root)
    lethal_grenade_img_label.grid(row=5, column=1, padx=1, pady=1)

    update_ocr_results()

def update_ocr_results():
    capture_and_ocr_bullet_count()
    capture_and_ocr_gun_name()
    capture_and_ocr_player_score()
    capture_and_ocr_enemy_score()
    capture_and_detect_tactical_grenade()
    capture_and_detect_lethal_grenade()
    
    root.after(500, update_ocr_results) # Schedule the next update

target_window = None
for window in gw.getAllTitles():
    if window.startswith("Call of Duty"):
        target_window = gw.getWindowsWithTitle(window)[0]
        break

# Start the floating window
create_floating_window(target_window)
root.mainloop()