SERVER_HOST = '212.132.114.68'
SERVER_PORT = 5378
HOST = '127.0.0.1'
PORT = 5378
host_port = (HOST, PORT)
how_many_flags = 3
import time
import threading
print('Welcome to Chat Client. Enter you login:')
divisor = '1000100000010001'
ack_char = '11111111' 
character = "u"
seq_bit_len = 7
wait_time_ack = 0.05
frame_len = 32
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


    

def log_in():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
                print(f"Succesfully logged in as {x[1]}!")
                return sock
                
            else:
                sock.close() #buahahhahhaahah get reconnected
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.connect(host_port)
                bad_login_response(data, username, sock)
        

def send_message(terminal_input):
    
    terminal_input = terminal_input.strip("@") # get rid of the leading @ symbol
    x = terminal_input.split(" ", 1)

    string_bytes = f"SEND {x[0]} {x[1]}\n" # encode it
    string_bytes = make_message(x[0], string_bytes, '0', bin(get_chat(x[0]).seq))
    # print(string_bytes)
    bytes_len = len(string_bytes) 
    num_bytes_to_send = bytes_len
    while num_bytes_to_send > 0: # send the message
        num_bytes_to_send -= sock.send(string_bytes[bytes_len-num_bytes_to_send:])
def frame_send(frame, person):
    sock.sendto(get_char(frame), host_port)

def whole_send(terminal_input, frame=None, person=None):
    if frame != None:
        for frame_index in len(encoded_data)/frame_len:
            frame_send(frame, person)
    else:
        terminal_input = terminal_input.strip("@") # get rid of the leading @ symbol
        x = terminal_input.split(" ", 1)
        string_bytes = f"SEND {x[0]} {x[1]}\n" 
        encoded_data = make_message(x[0], string_bytes, '0', bin(get_chat(x[0]).seq))
        person = get_chat(x[0])
        for frame_index in len(encoded_data)/frame_len:
            frame_send(encoded_data[frame_index * frame_len: (frame_index+1) * frame_len])


def get_active_list(): # send user list request

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
            whole_send(terminal_input)
            #send_message(terminal_input, sock)
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
                #print(data)
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
    thr = threading.Thread(target = retransmittions, args = (leave,), daemon=True)
    thr.start()
    get_input(sock, leave)
    #thr.join()
    
    
# has to be the same socket after login
#s = log_in()
#leave = False
#logged_in(s, leave)


####################################### unstable client below

chats = []


def retransmittions(leave): #yucky
    while not leave:
        for person in chats:
            for seq, mess_time in person.pending_ack:
                if (time.time() - mess_time[1]) > wait_time_ack:
                    sock.sendto(mess_time[0], host_port)
                    return

def get_chat(in_name):
    for i in chats:
        if chats[i].name == in_name:
            return chats[i]
    return None


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
    return argument[-crc_len:] 

def crc_make(argument):
    argument = shift_left(argument, len(divisor)-1)
    return crc_main(argument)

def check_crc(argument): # also remove it from the string
    crc = crc_main(argument)
    argument = argument[-len(divisor):]
    if int(crc,2) == 0:
        return argument
    return None

#tested
def icnrease_seqence_return_str(seq, bit_len): 
    seq += 1
    if seq >= pow(2, seq_bit_len):
        seq = 0

    return int_to_bits(seq, bit_len)

#tested
def int_to_bits(number, bit_len): # does not cut too big a number
    bits = bin(number)
    bits = bits.replace('b', '')
    cur_len = len(bits)

    if cur_len < bit_len:
        zeroes = ["0"] * (bit_len - cur_len)
        
        zeroes.append(bits)
        print(zeroes)
        bits = ''.join(zeroes)
        
    return bits
   
   

def make_name(username, seq_nr=0): # ret req nr after name
    encoded = ''
    for char in username:
        frame = ''
        ones = ["1"] * how_many_flags
        frame += int_to_bits(seq_nr, seq_bit_len)


#now works with strings and not just single characters
def get_binary(string):
    bits = ""
    for character in string:
        character = ord(character)
        character = bin(character)
        character = character.replace('b', '')
        bits += character
    return bits

#now works with strings and not just single characters
def get_char(bits):
    string = ""
    for bytes_index in range(math.floor(len(bits)/8)):
        byte = bits[bytes_index*8:(bytes_index+1)*8]
        character = int(byte, 2)
        character = chr(character)
        string += character
    return string

def make_message(name, data, ack_fl, seq_nr):
    
    friend = get_chat(name)
    to_send = ''
    #first = True
    #for character in data:
    frame = ''
    frame += bin(friend.seq) #seq nr

    frame += ack_fl # ack flag

    if friend.syn: # synchronize flag
        frame += '0' # maybe should reverse
    else:
        frame += '1'

    #i dont this this is neccessary if we send whole message at once
    #if first: # first frame of the message
    #    frame += '1'
    #else:
    #    frame += '0'
    
    frame += get_binary(character) # letter in bin

    frame += crc_make(frame) # add crc

    friend.add_pending(friend.seq, frame)

    to_send += frame

    return to_send

def send_ack(name, friend_seq):
    make_message(name, ack_char, '1', friend_seq)


def decode_message(name, data):
    if check_crc():
        friend = get_chat(name)
        data = data[0:-len(divisor)+1]
        if data[seq_bit_len] == 1: # ack flag
            friend.remove_pending(data[:seq_bit_len]) # may be one off
            return None
        else:
            send_ack(name, data[:seq_bit_len])


character = get_binary(character)
print(character)
print(crc_make(character))
character += crc_make(character)
print(character)

print(check_crc(character))
character = character[0:-len(divisor)+1] # remove crc
print(character)

character = get_char(character)
print(character)


print(get_char(ack_char))



class Chat:
    def __init__(self, name):
        self.name = name
        self.seq = 0 #random.randint(0, pow(2, seq_bit_len) - 1)
        self.syn = False
        #self.pending_ack = {} # dictonary seq_nr:message ## maybe should have time to live
        self.pending_ack_seq = -1
        self.pending_ack_mess = ''
        self.pending_ack_time = time.time()
        
        self.message_queue = {} # seq_nr:chars(s) from the frame
        self.ordered_message = [None] * pow(2, seq_bit_len)
        self.start_index = 0

    def increase(self):
        if self.seq >= pow(2, seq_bit_len) - 1:
            self.seq = 0
        else:
            self.seq += 1

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
                
   
        
    def add_pending(self, seq_nr, message):
        #self.pending_ack[seq_nr] = (message, time.time())
        self.pending_ack_seq = seq_nr
        self.pending_ack_mess = message
        self.pending_ack_time = time.time()

    def get_top_pending(self): # ret seq_nr
        #return next(iter(self.pending_ack))
    
    def remove_pending(self, seq_nr):
        #del self.pending_ack[seq_nr]
        if seq_nr == self.pending_ack_seq:
            self.pending_ack_seq = -1
            self.pending_ack_mess = ""
        else:
            whole_send("",self.pending_ack_mess, self)

