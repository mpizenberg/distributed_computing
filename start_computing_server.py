#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

import distributed_computing
import argparse
import sys


def load_tasks(filepath = None):
    """ Load the tasks written in the file.
    If no file is given, get the tasks from stdin.
    Each line of the file will be considered as a different task.
    """
    commands_list = []
    if filepath is not None:
        with open(filepath) as f:
            commands_list = [command[:-1] for command in f.readlines()]
    else:
        commands_list = [command[:-1] for command in sys.stdin.readlines()]
    #tasks_list = list(map(distributed_computing.Task, commands_list))
    tasks_list = [distributed_computing.Task(line, task_type=2) for line in commands_list]
    return tasks_list

def main(args):
    """ Setup a server socket that will handle connections from clients and give them work.
    The address of the server socket is (args.address, args.port).
    The tasks to distribute to the clients are in args.tasks.
    """
    try:
        # Initiate the tasks manager
        tasks_manager = distributed_computing.TasksManager(load_tasks(args.tasks))
        # Create the master server socket.
        # This socket is a TCP threaded socket.
        server_socket = distributed_computing.TasksThreadingTCPServer(
            (args.address, args.port), tasks_manager)
        # Listen for client connections and distribute the work load.
        server_socket.serve_forever()
    except KeyboardInterrupt:
        pass
    # If the serve_forever() loop ends, close the server socket and returns.
    print("Closing server")
    server_socket.shutdown()
    server_socket.server_close()
    print("Server closed")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=main)
    parser.add_argument('-v', '--version', action='version', version='0.1')
    parser.add_argument('-a', '--address', metavar='address', default='',
                        help='address for the server socket (eg. localhost or 0.0.0.0)')
    parser.add_argument('-p', '--port', metavar='port', type=int, default=8080,
                        help='port on which the server will run.')
    parser.add_argument('-t', '--tasks', metavar='filepath', default=None,
                        help='file containing the commands to run, if not specified, \
                        commands will be read through stdin')
    args = parser.parse_args()
    args.func(args)
