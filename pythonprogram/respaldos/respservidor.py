"""
import http.server
import socketserver
import socket
import sys

# Configuración del puerto
PUERTO = 8000

def obtener_ip_local():
    """
    Obtiene la dirección IP local en la red.
    """
    try:
        # Conectamos a un servidor externo (Google DNS) para determinar la IP de salida
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # Si falla, devolvemos localhost

def main():
    ip_local = obtener_ip_local()
    print("="*50)
    print("SERVIDOR WEB LOCAL")
    print("="*50)
    print(f"Servidor corriendo en:")
    print(f"  • Local:   http://localhost:{PUERTO}")
    print(f"  • Red:     http://{ip_local}:{PUERTO}")
    print("\nComparte la dirección de RED con otros dispositivos")
    print("conectados a la misma red Wi-Fi o cable.")
    print("\nPresiona Ctrl+C para detener el servidor.")
    print("="*50)

    # Configuramos el servidor para que escuche en todas las interfaces ("" equivale a 0.0.0.0)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PUERTO), handler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServidor detenido.")
        httpd.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()
"""