#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

import server
import distributed_computing


def manage_server_slave(client_socket, tasks_manager):
    still_connected = True
    while still_connected and not tasks_manager.all_tasks_done():
        # Get a task from the tasks manager.
        (task_id, task) = tasks_manager.get_next_task()
        if task_id is not None:
            (work_done, result) = distributed_computing.give_work(client_socket, task)
            still_connected = work_done
            # Give back the results to the tasks manager.
            tasks_manager.update(task_id, work_done, result)
    client_socket.close()


def main():
    server_socket = server.create_socket('', 8083)
    tasks_manager = distributed_computing.TasksManager([
        distributed_computing.Task("sleep 10 && echo 0"),
        distributed_computing.Task("sleep 10 && echo 1"),
        distributed_computing.Task("sleep 10 && echo 2"),
        distributed_computing.Task("sleep 10 && echo 3"),
        ])
    server.launch_clients_threads_loop(
        server_socket,
        tasks_manager.all_tasks_done,
        manage_server_slave,
        tasks_manager)


if __name__ == '__main__':
    main()
