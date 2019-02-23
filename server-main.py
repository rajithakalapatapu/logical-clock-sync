import tkinter as tk
from tkinter import ttk, scrolledtext, END
import socket
from threading import Thread
import selectors
from http_helper import *
import pprint

pp = pprint.PrettyPrinter(indent=4)
# references: Python GUI cookbook
# https://docs.python.org/3/howto/sockets.html#creating-a-socket
# https://pymotw.com/3/select/
# https://pymotw.com/3/selectors/
# https://docs.python.org/3/library/queue.html
# http://net-informations.com/python/net/thread.htm
# https://www.geeksforgeeks.org/socket-programming-multi-threading-python/
# https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170


server_window = tk.Tk()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected_clients = {}
client_labels = [None, None, None]
scroll_width = 70
scroll_height = 10
scr = scrolledtext.ScrolledText(
    server_window, width=scroll_width, height=scroll_height, wrap=tk.WORD
)
def_selector = selectors.DefaultSelector()


def get_address_from_name(name):
    for address, client in connected_clients.items():
        if client[2] == name:
            return address


def parse_data_from_client(client_address, data_from_client):
    mode, destination, message = extract_message_details(
        data_from_client.split("\n")[6]
    )
    print("Message {} destined to {} via mode {}".format(message, destination, mode))

    response_message = prepare_send_message_response(
        mode, connected_clients[client_address][2], message
    )

    if mode == "1-1":
        print(
            "{} Sending message to {}".format(
                "*" * 8, connected_clients[get_address_from_name(destination)]
            )
        )
        connected_clients[get_address_from_name(destination)][0].sendall(
            bytes(response_message, "UTF-8")
        )
    elif mode == "1-N":
        print("{} Sending message to all clients".format("*" * 8))
        for address, client in connected_clients.items():
            client[0].sendall(bytes(response_message, "UTF-8"))
    elif mode == "get":
        pass


def read_from_client(client_connection, event_mask):
    print(
        "{} Client activity on {} with event mask {}".format(
            "*" * 4, client_connection, event_mask
        )
    )

    client_address = client_connection.getpeername()
    data_from_client = client_connection.recv(MAX_MESSAGE_SIZE).decode("UTF-8")
    if data_from_client:
        print("\t Received '{}' from '{}'".format(data_from_client, client_address))
        scr.insert(END, "{}: \t {}\n".format(client_address, data_from_client))
        scr.see(END)
        if REGISTER_CLIENT_NAME in data_from_client:
            register_client_name(client_connection, client_address, data_from_client)
        elif GET_ALL_CLIENTS in data_from_client:
            names = [GET_ALL_CLIENTS]
            for address, client in connected_clients.items():
                names.append(client[2])
            connected_clients[client_address][0].sendall(
                bytes(prepare_get_all_client_names_response(names), "UTF-8")
            )
        else:
            parse_data_from_client(client_address, data_from_client)
    else:
        print("Closing socket to {}".format(client_connection))
        unregister_client_name(client_connection)


def unregister_client_name(client_connection):
    def_selector.unregister(client_connection)
    client_address = client_connection.getpeername()
    del connected_clients[client_address]
    update_client_labels(connected_clients)
    client_connection.close()


def update_client_labels(clients):
    for i in range(len(client_labels)):
        client_labels[i]["text"] = ""
    index = 0
    for name, client in clients.items():
        client_labels[index]["text"] = client[2].strip()
        index += 1


def register_client_name(client_sock, client_address, data_str):
    client_name = extract_client_name(data_str)
    print(
        "Client {} connected with name {}".format(
            (client_sock, client_address), client_name
        )
    )
    global connected_clients
    connected_clients[client_address] = (client_sock, client_address, client_name)
    print("List of all connected_clients")
    pp.pprint(connected_clients)
    update_client_labels(connected_clients)
    sent = connected_clients[client_address][0].send(
        bytes(prepare_post_client_name_response(), "UTF-8")
    )
    print("Client registered name {} Sent 200 OK in {} bytes".format(client_name, sent))


def accept_new_client(server, event_mask):
    print(
        "A new client {} with event mask {} is connecting...".format(server, event_mask)
    )
    client_sock, client_address = server.accept()
    client_sock.setblocking(False)

    def_selector.register(client_sock, selectors.EVENT_READ, read_from_client)


def run_select_thread():
    while True:
        for key, mask in def_selector.select(timeout=None):
            key.data(key.fileobj, mask)


def setup_server_socket():
    try:
        server_socket.setblocking(False)
        server_socket.bind((server_host, server_port))
        server_socket.listen(5)
        def_selector.register(server_socket, selectors.EVENT_READ, accept_new_client)
        print("Server started...")
        select_loop = Thread(target=run_select_thread)
        select_loop.daemon = True
        select_loop.start()

    except OSError as e:
        print("An error occurred {}. \n".format(str(e)))
        print("Please fix before relaunching.")
        import sys

        sys.exit(1)


def exit_program():
    print("Existing clients are {}".format(connected_clients))
    for name, client in connected_clients.items():
        print("Closing connection to client {}".format(name))
        def_selector.unregister(client[0])
        client[0].close()
    server_window.destroy()


def setup_server_window():
    server_window.title("Server UI")
    server_window.geometry("800x640")
    server_window.resizable(False, False)

    label_frame = ttk.LabelFrame(server_window, text="List of active clients")
    label_frame.grid(column=0, row=0, padx=320, pady=100)
    global client_labels
    for i in range(len(client_labels)):
        client_labels[i] = ttk.Label(label_frame)
        client_labels[i].grid(column=0, row=i)
    for child in label_frame.winfo_children():
        child.grid_configure(padx=8, pady=4)

    scr.grid(column=0, columnspan=20, padx=10, pady=10)

    exit_button = ttk.Button(server_window, text="Exit", command=exit_program)
    exit_button.grid(column=0, columnspan=2, padx=10, pady=10)
    server_window.protocol("WM_DELETE_WINDOW", exit_program)


def main():
    setup_server_window()
    setup_server_socket()
    server_window.mainloop()


if __name__ == "__main__":
    main()
