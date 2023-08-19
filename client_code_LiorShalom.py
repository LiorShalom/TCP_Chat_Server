#!/usr/bin/python3
import socket
import select
import threading
import os # Used the 'os.exit(0)' to force close of the entire program.


# To save time - ensure the 'colorama' module is installed:
import subprocess

def check_module(module_name):
    try:
        # Checks if the 'colorama' module is installed:
        __import__(module_name)
    except ImportError:
        # Installs the module:
        subprocess.check_call(['pip', 'install', module_name])

module_name = 'colorama'
check_module(module_name)

# COLORS:
from colorama import Fore, Style

r  = Fore.LIGHTRED_EX     # RED
g  = Fore.LIGHTGREEN_EX   # GREEN
b  = Fore.LIGHTCYAN_EX    # BLUE
p  = Fore.LIGHTMAGENTA_EX # PURPLE
y  = Fore.LIGHTYELLOW_EX  # YELLOW
Lb = Fore.LIGHTBLACK_EX   # GRAY 

reset = Style.RESET_ALL   # RESET

def configuration():
    print(f"{p}[ATTENSION]{reset} To make the connection happen, I need some details:")

    # Get the servers IP ADDRESS manually from the user:
    import ipaddress

    while True:
        try:
            server_ip = input(f"[{b}Server{reset} {g}HOST{reset}/{g}IP{reset}] > {b}")
            print(reset, end='\r') # Reset color

            # Check if 'exit()':
            if server_ip == 'exit()':
                raise SystemExit

            # Check if 'localhost':
            elif server_ip == 'localhost':
                break

            # Check if valid:
            ipaddress.IPv4Address(server_ip)
            break

        except ipaddress.AddressValueError:
            print(f"{r}[INVALID]{reset} Please anter a valid IP address.")
        except SystemExit:
            print("Closing program...")
            exit()

    # Get the servers PORT manually from the user:
    while True:
        try:
            server_port = input(f"[{b}Server{reset} {g}PORT{reset}]    > {b}")
            print(reset, end='\r') # Reset color

            # First check on input:
            if server_port == 'exit()':
                raise SystemExit
            elif server_port.isdigit():
                server_port = int(server_port)

            # Check port validation:
            if 0 < int(server_port) < 65535:
                break
            else:
                print(f"{r}[INVALID]{reset} Port number is not valid.")
        
        except ValueError:
            print(f"{r}[INVALID]{reset} Invalid input. Try again.")
        except SystemExit:
            print("Closing program...")
            exit()
    


    # Connection details (server address):
    return (server_ip, server_port)

print(F'{y}[CLIENT]{reset}')
print(f"{p}[KEEP IN MIND]{reset} To exit the program type {r}'exit()'{reset} at ANY TIME.")
print(f'{p}------------------------------------------------------------------{reset}')
while True:
    try:
        SERVER_ADDRESS = configuration()
        client_socket_check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client_socket_check.connect(SERVER_ADDRESS)
        client_socket_check.send(':REMOVE:'.encode('utf-8'))
        
        client_socket_check.shutdown(socket.SHUT_RDWR)
        client_socket_check.close()
        print(f'{p}------------------------------------------------------------------{reset}')
        break
    except (ConnectionRefusedError, OSError):
        print(f"{r}[ERROR]{reset} Server is closed or the details are not correct.")



# RECEIVE:
def receive_data(client_socket):
    while True:
        try:
            # Receive encoded data from the user:
            data = client_socket.recv(1024)
            # Checks if there is no data - server closed the conncetion:
            if not data:
                print(f"{reset}[ {r}SERVER DISCONNECTED{reset} ]")
                break
            
            # Decode the data into a readable text:
            message = data.decode('utf-8')

            # Check if the message is 'exit_server'. if so, the server is shuting down.
            if message == 'exit_server':
                print(f"{reset}[ {r}SERVER IS SHUTTING DOWN{reset} ] - Disconnecting...")
                # Fore exit the entire program:
                os._exit(0)
                break

            # print received message:
            print(f"{message}")
        except (ConnectionAbortedError, ConnectionResetError):
            break

    client_socket.close()

# SEND:
def send_data(name, user_name, password, client_socket):
    while True:
        # Wait for input from the user:
        print(f"{Lb}>", end='\r')
        message = input(f"{reset}")
        if ':' in message:
            print("The use of ':' is not allowed!")
            continue
        elif message == '' or message == None:
            continue

        # Encode the message in order to send the binary data to the server:
        complete_message = f'[ACTIVE]:{name}:{user_name}:{password}:{client_socket}:{message}'
        data = complete_message.encode('utf-8')

        # Send the message to the server:
        client_socket.send(data)

        # Checks if the text message is 'exit' to close client:
        if message == 'exit()':
            print("Disconnected.")
            client_socket.close()

            # Force exit the entire program:
            os._exit(0)
            break

