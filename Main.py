import bisect
import ctypes
import datetime
import json
import os.path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import tkcalendar
from PIL import Image, ImageTk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from DataBase import *
from config import *


def is_valid(text: str):
    try:
        Product.get(Product.name.contains(text.lower()) | Product.name.contains(text.capitalize()))
    except Exception:
        return False
    return True


def hash_date(month, day, year):
    return str(month * 1000 + day + year * 10_000_000)


days = dict()
try:
    with open("days.json", "r") as file:
        days = dict(json.load(file))
except Exception:
    pass

water_cap: int
calorie_cap: int


class RegistrationWindow:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Новый пользователь")
        self.window.geometry("900x1200")
        self.window.resizable(False, False)

        self.window.tk.call("tk", "scaling", 3)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

        self.height_label = tk.Label(self.window, text="Рост")
        self.height_label.place(x=194, y=70)

        self.weight_label = tk.Label(self.window, text="Вес")
        self.weight_label.place(x=394, y=70)

        self.age_label = tk.Label(self.window, text="Возраст")
        self.age_label.place(x=594, y=70)

        self.height_box = tk.Spinbox(self.window, from_=130, to=210)
        self.height_box.place(x=194, y=120, width=100)

        self.weight_box = tk.Spinbox(self.window, from_=35, to=150)
        self.weight_box.place(x=394, y=120, width=100)

        self.age_box = tk.Spinbox(self.window, from_=14, to=99)
        self.age_box.place(x=594, y=120, width=100)

        self.sex_group = tk.LabelFrame(self.window, text="Пол")
        self.sex_group.place(x=250, y=200, width=400, height=240)

        self.target_group = tk.LabelFrame(self.window, text="Цель использования")
        self.target_group.place(x=250, y=450, width=400, height=240)

        self.activity_group = tk.LabelFrame(self.window, text="Уровень активности")
        self.activity_group.place(x=250, y=700, width=400, height=240)

        self.enter_main = tk.Button(self.window, text="Подтвердить", command=self.create_main_window)
        self.enter_main.place(x=200, y=1000, width=500, height=100)

        self.sex = tk.BooleanVar()
        self.target = tk.DoubleVar()
        self.activity = tk.DoubleVar()

        radio = tk.Radiobutton(self.sex_group, text="Мужской", variable=self.sex, value=True)
        radio.place(x=20, y=20)
        radio.select()

        radio = tk.Radiobutton(self.sex_group, text="Женский", variable=self.sex, value=False)
        radio.place(x=20, y=70)

        radio = tk.Radiobutton(self.target_group, text="Похудение", variable=self.target, value=0.85)
        radio.place(x=20, y=20)
        radio.select()

        radio = tk.Radiobutton(self.target_group, text="Набор", variable=self.target, value=1.15)
        radio.place(x=20, y=120)

        radio = tk.Radiobutton(self.target_group, text="Поддержание", variable=self.target, value=1)
        radio.place(x=20, y=70)

        radio = tk.Radiobutton(self.activity_group, text="Маленький", variable=self.activity, value=0.89)
        radio.place(x=20, y=20)
        radio.select()

        radio = tk.Radiobutton(self.activity_group, text="Умеренный", variable=self.activity, value=1)
        radio.place(x=20, y=70)

        radio = tk.Radiobutton(self.activity_group, text="Высокий", variable=self.activity, value=1.115)
        radio.place(x=20, y=120)

        self.color_default()

        self.window.config(bg=bg_color)

    def color_default(self):
        for label in filter(
                lambda a: isinstance(a, tk.Label) or isinstance(a, tk.LabelFrame) or isinstance(a,
                                                                                                tk.Button),
                self.window.children.values()):
            if isinstance(label, tk.LabelFrame):
                for label_ in label.children.values():
                    label_.config(fg=fg_color, bg=bg_color, activebackground=bg_color)
            elif isinstance(label, tk.Button):
                label.config(activebackground=bg_color)
            label.config(fg=fg_color, bg=bg_color)

    def initialize(self):
        self.window.mainloop()

    def create_main_window(self):
        hwa = []
        self.color_default()
        flag = False
        for box in filter(lambda a: isinstance(a, tk.Spinbox), self.window.children.values()):
            try:
                hwa.append(float(box.get()))
            except ValueError:
                box.config(bg="red")
                flag = True
        if flag: return
        if hwa[0] < 130 or hwa[0] > 220:
            self.height_box.config(bg="red")
            flag = True
        if hwa[1] < 35 or hwa[1] > 170:
            self.weight_box.config(bg="red")
            flag = True
        if hwa[2] < 10 or hwa[2] > 99 or hwa[2] % 1 != 0:
            self.age_box.config(bg="red")
            flag = True
        if flag:
            return
        else:
            with open("user.txt", "w") as file:
                if self.sex.get():
                    file.write(str(int((66.5 + (13.75 * hwa[1]) + (5.003 * hwa[0]) - (
                            6.775 * hwa[2])) * 1.55 * self.target.get() * self.activity.get())))
                else:
                    file.write(str(int((655 + (9.563 * hwa[1]) + (1.85 * hwa[0]) - (
                            4.676 * hwa[2])) * 1.55 * self.target.get() * self.activity.get())))
                water = 105
                file.write(f"\n{water}")
            self.window.destroy()


