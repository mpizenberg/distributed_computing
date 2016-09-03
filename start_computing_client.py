#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

import socket
import distributed_computing
import traceback


def main():
    try:
        client_socket = socket.socket()
        client_socket.connect(('localhost', 8083))
        while distributed_computing.handle_work(client_socket):
            pass
    except ConnectionError as err:
        print("Connection error: {}".format(err))
    except BaseException as err:
        traceback.print_exc()
    client_socket.close()

if __name__ == '__main__':
    main()
