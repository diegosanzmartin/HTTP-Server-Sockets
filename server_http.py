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

    print("-> Servidor activo en: ", serv_addr)

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
                        uri = uri.decode("utf-8")
                        method = method.decode("utf-8")
                        version = version.decode("utf-8")
                        print(method, uri, version)
                        
                        if uri == "/":
                            data = open("index.html").read()
                            data = str.encode(data)
                            sck.send(b'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\nContent-Length: %i\r\n\r\n' % len(data))
                            sck.send(data)

                        elif uri == "/login" and method == "GET":
                            data = open("login.html").read()
                            data = str.encode(data)
                            sck.send(b'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\nContent-Length: %i\r\n\r\n' % len(data))
                            sck.send(data)

                        elif uri == "/login" and method == "POST":
                            print(dataRecv)

                        elif uri == "favicon.ico":
                            sck.send(b'HTTP/1.0 404 Not Found\r\n\r\n')

                        elif uri.find("/css/") == 0:
                            data = open(uri[1:]).read()
                            data = str.encode(data)
                            sck.send(b'HTTP/1.0 200 OK\r\nContent-Type: text/css\r\nContent-Length: %i\r\n\r\n' % len(data))
                            sck.send(data)

                        elif uri.find("/images/") == 0:
                            with open(uri[1:], "rb") as image:
                                data = image.read()

                            sck.send(b'HTTP/1.0 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: %i\r\n\r\n' % len(data))
                            sck.send(data)

                        else:
                            data = open("404.html").read()
                            data = str.encode(data)
                            sck.send(b'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\nContent-Length: %i\r\n\r\n' % len(data))
                            sck.send(data)
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