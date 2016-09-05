# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

import sys
import math
import os

# Some useful constants
STYLE_GREEN   = '\033[32m'
STYLE_YELLOW  = '\033[33m'
STYLE_BOLD    = '\033[1m'
STYLE_DEFAULT = '\033[0m'


def get_terminal_size():
    """ Returns (rows, columns)
    where rows is the number of rows of the terminal window ...
    """
    return tuple(map(int, os.popen('stty size', 'r').read().split()))


def print_progress(print_control, total, done, working):
    """ Prints the progress of a process with a stylish colored progress bar.
    """
    with print_control['lock']:
        if not print_control['finished']:
            rows, columns = get_terminal_size()
            progress_bar_length = int(columns / 2)
            done_ratio         = done / total
            working_ratio      = working / total
            done_bar_number    = int(done_ratio * progress_bar_length)
            working_bar_number = math.ceil(working_ratio * progress_bar_length)

            finished = (done == total)

            sys.stderr.write('\r{bold}[{done_bars}{working_bars}{spaces}{bold}]{percentage} %'.format(**{
                'bold':         STYLE_BOLD,
                'default':      STYLE_DEFAULT,
                'done_bars':    STYLE_GREEN + '|' * done_bar_number,
                'working_bars': STYLE_YELLOW + '|' * working_bar_number,
                'spaces':       STYLE_DEFAULT + ' ' * (progress_bar_length - done_bar_number - working_bar_number),
                'percentage':   STYLE_DEFAULT + ' {:6.2f}'.format(done_ratio * 100 if not finished else 100)}))

            if finished:
                sys.stdout.write("\n")
                print_control['finished'] = True
