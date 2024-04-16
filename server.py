codSERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 5378


print('Server is on')
# Please put your code in this file

import socket
import threading
host_port = (codSERVER_ADDRESS, SERVER_PORT)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(host_port)
sock.listen()
#clients = []
clients = {} #empty dictionary 


def send_message(con, message):
    string_bytes = (f"{message}\n").encode("utf-8") # encode it
    
    bytes_len = len(string_bytes) 
    num_bytes_to_send = bytes_len
    
    while num_bytes_to_send > 0: # send the name
        num_bytes_to_send -= con.send(string_bytes[bytes_len-num_bytes_to_send:])


def at_capacity(con):
    send_message(con, "BUSY")
    con.close()

def connect_clients():
    while True:
        con, add = sock.accept()
        if len(clients) >= 16:
            thr = threading.Thread(target = at_capacity, args = (con,), daemon=True)
            thr.start()
        else:
            thr = threading.Thread(target = handle_client, args = (con,), daemon=True)
            thr.start()


def read_socket(con):
    data = con.recv(1)
    if not data:
        return data
    data = data.decode("utf-8")

    while not ("\n" in data):
        d = con.recv(1)
        d = d.decode("utf-8")
        data+=d
    
    return data


def check_name_syntax(name): #ugly :(
    if (' ' in name) or (',' in name):
        return False
    return True

def check_name(str, con): # True on good name and False on bad
    x = str.split(" ", 1)
    name = x[1]
    name = name.strip('\n') # delete the trailing newline

    #chars = r"!@#$%^&$, " #https://stackoverflow.com/questions/5188792/how-to-check-a-string-for-specific-characters
    if check_name_syntax(name): #any(c in name for c in chars):
        if name not in clients: #if the name is not taken yet
            clients[name]=con # add name:socket pair to clients 
            send_message(con, f"HELLO {name}")
            return True
        else:
            send_message(con, "IN-USE")
    else:
        send_message(con, "BAD-RQST-BODY")





def log_in(con):
    data = read_socket(con)
    while data:
        if "HELLO-FROM" in data:
            if check_name(data, con):
                return True
        else:
            send_message(con, "BAD-RQST-HDR")
        data = read_socket(con)

    return False

def find_key(con): # this is bad, just sad :(
    for name, soc in clients.items():
        if soc == con:
            return name
    return
 
def send_DM(sender, message): # sender socket, <name> <msg>
    x = message.split(" ", 1)
    x[1] = x[1].strip("\n")
    #print(f"{x[0]}, {x[1]}.")
    if len(x[1]) == 0:
        send_message(sender, "BAD-RQST-BODY")
        #print("closes/n")
    elif x[0] in clients:
        send_message(clients[x[0]], f'DELIVERY {find_key(sender)} {x[1]}')
        send_message(sender, "SEND-OK")
    else:
        send_message(sender, "BAD-DEST-USER")
        
def send_list(con):
    mess = "LIST-OK "
    for name, soc in clients.items():
        mess += f"{name},"

    mess = mess[:-1] # remove last comma
    send_message(con, mess)

            


def handle_input(con, data):
    x = data.split(" ", 1)
    command = x[0]

    
    match command:
        case "SEND":
            send_DM(con, x[1])
        case "LIST\n":
            send_list(con)
        case _:
            print(f"{command}.")




def handle_client(con):
    if not log_in(con):
        con.close()
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
    



# Assume the connect_clients function accepts incoming connections
# and returns all of them as a list.
