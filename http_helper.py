MAX_MESSAGE_SIZE = 2048

server_host = "127.0.0.1"
server_port = 9999
GET_ALL_CLIENTS = "all/client/names"
REGISTER_CLIENT_NAME = "register/client/name"
SEND_MESSAGE = "send/message"


def extract_client_name(http_request):
    client_name = ""
    lines = http_request.split("\n")
    for line in lines[1:]:
        if "name" in line:
            client_name = line.split(":")[1]
    return client_name


def extract_message_details(line):
    print("Line to process {}".format(line))
    import json

    try:
        line = json.loads(line)
        return (
            line.get("mode", None),
            line.get("destination", None),
            line.get("message", None),
        )
    except json.decoder.JSONDecodeError as e:
        # ack message
        return "ACK", None, None


def prepare_http_msg_request(verb, resource, body=""):
    import datetime

    request = []
    headers = {
        "Content-Type": "Application/x-www-form-urlencoded",
        "Content-Length": len(body),
        "Host": "{}".format(server_host),
        "Date": datetime.datetime.utcnow(),
        "User-Agent": "Custom HTTP endpoint written for CSE5306 lab",
    }
    for key, value in headers.items():
        request.append("{}:{}".format(key, value))

    http_msg_to_send = "{} {} HTTP/1.0\n{}\n\n{}\n".format(
        verb, resource, "\n".join(request), body
    )
    return http_msg_to_send


def prepare_get_all_client_names_request():
    return prepare_http_msg_request("GET", GET_ALL_CLIENTS)


def prepare_post_client_name_request(name_entered):
    body = "name:{}".format(name_entered)
    return prepare_http_msg_request("POST", REGISTER_CLIENT_NAME, body)


def prepare_http_msg_response(status, body=""):
    import datetime

    first_line = "HTTP/1.0 {}".format(status)
    headers = {
        "Content-Type": "Application/json",
        "Content-Length": len(body),
        "Host": "{}".format(server_host),
        "Date": datetime.datetime.utcnow(),
        "User-Agent": "Custom HTTP endpoint written for CSE5306 lab",
    }
    response_headers = []
    for key, value in headers.items():
        response_headers.append("{}:{}".format(key, value))
    import json

    http_msg_response = "{}\n{}\n{}\n".format(
        first_line, response_headers, json.dumps(body)
    )
    return http_msg_response


def prepare_get_all_client_names_response(names):
    return prepare_http_msg_response("200 OK", names)


def prepare_post_client_name_response():
    return prepare_http_msg_response("200 OK", REGISTER_CLIENT_NAME)


def parse_client_name_response(http_response):
    names = http_response.split("\n")[2]
    import json

    return json.loads(names)


def prepare_fwd_msg_to_client(mode, destination, message):
    import json

    body = {
        "resource": SEND_MESSAGE,
        "mode": mode,
        "destination": destination,
        "message": message,
    }
    return prepare_http_msg_response("200 OK", json.dumps(body))


def prepare_ack_message():
    return prepare_http_msg_response("200 OK", SEND_MESSAGE)
