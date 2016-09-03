#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

import socket
import shared_computing


def main():
    client_socket = socket.socket()
    client_socket.connect(('localhost', 8083))
    work_done = shared_computing.handle_work(client_socket)

if __name__ == '__main__':
    main()
