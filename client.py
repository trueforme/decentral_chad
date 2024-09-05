import socket
import json
import threading
class Client():
    def __init__(self, port,nickname, max_clients=1):
        self.port = int(port)
        self.max_clients = max_clients
        self.nickname = nickname
        self.clients_ip = ['' for i in range(self.max_clients)]
        self.clients_socket = [socket.socket() for i in range(self.max_clients)]
        self.threds = [threading.Thread() for i in range(self.max_clients)]
        print(self.clients_socket[0])
        self.clients_nick = {}
        self.host_socket = socket.socket()
        self.host_socket.bind(('192.168.0.102',self.port))
        print(self.host_socket)
        self.host_socket.listen(self.max_clients)
        self.clients_socket_busy = [False for i in range(self.max_clients)]
        # self.fill_client_data()

    def get_free_socket_index(self):
        index = -1
        for is_busy in self.clients_socket_busy:
            index += 1
            if not is_busy:
                return index
        return None

    def start_session(self,ip, port):
        if ip in self.clients_ip:
            print('уже подключен')
            return
        client_index = self.get_free_socket_index()
        if client_index is None:
            print('error1')
        self.clients_ip[client_index] = ip
        print('there')
        self.connect(client_index, port)
        print("sesion started")


    def connect(self,client_index, port):
        # try:
            print(client_index,self.clients_ip,port)
            self.clients_socket[client_index].connect((self.clients_ip[client_index], port))
            self.clients_socket_busy[client_index] = True
            self.clients_nick[self.clients_ip[client_index]] = self.clients_socket[client_index].recv(1024).decode()
            self.clients_socket[client_index].send(self.nickname.encode())

            return True
        # except:
        #     return False

    def accept_connection(self):
        while True:
            index = self.get_free_socket_index()
            if index is not None:
                conn, addr = self.host_socket.accept()
                if addr not in self.clients_ip:
                    self.clients_ip[index] = addr
                    self.clients_socket[index] = conn
                    self.clients_socket_busy[index] = True
                    self.clients_socket[index].send(self.nickname.encode())
                    self.clients_nick[self.clients_ip[index]] = self.clients_socket[index].recv(1024).decode()
                else:
                    print('уже подключен')


    def send_msgH(self,msg,ind):
        self.clients_socket[ind].send(msg.encode())
        with open(f'{self.clients_ip[ind]}.txt','a+') as f:
            f.write(f'{self.nickname}:{msg}\n')
    def get_msgH(self,ind):
        while True:
            msg = self.clients_socket[ind].recv(1024).decode()
            with open(f'{self.clients_ip[ind]}.txt','a+') as f:
                f.write(f'{self.clients_nick[self.clients_ip[ind]]}:{msg}')
