import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        self.data_file = "weather_data.json"
        self.records = self.load_data()

        # Создание интерфейса
        self.create_input_frame()
        self.create_records_tree()
        self.create_filter_frame()
        self.create_button_frame()

        self.update_treeview()

    # ---------------------- Ввод данных ----------------------
    def create_input_frame(self):
        frame = tk.LabelFrame(self.root, text="Добавить запись", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Дата
        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", pady=2)
        self.date_entry = tk.Entry(frame, width=15)
        self.date_entry.grid(row=0, column=1, pady=2)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        # Температура
        tk.Label(frame, text="Температура (°C):").grid(row=1, column=0, sticky="w", pady=2)
        self.temp_entry = tk.Entry(frame, width=10)
        self.temp_entry.grid(row=1, column=1, pady=2)

        # Описание
        tk.Label(frame, text="Описание:").grid(row=2, column=0, sticky="w", pady=2)
        self.desc_entry = tk.Entry(frame, width=30)
        self.desc_entry.grid(row=2, column=1, pady=2)

        # Осадки
        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="Осадки", variable=self.precip_var).grid(row=3, column=1, sticky="w", pady=2)

        # Кнопка добавить
        tk.Button(frame, text="Добавить запись", command=self.add_record, bg="#4CAF50", fg="white").grid(row=4, column=0, columnspan=2, pady=10)

    # ---------------------- Таблица записей ----------------------
    def create_records_tree(self):
        frame = tk.LabelFrame(self.root, text="Записи о погоде", padx=10, pady=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Дата", "Температура", "Описание", "Осадки")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ---------------------- Фильтрация ----------------------
    def create_filter_frame(self):
        frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по дате
        tk.Label(frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5)
        self.filter_date_entry = tk.Entry(frame, width=12)
        self.filter_date_entry.grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Применить", command=self.apply_filter).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=3, padx=5)

        # Фильтр по температуре
        tk.Label(frame, text="Температура выше (°C):").grid(row=1, column=0, padx=5)
        self.filter_temp_entry = tk.Entry(frame, width=5)
        self.filter_temp_entry.grid(row=1, column=1, padx=5, sticky="w")
        tk.Button(frame, text="Применить", command=self.apply_temp_filter).grid(row=1, column=2, padx=5)

    def create_button_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Button(frame, text="Сохранить в JSON", command=self.save_to_file, bg="#2196F3", fg="white").pack(side="left", padx=5)
        tk.Button(frame, text="Загрузить из JSON", command=self.load_from_file, bg="#FF9800", fg="white").pack(side="left", padx=5)

    # ---------------------- Логика работы с данными ----------------------
    def add_record(self):
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()

        # Валидация
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        try:
            temp = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        if not description:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        self.records.append({
            "date": date,
            "temperature": temp,
            "description": description,
            "precipitation": precipitation
        })

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

        self.update_treeview()
        messagebox.showinfo("Успех", "Запись добавлена")

    def update_treeview(self, filtered_records=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        records_to_show = filtered_records if filtered_records is not None else self.records
        for rec in records_to_show:
            precip_text = "Да" if rec["precipitation"] else "Нет"
            self.tree.insert("", tk.END, values=(
                rec["date"],
                f"{rec['temperature']}°C",
                rec["description"],
                precip_text
            ))

    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        if not filter_date:
            messagebox.showwarning("Внимание", "Введите дату для фильтрации")
            return

        filtered = [r for r in self.records if r["date"] == filter_date]
        self.update_treeview(filtered)
        if not filtered:
            messagebox.showinfo("Результат", f"Нет записей за {filter_date}")

    def apply_temp_filter(self):
        temp_str = self.filter_temp_entry.get().strip()
        if not temp_str:
            messagebox.showwarning("Внимание", "Введите значение температуры")
            return

        try:
            temp_threshold = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        filtered = [r for r in self.records if r["temperature"] > temp_threshold]
        self.update_treeview(filtered)
        if not filtered:
            messagebox.showinfo("Результат", f"Нет записей с температурой выше {temp_threshold}°C")

    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_treeview()

    # ---------------------- Работа с JSON ----------------------
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_to_file(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранено", f"Данные сохранены в {self.data_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_file(self):
        if os.path.exists(self.data_file):
            self.records = self.load_data()
            self.update_treeview()
            messagebox.showinfo("Загружено", "Данные загружены из файла")
        else:
            messagebox.showerror("Ошибка", "Файл не найден")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
