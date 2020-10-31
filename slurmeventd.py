#!/usr/bin/python3

import select
import socket
import socketserver
import subprocess
import sys
import time
import threading

clientList = []
#inbox = []

message = ""
messageid = 0

serverRunning = True

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
  clients = []    
  msgid = messageid
  running = serverRunning
  def setup(self):
    clientList.append(self.client_address)

    self.clients = list(dict.fromkeys(clientList)) #FIXME remove this?
    print(self.clients)
    print("Client List Length : ",len(self.clients))

  def handle(self):
    print("Server handle.")
    while self.running:
      #r,w,e = select.select([self.request],[],[],0.01)
      r,w,e = select.select([self.request],[],[],0.5)

      for rs in r:
        if rs == self.request:
          try:
            data = str(self.request.recv(1024) ,"ascii").strip()
          except:
            data = ""

#TODO: reply to client request?
          if data == "quit":
            self.running = False

      # Check if client has latest message
      if messageid > self.msgid:
        try:
          self.msgid = messageid
          #self.request.sendall(bytes(message, 'utf-8'))
          self.request.sendall(message)
        except BrokenPipeError as e:
          print(e)
          self.running = False

      # Shutdown?
      if serverRunning == False:
        self.running = False

  def finish(self):
    print("Client disconnect")
    clientList.remove(self.client_address)
    print("Clients: ",len(clientList))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
  pass

def read_log():
  global message, messageid
  if tail.poll(1):
    log = logfile.stdout.readline()
    print(log)
    message = log
    messageid += 1
  pass


if __name__ == "__main__":
  logfile = subprocess.Popen(['tail', '-n0', '-F', 'my.log'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  tail = select.poll()
  tail.register(logfile.stdout) 

  HOST, PORT = "localhost", 50007
  try:
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
  except socket.error as e:
    print("Bind error: ",str(e))
    sys.exit(1)

  ip, port = server.server_address

  server_thread = threading.Thread(target=server.serve_forever)

  server_thread.daemon = True
  server_thread.start()

  try:
    while server_thread:
      read_log()
  except KeyboardInterrupt:
    print("Shutting down.")
    serverRunning = False

  sys.exit()


