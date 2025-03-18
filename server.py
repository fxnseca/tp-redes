import socket


if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 12134
    
    #criando o server com o socket
    #AF_INET: a "familia" do endereço é IPV4
    #SOCK_STREAM: o tipo de protocolo de conexão é TCP
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(3) # nro de conexões que podem esperar no servidor 
    
    while True:
        client, adress = server.accept()
        print(f"--- CONEXAO ESTABELECIDA: {adress[0]}:{adress[1]} ---")
        
        string = client.recv(1024)
        string = string.decode("utf-8")
        string = string.upper() #transforma o texto em CAPSLOCK
        client.send(bytes(string, "utf-8"))
        
        # print(f"\n--> Mensagem recebida: {string}")
        
        
        client.close()
        print("\n--- CONEXAO ENCERRADA ---\n")
        