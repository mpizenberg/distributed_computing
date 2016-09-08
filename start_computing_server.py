#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

import distributed_computing as dis_comp
import argparse
import sys
import os
from functools import partial
from itertools import zip_longest


def load_tasks(tasks_filepath=None,
        results_filepath=None, types=dis_comp.STD_OUT):
    """ Load the tasks written in the file.
    If no file is given, get the tasks from stdin.
    Each line of the file will be considered as a different task.
    """
    # First load the commands.
    commands_list = []
    if tasks_filepath is not None:
        with open(tasks_filepath) as f:
            commands_list = [command[:-1] for command in f.readlines()]
    else:
        print("Type down 1 command per line here. Ctrl-D when finished.")
        commands_list = [command[:-1] for command in sys.stdin.readlines()]
    nb_tasks = len(commands_list)

    # Then load the results.
    results_paths_list = []
    if results_filepath is None:
        types = dis_comp.NO_OUT
    else:
        with open(results_filepath) as f:
            results_paths_list = [path[:-1] for path in f.readlines()]
        assert(len(results_paths_list) == nb_tasks)

    # Finally create the tasks.
    tasks_list = [dis_comp.Task(command, result_path,  types)\
        for (command, result_path) in \
        zip_longest(commands_list, results_paths_list)]
    return tasks_list

def main(args):
    """ Setup a server socket that will handle connections from clients and give them work.
    The address of the server socket is (args.address, args.port).
    The tasks to distribute to the clients are in args.tasks.
    """
    try:
        # Initiate the tasks manager
        tasks_manager = dis_comp.TasksManager(
            load_tasks(args.tasks, args.results,
                dis_comp.FILE_OUT if args.resultsAreFiles else dis_comp.STD_OUT))
        # Create the master server socket.
        # This socket is a TCP threaded socket.
        server_socket = dis_comp.TasksThreadingTCPServer(
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


def check_path(path, should_exist):
    """ Check that a path (file or folder) exists or not and return it.
    """
    path = os.path.normpath(path)
    if should_exist != os.path.exists(path):
        msg = "path " + ("does not" if should_exist else "already") + " exist: " + path
        raise argparse.ArgumentTypeError(msg)
    return path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=main)
    parser.add_argument('-v', '--version', action='version', version='0.1')
    parser.add_argument('-a', '--address', metavar='address', default='',
                        help='address for the server socket (eg. localhost or 0.0.0.0)')
    parser.add_argument('-p', '--port', metavar='port', type=int, default=8080,
                        help='port on which the server will run.')
    parser.add_argument('-t', '--tasks', metavar='filepath',
                        type=partial(check_path, should_exist=True), default=None,
                        help='file containing the commands to run, if not specified, \
                        commands will be read through stdin')
    parser.add_argument('-r', '--results', metavar='filepath',
                        type=partial(check_path, should_exist=True), default=None,
                        help='expect the results of tasks as files.')
    parser.add_argument('--resultsAreFiles', action='store_true',
                        help='expect the results of tasks as files.')
    args = parser.parse_args()
    args.func(args)
