import socket
# import threading
# import os

if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 12134
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((ip, port))
    
    string = input("\n-> Digite a mensagem: ")
    server.send(bytes(string, "utf-8"))
    
    # mostra no client o que o server ta recebendo
    buffer = server.recv(1024)
    buffer = buffer.decode("utf-8")
    print(f"\n-> Server: {buffer}")