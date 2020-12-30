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

import click
import psutil


# *** constants ***

RCLONE_PROG      = 'rclone'
RCLONE_PROG_TEST = 'ls' # a program we know MUST exist to the which command
SPECIAL_DIRS     = ( 'Downloads', 'Documents' )
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


class Configuration(object):
    def __init__(self):
        self.confDir = POOF_CONFIG_DIR       
        self.confFiles = POOF_CONFIG_FILES


globalConf = click.make_pass_decorator(Configuration, ensure = True)


# *** functions ***

@click.group()
@click.option('--confdir', default = POOF_CONFIG_DIR, help = 'poof configuration directory', show_default = True)
@click.option('--poofconf', default = POOF_CONFIG_FILES['poof.conf'], help = 'poof configuration file', show_default = True)
@click.option('--rcloneconf', default = POOF_CONFIG_FILES['rclone-poof.conf'], help = 'rclone configuration file', show_default = True)
@globalConf
def main(conf, confdir, poofconf, rcloneconf):
    # IMPORTANT - it must exist before declaring the functions, top-down,
    # because of the decorator.
    conf.confDir   = confdir
    conf.confFiles = { 'poof.conf': poofconf, 'rclone-poof.conf': rcloneconf, }

    
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


def die(message, exitCode = 0):
    print(message)
    if exitCode:
        sys.exit(exitCode)


def _nukeDirectory(path):
    result = True
    error  = None

    try:
        shutil.rmtree(path)
    except Exception as e:
        error  = e 
        result = False

    return result, error


@main.command()
@globalConf
def config(conf):
    confFile = conf.confFiles['poof.conf']
    _initializeConfigIn(confFile, conf.confDir)

    with open(confFile, 'r') as inputFile:
        actualConfiguration = json.load(inputFile)

    return actualConfiguration


def _clone(toCloud, confDir = POOF_CONFIG_DIR, confFiles = POOF_CONFIG_FILES, nukeLocal = True):
    _, status = verify(confFiles = confFiles)

    if status != PoofStatus.OK:
        die("cannot poof the files to the cloud", 4)

    conf    = _config()
    poofDir = None

    for localDir, cloudDir in conf['paths'].items():
        if localDir.endswith(os.sep):
            localDir = localDir[:-1]

        if toCloud:
            args = ( RCLONE_PROG,
                    '--config',
                    confFiles['rclone-poof.conf'],
                    # TODO: Issue #20
                    '-P',
                    'sync', 
                    localDir,
                    '%s:%s/%s' % (conf['remote'], conf['bucket'], cloudDir),
                  )
            processingItem = localDir
        else:
            cloudPath ='%s:%s/%s' % (conf['remote'], conf['bucket'], cloudDir) 
            args = ( RCLONE_PROG,
                    '--config',
                    confFiles['rclone-poof.conf'],
                    # TODO: Issue #20
                    '-P',
                    'sync', 
                    cloudPath,
                    localDir,
                  )
            processingItem = cloudPath

        print('\nprocessing: %s' % processingItem)
        result = subprocess.run(args)

        try:
            result.check_returncode()
        except:
            die('%s failed = %d - see output for details' % (RCLONE_PROG, result.returncode), 3)

        if toCloud and 'poof' not in localDir and nukeLocal:
            status, error = _nukeDirectory(localDir)
            if not status:
                dirItem = os.path.split(error.filename)[1].replace(os.sep, '')
                if dirItem in SPECIAL_DIRS:
                    print('  > special dir %s not deleted' % localDir)
                else:
                    die('%s while removing %s' % (error, os.path.join(localDir, dirItem)), 5)
        elif nukeLocal:
            poofDir = localDir

    if toCloud and poofDir:
        neuter(confDir)

    return True


@main.command()
@globalConf
def backup(conf):
    return _clone(True, confDir = conf.confDir, confFiles = conf.confFiles, nukeLocal = False)


