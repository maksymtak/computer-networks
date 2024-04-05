
import socket

SERVER_HOST = '212.132.114.68'
SERVER_PORT = 5378
host_port = (SERVER_HOST, SERVER_PORT)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print('Welcome to Chat Client. Enter you login:')
# Please put your code in this file



def bad_login_response(response, name):
    try:
        if 'BAD-RQST-BODY' in response:
            print(f"Cannot log in as {name}. That username contains disallowed characters.")
        elif 'BUSY' in response:
            print("Cannot log in. The server is full!")
    except OSError as msg:
        print(msg)
    



def log_in():
    
    sock.connect(host_port)
    logged = False
    while (not logged): # while username is not set
        username = input("") # get name 
        string_bytes = (f"HELLO-FROM {username} \n").encode("utf-8") # encode it
        print(string_bytes)
        bytes_len = len(string_bytes) 
        num_bytes_to_send = bytes_len
        while num_bytes_to_send > 0: # send the name
            num_bytes_to_send -= sock.send(string_bytes[bytes_len-num_bytes_to_send:])

        data = sock.recv(4096) # get login response
        if not data:
            print("Socket is closed.")
            

        else:
            data = data.decode("utf-8")
            # print(f"Read data from socket: {data}")
            if 'HELLO' in data:
                x = data.split()
                print(f"Successfully logged in as {x[1]}!")
                return
            else:
                bad_login_response(data, username)

def send_response(data):
    if "SEND-OK" in data:
        print("The message was sent succesfully")
    elif "BAD-DEST-USER" in data:
        print("The destination user does not exist")
    elif "DELIVERY" in data: # this is a biiiiig assumption but the only other return I got was when messaging myself
        prt_message(data)

def send_message(terminal_input):
    
    terminal_input = terminal_input.strip("@")
    x = terminal_input.split(" ", 1)

    string_bytes = (f"SEND {x[0]} {x[1]}\n").encode("utf-8") # encode it
    bytes_len = len(string_bytes) 
    num_bytes_to_send = bytes_len
    while num_bytes_to_send > 0: # send the name
        num_bytes_to_send -= sock.send(string_bytes[bytes_len-num_bytes_to_send:])

    data = sock.recv(4096) # get login response
    if not data:
        print("Socket is closed.")
        
    else:
        data = data.decode("utf-8")
        send_response(data)


    

def get_active_list():
    string_bytes = ("LIST\n").encode("utf-8") # encode it
    bytes_len = len(string_bytes) 
    num_bytes_to_send = bytes_len
    while num_bytes_to_send > 0: # send the request
        num_bytes_to_send -= sock.send(string_bytes[bytes_len-num_bytes_to_send:])

    data = sock.recv(4096) # get login response
    if not data:
        print("Socket is closed.")
    else:
        data = data.decode("utf-8")
        plist = data.split(",")
        plist[0] = plist[0].strip("LIST-OK ")
        print(f"There are {len(plist)} online:")

        for i in plist:
            print(f"- {i} \n")


def prt_message(message):
    x = message.split(" ", 2)
    print(f"From {x[1]}: {x[2]}")

    

def logged_in(): 
    terminal_input = input("") # get name 
    while not ("!quit" in terminal_input):
        if terminal_input.startswith("@"):
            send_message(terminal_input)
        elif "!who" in terminal_input:
            get_active_list()
            return # it craches after :((
            
        else:
            print("say what now?")
            exit()

        data = sock.recv(4096)
        data = data.decode("utf-8")
        if "DELIVERY" in data:
            prt_message(data)
        terminal_input = input("") # get input 
            

try:
    log_in()
    logged_in()
except OSError as msg:
    print(msg)




