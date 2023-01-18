from socket import socket, AF_INET, SOCK_STREAM
from logging import info, debug, warning
import logging
from packethandler import PacketHandler
from dataclasses import dataclass
from messagetypes import TaggedMessage, Post, EndOfPosts
from threading import Thread

logging.basicConfig(level=logging.DEBUG)


# TODO: architect this so it doesn't require mutable global variables

@dataclass
class ClientSession:
    socket: PacketHandler
    name: str
    messages: list

    def close(self):
        self.socket.close()


def handle_client(session: ClientSession):
    debug("client thread spawned")
    while True:
        message = session.socket.receive_message()
        tagged_message = TaggedMessage.from_bytes(message)
        debug(f"got message with tag '{tagged_message.tag}'")
        if tagged_message.tag == b'SYNC':
            for message in session.messages:
                session.socket.send_message(Post(message))
            session.socket.send_message(EndOfPosts())
        elif tagged_message.tag == b'POST':
            debug(f"got post from {session.name}")
            session.messages.append(tagged_message.message)
        else:
            warning(f"unrecognized tag {tagged_message.tag} from {session.name}")
            break


def main(sock):
    message_history = []
    thread_pool = []
    while True:
        debug("waiting on new clients")
        (conn, addr) = sock.accept()
        session = ClientSession(
            socket=PacketHandler(conn),
            name=addr,
            messages=message_history,
        )
        t = Thread(target=handle_client, args=(session,))
        t.start()
        thread_pool[:] = filter(Thread.is_alive, thread_pool)
        thread_pool.append(t)


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    with socket(AF_INET, SOCK_STREAM) as sock:
        try:
            sock.bind((HOST, PORT))
            info(f"listening on port {PORT}")
            sock.listen()
            main(sock)
        finally:
            sock.close()
