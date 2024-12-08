import tkinter
import sys
import window as win
import client
from controller import DatabaseController

default_port = 20204
port = default_port
args = sys.argv[1:]
if len(args) == 1 and args[0].isdigit():
    port = int(args[0])
elif len(args) == 2 and args[0] in ["--port", "-p"] and args[1].isdigit():
    port = int(args[1])

try:
    with open("nick.txt", "r") as f:
        win.nickname = f.readline().strip()
except FileNotFoundError:
    root = tkinter.Tk()
    win.WelcomeWindow(root)
    root.mainloop()

root = tkinter.Tk()
# Создаем клиент:
app_client = client.Client(win.nickname, port=port)
checker = client.threading.Thread(target=app_client.accept_connection)
checker.start()

# Передаем client и nickname в контроллер
db_controller = DatabaseController(root, app_client, win.nickname)
root.mainloop()
# Далее вы можете реализовать логику обновления чата,
# аналогично тому, что у вас было (chat_windows, и т.д.)
# Для полной MVC может потребоваться рефакторинг и их классов
# Но основной принцип декомпозиции уже продемонстрирован
