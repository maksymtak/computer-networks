
import socket
import threading


SERVER_HOST = '212.132.114.68'
SERVER_PORT = 5378
HOST = '127.0.0.1'
PORT = 5378
host_port = (HOST, PORT)



#print("Welcome to Chat Client. Enter your login:")
# Please put your code in this file


def graceful_exit(sock): # (not so) graceful exit
    print("goodbye")
    sock.close()
    exit()



def bad_login_response(response, name, sock):
    if 'BAD-RQST-BODY' in response:
        print(f"Cannot log in as {name}. That username contains disallowed characters.")
    elif 'BUSY' in response:
        print("Cannot log in. The server is full!")
        graceful_exit(sock)
    elif 'IN-USE' in response:
        print(f'Cannot log in as {name}. That username is already in use.')
    else:
        print(f'something went wrong {response}')




def log_in():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(host_port)
    logged = False
    while (not logged): # while username is not set
        username = input("Welcome to Chat Client. Enter your login:") # get name 

        if "!quit" in username:
            graceful_exit(sock)

        string_bytes = (f"HELLO-FROM {username}\n").encode("utf-8") # encode it
        
        bytes_len = len(string_bytes) 
        num_bytes_to_send = bytes_len
        
        while num_bytes_to_send > 0: # send the name
            num_bytes_to_send -= sock.send(string_bytes[bytes_len-num_bytes_to_send:])
            
        data = sock.recv(4096) # get login response
        print(data)
        if not data:
            print("Socket is closed.")
            graceful_exit(sock)
        else:
            data = data.decode("utf-8")
            # print(f"Read data from socket: {data}")
            
            if 'HELLO' in data:
                x = data.split()
                print(f"Successfully logged in as {x[1]}!")
                return sock
                
            else:
                sock.close() #buahahhahhaahah get reconnected
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(host_port)
                bad_login_response(data, username, sock)
        

def send_message(terminal_input, sock):
    terminal_input = terminal_input.strip("@") # get rid of the leading @ symbol
    x = terminal_input.split(" ", 1)

    string_bytes = (f"SEND {x[0]} {x[1]}\n").encode("utf-8") # encode it
    # print(string_bytes)
    bytes_len = len(string_bytes) 
    num_bytes_to_send = bytes_len
    while num_bytes_to_send > 0: # send the message
        num_bytes_to_send -= sock.send(string_bytes[bytes_len-num_bytes_to_send:])


def get_active_list(sock): # send user list request

    string_bytes = ("LIST\n").encode("utf-8") # encode it
    bytes_len = len(string_bytes) 
    num_bytes_to_send = bytes_len

    while num_bytes_to_send > 0: # send the request
        num_bytes_to_send -= sock.send(string_bytes[bytes_len-num_bytes_to_send:])



def prt_message(message): # print incoming message
    x = message.split(" ", 2) # split into three parts DELIVERY, <NAME>, <MESSAGE>
    print(f"From {x[1]}: {x[2]}")


def get_input(sock, leave):
    while not leave:
        terminal_input = input("") # get name and mess
        if terminal_input.startswith("@"):
            send_message(terminal_input, sock)
        elif "!who" in terminal_input:
            get_active_list(sock)
        elif "!quit" in terminal_input:
            leave = True
            return
        else:
            print("say what now?")
            

def print_list(data):
    plist = data.split(",")
    plist[0] = plist[0].strip("LIST-OK ")
    print(f"There are {len(plist)} online:")
    for i in plist:
        print(f"{i} \n")

def handle_response(sock, leave):
    while not leave:
        
        data = sock.recv(1)
        data = data.decode("utf-8")


        while not ("\n" in data):
            d = sock.recv(1)
            d = d.decode("utf-8")
            data+=d

        #print(data)
        if data:
            if "DELIVERY" in data:
                prt_message(data)
            elif "LIST-OK" in data:
                print(data)
                print_list(data)
            elif "SEND-OK" in data:
                print("The message was sent succesfully")
            elif "BAD-DEST-USER" in data:
                print("The destination user does not exist")
            elif "BAD-RQST-HDR" in data:
                print("Error: Unknown issue in previous message header.")
            elif "BAD-RQST-BODY" in data:
                print("Error: Unknown issue in previous message body.")
            else:
                print("whoops")
                print(data)
        else:
            print("Socket closed")
        

def logged_in(sock, leave): 
    # check server and handle inputs simultaneously
    thr = threading.Thread(target = handle_response, args = (sock,leave), daemon=True)
    thr.start()
    get_input(sock, leave)
    #thr.join()
    
    
# has to be the same socket after login
s = log_in()
leave = False
logged_in(s, leave)
