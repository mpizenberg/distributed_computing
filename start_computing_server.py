#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

import server
import shared_computing


def main():
    server_socket = server.create_socket('', 8083)
    tasks_manager = shared_computing.TasksManager([
        shared_computing.Task("echo 0"),
        shared_computing.Task("echo 1"),
        ])
    server.launch_clients_threads_loop(
        server_socket,
        shared_computing.give_work,
        tasks_manager = tasks_manager)


if __name__ == '__main__':
    main()
