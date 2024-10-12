import socket


class Client:
    def __init__(self, nick, port, max_clients=5):
        self.nickname = nick
        self.max_clients = max_clients
        self.clients_ip = ["" for i in range(self.max_clients)]
        self.clients_socket = [socket.socket() for i in range(self.max_clients)]
        for sock in self.clients_socket:
            sock.settimeout(1)
        self.clients_nick = {}
        self.host_socket = socket.socket()
        self.host_socket.bind((socket.gethostbyname(socket.gethostname()), port))
        self.ip, self.port = self.host_socket.getsockname()
        self.host_socket.listen(self.max_clients)
        self.clients_socket_busy = [False for i in range(self.max_clients)]
        self.to_connect = []

    def get_ind_by_ip(self, ip):
        for ind in range(self.max_clients):
            if self.clients_ip[ind] == ip:
                return ind

    def get_free_socket_index(self):
        index = -1
        for is_busy in self.clients_socket_busy:
            index += 1
            if not is_busy:
                return index
        return None

    def connect(self, ip, port):
        if ip in self.clients_ip:
            print("уже подключен")
            return False
        client_index = self.get_free_socket_index()
        if client_index is None:
            print("максимум подключенных")
            return False
        print(client_index, self.clients_ip, port)
        self.clients_socket[client_index].connect((ip, port))
        print("tut")
        self.clients_ip[client_index] = ip
        self.clients_socket_busy[client_index] = True
        self.clients_nick[self.clients_ip[client_index]] = (
            self.clients_socket[client_index].recv(1024).decode()
        )
        self.clients_socket[client_index].send(self.nickname.encode())
        return True

    def accept_connection(self):
        while True:
            try:
                index = self.get_free_socket_index()
                if index is not None:
                    conn, addr = self.host_socket.accept()
                    if addr not in self.clients_ip:
                        self.clients_ip[index] = addr[0]
                        self.clients_socket[index] = conn
                        self.clients_socket_busy[index] = True
                        self.clients_socket[index].send(self.nickname.encode())
                        self.clients_nick[self.clients_ip[index]] = (
                            self.clients_socket[index].recv(1024).decode()
                        )
                        self.to_connect.append((addr, conn))
                    else:
                        print("уже подключен")
            except OSError:
                break

    def close_connection(self):
        self.host_socket.close()
        for socket in self.clients_socket:
            socket.close()

    def delete_client(self, ip):
        ind = self.get_ind_by_ip(ip)
        self.clients_ip[ind] = ""
        self.clients_socket[ind].close()
        self.clients_socket[ind] = socket.socket()
        self.clients_socket_busy[ind] = False
        del self.clients_nick[ip]
