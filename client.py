# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements


def send_msg(sock, bytes_msg):
    """ Send a message from a socket.
    """
    bytes_sent = 0
    msg_length = len(bytes_msg)
    while bytes_sent < msg_length:
        sent = sock.send(bytes_msg[bytes_sent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        bytes_sent = bytes_sent + sent
    assert bytes_sent == msg_length
    return bytes_sent


def recv_msg(sock, msg_length, max_chunk_length=2048):
    """ Receive a message from a socket of a given length.
    return: the message in a bytes string.
    """
    chunks = []
    bytes_recvd = 0
    while bytes_recvd < msg_length:
        chunk = sock.recv(min(msg_length-bytes_recvd, max_chunk_length))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recvd = bytes_recvd + len(chunk)
    assert bytes_recvd == msg_length
    return b''.join(chunks)
