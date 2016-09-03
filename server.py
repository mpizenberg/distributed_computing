# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

import socket
import threading

def create_socket(host_address, port, nb_listen=5):
    """ Create a server socket with a host address and a port.
    return: a server socket.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host_address, port))
    server_socket.listen(nb_listen)
    return server_socket


def launch_clients_threads_loop(server_socket, threaded_function, **kwargs):
    """
    """
    print("Waiting for clients ...")
    try:
        sockets_list = []
        while True:
            # Accept connections from outside (blocking).
            (client_socket, address) = server_socket.accept()
            sockets_list.append(client_socket)
            # Launch a function in another thread with this client socket.
            client_thread = threading.Thread(
                target = threaded_function,
                args = (client_socket, ),
                kwargs = kwargs)
            client_thread.run()
    except KeyboardInterrupt:
        print("Server stopped by user.")
        server_socket.close()
        for s in sockets_list:
            s.close()
        # TODO: Take care of possible opened files ?
