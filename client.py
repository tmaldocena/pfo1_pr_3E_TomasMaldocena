import socket

HOST = "localhost"
PORT = 5000
PALABRA_SALIDA = "exit"


def conectar_servidor():
    """
    Creación del socket y conexión al servidor
    """
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente_socket.connect((HOST, PORT))
        print(f"[CONEXIÓN] Conectado al servidor {HOST}:{PORT}")
    except ConnectionRefusedError:
        print("[ERROR] No se pudo conectar al servidor. ¿Está corriendo server.py?")
        raise SystemExit(1)
    return cliente_socket


def enviar_mensajes(cliente_socket):
    """
    El loop del cliente: pide mensajes por consola y los evia al servidor
    hasta que el usuario escriba "exit"
    """
    print(f"Escribí '{PALABRA_SALIDA}' para terminar la conversación.\n")

    while True:
        mensaje = input("Mensaje a enviar: ").strip()

        if mensaje.lower() in PALABRA_SALIDA:
            print("[CLIENTE] Cerrando la conexión...")
            break

        if mensaje == "":
            print("[CLIENTE] No se puede enviar un mensaje vacío.")
            continue

        try:
            cliente_socket.sendall(mensaje.encode("utf-8"))
            respuesta = cliente_socket.recv(1024).decode("utf-8")
            print(f"[SERVIDOR] {respuesta}\n")
        except (BrokenPipeError, ConnectionResetError):
            print("[ERROR] Se perdió la conexión con el servidor.")
            break


def main():
    cliente_socket = conectar_servidor()
    try:
        enviar_mensajes(cliente_socket)
    finally:
        cliente_socket.close()
        print("[CONEXIÓN] Socket del cliente cerrado.")


if __name__ == "__main__":
    main()
