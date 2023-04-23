import socket

# replace with the hostname or IP address of the Java server
SERVER_HOSTNAME = '192.168.0.9'
SERVER_PORT = 8000  # replace with the port number on which the Java server is listening

# create a socket object and connect to the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print("hello")
    s.connect((SERVER_HOSTNAME, SERVER_PORT))
    print("Socket Connected")
    # send a string message to the server
    message = '01 requestQuestions'
    s.sendall(message.encode())

    # receive data from the server
    data = s.recv(1024)

# print the response received from the server
print('Received:', repr(data.decode()))
