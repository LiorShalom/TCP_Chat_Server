#!/usr/bin/python3
import socket
import select
import threading


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

r = Fore.LIGHTRED_EX        # RED
g = Fore.LIGHTGREEN_EX      # GREEN
b = Fore.LIGHTCYAN_EX       # BLUE
p = Fore.LIGHTMAGENTA_EX    # PURPLE
y = Fore.LIGHTYELLOW_EX     # YELLOW

reset = Style.RESET_ALL     # RESET

# Use 'localhost' address or Local IPv4 address:
def choose_address():
    while True:
        try:
            print('Choose one of the following options:')
            print(f'[{g}1{reset}] > Use {g}localhost {reset}.  ({b}Test{reset} the chat server on your own machine)')
            print(f'[{g}2{reset}] > Use {g}Local IPv4 {reset}. (Connect others on the {b}same network{reset})')
            choice = input(f"> {b}")
            print(f'{reset}', end='\r')
            if choice == '1': # Localhost
                return '127.0.0.1'
            elif choice == '2': # Local IPv4
                return get_local_ip()
            elif choice == 'exit()':
                raise SystemExit
            else:
                print("Invalid input! Please try again...")
        except SystemExit:
            print(f"{reset}Sad to see you leaving...")
            exit()

# Get the local IP address of the device you running the server on:
import ipaddress

def get_local_ip():
    try:
        # Get the local IP address automatically:
        # Create a temporary UDP socket to get the desired IP address:
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # connect to a known IP address:
        temp_socket.connect(('8.8.8.8', 80))
        # To get the local IP address to which the temp socket is bound:
        local_ip = temp_socket.getsockname()[0]
        return local_ip
    except:
        # Get the IP address manually from the user:
        print(f"{r}[ERROR]{reset} I didn't managed to get your local IP address by myself.")
        print("I need your help. Check it manually.")

        while True:
            try:
                local_ip = input(f"Enter your local IP address: {g}")
                print(reset, end='\r') # Reset text color

                # Check if 'exit()':
                if local_ip == 'exit()':
                    raise SystemExit

                # Check if 'localhost':
                elif local_ip == 'localhost':
                    return local_ip

                # Check if valid:
                ipaddress.IPv4Address(local_ip)
                return local_ip

            except ipaddress.AddressValueError:
                print(f"{r}[INVALID]{reset} Please anter a valid IP address.")
            except SystemExit:
                print("Closing program...")
                exit()
                # break


print(F'{y}[SERVER]{reset}')
print(f'{p}------------------------------------------------------------------{reset}')

server_ip = choose_address()
server_port = 23791
print(f"{p}[KEEP IN MIND]{reset} To turn off the server type {r}'shutdown'{reset} at ANY TIME.")
print(f'{p}------------------------------------------------------------------{reset}')
print(f"{p}[IMPORTANT]{reset} The server is running with those details:")
print(f"[{g}HOST{reset}/{g}IP{reset}] > {b}{server_ip}{reset}\n[{g}PORT{reset}]    > {b}{server_port}{reset}")
# How to use:
print(f"{p}[INSTRUCTIONS]{reset} To connect to the server from your client program,\nuse the above {g}HOST{reset}/{g}IP{reset} and {g}PORT{reset} values.")
print(f'{p}------------------------------------------------------------------{reset}')

# Server address definition:
SERVER_ADDRESS = (server_ip, server_port)


# CLASS THAT HANDLES CLIENTS INFORMATION:
class Client_info:
    def __init__(self):
        # Dictionary to store client information:
        self.clients_info_dict = {}

    # This method is used to add client information to the 'clients_info_dict' dictionary:
    def sign_up_operation(self, name, user_name, password, client_socket):
        # Add client information to the dictionary with the 'client_socket' as a key:
        self.clients_info_dict[(user_name, password)] = (name, client_socket)
        print(f'{reset} - {b}[NEW]{reset} account was created!')

    # This method is used to check if the provided credentials match any of the stored client information:
    def log_in_operation(self, name, user_name, password, client_socket):
        if (user_name, password) in self.clients_info_dict and self.clients_info_dict[(user_name, password)] == (name, ''):
            self.clients_info_dict[(user_name, password)] = (name, client_socket)
            return True

        # If no match is found, it returns False:
        return False
    
    def client_exit(self, name, user_name, password, client_socket):
        # print(f"{r}exiting{reset}")
        if (user_name, password) in self.clients_info_dict and self.clients_info_dict[(user_name, password)] == (name, client_socket):
            self.clients_info_dict[(user_name, password)] = (name, '')


