import sys

codSERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 5378
#print(sys.argv)
#codSERVER_ADDRESS = sys.argv[2]
#SERVER_PORT = sys.argv[4]

print('Server is on')
# Please put your code in this file

import socket
import threading
host_port = (codSERVER_ADDRESS, int(SERVER_PORT))
sock = socket.socket()
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(host_port)
sock.listen()
#clients = []
clients = {} #empty dictionary takes key:value (or name:socket in this case) pairs

def funny_send(con, message):
    string_bytes = (f"{message}\n") # encode it
    
    #bytes_len = len(string_bytes) 
    #num_bytes_to_send = bytes_len
    for char in string_bytes:
        con.send(char.encode("utf-8"))
    

    
def send_message(con, message): #con (socket), mesage (string of wanted message)
    string_bytes = (f"{message}\n").encode("utf-8") # encode it
    
    bytes_len = len(string_bytes) 
    num_bytes_to_send = bytes_len
    
    while num_bytes_to_send > 0: # send the name
        num_bytes_to_send -= con.send(string_bytes[bytes_len-num_bytes_to_send:])


def at_capacity(con):
    send_message(con, "BUSY")
    con.close()

def connect_clients(): #idle checking for new connections
    while True:
        con, add = sock.accept()
        #print("hello mans") 
        if len(clients) >= 16:
            thr = threading.Thread(target = at_capacity, args = (con,), daemon=True)
            thr.start()
        else:
            thr = threading.Thread(target = handle_client, args = (con,), daemon=True)
            thr.start()
            


def read_socket(con): #read a newline terminating data from socket, 
                    #returns string of what was read or nothing if socket is closed
    data = con.recv(1)
    if not data:
        return data
    data = data.decode("utf-8")

    while not ("\n" in data):
        d = con.recv(1)
        d = d.decode("utf-8") #wonder if decoding everything after would be faster
        data+=d
    
    return data


def check_name_syntax(name): #check if forbidden chars in the input name
    if (' ' in name) or (',' in name) or ('\\' in name): #return false on invalid name, true on valid ones
        print("bad message")
        return False
    else:
        return True

def check_name(str, con): # True on good name and False on bad
    x = str.split(" ", 1) #split "hello-from" from <name>
    
    name = x[1]
    name = name.strip('\n') # delete the trailing newline
    print(f'name = {name}')
    if check_name_syntax(name): #if no forbidden chars
        if name not in clients: #if the name is not taken yet
            shake(name, con)
            return True
        else:
            send_message(con, "IN-USE")
    else:
        
        #send_message(con, "BAD-RQST-HDR")
        print("Error: Unknown issue in previous message body.") 
    return False


def shake(name, con):
    print("unfortunate demise")
    clients[name]=con # add name:socket pair to clients 
    send_message(con, f"HELLO {name}")
    
#########
#the problem is somewhere here?

def log_in(con): 
    data = read_socket(con)
    if data:
        if "HELLO-FROM" in data:
            if check_name(data, con):
                return True
            else:
                send_message(con, "BAD-RQST-BODY")
                #send_message(con, "BAD-RQST-HDR")
        else:
            send_message(con, "BAD-RQST-HDR")
            
            #print("BAD-RQST-HDR")
        
        #return False
    print("not cool dude")
    con.close()
    return False # only if the socket closed client-side

def find_key(con): # loop over dictionary to find name corresponding to given socket
    for name, soc in clients.items():
        if soc == con:
            return name
    return
 
def send_DM(sender, message): # sender socket, <name> <msg>
    x = message.split(" ", 1)
    x[1] = x[1].strip("\n")
    #print(f"{x[0]}, {x[1]}.")
    if len(x[1]) == 0: #if there is no message inputted
        send_message(sender, "BAD-RQST-BODY")
    elif x[0] in clients: #if valid destination client
        sender_name = find_key(sender)
        if sender_name:
            send_message(clients[x[0]], f'DELIVERY {sender_name} {x[1]}')
            send_message(sender, "SEND-OK")
    else:
        send_message(sender, "BAD-DEST-USER")
        
def send_list(con): #make and send active user list 
    mess = "LIST-OK "
    for name, soc in clients.items():
        mess += f"{name},"

    mess = mess[:-1] # remove last comma
    send_message(con, mess)
    

def handle_input(con, data): #
    x = data.split(" ", 1)
    command = x[0]

    match command: #i thought there were more commands when thinking of switch
        case "SEND":
            send_DM(con, x[1])
        case "LIST\n":
            send_list(con)
        case _:
            send_message(con, "BAD-RQST-HDR")
            print(f"{command}.")

def close_it(con):
    con.close()


def handle_client(con): # log in and loop reading from socket
    print("hi")
    if not log_in(con): # try to log in
        print("idk what is on")
        #close_it(con)
        return
    while True:
        data = read_socket(con)
        if data:
            handle_input(con, data)
        else:
            name = find_key(con)
            con.close()
            del clients[name] # remove from client list
            return
            

connect_clients()
    
