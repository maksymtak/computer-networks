SERVER_HOST = '212.132.114.68'
SERVER_PORT = 5382
HOST = '127.0.0.1'
PORT = 5378
host_port = (HOST, PORT)
server_ = (SERVER_HOST, SERVER_PORT)
how_many_flags = 1
import time
import threading
# print('Welcome to Chat Client. Enter you login:')
divisor = '10001000000100011'
ack_char = '11111111' 
headers = ["DELIVERY", "SEND-OK", "LIST-OK", "BAD-RQST-BODY", "BAD-RQST-HDR", "SET-OK"]
character = "u"
seq_bit_len = 7
# crc_len = 16
wait_time_ack = 1
# frame_len = 32
name_self = ''
import random
import math
import socket


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

# def make_name(username): # ret req nr after name
#     encoded = username
#     print(crc_make(get_binary(username)))
#     encoded += int(crc_make(get_binary(username)), 2)
#     return encoded

def log_in():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logged = False
    while (not logged): # while username is not set
        username = input("Welcome to Chat Client. Enter your login:") # get name 

        if "!quit" in username:
            graceful_exit(sock)
        
        crcd_username = crc_make(username)#.strip(" /\!@#$%^") 

        string_bytes = (f'HELLO-FROM {crcd_username}\n').encode("utf-8")
        #print(string_bytes)
        send_string(string_bytes)
        #print("got through")
        data, addr = sock.recvfrom(1024) # get login response
        print(data)
        if not data:
            print("Socket is closed.")
            graceful_exit(sock)
        else:
            data = data.decode("utf-8")
            # print(f"Read data from socket: {data}")
            
            if 'HELLO' in data:
                x = data.split()
                x[1] = check_crc(x[1])
                print(f"Succesfully logged in as {x[1]}!")
                return sock
                
            else:
                sock.close() #buahahhahhaahah get reconnected
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                #sock.bind(host_port)
                bad_login_response(data, username, sock)
        

def send_message(terminal_input):
    
    terminal_input = terminal_input.strip("@") # get rid of the leading @ symbol
    x = terminal_input.split(" ", 1)
    string_bytes = f"{x[1]}"
    friend = get_chat(x[0])
    # if friend == None:
    #     friend = Chat(x[0])
    #     chats.append(friend)
    string_bytes = make_message(x[0], string_bytes, '0', friend.seq_self)
    string_bytes = (f"SEND {crc_make(x[0])} {string_bytes}\n").encode("utf-8")
    friend.add_pending(string_bytes)
    # print(string_bytes)
    send_string(string_bytes)


def send_ack(name, friend_seq):
    frame = make_message(name, get_char(ack_char), '1', friend_seq)
    send_string((f"SEND {crc_make(name)} {frame}\n").encode("utf-8"))


# do not use
# def whole_send(terminal_input, frame=None, person=None):
#     # if frame != None:
#     #     for frame_index in len(encoded_data)/frame_len:
#     #         frame_send(frame, person)
#     # else:
#     terminal_input = terminal_input.strip("@") # get rid of the leading @ symbol
#     x = terminal_input.split(" ", 1)
    
#     encoded_data = make_message(x[0], x[1], '0', bin(get_chat(x[0]).seq_self))
#     string_bytes = f"SEND {x[0]} {encoded_data}\n" 
#     person = get_chat(x[0])
#     person.add_pending(string_bytes)
        
#         #for frame_index in len(encoded_data)/frame_len:
#         #    frame_send(encoded_data[frame_index * frame_len: (frame_index+1) * frame_len])


def get_active_list(): # send user list request
    send_string("LIST\n").encode("utf-8") 
    # string_bytes = ("LIST\n").encode("utf-8") # encode it
    # bytes_len = len(string_bytes) 
    # num_bytes_to_send = bytes_len

    # while num_bytes_to_send > 0: # send the request
    #     num_bytes_to_send -= sock.send(string_bytes[bytes_len-num_bytes_to_send:])