# SIGN-UP
def sign_up():
    try:
        while True:
            print(f'- {p}SIGN-UP{reset} -')
            # Define client:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # ENTER:
            # NAME:
            name = input(f"{reset}Enter your {g}name{reset}: {b}")
            print(f'{reset}', end='\r')
            if name == 'exit()':
                raise SystemExit
            elif ':' in name:
                print(f"{r}[INVALID]{reset} Invalid details.\nTry again...")
                continue

            # USER-NAME
            user_name = input(F"{reset}Create a {g}user name{reset}: {b}")
            print(f'{reset}', end='\r')
            if user_name == 'exit()':
                raise SystemExit
            elif ':' in user_name:
                print(f"{r}[INVALID]{reset} Invalid details.\nTry again...")
                continue
            elif len(user_name) < 4:
                print(f"{r}[INVALID]{reset} User-Name is too short! Must contain at least 4 letters.\nTry again...")
                continue
            
            # PASSWORD:
            while True:
                while True:
                    password = input(f"{reset}Create a strong {g}password{reset}: {b}")
                    print(f'{reset}', end='\r')
                    if password == 'exit()':
                        raise SystemExit
                    if ':' in password:
                        print(f"{r}[INVALID]{reset} Invalid details.\nTry again...")
                        continue
                    elif len(password) < 5:
                        print(f"{r}[INVALID]{reset} Password must contain at least 5 digits.")
                        continue
                    break

                # CONFIRM PASSWORD:
                confirm_pass = input(f"{g}Confirm{reset} your password: {b}")
                print(f'{reset}', end='\r')
                if confirm_pass == 'exit()':
                    raise SystemExit
                elif ':' in password or ':' in confirm_pass:
                    print(f"{r}[INVALID]{reset} Invalid details.\nTry again...")
                    continue

                # CHECK:
                if confirm_pass != password:
                    print(f"{r}[INVALID]{reset}The passwords are not the same.\nTry again...")
                    continue

                # If passwords match:
                else:
                    break

            

            # SEND NEW CLIENT DATA TO SERVER:
            print(f"{r}[{reset} Creating account...       ]", end='\r')
            # Send new details to server
            sign_up_data = f'[NEW]:signup:{name}:{user_name}:{password}:{client_socket}'

            print(f"{r}[{reset} Sending data to server... ]", end='\r')
            # Add client information to the client:
            client_socket.connect(SERVER_ADDRESS)
            client_socket.send(sign_up_data.encode('utf-8'))
            
            created = client_socket.recv(1024).decode('utf-8')
            if not created:
                print(f"{r}[ERROR]{reset} An error occurred! Account not created.")
                raise SystemExit
            else:
                print(f"{g}[ ACCOUNT CREATED!          ]{reset}")
                client_socket.close()
                return True

    except SystemExit:
        return False
            

# LOG-IN
def log_in():
    try:
        while True:
            print(f'- {p}LOG-IN{reset} -')
            # Define client:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # ENTER:
            # NAME:
            name = input(f"{reset}Enter your {g}name{reset}: {b}")
            print(f'{reset}', end='\r')
            if name == 'exit()':
                raise SystemExit

            # USER-NAME
            user_name = input(f"{reset}Enter your {g}user name{reset}: {b}")
            print(f'{reset}', end='\r')
            if user_name == 'exit()':
                raise SystemExit

            # PASSWORD:
            password = input(f"Enter your {g}password{reset}: {b}")
            print(f'{reset}', end='\r')
            if password == 'exit()':
                raise SystemExit
            
            # CHECK:
            if ':' in name or ':' in user_name or ':' in password:
                print(f"{r}[INVALID]{reset} Invalid details.\nTry again...")
                continue

            print(f"{r}[{reset} Checking login data...    ]", end='\r')
            # Check details at server database:
            log_in_data = f'[NEW]:login:{name}:{user_name}:{password}:{client_socket}'

            print(f"{r}[{reset} Sending data to server... ]", end='\r')
            # Add client information to the client:
            client_socket.connect(SERVER_ADDRESS)
            client_socket.send(log_in_data.encode('utf-8'))

            log_in_success = client_socket.recv(1024).decode('utf-8')
            
            if log_in_success == 'True':
                print(f"{g}[ CONNECTED successfully!   ]{reset}")
                print('\n-------------------------------------------------------------')
                print(f"{reset}Good to see you {g}{name.capitalize()}{reset}!                                  ")
                return name, user_name, password, client_socket

            elif log_in_success == 'False':
                print("                                                           ", end='\r')
                print(f"{r}ERROR!{reset}")
                print("Make sure that the account is not in use on another device and the details you've entered are correct.")
                client_socket.close()
                continue

    except SystemExit:
        name = False
        user_name = False
        password = False
        client_socket = False
        return name, user_name, password, client_socket
        


# WELCOME:
def welcome():
    try:
        print(f'\n{b}WELCOME! To the - CHAT SERVER OF ALL TIME!{reset}')
        print(f'{p}[ATTENSION]{reset} By default, there are no existing accounts.')
        
        while True:
            print('Choose one of the following options:')
            print(f'[{g}1{reset}] >{g} Sign Up {reset}to create a new account')
            print(f'[{g}2{reset}] >{g} Log In {reset}to an existing account')
            choice = input(f"> {b}")
            print(f'{reset}', end='\r')
            if choice == '1': # sign up
                client_socket = sign_up()
                if not client_socket:
                    raise SystemExit

            elif choice == '2': # log in
                name, user_name, password, client_socket = log_in()
                if not client_socket:
                    raise SystemExit
                return name, user_name, password, client_socket

            elif choice == 'exit()':
                raise SystemExit

            else:
                print("Invalid input! Please try again...")

    except SystemExit:
        name = False
        user_name = False
        password = False
        client_socket = False
        return name, user_name, password, client_socket

def main(): # The socket definition and the first steps of the connection are in the log_in and sign_up functions.
    try:
        # Welcome / log_in / sign_up:
        name, user_name, password, client_socket = welcome()
        if client_socket == False:
            raise SystemExit
        # CREATE thread for each operation to handle both at same time:
        _recv = threading.Thread(target=(receive_data), args=(client_socket,))
        _send = threading.Thread(target=(send_data), args=(name, user_name, password, client_socket))
        # START the threading:
        _recv.start()
        _send.start()
        # WAIT for both threading to complete:
        _send.join()
        _recv.join()
        # CLOSE:
        client_socket.close()
    except SystemExit:
        print("Exit program...")
        exit()

if __name__ == '__main__':
    main()


