import socket
import json


class Client:
    def __init__(self, port, nickname):
        self.socket = socket.socket()
        self.port = port
        self.nickname = nickname
        self.client_data = {}
        self.fill_client_data()

    def fill_client_data(self):
        try:
            f = open('clients_data.txt', 'r')
            for line in f.readlines():
                ip, nick = line.split(': ')
                self.client_data[ip] = nick
            f.close()
        except FileNotFoundError:
            f = open('clients_data.txt', 'w')
            f.close()

    def Host(self, max_clients):
        self.socket.bind(('', self.port))
        self.socket.listen(max_clients)
        conn, addr = self.socket.accept()
        nick = conn.recv(1024)
        self.client_data[addr[0]] = nick.decode()
        self.Update_clients_data()
        data = json.dumps(self.client_data)
        conn.send(data.encode())

    def Connect(self):
        self.socket.connect(('localhost', self.port))
        self.socket.send(self.nickname.encode())
        self.client_data = json.loads(self.socket.recv(1024).decode())
        self.Update_clients_data()

    def Update_clients_data(self):
        lines = []
        for key, val in self.client_data.items():
            lines.append(f'{key}: {val}')
        with open('clients_data.txt', 'w') as f:
            f.writelines(lines)
