import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Step 1: Read Excel files
df1 = pd.read_excel('file1.xlsx')
df2 = pd.read_excel('file2.xlsx')
df = pd.concat([df1, df2])

# Step 2: Create a chart
def create_chart(dataframe):
    plt.figure(figsize=(10, 5))
    plt.plot(dataframe['Column1'], dataframe['Column2'], label='Line 1')
    plt.xlabel('Column1')
    plt.ylabel('Column2')
    plt.title('Sample Chart')
    plt.legend()
    plt.grid(True)
    plt.savefig('chart.png')  # Save the chart as an image

create_chart(df)

# Step 3: Embed the chart in a Tkinter application
root = tk.Tk()
root.title("Excel Charts in Tkinter")

frame = ttk.Frame(root)
frame.pack(padx=10, pady=10)

img = Image.open('chart.png')
img = ImageTk.PhotoImage(img)

label = ttk.Label(frame, image=img)
label.pack()

root.mainloop()