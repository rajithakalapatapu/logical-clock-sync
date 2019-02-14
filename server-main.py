import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import socket


# references: Python GUI cookbook
server_window = tk.Tk()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host = "127.0.0.1"
server_port = 9999


def main():
    setup_server_window()
    # TODO: server_window.mainloop()
    setup_server_socket()


def setup_server_socket():
    server_socket.bind((server_host, server_port))
    server_socket.listen(1)
    print("Server started")
    print("Waiting for client request..")
    clientsock, clientAddress = server_socket.accept()
    data = clientsock.recv(2048)
    data = data.decode()
    print("Client connected {}".format(data))


def setup_server_window():
    server_window.title("Server UI")
    server_window.geometry("800x640")
    server_window.resizable(False, False)

    label_frame = ttk.LabelFrame(server_window, text="List of active clients")
    label_frame.grid(column=0, row=0, padx=320, pady=100)
    ttk.Label(label_frame).grid(column=0, row=0)
    ttk.Label(label_frame).grid(column=0, row=1)
    ttk.Label(label_frame).grid(column=0, row=2)
    for child in label_frame.winfo_children():
        child.grid_configure(padx=8, pady=4)

    scroll_width = 70
    scroll_height = 10
    scr = scrolledtext.ScrolledText(
        server_window, width=scroll_width, height=scroll_height, wrap=tk.WORD
    )
    scr.grid(column=0, columnspan=20, padx=10, pady=10)


if __name__ == "__main__":
    main()
