import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import socket

client_window = tk.Tk()
username = tk.StringVar()
connection_status = ttk.Label(client_window, text="Not connected to server")
server_host = "127.0.0.1"
server_port = 9999
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def connect_to_server():
    if not username.get():
        messagebox.showerror("Username invalid", "Empty username is invalid")
        return
    name_entered = "name:" + username.get()
    client_socket.connect((server_host, server_port))
    client_socket.sendall(bytes(name_entered, "UTF-8"))
    connection_status.config(text="Connected to server...")


def setup_client_window():
    client_window.title("Client UI")
    client_window.geometry("800x640")
    client_window.resizable(False, False)

    username_label = ttk.Label(client_window, text="Enter a username")
    username_label.grid(column=10, row=10, padx=20, pady=40)
    username_entry = ttk.Entry(client_window, width=32, textvariable=username)
    username_entry.grid(column=60, row=10, padx=20, pady=40)
    username_register = ttk.Button(
        client_window, text="Connect", command=connect_to_server
    )
    username_register.grid(column=100, row=10, padx=20, pady=40)

    connection_status.grid(column=60, row=100, padx=20, pady=40)


def main():
    setup_client_window()
    client_window.mainloop()


if __name__ == "__main__":
    main()
