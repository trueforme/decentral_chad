import threading
class Sender:
    def __init__(self, socket):
        self.socket = socket
        self.receiver = threading.Thread(target=self.get_bytes)
        self.receiver.start()
        self.recived_msgs = []
        self.non_active = False

    def send_msg(self, msg):
        try:
            self.socket.sendall(msg.encode("utf-8"))
        except ConnectionResetError:
            self.non_active = True
        except OSError:
            None

    def get_msg(self, msg):
        if msg != "":
            self.recived_msgs.append(msg)

    def send_file(self, file_path):
        try:
            file_name = file_path.split("/")[-1]
            self.socket.send(file_name.encode("utf-16"))
            with open(file_path, "rb") as file:
                self.socket.sendall(file.read())
        except ConnectionResetError:
            self.non_active = True
        except OSError:
            None

    def get_file(self, file_name):
        file = self.socket.recv(1024 * 8 * 1024)
        with open(file_name, "wb") as f:
            f.write(file)

    def get_bytes(self):
        while True:
            try:
                data = self.socket.recv(1024 * 1024 * 8)
                try:
                    decoded_data = data.decode("utf-8")
                    self.get_msg(decoded_data)
                except UnicodeDecodeError:
                    decoded_data = data.decode("utf-16")
                    self.get_file(decoded_data)
            except ConnectionResetError:
                self.non_active = True
            except OSError or TimeoutError:
                None