class MainWindow:
    selected_product = None
    photos = []
    now = hash_date(datetime.datetime.now().month, datetime.datetime.now().day, datetime.datetime.now().year)
    active_part = []

    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("1700x1200")
        self.window.title("Главное окно")
        self.window.tk.call("tk", "scaling", 3)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

        if not days.get(self.now):
            days[self.now] = {"__water": 0, "__calories": 0, "__carbohydrates": 0, "__proteins": 0, "__fats": 0}

        with open("user.txt", "r") as file:
            data = file.read().split("\n")
            global calorie_cap, water_cap
            calorie_cap = int(data[0])
            water_cap = int(data[1])

        style = ttk.Style()
        style.theme_use('clam')

        style.configure("Custom.Treeview", rowheight=200)
        style.configure("Parts.Treeview", rowheight=40, background="#0000000")

        self.table = ttk.Treeview(self.window, columns=("Text",), style="Custom.Treeview")
        self.table.heading("#0", text="Продукт", anchor="center")
        self.table.heading("Text", text="", anchor="center")
        self.table.column("Text", anchor="center")
        self.table.column("#0", width=100)
        self.table.place(x=20, y=20, width=700, height=700)

        prod_name = tk.StringVar()
        self.product_name_box = ttk.Combobox(self.window, textvariable=prod_name, validate='focusout',
                                             validatecommand=(self.window.register(is_valid), '%P'),
                                             values=[prod.name for prod in Product.select()])
        self.product_name_box.bind("<KeyRelease>", self.modified)
        self.product_name_box.bind("<Return>", self.return_)
        self.product_name_box.bind("<<ComboboxSelected>>", self.selected)
        self.product_name_box.place(x=800, y=240, width=400)

        self.new_product_button = tk.Button(self.window, command=self.create_new_product_window, text="+",
                                            font="Helvetica 15", borderwidth=1)
        self.new_product_button.place(x=1210, y=240, height=40, width=40)
        self.new_product_button.config(bg=bg_color)

        self.image_box = tk.Label(self.window, bg=bg_color)
        self.image_box.place(x=800, y=20, height=200, width=200)
        self.image_label = tk.Label(self.window, bg=bg_color)
        self.image_label.place(x=1020, y=30)

        self.weight_label = tk.Label(self.window, bg=bg_color, text='Вес продукта:\t           грамм')
        self.weight_label.place(x=796, y=290)

        self.weight_box = tk.Spinbox(self.window, from_=10, to=999, increment=10)
        self.weight_box.place(y=290, x=1000, width=100)

        self.add_product_butt = tk.Button(self.window, text="Добавить", command=self.add_product)
        self.add_product_butt.place(x=800, y=340, width=400)

        self.new_part_butt = tk.Button(self.window, text="Новый приём пищи", command=self.add_part)
        self.new_part_butt.place(x=425, y=1000)

        self.part_box = tk.Text(self.window)
        self.part_box.place(x=460, y=950, width=200, height=40)

        style.configure("Treeview", background="#FFFFFF", rowheight=40)

        self.parts_table = ttk.Treeview(self.window, style="Parts.Treeview")
        self.parts_table.heading("#0", text="Приём пищи", anchor="center")
        self.parts_table.column("#0", width=320)
        self.parts_table.place(x=396, y=740, height=200)

        self.date_choose = tkcalendar.DateEntry(self.window, date_pattern="dd.mm.yyyy")
        self.date_choose.place(x=1400, y=20)

        def on_date_change(event):
            self.now = hash_date(self.date_choose.get_date().month, self.date_choose.get_date().day,
                                 self.date_choose.get_date().year)
            self.clear_table(self.table)
            self.clear_table(self.parts_table)
            self.create_parts_table()
            self.water_progress["value"] = 0
            if not days[self.now].get("__water"):
                days[self.now]["__water"] = 0
            add_water(days[self.now].get("__water") // 15)
            self.active_part = None
            self.update_total()

        self.date_choose.bind("<<DateEntrySelected>>", on_date_change)

        def part_selected(event):
            self.active_part = self.parts_table.item(self.parts_table.focus(), "values")[0]
            self.clear_table(self.table)
            for prod, weight in days[self.now][self.active_part].items():
                try:
                    self.append_product(Product.get(Product.name == prod), weight)
                except Exception:
                    pass

        self.parts_table.bind("<<TreeviewSelect>>", part_selected)
        self.create_parts_table()

        style.configure("blue.Vertical.TProgressbar", troughcolor='white', background="blue")

        self.water_progress = ttk.Progressbar(self.window, orient="vertical", mode="determinate", length=240,
                                              maximum=100, style="blue.Vertical.TProgressbar")
        self.water_progress.place(x=120, y=740, width=140)

        def add_water(num=1):
            if not num:
                days[self.now]["__water"] = 0
                num = 0
            self.water_progress["value"] += 15 * num
            days[self.now]["__water"] = self.water_progress["value"]
            if self.water_progress["value"] >= water_cap:
                self.add_water_butt.config(state="disabled")
                style.configure("blue.Vertical.TProgressbar", troughcolor='white', background="light green")
            else:
                self.add_water_butt.config(state="active")
                style.configure("blue.Vertical.TProgressbar", troughcolor='white', background="blue")
            self.window.update_idletasks()

        self.add_water_butt = tk.Button(self.window, command=add_water, text="Стакан воды")
        self.add_water_butt.place(x=100, y=1000)
        add_water(days[self.now].get("__water") // 15)

        self.total_label = tk.Label(self.window, background=bg_color)
        self.total_label.place(x=840, y=440)
        self.update_total()

        self.start_date = tkcalendar.DateEntry(self.window, date_pattern="dd.mm.yy")
        self.start_date.place(x=840, y=950, width=140)

        self.end_date = tkcalendar.DateEntry(self.window, date_pattern="dd.mm.yy")
        self.end_date.place(x=1020, y=950, width=140)

        self.chertochka = tk.Label(self.window, text="-", bg=bg_color)
        self.chertochka.place(x=990, y=950)

        self.otchet_button = tk.Button(self.window, command=self.create_otchet, text="Отчет")
        self.otchet_button.place(x=840, y=1000, width=320)

    def create_otchet(self):
        start = self.start_date.get_date()
        end = self.end_date.get_date()
        if end < start:
            messagebox.showerror("Ошибка даты", "Конечная дата не должна быть меньше начальной даты")
            return
        o = DiagramWindow(self.window, self, start, end)

    def update_total(self):
        now = days.get(self.now)
        prots = now.get("__proteins")
        fats = now.get("__fats")
        carbs = now.get("__carbohydrates")
        text = (f"Итого калорий: {int(now.get("__calories"))}/{calorie_cap}\n"
                f"Белков: {round(prots, 1)}\n"
                f"Жиров: {round(fats, 1)}\n"
                f"Углеводов: {round(carbs, 1)}")
        self.total_label.config(text=text)

    def create_parts_table(self):
        if days.get(self.now):
            for part in days[self.now].keys():
                if part.startswith("__"):
                    continue
                self.add_part_text(part)
        else:
            days[self.now] = {"__water": 0, "__calories": 0, "__carbohydrates": 0, "__proteins": 0, "__fats": 0}

    def clear_table(self, table):
        for item in table.get_children():
            table.delete(item)

    def disable_widgets(self, widget):
        self.new_product_button.configure(state='disabled')

    def enable_widgets(self, widget):
        self.new_product_button.configure(state='normal')

    def add_part(self):
        text = self.part_box.get("1.0", tk.END).strip()
        if text:
            days[self.now][text] = {}
            self.parts_table.insert("", 'end', text=text, values=[text])

    def add_part_text(self, text):
        self.parts_table.insert("", 'end', text=text, values=[text])

    def modified(self, event):
        self.product_name_box.config(values=[prod.name for prod in Product.select().where(
            Product.name.contains(self.product_name_box.get().lower()) | Product.name.contains(
                self.product_name_box.get().capitalize()))])

    def return_(self, event):
        self.product_name_box.event_generate('<Down>')

    def selected(self, event):
        self.selected_product = Product.get(Product.name == self.product_name_box.get())
        self.update_product_info()

    def initialize(self):
        self.window.config(bg=bg_color)
        self.window.mainloop()

    def update_product_info(self):
        try:
            self.img = ImageTk.PhotoImage(Image.open(self.selected_product.photo).resize((200, 200)))
        except Exception:
            self.img = ImageTk.PhotoImage(Image.open("default.png").resize((200, 200)))
        self.photos.append(self.img)
        self.image_label.config(text=self.selected_product.to_str())
        self.image_box.config(image=self.img)

    def add_product(self):
        if not self.active_part:
            messagebox.showerror("Не выбран приём пищи",
                                 "Выберите приём пищи, либо создайте новый для добавления продуктов")
            return
        try:
            self.img = ImageTk.PhotoImage(Image.open(self.selected_product.photo).resize((200, 200)))
        except Exception:
            self.img = ImageTk.PhotoImage(Image.open("default.png").resize((200, 200)))
        self.photos.append(self.img)
        weight = float(self.weight_box.get()) / 100
        if weight >= 10 or weight < 0.1:
            messagebox.showerror("Вес продукта некорректен", "Введите корректный вес продукта")
            return
        self.table.insert("", 'end', text="",
                          values=(str(self.selected_product.to_str(weight)),),
                          image=self.img)
        days[self.now][self.active_part][self.selected_product.name] = weight
        days[self.now]["__carbohydrates"] += self.selected_product.carbs * weight
        days[self.now]["__fats"] += self.selected_product.fats * weight
        days[self.now]["__proteins"] += self.selected_product.prots * weight
        days[self.now]["__calories"] += self.selected_product.callories * weight
        self.update_total()

    def append_product(self, prod, weight):
        try:
            self.img = ImageTk.PhotoImage(Image.open(prod.photo).resize((200, 200)))
        except Exception:
            self.img = ImageTk.PhotoImage(Image.open("default.png").resize((200, 200)))
        self.photos.append(self.img)
        self.table.insert("", 'end', text="",
                          values=(str(prod.to_str(weight)),),
                          image=self.img)

    def create_new_product_window(self):
        self.disable_widgets(self.window)
        new_product_window = NewProductWindow(self.window, self)
        new_product_window.protocol("WM_DELETE_WINDOW", lambda: self.on_close_new_product_window(new_product_window))
        new_product_window.initialize()

    def on_close_new_product_window(self, new_product_window):
        new_product_window.destroy()
        self.enable_widgets(self.window)


class NewProductWindow(tk.Toplevel):

    def __init__(self, parent, main_window):
        super().__init__()
        self.path = "default.png"
        self.main_window = main_window
        self.title("Новый продукт")
        self.geometry("800x500")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window = self
        self.style = ttk.Style()
        self.style.configure("Label", bg=bg_color)
        self.window.resizable(False, False)

        def make_white(event):
            event.widget.config(bg="white")

        self.label = tk.Label(self.window, text="Белки")
        self.label.place(x=40, y=40)

        self.prot_spin = tk.Spinbox(self.window, from_=0, to=100)
        self.prot_spin.place(x=44, y=84, width=110)

        self.label = tk.Label(self.window, text="Жиры")
        self.label.place(x=40, y=140)

        self.fat_spin = tk.Spinbox(self.window, from_=0, to=100)
        self.fat_spin.place(x=44, y=184, width=110)

        self.label = tk.Label(self.window, text="Углеводы")
        self.label.place(x=40, y=240)

        self.carb_spin = tk.Spinbox(self.window, from_=0, to=100)
        self.carb_spin.place(x=44, y=284, width=110)

        self.label = tk.Label(self.window, text="Калории")
        self.label.place(x=44, y=340)

        self.calorie_spin = tk.Spinbox(self.window, from_=0, to=999)
        self.calorie_spin.place(x=44, y=384, width=110)

        self.label = tk.Label(self.window, text="Название продукта")
        self.label.place(x=300, y=200)

        self.text_box = tk.Text(self.window, font="ComicSans 10")
        self.text_box.place(x=300, y=250, height=40, width=220)

        def change_text(event):
            self.text_box.delete("1.0", tk.END)
            self.text_box.config(bg="white")

        self.text_box.bind("<Button-1>", change_text)

        self.submit = tk.Button(self.window, command=self.check_info, text="Добавить")
        self.submit.place(x=300, y=300, width=220)

        self.add_photo_butt = tk.Button(self.window, command=self.add_photo, borderwidth=1, text="+",
                                        font="Helvetica 30", bg=bg_color)
        self.add_photo_butt.place(x=530, y=250, height=40, width=40)

        self.drop_base_butt = tk.Button(self.window, command=self.DROP_DATABASE_NAHOI, borderwidth=1, text="⭕",
                                        bg=bg_color)
        self.drop_base_butt.place(y=10, x=750, height=40, width=40)

        for lebel in self.winfo_children():
            if isinstance(lebel, tk.Label):
                lebel.config(bg=bg_color)
            if isinstance(lebel, tk.Spinbox):
                lebel.bind("<Button-1>", make_white)

    def check_info(self):
        p = None
        try:
            p = Product.get(Product.name == self.text_box.get("1.0", tk.END)[:-1])
            res = messagebox.askyesno("Изменение существующего продукта", "Вы точно хотите изменить данные о продукте?")
            if res:
                raise Exception
            else:
                self.text_box.config(bg="red")
        except Exception:
            data = []
            flag = False
            for child in self.winfo_children():
                if isinstance(child, tk.Spinbox):
                    try:
                        data.append(float(child.get()))
                    except ValueError:
                        flag = True
                        child.config(bg="red")
            if flag:
                return
            if sum(data[:3]) > 100:
                for child in self.winfo_children():
                    if isinstance(child, tk.Spinbox):
                        child.config(bg="red")
                self.calorie_spin.config(bg="white")
                return

            id_ = Product.select().order_by(Product.ID.desc()).get().ID
            if p:
                id_ = p.ID - 1
            p = Product(name=self.text_box.get("1.0", tk.END)[:-1], prots=data[0], fats=data[1], carbs=data[2],
                        callories=data[3], ID=id_ + 1, photo=self.path)
            try:
                Product.create(name=self.text_box.get("1.0", tk.END)[:-1], prots=data[0], fats=data[1], carbs=data[2],
                               callories=data[3], ID=id_ + 1, photo=self.path)
            except Exception:
                pass
            p.save()
            self.main_window.on_close_new_product_window(self)

    def on_close(self):
        self.destroy()

    def initialize(self):
        self.config(bg=bg_color)
        self.mainloop()

    def add_photo(self):
        filetypes = [("JPEG files", "*.jpg;*.jpeg"), ("PNG files", "*.png"), ("BMP files", "*.bmp"),
                     ("GIF files", "*.gif"), ("PPM files", "*.ppm")]
        self.path = filedialog.askopenfilename(filetypes=filetypes)

    def DROP_DATABASE_NAHOI(self):
        with open(r"Backup\Products.db", "rb") as file:
            with open(r"Products.db", "wb") as to_rewrite:
                to_rewrite.write(file.read())
        self.main_window.on_close_new_product_window(self)


class DiagramWindow(tk.Toplevel):

    def __init__(self, parent, main_window, start_date, end_date):
        super().__init__()
        self.main_window = main_window
        self.title("Отчет")
        self.geometry("2100x1050")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window = self
        self.style = ttk.Style()
        self.style.configure("Label", bg=bg_color)
        self.window = self
        self.start = hash_date(start_date.month, start_date.day, start_date.year)
        self.end = hash_date(end_date.month, end_date.day, end_date.year)
        self.days_in_format = sorted(map(int, days.keys()))
        start_i = bisect.bisect_left(self.days_in_format, int(self.start))
        end_i = bisect.bisect_left(self.days_in_format, int(self.end) + 1)

        total_calories = 0
        total_fats = 0
        total_carbohydrates = 0
        total_proteins = 0
        total_water = 0

        for day in self.days_in_format[start_i: end_i]:
            data = days.get(str(day))
            total_water += data.get("__water")
            total_calories += data.get("__calories")
            total_fats += data.get("__fats")
            total_carbohydrates += data.get("__carbohydrates")
            total_proteins += data.get("__proteins")

        total = total_fats + total_carbohydrates + total_proteins

        if total < 1:
            self.error_label = tk.Label(self.window, font="Helvetica 40", text="Недостаточно данных")
            self.error_label.pack(pady=100)
        else:
            plt.rcParams['text.color'] = 'blue'
            self.fig = Figure(figsize=(12, 6), dpi=80)
            self.fig.subplots_adjust(wspace=0.5)

            self.fig.patch.set_facecolor(bg_color)

            self.circle_diagram = self.fig.add_subplot(1, 2, 1)
            self.bar_diagram = self.fig.add_subplot(1, 2, 2)

            labels = ['Белки', 'Жиры', 'Углеводы']
            sizes = [(total_proteins / total) * 100, (total_fats / total) * 100, (total_carbohydrates / total) * 100]
            colors = ['white', 'gold', 'yellowgreen']
            self.circle_diagram.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=False,
                                    startangle=140)
            self.circle_diagram.axis("equal")

            water_percentage = (total_water / (water_cap * (end_i - start_i))) * 100
            calories_percentage = (total_calories / (calorie_cap * (end_i - start_i))) * 100
            water_cap_percentage = 100
            calories_cap_percentage = 100
            bar_labels = ['Вода', 'Вода норма', 'Калории', 'Калории норма']
            bar_sizes = [water_percentage, water_cap_percentage, calories_percentage, calories_cap_percentage]
            base_values = [min(value, 100) for value in bar_sizes]
            self.bar_diagram.barh(bar_labels, base_values, color=['lightblue', 'blue', 'yellowgreen', 'green'],
                                  edgecolor='black')
            excess_values = [max(0, value - 100) for value in bar_sizes]
            self.bar_diagram.barh(bar_labels, excess_values, left=base_values, color='red', edgecolor='black')
            self.bar_diagram.set_xlabel('Процент')
            self.bar_diagram.set_title('Сравнение потребления воды и калорий в процентах')
            canvas = FigureCanvasTkAgg(self.fig, master=self.window)
            canvas.draw()
            canvas.get_tk_widget().place(x=1, y=1)

    def on_close(self):
        self.destroy()

    def initialize(self):
        self.config(bg=bg_color)
        self.mainloop()


if not os.path.exists("user.txt"):
    reg = RegistrationWindow()
    reg.initialize()
main = MainWindow()
main.initialize()
with open("days.json", "w") as file:
    json.dump(days, file, indent=4)
