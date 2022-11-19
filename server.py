import socket, select


def callback(request: bytes) -> bytes:
    if request == b"GET /test\n":
        return b"TEST\n"

    return b"404\n"


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setblocking(False)
    server_socket.bind(("0.0.0.0", 8080))
    server_socket.listen()

    epoll = select.epoll()
    epoll.register(server_socket.fileno(), select.EPOLLIN)

    client_sockets: dict[int, socket.socket] = {}
    responses: dict[int, bytes] = {}

    try:
        while True:
            for fd, event in epoll.poll():
                if fd == server_socket.fileno():
                    sock, addr = server_socket.accept()
                    sock.setblocking(False)
                    epoll.register(sock.fileno(), select.EPOLLIN)
                    client_sockets[sock.fileno()] = sock
                    print(f"New connection, fd = {sock.fileno()}")
                elif event & select.EPOLLIN:
                    data = client_sockets[fd].recv(16)
                    if len(data) == 0:
                        print(f"Connection closed, unregister fd {fd}")
                        epoll.unregister(fd)
                        client_sockets.pop(fd).close()
                    else:
                        print(f"fd {fd} received {data}")
                        responses[fd] = callback(data)
                        epoll.modify(fd, select.EPOLLOUT)
                        client_sockets[fd].setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
                elif event & select.EPOLLOUT:
                    data = responses.pop(fd)
                    print(f"fd {fd} ready to send data, sending {data}")
                    sock = client_sockets[fd]
                    sock.send(data)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 0)
                    epoll.modify(fd, select.EPOLLIN)
    except KeyboardInterrupt:
        pass
    finally:
        epoll.unregister(server_socket.fileno())
        epoll.close()
        server_socket.close()


if __name__ == "__main__":
    main()
