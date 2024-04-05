
import socket

SERVER_HOST = '212.132.114.68'
SERVER_PORT = 5378

print('Welcome to Chat Client. Enter you login:')
# Please put your code in this file



def bad_login_response(response):
    if 'BAD-RQST-BODY' in response:
        return "bad name"
    return "idk"



def log_in():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host_port = (SERVER_HOST, SERVER_PORT)
    sock.connect(host_port)
    logged = False
    isBusy = False
    while (not logged): # while username is not set
        username = input("enter a username") # get name 
        string_bytes = (f"HELLO-FROM {username} \n").encode("utf-8") # encode it
        bytes_len = len(string_bytes) 
        num_bytes_to_send = bytes_len
        while num_bytes_to_send > 0: # send the name
            num_bytes_to_send -= sock.send(string_bytes[bytes_len-num_bytes_to_send:])

        data = sock.recv(4096) # get login response
        if not data:
            print("Socket is closed.")
        else:
            data = data.decode("utf-8")
            print(f"Read data from socket: {data}")
            if 'HELLO' in data:
                return
            else:
                print(bad_login_response(data))



log_in()
print("living la vida loca")


