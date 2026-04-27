
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("План тренировок")
        self.root.geometry("800x600")

        self.data_file = "trainings.json"
        self.trainings = self.load_data()
        self.training_types = ["Кардио", "Силовая", "Растяжка", "Йога", "HIIT", "Другое"]

        # --- Основные фреймы ---
        input_frame = ttk.LabelFrame(root, text="Добавить тренировку", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        filter_frame = ttk.LabelFrame(root, text="Фильтрация", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tree_frame = ttk.Frame(root, padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # --- Поля ввода ---
        ttk.Label(input_frame, text="Дата:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = DateEntry(input_frame, width=12, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.type_combo = ttk.Combobox(input_frame, values=self.training_types, width=20)
        self.type_combo.grid(row=0, column=3, padx=5, pady=5)
        self.type_combo.set(self.training_types[0])

        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.duration_entry = ttk.Entry(input_frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)

        add_button = ttk.Button(input_frame, text="Добавить", command=self.add_training)
        add_button.grid(row=0, column=6, padx=10, pady=5, sticky="e")
        input_frame.grid_columnconfigure(6, weight=1)

        # --- Фильтры ---
        ttk.Label(filter_frame, text="Фильтр по дате (от):").grid(row=0, column=0, padx=5, pady=5)
        self.start_date_filter = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.start_date_filter.grid(row=0, column=1, padx=5)
        self.start_date_filter.set_date(None) # По умолчанию пусто

        ttk.Label(filter_frame, text="(до):").grid(row=0, column=2, padx=2, pady=5)
        self.end_date_filter = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.end_date_filter.grid(row=0, column=3, padx=5)
        self.end_date_filter.set_date(None) # По умолчанию пусто

        ttk.Label(filter_frame, text="Тип тренировки:").grid(row=0, column=4, padx=5, pady=5)
        self.type_filter_combo = ttk.Combobox(filter_frame, values=["Все"] + self.training_types, width=15)
        self.type_filter_combo.grid(row=0, column=5, padx=5)
        self.type_filter_combo.set("Все")

        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_button.grid(row=0, column=6, padx=10)

        # --- Таблица ---
        self.tree = ttk.Treeview(tree_frame, columns=("date", "type", "duration"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        self.tree.column("date", width=150, anchor=tk.CENTER)
        self.tree.column("type", width=250)
        self.tree.column("duration", width=150, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.populate_table(self.trainings)

    def add_training(self):
        date_str = self.date_entry.get()
        training_type = self.type_combo.get()
        duration_str = self.duration_entry.get()

        try:
            duration = int(duration_str)
            if duration <= 0:
                messagebox.showerror("Ошибка ввода", "Длительность должна быть положительным числом.")
                return
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Длительность должна быть целым числом.")
            return
        
        if not training_type:
            messagebox.showerror("Ошибка ввода", "Выберите тип тренировки.")
            return

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Неверный формат даты.")
            return

        new_training = {"date": date_str, "type": training_type, "duration": duration}
        self.trainings.append(new_training)
        self.save_data()
        self.apply_filter()
        self.duration_entry.delete(0, tk.END)

    def populate_table(self, data_to_show):
        for i in self.tree.get_children():
            self.tree.delete(i)

        sorted_data = sorted(data_to_show, key=lambda x: x['date'], reverse=True)
        for training in sorted_data:
            self.tree.insert("", tk.END, values=(training["date"], training["type"], training["duration"]))

    def apply_filter(self):
        start_date_str = self.start_date_filter.get()
        end_date_str = self.end_date_filter.get()
        training_type = self.type_filter_combo.get()

        filtered_data = self.trainings
        
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                filtered_data = [t for t in filtered_data if datetime.strptime(t['date'], '%Y-%m-%d').date() >= start_date]
            
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                filtered_data = [t for t in filtered_data if datetime.strptime(t['date'], '%Y-%m-%d').date() <= end_date]
        except ValueError:
            messagebox.showerror("Ошибка даты", "Некорректный формат даты в фильтре.")
            return

        if training_type != "Все":
            filtered_data = [t for t in filtered_data if t["type"] == training_type]

        self.populate_table(filtered_data)

    def load_data(self):
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.trainings, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
