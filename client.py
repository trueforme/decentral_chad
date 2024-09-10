import socket
import threading
class Client():
    def __init__(self, max_clients=5):

        self.max_clients = max_clients
        self.clients_ip = ['' for i in range(self.max_clients)]
        self.clients_socket = [socket.socket() for i in range(self.max_clients)]
        self.threads = [threading.Thread() for i in range(self.max_clients)]
        self.clients_nick = {}
        self.host_socket = socket.socket()
        self.host_socket.bind((socket.gethostbyname(socket.gethostname()),0))
        self.port = self.host_socket.getsockname()[1]
        self.host_socket.listen(self.max_clients)
        self.clients_socket_busy = [False for i in range(self.max_clients)]

    def get_free_socket_index(self):
        index = -1
        for is_busy in self.clients_socket_busy:
            index += 1
            if not is_busy:
                return index
        return None

    def connect(self,ip, port):
        if ip in self.clients_ip:
            print('уже подключен')
            return
        client_index = self.get_free_socket_index()
        if client_index is None:
            print('максимум подключенных')
            return
        self.clients_ip[client_index] = ip
        print(client_index,self.clients_ip,port)
        self.clients_socket[client_index].connect((self.clients_ip[client_index], port))
        self.clients_socket_busy[client_index] = True
        self.clients_nick[self.clients_ip[client_index]] = self.clients_socket[client_index].recv(1024).decode()
        self.clients_socket[client_index].send(self.nickname.encode())

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
            else:
                break

    def thread_on_recv_msg(self,ind):
        self.threads[ind] = threading.Thread(target=self.get_bytes(),args=[ind])
        self.threads[ind].start()
    def delete_client(self,ind):
        self.clients_ip[ind] = ''
        self.threads[ind] = threading.Thread()
        self.clients_socket[ind].close()
        self.clients_socket[ind] = socket.socket()
        self.clients_socket_busy[ind] = False

    def send_msg(self,msg,ind):
        try:
            self.clients_socket[ind].sendall(msg.encode('utf-8'))
        except ConnectionResetError:
            self.delete_client(ind)
    def get_msg(self,msg,ind):
        with open(f'{self.clients_ip[ind]}.txt','a+') as f:
            f.write(f'{self.clients_nick[self.clients_ip[ind]]}:{msg}')
    def send_file(self,file_path,ind):
        try:
            file_name = file_path.split('\\')[-1]
            self.clients_socket[ind].send(file_name.encode('utf-16'))
            with open(file_path,'rb') as file:
                self.clients_socket[ind].sendall(file.read())
        except ConnectionResetError:
            self.delete_client(ind)
    def get_file(self,file_name,ind):
        file = self.clients_socket[ind].recv(64*8*1024)
        with open(file_name,'wb') as f:
            f.write(file)
    def get_bytes(self,ind):
        while True:
            data = self.clients_socket[ind].recv(64*1024*8)
            try:
                decoded_data = data.decode('utf-8')
                self.get_msg(decoded_data,ind)
            except UnicodeDecodeError:
                decoded_data = data.decode('utf-16')
                self.get_file(decoded_data,ind)