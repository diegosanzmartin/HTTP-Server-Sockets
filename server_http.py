import signal, select, socket, sys, os, re                                      #Funciones orientadas a conexión, sistema, json y expresiones regulares
from time import time                                                           #Cronometrar tiempos

ERR = "\033[93m"
END = "\033[0m"

if __name__ == "__main__":
    if len(sys.argv) != 2 :                                                     
        print(ERR + "ERR: Nº de argumentos no válidos" + END)
        sys.exit()
        conn, addr = sock.accept()

    #Variables socket
    servIP = "0.0.0.0"
    servPort = int(sys.argv[1])
    serv_addr = (servIP, servPort)

    if servPort not in [80, 443, 591] and servPort < 1023:
        print(ERR + "ERR: El nº de puerto debe ser 80, 443, 591 o mayor que 1023" + END)
        sys.exit()

    #Creación del socket TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(0)                                                         #Establecemos modo no bloqueo

    #Conexión socket
    sock.bind(serv_addr)
    sock.listen(10)
    inputs = [sock]                                                             #Lista de sockets de lectura
    outputs = []                                                                #Lista de sockets de escritura
    clientes = {}                                                               #Lista de clientes  
    nCli = 0

    while True:
        try:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)     #Select coordina entre i/o

            for sck in readable:                                                #Sockets de entrada disponibles
                if sck == sock:                                                 #Un nuevo socket desea conectarse                                        
                    cli, cli_add = sock.accept()                                #Aceptamos la conexión de un socket "readable"
                    cli.setblocking(0)                                          #Establecemos modo no bloqueo
                    print("-Cliente:", cli_add)

                    inputs.append(cli)                                          #Añadimos al final la lista inputs
                    outputs.append(cli)                                         #Añadimos al final la lista outputs

                else:
                    dataRecv = sck.recv(1024)
                    if dataRecv:
                        lines = dataRecv.split(b'\r\n')
                        method, uri, version = lines[0].split(b' ')

                        if uri == b'/' or uri == b'/index.html':
                            sck.send(b'HTTP/1.1 200 OK\r\n\r\n')
                            html = open("index.html").read()
                            html = str.encode(html)
                            sck.send(html)

                        elif uri == b'/favicon.ico':
                            sck.send(b'HTTP/1.1 404 Not Found\r\n\r\n')

                        else:
                            sck.send(b'HTTP/1.1 200 OK\r\n\r\n')
                            html = open("404.html").read()
                            html = str.encode(html)
                            sck.send(html)
                    else:
                        outputs.remove(sck)                                     #Eliminamos el socket de la lista de outputs
                        inputs.remove(sck)                                      #Eliminamos el socket de la lista de inputs
                        sck.close()


            for sck in exceptional:                                             #Condiciones excepcionales
                inputs.remove(sck)                                              #Eliminamos el socket de la lista de inputs
                outputs.remove(sck)                                             #Eliminamos el socket de la lista de outputs
                sck.close()                                                     #Cerramos el socket

        except KeyboardInterrupt:
            print("\nCerrando conexión con clientes")
            sys.exit()