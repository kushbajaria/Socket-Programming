import socket
import os

CONTROL_PORT = 11123

def send_ctrl(conn, msg):
    conn.send(msg.encode())

def recv_ctrl(conn, buf=4096):
    return conn.recv(buf).decode().strip()

def open_data_listener():
    ds = socket.socket()
    ds.bind(('', 0))
    ds.listen(1)
    port = ds.getsockname()[1]
    return ds, port

def handle_ls(ctrl_conn):
    files = os.listdir('.')
    listing = '\n'.join(files) if files else 'No files found.'

    ds, port = open_data_listener()
    send_ctrl(ctrl_conn, f"DATAPORT {port}")

    data_conn, _ = ds.accept()
    try:
        data_conn.sendall(listing.encode())
    finally:
        data_conn.close()
        ds.close()

    send_ctrl(ctrl_conn, "DONE")

def handle_get(ctrl_conn, filename):
    if not os.path.exists(filename):
        send_ctrl(ctrl_conn, "NOTFOUND")
        return

    send_ctrl(ctrl_conn, "OK")
    ds, port = open_data_listener()
    send_ctrl(ctrl_conn, f"DATAPORT {port}")

    data_conn, _ = ds.accept()
    try:
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                data_conn.sendall(chunk)
    finally:
        data_conn.close()
        ds.close()

    send_ctrl(ctrl_conn, "DONE")

def handle_put(ctrl_conn, filename):
    send_ctrl(ctrl_conn, "OK")
    ds, port = open_data_listener()
    send_ctrl(ctrl_conn, f"DATAPORT {port}")

    data_conn, _ = ds.accept()
    try:
        with open(filename, 'wb') as f:
            while True:
                chunk = data_conn.recv(4096)
                if not chunk:
                    break
                f.write(chunk)
    finally:
        data_conn.close()
        ds.close()

    send_ctrl(ctrl_conn, "DONE")

def main():
    s = socket.socket()
    print("Socket created")
    s.bind(('', CONTROL_PORT))
    print(f"Listening on control port {CONTROL_PORT}")
    s.listen(5)

    ctrl_conn, addr = s.accept()
    print(f"Control connection from {addr}")

    while True:
        try:
            data = recv_ctrl(ctrl_conn)
        except Exception:
            break

        if not data:
            break

        print(f"Received command: {data}")
        cmd = data.split()
        if not cmd:
            send_ctrl(ctrl_conn, "ERROR: Empty command")
            continue

        verb = cmd[0].lower()
        if verb == 'ls':
            handle_ls(ctrl_conn)

        elif verb == 'get':
            if len(cmd) != 2:
                send_ctrl(ctrl_conn, "ERROR: Missing filename")
                continue
            handle_get(ctrl_conn, cmd[1])

        elif verb == 'put':
            if len(cmd) != 2:
                send_ctrl(ctrl_conn, "ERROR: Missing filename")
                continue
            handle_put(ctrl_conn, cmd[1])

        elif verb == 'quit':
            send_ctrl(ctrl_conn, "Goodbye")
            break

        else:
            send_ctrl(ctrl_conn, "Unknown command")

    ctrl_conn.close()
    s.close()
    print("Server shutdown")

if __name__ == '__main__':
    main()
