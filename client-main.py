import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, END
import socket
from threading import Thread
from http_helper import *

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
message_cast_option = tk.IntVar()
chosen_client = tk.StringVar()


def on_choosing_client():
    print(chosen_client.get())


def get_clients_from_server():
    client_socket.send(bytes(prepare_get_all_client_names(), "UTF-8"))


def on_message_cast_option():
    if message_cast_option.get() == 0:
        # 1-1
        print("1-1")
        get_clients_from_server()
    else:
        # 1-N
        print("1-N")


def exit_program():
    client_socket.close()
    client_window.destroy()


def send_1_1_message(destination, message):
    client_socket.send(bytes("{}:{}:{}".format("1-1", destination, message), "UTF-8"))


def send_1_N_message(msg):
    client_socket.send(bytes("{}:{}:{}".format("1-N", "ignore", msg), "UTF-8"))


def send_to_server():
    msg = msg_client_entered.get()
    global connected
    if not msg.strip() or msg == default_msg or not connected:
        msg_client_entered.set(default_msg)
    else:
        msg_client_entered.set("")
        global message_cast_option
        if message_cast_option.get() == 0:
            send_1_1_message(chosen_client.get(), msg)
        else:
            send_1_N_message(msg)
        print("Sent message {} to the server".format(msg))


def display_client_names(names):
    for index, name in enumerate(names):
        radio = ttk.Radiobutton(
            client_window,
            text=name,
            variable=chosen_client,
            command=on_choosing_client,
            value=name,
        )
        radio.grid(column=index, row=17, padx=10, pady=10)


def parse_incoming_message(msg):
    print(msg)
    tokens = msg.split(":")
    if tokens[0] == "get":
        display_client_names(tokens[1:])


def receive_from_server():
    try:
        while True:
            data_from_server = client_socket.recv(MAX_MESSAGE_SIZE)
            data_from_server = data_from_server.decode("UTF-8")
            if data_from_server:
                msg_area.insert(END, "\n" + data_from_server)
                parse_incoming_message(data_from_server)
            else:
                print("Closing this window as the server exited.")
                exit_program()
                break
    except OSError as e:
        print(e)


def connect_to_server():
    try:
        if not username.get():
            messagebox.showerror("Username invalid", "Empty username is invalid")
            return
        name_entered = username.get()
        global client_socket
        client_socket.connect((server_host, server_port))
        client_socket.sendall(bytes(prepare_post_client_name(name_entered), "UTF-8"))
        connection_status.config(text="Connected to server...")
        t = Thread(target=receive_from_server)
        t.daemon = True
        t.start()
        global connected
        connected = True
    except OSError:
        connected = False


def setup_client_window():
    client_window.title("Client UI")
    client_window.geometry("800x640")
    client_window.resizable(False, False)

    username_label = ttk.Label(client_window, text="Enter a username")
    username_label.grid(column=0, row=1, padx=30, pady=15)
    username_entry = ttk.Entry(client_window, width=32, textvariable=username)
    username_entry.grid(column=1, row=1, padx=30, pady=15)
    username_register = ttk.Button(
        client_window, text="Connect", command=connect_to_server
    )
    username_register.grid(column=2, row=1, padx=30, pady=15)

    connection_status.grid(column=1, row=2, padx=30, pady=15)

    msg_area.grid(column=1, row=5, padx=5, pady=5)

    msg_entry = ttk.Entry(client_window, width=32, textvariable=msg_client_entered)
    msg_entry.grid(column=1, row=25, padx=30, pady=15)
    msg_client_entered.set(default_msg)
    msg_send = ttk.Button(client_window, text="Send", command=send_to_server)
    msg_send.grid(column=2, row=25, padx=30, pady=15)

    exit_button = ttk.Button(client_window, text="Exit", command=exit_program)
    exit_button.grid(column=1, row=30, padx=10, pady=10)
    client_window.protocol("WM_DELETE_WINDOW", exit_program)

    message_cast_options = ["1:1", "1:N"]
    for index, option in enumerate(message_cast_options):
        radio = ttk.Radiobutton(
            client_window,
            text=option,
            variable=message_cast_option,
            command=on_message_cast_option,
            value=index,
        )
        radio.grid(column=index, row=13, padx=10, pady=10)


def main():
    try:
        setup_client_window()
        client_window.mainloop()
    except RuntimeError:
        print("Exiting...")


if __name__ == "__main__":
    main()
