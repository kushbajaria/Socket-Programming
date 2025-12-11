import socket
import os

CONTROL_PORT = 11123
SERVER_HOST = '127.0.0.1'

def recv_ctrl(sock, buf=4096):
    return sock.recv(buf).decode().strip()

def parse_dataport(msg):
    parts = msg.split()
    if len(parts) == 2 and parts[0] == 'DATAPORT':
        try:
            return int(parts[1])
        except ValueError:
            return None
    return None

def do_ls(ctrl_sock):
    ctrl_sock.send(b'ls')
    msg = recv_ctrl(ctrl_sock)
    port = parse_dataport(msg)
    if not port:
        print('Protocol error: expected DATAPORT, got:', msg)
        return

    data_sock = socket.socket()
    data_sock.connect((SERVER_HOST, port))
    listing = b''
    while True:
        chunk = data_sock.recv(4096)
        if not chunk:
            break
        listing += chunk
    data_sock.close()

    print(listing.decode())
    final = recv_ctrl(ctrl_sock)
    if final and final != 'DONE':
        print(final)

def do_get(ctrl_sock, filename):
    ctrl_sock.send(f'get {filename}'.encode())
    msg = recv_ctrl(ctrl_sock)
    if msg == 'NOTFOUND':
        print('File not found on server.')
        return
    if msg == 'OK':
        msg = recv_ctrl(ctrl_sock)

    port = parse_dataport(msg)
    if not port:
        print('Protocol error: expected DATAPORT, got:', msg)
        return

    data_sock = socket.socket()
    data_sock.connect((SERVER_HOST, port))
    with open(filename, 'wb') as f:
        while True:
            chunk = data_sock.recv(4096)
            if not chunk:
                break
            f.write(chunk)
    data_sock.close()

    final = recv_ctrl(ctrl_sock)
    if final and final != 'DONE':
        print(final)
    else:
        print(f"File '{filename}' downloaded successfully.")

def do_put(ctrl_sock, filename):
    if not os.path.exists(filename):
        print('File not found locally.')
        return

    ctrl_sock.send(f'put {filename}'.encode())
    msg = recv_ctrl(ctrl_sock)
    if msg != 'OK':
        print('Server not ready for upload. Response:', msg)
        return

    msg = recv_ctrl(ctrl_sock)
    port = parse_dataport(msg)
    if not port:
        print('Protocol error: expected DATAPORT, got:', msg)
        return

    data_sock = socket.socket()
    data_sock.connect((SERVER_HOST, port))
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            data_sock.sendall(chunk)
    data_sock.close()

    final = recv_ctrl(ctrl_sock)
    if final and final != 'DONE':
        print(final)
    else:
        print(f"File '{filename}' uploaded successfully.")

def main():
    ctrl = socket.socket()
    ctrl.connect((SERVER_HOST, CONTROL_PORT))
    print('\nAvailable commands: ls, get <filename>, put <filename>, quit')

    while True:
        command = input('\n> ').strip()
        if not command:
            continue

        parts = command.split()
        verb = parts[0].lower()
        if verb == 'ls':
            do_ls(ctrl)

        elif verb == 'get':
            if len(parts) != 2:
                print('Usage: get <filename>')
                continue
            do_get(ctrl, parts[1])

        elif verb == 'put':
            if len(parts) != 2:
                print('Usage: put <filename>')
                continue
            do_put(ctrl, parts[1])

        elif verb == 'quit':
            ctrl.send(b'quit')
            break

        else:
            print('Unknown command')

    ctrl.close()
    print('Connection closed.')

if __name__ == '__main__':
    main()