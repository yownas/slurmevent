import optparse
import socket
import sys

HOST, PORT = "localhost", 50007

waiting = True
errno = 0

op = optparse.OptionParser(usage="usage: %prog [-h] [-v] [-p|-r|-c jobid]")
op.add_option("-v", "--verbose",
              action="store_true", dest="verbose", default=False,
              help="show incomming data")
op.add_option("-p", "--pending",
              action="store", type="string", default="",
              help="wait until jobid is pending")
op.add_option("-r", "--running",
              action="store", type="string", default="",
              help="wait until jobid is pending")
op.add_option("-c", "--complete",
              action="store", type="string", default="",
              help="wait until jobid is pending")
(opts, args) = op.parse_args()

if opts.pending != "":
  waitfor = " %s pending" % (opts.pending)
if opts.running != "":
  waitfor = " %s running" % (opts.running)
if opts.complete != "":
  waitfor = " %s complete" % (opts.complete)

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
    if verbose:
      print(received)
    # Check it match and exit
    if waitfor in received:
      print(received)
      waiting = False

sock.close()
sys.exit(errno)
