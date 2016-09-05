# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

import client
import tempfile
import threading
import subprocess
import sys
import socketserver


# Define the different tasks types:
NO_OUT = 0
STD_OUT = 1
FILE_OUT = 2


class TasksThreadingTCPServer(socketserver.ThreadingTCPServer):
    def __init__(self, server_address, tasks_manager):
        self.allow_reuse_address = True
        self.tasks_manager = tasks_manager
        # NO WAY TO SHUTDOWN ALL CLIENTS SOCKETS !!!!!!
        self.daemon_threads = True
        super().__init__(server_address, TasksTCPHandler)


class TasksTCPHandler(socketserver.BaseRequestHandler):
    """
    """

    def handle(self):
        tasks_manager = self.server.tasks_manager
        while not tasks_manager.all_tasks_done():
            # Get a task from the tasks manager.
            (task_id, task) = tasks_manager.get_next_task()
            if task_id is not None:
                tasks_manager.print_progress()
                (work_done, result) = give_work(self.request, task)
                # Give back the results to the tasks manager.
                tasks_manager.update(task_id, work_done, result)
                if not work_done:
                    raise RuntimeError("client work not done")

        # Shutdown all clients if all tasks are done.
        self.server.shutdown()


def give_work(client_socket, task):
    """
    """
    work_done = False
    result = None
    # Send task through the client socket.
    task_sent = task.send_through(client_socket)
    if task_sent:
        # Wait for the answer.
        (work_done, result) = task.retrieve_result(client_socket)
    else:
        client_socket.close()
    return (work_done, result)



def handle_work(client_socket):
    """
    """
    work_done = False
    try:
        print("waiting for work ...")
        # First get the type of task to do.
        task_type = int.from_bytes(client.recv_msg(client_socket, 1), 'little')
        # Then get the command message size.
        msg_length = int.from_bytes(client.recv_msg(client_socket, 4), 'little')
        # Then get the command itself.
        cmd_msg = client.recv_msg(client_socket, msg_length).decode()

        # Now execute the task.
        print("working ...")
        task = Task(cmd_msg, task_type)
        result = task.execute()

        # Finally return the results.
        print("sending back result ...")
        client.send_msg(client_socket, len(result).to_bytes(4,'little'))
        client.send_msg(client_socket, result)
        print("done")
        work_done = True
    except RuntimeError as err:
        print("Runtime Error: {}".format(err))
        client_socket.close()
    except KeyboardInterrupt:
        print("Client stopped by user.")
        client_socket.close()
    return work_done


class Task:
    """
    """
    def __init__(self, command, task_type=STD_OUT):
        self.command = command
        self.task_type = task_type

    def send_through(self, client_socket):
        """
        """
        task_sent = False
        try:
            # First send the task type.
            type_msg = self.task_type.to_bytes(1,'little')
            client.send_msg(client_socket, type_msg)
            # Then send the command size.
            cmd_msg = str.encode(self.command)
            msg_length = len(cmd_msg).to_bytes(4,'little')
            client.send_msg(client_socket, msg_length)
            # Finally send the command message.
            client.send_msg(client_socket, cmd_msg)
            task_sent = True
        except RuntimeError as err:
            print("Runtime Error: {}".format(err))
            client_socket.close()
        except KeyboardInterrupt:
            print("Client stopped by user.")
            client_socket.close()
        return task_sent

    def retrieve_result(self, client_socket):
        """
        """
        msg_retrieved = False
        msg = None
        try:
            # First receive the message size.
            msg_length_bytes = client.recv_msg(client_socket, 4)
            msg_length = int.from_bytes(msg_length_bytes, 'little')
            if msg_length > 0:
                msg_bytes = client.recv_msg(client_socket, msg_length)
            # Then receive the actual result message.
            if self.task_type == STD_OUT:
                msg = msg_bytes.decode()
            elif self.task_type == FILE_OUT:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_path = temp_file.name
                    temp_file.write(msg_bytes)
                msg = temp_path
            msg_retrieved = True
        except RuntimeError as err:
            print("Runtime Error: {}".format(err))
            client_socket.close()
        except KeyboardInterrupt:
            print("Client stopped by user.")
            client_socket.close()
        # Finally return the results.
        return (msg_retrieved, msg)

    def execute(self):
        """
        """
        result = None
        if self.task_type == STD_OUT:
            p = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE)
            result = p.stdout.read()
        return result


class TasksManager:
    """
    """
    def __init__(self, tasks_list):
        self.tasks_list = tasks_list
        # A task status can be:
        # 0: Nothing done with it.
        # 1: Some thread working on it.
        # 2: Done.
        self.tasks_status = [0] * len(tasks_list)
        self.tasks_results = [None] * len(tasks_list)
        self.lock = threading.Lock()

    def all_tasks_done(self):
        with self.lock:
            return all(status==2 for status in self.tasks_status)

    def get_next_task(self):
        """
        """
        task_id = None
        task = None
        with self.lock:
            for (i,status) in enumerate(self.tasks_status):
                if status == 0:
                    task_id = i
                    task = self.tasks_list[task_id]
                    break
            # Update status of the task (to working on it).
            if task_id is not None:
                self.tasks_status[task_id] = 1
        return (task_id, task)

    def update(self, task_id, done, result):
        """
        """
        with self.lock:
            self.tasks_status[task_id] = 2 if done else 0
            self.tasks_results[task_id] = result
        self.print_progress()

    def print_progress(self):
        length = len(self.tasks_status)
        sys.stdout.write("[%s]" % ''.join(map(str, self.tasks_status)))
        sys.stdout.flush()
        sys.stdout.write("\b" * (length+2))
        if self.all_tasks_done():
            sys.stdout.write("\n")
