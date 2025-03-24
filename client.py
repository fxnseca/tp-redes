import socket
import threading  

def client():
    ip = "127.0.0.1"
    port = 12344
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((ip, port))
    except:
        print("\n--> ERRO: NÃO FOI POSSÍVEL SE CONECTAR AO SERVIDOR.")
        return

    # Enviar login
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

    # Se a senha estiver errada, encerra a conexão
    if "SENHA INCORRETA" in resposta or "ERRO" in resposta:
        print("\n--> Conexão encerrada devido a erro de login.")
        client.close()
        return  
    if "n" in resposta:
        print("\n--> Conexão encerrada devido a erro de cadastro.")
        client.close()
        return
    
    # Criando múltiplas threads:
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
            client.send(f'<{username}> {message}'.encode("utf-8"))
        except:
            print("\n--> ERRO: Não foi possível enviar a mensagem.")
            client.close()
            break


client()