def send_string(data):
    #print(data)
    # data = data.encode("utf-8")    
    sock.sendto(data, server_)
    # bytes_len = len(data) 
    # num_bytes_to_send = bytes_len
    # print(data)
    # while num_bytes_to_send > 0: # send the request
    #     num_bytes_to_send -= sock.sendto(data[bytes_len-num_bytes_to_send:], server_)



def set_params(terminal_input):
    split_input = terminal_input.split(" ", 2)
    string_bytes = (f"SET {split_input[1].upper()} {split_input[2]}\n").encode("utf-8")
    send_string(string_bytes)


def get_params(terminal_input):
    split_input = terminal_input.split(" ", 2)
    string_bytes = (f"SET {split_input[1].upper()}\n") 
    send_string(string_bytes)

def reset():
    send_string("RESET\n")
    

def get_input(sock, leave):
    while not leave:
        terminal_input = input("") # get input
        if terminal_input.startswith("@"):
            #whole_send(terminal_input)
            send_message(terminal_input)
        elif "!who" in terminal_input:
            get_active_list(sock)
        elif "!set" in terminal_input:
            set_params(terminal_input)
        elif "!get" in terminal_input:
            get_active_list(sock)
        elif "!reset" in terminal_input:
            reset()
        elif "!quit" in terminal_input:
            leave = True
            return
        else:
            print("say what now?")
            

def print_list(data):
    plist = data.split(",")
    plist[0] = plist[0].strip("LIST-OK ")
    for i in plist:
        i = check_crc(i)
        if i == None:
            get_active_list()
            return
    print(f"There are {len(plist)} online:")
    for i in plist:
        print(f"{i} \n")

def handle_response(sock, leave):
    while not leave:
        
        data, ad = sock.recvfrom(1024)
        data = data.decode("utf-8")

        # tail_recv = math.floor(crc_len / 8)!
        # while not ("\n" in data): # \n is the end of the message (might be dangerous)
        #     d, ad = sock.recvfrom(2)
        #     d = d.decode("utf-8")
        #     data+=d
        # for i in range(len(tail_recv)):
        #     d = sock.recv(1)
        #     d = d.decode("utf-8")
        #     data+=d

        #print(data)
        if data:
            divided_data = data.split(" ", 2) # into three parts hdr name data
            header = headers[find_header(divided_data[0])]
            #print("getting close")
            match header:
                case "DELIVERY":
                    print(f'got it!, {divided_data[1]}, {divided_data[2]}')
                    decode_message(divided_data[1], divided_data[2])
                case "LIST-OK":
                    print_list(divided_data[1])
                case "SEND-OK":
                    print("The message was sent succesfully")
                case "BAD-DEST-USER":
                    print("The destination user does not exist")
                case "BAD-RQST-HDR":
                    print("Error: Unknown issue in previous message header.")
                case "BAD-RQST-BODY":
                    print("Error: Unknown issue in previous message body.")
                case _:
                    print("whoops")
                    print(data)
            #if header == "DELIVERY": 
                
            #make rest of cases

            #if "DELIVERY" in data:
            #    prt_message(data)
            # elif "LIST-OK" in data:
            #     #print(data)
            #     print_list(data)
            # elif "SEND-OK" in data:
            #     print("The message was sent succesfully")
            # elif "BAD-DEST-USER" in data:
            #     print("The destination user does not exist")
            # elif "BAD-RQST-HDR" in data:
            #     print("Error: Unknown issue in previous message header.")
            # elif "BAD-RQST-BODY" in data:
            #     print("Error: Unknown issue in previous message body.")
            # else:
            #     print("whoops")
            #     print(data)
        else:
            print("Socket closed")
        

def logged_in(sock, leave): 
    # check server and handle inputs simultaneously
    thr = threading.Thread(target = handle_response, args = (sock,leave), daemon=True)
    thr.start()
    thr = threading.Thread(target = retransmittions, args = (leave,), daemon=True)
    thr.start()
    get_input(sock, leave)
    #thr.join()
    
    
#has to be the same socket after login

####################################### unstable client below

chats = []


