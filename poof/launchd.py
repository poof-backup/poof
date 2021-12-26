# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


import getpass
import platform
import os
import sys

import appdirs


# --- constants ---

LAUNCH_AGENT_OS = "Darwin"
LAUNCH_AGENT_PATH = os.path.join(os.environ['HOME'], 'Library/LaunchAgents') if platform.system() == LAUNCH_AGENT_OS else None
LAUNCH_AGENT_SERVICE_ID = 'org.pypi.poof'
LAUNCH_AGENT_USER_ID = os.geteuid()
LAUNCH_AGENT_USER_NAME = getpass.getuser()


# +++ implementation ***

def isSupported(targetOS = LAUNCH_AGENT_OS):
    return targetOS == LAUNCH_AGENT_OS


def plist(agentPath = LAUNCH_AGENT_PATH):
    raise NotImplementedError

