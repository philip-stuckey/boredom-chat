from dataclasses import dataclass

@dataclass
class TaggedMessage:
    tag: bytes
    message: bytes

    @staticmethod
    def from_bytes(bytes):
        return TaggedMessage(tag=bytes[0:4], message=bytes[4:])

    def __bytes__(self):
        return self.tag + self.message


class Sync(TaggedMessage):
    def __init__(self):
        super().__init__(tag=b'SYNC', message=b'')


class Post(TaggedMessage):
    def __init__(self, message):
        super().__init__(tag=b'POST', message=message)

class EndOfPosts(TaggedMessage):
    def __init__(self):
        super().__init__(tag=b"ENDP", message=b'')
