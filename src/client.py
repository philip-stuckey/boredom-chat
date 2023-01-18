import socket
from sys import argv, stdin
from queue import Queue
from packethandler import PacketHandler
from messagetypes import Sync, TaggedMessage
from logging import debug
import logging

logging.basicConfig(level=logging.INFO)

class Client:
    packet_size=2048

    def __init__(self, socket):
        self.socket=PacketHandler(socket)
        self.inbox=Queue()

    def receive(self):
        return self.socket.receive_message()

    def post(self, message_body):
        debug("posting")
        message = f"POST\nfrom: {socket.gethostname()}\n{message_body}"
        self.socket.send_message(message.encode())

    def sync(self):
        debug("syncing")
        self.socket.send_message(bytes(Sync()))
        debug("waiting on packets")
        response = TaggedMessage.from_bytes(self.socket.receive_message())
        while response.tag != b'ENDP':
            debug(f"got response {response}")
            self.inbox.put(response.message)
            response = TaggedMessage.from_bytes(self.socket.receive_message())


def main(client):
    client.sync()
    while not client.inbox.empty():
        print(client.inbox.get().decode())

    try:
        while True:
            message=input(">").strip()
            if len(message) > 0:
                client.post(message)
            client.sync()
            while not client.inbox.empty():
                print(client.inbox.get().decode())
    except KeyboardInterrupt:
        pass


HOST, PORT = "localhost", 9999
if __name__ == '__main__':
    debug("got here")
    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        main(client = Client(sock))
