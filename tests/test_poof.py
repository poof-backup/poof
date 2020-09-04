# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


from poof import _parseCLI
from poof import die
from poof import main
from poof import verifyEnvironment
from poof import RCLONE_PROG_TEST

import copy
import sys

import pytest


# *** pre-test ***

realArgs = copy.deepcopy(sys.argv)
del sys.argv[1:]
sys.argv.append('test')


# *** tests ***

def test__parseCLI():
    config = _parseCLI()
    assert config['command'] == 'test'

    del(sys.argv[1])

    sys.argv.append('bogus')

    with pytest.raises(NotImplementedError):
        config = _parseCLI()

    del(sys.argv[1])

    sys.argv.append('test')


def test_verifyEnvironment():
    assert verifyEnvironment(program = RCLONE_PROG_TEST)
    assert not verifyEnvironment(program = 'bogusxxxxx1213')
    raise NotImplementedError


def test_die():
    die('nothing to do', 0)


def test_main():
    assert main() == True

