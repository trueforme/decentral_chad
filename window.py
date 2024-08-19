import tkinter as tk

# Функция для добавления текста в текстовую область
def add_text_to_window(text):
    text_area.insert(tk.END, text + '\n')
    text_area.see(tk.END)  # Автоматически прокручивать текстовую область вниз

# Создаем основное окно
root = tk.Tk()
root.title("Chat Window")

# Создаем текстовую область
text_area = tk.Text(root, wrap=tk.WORD, height=15, width=50)
text_area.pack(padx=10, pady=10)

# Отключаем возможность редактирования текста в текстовой области
text_area.config(state=tk.DISABLED)

# Функция для приема текста из консоли
def receive_input():
    while True:
        user_input = input("Введите текст: ")
        root.after(0, lambda: update_text_area(user_input))

# Функция для обновления текстовой области в графическом интерфейсе
def update_text_area(text):
    text_area.config(state=tk.NORMAL)  # Включаем редактирование, чтобы добавить текст
    add_text_to_window(text)
    text_area.config(state=tk.DISABLED)  # Снова отключаем редактирование

# Запуск потока для приема данных из консоли
import threading
input_thread = threading.Thread(target=receive_input)
input_thread.daemon = True
input_thread.start()

# Запуск основного цикла обработки событий
root.mainloop()
