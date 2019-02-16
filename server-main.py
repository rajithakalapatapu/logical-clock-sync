import tkinter as tk
from tkinter import ttk, scrolledtext, END
import socket
from threading import Thread
import selectors

# references: Python GUI cookbook
# https://docs.python.org/3/howto/sockets.html#creating-a-socket
# https://pymotw.com/3/select/
# https://docs.python.org/3/library/queue.html
# http://net-informations.com/python/net/thread.htm
# https://www.geeksforgeeks.org/socket-programming-multi-threading-python/
# https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
MAX_MESSAGE_SIZE = 2048

server_window = tk.Tk()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host = "127.0.0.1"
server_port = 9999
connected_clients = []
client_labels = [None, None, None]
scroll_width = 70
scroll_height = 10
scr = scrolledtext.ScrolledText(
    server_window, width=scroll_width, height=scroll_height, wrap=tk.WORD
)
def_selector = selectors.DefaultSelector()


def read_from_client(client_connection, event_mask):
    print(
        "Client activity on {} with event mask {}".format(client_connection, event_mask)
    )
    client_address = client_connection.getpeername()
    data_from_client = client_connection.recv(MAX_MESSAGE_SIZE)
    if data_from_client:
        print("Received {} from {}".format(data_from_client, client_address))
        scr.insert(END, "\n" + data_from_client.decode("UTF-8"))
    else:
        def_selector.unregister(client_connection)
        client_connection.close()


def show_client_name(client_sock, client_address, data_bytes):
    data_bytes = data_bytes.decode("UTF-8")
    client_name = data_bytes.split(":")[1]
    print(
        "Client {} connected with name{}".format(
            (client_sock, client_address), client_name
        )
    )
    global connected_clients
    connected_clients.append((client_sock, client_address, client_name))
    print("List of all connected_clients {}".format(connected_clients))
    client_labels[len(connected_clients) - 1]["text"] = client_name.strip()


def accept_new_client(server, event_mask):
    print(
        "A new client {} with event mask {} is connecting...".format(server, event_mask)
    )
    client_sock, client_address = server.accept()
    client_sock.setblocking(False)
    show_client_name(client_sock, client_address, client_sock.recv(2048))
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
        select_loop.start()

    except OSError as e:
        print("An error occurred {str(e)}. \n")
        print("Please fix before relaunching.")
        import sys

        sys.exit(1)


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


def main():
    setup_server_window()
    setup_server_socket()
    server_window.mainloop()


if __name__ == "__main__":
    main()
