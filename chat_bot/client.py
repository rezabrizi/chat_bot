import socket
import threading 

def receive_messages(sock):

    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if message: print(message)
            else:
               break
        except:
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect(("127.0.0.1", 8888))
    threading.Thread(target = receive_messages, args=(client,)).start()

    while True():
        message = input("")
        if message:
            client.send(message.encode('utf-8'))
        else: break

        client.close()

if __name__ == "__main__":
    main()

