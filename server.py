import socket
import threading
import os

clients = []

def server():
    ip = "127.0.0.1"
    port = 12443
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind((ip, port))
        server.listen(5)  # Número de conexões que podem esperar no servidor
        print("--> SERVIDOR INICIADO COM SUCESSO! ---")
    except:
        print("\n--> ERRO: NÃO FOI POSSÍVEL INICIAR O SERVIDOR.")
        return
    
    while True:
        client, addr = server.accept()
        print(f"--- CONEXÃO ESTABELECIDA: {addr[0]}:{addr[1]} ---")
        clients.append(client)  # Adiciona o cliente na lista de clientes
        
        thread = threading.Thread(target=tratamento_messages, args=[client])
        thread.start()


# def load_users():
#     usuarios = {}  # Dicionário para armazenar usuários

#     if not os.path.exists("database.txt"):  # Verifica se o arquivo existe
#         with open("database.txt", "w") as file:
#             file.write("admin:1234\n")  # Adiciona um usuário padrão

#     # Agora carrega os usuários do arquivo
#     with open("database.txt", "r") as file:
#         for linha in file:
#             user, senha = linha.strip().split(":")
#             usuarios[user] = senha
            
#     return usuarios

# usuarios = load_users()  # Carrega os usuários ao iniciar o servidor

def load_users():
    usuarios = {}  # Dicionário para armazenar usuários

    if not os.path.exists("database.txt"):  # Verifica se o arquivo existe
        with open("database.txt", "w") as file:
            file.write("admin:1234\n")  # Adiciona um usuário padrão

    # Agora carrega os usuários do arquivo corretamente
    with open("database.txt", "r") as file:
        for linha in file:
            partes = linha.strip().split(":")  

            # Garante que há apenas usuário e senha
            if len(partes) == 2:
                user, senha = partes
                usuarios[user] = senha
            else:
                print(f"⚠ Erro ao carregar linha mal formatada: '{linha.strip()}'")
    return usuarios

usuarios = load_users()  # Carrega os usuários ao iniciar o servidor

def save_users(username, password):
    with open("database.txt", "a") as file:  # 'a' para adicionar sem apagar o conteúdo
        file.write(f"{username}:{password}\n")
        
    

def tratamento_messages(client):
    try:
        # Recebe a escolha do cliente (Login ou Registro)
        opcao = client.recv(1024).decode("utf-8").strip()

        client.send("> Digite seu usuário: ".encode("utf-8"))
        username = client.recv(1024).decode("utf-8").strip()

        if not username:
            client.send("--> ERRO: Nome de usuário inválido.\n".encode("utf-8"))
            client.close()
            return

        if opcao == "2":  # Registro
            if username in usuarios:
                client.send("--> ERRO: Usuário já existe! Tente outro nome.\n".encode("utf-8"))
                client.close()
                return

            client.send("> Crie uma nova senha: ".encode("utf-8"))
            password = client.recv(1024).decode("utf-8").strip()

            if not password:
                client.send("--> ERRO: Senha inválida.\n".encode("utf-8"))
                client.close()
                return

            # Registrar o usuário
            usuarios[username] = password
            save_users(username, password)
            client.send("--> NOVO USUÁRIO REGISTRADO COM SUCESSO!\n".encode("utf-8"))
            print(f"--- Usuário {username} registrado ---")

        elif opcao == "1":  # Login
            if username not in usuarios:
                client.send("--> ERRO: Usuário não cadastrado! Tente registrar primeiro.\n".encode("utf-8"))
                client.close()
                return

            client.send("> Digite sua senha: ".encode("utf-8"))
            password = client.recv(1024).decode("utf-8").strip()

            if usuarios[username] != password:
                client.send("--> SENHA INCORRETA!\n".encode("utf-8"))
                client.close()
                return

            client.send("--> LOGIN BEM SUCEDIDO!\n".encode("utf-8"))
            print(f"--- Usuário {username} conectado ---")

        while True:
            message = client.recv(2048)
            if not message:
                break

            message = message.decode("utf-8")
            print
            # Verifica se é um comando para envio de arquivo
            if message.startswith("put "):
                _, filename, filesize = message.split(" ", 2)
                filesize = int(filesize)

                # Criar diretório uploads, se não existir
                if not os.path.exists("uploads"):
                    os.makedirs("uploads")

                filepath = os.path.join("uploads", filename)

                with open(filepath, "wb") as file:
                    received_bytes = 0
                    while received_bytes < filesize:
                        data = client.recv(min(4096, filesize - received_bytes))
                        if not data:
                            break
                        file.write(data)
                        received_bytes += len(data)


                print(f"--> Arquivo '{filename}' recebido e salvo em 'uploads/'.")
                client.send(f"--> Arquivo '{filename}' salvo no servidor.".encode("utf-8"))
                continue  # Pula o broadcast para evitar enviar o comando 'put' como mensagem normal

            broadcast(message, client)

    except (ConnectionResetError, BrokenPipeError):
        print(f"--- Conexão perdida com {client} ---")
    finally:
        deleteClient(client)  # Remove cliente da lista

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