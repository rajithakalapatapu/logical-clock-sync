import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, END
import socket
from threading import Thread

MAX_MESSAGE_SIZE = 2048

server_host = "127.0.0.1"
server_port = 9999
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = False
client_window = tk.Tk()
username = tk.StringVar()
connection_status = ttk.Label(client_window, text="Not connected to server")
msg_client_entered = tk.StringVar()
scroll_width = 32
scroll_height = 15
msg_area = scrolledtext.ScrolledText(
    client_window, width=scroll_width, height=scroll_height, wrap=tk.WORD
)
default_msg = "Enter message here..."


def connect_to_server():
    try:
        if not username.get():
            messagebox.showerror("Username invalid", "Empty username is invalid")
            return
        name_entered = "name:" + username.get()
        client_socket.connect((server_host, server_port))
        client_socket.sendall(bytes(name_entered, "UTF-8"))
        connection_status.config(text="Connected to server...")
        t = Thread(target=receive_from_server)
        t.start()
        global connected
        connected = True
    except Exception as e:
        connected = False


def setup_client_window():
    client_window.title("Client UI")
    client_window.geometry("800x640")
    client_window.resizable(False, False)

    username_label = ttk.Label(client_window, text="Enter a username")
    username_label.grid(column=0, row=1, padx=30, pady=25)
    username_entry = ttk.Entry(client_window, width=32, textvariable=username)
    username_entry.grid(column=1, row=1, padx=30, pady=25)
    username_register = ttk.Button(
        client_window, text="Connect", command=connect_to_server
    )
    username_register.grid(column=2, row=1, padx=30, pady=25)

    connection_status.grid(column=1, row=3, padx=30, pady=25)

    msg_area.grid(column=1, row=10, padx=5, pady=5)

    msg_entry = ttk.Entry(client_window, width=32, textvariable=msg_client_entered)
    msg_entry.grid(column=1, row=20, padx=30, pady=25)
    msg_client_entered.set(default_msg)
    msg_send = ttk.Button(client_window, text="Send", command=send_to_server)
    msg_send.grid(column=2, row=20, padx=30, pady=25)


def send_to_server():
    msg = msg_client_entered.get()
    global connected
    if not msg.strip() or msg == default_msg or not connected:
        msg_client_entered.set(default_msg)
    else:
        msg_client_entered.set("")
        client_socket.send(bytes(msg, "UTF-8"))
        print("Sent message {} to the server".format(msg))


def receive_from_server():
    try:
        while True:
            data_from_server = client_socket.recv(MAX_MESSAGE_SIZE)
            data_from_server = data_from_server.decode("UTF-8")
            msg_area.insert(END, "\n" + data_from_server)
    except OSError as e:
        print(e)


msg_send = ttk.Button(client_window, text="Send", command=send_to_server)


def main():
    try:
        setup_client_window()
        client_window.mainloop()
    except RuntimeError as e:
        print("Exiting...")


if __name__ == "__main__":
    main()
