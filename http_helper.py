MAX_MESSAGE_SIZE = 2048

server_host = "127.0.0.1"
server_port = 9999


def extract_client_name(http_request):
    client_name = ""
    lines = http_request.split("\n")
    for line in lines[1:]:
        if "name" in line:
            client_name = line.split(":")[1]
    return client_name


def prepare_http_msg_to_send(verb, resource, body):
    import datetime

    request = []
    headers = {
        "Content-Type": "Application/x-www-form-urlencoded",
        "Content-Length": MAX_MESSAGE_SIZE,
        "Host": "{}".format(server_host),
        "Date": datetime.datetime.utcnow(),
    }
    for key, value in headers.items():
        request.append("{}:{}".format(key, value))

    http_msg_to_send = "{} {} HTTP/1.0\n{}\n\n{}\n".format(
        verb, resource, "\n".join(request), body
    )
    return http_msg_to_send


def prepare_get_all_client_names():
    resource = "get-all-clients"
    return prepare_http_msg_to_send("GET", resource, None)


def prepare_post_client_name(name_entered):
    body = "name:{}".format(name_entered)
    resource = "client-name"
    return prepare_http_msg_to_send("POST", resource, body)
