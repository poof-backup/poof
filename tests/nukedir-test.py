# See: https://github.com/poof-backup/poof/blob/master/LICENSE.txt


from poof.nukedir import nukeDirectory

import os
import pytest


TEST_POOF_CONF_DIR   = './tests/config'


def test_nukeDirectory():
    bogusDir = os.path.join(TEST_POOF_CONF_DIR, 'bogusxxxxx1213')
    errorsList = nukeDirectory(bogusDir)
    assert len(errorsList)

    os.makedirs(bogusDir, exist_ok = True)
    errorsList = nukeDirectory(bogusDir)
    assert not len(errorsList)

