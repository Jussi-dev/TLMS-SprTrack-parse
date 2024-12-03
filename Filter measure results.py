import pandas as pd
import tkinter as tk
from tkinter import filedialog

# Create a Tkinter root window and hide it
def main():
    root = tk.Tk()
    root.withdraw()

# Open a file dialog to select the input file
    input_file_path = filedialog.askopenfilename(title="Select the input Excel file", filetypes=[("Excel files", "*.xlsx")])

# Read the selected Excel file
    df = pd.read_excel(input_file_path)

# Filter rows based on column values
    filtered_df = df[df['Lane'] == 3]

# Save the filtered subset as a new Excel file
    filtered_df.to_excel('filtered_output.xlsx', index=False)

if __name__ == '__main__':
    main()