# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


from enum import Enum

from appdirs import AppDirs

import argparse
import configparser
import json
import shutil
import os
import sys


# *** constants ***

RCLONE_PROG      = 'rclone'
RCLONE_PROG_TEST = 'ls'
VALID_COMMANDS   = ( 'upload', 'download', 'config', 'cconfig', 'verify', 'test' )

EPILOG = """
%s must be available in PATH and configured, otherwise there's no way to
trasnfer the files to/from the cloud.
""" % RCLONE_PROG

# -------------------- 

POOF_CONFIG_DIR = AppDirs('poof', os.environ['USER']).user_config_dir
POOF_CONFIG_FILES = {
    'poof.config': os.path.join(POOF_CONFIG_DIR, 'poof.config'),
    'rclone-poof.config': os.path.join(POOF_CONFIG_DIR, 'rclone-poof.config'),
}


# --- states ---

class ConfigStatus(Enum):
    OK                      = 0
    MISSING_POOF_CONFIG     = 1
    MISSING_CLONING_CONFIG  = 2
    INVALID_POOF_CONFIG     = 3
    INVALID_CLONING_CONFIG  = 4
    MISSING_CLONING_PROGRAM = 5
    MISSING_CONFIG_FILE     = 6


# *** functions ***

def _parseCLI():
    config = dict()
    parser = argparse.ArgumentParser()

    parser.add_argument('command', type=str, help = '|'.join(VALID_COMMANDS))

    args = parser.parse_args()
    
    config['command'] = args.command

    if config['command'] not in VALID_COMMANDS:
        # TODO: Define a cleaner exit here.
        raise NotImplementedError

    return config


def _initializeConfigIn(configFile, configDir):
    if not os.path.exists(configFile):
        os.makedirs(configDir, exist_ok = True)
        with open(configFile, 'w') as outputFile:
            paths       = [ configDir ]
            basicConfig = { 'configFile': configFile, 'paths': paths }
            json.dump(basicConfig, outputFile, indent = 4, sort_keys = True)


def _initCloningScaffold():
    config = configparser.ConfigParser()

    section  = 'my-poof'
    scaffold = {
        'type': 's3',
        'provider': 'AWS',
        'env_auth': 'false',
        'access_key_id': 'BOGUS-KEY-USE-YOURS',
        'secret_access_key': 'BOGUS-SECRET-KEY-USE-YOURS',
        'region': 'eu-west-1',
        'location_constraint': 'eu-west-1',
        'acl': 'private',
        'storage_class': 'STANDARD_IA',
        'chunk_size': '8M',
        'upload_concurrency': '2',
        'server_side_encryption': 'AES256',
    }
    config.add_section(section)

    for option, value in scaffold.items():
        config.set(section, option, value)

    return config



def _initializeCloningConfigIn(configFile, configDir):
    if not os.path.exists(configFile):
        cloningConfig = _initCloningScaffold()
        with open(configFile, 'w') as outputFile:
            cloningConfig.write(outputFile)


def getOrCreateConfiguration(configFiles = POOF_CONFIG_FILES, configDir = POOF_CONFIG_DIR):
    configFile = configFiles['poof.config']
    _initializeConfigIn(configFile, configDir)

    with open(configFile, 'r') as inputFile:
        config = json.load(inputFile)

    return config


def getOrCreateCloningConfiguration(configFiles = POOF_CONFIG_FILES, configDir = POOF_CONFIG_DIR): 
    configFile = configFiles['rclone-poof.config']
    _initializeCloningConfigIn(configFile, configDir)

    cloningConfig = configparser.ConfigParser()
    with open(configFile, 'r') as inputFile:
        cloningConfig.read_file(inputFile)

    return cloningConfig


def verifyEnvironment(program = RCLONE_PROG, configFiles = POOF_CONFIG_FILES, allCompoents = True):
    status = ConfigStatus.OK

    if not shutil.which(program):
        return program, ConfigStatus.MISSING_CLONING_PROGRAM

    print('%s - %s' % (program, status))

    if allCompoents:
        for key, value in configFiles.items():
            if not os.path.exists(value):
                status = ConfigStatus.MISSING_CONFIG_FILE

            print('%s - %s' % (key, status))

            if status != ConfigStatus.OK:
                return key, status

    return None, status


def die(message, exitCode = 0):
    print(message)
    if exitCode:
        sys.exit(exitCode)


def main():
    command = _parseCLI()['command']

    if command == 'test':
        return True
    elif command == 'verify':
        if not verifyEnvironment():
            die(EPILOG, 1)


# *** main ***

if '__main__' == __name__:
    main()

