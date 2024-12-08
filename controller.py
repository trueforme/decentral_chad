import re
import threading
from view import DatabaseView
from model import UserDatabase
from window import ChatWindow

class DatabaseController:
    def __init__(self, root, client, nickname):
        self.root = root
        self.client = client
        self.nickname = nickname
        self.model = UserDatabase()
        self.view = DatabaseView(root)

        # Отображаем инфо о текущем пользователе (хост)
        self.view.set_nickname_info(self.nickname, self.client.ip, self.client.port)

        self.update_view()

        # Привязываем действия
        self.view.add_user_button.config(command=self.on_add_user_clicked)
        self.view.change_nickname_button.config(command=self.on_change_nickname)

        self.context_menu = self.view.create_context_menu(
            on_connect=self.connect_to_user,
            on_delete=self.delete_selected_record,
            on_refresh=self.update_view
        )
        self.view.bind_tree_context_menu(self.context_menu)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Словарь для хранения открытых чатов
        self.chat_windows = {}

        # Запускаем периодический опрос событий (новые подключения, сообщения)
        self.poll_events()

    def on_close(self):
        self.model.close()
        # Закрываем все соединения клиента
        self.client.close_connection()
        self.root.destroy()

    def on_add_user_clicked(self):
        self.view.prompt_add_user(self.add_user, self.cancel_add_user)

    def add_user(self, user_nickname, ip, port, window):
        if user_nickname and ip and port:
            if self.validate_ipv4(ip):
                self.model.add_record(user_nickname, ip, port)
                window.destroy()
                self.update_view()
            else:
                self.view.show_error("несуществующий ip", parent=window)
        else:
            self.view.show_error("Заполните все поля", parent=window)

    def cancel_add_user(self, window):
        window.destroy()

    def update_view(self):
        records = self.model.get_all_records()
        self.view.show_records(records)

    def connect_to_user(self):
        record = self.view.get_selected_record()
        if not record:
            return
        nickname, ip, port = record
        try:
            if self.client.connect(ip, int(port)):
                # Получаем сокет подключенного клиента
                socket = self.client.clients_socket[self.client.get_ind_by_ip(ip)]
                self.open_chat_window(ip, socket)
            else:
                self.view.show_error("Не удалось подключиться")
        except TimeoutError:
            self.view.show_error('не удалось подключиться')
        except ConnectionRefusedError:
            self.view.show_error('ошибка подключения')

    def delete_selected_record(self):
        record = self.view.get_selected_record()
        if record:
            nickname, ip, port = record
            self.model.delete_record(nickname)
            self.update_view()

    def on_change_nickname(self):
        new_nick = self.view.prompt_nickname()
        if new_nick:
            self.set_nickname(new_nick)
            self.view.set_nickname_info(self.nickname, self.client.ip, self.client.port)

    def set_nickname(self, new_nickname):
        self.nickname = new_nickname
        self.client.nickname = new_nickname
        with open("nick.txt", "w") as f:
            f.write(new_nickname)

    @staticmethod
    def validate_ipv4(ip):
        ipv4_pattern = r'\b([0-9]{1,3}\.){3}[0-9]{1,3}\b'
        if re.match(ipv4_pattern, ip):
            parts = ip.split('.')
            return all(0 <= int(p) <= 255 for p in parts)
        return False

    def open_chat_window(self, ip, socket):
        # Если чат уже открыт, обновляем сокет отправителя
        if ip in self.chat_windows:
            self.chat_windows[ip].update_sender(socket)
        else:
            chat_window = ChatWindow(self.root, socket, self.client.clients_nick[ip])
            self.chat_windows[ip] = chat_window

    def poll_events(self):
        # Проверяем новые входящие подключения
        if len(self.client.connected):
            ip, socket = self.client.connected.pop(0)
            self.open_chat_window(ip[0], socket)

        # Обрабатываем входящие сообщения и закрытие чатов
        for ip, chat_window in list(self.chat_windows.items()):
            # Показываем все новые сообщения
            while len(chat_window.sender.recived_msgs):
                msg = chat_window.sender.recived_msgs.pop(0)
                chat_window.display_text(msg, chat_window.nickname)

            # Если чат завершен с той стороны
            if chat_window.sender.non_active:
                chat_window.display_exit_text()
                chat_window.main_frame.destroy()
                self.client.delete_client(ip)
                del self.chat_windows[ip]

        # Запускаем следующий опрос через 100 мс
        self.root.after(100, self.poll_events)
