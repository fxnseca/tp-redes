import socket
import threading  
# import os

def client():
    ip = "127.0.0.1"
    port = 12344
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((ip, port))
    except:
        return print("\n--> ERRO: NAO FOI POSSIVEL SE CONECTAR AO SERVIDOR.")
    
    username = input("> Usuario: ")
    print("\n--- CONECTADO ---")
    
    #criando multiplas threads:
    thread_1 = threading.Thread(target=receiveMessages, args=[client])
    thread_2 = threading.Thread(target=sendMessages, args=[client, username])
    
    thread_1.start()
    thread_2.start()
    
    
def receiveMessages(client):
    while True:
        try:
            message = client.recv(2048).decode("utf-8")
            print(message+'\n')
        except:
            print('\n--> NÃO FOI POSSIVEL PERMANECER CONECTADO NO SERVIDOR.')
            print('-> Pressione <ENTER> pra continuar...')
            client.close()
            break
    
def sendMessages(client, username):
    while True:
        try:
            message = input("\n")
            client.send(f'<{username}> {message}' .encode("utf-8"))
        except:
            return 

client()