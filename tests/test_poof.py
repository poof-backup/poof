# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


from poof import ConfigStatus
from poof import RCLONE_PROG_TEST
from poof import _parseCLI
from poof import die
from poof import getOrCreateCloningConfiguration
from poof import getOrCreateConfiguration
from poof import main
from poof import verifyEnvironment

import copy
import os
import shutil
import sys

import pytest


# *** pre-test ***

realArgs = copy.deepcopy(sys.argv)
del sys.argv[1:]
sys.argv.append('test')

TEST_CLOUD_TYPE        = 's3'
TEST_POOF_CONFIG_DIR   = './tests/config'
TEST_POOF_CONFIG_FILES = {
    'poof.config': os.path.join(TEST_POOF_CONFIG_DIR, 'poof.config'),
    'rclone-poof.config': os.path.join(TEST_POOF_CONFIG_DIR, 'rclone-poof.config'),
}


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


def _nukeTestConfigDir():
        try:
            shutil.rmtree(TEST_POOF_CONFIG_DIR)
        except:
            pass


def test_getOrCreateConfiguration():
    poofConfigFile = TEST_POOF_CONFIG_FILES['poof.config']

    if os.path.exists(poofConfigFile):
        _nukeTestConfigDir()

    poofConfig = getOrCreateConfiguration(TEST_POOF_CONFIG_FILES, TEST_POOF_CONFIG_DIR)

    assert poofConfig['configFile'] == poofConfigFile
    assert TEST_POOF_CONFIG_DIR in poofConfig['paths']


def test_getOrCreateCloningConfiguration():
    config = getOrCreateCloningConfiguration(TEST_POOF_CONFIG_FILES, TEST_POOF_CONFIG_DIR)

    assert config.get('my-poof', 'type') == TEST_CLOUD_TYPE


def test_verifyEnvironment():
    bogusCloningProgram = 'bogusxxxxx1213'
    _nukeTestConfigDir()

    assert verifyEnvironment(program = bogusCloningProgram, configFiles = TEST_POOF_CONFIG_FILES) == (bogusCloningProgram, ConfigStatus.MISSING_CLONING_PROGRAM)
    assert verifyEnvironment(program = RCLONE_PROG_TEST, configFiles = TEST_POOF_CONFIG_FILES, allCompoents = False) == (None, ConfigStatus.OK)

    raise NotImplementedError


def test_die():
    die('nothing to do', 0)


def test_main():
    assert main() == True


# test_verifyEnvironment()

