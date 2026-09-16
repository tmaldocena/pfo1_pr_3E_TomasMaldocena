# TP: Chat Básico Cliente-Servidor con Sockets y Base de Datos

Implementación de un chat simple cliente-servidor en Python usando sockets TCP/IP, con persistencia de los mensajes en una base de datos SQLite.

## Objetivo

Configurar un servidor de sockets que reciba mensajes de clientes, los almacene en una base de datos y envíe confirmaciones, aplicando buenas prácticas de modularización y manejo de errores.

## Estructura del proyecto

```
.
├── server.py      # Servidor de sockets + persistencia en SQLite
├── client.py      # Cliente que se conecta y envía mensajes
├── mensajes.db    # Base de datos SQLite (se crea automáticamente al ejecutar el servidor)
└── README.md
```

## Requisitos

- Python 3.7 o superior

No requiere instalar dependencias externas: `socket`, `sqlite3` y `datetime` forman parte de la librería estándar de Python.

## Cómo ejecutarlo

Se necesitan **dos terminales**.

**Terminal 1 — Servidor:**

```bash
python3 server.py
```

Salida esperada:

```
[DB] Base de datos 'mensajes.db' inicializada correctamente.
[SOCKET] Servidor escuchando en localhost:5000...
```

**Terminal 2 — Cliente:**

```bash
python3 client.py
```

Luego se escriben los mensajes por consola. Para terminar la conversación, escribir `éxito`.

Ejemplo de sesión:

```
[CONEXIÓN] Conectado al servidor localhost:5000
Escribí 'éxito' para terminar la conversación.

Mensaje a enviar: Hola mundo
[SERVIDOR] Mensaje recibido: 2026-09-16 14:32:07

Mensaje a enviar: Segundo mensaje
[SERVIDOR] Mensaje recibido: 2026-09-16 14:32:15

Mensaje a enviar: éxito
[CLIENTE] Cerrando la conexión...
[CONEXIÓN] Socket del cliente cerrado.
```

Para detener el servidor: `Ctrl + C`.

## Base de datos

El servidor crea automáticamente la base `mensajes.db` con la tabla `mensajes`:

| Campo         | Tipo    | Descripción                              |
|---------------|---------|------------------------------------------|
| `id`          | INTEGER | Clave primaria autoincremental           |
| `contenido`   | TEXT    | Texto del mensaje enviado por el cliente |
| `fecha_envio` | TEXT    | Timestamp `YYYY-MM-DD HH:MM:SS`          |
| `ip_cliente`  | TEXT    | Dirección IP de origen del cliente       |

Para consultar los mensajes guardados:

```bash
sqlite3 mensajes.db "SELECT * FROM mensajes;"
```

O desde Python:

```python
import sqlite3
conexion = sqlite3.connect("mensajes.db")
for fila in conexion.execute("SELECT * FROM mensajes"):
    print(fila)
```

## Arquitectura

### Servidor (`server.py`)

Está modularizado en funciones con una responsabilidad clara cada una:

| Función                | Responsabilidad                                                        |
|------------------------|------------------------------------------------------------------------|
| `inicializar_db()`     | Crea la base y la tabla `mensajes` si no existen                       |
| `guardar_mensaje()`    | Inserta un mensaje en la DB y devuelve el timestamp                    |
| `inicializar_socket()` | Crea, configura (`bind`) y pone en escucha (`listen`) el socket TCP    |
| `atender_cliente()`    | Recibe mensajes de un cliente conectado y responde la confirmación     |
| `aceptar_conexiones()` | Loop principal: acepta conexiones entrantes y las delega               |
| `main()`               | Punto de entrada que orquesta el flujo completo                        |

El servidor responde a cada mensaje con el formato: `Mensaje recibido: <timestamp>`.

### Cliente (`client.py`)

| Función               | Responsabilidad                                                  |
|-----------------------|------------------------------------------------------------------|
| `conectar_servidor()` | Crea el socket y se conecta a `localhost:5000`                   |
| `enviar_mensajes()`   | Loop de envío hasta que el usuario escriba `éxito`               |
| `main()`              | Punto de entrada; garantiza el cierre del socket con `finally`   |

## Manejo de errores

| Situación                         | Manejo                                                                 |
|-----------------------------------|------------------------------------------------------------------------|
| Puerto 5000 ocupado               | Se captura `OSError` en el `bind` y se avisa antes de salir            |
| Base de datos no accesible        | Se captura `sqlite3.Error` al inicializar y al insertar                |
| Servidor apagado al conectar      | El cliente captura `ConnectionRefusedError` con un mensaje claro       |
| Cliente cerrado abruptamente      | El servidor captura `ConnectionResetError` y libera la conexión        |
| Conexión perdida durante el envío | El cliente captura `BrokenPipeError` / `ConnectionResetError`          |
| Mensaje vacío                     | El cliente lo valida y no lo envía                                     |
| Interrupción con `Ctrl + C`       | Se captura `KeyboardInterrupt` y se cierra el socket ordenadamente     |

Además se usa `SO_REUSEADDR` para permitir reiniciar el servidor de inmediato sin esperar a que el sistema libere el puerto, y los sockets se cierran siempre dentro de bloques `finally`.

## Detalles de implementación

- **Protocolo:** TCP (`SOCK_STREAM`) sobre IPv4 (`AF_INET`).
- **Dirección:** `localhost:5000`.
- **Codificación:** UTF-8 en el envío y la recepción, con buffer de 1024 bytes.
- **Concurrencia:** el servidor atiende un cliente por vez (modelo secuencial), suficiente para el alcance del TP. Con `listen(5)` se permite una cola de hasta 5 conexiones en espera.
- **Consultas parametrizadas:** los `INSERT` usan placeholders `?` en lugar de concatenar strings, evitando inyección SQL.
