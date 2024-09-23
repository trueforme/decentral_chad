import socket
import threading
class Client():
    def __init__(self, nick, max_clients=5):
        self.nickname = nick
        self.max_clients = max_clients
        self.clients_ip = ['' for i in range(self.max_clients)]
        self.clients_socket = [socket.socket() for i in range(self.max_clients)]
        for sock in self.clients_socket:
            sock.settimeout(1)
        self.clients_nick = {}
        self.host_socket = socket.socket()
        self.host_socket.bind((socket.gethostbyname(socket.gethostname()),20201))
        print(self.host_socket)
        self.ip, self.port = self.host_socket.getsockname()
        self.host_socket.listen(self.max_clients)
        self.clients_socket_busy = [False for i in range(self.max_clients)]
        self.connected = []

    def get_ind_by_ip(self,ip):
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

    def connect(self,ip, port):
        if ip in self.clients_ip:
            print('уже подключен')
            return False
        client_index = self.get_free_socket_index()
        if client_index is None:
            print('максимум подключенных')
            return False
        print(client_index,self.clients_ip,port)
        self.clients_socket[client_index].connect((ip, port))
        print('tut')
        self.clients_ip[client_index] = ip
        self.clients_socket_busy[client_index] = True
        self.clients_nick[self.clients_ip[client_index]] = self.clients_socket[client_index].recv(1024).decode()
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
                        self.clients_nick[self.clients_ip[index]] = self.clients_socket[index].recv(1024).decode()
                        self.connected.append((addr,conn))
                    else:
                        print('уже подключен')
            except OSError:
                None
    def close_connection(self):
        self.host_socket.close()
        for socket in self.clients_socket:
                socket.close()

    def delete_client(self,ip):
        ind = self.get_ind_by_ip(ip)
        self.clients_ip[ind] = ''
        self.clients_socket[ind].close()
        self.clients_socket[ind] = socket.socket()
        self.clients_socket_busy[ind] = False
        del self.clients_nick[ip]

class Sender():
    def __init__(self,socket):
        self.socket = socket
        self.receiver = threading.Thread(target=self.get_bytes)
        self.receiver.start()
        self.recived_msgs = []
        self.non_active = False
    def send_msg(self,msg):
        try:
            self.socket.sendall(msg.encode('utf-8'))
        except ConnectionResetError:
            self.non_active = True
        except OSError:
            None

    def get_msg(self,msg):
        self.recived_msgs.append(msg)
    def send_file(self,file_path):
        try:
            file_name = file_path.split('/')[-1]
            self.socket.send(file_name.encode('utf-16'))
            with open(file_path,'rb') as file:
                self.socket.sendall(file.read())
        except ConnectionResetError:
            self.non_active = True
        except OSError:
            None
    def get_file(self,file_name):
        file = self.socket.recv(1024*8*1024)
        with open(file_name,'wb') as f:
            f.write(file)
    def get_bytes(self):
        while True:
            try:
                data = self.socket.recv(1024*1024*8)
                try:
                    decoded_data = data.decode('utf-8')
                    self.get_msg(decoded_data)
                except UnicodeDecodeError:
                    decoded_data = data.decode('utf-16')
                    self.get_file(decoded_data)
            except ConnectionResetError:
                self.non_active = True
            except OSError or TimeoutError:
                None