#!/usr/bin/python3

import re
import sys
import socket
import select
import subprocess


HOST = 'localhost' 
PORT = 50007

SOCKET_LIST = []
RECV_BUFFER = 4096 

def chat_server():
    # Open logfile tail
    logfile = subprocess.Popen(['tail', '-n0', '-F', 'my.log'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    tail = select.poll()
    tail.register(logfile.stdout) 

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(256)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
 
    print("slurmeventd started on port " + str(PORT))
 
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
      
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                print("Client (%s, %s) connected" % addr)
                 
                #broadcast(server_socket, sockfd, "[%s:%s] entered our chatting room\n" % addr)
             
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        ## there is something in the socket
                        #broadcast(server_socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)  
                        print('[' + str(sock.getpeername()) + '] ' + data)  
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        ## at this stage, no data means probably the connection has been broken
                        #broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr) 

                # exception 
                except:
                    #broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
                    continue

        # Check if there is new logdata
        if tail.poll(0.1):
            #log = str(logfile.stdout.readline()).strip()
            log = logfile.stdout.readline().decode('utf-8')
            state = ""

            m = re.match("\[(.*)\] _slurm_rpc_submit_batch_job: JobId=([0-9]*) .*", log)
            if m is not None:
                time = m.groups()[0]
                jobid = m.groups()[1]
                state = "pending"

            m = re.match("\[(.*)\] prolog_running_decr: Configuration for JobId=([0-9]*) is complete", log)
            if m is not None:
                time = m.groups()[0]
                jobid = m.groups()[1]
                state = "running"

            m = re.match("\[(.*)\] _job_complete: JobId=([0-9]*) done", log)
            if m is not None:
                time = m.groups()[0]
                jobid = m.groups()[1]
                state = "complete"

            if state != "":
                message = "[%s] %s %s" % (time, jobid, state)
                print("%s" % (message))
                broadcast(server_socket, message)

    server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket :
            try :
                socket.send(bytes(message, 'ascii'))
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)
 
if __name__ == "__main__":

    sys.exit(chat_server())  
