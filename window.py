import tkinter as tk
from tkinter import ttk, simpledialog, font, filedialog
import sqlite3
import threading


# Класс для Database Window
class DatabaseWindow:
    def __init__(self, root):
        self.root = root
        self.conn = sqlite3.connect('simple_database.db')
        self.cursor = self.conn.cursor()

        # Создаем новое окно для базы данных
        self.db_window = tk.Toplevel(self.root)
        self.db_window.title("Database Window")

        # Создаем таблицу, если она еще не существует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                nickname TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # Создаем дерево (Treeview) для отображения данных
        self.columns = ("nickname", "value")
        self.tree = ttk.Treeview(self.db_window, columns=self.columns,
                                 show="headings")
        self.tree.heading("nickname", text="Nickname")
        self.tree.heading("value", text="Value")
        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Создаем контекстное меню
        self.context_menu = tk.Menu(self.db_window, tearoff=0)
        self.context_menu.add_command(label="Delete",
                                      command=self.delete_selected_record)

        # Привязываем правый клик мыши к функции открытия контекстного меню
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Настройка сетки в окне базы данных
        self.db_window.columnconfigure(0, weight=1)
        self.db_window.rowconfigure(0, weight=1)
        self.db_window.rowconfigure(1, weight=0)


        # Создаем фрейм для ввода данных и кнопки
        self.input_frame = tk.Frame(self.db_window)
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Настраиваем динамическое изменение размера колонок
        self.input_frame.columnconfigure(0, weight=1)
        self.input_frame.columnconfigure(1, weight=1)
        self.input_frame.columnconfigure(2, weight=0)

        # Кнопка для добавления пользователя
        self.add_user_button = tk.Button(self.input_frame, text="Add User",
                                         command=self.on_add_user)
        self.add_user_button.grid(row=0, column=2, rowspan=2, padx=5, pady=5,
                                  sticky="ns")

        # Кнопка для обновления данных
        self.refresh_button = tk.Button(self.db_window, text="Refresh Data",
                                        command=self.update_treeview)
        self.refresh_button.grid(row=2, column=0, padx=10, pady=10,
                                 sticky="ew")

        # Заполнение дерева начальными данными
        self.update_treeview()

        # Закрываем соединение при закрытии окна
        self.db_window.protocol("WM_DELETE_WINDOW", self.on_close)

    # Функция для добавления записи в базу данных (Database Window)
    def add_record(self, nickname, value):
        self.cursor.execute('''
            INSERT OR REPLACE INTO users (nickname, value)
            VALUES (?, ?)
        ''', (nickname, value))
        self.conn.commit()
        self.update_treeview()

    # Функция для получения всех записей из базы данных (Database Window)
    def get_all_records(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()

    # Функция для обновления отображения данных в Treeview (Database Window)
    def update_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in self.get_all_records():
            self.tree.insert('', tk.END, values=row)

    def show_context_menu(self, event):
        # Проверяем, есть ли выделенная строка
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            # Выделяем строку при правом клике
            self.tree.selection_set(selected_item)
            # Показываем контекстное меню
            self.context_menu.post(event.x_root, event.y_root)
        else:
            # Скрываем меню, если клик не по элементу
            self.context_menu.unpost()

    # Функция для обработки нажатия кнопки Add User (Database Window)
    def on_add_user(self):
        self.open_add_user_window()

        # Функция для открытия окна добавления пользователя

    def delete_selected_record(self):
        # Получаем выделенный элемент в Treeview
        selected_item = self.tree.selection()[0]
        if selected_item:
            # Получаем значение nickname из выделенной строки
            values = self.tree.item(selected_item, 'values')
            nickname = values[0]

            # Удаляем запись из базы данных
            self.cursor.execute('DELETE FROM users WHERE nickname = ?',
                                (nickname,))
            self.conn.commit()

            # Удаляем запись из Treeview
            self.tree.delete(selected_item)

    def open_add_user_window(self):
        add_user_window = tk.Toplevel(self.db_window)
        add_user_window.title("Add User")

        # Поле для ввода никнейма
        tk.Label(add_user_window, text="Nickname:").grid(row=0, column=0,
                                                         padx=5, pady=5)
        nickname_entry = tk.Entry(add_user_window)
        nickname_entry.grid(row=0, column=1, padx=5, pady=5)

        # Поле для ввода значения
        tk.Label(add_user_window, text="Value:").grid(row=1, column=0,
                                                      padx=5, pady=5)
        value_entry = tk.Entry(add_user_window)
        value_entry.grid(row=1, column=1, padx=5, pady=5)

        # Кнопка "OK"
        ok_button = tk.Button(add_user_window, text="OK",
                              command=lambda: self.add_user(
                                  nickname_entry.get(), value_entry.get(),
                                  add_user_window))
        ok_button.grid(row=2, column=0, padx=5, pady=5)

        # Кнопка "Cancel"
        cancel_button = tk.Button(add_user_window, text="Cancel",
                                  command=add_user_window.destroy)
        cancel_button.grid(row=2, column=1, padx=5, pady=5)

        # Центрирование окна Add User относительно Database Window
        self.center_window(add_user_window, 210, 100)

    # Функция для добавления пользователя
    def add_user(self, nickname, value, window):
        if nickname and value:
            self.add_record(nickname, value)
            window.destroy()

    # Закрытие окна и соединения с базой данных

    def center_window(self, window, width, height):
        # Получаем размеры окна родителя (DatabaseWindow)
        db_window_width = self.db_window.winfo_width()
        db_window_height = self.db_window.winfo_height()
        db_window_x = self.db_window.winfo_x()
        db_window_y = self.db_window.winfo_y()

        # Вычисляем координаты для центрирования окна Add User
        pos_x = db_window_x + (db_window_width // 2) - (width // 2)
        pos_y = db_window_y + (db_window_height // 2) - (height // 2)

        # Задаем размер и положение окна
        window.geometry(f'{width}x{height}+{pos_x}+{pos_y}')
        window.grab_set()  # Фокус на новом окне

    def on_close(self):
        self.conn.close()
        self.db_window.destroy()


# Класс для Chat Window
class ChatWindow:
    def __init__(self, root):
        self.root = root
        self.nickname = ""  # Изначально никнейм не задан

        # Настраиваем основную рамку
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Создаем текстовую область для Chat Window
        self.text_area = tk.Text(self.main_frame, wrap=tk.WORD, height=15,
                                 width=50)
        self.text_area.grid(row=1, column=0, columnspan=2, padx=5, pady=5,
                            sticky="nsew")
        self.text_area.config(state=tk.DISABLED)

        # Шрифт для текста
        self.bold_font = font.Font(weight="bold", size=9, family='Courier')
        self.text_area.tag_configure("bold", font=self.bold_font)

        # Фрейм для никнейма и кнопки изменения никнейма
        self.nickname_frame = tk.Frame(self.main_frame)
        self.nickname_frame.grid(row=0, column=0, columnspan=2, sticky="e",
                                 padx=5, pady=5)

        # Метка для отображения текущего никнейма
        self.nickname_label = tk.Label(self.nickname_frame,
                                       text="Ваш никнейм: ")
        self.nickname_label.grid(row=0, column=0, sticky="e")

        # Кнопка для изменения никнейма
        self.change_nickname_button = tk.Button(self.nickname_frame,
                                                text="Изменить ник",
                                                command=self.change_nickname)
        self.change_nickname_button.grid(row=0, column=1, sticky="e", padx=5)

        # Фрейм для ввода текста и кнопки отправки
        self.input_frame = tk.Frame(self.main_frame)
        self.input_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Поле для ввода текста
        self.input_entry = tk.Entry(self.input_frame, width=40)
        self.input_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Кнопка для отправки текста
        self.send_button = tk.Button(self.input_frame, text="Отправить",
                                     command=self.send_text)
        self.send_button.grid(row=0, column=1, padx=5, pady=5)

        # Кнопка для открытия Database Window
        self.open_db_button = tk.Button(self.main_frame,
                                        text="Открыть Database Window",
                                        command=self.open_database_window)
        self.open_db_button.grid(row=2, column=1, padx=5, pady=5, sticky="se")

        # Кнопка для добавления файла
        self.add_file_button = tk.Button(self.input_frame, text="Add File",
                                         command=self.open_file_dialog)
        self.add_file_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Настройка динамического изменения размеров колонок и строк
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=0)
        self.main_frame.rowconfigure(1, weight=1)

        # Открытие диалогового окна для выбора файла

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            file_name = file_path.split('/')[-1]  # Получаем имя файла
            self.display_text(file_name, self.nickname)

    def change_nickname(self):
        new_nickname = simpledialog.askstring("", "new nickname:")
        if new_nickname:
            self.nickname = new_nickname.strip()
            self.nickname_label.config(text=f"Ваш никнейм: {self.nickname}")

    def send_text(self):
        user_input = self.input_entry.get()
        if user_input:
            self.display_text(user_input, self.nickname)

    def display_text(self, text, nickname):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END,
                              f"{nickname or 'You'}: {text}\n")
        self.text_area.config(state=tk.DISABLED)
        self.input_entry.delete(0, tk.END)

    def get_text(self):
        pass

    def open_database_window(self):
        DatabaseWindow(self.root)


# Создаем основное окно
root = tk.Tk()
root.title("Chat Window")
root.resizable(False, True)

# Создаем экземпляр окна чата
chat_window = ChatWindow(root)

# Запуск основного цикла обработки событий
root.mainloop()
