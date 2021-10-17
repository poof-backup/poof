# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


from datetime import datetime
from enum import Enum

from appdirs import AppDirs

import configparser
import json
import os
import platform
import shutil
import stat
import subprocess
import sys

import click


# *** constants ***

__VERSION__ = "1.1.6"

RCLONE_PROG      = 'rclone'
RCLONE_PROG_TEST = 'ls' # a program we know MUST exist to the which command
SPECIAL_DIRS     = (
    'Desktop',
    'Documents',
    'Downloads',
    'Movies',
    'Music',
    'Pictures',
    'Public',
    'Shared',
    'Sites',
    'Updates',
    'VirtualBox VMs',
)

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
_startPoof = datetime.now()


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
                'remote': 'my-poof', # rclone .INI section
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
    click.echo(click.style(message, fg='red'))
    if exitCode:
        sys.exit(exitCode)

# TODO:  use the Python API instead of calling external OS-levels commands here?
#        Neither rm -P nor srm are standard, and neither has much effect on
#        actual security since they don't work on SSDs anyway.
def _getNukeDirectoryArgsMac(path):
	args = (
		'/bin/rm',
		'-Prfv',
		path,
	)
	return args

def _getNukeDirectoryArgsLinux(path):
	args = (
		'/bin/rm',
		'-Rfv',
		path,
	)
	return args

def _nukeDirectory(path):
    result = False
    error  = Exception()
    args = False

    hostPlatform = platform.system()

    if os.path.exists(path):
        if 'Darwin' == hostPlatform:
            args =  _getNukeDirectoryArgsMac(path)
        elif 'Linux' == hostPlatform:
            args =  _getNukeDirectoryArgsLinux(path)

    if args:
        procResult = subprocess.run(args)
        result = not procResult.returncode

    return result, error


def _config(confFiles = POOF_CONFIG_FILES, confDir = POOF_CONFIG_DIR):
    confFile = confFiles['poof.conf']
    _initializeConfigIn(confFile, confDir)

    with open(confFile, 'r') as inputFile:
        actualConfiguration = json.load(inputFile)

    return actualConfiguration

@main.command()
@globalConf
def config(conf):
    """
Ensure that the poof.conf file exists;  creates it if not present.
"""
    return _config(conf.confFiles, conf.confDir)


def _clone(toCloud, confDir = POOF_CONFIG_DIR, confFiles = POOF_CONFIG_FILES, nukeLocal = True):
    _, status = _verify(confFiles = confFiles)

    if status != PoofStatus.OK:
        die("cannot poof the files to the cloud", 4)

    conf    = _config(confFiles = confFiles)
    poofDir = None

    for localDir, cloudDir in conf['paths'].items():
        if localDir.endswith(os.sep):
            localDir = localDir[:-1]

        if toCloud:
            args = ( RCLONE_PROG,
                    '--config',
                    confFiles['rclone-poof.conf'],
                    '-P',
                    '-L',
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
                    '-P',
                    'sync',
                    cloudPath,
                    localDir,
                  )
            processingItem = cloudPath

        click.secho('\nprocessing: %s' % processingItem)
        result = subprocess.run(args)

        try:
            result.check_returncode()
        except:
            die('%s failed = %d - see output for details' % (RCLONE_PROG, result.returncode), 3)

        if toCloud and 'poof' not in localDir and nukeLocal:
            status, error = _nukeDirectory(localDir)
            if not status:
                click.secho('  > dir %s may be system-protected' % localDir, fg = 'bright_cyan')
        elif nukeLocal:
            poofDir = localDir

    if toCloud and poofDir:
        _neuter(confDir)

    return True


