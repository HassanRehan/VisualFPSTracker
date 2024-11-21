import difflib
import tkinter as tk
from PIL import Image, ImageTk
import io
import pygetwindow as gw
import mss
import easyocr
import cv2
import numpy as np
from openpyxl import Workbook
import time

# Constants
ROTATION = 9.5
THRESHOLD = 190
UPDATE_INTERVAL = 800  # in milliseconds
EXCEL_FILE = "ocr_data.xlsx"
GUN_NAME_MATCH_THRESHOLD = 0.5

# Weapon categories and names
weapons = {
    "Assault Rifles": ["KN-44", "XR-2", "HVK-30", "ICR-1", "Man-O-War", "Sheiva", "M8A7", "Peacekeeper MK2", "FFAR", "MX Garand"],
    "Submachine Guns": ["Kuda", "VMP", "Weevil", "Vesper", "Pharo", "Razorback", "HG 40"],
    "Light Machine Guns": ["BRM", "Dingo", "Gorgon", "48 Dredge", "R70 Ajax"],
    "Sniper Rifles": ["Drakon", "Locus", "SVG-100", "P-06", "RSA Interdiction"],
    "Shotguns": ["KRM-262", "205 Brecci", "Haymaker 12", "Argus", "Banshii"],
    "Pistols": ["MR6", "RK5", "L-CAR 9", "1911"],
    "Launchers": ["XM-53", "BlackCell"],
    "Melee Weapons": ["Fists", "Combat Knife", "Butterfly Knife", "Wrench", "Brass Knuckles", "Iron Jim", "Fury's Song", "MVP", "Malice", "Carver", "Skull Splitter", "Slash 'n Burn", "Nightbreaker", "Buzz Cut", "Nunchucks", "Raven's Eye", "Ace of Spades", "Path of Sorrows"],
    "Special Weapons": ["NX ShadowClaw", "Ballistic Knife", "D13 Sector", "Rift E9"]
}

def save_to_excel(bullet_count, gun_name, player_score, enemy_score, lethal_grenade, tactical_grenade, killcam_status):
    """Save results to an Excel file."""
    # elapsed_time = round(time.time() - start_time, 1)
    elapsed_time = int(time.time() - start_time)
    ws.append([elapsed_time, bullet_count, gun_name, player_score, enemy_score, lethal_grenade, tactical_grenade, killcam_status])
    wb.save(EXCEL_FILE)

def find_closest_weapon_name(gun_name):
    """Find the closest matching weapon name from the list of weapon categories."""
    closest_matches = difflib.get_close_matches(gun_name, all_weapon_names, n=1, cutoff=GUN_NAME_MATCH_THRESHOLD)
    if closest_matches:
        closest_weapon = closest_matches[0]
        category = weapon_name_to_category[closest_weapon]
        return f"{category}: {closest_weapon}"
    return ''

def capture_screen_region(region):
    """Capture a specific region of the screen."""
    x, y, w, h = region
    with mss.mss() as sct:
        monitor = {"left": target_window.left + x, "top": target_window.top + y, "width": w, "height": h}
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
    return img

def capture_and_detect_grenade(region, text_var, img_label, grenade_type):
    """Capture a region of the screen and detect if a grenade is present."""
    capture_and_detect_edge(region, ROTATION, text_var, img_label, grenade_type)
    return "Occupied" if "Occupied" in text_var.get() else "Empty"

def capture_and_ocr(region, rotation, text_var, img_label, threshold, is_numeric=False):
    """Capture a region of the screen and perform OCR on the image."""
    img = capture_screen_region(region)
    img = img.rotate(rotation, expand=True).convert('L').point(lambda p: p > threshold and 255)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    result = reader.readtext(img_byte_arr)
    text = "".join([item[1] for item in result if item[1].isdigit()]) if is_numeric else " ".join([item[1] for item in result])
    text_var.set(text)
    imgTk = ImageTk.PhotoImage(image=Image.open(io.BytesIO(img_byte_arr)))
    img_label.config(image=imgTk)
    img_label.image = imgTk
    return text

def capture_and_ocr_bullet_count():
    """Capture and OCR the bullet count from the screen."""
    return capture_and_ocr((1565, 960, 70, 58), ROTATION, bullet_count_text_var, bullet_count_img_label, THRESHOLD, is_numeric=True)

