# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


from poof.launchd import LAUNCH_AGENT_FILE
from poof.launchd import LAUNCH_AGENT_OS
from poof.launchd import LAUNCH_AGENT_PROG
from poof.launchd import LAUNCH_AGENT_USER_NAME
from poof.launchd import _is_launchdReady
from poof.launchd import _resolveTemplate
from poof.launchd import disable
from poof.launchd import enable
from poof.launchd import isEnabled
from poof.launchd import isSupported
from poof.launchd import launchdConfig

import os


# +++ pre-test +++

TEST_LAUNCH_AGENTS_PATH = './tests/LaunchAgents'
TEST_LAUNCH_AGENT_FULL_PATH = os.path.join(TEST_LAUNCH_AGENTS_PATH, LAUNCH_AGENT_FILE)
TEST_LAUNCH_AGENT_POOF = 'test.unit.poof'
TEST_LAUNCH_AGENT_PROG = LAUNCH_AGENT_PROG.replace('poof', 'poofbogus')

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
    assert not _is_launchdReady(launchAgent = TEST_LAUNCH_AGENT_POOF)


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
        assert enable(targetOS = LAUNCH_AGENT_OS, agentFile = TEST_LAUNCH_AGENT_FULL_PATH, launchAgent = TEST_LAUNCH_AGENT_POOF)
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
        assert disable(targetOS = LAUNCH_AGENT_OS, agentFile = TEST_LAUNCH_AGENT_FULL_PATH, launchAgent = TEST_LAUNCH_AGENT_POOF)
    else:
        # Ignore other OSs
        pass


def test_launchdConfig():
    if LAUNCH_AGENT_OS == 'Darwin':
        plist = launchdConfig(targetOS = LAUNCH_AGENT_OS, agentFile = TEST_LAUNCH_AGENT_FULL_PATH, launchAgent = TEST_LAUNCH_AGENT_POOF)

        assert len(plist)

        disable(targetOS = LAUNCH_AGENT_OS, agentFile = TEST_LAUNCH_AGENT_FULL_PATH, launchAgent = TEST_LAUNCH_AGENT_POOF)
    else:
        # Ignore other OSs
        pass

