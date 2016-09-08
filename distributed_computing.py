# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

import client
import tempfile
import threading
import subprocess
import socketserver
import utils
import os
import shutil

# Define the different tasks types:
NO_OUT = 0
STD_OUT = 1
FILE_OUT = 2


class TasksThreadingTCPServer(socketserver.ThreadingTCPServer):
    """ A threaded TCP server socket aware of a tasks manager.
    """
    def __init__(self, server_address, tasks_manager):
        # Tell the kernel to reuse a local socket still in TIME_WAIT mode.
        self.allow_reuse_address = True
        # Link to the tasks manager.
        self.tasks_manager = tasks_manager
        # Shutdown all child threads when main thread terminates.
        self.daemon_threads = True
        super().__init__(server_address, TasksTCPHandler)


class TasksTCPHandler(socketserver.BaseRequestHandler):
    """ A request handler class exposing a handle method.
    The handle method will be automatically called
    by the TCP server for each client request.
    """

    def handle(self):
        tasks_manager = self.server.tasks_manager
        # As long as there is work to do:
        while not tasks_manager.all_tasks_done():
            # Get a task from the tasks manager.
            (task_id, task) = tasks_manager.get_next_task()
            if task_id is not None:
                tasks_manager.print_progress()
                # Give work through the client socket.
                (work_done, result) = give_work(self.request, task)
                # Give back the results to the tasks manager.
                tasks_manager.update(task_id, work_done, result)
                if not work_done:
                    raise RuntimeError("client work not done")

        # Shutdown all clients if all tasks are done.
        self.server.shutdown()


def give_work(client_socket, task):
    """ Send a task through a client socket and retrieve the results.
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
    """ Handle a task on a client machine.
    First wait for a task, then execute the task,
    finally return the results to the server.
    Return True if everything went well.
    """
    work_done = False
    try:
        # Wait for a task.
        print("waiting for work ...")
        (task_type, cmd_msg) = client.recv_typed_msg(client_socket)

        # Now execute the task.
        print("working ...")
        task = Task(cmd_msg, None, task_type)
        result = task.execute()

        # Finally return the results.
        print("sending back result ...")
        client.send_sized_msg(client_socket, result)
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
    """ A Task is composed of a command (one line of bash) and a type.
    The type describes the type of results expected.
    Results can be nothing, stdout or a file.
    """
    def __init__(self, command, result_filepath=None, task_type=STD_OUT):
        self.command = command
        self.result_filepath = result_filepath
        self.task_type = task_type
        # Create the directory hierarchy
        if result_filepath is not None:
            basedir = os.path.abspath(os.path.dirname(result_filepath))
            if not os.path.exists(basedir):
                os.makedirs(basedir)

    def send_through(self, client_socket):
        """ Send a task through a client socket to give work to a client computer.
        """
        task_sent = False
        try:
            cmd_msg = str.encode(self.command)
            client.send_typed_msg(client_socket, self.task_type, cmd_msg)
            task_sent = True
        except RuntimeError as err:
            print("Runtime Error: {}".format(err))
            client_socket.close()
        except KeyboardInterrupt:
            print("Client stopped by user.")
            client_socket.close()
        return task_sent

    def retrieve_result(self, client_socket):
        """ Retrieve the results sent back by a client
        and process it depending on the task type.
        """
        msg_retrieved = False
        msg = None
        try:
            # First receive the results message.
            msg_bytes = client.recv_sized_msg(client_socket)
            if msg_bytes is None:
                if self.task_type == NO_OUT:
                    msg_retrieved = True
            else:
                # Then process it depending on the task type.
                # For a STD_OUT task, just transform the bytes to string.
                if self.task_type == STD_OUT:
                    msg = msg_bytes.decode()
                # For a FILE_OUT task, write the bytes to a temporary file,
                # and return its filepath.
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

    def save_result(self, result):
        """ Save the result into the appropriate file.
        """
        # If the task type is STD_OUT the result is a string.
        if self.task_type == STD_OUT:
            with open(self.result_filepath, 'w') as f:
                f.write(result)
        # If the task type is FILE_OUT the result is temporary filepath.
        elif self.task_type == FILE_OUT:
            shutil.copy(result, self.result_filepath)

    def execute(self):
        """ Execute a task and get the results in a form of bytes.
        """
        result = None
        # Execute the task.
        p = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE)
        # Get the standard output.
        stdout = p.stdout.read()
        # If the task type is STD_OUT, stdout actually is the result.
        if self.task_type == STD_OUT:
            result = stdout
        # If the task type is FILE_OUT,
        # we consider the stdout to be the filepath of the result file.
        elif self.task_type == FILE_OUT:
            with open(stdout[:-1], 'rb') as f:
                result = f.read()
        return result


class TasksManager:
    """ Manages a list of tasks and their states (done, working, ...).
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

        # Used to avoid printing several times the last \n when everything is finished
        self.print_control = {'lock': threading.Lock(), 'finished': False}
        self.print_progress()

    def all_tasks_done(self):
        """ Return True if every task has the state done.
        """
        with self.lock:
            return all(status==2 for status in self.tasks_status)

    def get_next_task(self):
        """ Get the next task to be done.
        It cannot return a task already in state working.
        """
        task_id = None
        task = None
        with self.lock:
            # Search for the first not done task.
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
        """ Update the tasks manager with a task that just changed of state.
        """
        with self.lock:
            self.tasks_status[task_id] = 2 if done else 0
            self.tasks_results[task_id] = result
        if done:
            self.tasks_list[task_id].save_result(result)
        self.print_progress()

    def print_progress(self):
        """ Print a progress bar representing the current state of the tasks.
        """
        tasks_number = len(self.tasks_status)
        done = sum(map(lambda x: x == 2, self.tasks_status))
        working = sum(map(lambda x: x == 1, self.tasks_status))
        utils.print_progress(self.print_control, tasks_number, done, working)
