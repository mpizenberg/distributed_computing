#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

import server
import distributed_computing
import argparse


def load_tasks(filepath = None):
    tasks_list = []
    if filepath is not None:
        with open(filepath) as f:
            commands_list = [command[:-1] for command in f.readlines()]
            tasks_list = list(map(distributed_computing.Task, commands_list))
    return tasks_list

def main(args):
    server_socket = server.create_socket(args.address, args.port)
    tasks_manager = distributed_computing.TasksManager(load_tasks(args.tasks))
    server.launch_clients_threads_loop(
        server_socket,
        tasks_manager.all_tasks_done,
        distributed_computing.manage_server_slave,
        tasks_manager)


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