def retransmittions(leave): #yucky
    while not leave:
        for person in chats:
            if (time.time() - person.pending_ack_time) > wait_time_ack and person.pending_ack_seq != -1:
                person.send_pending()
            #for seq, mess_time in person.pending_ack:
                # if (time.time() - mess_time[1]) > wait_time_ack:
                #     sock.sendto(mess_time[0], host_port)
                #     return

def get_chat(in_name, seq_nr = -1):
    for i in chats:
        #print(f'saved name: {i.name}, given name: {in_name}.')
        if i.name == in_name:
            #print("gottem good")
            return i
    
    person = Chat(in_name, seq_nr)
    chats.append(person)
    return person


def find_chat_seq(in_name):
    person = get_chat(in_name)
    if person != None:
        return person.seq
    
    chats.append(Chat(in_name))
    return chats[len(chats)].seq
    
# https://stackoverflow.com/questions/41752946/replacing-a-character-from-a-certain-index
def replace_str_index(text,index=0,replacement=''): 
    return f'{text[:index]}{replacement}{text[index+1:]}'

def shift_left(argument, offset): # bad i made a nicer one somewhere else
    for i in range(offset):
        argument += '0'
    return argument

def crc_main(argument):
    crc_len = len(divisor) - 1
    #argument << crc_len
    loop_count = 0
    min_val = pow(2, crc_len)
    while int(argument, 2) >= min_val:
        #print(f'{argument}, {int(argument,2)}, {min_val}')
        if argument[loop_count] == '1':
            for small_loop in range(crc_len + 1):
                xor_fl = False
                if argument[loop_count + small_loop] == '1':
                    xor_fl = not xor_fl 
                if divisor[small_loop] == '1':
                    xor_fl = not xor_fl 
                if xor_fl:
                    argument = replace_str_index(argument, loop_count + small_loop, "1")
                else:
                    argument = replace_str_index(argument, loop_count + small_loop, "0")
        loop_count += 1
    #crc_len = crc_len * -1
    #print(argument[-crc_len:])
    return argument[-crc_len:] # return only crc

def get_int_string_of_bits(argument):
    argument = int(argument, 2)
    argument = str(argument)
    chars = "abcdefghij"
    ret = ''
    for char in argument:
        ret += chars[int(char)]
    return ret
    # if len(ret) < 3: # could be better and should make this into a func
    #     zeroes = ["0"] * (3 - len(ret))
    #     zeroes.append(ret)
    #     #print(zeroes)
    #     ret = ''.join(zeroes)
    # return ret

def get_int_of_letters(arg):
    ret = ''
    for char in arg:
        ch = ord(char) - 97
        ret += str(ch)
    return int(ret)

def add_leading_zeroes(data, amount, leading_char):
    if len(data) < amount: # could be better and should make this into a func
        zeroes = [leading_char] * (amount - len(data))
        zeroes.append(data)
        #print(zeroes)
        data = ''.join(zeroes)
    return data


def crc_make(argument):
    working = shift_left(get_binary(argument), len(divisor)-1)
    #argument = get_char(argument)
    working = crc_main(working)
    #print(working)
    argument += add_leading_zeroes(get_int_string_of_bits(working), 5, 'a')
    return argument


def check_crc(argument): # also remove it from the string
    #print(f'{argument}.\n{argument[:-5]} {argument[-5:]}')
    data = get_binary(argument[:-5])
    crc = bin(get_int_of_letters(argument[-5:]))[2:]
    crc = add_leading_zeroes(crc, 16, '0')
    crc = crc_main(data + crc)

    if int(crc,2) == 0:
        return argument[:-5]
    return None


#tested
def icnrease_seqence_return_int(seq): 
    seq += 1
    if seq >= pow(2, seq_bit_len):
        seq = 0

    return seq

#tested
def int_to_bits(number, bit_len=0): # does not cut too big a number
    bits = bin(number)
    bits = bits[2:]
    cur_len = len(bits)

    if cur_len < bit_len:
        zeroes = ["0"] * (bit_len - cur_len)
        
        zeroes.append(bits)
        print(zeroes)
        bits = ''.join(zeroes)
        
    return bits
   
