import socket
import sys

HOST, PORT = "localhost", 50007

waiting = True
errno = 0

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
  # Connect to server
  sock.connect((HOST, PORT))
except:
  print("Error")
  sys.exit(1)

#    sock.sendall(data + "\n")

while waiting:
  # Receive data from the server and shut down
  received = str(sock.recv(1024), "ascii").strip()
  if received == "":
    errno = 1
    waiting = False
  else:
    print(format(received))

sock.close()
sys.exit(errno)
