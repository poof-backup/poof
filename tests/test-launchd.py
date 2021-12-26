# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


from poof.launchd import isSupported
from poof.launchd import plist
from poof.launchd import LAUNCH_AGENT_OS

import platform

import pytest


# --- tests ---

def test_monitos():
    assert isSupported(LAUNCH_AGENT_OS)
    assert not isSupported('Linux')
    assert not isSupported('Windows')


def test_plist():
    with pytest.raises(NotImplementedError):
        plist()

