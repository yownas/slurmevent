#!/usr/bin/python3

import re
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
      r,w,e = select.select([self.request],[],[],0.01)

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
          self.request.sendall(bytes("%d %s" % (self.msgid, message), 'ascii'))
          #self.request.sendall(message)
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

  #FIXME wait until all clients has got the last msg

  if tail.poll(1):
    log = str(logfile.stdout.readline())
    state = ""

    m = re.match(".* _slurm_rpc_submit_batch_job: JobId=([0-9]*) .*", log)
    if m is not None:
      jobid = m.groups()[0]
      state = "pending"

    m = re.match(".* prolog_running_decr: Configuration for JobId=([0-9]*) is complete", log)
    if m is not None:
      jobid = m.groups()[0]
      state = "running"

    m = re.match(".* _job_complete: JobId=([0-9]*) done", log)
    if m is not None:
      jobid = m.groups()[0]
      state = "complete"

    if state != "":
      #message = log
      message = "%s %s" % (jobid, state)
      messageid += 1
      print("%d %s" % (messageid, message))
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


