@staticmethod
def update_workload(file_path, workload_id, teacher_id, subject_id, group_number):
    """Обновляет запись о нагрузке"""
    conn = sq.connect(file_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE workload 
        SET teacher_id=?, subject_id=?, group_number=?
        WHERE id=?
    """, (teacher_id, subject_id, group_number, workload_id))
    conn.commit()
    conn.close()

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
        self.edit_workload(values)  # ← Изменено
        с messagebox на вызов функции

        def edit_workload(self, values):
    dialog = tk.Toplevel(self.root)
    dialog.title("Изменить нагрузку")
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
