import socket
import threading
import os

clients = []

def server():
    ip = "127.0.0.1"
    port = 12344
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind((ip, port))
        server.listen(5) # nro de conexões que podem esperar no servidor 
    except:
        return print("\n--> ERRO: NAO FOI POSSIVEL INICIAR O SERVIDOR.")
    
    while True:
        client, addr = server.accept()
        print(f"--- CONEXAO ESTABELECIDA: {addr[0]}:{addr[1]} ---")
        clients.append(client) #adiciona o cliente na lista de clientes
        
        thread = threading.Thread(target=tratamento_messages, args=[client])
        thread.start()
        

def load_users():
    usuarios = {}  #usar {} é um dicionario (e não uma lista [])

    if not os.path.exists("database.txt"):  #vê se o arquivo existe
        with open("database.txt", "w") as file:
            file.write("admin:1234\n")  #adiciona um usuario padrao

    #agora carrega os usuarios do arquivo
    with open("database.txt", "r") as file:
        for linha in file:
            user, senha = linha.strip().split(":")
            usuarios[user] = senha
            
    return usuarios

usuarios = load_users() #chama a função assim que carrega o servidor


def save_users(username, password):
    with open("database.txt", "a") as file: # 'a' pra adicionar sem apagar o conteudo
        file.write(f"{username}:{password}\n")
    
    
def tratamento_messages(client):
    client.send("> Digite seu user: ".encode("utf-8"))
    username = client.recv(1024).decode("utf-8").strip()  #strip: remove espaços em branco
    
    client.send("> Digite sua senha: ".encode("utf-8"))
    password = client.recv(1024).decode("utf-8").strip()  #strip: remove espaços em branco
    
    if username in usuarios:
        if usuarios[username] == password:
            client.send("--> LOGIN BEM SUCEDIDO!\n".encode("utf-8"))
            print(f"--- Usuário {username} conectado ---")
        else:
            client.send("--> SENHA INCORRETA!\n".encode("utf-8"))
            client.close()
            return
    else:
        usuarios[username] = password    #adiciona novo usuario
        save_users(username, password)   #salva no arquivo
        client.send("--> NOVO USUÁRIO REGISTRADO!\n".encode("utf-8"))
        print(f"--- Usuário {username} registrado ---")
    
    while True:
        try:
            message = client.recv(2048)
            if not message:
                deleteClient(client)
                break
            broadcast(message, client)
        except:
            deleteClient(client)
            break  #pra parar de "ouvir" a mensagem desse cliente, ja que foi deletado.
        

def broadcast(message, client):
    for clnt in clients:
        if clnt!= client:
            try:
                clnt.send(message)
            except:
                deleteClient(clnt)

                
def deleteClient(client):
    print(f"--- CONEXAO ENCERRADA: {client} se desconectou ---")
    clients.remove(client)
        
        
server()