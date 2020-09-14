# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


from enum import Enum

from appdirs import AppDirs

import argparse
import configparser
import json
import shutil
import os
import stat
import subprocess
import sys


# *** constants ***

RCLONE_PROG      = 'rclone'
RCLONE_PROG_TEST = 'ls' # a program we know MUST exist to the which command
VALID_COMMANDS   = ( 
        'cconfig',
        'config',
        'download',
        'neuter',
        'test',
        'upload',
        'verify',
        'view',
    )

EPILOG = """
%s must be available in PATH and configured, otherwise there's no way to
trasnfer the files to/from the cloud.
""" % RCLONE_PROG

# -------------------- 

POOF_CONFIG_DIR = AppDirs('poof', os.environ['USER']).user_config_dir
POOF_CONFIG_FILES = {
    'poof.conf': os.path.join(POOF_CONFIG_DIR, 'poof.conf'),
    'rclone-poof.conf': os.path.join(POOF_CONFIG_DIR, 'rclone-poof.conf'),
}


# --- states ---

class PoofStatus(Enum):
    OK                      = 0
    MISSING_POOF_CONFIG     = 1
    MISSING_CLONING_CONFIG  = 2
    INVALID_POOF_CONFIG     = 3
    INVALID_CLONING_CONFIG  = 4
    MISSING_CLONING_PROGRAM = 5
    MISSING_CONFIG_FILE     = 6
    WARN_MISCONFIGURED      = 100


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


def _initializeConfigIn(confFile, confDir):
    if not os.path.exists(confFile):
        os.makedirs(confDir, exist_ok = True)
        with open(confFile, 'w') as outputFile:
            paths = {
                confDir: 'unittest',
            }
            basicConfig = {
                'bucket': 'poofbackup',
                'confFile': confFile,
                'paths': paths,
                'remote': 'poof', # rclone .INI section
            }
            json.dump(basicConfig, outputFile, indent = 2, sort_keys = True)
        os.chmod(confFile, stat.S_IRUSR | stat.S_IWUSR)


def _initCloningScaffold():
    conf = configparser.ConfigParser()

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
    conf.add_section(section)

    for option, value in scaffold.items():
        conf.set(section, option, value)

    return conf



def _initializeCloningConfigIn(confFile, confDir):
    if not os.path.exists(confFile):
        cloningConf = _initCloningScaffold()
        with open(confFile, 'w') as outputFile:
            cloningConf.write(outputFile)

        os.chmod(confFile, stat.S_IRUSR | stat.S_IWUSR)


def getOrCreateConfiguration(confFiles = POOF_CONFIG_FILES, confDir = POOF_CONFIG_DIR):
    confFile = confFiles['poof.conf']
    _initializeConfigIn(confFile, confDir)

    with open(confFile, 'r') as inputFile:
        conf = json.load(inputFile)

    return conf


def getOrCreateCloningConfiguration(confFiles = POOF_CONFIG_FILES, confDir = POOF_CONFIG_DIR): 
    confFile = confFiles['rclone-poof.conf']
    _initializeCloningConfigIn(confFile, confDir)

    cloningConf = configparser.ConfigParser()
    with open(confFile, 'r') as inputFile:
        cloningConf.read_file(inputFile)

    return cloningConf


def verifyEnvironment(component = RCLONE_PROG, confFiles = POOF_CONFIG_FILES, allCompoents = True):
    status = PoofStatus.OK

    if not shutil.which(component):
        return component, PoofStatus.MISSING_CLONING_PROGRAM

    print('installed %s? - %s' % (component, status))

    if allCompoents:
        for component, path in confFiles.items():
            if not os.path.exists(path):
                status = PoofStatus.MISSING_CONFIG_FILE

            print('exists %s? - %s' % (component, status))

            if status != PoofStatus.OK:
                return component, status

        # heuristic:
        conf = getOrCreateConfiguration(confFiles, confDir = POOF_CONFIG_DIR)
        if len(conf['paths']) == 1:
            component = confFiles['poof.conf']
            status    = PoofStatus.WARN_MISCONFIGURED
            print('configuration %s? - %s' % (component, status))

            return component, status

        # heuristic:
        cloningConf = getOrCreateCloningConfiguration(confFiles, POOF_CONFIG_DIR)
        for section in cloningConf.sections():
            if cloningConf.get(section, 'secret_access_key') == 'BOGUS-SECRET-KEY-USE-YOURS':
                component = confFiles['rclone-poof.conf']
                status    = PoofStatus.WARN_MISCONFIGURED
                print('configuration %s? - %s' % (component, status))

                return component, status

    return None, status


def die(message, exitCode = 0):
    print(message)
    if exitCode:
        sys.exit(exitCode)


def neuter(confDir = POOF_CONFIG_DIR):
    try:
        shutil.rmtree(confDir)
    except FileNotFoundError:
        pass  # Already not here


def _clone(toCloud, confDir = POOF_CONFIG_DIR, confFiles = POOF_CONFIG_FILES):
    _, status = verifyEnvironment(confFiles = confFiles)

    if status != PoofStatus.OK:
        die("cannot poof the files to the cloud", 4)

    conf    = getOrCreateConfiguration()
    poofDir = None

    for localDir, cloudDir in conf['paths'].items():
        if toCloud:
            args = ( RCLONE_PROG,
                    '--config',
                    confFiles['rclone-poof.conf'],
                    '-v',
                    'sync', 
                    localDir,
                    '%s:%s/%s' % (conf['remote'], conf['bucket'], cloudDir),
                  )
        else:
            args = ( RCLONE_PROG,
                    '--config',
                    confFiles['rclone-poof.conf'],
                    '-v',
                    'sync', 
                    '%s:%s/%s' % (conf['remote'], conf['bucket'], cloudDir),
                    localDir,
                  )
        result = subprocess.run(args)

        try:
            result.check_returncode()
        except:
            die('%s failed = %d - see output for details' % (RCLONE_PROG, result.returncode), 3)

        if toCloud and 'poof' not in localDir:
            shutil.rmtree(localDir)
        else:
            poofDir = localDir

    if toCloud and poofDir:
        neuter(confDir)

    return True


def upload(confDir = POOF_CONFIG_DIR, confFiles = POOF_CONFIG_FILES):
    return _clone(True, confDir = confDir, confFiles = confFiles)


def download(confDir = POOF_CONFIG_DIR, confFiles = POOF_CONFIG_FILES):
    return _clone(False, confDir = confDir, confFiles = confFiles)


def viewConfig(confFiles = POOF_CONFIG_FILES):
#     component, status = verifyEnvironment(confFiles = confFiles)
# 
#     if status != PoofStatus.OK:
#         return component, status
# 
#     conf = getOrCreateConfiguration(confFiles = confFiles)
#     cloneConf = getOrCreateCloningConfiguration(confFiles = confFiles)
# 
#     return conf, cloneConf
    raise NotImplementedError


def main():
    command = _parseCLI()['command']

    if command == 'test':
        return True
    elif command == 'config':
        getOrCreateConfiguration()
    elif command == 'cconfig':
        getOrCreateCloningConfiguration()
    elif command == 'download':
        download()
    elif command == 'neuter':
        try:
            neuter()
        except Exception as e:
            die('unable to neuter poof directory at %s - %s' % (POOF_CONFIG_DIR, e), 2)
    elif command == 'upload':
        upload()
    elif command == 'verify':
        if verifyEnvironment() != (None, PoofStatus.OK):
            die(EPILOG, 1)


# *** main ***

if '__main__' == __name__:
    main()