# SHUTDOWN SERVER SOCKET AND ALL CLIENTS CONNECTED:
def shutdown_server(clients_list, server_socket):
    while True:
        shut = input(f"{r}")
        if shut == 'shutdown':
            # Notify all the clients about the server shutdown:
            for client in clients_list:
                if client != server_socket:
                    try:
                        client.send(b'exit_server')
                    except ConnectionResetError:
                        pass
            break
        else:
            print(f"{r}!{reset}To turn off the server type {r}'shutdown'{reset}")
    # Close all client sockets and server socket:
    for client_socket in clients_list:
        try:
            client_socket.close()
        except OSError:
            continue

    server_socket.close()
    exit()


def main():
    # An instance of the Client_info class to manage the clients information.
    client_info = Client_info()

    # Define TCP server socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind server to address:
    server_socket.bind(SERVER_ADDRESS)
    
    # Set the server to Non-Blocking:
    server_socket.setblocking(False)

    # Listen for connections:
    server_socket.listen(20)
    print(f"\n{reset}The server is {g}[READY]{reset} And waiting to handle connections...")

    # List connected sockets:
    clients_list = [server_socket]

    # An option for the user to shutdown the server at any time:
    threading.Thread(target=shutdown_server, args=(clients_list, server_socket)).start()

    # The 'select' module gives the server the ability to handle multiple connections in a single thread.
    while clients_list:
        try:
            readable, _, _ = select.select(clients_list, [], [], 0.2)

            for sock in readable:
                # Accept client connections:   [SERVER]
                if sock == server_socket:
                    client_socket, client_address = server_socket.accept()

                    # Add client to list:
                    clients_list.append(client_socket)

                # Handle client communication: [CLIENTS]
                else:
                    try:
                        # RECEIEVE:
                        data = sock.recv(1024)
                        # Encode data into text:
                        text = data.decode('utf-8')

                        if text.startswith('[NEW]'):
                            _, option, name, user_name, password, private_sock = text.split(':', 6)
                            if option == 'signup':
                                # Add client info to dictionary:
                                client_info.sign_up_operation(name, user_name, password, sock)
                                sock.send(b"Account Created")

                                # exit
                                client_info.client_exit(name, user_name, password, sock)
                                clients_list.remove(sock)
                                sock.close()
                                break

                            elif option == 'login':
                                # Login details are correct:
                                if client_info.log_in_operation(name, user_name, password, sock):
                                    print(f"{g}[{reset} {client_address[0]}{g}:{reset}{client_address[1]} ] - [ {g}CONNECTED{reset}    ] - {b}{name}{reset}")
                                    sock.send(b'True')

                                    # SEND all connected clients an indication of new connected user:
                                    for client in clients_list:
                                        if client != sock and client != server_socket:
                                            client.send(f'[{b}{name}{reset} - {g}connected{reset} to the server!]'.encode('utf-8'))

                                # Login details are NOT correct:
                                else:
                                    # Details are 
                                    sock.send(b'False')
                                    clients_list.remove(sock)
                                    sock.close()
                                    break
                            else:
                                print("PROBLEM!")
                                exit()

                        elif text.startswith('[ACTIVE]'):
                            _, name, user_name, password, private_sock, message = text.split(':', 6)
                            # Check if client disconnceted:
                            if message == 'exit()':
                                print(f"{r}[{reset} {client_address[0]}{r}:{reset}{client_address[1]} ] - [ {r}DISCONNECTED{reset} ] - {b}{name}{reset}")
                                client_info.client_exit(name, user_name, password, sock)
                                # print(f'disconnected: {name} - {user_name} - {password}')

                                # SEND all connected clients an indication of the disconnected user:
                                for client in clients_list:
                                    if client != sock and client != server_socket:
                                        client.send(f'[{b}{name}{reset} - {r}disconnected{reset} from the server!]'.encode('utf-8'))

                                clients_list.remove(sock)
                                sock.close()
                                break


                            # BROADCAST ALL CLIENTS:
                            else:
                                for client in clients_list:
                                    if client != sock and client != server_socket:
                                        client.send(f'{message} - ({b}{name}{reset})'.encode('utf-8'))

                        elif text == ':REMOVE:':
                            clients_list.remove(sock)
                            sock.close()
                            break


                    except ConnectionResetError: # client disconnected:
                        print(f"{r}[{reset} {client_address[0]}{r}:{reset}{client_address[1]} ] - [ {r}DISCONNECTED{reset} ] - {b}{name}{reset}")
                        client_info.client_exit(name, user_name, password, sock)
                        clients_list.remove(sock)
                        sock.close()
                        break

        except ValueError:
            break
        except OSError:
            break

    
    


if __name__ == '__main__':
    main()