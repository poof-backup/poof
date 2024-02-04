# See: https://github.com/poof-backup/poof/blob/master/LICENSE.txt


from shutil import rmtree

import os
import sys


TEST_DIR = os.path.join('/', os.environ['HOME'], 'NukeDirTest')


# --- globals ---

nukeErrorsList = None


# --- implementation ---

def _nukeDirectoryException(f, path, excinfo):
    global nukeErrorsList
    logEntry = { 'path': path, 'exception': excinfo[0].__name__, 'info': str(excinfo[1]), }
    nukeErrorsList.append(logEntry)


def nukeDirectory(path):
    """
    Deletes a directory and all its contents using system services.

    Arguments
    ---------
        path
    The canonical path to the directory to remove from the file system.

    Returns
    -------
        aList
    A list of log entries in Python dictionary format, ready to be processed by
    a JSON-like logger (ELK, Datadog, etc.).  Each entry has these attributes:

    `path` - The path to the file or directory that caused the exception
    `exception' - The exception class name, in human-readable form
    `info` - A human-readable descripton of the problem
    """
    global nukeErrorsList

    nukeErrorsList = list()
    # Use onexc instead of onerror for Python >= 3.12); see
    # https://docs.python.org/3/library/shutil.html
    if (sys.version_info.major >= 3 and sys.version_info.minor >= 12):
        rmtree(path, onexc = _nukeDirectoryException)
    else:
        rmtree(path, onerror = _nukeDirectoryException)

    return nukeErrorsList

