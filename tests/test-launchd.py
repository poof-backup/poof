# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


from poof.launchd import LAUNCH_AGENT_FILE
from poof.launchd import LAUNCH_AGENT_OS
from poof.launchd import LAUNCH_AGENT_PROG
from poof.launchd import LAUNCH_AGENT_USER_NAME
from poof.launchd import TEST_LAUNCH_AGENTS_PATH
from poof.launchd import TEST_LAUNCH_AGENT_FULL_PATH
from poof.launchd import TEST_LAUNCH_AGENT_POOF
from poof.launchd import TEST_LAUNCH_AGENT_PROG
from poof.launchd import _is_launchdReady
from poof.launchd import _resolveTemplate
from poof.launchd import disable
from poof.launchd import enable
from poof.launchd import isEnabled
from poof.launchd import isSupported
from poof.launchd import launchdConfig

import os
import platform


# +++ pre-test +++

if not os.path.exists(TEST_LAUNCH_AGENTS_PATH):
    os.mkdir(TEST_LAUNCH_AGENTS_PATH)


# --- tests ---

def test_isSupported():
    assert isSupported(LAUNCH_AGENT_OS)
    assert not isSupported('Linux')
    assert not isSupported('Windows')


def test__is_launchdReadyFalse():
    assert not _is_launchdReady('Linux')
    assert not _is_launchdReady('Windows')
    assert not _is_launchdReady(hostOS = platform.system(), launchAgent = TEST_LAUNCH_AGENT_POOF)


def test_isEnabledFalse():
    assert not isEnabled('Linux')
    assert not isEnabled('Windows')
    assert not isEnabled(LAUNCH_AGENT_OS, launchAgentFile = TEST_LAUNCH_AGENT_FULL_PATH, launchAgent = TEST_LAUNCH_AGENT_POOF)


def test__resolveTemplate():
    output = _resolveTemplate(launchAgent = TEST_LAUNCH_AGENT_POOF,
                launchAgentProg = TEST_LAUNCH_AGENT_PROG,
                launchAgentUserName = LAUNCH_AGENT_USER_NAME,
                launchAgentFile = TEST_LAUNCH_AGENT_FULL_PATH)

    assert '%%HOME%%' not in output
    assert '%%LAUNCH_AGENT_POOF%%' not in output
    assert '%%LAUNCH_AGENT_PROG%%' not in output
    assert '%%LAUNCH_AGENT_USER_NAME%%' not in output

    assert os.path.exists(TEST_LAUNCH_AGENT_FULL_PATH)

    os.unlink(TEST_LAUNCH_AGENT_FULL_PATH)


def test_enable():
    if LAUNCH_AGENT_OS == 'Darwin':
        assert enable(hostOS = LAUNCH_AGENT_OS, agentFile = TEST_LAUNCH_AGENT_FULL_PATH, launchAgent = TEST_LAUNCH_AGENT_POOF)
    else:
        # Ignore other OSs
        pass


def test__is_launchdReady():
    assert not _is_launchdReady('Linux')
    assert not _is_launchdReady('Windows')
    assert _is_launchdReady(launchAgent = TEST_LAUNCH_AGENT_POOF)


def test_isEnabled():
    assert not isEnabled('Linux')
    assert not isEnabled('Windows')
    assert isEnabled(LAUNCH_AGENT_OS, launchAgentFile = TEST_LAUNCH_AGENT_FULL_PATH, launchAgent = TEST_LAUNCH_AGENT_POOF)


def test_disable():
    if LAUNCH_AGENT_OS == 'Darwin':
        assert disable(hostOS = LAUNCH_AGENT_OS, agentFile = TEST_LAUNCH_AGENT_FULL_PATH, launchAgent = TEST_LAUNCH_AGENT_POOF, unitTest = True)
    else:
        # Ignore other OSs
        pass


def test_launchdConfig():
    if LAUNCH_AGENT_OS == 'Darwin':
        plist = launchdConfig(hostOS = LAUNCH_AGENT_OS, agentFile = TEST_LAUNCH_AGENT_FULL_PATH, launchAgent = TEST_LAUNCH_AGENT_POOF)

        assert len(plist)

        disable(hostOS = LAUNCH_AGENT_OS, agentFile = TEST_LAUNCH_AGENT_FULL_PATH, launchAgent = TEST_LAUNCH_AGENT_POOF)
    else:
        # Ignore other OSs
        pass


test__is_launchdReadyFalse()

