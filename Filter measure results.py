import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog

class FilterMeasureResultsApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        self.df = None
        self.selected_columns = {}

    def select_file(self):
        input_file_path = filedialog.askopenfilename(title="Select the input Excel file", filetypes=[("Excel files", "*.xlsx")])
        if input_file_path:
            self.df = pd.read_excel(input_file_path)
            self.show_column_selection()

    def show_column_selection(self):
        self.root.deiconify()
        self.root.title("Select the columns to filter")
        lb_columns = tk.Listbox(self.root)
        lb_columns.bind("<Double-Button-1>", self.on_double_click)
        btn_done = tk.Button(self.root, text="Done", command=lambda: self.selection_done(lb_columns))

        # Insert all columns into the listbox
        for column in self.df.columns.tolist():
            lb_columns.insert(tk.END, column)
            
        # Pack the listbox and button
        lb_columns.pack()
        btn_done.pack()

    def on_double_click(self, event):
        lb_columns = event.widget
        selected_column = lb_columns.get(lb_columns.curselection())
        lb_values = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        btn_add = tk.Button(self.root, text="Add", command=lambda: self.add_column_value(selected_column, lb_values, btn_add))

        for value in self.df[selected_column].unique():
            lb_values.insert(tk.END, value)

        lb_values.pack()
        btn_add.pack()

    def add_column_value(self, column, lb_values, btn_add):
        selected_values = [lb_values.get(i) for i in lb_values.curselection()]
        if column in self.selected_columns:
            self.selected_columns[column].extend(selected_values)
        else:
            self.selected_columns[column] = selected_values
        lb_values.destroy()
        btn_add.destroy()

    def selection_done(self, lb_columns):
        selected_indices = lb_columns.curselection()
        for i in selected_indices:
            column = lb_columns.get(i)
            if column not in self.selected_columns:
                self.selected_columns[column] = []
        self.root.quit()
        self.filter_data()

    def filter_data(self):
        if self.df is not None and self.selected_columns:
            filtered_df = self.df
            for column, values in self.selected_columns.items():
                if values:
                    filtered_df = filtered_df[filtered_df[column].astype(str).isin(map(str, values))]
            filtered_df.to_excel('filtered_output.xlsx', index=False)
            print("Filtered data saved to 'filtered_output.xlsx'.")

    def run(self):
        self.select_file()
        self.root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    app = FilterMeasureResultsApp(root)
    app.run()