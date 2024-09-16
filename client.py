import socket
import threading


class Client():
    def __init__(self, nick, max_clients=5):
        self.Active = True  # Флаг активности клиента
        self.lock = threading.Lock()  # Блокировка для синхронизации доступа
        self.nickname = nick
        self.max_clients = max_clients
        self.clients_ip = ['' for _ in range(self.max_clients)]
        self.clients_socket = [socket.socket() for _ in
                               range(self.max_clients)]
        self.clients_nick = {}
        self.host_socket = socket.socket()
        self.host_socket.settimeout(0.5)
        print(self.host_socket)
        self.host_socket.bind(
            (socket.gethostbyname(socket.gethostname()), 20202))
        self.ip, self.port = self.host_socket.getsockname()
        print(self.ip,self.port)
        self.host_socket.listen(self.max_clients)
        self.clients_socket_busy = [False for _ in range(self.max_clients)]
        self.connected = []

    def connect(self, ip, port):
        # Устанавливаем начальное значение successful_connection

        # Запуск подключения в отдельном потоке
        connection_thread = threading.Thread(target=self._connect_in_thread,
                                             args=(ip, port))
        connection_thread.start()

        # Ожидание завершения подключения
        connection_thread.join()

        # Используем self.successful_connection внутри функции connect
        return self.successful_connection

    def _connect_in_thread(self, ip, port):
        """Функция для подключения, выполняемая в отдельном потоке."""
        with self.lock:  # Защищаем доступ к сокетам
            if ip in self.clients_ip:
                print('уже подключен')
                return
            client_index = self.get_free_socket_index()
            if client_index is None:
                print('максимум подключенных')
                return
            try:
                self.clients_ip[client_index] = ip
                self.clients_socket[client_index].connect((ip, port))
                self.clients_socket_busy[client_index] = True
                print(f'Подключен к {ip}:{port}')
                self.successful_connection = True
            except Exception as e:
                print(f'Ошибка подключения к {ip}:{port} - {e}')
                self.successful_connection = False

    def accept_connection(self):
        """Ожидание подключения клиентов. Можно также выполнять в отдельном потоке."""
        while self.Active:  # Проверка активности
            index = self.get_free_socket_index()
            if index is not None:
                if self.host_socket.fileno() != -1:
                    try:
                        conn, addr = self.host_socket.accept()
                        with self.lock:
                            if addr not in self.clients_ip:
                                self.clients_ip[index] = addr[0]
                                self.clients_socket[index] = conn
                                self.clients_socket_busy[index] = True
                                self.connected.append((addr, conn))
                                print(f'Клиент {addr[0]} подключен.')
                            else:
                                print('уже подключен')
                    except OSError:
                        print('Ошибка при принятии соединения')
                        break
                else:
                    break

    def get_free_socket_index(self):
        """Ищет и возвращает индекс первого свободного сокета."""
        for index, is_busy in enumerate(self.clients_socket_busy):
            if not is_busy:  # Если сокет не занят
                return index  # Возвращаем индекс свободного сокета
        return None  # Если свободных сокетов нет


    def delete_client(self, ip):
        """Удаляет клиента по его IP и закрывает его сокет."""
        with self.lock:
            ind = self.get_ind_by_ip(ip)
            if ind is not None and self.clients_socket[ind].fileno() != -1:
                try:
                    self.clients_socket[ind].close()
                except OSError:
                    pass
            self.clients_ip[ind] = ''
            self.clients_socket[
                ind] = socket.socket()  # Создаем новый сокет на месте старого
            self.clients_socket_busy[ind] = False
            if ip in self.clients_nick:
                del self.clients_nick[ip]

    def get_ind_by_ip(self, ip):
        """Возвращает индекс клиента по его IP-адресу."""
        for ind, client_ip in enumerate(self.clients_ip):
            if client_ip == ip:
                return ind
        return None  # Если клиент не найден

    def close_all_sockets(self):
        """Закрывает все сокеты и завершает работу."""
        self.Active = False  # Флаг для остановки всех потоков
        with self.lock:
            # Закрываем все клиентские сокеты
            for s in self.clients_socket:
                if s.fileno() != -1:
                    try:
                        s.close()
                    except OSError:
                        pass
            # Закрываем хост-сокет
            if self.host_socket.fileno() != -1:
                try:
                    self.host_socket.close()
                except OSError:
                    pass

        # Ждем завершения всех активных потоков
        for conn, _ in self.connected:
            try:
                conn.close()
            except OSError:
                pass


class Sender():
    def __init__(self, socket, my_nick):
        self.my_nick = my_nick
        self.socket = socket
        self.reciver = threading.Thread(target=self.get_bytes)
        self.reciver.daemon = True  # Делаем поток демоном, чтобы он завершался вместе с программой
        self.reciver.start()
        self.recived_msgs = []
        self.non_active = False

    def send_msg(self, msg):
        """Отправка сообщения."""
        try:
            self.socket.sendall((f'{self.my_nick}: ' + msg).encode('utf-8'))
        except (ConnectionResetError, OSError):
            self.non_active = True

    def get_msg(self, msg):
        """Получение сообщения."""
        self.recived_msgs.append(msg)

    def send_file(self, file_path):
        """Отправка файла."""
        try:
            file_name = file_path.split('/')[-1]
            self.socket.send(file_name.encode('utf-16'))
            with open(file_path, 'rb') as file:
                self.socket.sendall(file.read())
        except (ConnectionResetError, OSError):
            self.non_active = True

    def get_file(self, file_name):
        """Получение файла."""
        file = self.socket.recv(1024 * 8 * 1024)
        with open(file_name, 'wb') as f:
            f.write(file)

    def get_bytes(self):
        """Получение данных (сообщений или файлов)."""
        while True:
            try:
                data = self.socket.recv(1024 * 1024 * 8)
                try:
                    decoded_data = data.decode('utf-8')
                    self.get_msg(decoded_data)
                except UnicodeDecodeError:
                    decoded_data = data.decode('utf-16')
                    self.get_file(decoded_data)
            except (ConnectionResetError, OSError):
                self.non_active = True
                break
