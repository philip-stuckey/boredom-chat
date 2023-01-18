from socket import socket, AF_INET, SOCK_STREAM
from logging import info, debug, warning
import logging
from packethandler import PacketHandler
from dataclasses import dataclass
from messagetypes import TaggedMessage, Post, EndOfPosts
from threading import Thread
from queue import Queue
from typing import List

logging.basicConfig(level=logging.DEBUG)
# TODO: architect this so it doesn't require mutable global variables



@dataclass
class ClientSession:
    socket: PacketHandler
    name: str
    message_queue: Queue

    def close(self):
        self.socket.close()

def handle_client(session: ClientSession):
    while True:
        message = session.socket.receive_message()
        tagged_message = TaggedMessage.from_bytes(message)
        debug(f"got message with tag '{tagged_message.tag}'")
        if tagged_message.tag == b'SYNC':
            while not session.message_queue.empty():
                message = session.message_queue.get()
                session.socket.send_message(Post(message))
            session.socket.send_message(EndOfPosts())
        elif tagged_message.tag == b'POST':
            debug(f"got post from {session.name}")
            session.message_queue.put(tagged_message.message)
        else:
            warning(f"unrecognized tag {tagged_message.tag} from {session.name}")
            raise Exception(f"unrecognized tag {tagged_message.tag} from {session.name}")


def main(socket):
    message_queue = Queue()
    while True:
        debug("waiting on new clients")
        (conn, addr) = sock.accept()
        session = ClientSession(
            socket=PacketHandler(conn),
            name=addr,
            message_queue=message_queue
        )
        try:
            handle_client(session)
        # TODO FIX this
        except Exception as e:
            print(e)

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    with socket(AF_INET, SOCK_STREAM) as sock:
        try:
            sock.bind((HOST, PORT))
            info(f"listening on port {PORT}")
            sock.listen()
            main(socket)
        finally:
            sock.close()
