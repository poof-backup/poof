# See: https://github.com/poof-backup/poof/blob/master/LICENSE.txt


from poof.nukedir import _getNukeDirectoryArgsLinux
from poof.nukedir import _getNukeDirectoryArgsMac
from poof.nukedir import _getNukeDirectoryArgsWindows
from poof.nukedir import nukeDirectory
from poof.nukedir import nukeDirectoryProcess

import os
import pytest


TEST_POOF_CONF_DIR   = './tests/config'


def test__getNukeDirectoryArgsMac():
    path = '/tmp/bogus'
    argsList = _getNukeDirectoryArgsMac(path)
    assert isinstance(argsList, tuple)
    assert argsList[1] == '-Prf'


def test__getNukeDirectoryArgsLinux():
    path = '/tmp/bogus'
    argsList = _getNukeDirectoryArgsLinux(path)
    assert isinstance(argsList, tuple)
    assert argsList[1] == '-Rf'


def test__getNukeDirectoryArgsWindows():
    path = '/tmp/bogus'
    with pytest.raises(NotImplementedError):
        _getNukeDirectoryArgsWindows(path)
        pass


def test_nukeDirectoryProcess():
    bogusDir = os.path.join(TEST_POOF_CONF_DIR, 'bogusxxxxx1213')
    status, error = nukeDirectoryProcess(bogusDir)
    assert not status

    os.makedirs(bogusDir, exist_ok = True)
    status, error = nukeDirectoryProcess(bogusDir)
    assert status


# TODO: Fix DRY!  This is only tests scaffolding.
def test_nukeDirectory():
    bogusDir = os.path.join(TEST_POOF_CONF_DIR, 'bogusxxxxx1213')
    status, error = nukeDirectory(bogusDir)
    assert not status

    os.makedirs(bogusDir, exist_ok = True)
    status, error = nukeDirectory(bogusDir)
    assert status

