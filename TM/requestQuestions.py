#TODO: THIS SHOULD BE AN IMPORT FROM THE TESTMANAGER


import socket

# TODO: replace with the hostname or IP address of the Java server
# TODO: replace with the port number on which the Java server is listening
SERVER_HOSTNAME = '180.150.80.41'
SERVER_PORT = 8000

# create a socket object and connect to the server
def request():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("hello")
        s.connect((SERVER_HOSTNAME, SERVER_PORT))
        print("Socket Connected")
        # send a string message to the server
        message = '22751096 requestQuestions'
        userID = 22751096
        s.sendall(message.encode())

        # receive data from the server
        data = s.recv(4096)
        fileName = 'storage/users/usersQuestions/' + str(userID) + '.json'
        # Save the data to a file
        with open(fileName, 'wb') as f:
            f.write(data)

        print('Received data saved to received_data.txt')

        # print the response received from the server
