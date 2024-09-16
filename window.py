import threading
import tkinter as tk
from tkinter import ttk, simpledialog, font, filedialog
import sqlite3
import client
import time
nickname = ''


# Класс для Database Window
class DatabaseWindow:
    def __init__(self, root):
        self.running = True
        self.root = root
        self.conn = sqlite3.connect('nick_ip_port.db')
        self.cursor = self.conn.cursor()
        self.nickname = nickname
        self.client = client.Client(nickname)
        self.checker = threading.Thread(target=self.client.accept_connection)
        self.checker.start()
        self.chat_windows = {}

        # Создаем новое окно для базы данных
        self.db_frame = tk.Frame(self.root)
        self.db_frame.pack(fill=tk.BOTH, expand=True)

        # Создаем таблицу с полями nickname, ip и port
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                nickname TEXT PRIMARY KEY,
                ip TEXT,
                port TEXT
            )
        ''')

        # Создаем дерево (Treeview) для отображения данных
        self.columns = ("nickname", "value", "another_value")
        self.tree = ttk.Treeview(self.db_frame, columns=self.columns,
                                 show="headings")
        self.tree.column("another_value", width=75)
        self.tree.column("value", width=100)
        self.tree.column("nickname", width=150)
        self.tree.heading("nickname", text="Nickname", anchor='w')
        self.tree.heading("value", text="ip", anchor='w')
        self.tree.heading("another_value", text="port", anchor='w')
        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tree.tag_configure('evenrow', background='lightgrey')
        self.tree.tag_configure('oddrow', background='white')

        # Создаем контекстное меню
        self.context_menu = tk.Menu(self.db_frame, tearoff=0)
        self.context_menu.add_command(label="Connect",
                                      command=self.connect_to_user)
        self.context_menu.add_command(label="Delete",
                                      command=self.delete_selected_record)

        # Привязываем правый клик мыши к функции открытия контекстного меню
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Настройка сетки в окне базы данных
        self.db_frame.columnconfigure(0, weight=1)
        self.db_frame.rowconfigure(0, weight=1)
        self.db_frame.rowconfigure(1, weight=0)

        # Создаем фрейм для ввода данных и кнопки
        self.input_frame = tk.Frame(self.db_frame)
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Поле для отображения никнейма
        self.nickname_label = tk.Label(self.input_frame,
                                       text=f"Ваш ник: {self.nickname}")
        self.nickname_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # Настраиваем динамическое изменение размера колонок
        self.input_frame.columnconfigure(0, weight=1)
        self.input_frame.columnconfigure(1, weight=1)
        self.input_frame.columnconfigure(2, weight=0)

        # Кнопка для добавления пользователя
        self.refresh_button = tk.Button(self.db_frame, text="Add user",
                                        command=self.on_add_user, width=10)
        self.refresh_button.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        # Кнопка для обновления данных
        self.refresh_button = tk.Button(self.db_frame, text="Refresh Data",
                                        command=self.update_treeview, width=10)
        self.refresh_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Кнопка для изменения никнейма, расположенная близко к метке
        self.change_nickname_button = tk.Button(self.input_frame,
                                                text="Изменить", width=10,
                                                command=self.change_nickname
                                                )
        self.change_nickname_button.grid(row=0, column=2, padx=0, pady=0,
                                         sticky="e")

        # Заполнение дерева начальными данными
        self.update_treeview()

        # Закрываем соединение при закрытии окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # Функция для добавления записи в базу данных (Database Window)
    def add_record(self, nickname, ip, port):
        self.cursor.execute('''
            INSERT OR REPLACE INTO users (nickname, ip,port)
            VALUES (?, ?,? )
        ''', (nickname, ip, port))
        self.conn.commit()
        self.update_treeview()

    # Функция для получения всех записей из базы данных (Database Window)
    def get_all_records(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()

    # Функция для обновления отображения данных в Treeview (Database Window)
    def update_treeview(self):
        global nickname
        for row in self.tree.get_children():
            self.tree.delete(row)
        for index, row in enumerate(self.get_all_records()):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.insert('', tk.END, values=row, tags=(tag,))
        self.nickname_label.config(text=f"Ваш ник: {nickname}")

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

    def open_chat_window(self, ip, socket):
        chat_window = ChatWindow(self.root, socket)
        self.chat_windows[ip] = chat_window

    # Функция для обработки нажатия кнопки Add User (Database Window)
    def on_add_user(self):
        self.open_add_user_window()

        # Функция для открытия окна добавления пользователя

    # это кнопка Connect
    def connect_to_user(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("Новое окно")

        label = tk.Label(new_window, text="ожидание")
        label.pack(padx=20, pady=20)
        try:
            data_coded = self.tree.selection()[0]
            ip = self.tree.item(data_coded, "values")[1]
            port = self.tree.item(data_coded, "values")[2]
            if self.client.connect(ip, int(port)):
                self.open_chat_window(ip, self.client.clients_socket[
                    self.client.get_ind_by_ip(ip)])
            new_window.destroy()
        except TimeoutError:
            label.config(text='не удалось подключиться')
        except:
            label.config(text='неккоректные данные')

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
        add_user_window = tk.Toplevel(self.db_frame)
        add_user_window.title("Add User")

        # Поле для ввода никнейма
        tk.Label(add_user_window, text="Nickname:").grid(row=0, column=0,
                                                         padx=5, pady=5)
        nickname_entry = tk.Entry(add_user_window)
        nickname_entry.grid(row=0, column=1, padx=5, pady=5)

        # Поле для ввода значения
        tk.Label(add_user_window, text="Ip:").grid(row=1, column=0,
                                                   padx=5, pady=5)
        ip_entry = tk.Entry(add_user_window)
        ip_entry.grid(row=1, column=1, padx=5, pady=5)

        # помогите ЛОООООООЛЛЛЛЛЛЛЛЛЛЛЛЛЛЛЛЛЛ
        tk.Label(add_user_window, text="Port").grid(row=2, column=0,
                                                    padx=5, pady=5)
        port_entry = tk.Entry(add_user_window)
        port_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка "OK"
        ok_button = tk.Button(add_user_window, text="OK",
                              command=lambda: self.add_user(
                                  nickname_entry.get(), ip_entry.get(),
                                  port_entry.get(),
                                  add_user_window))
        ok_button.grid(row=3, column=0, padx=5, pady=0)

        # Кнопка "Cancel"
        cancel_button = tk.Button(add_user_window, text="Cancel",
                                  command=add_user_window.destroy)
        cancel_button.grid(row=3, column=1, padx=5, pady=5)

        # Центрирование окна Add User относительно Database Window
        self.center_window(add_user_window, 210, 130)

    # Функция для добавления пользователя
    def add_user(self, nickname, ip, port, window):
        if nickname and ip and port:
            self.add_record(nickname, ip, port)
            window.destroy()

    # Закрытие окна и соединения с базой данных

    def center_window(self, window, width, height):
        # Получаем размеры окна родителя (DatabaseWindow)
        db_frame_width = self.db_frame.winfo_width()
        db_frame_height = self.db_frame.winfo_height()
        db_frame_x = self.db_frame.winfo_x()
        db_frame_y = self.db_frame.winfo_y()

        # Вычисляем координаты для центрирования окна Add User
        pos_x = db_frame_x + (db_frame_width // 2) - (width // 2)
        pos_y = db_frame_y + (db_frame_height // 2) - (height // 2)

        # Задаем размер и положение окна
        window.geometry(f'{width}x{height}+{pos_x}+{pos_y}')
        window.grab_set()  # Фокус на новом окне

    def on_close(self):
        self.conn.close()
        self.root.destroy()
        self.running = False

    def change_nickname(self):
        new_nickname = simpledialog.askstring("", "new nickname:")
        if new_nickname:
            self.set_nickname(new_nickname)
        self.update_treeview()

    def set_nickname(self, new_nickname):
        global nickname
        nickname = new_nickname

    def on_closing(self):
        self.root.destroy()




# Класс для Chat Window
class ChatWindow:
    def __init__(self, root, socket):
        self.root = root
        self.running = True
        self.sender = client.Sender(socket, nickname)
        self.nickname = nickname  # Изначально никнейм не задан
        self.root.resizable(False, True)

        # Настраиваем основную рамку
        self.main_frame = tk.Toplevel(self.root)

        # Создаем текстовую область для Chat Window
        self.text_area = tk.Text(self.main_frame, wrap=tk.WORD, height=15,
                                 width=50)
        self.text_area.grid(row=1, column=0, columnspan=2, padx=5, pady=5,
                            sticky="nsew")
        self.text_area.config(state=tk.DISABLED)

        # Шрифт для текста
        self.bold_font = font.Font(weight="bold", size=9, family='Courier')
        self.text_area.tag_configure("bold", font=self.bold_font)

        # Фрейм для ввода текста и кнопки отправки
        self.input_frame = tk.Frame(self.main_frame)
        self.input_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Поле для ввода текста
        self.input_entry = tk.Entry(self.input_frame, width=40)
        self.input_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Привязка события Enter к текстовому полю
        self.input_entry.bind("<Return>", self.send_text_with_event)

        # Кнопка для отправки текста
        self.send_button = tk.Button(self.input_frame, text="Отправить",
                                     command=self.send_text)
        self.send_button.grid(row=0, column=1, padx=5, pady=5)

        # Кнопка для добавления файла
        self.add_file_button = tk.Button(self.input_frame, text="Add File",
                                         command=self.open_file_dialog)
        self.add_file_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Настройка динамического изменения размеров колонок и строк
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=0)
        self.main_frame.rowconfigure(1, weight=1)

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.sender.send_file(file_path)
            # file_name = file_path.split('/')[-1]  # Получаем имя файла
            # self.display_text(file_name, self.nickname)

    # пишешь епта в строку
    def send_text(self):
        user_input = self.input_entry.get()
        if user_input:
            self.sender.send_msg(user_input)
            self.display_text(user_input, 'YOU')

    # Обработчик, который передает вызов send_text
    def send_text_with_event(self, event):
        self.send_text()

    def display_text(self, text, nickname=''):
        self.text_area.config(state=tk.NORMAL)
        if nickname:
            self.text_area.insert(tk.END,
                                  f"{nickname}: {text}\n")
        else:
            self.text_area.insert(tk.END, f"{text}\n")
        self.text_area.config(state=tk.DISABLED)
        self.input_entry.delete(0, tk.END)

    def display_exit_text(self, nick):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(f'{nick} покинул чат')
        self.text_area.config(state=tk.DISABLED)
        self.input_entry.delete(0, tk.END)

    def receive_messages(self):
        while self.running:
            try:
                # Получаем сообщение от сервера
                message = self.sender.recived_msgs()
                if message:
                    # Используем self.root.after для безопасного обновления интерфейса из потока
                    self.root.after(0, self.display_text, message)
                time.sleep(0.1)
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.running = False
                break


class WelcomeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Welcome Window")

        # Создаем метку с текстом "Здравствуйте!"
        self.label = tk.Label(self.root, text="Здравствуйте!",
                              font=("Arial", 16))
        self.label.pack(pady=20)

        # Поле для ввода текста (никнейм)
        self.nickname_entry = tk.Entry(self.root)
        self.nickname_entry.pack(pady=10)
        self.nickname_entry.bind("<KeyRelease>",
                                 self.check_entry)  # Привязка к событию

        # Кнопка "Здравствуйте", пока не активна
        self.greet_button = tk.Button(self.root, text="Здравствуйте",
                                      state=tk.DISABLED,
                                      command=self.open_chat_window)
        self.greet_button.pack(pady=10)

    # Функция проверки поля ввода
    def check_entry(self, event):
        global nickname
        nickname = self.nickname_entry.get().strip()  # Получаем значение и убираем пробелы
        if nickname:  # Если никнейм не пустой
            self.greet_button.config(state=tk.NORMAL)
        else:
            self.greet_button.config(state=tk.DISABLED)


    # def open_chat_window(self):
    #     self.root.destroy()  # Закрываем окно приветствия
    #     DatabaseWindow(tk.Tk())  # Открываем окно чата
