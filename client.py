import os
import socket
import threading  

def client():
    ip = "127.0.0.1"
    port = 12443
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((ip, port))
    except:
        print("\n--> ERRO: NÃO FOI POSSÍVEL SE CONECTAR AO SERVIDOR.")
        return

    while True:
        print("\n----- MENU -----")
        print("1. Login")
        print("2. Registrar")
        opcao = input("\nEscolha uma opção (1 ou 2): ")

        if opcao not in ["1", "2"]:
            print("\n--> Opção inválida. Tente novamente.")
            continue

        client.send(opcao.encode("utf-8"))  # Envia a opção para o servidor

        # Enviar nome de usuário
        print(client.recv(1024).decode("utf-8"), end="")
        username = input()
        client.send(username.encode("utf-8"))

        # Enviar senha
        print(client.recv(1024).decode("utf-8"), end="")
        password = input()
        client.send(password.encode("utf-8"))

        # Confere resposta do servidor
        resposta = client.recv(1024).decode("utf-8")
        print(resposta)  

        if "SENHA INCORRETA" in resposta or "ERRO" in resposta:
            print("\n--> Conexão encerrada devido a erro de login.")
            client.close()
            return  
        elif "REGISTRO CANCELADO" in resposta:
            print("\n--> Conexão encerrada devido ao cancelamento do registro.")
            client.close()
            return  
        elif "NOVO USUÁRIO REGISTRADO" in resposta or "LOGIN BEM SUCEDIDO" in resposta:
            break  # Sai do loop e entra no chat

    # Criando múltiplas threads para enviar e receber mensagens:
    thread_1 = threading.Thread(target=receiveMessages, args=[client])
    thread_2 = threading.Thread(target=sendMessages, args=[client, username])
    
    thread_1.start()
    thread_2.start()


def receiveMessages(client):
    while True:
        try:
            message = client.recv(2048).decode("utf-8")
            if not message:
                break
            print("\n" + message)
        except:
            print('\n--> NÃO FOI POSSÍVEL PERMANECER CONECTADO AO SERVIDOR.')
            print('--> Pressione <ENTER> para sair...')
            client.close()
            break


def sendMessages(client, username):
    while True:
        try:
            message = input()
            if message.lower() == "sair":
                print("\n--> Você saiu do chat.")
                client.close()
                break

            if message.startswith("put "):  # Enviar arquivo
                _, filename = message.split(" ", 1)

                # Verifica se o arquivo existe
                if not os.path.exists(filename):
                    print(f"--> ERRO: Arquivo '{filename}' não encontrado.\nDeseja criar um novo arquivo? (s/n)")
                    resposta = input().strip().lower()

                    if resposta == "s":
                        print(f"--> Criando arquivo '{filename}'. Informe o conteúdo:")
                        conteudo = input()  # Captura o conteúdo do novo arquivo

                        if not os.path.exists("cliente " + username):
                            os.makedirs("cliente " + username)
                        filepath = os.path.join("cliente " + username, filename)

                        with open(filepath, "w", encoding="utf-8") as file:
                            file.write(conteudo)

                        print(f"--> Arquivo '{filename}' criado com sucesso.")
                    else:
                        print("--> Operação cancelada.")
                        continue  # Volta ao loop após cancelar a criação

                # Obtém o tamanho do arquivo
                filesize = os.path.getsize(filepath)
                client.send(f"put {filename} {filesize}".encode("utf-8"))

                # Lê e envia o arquivo
                with open(filepath, "rb") as file:
                    client.sendall(file.read())

                print(f"--> Arquivo '{filename}' enviado para o servidor.")
                os.remove(filepath)
                print(f"--> Arquivo '{filename}' removido da pasta do cliente.")

                continue  # Evita que o comando 'put' seja enviado como mensagem normal
            client.send(f'<{username}> {message}'.encode("utf-8"))

            if message.startswith("mkdir "):
                _, folder_name = message.split(" ", 1)
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                    print(f"--> Diretório '{folder_name}' criado com sucesso.")
                else:
                    print(f"--> ERRO: Diretório '{folder_name}' já existe.")
                continue  # Evita que o comando 'mkdir' seja enviado como mensagem normal

            if message.startswith("cd "):
                _, folder_name = message.split(" ", 1)
                if os.path.exists(folder_name) and os.path.isdir(folder_name):
                    os.chdir(folder_name)
                    print(f"--> Diretório alterado para '{os.getcwd()}'.")
                else:
                    print(f"--> ERRO: Diretório '{folder_name}' não encontrado ou não é um diretório válido.")
                continue
        except Exception:
            print("\n--> ERRO: Não foi possível enviar a mensagem.")
            client.close()
            break

client()
