import socket
import sqlite3
import datetime
import os

HOST = "localhost"
PORT = 5000
DB_NAME = "mensajes.db"



def inicializar_db():
    """
    Crea la tabla mensajes si no existe.
    Los campos son id, contenido, fecha_envio e ip_cliente.
    Maneja errores.
    """
    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TEXT NOT NULL,
                ip_cliente TEXT NOT NULL
            )
        """)
        conexion.commit()
        conexion.close()
        print(f"[DB] Base de datos '{DB_NAME}' inicializada correctamente.")
    except sqlite3.Error as error:
        print(f"[DB] Error al inicializar la base de datos: {error}")
        raise SystemExit(1)


def guardar_mensaje(contenido, ip_cliente):
    """
    Guarda un mensaje recibido en la base de datos SQLite.
    Devuelve el timestamp usado, para incluirlo en la respuesta al cliente.
    """
    fecha_envio = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO mensajes (contenido, fecha_envio, ip_cliente) VALUES (?, ?, ?)",
            (contenido, fecha_envio, ip_cliente)
        )
        conexion.commit()
        conexion.close()
    except sqlite3.Error as error:
        print(f"[DB] Error al guardar el mensaje: {error}")
    return fecha_envio


def inicializar_socket():
    """
    Crea, configura y pone en escucha el socket del servidor.
    """
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        servidor_socket.bind((HOST, PORT))
    except OSError as error:
        print(f"[SOCKET] No se pudo iniciar el servidor en {HOST}:{PORT} -> {error}")
        print("[SOCKET] Verificá que el puerto no esté siendo usado por otro proceso.")
        raise SystemExit(1)

    servidor_socket.listen(5)
    print(f"[SOCKET] Servidor escuchando en {HOST}:{PORT}...")
    return servidor_socket


def atender_cliente(conexion, direccion):
    """
    Atiende a un cliente ya conectado:
    recibe mensajes los guarda en la DB y responde con la confirmación.
    """
    ip_cliente = direccion[0]
    print(f"[CONEXIÓN] Cliente conectado desde {ip_cliente}")

    try:
        while True:
            datos = conexion.recv(1024)
            if not datos:
                break

            mensaje = datos.decode("utf-8").strip()
            print(f"[MENSAJE] {ip_cliente} -> {mensaje}")

            timestamp = guardar_mensaje(mensaje, ip_cliente)

            respuesta = f"Mensaje recibido: {timestamp}"
            conexion.sendall(respuesta.encode("utf-8"))

    except ConnectionResetError:
        print(f"[CONEXIÓN] El cliente {ip_cliente} cerró la conexión abruptamente.")
    except Exception as error:
        print(f"[ERROR] Ocurrió un error atendiendo a {ip_cliente}: {error}")
    finally:
        conexion.close()
        print(f"[CONEXIÓN] Conexión cerrada con {ip_cliente}")


def aceptar_conexiones(servidor_socket):
    try:
        while True:
            conexion, direccion = servidor_socket.accept()
            atender_cliente(conexion, direccion)
    except KeyboardInterrupt:
        print("\n[SOCKET] Servidor detenido manualmente (Ctrl+C).")
    finally:
        servidor_socket.close()
        print("[SOCKET] Socket del servidor cerrado.")


def main():
    inicializar_db()
    servidor_socket = inicializar_socket()
    aceptar_conexiones(servidor_socket)


if __name__ == "__main__":
    main()