def capture_and_ocr_gun_name():
    """Capture and OCR the gun name from the screen."""
    gun_name = capture_and_ocr((1520, 1030, 220, 40), ROTATION, gun_name_text_var, gun_name_img_label, THRESHOLD)
    closest_weapon_name = find_closest_weapon_name(gun_name)
    gun_name_text_var.set(closest_weapon_name)
    return closest_weapon_name

def capture_and_ocr_player_score():
    """Capture and OCR the player score from the screen."""
    return capture_and_ocr((177, 953, 90, 40), -ROTATION, player_score_text_var, player_score_img_label, THRESHOLD, is_numeric=True)

def capture_and_ocr_enemy_score():
    """Capture and OCR the highest enemy score from the screen."""
    return capture_and_ocr((182, 1010, 70, 35), -ROTATION, highest_enemy_score_text_var, highest_enemy_score_img_label, 120, is_numeric=True)

def capture_and_detect_killcam(region, text_var, img_label):
    """Capture a region of the screen and detect if the killcam is active."""
    text = capture_and_ocr(region, 0, text_var, img_label, THRESHOLD)
    status = "Killed" if "kill" in text.lower() else "Alive"
    text_var.set(status)
    return status

def capture_and_detect_edge(region, rotation, text_var, img_label, type=""):
    """Capture a region of the screen and detect edges."""
    img = capture_screen_region(region).rotate(rotation, expand=True).convert('L')
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_GRAY2BGR)
    edges = cv2.Canny(img_cv, threshold1=400, threshold2=400)
    mid_section = edges[edges.shape[0] // 3:2 * edges.shape[0] // 3, edges.shape[1] // 3:2 * edges.shape[1] // 3]
    text_var.set(f"{type} Slot {'Occupied' if np.any(mid_section == 255) else 'Empty'}")
    img_pil = Image.fromarray(edges)
    img_byte_arr = io.BytesIO()
    img_pil.save(img_byte_arr, format='PNG')
    imgTk = ImageTk.PhotoImage(image=Image.open(io.BytesIO(img_byte_arr.getvalue())))
    img_label.config(image=imgTk)
    img_label.image = imgTk

def create_floating_window(target_window):
    """Create a floating window to display the OCR results."""
    global root, bullet_count_text_var, gun_name_text_var, player_score_text_var, highest_enemy_score_text_var, tactical_grenade_text_var, lethal_grenade_text_var, killcam_text_var
    global bullet_count_img_label, gun_name_img_label, player_score_img_label, highest_enemy_score_img_label, tactical_grenade_img_label, lethal_grenade_img_label, killcam_img_label
    global session_kills_text_var, kills_streak_text_var, deaths_text_var, kdr_text_var, highest_consecutive_kills_text_var

    root = tk.Tk()
    root.title("OCR Tracker")
    root.geometry("800x600")

    bullet_count_text_var = tk.StringVar(value="Bullet Count: N/A")
    gun_name_text_var = tk.StringVar(value="Gun Name: N/A")
    player_score_text_var = tk.StringVar(value="Player Score: N/A")
    highest_enemy_score_text_var = tk.StringVar(value="Highest Enemy Score: N/A")
    tactical_grenade_text_var = tk.StringVar(value="Tactical Grenade: N/A")
    lethal_grenade_text_var = tk.StringVar(value="Lethal Grenade: N/A")
    killcam_text_var = tk.StringVar(value="Killcam: N/A")
    session_kills_text_var = tk.StringVar(value="Session Kills: 0")
    kills_streak_text_var = tk.StringVar(value="Current kill streak: 0")
    deaths_text_var = tk.StringVar(value="Deaths: 0")
    kdr_text_var = tk.StringVar(value="K/D Ratio: 0.0")
    highest_consecutive_kills_text_var = tk.StringVar(value="Highest Kill Streak: 0")

    labels = [
        (bullet_count_text_var, "Bullet Count: N/A"),
        (gun_name_text_var, "Gun Name: N/A"),
        (player_score_text_var, "Player Score: N/A"),
        (highest_enemy_score_text_var, "Highest Enemy Score: N/A"),
        (tactical_grenade_text_var, "Tactical Grenade: N/A"),
        (lethal_grenade_text_var, "Lethal Grenade: N/A"),
        (killcam_text_var, "Killcam: N/A"),
        (session_kills_text_var, "Session Kills: 0"),
        (kills_streak_text_var, "Current Kill streak: 0"),
        (deaths_text_var, "Session Deaths: 0"),
        (kdr_text_var, "Session K/D Ratio: 0.0"),
        (highest_consecutive_kills_text_var, "Session Highest Kill Streak: 0")
    ]

    for i, (text_var, default_text) in enumerate(labels):
        text_label = tk.Label(root, textvariable=text_var)
        text_label.grid(row=i, column=0, padx=1, pady=1)
        img_label = tk.Label(root)
        img_label.grid(row=i, column=1, padx=1, pady=1)
        if i == 0:
            bullet_count_img_label = img_label
        elif i == 1:
            gun_name_img_label = img_label
        elif i == 2:
            player_score_img_label = img_label
        elif i == 3:
            highest_enemy_score_img_label = img_label
        elif i == 4:
            tactical_grenade_img_label = img_label
        elif i == 5:
            lethal_grenade_img_label = img_label
        elif i == 6:
            killcam_img_label = img_label

    update_ocr_results()

def update_ocr_results():
    """Update the OCR results in the floating window."""
    global current_kills_streak, session_kills, deaths, highest_consecutive_kills, initial_player_score, killcam_flag, kill_flag

    bullet_count = capture_and_ocr_bullet_count()
    gun_name = capture_and_ocr_gun_name()
    player_score = capture_and_ocr_player_score()
    enemy_score = capture_and_ocr_enemy_score()
    lethal_grenade = capture_and_detect_grenade((1680, 907, 50, 50), lethal_grenade_text_var, lethal_grenade_img_label, "Lethal Grenade")
    tactical_grenade = capture_and_detect_grenade((1617, 907, 50, 50), tactical_grenade_text_var, tactical_grenade_img_label, "Tactical Grenade")
    killcam = capture_and_detect_killcam((645, 80, 640, 60), killcam_text_var, killcam_img_label)

    # Update kills and deaths
    if player_score.isdigit():
        player_score = int(player_score)
        if initial_player_score is None:
            initial_player_score = player_score
        elif player_score > initial_player_score + session_kills:
            session_kills += 1
            current_kills_streak += 1
            session_kills_text_var.set(f"Session Kills: {session_kills}")
            kill_flag = False

    if "kill" in killcam.lower():
        if not killcam_flag:
            deaths += 1
            highest_consecutive_kills = max(highest_consecutive_kills, current_kills_streak)
            current_kills_streak = 0
            deaths_text_var.set(f"Session Deaths: {deaths}")
        killcam_flag = True
    else:
        killcam_flag = False

    # Update K/D ratio
    kdr = session_kills / deaths if deaths > 0 else current_kills_streak

    # Update the new labels
    kills_streak_text_var.set(f"Current Kill streak: {current_kills_streak}")
    kdr_text_var.set(f"Session K/D Ratio: {kdr:.2f}")
    highest_consecutive_kills_text_var.set(f"Session Highest Kill Streak: {highest_consecutive_kills}")

    save_to_excel(bullet_count, gun_name, player_score, enemy_score, lethal_grenade, tactical_grenade, killcam)
    root.after(UPDATE_INTERVAL, update_ocr_results)

# Preprocess weapon names and categories
weapon_name_to_category = {}
for category, weapon_list in weapons.items():
    for weapon in weapon_list:
        weapon_name_to_category[weapon] = category

all_weapon_names = list(weapon_name_to_category.keys())

# Initialize the target window
target_window = next((gw.getWindowsWithTitle(window)[0] for window in gw.getAllTitles() if window.startswith("Call of Duty")), None)

# Initialize the OCR reader
reader = easyocr.Reader(['en'])

# Initialize the Excel workbook and worksheet
wb = Workbook()
ws = wb.active
ws.title = "OCR Data"
ws.append(["Elapsed Time (s)", "Bullet Count", "Gun Name", "Player Score", "Enemy Score", "Lethal Grenade", "Tactical Grenade", "Killcam Status"])

# Record the start time of the program
start_time = time.time()

# Initialize variables to track kills, deaths, and highest consecutive kills
initial_player_score = None
current_kills_streak = 0
session_kills = 0
deaths = 0
highest_consecutive_kills = 0
killcam_flag = False
kill_flag = False


# Start the floating window
create_floating_window(target_window)
root.mainloop()