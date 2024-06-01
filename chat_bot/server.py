import socket 
import threading 

def remove_client(c_socket, clients):
    if c_socket in clients:
        clients.remove(c_socket)
        c_socket.close()

def broadcast(message, c_socket, clients):
    for client in clients:
        if client != c_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                remove_client(client, clients)



def handle_client(c_scoket, clients):
    while True:
        try:
            message = c_scoket.recv(1024).decode('utf-8')
            if message:
                broadcast(message, c_scoket, clients)
            else :
                remove_client(c_scoket, clients)
                break
        except:
            remove_client(c_scoket, clients)
            break

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8888))

    server.listen(10000)
    clients = []

    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket, clients)).start()