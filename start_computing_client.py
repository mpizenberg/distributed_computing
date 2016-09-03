#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

import socket
import distributed_computing
import traceback
import argparse


def main(args):
    try:
        client_socket = socket.socket()
        client_socket.connect((args.address, args.port))
        while distributed_computing.handle_work(client_socket):
            pass
    except ConnectionError as err:
        print("Connection error: {}".format(err))
    except BaseException as err:
        traceback.print_exc()
    client_socket.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=main)
    parser.add_argument('-v', '--version', action='version', version='0.1')
    parser.add_argument('-a', '--address', metavar='address', default='localhost',
                        help='address of the server to connect to (eg. localhost or 0.0.0.0)')
    parser.add_argument('-p', '--port', metavar='port', type=int, default=8080,
                        help='port to use to reach the server.')
    args = parser.parse_args()
    args.func(args)
