# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


from unittest.mock import patch

from poof import PoofStatus
from poof import RCLONE_PROG_TEST
from poof import _parseCLI
from poof import die
from poof import getOrCreateCloningConfiguration
from poof import getOrCreateConfiguration
from poof import main
from poof import neuter
from poof import verifyEnvironment
from poof import viewConfig

import copy
import json
import os
import shutil
import sys

import pytest


# *** pre-test ***

realArgs = copy.deepcopy(sys.argv)
del sys.argv[1:]
sys.argv.append('test')

TEST_CLOUD_TYPE      = 's3'
TEST_POOF_CONF_DIR   = './tests/config'
TEST_POOF_CONF_FILES = {
    'poof.conf': os.path.join(TEST_POOF_CONF_DIR, 'poof.conf'),
    'rclone-poof.conf': os.path.join(TEST_POOF_CONF_DIR, 'rclone-poof.conf'),
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
            shutil.rmtree(TEST_POOF_CONF_DIR)
        except:
            pass


def test_getOrCreateConfiguration():
    poofConfFile = TEST_POOF_CONF_FILES['poof.conf']

    if os.path.exists(poofConfFile):
        _nukeTestConfigDir()

    poofConf = getOrCreateConfiguration(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR)

    assert poofConf['confFile'] == poofConfFile
    assert TEST_POOF_CONF_DIR in poofConf['paths']


def test_getOrCreateCloningConfiguration():
    conf = getOrCreateCloningConfiguration(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR)

    assert conf.get('my-poof', 'type') == TEST_CLOUD_TYPE


def test_verifyEnvironment():
    bogusCloningProgram = 'bogusxxxxx1213'
    _nukeTestConfigDir()

    assert verifyEnvironment(component = bogusCloningProgram, confFiles = TEST_POOF_CONF_FILES) == (bogusCloningProgram, PoofStatus.MISSING_CLONING_PROGRAM)
    assert verifyEnvironment(component = RCLONE_PROG_TEST, confFiles = TEST_POOF_CONF_FILES, allCompoents = False) == (None, PoofStatus.OK)
    assert verifyEnvironment(component = RCLONE_PROG_TEST, confFiles = TEST_POOF_CONF_FILES) == ('poof.conf', PoofStatus.MISSING_CONFIG_FILE)
    poofConf = getOrCreateConfiguration(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR) 
    assert verifyEnvironment(component = RCLONE_PROG_TEST, confFiles = TEST_POOF_CONF_FILES) == ('rclone-poof.conf', PoofStatus.MISSING_CONFIG_FILE)
    getOrCreateCloningConfiguration(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR)

    assert len(poofConf['paths']) == 1 # Only for testing - one entry, itself

    poofConf['paths']['/tmp'] = 'tmp'
    with open(TEST_POOF_CONF_FILES['poof.conf'], 'w') as outputFile:
        json.dump(poofConf, outputFile)

    assert verifyEnvironment(component = RCLONE_PROG_TEST, confFiles = TEST_POOF_CONF_FILES) == (TEST_POOF_CONF_FILES['rclone-poof.conf'], PoofStatus.WARN_MISCONFIGURED)
    # TODO: All failure cases tested, normal op is ignored for now.
    # assert verifyEnvironment(component = RCLONE_PROG_TEST, confFiles = TEST_POOF_CONF_FILES) == (None, PoofStatus.OK)


def test_die():
    die('nothing to do', 0)


def test__clone():
    with patch('poof._clone') as _clone:
        # Nothing to do in the unit test - this needs integration testing fo' sho'
        assert _clone(confDir = TEST_POOF_CONF_DIR)


def test_upload():
    with patch('poof.upload') as upload:
        # Nothing to do in the unit test - this needs integration testing fo' sho'
        assert upload(confDir = TEST_POOF_CONF_DIR)


def test_download():
    with patch('poof.download') as download:
        assert download(confDir = TEST_POOF_CONF_DIR)


def test_viewConfig():
    # TODO: Implementation
#     conf, cloneConf = viewConfig(confFiles = TEST_POOF_CONF_FILES)
#     raise NotImplementedError
    pass


def test_neuter():
    mode = os.stat(TEST_POOF_CONF_DIR).st_mode
    os.chmod(TEST_POOF_CONF_DIR, 0)
    with pytest.raises(Exception):
        neuter(TEST_POOF_CONF_DIR)
    os.chmod(TEST_POOF_CONF_DIR, mode)

    neuter(TEST_POOF_CONF_DIR)


def test_main():
    assert main() == True


# test_getOrCreateConfiguration()
# test_getOrCreateCloningConfiguration()
# test_verifyEnvironment()
# test_viewConfig()

