
import socket
import threading
import sys
import gzip

def handle_request(client, data):
        request_data = data.decode().lower().split("\r\n")
        path_type = request_data[0].split(" ")[0]
        path = request_data[0].split(" ")[1]
        
        
        if path.startswith("/echo") and path_type=="get" :
            body = path[6:].encode()
            response= f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n"
            
            if "gzip" in request_data[2]:
                body = gzip.compress(body)
                response= f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n"
            client.sendall(response.encode() + body)

        elif path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
            client.send(response.encode())

        elif path.startswith("/echo") and path_type!="get":

            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}"
            if "gzip" in request_data[2]:
                response= f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}"
                if path_type == "get":
                    response= f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:] + gzip.compress(body))}\r\n\r\n{gzip.compress(body)}" 
            client.send(response.encode())

        elif path.startswith("/user-agent"):
            user_agent = request_data[2].split(": ")[1]
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}"
            client.send(response.encode())

        elif path.startswith("/files") and path_type == "get":
            directory = sys.argv[2]
            filename = path[7:]
            try:
                with open(f"/{directory}/{filename}", "r") as f:
                    body = f.read()
                response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body)}\r\n\r\n{body}"
                
            except Exception as e:
                response = f"HTTP/1.1 404 Not Found\r\n\r\n"
            client.send(response.encode())
        
        elif path.startswith("/files") and path_type == "post":
            directory = sys.argv[2]
            filename = path[7:]
            body_data = request_data[-1]
            with open(f"{directory}/{filename}", "w") as out:
                    out.write(body_data)
            response = "HTTP/1.1 201 Created\r\n\r\n"
            client.send(response.encode())
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
            client.send(response.encode())
        # print(response)
            
        client.close()

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client, addr = server_socket.accept()  # wait for client
        data = client.recv(4096)
        threading.Thread(target=handle_request, args=(client, data)).start()



if __name__ == "__main__":
    main()

