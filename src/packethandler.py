from more_itertools import batched
import struct
from socket import socket
from logging import debug
from dataclasses import dataclass

@dataclass
class Packet:
    more: bool
    data: bytes

    def __bytes__(self):
        return struct.pack(f"?{len(self.data)}s", self.more, self.data)

    @staticmethod
    def from_bytes(data: bytes):
        payload_length = max(0, len(data)-1)
        debug(f"payload length {payload_length}")
        data_format = f"?{payload_length}s" if payload_length > 0 else '?'
        (more, data) = struct.unpack(data_format, data)
        return Packet(more=more, data=data)

class PacketHandler:
    def __init__(self, sock: socket, packet_size=1024):
        self.socket = sock
        self.packet_size = packet_size

    def to_packets(self, data):
        batches = batched(bytes(data), self.packet_size - 1)
        last_batch = next(batches, None)
        while (batch := next(batches, None)) is not None:
            yield Packet(more=True, data=bytes(last_batch))
            last_batch = batch
        yield Packet(more=False, data=bytes(last_batch))

    def next_packet(self):
        data = self.socket.recv(self.packet_size)
        debug(f"got {len(data)} bytes: {data!r}")
        return Packet.from_bytes(data)

    def send_packet(self, packet):
        self.socket.sendall(bytes(packet))

    def packets(self):
        more = True
        while more:
            packet = self.next_packet()
            (more, chunk) = (packet.more, packet.data)
            debug(f"receiving packet {packet}")
            yield chunk

    def receive_message(self):
        return b''.join(self.packets())

    def send_message(self, message):
        for packet in self.to_packets(bytes(message)):
            debug(f"sending packet {packet}")
            self.send_packet(packet)

    def close(self):
        self.socket.close()