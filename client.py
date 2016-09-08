# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements


def send_msg(sock, bytes_msg):
    """ Send a single message from a socket.
    """
    bytes_sent = 0
    msg_length = len(bytes_msg)
    # Send as many times as need to send the complete message.
    while bytes_sent < msg_length:
        sent = sock.send(bytes_msg[bytes_sent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        bytes_sent = bytes_sent + sent
    assert bytes_sent == msg_length
    return bytes_sent

def send_sized_msg(sock, bytes_msg):
    """ Send first the size of the message (coded on 4 bytes little)
    and then the message itself.
    """
    msg_length = len(bytes_msg) if bytes_msg is not None else 0
    send_msg(sock, msg_length.to_bytes(4, 'little'))
    if msg_length > 0:
        send_msg(sock, bytes_msg)

def send_typed_msg(sock, msg_type, bytes_msg):
    """ Send a message with a type encoded over 1 bytes little.
    """
    send_msg(sock, msg_type.to_bytes(1, 'little'))
    send_sized_msg(sock, bytes_msg)




def recv_msg(sock, msg_length, max_chunk_length=2048):
    """ Receive a message from a socket of a given length.
    return: the message in a bytes string.
    """
    chunks = []
    bytes_recvd = 0
    # Receive as many times as need to receive the complete message.
    while bytes_recvd < msg_length:
        chunk = sock.recv(min(msg_length-bytes_recvd, max_chunk_length))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recvd = bytes_recvd + len(chunk)
    assert bytes_recvd == msg_length
    return b''.join(chunks)

def recv_sized_msg(sock):
    """ Receive first the size of the message (coded on 4 bytes little)
    and then the message itself.
    """
    msg_bytes = None
    msg_length = int.from_bytes(recv_msg(sock, 4), 'little')
    if msg_length > 0:
        msg_bytes = recv_msg(sock, msg_length)
    return msg_bytes

def recv_typed_msg(sock):
    """ Receive a message with a type encoded over 1 bytes little.
    """
    msg_type = int.from_bytes(recv_msg(sock, 1), 'little')
    msg_bytes = recv_sized_msg(sock)
    return (msg_type, msg_bytes)
