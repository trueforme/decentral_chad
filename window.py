import tkinter as tk
from tkinter import ttk
import sqlite3
import threading

# Функция для добавления текста в текстовую область (Chat Window)
def add_text_to_window(text):
    text_area.config(state=tk.NORMAL)  # Включаем редактирование, чтобы добавить текст
    text_area.insert(tk.END, text + '\n')
    text_area.see(tk.END)  # Автоматически прокручивать текстовую область вниз
    text_area.config(state=tk.DISABLED)  # Снова отключаем редактирование

# Функция для обновления текстовой области в графическом интерфейсе (Chat Window)
def update_text_area(text):
    add_text_to_window(text)

# Функция для обработки нажатия кнопки "Отправить"
def send_text():
    user_text = input_entry.get().strip()
    if user_text:
        update_text_area(user_text)
        input_entry.delete(0, tk.END)

# Функция для открытия окна с базой данных (Database Window)
def open_database_window():
    # Создаем новое окно для базы данных
    db_window = tk.Toplevel(root)
    db_window.title("Database Window")

    # Создаем или подключаемся к базе данных
    conn = sqlite3.connect('simple_database.db')
    cursor = conn.cursor()

    # Создаем таблицу, если она еще не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            nickname TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Функция для добавления записи в базу данных
    def add_record(nickname, value):
        cursor.execute('''
            INSERT OR REPLACE INTO users (nickname, value)
            VALUES (?, ?)
        ''', (nickname, value))
        conn.commit()
        update_treeview()

    # Функция для получения всех записей из базы данных
    def get_all_records():
        cursor.execute('SELECT * FROM users')
        return cursor.fetchall()

    # Функция для обновления отображения данных в Treeview
    def update_treeview():
        for row in tree.get_children():
            tree.delete(row)
        for row in get_all_records():
            tree.insert('', tk.END, values=row)

    # Функция для обработки нажатия кнопки Add User
    def on_add_user():
        nickname = nickname_entry.get().strip()
        value = value_entry.get().strip()
        if nickname and value:
            add_record(nickname, value)
            nickname_entry.delete(0, tk.END)
            value_entry.delete(0, tk.END)

    # Настройка сетки в окне базы данных
    db_window.columnconfigure(0, weight=1)
    db_window.rowconfigure(0, weight=1)
    db_window.rowconfigure(1, weight=0)

    # Создаем дерево (Treeview) для отображения данных
    columns = ("nickname", "value")
    tree = ttk.Treeview(db_window, columns=columns, show="headings")
    tree.heading("nickname", text="Nickname")
    tree.heading("value", text="Value")
    tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Создаем фрейм для ввода данных и кнопки
    input_frame = tk.Frame(db_window)
    input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    # Настраиваем динамическое изменение размера колонок
    input_frame.columnconfigure(0, weight=1)
    input_frame.columnconfigure(1, weight=1)
    input_frame.columnconfigure(2, weight=0)

    # Поле ввода для никнейма
    tk.Label(input_frame, text="Nickname:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    nickname_entry = tk.Entry(input_frame)
    nickname_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # Поле ввода для значения
    tk.Label(input_frame, text="Value:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    value_entry = tk.Entry(input_frame)
    value_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # Кнопка для добавления пользователя
    add_user_button = tk.Button(input_frame, text="Add User", command=on_add_user)
    add_user_button.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="ns")

    # Кнопка для обновления данных
    refresh_button = tk.Button(db_window, text="Refresh Data", command=update_treeview)
    refresh_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    # Заполнение дерева начальными данными
    update_treeview()

    # Закрываем соединение при закрытии окна
    db_window.protocol("WM_DELETE_WINDOW", lambda: conn.close() or db_window.destroy())


# Создаем основное окно
root = tk.Tk()
root.title("Chat Window")
root.resizable(False, True)

# Настраиваем основную рамку
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Создаем текстовую область для Chat Window
text_area = tk.Text(main_frame, wrap=tk.WORD, height=15, width=50)
text_area.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# Отключаем возможность редактирования текста в текстовой области
text_area.config(state=tk.DISABLED)

# Создаем фрейм для ввода текста и кнопки отправки
input_frame = tk.Frame(main_frame)
input_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

# Поле для ввода текста
input_entry = tk.Entry(input_frame, width=40)
input_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

# Кнопка для отправки текста
send_button = tk.Button(input_frame, text="Отправить", command=send_text)
send_button.grid(row=0, column=1, padx=5, pady=5)

# Кнопка для открытия Database Window
open_db_button = tk.Button(main_frame, text="Открыть Database Window", command=open_database_window)
open_db_button.grid(row=1, column=1, padx=5, pady=5, sticky="se")

# Настройка динамического изменения размеров колонок и строк
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=0)
main_frame.rowconfigure(0, weight=1)

# Запуск потока для приема данных из консоли (Chat Window)


# Запуск основного цикла обработки событий
root.mainloop()
