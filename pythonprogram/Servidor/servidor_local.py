import http.server
import socketserver
import socket
import sys
import urllib.parse

PUERTO = 8000

# usuario : {password, rol}
USUARIOS = {
    "admin": {"password": "1234", "rol": "admin"},
    "mario": {"password": "uaz2025", "rol": "usuario"},
}


def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


class MiHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):

        if self.path == "/login":

            longitud = int(self.headers['Content-Length'])
            datos = self.rfile.read(longitud).decode()

            campos = urllib.parse.parse_qs(datos)

            usuario = campos.get("usuario", [""])[0]
            password = campos.get("password", [""])[0]

            if usuario in USUARIOS and USUARIOS[usuario]["password"] == password:

                rol = USUARIOS[usuario]["rol"]

                if rol == "admin":
                    destino = "/admin.html"
                else:
                    destino = "/usuarios.html"

                self.send_response(302)
                self.send_header("Location", destino)
                self.end_headers()

            else:

                self.send_response(302)
                self.send_header("Location", "/index.html?error=1")
                self.end_headers()


def main():

    ip_local = obtener_ip_local()

    print("="*50)
    print("SERVIDOR WEB LOCAL")
    print("="*50)
    print(f"Local: http://localhost:{PUERTO}")
    print(f"Red:   http://{ip_local}:{PUERTO}")
    print("="*50)

    handler = MiHandler
    httpd = socketserver.TCPServer(("", PUERTO), handler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido")
        httpd.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()