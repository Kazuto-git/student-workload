import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from database import database

class App:
    def __init__(self, root):
        self.root = root
        self.database_file = None
        self.current_table = "workload"
        self.selected_item_id = None

        self.root.title("Распределение нагрузки преподавателей")
        self.root.geometry("1100x650")
        self.root.configure(bg="#ececec")

        # === ВЕРХНЯЯ ПАНЕЛЬ ===
        self.top_frame = tk.Frame(root, bg="#ececec", pady=5)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)

        self.btn_create = tk.Button(self.top_frame, text="Создать базу данных", 
                                    command=self.create_database, width=22)
        self.btn_create.pack(side=tk.LEFT, padx=3)

        self.btn_open = tk.Button(self.top_frame, text="Открыть базу данных", 
                                  command=self.open_database, width=22)
        self.btn_open.pack(side=tk.LEFT, padx=3)

        self.lbl_db_status = tk.Label(self.top_frame, text="База не выбрана", 
                                      bg="white", relief=tk.SUNKEN, width=45, anchor=tk.W)
        self.lbl_db_status.pack(side=tk.RIGHT, padx=5)

        # === ВКЛАДКИ ===
        self.tabs_frame = tk.Frame(root, bg="#ececec", pady=5)
        self.tabs_frame.pack(fill=tk.X, padx=5)

        self.btn_tab_teachers = tk.Button(self.tabs_frame, text="Преподаватели", 
                                          command=lambda: self.switch_table("teachers"), width=22)
        self.btn_tab_teachers.pack(side=tk.LEFT, padx=2)

        self.btn_tab_subjects = tk.Button(self.tabs_frame, text="Предметы", 
                                          command=lambda: self.switch_table("subjects"), width=22)
        self.btn_tab_subjects.pack(side=tk.LEFT, padx=2)

        self.btn_tab_workload = tk.Button(self.tabs_frame, text="Нагрузка", 
                                          command=lambda: self.switch_table("workload"), width=22)
        self.btn_tab_workload.pack(side=tk.LEFT, padx=2)

        # === ТАБЛИЦА ===
        self.table_frame = tk.Frame(root, relief=tk.SUNKEN, borderwidth=2, bg="white")
        self.table_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.table = ttk.Treeview(self.table_frame, show="headings", height=12)
        
        scrollbar_y = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.table.yview)
        scrollbar_x = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, command=self.table.xview)
        self.table.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        # Двойной клик для редактирования
        self.table.bind('<Double-Button-1>', self.on_double_click)

        self.setup_tables_config()
        self.switch_table("workload")

        # === НИЖНЯЯ ПАНЕЛЬ ===
        self.bottom_frame = tk.Frame(root, bg="#ececec", pady=5)
        self.bottom_frame.pack(fill=tk.X, padx=5, pady=5)

        self.btn_add = tk.Button(self.bottom_frame, text="Добавить", 
                                 command=self.add_record, width=15)
        self.btn_add.pack(side=tk.LEFT, padx=5)

        self.btn_edit = tk.Button(self.bottom_frame, text="Изменить", 
                                  command=self.edit_record, width=15)
        self.btn_edit.pack(side=tk.LEFT, padx=5)

        self.btn_refresh = tk.Button(self.bottom_frame, text="Обновить", 
                                     command=self.refresh_table, width=15)
        self.btn_refresh.pack(side=tk.LEFT, padx=5)

        self.btn_delete = tk.Button(self.bottom_frame, text="Удалить", 
                                    command=self.delete_record, width=15)
        self.btn_delete.pack(side=tk.LEFT, padx=5)

    # === СОЗДАНИЕ ЗАГОЛОВКОВ ТАБЛИЦЫ ===
    def setup_tables_config(self):
        self.tables_config = {
            "teachers": {
                "columns": ("id", "surname", "name", "patronymic", "degree", "position", "experience"),
                "headings": ("ID", "Фамилия", "Имя", "Отчество", "Степень", "Должность", "Стаж"),
                "widths": (0, 150, 120, 120, 100, 150, 60)
            },
            "subjects": {
                "columns": ("id", "title", "hours"),
                "headings": ("ID", "Название", "Часы"),
                "widths": (0, 450, 80)
            },
            "workload": {
                "columns": ("id", "teacher", "subject", "group", "degree", "position", "hours"),
                "headings": ("ID", "Преподаватель", "Предмет", "Группа", "Степень", "Должность", "Часы"),
                "widths": (0, 250, 200, 100, 120, 150, 60)
            }
        }

    # === СОЗДАНИЕ ЗАГОЛОВКОВ ТАБЛИЦЫ ===
    def switch_table(self, table_name):
        self.current_table = table_name
        self.selected_item_id = None

        for btn in [self.btn_tab_teachers, self.btn_tab_subjects, self.btn_tab_workload]:
            btn.configure(bg="#d4d0c8", relief=tk.RAISED)

        if table_name == "teachers":
            self.btn_tab_teachers.configure(bg="#a0a0a0", relief=tk.SUNKEN)
        elif table_name == "subjects":
            self.btn_tab_subjects.configure(bg="#a0a0a0", relief=tk.SUNKEN)
        elif table_name == "workload":
            self.btn_tab_workload.configure(bg="#a0a0a0", relief=tk.SUNKEN)

        config = self.tables_config[table_name]
        
        for item in self.table.get_children():
            self.table.delete(item)
        
        self.table["columns"] = ()
        self.table["columns"] = config["columns"]
        self.table["show"] = "headings"

        for col, heading, width in zip(config["columns"], config["headings"], config["widths"]):
            self.table.heading(col, text=heading)
            if width > 0:
                self.table.column(col, width=width, minwidth=50)
            else:
                self.table.column(col, width=0, stretch=False)

        self.refresh_table()

    def on_double_click(self, event):
        self.edit_record()

    def refresh_table(self):
        if not self.database_file:
            return

        for item in self.table.get_children():
            self.table.delete(item)

        if self.current_table == "teachers":
            data = database.get_all_teachers(self.database_file)
        elif self.current_table == "subjects":
            data = database.get_all_subjects(self.database_file)
        elif self.current_table == "workload":
            data = database.get_workload(self.database_file)
        else:
            data = []

        for row in data:
            self.table.insert("", tk.END, values=row, tags=(row[0],))

    def create_database(self):
        self.database_file = filedialog.asksaveasfilename(
            title="Создать базу данных",
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db")],
            initialfile="university.db"
        )
        if self.database_file:
            database.create_database(self.database_file)
            filename = self.database_file.split('/')[-1].split('\\')[-1]
            self.lbl_db_status.configure(text=f"База: {filename}")
            messagebox.showinfo("Успешно", "База данных создана")

    def open_database(self):
        self.database_file = filedialog.askopenfilename(
            title="Открыть базу данных",
            filetypes=[("SQLite Database", "*.db")]
        )
        if self.database_file:
            filename = self.database_file.split('/')[-1].split('\\')[-1]
            self.lbl_db_status.configure(text=f"База: {filename}")
            self.refresh_table()
            messagebox.showinfo("Успешно", "База данных загружена")

    def add_record(self):
        if not self.database_file:
            messagebox.showwarning("Внимание", "Сначала откройте базу данных!")
            return

        if self.current_table == "teachers":
            self.add_teacher()
        elif self.current_table == "subjects":
            self.add_subject()
        elif self.current_table == "workload":
            self.add_workload()

    def edit_record(self):
        if not self.database_file:
            messagebox.showwarning("Внимание", "Сначала откройте базу данных!")
            return

        selection = self.table.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите запись для редактирования!")
            return

        item = self.table.item(selection[0])
        values = item["values"]

        if self.current_table == "teachers":
            self.edit_teacher(values)
        elif self.current_table == "subjects":
            self.edit_subject(values)
        elif self.current_table == "workload":
            self.edit_workload(values)

    def delete_record(self):
        if not self.database_file:
            messagebox.showwarning("Внимание", "Сначала откройте базу данных!")
            return

        selection = self.table.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите запись для удаления!")
            return

        if not messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            return

        for item in selection:
            values = self.table.item(item, "values")
            record_id = values[0]
            
            if self.current_table == "teachers":
                success = database.delete_teacher(self.database_file, record_id)
                if not success:
                    messagebox.showwarning("Внимание", 
                        "Нельзя удалить преподавателя!\nОн есть в распределении нагрузки.\n"
                        "Сначала удалите нагрузку или измените преподавателя в нагрузке.")
                    return
            elif self.current_table == "subjects":
                success = database.delete_subject(self.database_file, record_id)
                if not success:
                    messagebox.showwarning("Внимание", 
                        "Нельзя удалить предмет!\nОн есть в распределении нагрузки.\n"
                        "Сначала удалите нагрузку или измените предмет в нагрузке.")
                    return
            elif self.current_table == "workload":
                database.delete_workload(self.database_file, record_id)

        self.refresh_table()
        messagebox.showinfo("Успешно", "Запись удалена")

    def add_teacher(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить преподавателя")
        dialog.geometry("420x290")
        dialog.resizable(False, False)
        dialog.configure(bg="#ececec")

        fields = {}
        error_labels = {}
    
        labels = [
            ("Фамилия:", "surname", True),
            ("Имя:", "name", True),
            ("Отчество:", "patronymic", False),
            ("Ученая степень:", "degree", True),
            ("Должность:", "position", True),
            ("Стаж (лет):", "experience", True)
        ]

        for text, key, required in labels:
            frame = tk.Frame(dialog, bg="#ececec")
            frame.pack(fill=tk.X, padx=15, pady=3)
        
            tk.Label(frame, text=text, bg="#ececec", width=16, anchor=tk.W).pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=30, relief=tk.SUNKEN, borderwidth=2)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            fields[key] = entry
        
            error_lbl = tk.Label(frame, text="", bg="#ececec", fg="red", 
                                font=("Arial", 8), width=16, anchor=tk.W)
            error_lbl.pack(side=tk.RIGHT, padx=5)
            error_labels[key] = (error_lbl, required)

        def validate():
            valid = True
        
            for key, (error_lbl, required) in error_labels.items():
                value = fields[key].get().strip()
            
                if required and not value:
                    error_lbl.configure(text="Обязательно!")
                    valid = False
                elif key in ["surname", "name", "patronymic", "degree", "position"] and value:
                    # Проверка на цифры
                    if any(char.isdigit() for char in value):
                        error_lbl.configure(text="Только буквы!")
                        valid = False
                    # Проверка минимальной длины
                    elif len(value) < 2:
                        error_lbl.configure(text="Мин. 2 символа!")
                        valid = False
                    else:
                        error_lbl.configure(text="")
                elif key == "experience" and value:
                    try:
                        exp = int(value)
                        if exp < 0 or exp > 100:
                            error_lbl.configure(text="0-100 лет!")
                            valid = False
                        else:
                            error_lbl.configure(text="")
                    except ValueError:
                        error_lbl.configure(text="Только число!")
                        valid = False
                elif not required and not value:
                    error_lbl.configure(text="")
        
            return valid

        def save():
            if not validate():
                return

            database.add_teacher(
                self.database_file,
                fields["surname"].get().strip(),
                fields["name"].get().strip(),
                fields["patronymic"].get().strip(),
                fields["degree"].get().strip(),
                fields["position"].get().strip(),
                int(fields["experience"].get()) if fields["experience"].get().strip() else 0
            )
            dialog.destroy()
            self.refresh_table()
            messagebox.showinfo("Успешно", "Преподаватель добавлен")

        btn_frame = tk.Frame(dialog, bg="#ececec")
        btn_frame.pack(pady=10)
    
        tk.Button(btn_frame, text="Сохранить", command=save, width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=10)

    def edit_teacher(self, values):
        dialog = tk.Toplevel(self.root)
        dialog.title("Изменить преподавателя")
        dialog.geometry("400x260")
        dialog.resizable(False, False)
        dialog.configure(bg="#ececec")

        fields = {}
        error_labels = {}
    
        labels_data = [
            ("Фамилия:", "surname", values[1], True),
            ("Имя:", "name", values[2], True),
            ("Отчество:", "patronymic", values[3], False),
            ("Ученая степень:", "degree", values[4], True),
            ("Должность:", "position", values[5], True),
            ("Стаж (лет):", "experience", str(values[6]), True)
        ]

        for text, key, default_value, required in labels_data:
            frame = tk.Frame(dialog, bg="#ececec")
            frame.pack(fill=tk.X, padx=15, pady=3)
        
            tk.Label(frame, text=text, bg="#ececec", width=16, anchor=tk.W).pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=30, relief=tk.SUNKEN, borderwidth=2)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            entry.insert(0, default_value if default_value else "")
            fields[key] = entry
        
            error_lbl = tk.Label(frame, text="", bg="#ececec", fg="red", 
                                font=("Arial", 8), width=16, anchor=tk.W)
            error_lbl.pack(side=tk.RIGHT, padx=5)
            error_labels[key] = (error_lbl, required)

        def validate():
            valid = True
        
            for key, (error_lbl, required) in error_labels.items():
                value = fields[key].get().strip()
            
                if required and not value:
                    error_lbl.configure(text="Обязательно!")
                    valid = False
                elif key in ["surname", "name", "patronymic", "degree", "position"] and value:
                    if any(char.isdigit() for char in value):
                        error_lbl.configure(text="Только буквы!")
                        valid = False
                    elif len(value) < 2:
                        error_lbl.configure(text="Мин. 2 символа!")
                        valid = False
                    else:
                        error_lbl.configure(text="")
                elif key == "experience" and value:
                    try:
                        exp = int(value)
                        if exp < 0 or exp > 100:
                            error_lbl.configure(text="0-100 лет!")
                            valid = False
                        else:
                            error_lbl.configure(text="")
                    except ValueError:
                        error_lbl.configure(text="Только число!")
                        valid = False
                elif not required and not value:
                    error_lbl.configure(text="")
        
            return valid

        def save():
            if not validate():
                return

            database.update_teacher(
                self.database_file,
                int(values[0]),
                fields["surname"].get().strip(),
                fields["name"].get().strip(),
                fields["patronymic"].get().strip(),
                fields["degree"].get().strip(),
                fields["position"].get().strip(),
                int(fields["experience"].get()) if fields["experience"].get().strip() else 0
            )
            dialog.destroy()
            self.refresh_table()
            messagebox.showinfo("Успешно", "Преподаватель изменен")

        btn_frame = tk.Frame(dialog, bg="#ececec")
        btn_frame.pack(pady=10)
    
        tk.Button(btn_frame, text="Сохранить", command=save, width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=10)

    def add_subject(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить предмет")
        dialog.geometry("420x240")
        dialog.resizable(False, False)
        dialog.configure(bg="#ececec")

        tk.Label(dialog, text="Название предмета:", bg="#ececec").pack(anchor=tk.W, padx=15, pady=(15,3))
        title_entry = tk.Entry(dialog, width=45, relief=tk.SUNKEN, borderwidth=2)
        title_entry.pack(fill=tk.X, padx=15, pady=3)
        title_error = tk.Label(dialog, text="", bg="#ececec", fg="red", font=("Arial", 8))
        title_error.pack(anchor=tk.W, padx=15)

        tk.Label(dialog, text="Количество часов:", bg="#ececec").pack(anchor=tk.W, padx=15, pady=(10,3))
        hours_entry = tk.Entry(dialog, width=15, relief=tk.SUNKEN, borderwidth=2)
        hours_entry.pack(anchor=tk.W, padx=15, pady=3)
        hours_error = tk.Label(dialog, text="", bg="#ececec", fg="red", font=("Arial", 8))
        hours_error.pack(anchor=tk.W, padx=15)

        def validate():
            valid = True
        
            title = title_entry.get().strip()
            if not title:
                title_error.configure(text="Обязательно!")
                valid = False
            elif len(title) < 2:
                title_error.configure(text="Мин. 2 символа!")
                valid = False
            elif len(title) > 70:
                title_error.configure(text="Макс. 70 символов!")
                valid = False
            else:
                title_error.configure(text="")
        
            hours_text = hours_entry.get().strip()
            if not hours_text:
                hours_error.configure(text="Обязательно!")
                valid = False
            else:
                try:
                    hours = int(hours_text)
                    if hours <= 0 or hours > 1000:
                        hours_error.configure(text="1-1000!")
                        valid = False
                    else:
                        hours_error.configure(text="")
                except ValueError:
                    hours_error.configure(text="Только число!")
                    valid = False
        
            return valid

        def save():
            if not validate():
                return

            database.add_subject(self.database_file, title_entry.get().strip(), int(hours_entry.get()))
            dialog.destroy()
            self.refresh_table()
            messagebox.showinfo("Успешно", "Предмет добавлен")

        btn_frame = tk.Frame(dialog, bg="#ececec")
        btn_frame.pack(pady=15)
    
        tk.Button(btn_frame, text="Сохранить", command=save, width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=10)

    def edit_subject(self, values):
        dialog = tk.Toplevel(self.root)
        dialog.title("Изменить предмет")
        dialog.geometry("420x240")
        dialog.resizable(False, False)
        dialog.configure(bg="#ececec")

        tk.Label(dialog, text="Название предмета:", bg="#ececec").pack(anchor=tk.W, padx=15, pady=(15,3))
        title_entry = tk.Entry(dialog, width=45, relief=tk.SUNKEN, borderwidth=2)
        title_entry.pack(fill=tk.X, padx=15, pady=3)
        title_entry.insert(0, values[1])
        title_error = tk.Label(dialog, text="", bg="#ececec", fg="red", font=("Arial", 8))
        title_error.pack(anchor=tk.W, padx=15)

        tk.Label(dialog, text="Количество часов:", bg="#ececec").pack(anchor=tk.W, padx=15, pady=(10,3))
        hours_entry = tk.Entry(dialog, width=15, relief=tk.SUNKEN, borderwidth=2)
        hours_entry.pack(anchor=tk.W, padx=15, pady=3)
        hours_entry.insert(0, str(values[2]))
        hours_error = tk.Label(dialog, text="", bg="#ececec", fg="red", font=("Arial", 8))
        hours_error.pack(anchor=tk.W, padx=15)

        def validate():
            valid = True
        
            title = title_entry.get().strip()
            if not title:
                title_error.configure(text="Обязательно!")
                valid = False
            elif len(title) < 2:
                title_error.configure(text="Мин. 2 символа!")
                valid = False
            elif len(title) > 70:
                title_error.configure(text="Макс. 70 символов!")
                valid = False
            else:
                title_error.configure(text="")
        
            hours_text = hours_entry.get().strip()
            if not hours_text:
                hours_error.configure(text="Обязательно!")
                valid = False
            else:
                try:
                    hours = int(hours_text)
                    if hours <= 0 or hours > 1000:
                        hours_error.configure(text="1-1000!")
                        valid = False
                    else:
                        hours_error.configure(text="")
                except ValueError:
                    hours_error.configure(text="Только число!")
                    valid = False
        
            return valid

        def save():
            if not validate():
                return

            database.update_subject(self.database_file, int(values[0]), 
                                   title_entry.get().strip(), int(hours_entry.get()))
            dialog.destroy()
            self.refresh_table()
            messagebox.showinfo("Успешно", "Предмет изменен")

        btn_frame = tk.Frame(dialog, bg="#ececec")
        btn_frame.pack(pady=15)
    
        tk.Button(btn_frame, text="Сохранить", command=save, width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=10)

    def add_workload(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Распределить нагрузку")
        dialog.geometry("450x320")
        dialog.resizable(False, False)
        dialog.configure(bg="#ececec")

        tk.Label(dialog, text="Преподаватель:", bg="#ececec").pack(anchor=tk.W, padx=15, pady=(15,3))
        teacher_combo = ttk.Combobox(dialog, width=43, state="readonly")
        teacher_combo.pack(fill=tk.X, padx=15, pady=3)

        teachers = database.get_all_teachers(self.database_file)
        teacher_map = {f"{t[1]} {t[2]} {t[3]}": t[0] for t in teachers}
        teacher_combo["values"] = list(teacher_map.keys())
        teacher_error = tk.Label(dialog, text="", bg="#ececec", fg="red", font=("Arial", 8))
        teacher_error.pack(anchor=tk.W, padx=15)

        tk.Label(dialog, text="Предмет:", bg="#ececec").pack(anchor=tk.W, padx=15, pady=(10,3))
        subject_combo = ttk.Combobox(dialog, width=43, state="readonly")
        subject_combo.pack(fill=tk.X, padx=15, pady=3)

        subjects = database.get_all_subjects(self.database_file)
        subject_map = {s[1]: s[0] for s in subjects}
        subject_combo["values"] = list(subject_map.keys())
        subject_error = tk.Label(dialog, text="", bg="#ececec", fg="red", font=("Arial", 8))
        subject_error.pack(anchor=tk.W, padx=15)

        tk.Label(dialog, text="Номер группы:", bg="#ececec").pack(anchor=tk.W, padx=15, pady=(10,3))
        group_entry = tk.Entry(dialog, width=20, relief=tk.SUNKEN, borderwidth=2)
        group_entry.pack(anchor=tk.W, padx=15, pady=3)
        group_error = tk.Label(dialog, text="", bg="#ececec", fg="red", font=("Arial", 8))
        group_error.pack(anchor=tk.W, padx=15)

        def validate():
            valid = True
        
            if not teacher_combo.get():
                teacher_error.configure(text="Выберите!")
                valid = False
            else:
                teacher_error.configure(text="")
        
            if not subject_combo.get():
                subject_error.configure(text="Выберите!")
                valid = False
            else:
                subject_error.configure(text="")
        
            if not group_entry.get().strip():
                group_error.configure(text="Обязательно!")
                valid = False
            else:
                group_error.configure(text="")
        
            return valid

        def save():
            if not validate():
                return

            teacher_id = teacher_map.get(teacher_combo.get())
            subject_id = subject_map.get(subject_combo.get())

            database.add_workload(self.database_file, teacher_id, subject_id, group_entry.get().strip())
            dialog.destroy()
            self.refresh_table()
            messagebox.showinfo("Успешно", "Нагрузка распределена")

        btn_frame = tk.Frame(dialog, bg="#ececec")
        btn_frame.pack(pady=15)
    
        tk.Button(btn_frame, text="Распределить", command=save, width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=10)

    def edit_workload(self, values):
        dialog = tk.Toplevel(self.root)

        dialog.title("Изменить нагрузку")
        dialog.geometry("450x320")
        dialog.resizable(False, False)
        dialog.configure(bg="#ececec")

        tk.Label(dialog, text="Преподаватель:", bg="#ececec").pack(anchor=tk.W, padx=15, pady=(15, 3))
        teacher_combo = ttk.Combobox(dialog, width=43, state="readonly")
        teacher_combo.pack(fill=tk.X, padx=15, pady=3)

        teachers = database.get_all_teachers(self.database_file)
        teacher_map = {f"{t[1]} {t[2]} {t[3]}": t[0] for t in teachers}
        teacher_combo["values"] = list(teacher_map.keys())
        teacher_error = tk.Label(dialog, text="", bg="#ececec", fg="red", font=("Arial", 8))
        teacher_error.pack(anchor=tk.W, padx=15)

        tk.Label(dialog, text="Предмет:", bg="#ececec").pack(anchor=tk.W, padx=15, pady=(10, 3))
        subject_combo = ttk.Combobox(dialog, width=43, state="readonly")
        subject_combo.pack(fill=tk.X, padx=15, pady=3)

        subjects = database.get_all_subjects(self.database_file)
        subject_map = {s[1]: s[0] for s in subjects}
        subject_combo["values"] = list(subject_map.keys())
        subject_error = tk.Label(dialog, text="", bg="#ececec", fg="red", font=("Arial", 8))
        subject_error.pack(anchor=tk.W, padx=15)

        tk.Label(dialog, text="Номер группы:", bg="#ececec").pack(anchor=tk.W, padx=15, pady=(10, 3))
        group_entry = tk.Entry(dialog, width=20, relief=tk.SUNKEN, borderwidth=2)
        group_entry.pack(anchor=tk.W, padx=15, pady=3)
        group_entry.insert(0, values[3])  # ← Предзаполняем группу
        group_error = tk.Label(dialog, text="", bg="#ececec", fg="red", font=("Arial", 8))
        group_error.pack(anchor=tk.W, padx=15)

        # ← Предзаполняем выбранные значения
        current_teacher = values[1]  # ФИО из таблицы
        current_subject = values[2]  # Название предмета из таблицы

        if current_teacher in teacher_map:
            teacher_combo.set(current_teacher)
        if current_subject in subject_map:
            subject_combo.set(current_subject)

        def validate():
            valid = True

            if not teacher_combo.get():
                teacher_error.configure(text="Выберите!")
                valid = False
            else:
                teacher_error.configure(text="")

            if not subject_combo.get():
                subject_error.configure(text="Выберите!")
                valid = False
            else:
                subject_error.configure(text="")

            if not group_entry.get().strip():
                group_error.configure(text="Обязательно!")
                valid = False
            else:
                group_error.configure(text="")

            return valid

        def save():
            if not validate():
                return

            teacher_id = teacher_map.get(teacher_combo.get())
            subject_id = subject_map.get(subject_combo.get())

            database.update_workload(
                self.database_file,
                int(values[0]),  # ID нагрузки
                teacher_id,
                subject_id,
                group_entry.get().strip()
            )
            dialog.destroy()
            self.refresh_table()
            messagebox.showinfo("Успешно", "Нагрузка изменена")

        btn_frame = tk.Frame(dialog, bg="#ececec")
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Сохранить", command=save, width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()