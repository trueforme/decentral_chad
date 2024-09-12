import tkinter
import window as win

root = tkinter.Tk()

main_window = win.DatabaseWindow(root)

while True:
    root.update()
    if len(main_window.client.connected):
            ip, socket = main_window.client.connected.pop(0)
            main_window.open_chat_window(ip, socket)
    for ip, chat_window in main_window.chat_windows.items():
        while len(chat_window.sender.recived_msgs):
            main_window.chat_windows[ip].display_text(chat_window.sender.recived_msgs.pop(0))
        if chat_window.sender.non_active:
            chat_window.display_exit_text(main_window.client.clients_nick[ip])
            del main_window.chat_windows[ip]
            main_window.client.delete_client(ip)