def get_binary(string):
    bits = ""
    for character in string:
        character = ord(character)
        character = bin(character)
        character = character[2:]
        if len(character) < 8:
            zeroes = ["0"] * (8 - len(character))
            zeroes.append(character)
            #print(zeroes)
            character = ''.join(zeroes)
        # character = character.replace('b', '')
        #print(character)
        bits += character
    #print(bits)
    return bits


def get_char(bits):
    string = ""
    # print(len(bits))
    # print((math.floor(len(bits)/8)))
    for bytes_index in range(math.floor(len(bits)/8)):
        byte = bits[bytes_index*8:(bytes_index+1)*8]
        character = int(byte, 2)
        character = chr(character)
        string += character
    return string

def make_message(name, data, ack_fl, seq_nr):
    
    friend = get_chat(name)

    #first = True
    #for character in data:
    frame = ''
    #frame += bin(seq_nr)[2:] #seq nr
    frame += int_to_bits(seq_nr)
    frame += ack_fl # ack flag
    
    # if friend.syn or ack_fl == '1': # synchronize flag
    #     frame += '0' # maybe should reverse
    # else:
    #     frame += '1'
    #print(f'frame: {frame}, {len(str(pow(2, seq_bit_len + how_many_flags)))}')
    frame = add_leading_zeroes(get_int_string_of_bits(frame), len(str(pow(2, seq_bit_len + how_many_flags))), 'a')
    frame += data #get_binary(data) # letter in bin
    frame = crc_make(frame) # add crc of the beginning and message
    #frame = get_char(frame)

    return frame


def decode_message(name, data):
    data = data[:-1] # remove \n and space
    #could be dangerous on edgecases
    #data = get_binary(data)
    # if len(get_binary(data)) <= seq_bit_len: # something is wrong with the message
    #     return
    #print(f'recieved {data}')
    
    data = check_crc(data) # check and remove crc
    #print(f'recieved1 {data}')
    if data != None: # if crc showed problems with mess
        #name = get_binary(name)
        name = check_crc(name)
        if name == None: # if crc showed problems with name
            return 
        friend = get_chat(name) # makes friend if not there yet
        #print(data[:len(str(pow(2, seq_bit_len + how_many_flags)))])
        
        seq_of_message = get_int_of_letters(data[:len(str(pow(2, seq_bit_len + how_many_flags)))])# take the seq of the mess 
        #print(f'recieved {data}')

        seq_of_message = int_to_bits(seq_of_message)
        #print(f'recieved3 {seq_of_message}')
        flags = seq_of_message[-1:]
        seq_of_message = seq_of_message[:-1]
        #print(f"seq letters = {seq_of_message}")
        
        # if friend == None: # not in dict so make new
        #     person = Chat(name)
        #     chats.append(person)
        #data = data[0:-len(divisor)+1]
        if flags[0] == "1": # ack flag
            friend.remove_pending(int(seq_of_message, 2))
            # friend.seq_self = icnrease_seqence_return_int(friend.seq_self)
            return
        else:
            
            if friend.seq_friend == -1: # syn flag
                friend.seq_friend = int(seq_of_message,2)
            #     # person = Chat(name, seq_of_message)
            #     # chats.append(person)
            #print(f'1. friend seq:{friend.seq_friend}, seq of message:{int(seq_of_message,2)}.')
            if int(seq_of_message,2) == friend.seq_friend:
                #print(f'2. friend seq:{friend.seq_friend}, seq of message:{int(seq_of_message,2)}.')
                send_ack(name, int(seq_of_message,2))
                friend.increase()
                data = data[len(str(pow(2, seq_bit_len + how_many_flags))):] # remove seq and flags for printing
                print(f"From {name}: {data}")
            else:
                send_ack(name, int(seq_of_message,2)) # send expected sequence number
            


