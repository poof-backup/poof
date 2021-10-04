# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


from datetime import timedelta
from unittest.mock import patch

from click.testing import CliRunner

from poof import PoofStatus
from poof import RCLONE_PROG_TEST
from poof import _cconfig
from poof import _config
from poof import _neuter
from poof import _nukeDirectory
from poof import _nukeDirectoryLinux
from poof import _nukeDirectoryMac
from poof import _timeLapsed
from poof import _verify
from poof import die
from poof import paths

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

def _nukeTestConfigDir():
        try:
            shutil.rmtree(TEST_POOF_CONF_DIR)
        except:
            pass


def test__config():
    poofConfFile = TEST_POOF_CONF_FILES['poof.conf']

    if os.path.exists(poofConfFile):
        _nukeTestConfigDir()

    poofConf = _config(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR)

    assert poofConf['confFile'] == poofConfFile
    assert TEST_POOF_CONF_DIR in poofConf['paths']


def test__cconfig():
    conf = _cconfig(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR)

    assert conf.get('my-poof', 'type') == TEST_CLOUD_TYPE


def test__timeLapsed():
    testTime = timedelta(hours = 1, minutes = 1, seconds = 1)
    hours, minutes, seconds = _timeLapsed(testTime)
    assert hours == 1
    assert minutes == 1
    assert seconds == 1

    testTime = timedelta(hours = 0, minutes = 1, seconds = 1)
    hours, minutes, seconds = _timeLapsed(testTime)
    assert hours == 0
    assert minutes == 1
    assert seconds == 1

    testTime = timedelta(hours = 1, minutes = 0, seconds = 1)
    hours, minutes, seconds = _timeLapsed(testTime)
    assert hours == 1
    assert minutes == 0
    assert seconds == 1


def test__verify():
    bogusCloningProgram = 'bogusxxxxx1213'
    _nukeTestConfigDir()

    assert _verify(component = bogusCloningProgram, confFiles = TEST_POOF_CONF_FILES) == (bogusCloningProgram, PoofStatus.MISSING_CLONING_PROGRAM)
    assert _verify(component = RCLONE_PROG_TEST, confFiles = TEST_POOF_CONF_FILES, allComponents = False) == (None, PoofStatus.OK)
    assert _verify(component = RCLONE_PROG_TEST, confFiles = TEST_POOF_CONF_FILES) == ('poof.conf', PoofStatus.MISSING_CONFIG_FILE)
    poofConf = _config(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR) 
    assert _verify(component = RCLONE_PROG_TEST, confFiles = TEST_POOF_CONF_FILES) == ('rclone-poof.conf', PoofStatus.MISSING_CONFIG_FILE)
    _cconfig(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR)

    assert len(poofConf['paths']) == 1 # Only for testing - one entry, itself

    poofConf['paths']['/tmp'] = 'tmp'
    with open(TEST_POOF_CONF_FILES['poof.conf'], 'w') as outputFile:
        json.dump(poofConf, outputFile)

    assert _verify(component = RCLONE_PROG_TEST, confFiles = TEST_POOF_CONF_FILES) == (TEST_POOF_CONF_FILES['rclone-poof.conf'], PoofStatus.WARN_MISCONFIGURED)


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


def test_backup():
    with patch('poof.backup') as backup:
        assert backup(confDir = TEST_POOF_CONF_DIR)


def test__neuter():
    mode = os.stat(TEST_POOF_CONF_DIR).st_mode
    os.chmod(TEST_POOF_CONF_DIR, 0)
    with pytest.raises(Exception):
        _neuter(TEST_POOF_CONF_DIR, unitTest = True)
    os.chmod(TEST_POOF_CONF_DIR, mode)

    _neuter(TEST_POOF_CONF_DIR, unitTest = True)


def test_paths():
    assert CliRunner().invoke(paths)


def test__nukeDirectoryMac():
    bogusDir = os.path.join(TEST_POOF_CONF_DIR, 'bogusxxxxx1213')
    os.makedirs(bogusDir, exist_ok = True)
    status, error = _nukeDirectoryMac(bogusDir)
    assert status


def test__nukeDirectoryLinux():
    # TODO:  https://github.com/poof-backup/poof/issues/35
    assert True


def test__nukeDirectory():
    bogusDir = os.path.join(TEST_POOF_CONF_DIR, 'bogusxxxxx1213')
    status, error = _nukeDirectory(bogusDir)
    assert not status

    os.makedirs(bogusDir, exist_ok = True)
    status, error = _nukeDirectory(bogusDir)
    assert status

