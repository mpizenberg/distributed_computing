# Distributed Computing

This library is intended to empower users to run their tasks on computers on the network.
Your 10h+ computing sessions will now finish in a blink of an eye.

## How to use

The two example scripts to run respectively on a server machine and on clients machines are:

* `start_computing_server.py`: run this on the server.
   If a file is provided (option --tasks) it will consider each line as a different task.
   Otherwise, tasks have to be written through stdin.
* `start_computing_client.py`: run this on the clients.
   Provided the correct address of the server (ip and port), it will connect to it,
   retrieve tasks, execute them, and send the results back to the server.

The more clients, the merrier!
[Culture](https://en.wikipedia.org/wiki/The_More_the_Merrier)

## Requirements and Installation

Hum ... no install
(just get the code with git or whatever you like: curl, wget, copy-paste, ...).
Did I say you need python? (ok well >= python 3.4). Not so much to bear.

## License

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

## Credits

Thanks Thomas for the inspiration and the strong basis that made this code possible.

For any question of any kind, you may address me an email at:
matthieu.pizenberg@gmail.com
