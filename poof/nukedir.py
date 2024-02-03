# See: https://github.com/poof-backup/poof/blob/master/LICENSE.txt


import os
import platform
import subprocess


# TODO:  Reference - https://docs.python.org/3/library/shutil.html


# TODO:  use the Python API instead of calling external OS-levels commands here?
#        Neither rm -P nor srm are standard, and neither has much effect on
#        actual security since they don't work on SSDs anyway.
#
#        https://github.com/poof-backup/poof/issues/59
def _getNukeDirectoryArgsMac(path):
	args = (
		'/bin/rm',
		'-Prf',
		path,
	)
	return args


def _getNukeDirectoryArgsLinux(path):
	args = (
		'/bin/rm',
		'-Rf',
		path,
	)
	return args


def _getNukeDirectoryArgsWindows(path):
    raise NotImplementedError


def nukeDirectoryProcess(path):
    result = False
    error  = Exception()
    args = False

    hostPlatform = platform.system()

    if os.path.exists(path):
        if 'Darwin' == hostPlatform:
            args =  _getNukeDirectoryArgsMac(path)
        elif 'Linux' == hostPlatform:
            args =  _getNukeDirectoryArgsLinux(path)

    if args:
        procResult = subprocess.run(args)
        result = not procResult.returncode

    return result, error


def nukeDirectory(path):
    return nukeDirectoryProcess(path)

