import socket
import threading
from Codec import codec, m_type


def receive_messages(sock, sys_users):
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            message = codec.decode(message)
            msg_type, msg_data = message.type, message.data
            if message:
                if msg_type == m_type.IND:
                    msg_data = msg_data.split(' ', 1)
                    print(f"\nUSER {msg_data[0]} to you: {msg_data[1]}")
                elif msg_type == m_type.BROADCAST:
                    msg_data = msg_data.split(' ', 1)
                    print(f"\nUSER {msg_data[0]} to everyone: {msg_data[1]}")
                elif msg_type == m_type.NEWUSER:
                    sys_users.add(msg_data)
                elif msg_type == m_type.DISCONNECT:
                    sys_users.remove(msg_data)
            else:
                break
        except:
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 8888))
    registered = False
    sys_users = set()
    my_username = ""
    
    while not registered: 
        curr_user = input("Enter username: ")
        msg = codec.encode(m_type.REGISTER, curr_user)
        if msg:
            client.send(msg.encode('utf-8'))
            while True: 
                try:
                    response = client.recv(1024).decode('utf-8')
                    response = codec.decode(response)
                    
                    res_type, res_data = response.type, response.data
                    if res_type == m_type.APPROVED:
                        print(res_data)
                        registered = True
                        username = curr_user
                        for other_user in res_data.split(' '):
                            sys_users.add(other_user)
                    else:
                        print(res_data)
                    break
                except:
                    break

        else:
            print("Username can't be empty")

    threading.Thread(target=receive_messages, args=(client, sys_users)).start()

    while True:
        c_type = input("1. Broadcast\n2. Individual user")
        message = ""
        if c_type == '1':
            c_text = input("Enter message: ")
            if c_text:
                message = codec.encode(m_type.BROADCAST, c_text)
            else: 
                continue
        elif c_type == '2':
            c_user = input("Enter User to Send to: ")
            if c_user in sys_users: 
                c_text = input("Enter message: ")
                if c_text:
                    message = codec.encode(m_type.IND, f"{c_user} {c_text}")
                else:
                    continue
            else:
                continue

        try:
            client.send(message.encode('utf-8'))
        except:
            print("Failed to send message. Exiting.")
            break

if __name__ == "__main__":
    main()