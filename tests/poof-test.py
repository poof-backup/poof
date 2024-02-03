# See: https://github.com/poof-backup/poof/blob/master/LICENSE.txt


from datetime import timedelta
from unittest.mock import patch

from click.testing import CliRunner
from pyperclip import PyperclipException

from poof import PoofStatus
from poof import RCLONE_PROG_TEST
from poof import _CRYPT_BOGUS_SECRETS
from poof import _S3_BOGUS_SECRETS
from poof import _cconfig
from poof import _config
from poof import _cryptoggle
from poof import _display_launchdStatus
from poof import _econfig
from poof import _encryptionIsEnabled
from poof import _getNukeDirectoryArgsLinux
from poof import _getNukeDirectoryArgsMac
from poof import _getNukeDirectoryArgsWindows
from poof import _neuter
from poof import _nukeDirectory
from poof import _timeLapsed
from poof import _verify
from poof import _verifyBogusValuesIn
from poof import die
from poof import paths

import copy
import json
import os
import platform
import shutil
import sys

import pyperclip
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

    confStrSource = open(poofConfFile, 'r').read()

    try:
        confStrTarget = pyperclip.paste()
        assert confStrSource == confStrTarget
    except PyperclipException:
        pass # Linux


def test__cconfig():
    conf = _cconfig(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR)

    assert conf.get('poof-backup', 'type') == TEST_CLOUD_TYPE

    confStrSource = open(TEST_POOF_CONF_FILES['rclone-poof.conf'], 'r').read()

    try:
        confStrTarget = pyperclip.paste()
        assert confStrSource == confStrTarget
    except PyperclipException:
        pass # Linux


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


def test__verifyBogusValuesIn():
    component    = RCLONE_PROG_TEST
    conf         = _cconfig(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR)
    section      = 'poof-backup'
    bogusSecrets = copy.deepcopy(_S3_BOGUS_SECRETS)
    assert _verifyBogusValuesIn(component, conf, section, bogusSecrets) == PoofStatus.WARN_MISCONFIGURED

    bogusSecrets['secret_access_key'] = 'bogus-access-key-not-default'
    assert _verifyBogusValuesIn(component, conf, section, bogusSecrets) == PoofStatus.OK

    bogusSecrets = copy.deepcopy(_CRYPT_BOGUS_SECRETS)
    section      = 'poof-backup'
    assert _verifyBogusValuesIn(component, conf, section, bogusSecrets) == PoofStatus.ERROR_MISSING_KEY


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


def test__nukeDirectory():
    bogusDir = os.path.join(TEST_POOF_CONF_DIR, 'bogusxxxxx1213')
    status, error = _nukeDirectory(bogusDir)
    assert not status

    os.makedirs(bogusDir, exist_ok = True)
    status, error = _nukeDirectory(bogusDir)
    assert status


def test__econfig():
    with pytest.raises(NotImplementedError):
        _econfig()
        pass


def test__encryptionIsEnabled():
    poofConf = _config(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR)
    cloneConf = _cconfig(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR)

    assert not _encryptionIsEnabled(poofConf, cloneConf)

    cloneConf['poof-crypt'] = {
        'type': 'crypt',
        'remote': 'bogus-remote',
        'password': 'bogus-password-not-default',
        'password2': 'bogus-password2-not-default',
    }

    poofConf['remote'] = 'poof-crypt'

    assert _encryptionIsEnabled(poofConf, cloneConf)


def test__cryptoggle():
    poofConf = _config(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR)
    cloneConf = _cconfig(TEST_POOF_CONF_FILES, TEST_POOF_CONF_DIR)

    assert _cryptoggle(poofConf, cloneConf, confFiles = TEST_POOF_CONF_FILES) == PoofStatus.ENCRYPTION_DISABLED

    cloneConf['poof-crypt'] = { 'type': 'crypt', 'remote': 'poof-backup', }
    assert _cryptoggle(poofConf, cloneConf, confFiles = TEST_POOF_CONF_FILES) == PoofStatus.ENCRYPTION_ENABLED
    assert _cryptoggle(poofConf, cloneConf, confFiles = TEST_POOF_CONF_FILES) == PoofStatus.ENCRYPTION_DISABLED


def test__display_launchdStatus():
    if platform.system() == 'Darwin':
        assert _display_launchdStatus()
    else:
        assert not _display_launchdStatus()