def find_header(given_header):
    bitwise_distance = [0] * len(headers)
    for char_index in range(len(given_header)):
        for header_index in range(len(headers)):
            hder  = headers[header_index]
            if len(hder) <= char_index: # out of range
                bitwise_distance[header_index] += 8 # whole byte
            else:
                bin_given = get_binary(given_header[char_index])
                bin_proper = get_binary(hder[char_index])
                for bit_index in range(len(bin_given)):
                    if bin_given[bit_index] != bin_proper[bit_index]:
                        bitwise_distance[header_index] += 1
                    
    min_dist = 999999
    index_correctest = -1
    for header_index in range(len(bitwise_distance)):
        if bitwise_distance[header_index] < min_dist:
            index_correctest = header_index
            min_dist = bitwise_distance[header_index]
    
    for header_index in range(len(bitwise_distance)): # check if two are correctest
        if header_index != index_correctest:
            if bitwise_distance[header_index] == min_dist:
                return None
        
    #print(headers[index_correctest])
    if bitwise_distance[index_correctest] > 16:
        return None
    return index_correctest



# character = get_binary(character)
# print(character)
# print(crc_make(character))
# character += crc_make(character)
# print(character)

# print(check_crc(character))
# character = character[0:-len(divisor)+1] # remove crc
# print(character)

# character = get_char(character)
# print(character)


# print(get_char(ack_char))




class Chat:
    def __init__(self, name, seq_friend=-1):
        self.name = name
        self.seq_self = random.randint(0, pow(2, seq_bit_len) - 1)
        print(f"rng seq nr:{self.seq_self}")
        self.seq_friend = seq_friend
        self.syn = False # meaning not synchronized yet
        #self.pending_ack = {} # dictonary seq_nr:message ## maybe should have time to live
        self.pending_ack_seq = -1
        self.pending_ack_mess = b''
        self.pending_ack_time = time.time()
        
        #self.message_queue = {} # seq_nr:chars(s) from the frame
        #self.ordered_message = [None] * pow(2, seq_bit_len)
        #self.start_index = 0

    def increase(self):
        if self.seq_friend >= pow(2, seq_bit_len) - 1:
            self.seq_friend = 0
        else:
            self.seq_friend += 1

    # def expand_message(self, index_multiplier): # cheeky and may not work
    #    if len(self.ordered_message) < (pow(2, seq_bit_len) - 1) * index_multiplier:
    #         add = [None] * pow(2, seq_bit_len)
    #         self.ordered_message.append(add)
    #     return True
        
    # def add_to_queue(self, seq_nr, chars, flush=False):
    #     if seq_nr in self.message_queue:
    #         index_multiplier = 1
    #         relative_pos = (seq_nr + pow(2, seq_bit_len) - self.start_index) % pow(2, seq_bit_len) 
    #         while self.expand_message(index_multiplier) and self.ordered_message[relative_pos * index_multiplier] != None:
    #             index_multiplier +=1
    #         self.ordered_message[(index_multiplier * pow(2, seq_bit_len) + relative_pos)] = self.message_queue[relative_pos]
    #         del self.message_queue[relative_pos]
    #     if not flush:
    #         self.message_queue[seq_nr] = chars
                
    def send_pending(self):
        sock.sendto(self.pending_ack_mess, server_)
        self.pending_ack_time = time.time()
        #self.remove_pending(self.seq_self)
        
    def add_pending(self, message):
        #self.pending_ack[seq_nr] = (message, time.time())
        self.pending_ack_seq = self.seq_self
        self.pending_ack_mess = message
        print(f'pending seq = {self.pending_ack_seq}')
        self.pending_ack_time = time.time()

    #def get_top_pending(self): # ret seq_nr
        #return next(iter(self.pending_ack))
    
    def remove_pending(self, seq_nr):
        #del self.pending_ack[seq_nr]
        if seq_nr == self.pending_ack_seq:
            print("removed")
            self.pending_ack_seq = -1
            self.pending_ack_mess = ""
            self.seq_self = icnrease_seqence_return_int(self.seq_self)
        else:
            print(f"did not remove incoming = {seq_nr}, our = {self.pending_ack_seq}")
        #else: # not expected seq nr in ack can only mean that the newest message was not delivered
            #self.send_pending()
            #whole_send("",self.pending_ack_mess, self)




s = log_in()
leave = False
logged_in(s, leave)

