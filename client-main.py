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
    print("Chose to send 1-1 to client {}".format(chosen_client.get()))


def get_clients_from_server():
    client_socket.send(bytes(prepare_get_all_client_names_request(), "UTF-8"))


def on_message_cast_option():
    if message_cast_option.get() == 0:
        # 1-1
        print("{} Client intends to send a 1-1 message - get client names".format("*"*4))
        get_clients_from_server()
    else:
        # 1-N
        print("{} Client intends to send a 1-N message".format("*"*4))



def exit_program():
    client_socket.close()
    client_window.destroy()


def send_one_to_one_message(destination, message):
    body = {"mode": "1-1", "destination": destination, "message": message}
    import json

    client_socket.send(
        bytes(prepare_http_msg_request("POST", SEND_MESSAGE, json.dumps(body)), "UTF-8")
    )


def send_one_to_n_message(msg):
    body = {"mode": "1-N", "message": msg}
    import json

    client_socket.send(
        bytes(prepare_http_msg_request("POST", SEND_MESSAGE, json.dumps(body)), "UTF-8")
    )


def send_to_server():
    msg = msg_client_entered.get()
    global connected
    if not msg.strip() or msg == default_msg or not connected:
        msg_client_entered.set(default_msg)
    else:
        msg_client_entered.set("")
        global message_cast_option
        if message_cast_option.get() == 0:
            send_one_to_one_message(chosen_client.get(), msg)
        else:
            send_one_to_n_message(msg)
        print("{} Sent message {} to the server".format("*"*4, msg))


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


def parse_connection_request_response(msg):
    if "200 OK" in msg:
        global connected
        connected = True
        connection_status.config(text="Connected to server...")
    else:
        # connection failed
        print("Try connecting again...")


def display_incoming_message(msg):
    if "200 OK in msg":
        import json

        mode, source, message = extract_message_details(json.loads(msg.split("\n")[2]))
        display_msg = "{} sent a {}: \n {}".format(source, mode, message)
        msg_area.insert(END, "\n" + display_msg)
        msg_area.see(END)
    else:
        print("Sending message failed {}".format(msg))


def parse_incoming_message(msg):
    print("Received {} from server".format(msg))
    if GET_ALL_CLIENTS in msg:
        display_client_names(parse_client_name_response(msg)[1:])
    elif REGISTER_CLIENT_NAME in msg:
        parse_connection_request_response(msg)
    elif SEND_MESSAGE in msg:
        display_incoming_message(msg)
    else:
        print("An unsupported operation happened! {}".format(msg))


def receive_from_server():
    try:
        while True:
            data_from_server = client_socket.recv(MAX_MESSAGE_SIZE)
            data_from_server = data_from_server.decode("UTF-8")
            if data_from_server:
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
            messagebox.showerror("Username invalid", "Enter a non-empty username")
            return
        name_entered = username.get()
        global client_socket
        client_socket.connect((server_host, server_port))
        client_socket.sendall(
            bytes(prepare_post_client_name_request(name_entered), "UTF-8")
        )
        t = Thread(target=receive_from_server)
        t.daemon = True
        t.start()
    except OSError:
        global connected
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
