import socket
import threading

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
        
        thread = threading.Thread(target=tratamentoMessages, args=[client])
        thread.start()
        
        
def tratamentoMessages(client):
    while True:
        try:
            message = client.recv(2048)
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