def _timeLapsed(lapsed = None):
    if not lapsed:
        lapsed = datetime.now()-_startPoof

    hours, seconds   = divmod(lapsed.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    return hours, minutes, seconds


@main.command()
@globalConf
def backup(conf):
    """
Backup to remote without wiping out the local data.
"""
    click.echo(click.style('BACKUP IN PROGRESS - PLEASE DO NOT INTERRUPT', fg='yellow'))
    outcome = _clone(True, confDir = conf.confDir, confFiles = conf.confFiles, nukeLocal = False)
    h, m, s = _timeLapsed()
    click.echo(click.style(('BACKUP COMPLETED in %d:%02d:%02d' % (h, m, s)), fg='green'))

    return outcome


@main.command()
@globalConf
def download(conf):
    """
Download the files from the cloud and set them in their corresponding
directories.
"""
    click.echo(click.style('DOWNLOAD SYNC IN PROGRESS - PLEASE DO NOT INTERRUPT', fg='yellow'))
    outcome = _clone(False, confDir = conf.confDir, confFiles = conf.confFiles)
    h, m, s = _timeLapsed()
    click.echo(click.style(('DOWNLOAD COMPLETED in %d:%02d:%02d' % (h, m, s)), fg='green'))

    return outcome


@main.command()
def paths():
    """
Output the platform-specific paths to the poof configuration files.
"""
    for key, item in POOF_CONFIG_FILES.items():
        click.echo('%s = %s' % (key, item))

    return True


def _neuter(confDir = POOF_CONFIG_DIR, unitTest = False):
    try:
        shutil.rmtree(confDir)
    except FileNotFoundError:
        pass  # Already not here

    if not unitTest:
        try:
            args = (
                'pip',
                'uninstall',
                '-y',
                'poof',
            )
            subprocess.run(args)
        except:
            pass # Ignore if it requires root


@main.command()
@globalConf
def neuter(conf):
    """
Neuter this poof installation by deleting its configuration.
"""
    _neuter(conf.confDir)


@main.command()
@globalConf
def upload(conf):
    """
Upload all the files to the cloud drive and delete the local paths.
"""
    click.echo(click.style('UPLOAD SYNC IN PROGRESS - PLEASE DO NOT INTERRUPT', fg='yellow'))
    outcome = _clone(True, confDir = conf.confDir, confFiles = conf.confFiles)
    h, m, s = _timeLapsed()
    click.echo(click.style(('UPLOAD COMPLETED in %d:%02d:%02d' % (h, m, s)), fg='green'))

    return outcome


def _cconfig(confFiles = POOF_CONFIG_FILES, confDir = POOF_CONFIG_DIR):
    confFile = confFiles['rclone-poof.conf']
    _initializeCloningConfigIn(confFile, confDir)

    cloningConf = configparser.ConfigParser()
    with open(confFile, 'r') as inputFile:
        cloningConf.read_file(inputFile)

    return cloningConf


@main.command()
def cconfig():
    """
Ensure that the rclone-poof.conf file exists; creates it if not present.
"""
    _cconfig()


def _verify(component = RCLONE_PROG, confFiles = POOF_CONFIG_FILES, allComponents = True):
    status = PoofStatus.OK

    if not shutil.which(component):
        return component, PoofStatus.MISSING_CLONING_PROGRAM

    click.echo('installed %s? - %s' % (component, status))

    if allComponents:
        for component, path in confFiles.items():
            if not os.path.exists(path):
                status = PoofStatus.MISSING_CONFIG_FILE

            click.echo('exists %s? - %s' % (component, status))

            if status != PoofStatus.OK:
                return component, status

        # heuristic:
        poofConf = _config(confFiles, POOF_CONFIG_DIR)
        if len(poofConf['paths']) == 1:
            component = 'poof.conf'
            status    = PoofStatus.WARN_MISCONFIGURED
            click.echo('configuration %s? - %s: set the poof.config cloud backup path to something other than unittest' % (component, status))

            return component, status

        # heuristic:
        cloningConf = _cconfig(confFiles, POOF_CONFIG_DIR)
        for section in cloningConf.sections():
            if cloningConf.get(section, 'secret_access_key') == 'BOGUS-SECRET-KEY-USE-YOURS':
                component = confFiles['rclone-poof.conf']
                status    = PoofStatus.WARN_MISCONFIGURED
                click.echo('configuration %s? - %s' % (component, status))

                return component, status

        click.echo('configuration appears to be valid and has valid credentials')

    return None, status

@main.command()
@click.option('--component', default = RCLONE_PROG, help = 'Component to check', show_default = True)
@globalConf
def verify(conf, component, allComponents = True):
    """
    Verify the poof and cloning tool configurations.
    """
    return _verify(component, conf.confFiles, allComponents)

@main.command()
@globalConf
def version(_):
    """
    Print software version and exit.
    """
    click.echo('poof version %s' % (__VERSION__))
