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
        server.listen(5)  # Número de conexões que podem esperar no servidor
    except:
        print("\n--> ERRO: NÃO FOI POSSÍVEL INICIAR O SERVIDOR.")
        return
    
    while True:
        client, addr = server.accept()
        print(f"--- CONEXÃO ESTABELECIDA: {addr[0]}:{addr[1]} ---")
        clients.append(client)  # Adiciona o cliente na lista de clientes
        
        thread = threading.Thread(target=tratamento_messages, args=[client])
        thread.start()


def load_users():
    usuarios = {}  # Dicionário para armazenar usuários

    if not os.path.exists("database.txt"):  # Verifica se o arquivo existe
        with open("database.txt", "w") as file:
            file.write("admin:1234\n")  # Adiciona um usuário padrão

    # Agora carrega os usuários do arquivo
    with open("database.txt", "r") as file:
        for linha in file:
            user, senha = linha.strip().split(":")
            usuarios[user] = senha
            
    return usuarios

usuarios = load_users()  # Carrega os usuários ao iniciar o servidor


def save_users(username, password):
    with open("database.txt", "a") as file:  # 'a' para adicionar sem apagar o conteúdo
        file.write(f"{username}:{password}\n")
    

def tratamento_messages(client):
    try:
        client.send("> Digite seu usuário: ".encode("utf-8"))
        username = client.recv(1024).decode("utf-8").strip()
        if not username in usuarios:
            client.send("--> USUARIO NAO CADASTRADO --\n> Deseja se cadastrar? (s/n): ".encode("utf-8"))
            resposta = client.recv(1024).decode("utf-8").strip()
            if resposta == "n":
                client.send("--> CONEXÃO ENCERRADA --\n".encode("utf-8"))
                client.close()
                return
            else:
                client.send("> Digite sua senha: ".encode("utf-8"))
                password = client.recv(1024).decode("utf-8").strip()

                usuarios[username] = password
                save_users(username, password)

            print(f"--- Usuário {username} registrado ---")

        if not username or not password:  # Verifica se os dados foram recebidos corretamente
            client.send("--> ERRO: Login inválido.\n".encode("utf-8"))
            client.close()
            return


        if username in usuarios:
            if usuarios[username] == password:
                client.send("--> LOGIN BEM SUCEDIDO!\n".encode("utf-8"))
                print(f"--- Usuário {username} conectado ---")
            else:
                client.send("--> SENHA INCORRETA!\n".encode("utf-8"))
                client.close()
                return
        else:
            usuarios[username] = password
            save_users(username, password)
            client.send("--> NOVO USUÁRIO REGISTRADO!\n".encode("utf-8"))
            print(f"--- Usuário {username} registrado ---")

        while True:
            message = client.recv(2048)
            if not message:
                break
            broadcast(message, client)
    except (ConnectionResetError, BrokenPipeError):
        print(f"--- Conexão perdida com {client} ---")
    finally:
        deleteClient(client)  # Garante que o cliente seja removido corretamente


def broadcast(message, client):
    for clnt in clients:
        if clnt != client:
            try:
                clnt.send(message)
            except:
                deleteClient(clnt)

                
def deleteClient(client):
    if client in clients:  # Verifica se o cliente ainda está na lista antes de remover
        clients.remove(client)
        print(f"--- CONEXÃO ENCERRADA: {client} se desconectou ---")

server()