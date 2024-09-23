import tkinter
import window as win

try:
    with open("nick.txt", "r") as f:
        win.nickname = f.readline()
except FileNotFoundError:
    root = tkinter.Tk()
    win.WelcomeWindow(root)
    root.mainloop()

root = tkinter.Tk()
main_window = win.DatabaseWindow(root)

while main_window.running:
    root.update()
    if len(main_window.client.connected):
            ip, socket = main_window.client.connected.pop(0)
            main_window.open_chat_window(ip[0], socket)
    for ip, chat_window in main_window.chat_windows.items():
        while len(chat_window.sender.recived_msgs):
            chat_window.display_text(chat_window.sender.recived_msgs.pop(0),chat_window.nickname)
        if chat_window.sender.non_active:
            chat_window.display_exit_text()
            chat_window.main_frame.destroy()
            main_window.client.delete_client(ip)
            del main_window.chat_windows[ip]
            break
main_window.client.close_connection()