@main.command()
def download(confDir = POOF_CONFIG_DIR, confFiles = POOF_CONFIG_FILES):
    print('download in progress!')
    return False
#     return _clone(False, confDir = confDir, confFiles = confFiles)


@main.command()
def paths():
    for key, item in POOF_CONFIG_FILES.items():
        print('%s = %s' % (key, item))

    return True


@main.command()
def neuter(confDir = POOF_CONFIG_DIR):
#     try:
#         shutil.rmtree(confDir)
#     except FileNotFoundError:
#         pass  # Already not here
    print('neuter in progress!')
    return False


@main.command()
def upload(confDir = POOF_CONFIG_DIR, confFiles = POOF_CONFIG_FILES):
    print('upload in progress!')
    return False
#     return _clone(True, confDir = confDir, confFiles = confFiles)


def _cconfig(confFiles = POOF_CONFIG_FILES, confDir = POOF_CONFIG_DIR): 
    confFile = confFiles['rclone-poof.conf']
    _initializeCloningConfigIn(confFile, confDir)

    cloningConf = configparser.ConfigParser()
    with open(confFile, 'r') as inputFile:
        cloningConf.read_file(inputFile)

    return cloningConf

@main.command()
def cconfig():
    _cconfig()


def viewConfig(confFiles = POOF_CONFIG_FILES):
# TODO: EC
#     component, status = verifyEnvironment(confFiles = confFiles)
# 
#     if status != PoofStatus.OK:
#         return component, status
# 
#     conf = config(confFiles = confFiles)
#     cloneConf = cconf(confFiles = confFiles)
# 
#     return conf, cloneConf
    raise NotImplementedError



@main.command()
@click.option('--component', default = RCLONE_PROG, help = 'Component to check', show_default = True)
@globalConf
def verify(conf, component, allCompoents = True):
    status = PoofStatus.OK

    if not shutil.which(component):
        return component, PoofStatus.MISSING_CLONING_PROGRAM

    print('installed %s? - %s' % (component, status))

    if allCompoents:
        for component, path in conf.confFiles.items():
            if not os.path.exists(path):
                status = PoofStatus.MISSING_CONFIG_FILE

            print('exists %s? - %s' % (component, status))

            if status != PoofStatus.OK:
                return component, status

        # heuristic:
#         confFile = config(conf)
#         print('000000000')
#         if len(confFile['paths']) == 1:
#             component = confFile['poof.conf']
#             status    = PoofStatus.WARN_MISCONFIGURED
#             print('configuration %s? - %s' % (component, status))
# 
#             return component, status

        # heuristic:
        cloningConf = _cconfig(conf.confFiles, POOF_CONFIG_DIR)
        for section in cloningConf.sections():
            if cloningConf.get(section, 'secret_access_key') == 'BOGUS-SECRET-KEY-USE-YOURS':
                component = conf.confFiles['rclone-poof.conf']
                status    = PoofStatus.WARN_MISCONFIGURED
                print('configuration %s? - %s' % (component, status))

                return component, status

    return None, status


# @click.group()
# def main():
#     pass
#     command = _parseCLI()['command']
# 
#     if command == 'test':
#         return True
#     elif command == 'backup':
#         backup()
#     elif command == 'config':
#         getOrCreateConfiguration()
#     elif command == 'cconfig':
#         getOrCreateCloningConfiguration()
#     elif command == 'download':
#         download()
#     elif command == 'neuter':
#         try:
#             neuter()
#         except Exception as e:
#             die('unable to neuter poof directory at %s - %s' % (POOF_CONFIG_DIR, e), 2)
#     elif command == 'paths':
#         outputPaths()
#     elif command == 'upload':
#         upload()
#     elif command == 'verify' or command == 'check':
#         if verifyEnvironment() != (None, PoofStatus.OK):
#             die(EPILOG, 1)


# *** main ***

# if '__main__' == __name__:
#     main()

