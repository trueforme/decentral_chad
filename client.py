import socket
import json
class Client():
    def __init__(self, port,nickname, max_clients=1):
        self.port = int(port)
        self.max_clients = max_clients
        self.nickname = nickname
        self.clients_ip = ['' for i in range(self.max_clients)]
        self.clients_socket = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for i in range(self.max_clients)]
        self.clients_nick = {}
        self.host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_socket.bind(('localhost',self.port))
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

    def start_session(self,ip):
        client_index = self.get_free_socket_index()
        if client_index is None:
            print('error1')
        self.clients_ip[client_index] = ip
        if not self.connect(client_index):
            print('error2')
        conn, addr = self.host_socket.accept()
        print("sesion started")





    def connect(self,client_index):
        try:
            self.clients_socket[client_index].connect((self.clients_ip[client_index], self.port))
            self.clients_socket_busy[client_index] = True
            return True
        except:
            return False




    # def fill_client_data(self):
    #     try:
    #         f = open('clients_data.txt', 'r')
    #         for line in f.readlines():
    #             ip,nick = line.split(': ')
    #             self.clients_nick[ip] = nick
    #         f.close()
    #     except FileNotFoundError:
    #         f = open('clients_data.txt', 'w')
    #         f.close()

    # def Host(self,max_clients):
    #     self.socket.bind(('',self.port))
    #     self.socket.listen(max_clients)
    #     self.conn, self.addr = self.socket.accept()
    #     nick = self.conn.recv(1024)
    #     self.clients_nick[self.addr[0]] = nick.decode()
    #     self.Update_clients_data()
    #     data = json.dumps(self.clients_nick)
    #     self.conn.send(data.encode())
    #
    # def Connect(self):
    #     self.socket.connect(('localhost',self.port))
    #     self.socket.send(self.nickname.encode())
    #     self.clients_nick = json.loads(self.socket.recv(1024).decode())
    #     self.Update_clients_data()
    def send_msgH(self,msg,ind):
        self.clients_socket[ind].send(msg.encode())
    def get_msgH(self,ind):
        while True:
            print(self.clients_socket[ind].recv(1024).decode())
    #
    #
    #
    # def Update_clients_data(self):
    #     lines = []
    #     for key,val in self.clients_nick.items():
    #         lines.append(f'{key}: {val}')
    #     with open('clients_data.txt','w') as f:
    #         f.writelines(lines)



