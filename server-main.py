import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import socket
from threading import Thread

# references: Python GUI cookbook
# https://docs.python.org/3/howto/sockets.html#creating-a-socket
# https://pymotw.com/3/select/
# https://docs.python.org/3/library/queue.html
# http://net-informations.com/python/net/thread.htm
# https://www.geeksforgeeks.org/socket-programming-multi-threading-python/
# https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170


server_window = tk.Tk()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host = "127.0.0.1"
server_port = 9999
connected_clients = []
client_labels = [None, None, None]
scr = None


def client_thread(client_sock, client_address, client_name):
    print("Started client handling thread for client {}".format(client_name))


def wait_for_new_clients():
    while True:
        server_socket.listen()
        print("Waiting for client request..")
        client_sock, client_address = server_socket.accept()
        data_on_sock = client_sock.recv(2048)
        data_on_sock = data_on_sock.decode()
        client_name = data_on_sock.split(":")[1]
        print(
            "Client {} connected with name{}".format(
                (client_sock, client_address), client_name
            )
        )
        global connected_clients
        connected_clients.append((client_sock, client_address, client_name))
        print("List of all connected_clients {}".format(connected_clients))
        client_labels[len(connected_clients) - 1]["text"] = client_name.strip()
        t = Thread(target=(client_thread(client_sock, client_address, client_name)))
        t.start()


def setup_server_socket():
    try:
        server_socket.bind((server_host, server_port))
        server_socket.setblocking(False)
        print("Server started")
    except OSError as e:
        print("An error occurred - please fix before relaunching " + str(e))
        raise e


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

    scroll_width = 70
    scroll_height = 10
    global scr
    scr = scrolledtext.ScrolledText(
        server_window, width=scroll_width, height=scroll_height, wrap=tk.WORD
    )
    scr.grid(column=0, columnspan=20, padx=10, pady=10)


def main():
    setup_server_window()
    setup_server_socket()
    t = Thread(target=wait_for_new_clients)
    t.start()
    server_window.mainloop()


if __name__ == "__main__":
    main()
