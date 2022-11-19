# Simple `epoll` TCP server in Python

Start the server:

```bash
python server.py
```

Use a TCP client to connect and send data:

```bash
netcat 127.0.0.1 8080
GET /test
```
