import signal, select, socket, sys, os, re                                      #Funciones orientadas a conexión, sistema, json y expresiones regulares

RED = "\033[93m"
END = "\033[0m"
BAR = "\n———————————————————————————————\n"

if __name__ == "__main__":
    if len(sys.argv) != 2 :                                                     
        print(RED + "ERR: Nº de argumentos no válidos" + END)
        sys.exit()
        conn, addr = sock.accept()

    #Variables socket
    servIP = "0.0.0.0"
    servPort = int(sys.argv[1])
    serv_addr = (servIP, servPort)

    if servPort not in [80, 443, 591] and servPort < 1023:
        print(RED + "ERR: El nº de puerto debe ser 80, 443, 591 o mayor que 1023" + END)
        sys.exit()

    #Creación del socket TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(0)                                                         #Establecemos modo no bloqueo

    #Conexión socket
    sock.bind(serv_addr)
    sock.listen(10)

    #Variable cabecera
    persistentHeader = b"Connection: keep/alive\r\n"                            #Modo persistente por defecto
    languageHeader = b"Content-Language: es\r\n"                                #Idioma en español por defecto
    index = "index.html"                                                        #Página principal es

    print("-> Servidor activo en: ", serv_addr)

    inputs = [sys.stdin, sock]                                                  #Lista de sockets de lectura
    outputs = []                                                                #Lista de sockets de escritura
    timeout = 10

    while True:
        try:
            readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)       #Select coordina entre i/o

            for sck in readable:                                                                    #Sockets de entrada disponibles
                if sck == sys.stdin:                                                                #Si detecta el teclado
                    mssIn = sys.stdin.readline()

                    if mssIn == "persistente\n":                                                    #Si detecta persistente se cambia la cabecera
                        print(RED + "->Servidor configurado en modo persistente" + END)
                        persistentHeader = b"Connection: keep/alive\r\n"

                    elif mssIn == "no persistente\n":                                               #Si detecta no persistente se cambia la cabecera
                        print(RED + "->Servidor configurado en modo no persistente" + END)
                        persistentHeader = b"Connection: close\r\n"

                elif sck == sock:                                                                   #Un nuevo socket desea conectarse                                       
                    cli, cli_add = sock.accept()                                                    #Aceptamos la conexión de un socket "readable"
                    print("->Cliente conectado:", cli_add)

                    inputs.append(cli)                                                              #Añadimos al final la lista inputs
                    outputs.append(cli)                                                             #Añadimos al final la lista outputs

                else:
                    dataRecv = sck.recv(2048).decode("utf-8")
                    method = uri = version  = data = ""                                             #Inicializamos varibales

                    if dataRecv:
                        print(BAR,RED + dataRecv + END)

                        if dataRecv.startswith(("GET", "POST", "PUT", "DELETE")):                   #Si dataRecv comienza por algún método HTTP
                            dataRecSplit = dataRecv.split("\r\n")                                   
                            method, uri, version = dataRecSplit[0].split(" ")                       #Obtenemos de dataRecv el método, uri y la versión

                            #Cabeceras de idiomas
                            lang = []
                            for x in dataRecSplit:                                                  
                                if x.startswith("Accept-Language: "):                               #Obtenemos los idiomas preferidos por el cliente
                                    lang = x[17:].split(",")
                                    
                            for l in lang:
                                if l[:2] == "es":                                                   #Si el idioma es es/ca/en cambiamos la cabecera y el index
                                    index = "index.html"
                                    languageHeader = b"Content-Language: es\r\n"
                                    break

                                if l[:2] == "ca":
                                    index = "languages/index_ca.html"
                                    languageHeader = b"Content-Language: ca\r\n"
                                    break
                                    
                                if l[:2] == "en":
                                    index = "languages/index_en.html"
                                    languageHeader = b"Content-Language: en\r\n"
                                    break


                        if method == "GET":
                            for file in os.listdir():                                               #Cualquier pagina que exista en el servidor con la uri proporcionada (sin .html)
                                if file.endswith(".html") and file[:-5] == uri[1:]:                 #será enviada al cliente
                                        data = open(uri[1:] + ".html").read()
                                        data = str.encode(data)
                                        sck.send(b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: %i\r\n%b%b\r\n' %(len(data), persistentHeader, languageHeader))
                                        sck.send(data)

                            if uri == "/":                                                          #La página principal será la variable index (cabecera idiomas)
                                data = open(index).read()
                                data = str.encode(data)
                                sck.send(b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: %i\r\n%b%b\r\n' %(len(data), persistentHeader, languageHeader))
                                sck.send(data)

                            elif uri == "/favicon.ico":                                             #No existe un favicon.ico para la página
                                sck.send(b'HTTP/1.0 404 Not Found\r\n\r\n')

                            elif uri.find("/css/") == 0:                                            #Los archivos que contengan la uri /css/archivo.css serán enviados al cliente
                                css_size = os.path.getsize(uri[1:])
                                sck.send(b'HTTP/1.1 200 OK\r\nContent-Type: text/css\r\nContent-Length: %i\r\n%b\r\n' %(css_size, persistentHeader))
                                
                                with open(uri[1:], "rb") as file:
                                    sck.sendfile(file, 0)  #Utilizamos sendfile para archivos css grandes

                            elif uri.find("/js/") == 0:                                             #Los archivos que contengan la uri /js/archivo.js serán enviados al cliente
                                data = open(uri[1:]).read()
                                data = str.encode(data)
                                sck.send(b'HTTP/1.1 200 OK\r\nContent-Type: text/javascript\r\nContent-Length: %i\r\n%b\r\n' %(len(data), persistentHeader))
                                sck.send(data)

                            elif uri.find("/images/") == 0:                                         #Los archivos que contengan la uri /images/ serán enviados al cliente
                                img_size = os.path.getsize(uri[1:])
                                sck.send(b'HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: %i\r\n%b\r\n' %(img_size, persistentHeader))
                                
                                try:                                                                
                                    """ with open(uri[1:], "rb") as file:
                                            sck.sendfile(file, 0) """

                                    with open(uri[1:], "rb") as file:                               #Otra forma de enviar archivos grandes
                                        c = 0
                                        while c <= img_size:
                                            data = file.read(1024)
                                            if not (data):
                                                print(uri[1:], img_size, "enviado")
                                                break
                                            sck.send(data)
                                            c += len(data)
                                
                                except BrokenPipeError:                                             #Si el cliente cierra el socket antes de tiempo será notificado
                                    print("ERR: Broken Pipe")

                            elif uri.find("/videos/") == 0:                                         #Los archivos que contengan la uri /videos/ serán enviados al cliente
                                vid_size = os.path.getsize(uri[1:])
                                sck.send(b'HTTP/1.0 200 OK\r\nContent-Type: video/mp4\r\nContent-Length: %i\r\n\%b\r\n' %(vid_size, persistentHeader))

                                try:
                                    """ with open(uri[1:], "rb") as file:
                                            sck.sendfile(file, 0) """

                                    with open(uri[1:], "rb") as file:
                                        c = 0
                                        while c <= vid_size:
                                            data = file.read(1024)
                                            if not (data):
                                                print(uri[1:], vid_size, "enviado")
                                                break
                                            sck.send(data)
                                            c += len(data)
                                
                                except BrokenPipeError:
                                    print("ERR: Broken Pipe")

                            else:                                                                   #Si la uri recibida no corresponde con ningun parámetro anterior se envia 404.html
                                print("ERR 404", uri, "not found")                                  
                                data = open("404.html").read()
                                data = str.encode(data)
                                sck.send(b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: %i\r\n%b%b\r\n' %(len(data), persistentHeader, languageHeader))
                                sck.send(data)
                        
                        elif method == "POST":
                            data = dataRecSplit[-1].split("&")                                      #Obtenemos el request de POST
                            if uri == "/login":
                                user = data[0].split("user=")[1]                                    #Separamos la información en usuario, email, contraseña
                                email = data[1].split("email=")[1].replace("%40", "@")
                                passw = data[2].split("pass=")[1]
                                                                                                    #Ejemplo de procesamiento de POST
                                html = """  <html>
                                                <body>
                                                    Usuario: {user}<br>
                                                    Email: {email}<br>
                                                    Contraseña: {passw}<br>
                                                </body>
                                            </html>
                                        """.format(user = user, email = email, passw = passw)
                                
                                sck.send(b'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: %i\r\n\r\n' % len(html))
                                sck.send(html.encode())
                        
                        elif method == "PUT" and uri == "/putfile":
                                pos = dataRecv.index("<!DOCTYPE html>")                             #Obtenemos la posicion de la carga útil
                                with open("ejemplo.html", "w") as file:                             #Guardamos la información en un archivo
                                    file.write(dataRecv[pos:])

                                print("Archivo subido en /ejemplo")
                        

                    else:
                        outputs.remove(sck)                                     #Eliminamos el socket de la lista de outputs
                        inputs.remove(sck)                                      #Eliminamos el socket de la lista de inputs
                        try:
                            cli_add = sck.getpeername()
                            print("->Cliente desconectado:", cli_add)
                            sck.close()

                        except OSError:
                            print("ERR: El cliente se desconectó inesperadamente")

            for sck in exceptional:                                             #Condiciones excepcionales
                inputs.remove(sck)                                              #Eliminamos el socket de la lista de inputs
                outputs.remove(sck)                                             #Eliminamos el socket de la lista de outputs
                cli_add = sck.getpeername()

                print("->Cliente desconectado:", cli_add)
                sck.close()                                                     #Cerramos el socket

            if not (readable or writable or exceptional):                       #Si select no recibe una solicitud en 10sec lo notificará
                print("Servidor web inactivo")

        except KeyboardInterrupt:
            print("\nCerrando conexión con clientes")
            sys.exit()