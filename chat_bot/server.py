import socket
import threading
from Codec import codec, m_type


class Client:
    def __init__(self, c_sock, c_addr):
        self.c_sock = c_sock
        self.c_addr = c_addr
        self.username = None

def remove_client(client, clients, users, sem):
    sem.acquire()
    try:
        if client.username in users:
            del users[client.username]
    except Exception as e:
        print(f"Error removing client: {e}")
    finally:
        for username, other_c in users.items(): 
            # send to all the other users the username of the user that disconnected
            send(codec.encode(m_type.DISCONNECT, client.username), other_c, clients, users, sem)
        sem.release()
    
    if client.c_sock in clients:
        clients.remove(client.c_sock)
        client.c_sock.close()
    
    
    

def broadcast(message, client, clients, users, sem):
    for curr in users.values():
        if curr.c_sock != client.c_sock:
            send(codec.encode(m_type.BROADCAST, message), curr, clients, users, sem)

def send(message, client, clients, users, sem):
    try:
        client.c_sock.send(message.encode('utf-8'))
    except:
        remove_client(client, clients, users, sem)

def _get_list_of_current_users(users) -> str:
    user_str = ""
    for username in users.keys():
        user_str += f"{username} "
    return user_str
    

def handle_client(client, clients, users, sem):
    while True:
        try:
            message = client.c_sock.recv(1024).decode('utf-8')
            if message:
                # If the client is not registered yet
                message = codec.decode(message)
                msg_type, msg_data = message.type, message.data
                if client.username is None and msg_type == m_type.REGISTER:
                    current_username = msg_data
                    sem.acquire()
                    try:
                        if msg_data in users:
                            send(codec.encode(m_type.FAILED, "Username already exists"), client, clients, users, sem)
                        else:
                            send(codec.encode(m_type.APPROVED, _get_list_of_current_users(users)), client, clients, users, sem)
                            for other_username in users:
                                send(codec.encode(m_type.NEWUSER, current_username), users[other_username], clients, users, sem)
                            client.username = current_username
                            users[current_username] = client
                    finally:
                        sem.release()
                elif client.username is not None and msg_type == m_type.REGISTER:
                    send(codec.encode(m_type.FAILED, "User already registered!"), client, clients, users, sem)
                elif msg_type == m_type.BROADCAST:
                    broadcast(f"{client.username} {msg_data}", client, clients, users, sem)
                elif msg_type == m_type.IND:
                    msg_data = msg_data.split(' ', 1)
                    destination, msg_data = msg_data[0], msg_data[1]
                    if destination in users: 
                        send(codec.encode(m_type.IND, f"{client.username} {msg_data}"), users[destination], clients, users, sem) 
            else:
                break
        except:
            print("Some issue ")
            break
    remove_client(client, clients, users, sem)

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 8888))

    server.listen(10000)
    print("Server started and listening on port 8888...")

    clients = []
    users = {}
    users_sem = threading.Semaphore(1)

    while True:
        client_socket, client_addr = server.accept()
        curr_client = Client(client_socket, client_addr)
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(curr_client, clients, users, users_sem)).start()