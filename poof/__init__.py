# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


from datetime import datetime
from enum import Enum

from appdirs import AppDirs
from pyperclip import PyperclipException

import configparser
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import uuid

import click
import pyperclip


# *** constants ***

__VERSION__ = "1.2.9"

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
_CRYPT_BOGUS_SECRETS = {
    'password': 'BOGUS-PASSWORD',
    'password2': 'BOGUS-PASSWORD2',

}
_S3_BOGUS_SECRETS = {
    'secret_access_key': 'BOGUS-SECRET-KEY-USE-YOURS',
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
    ENCRYPTION_ENABLED      = 7
    ENCRYPTION_DISABLED     = 8
    WARN_MISCONFIGURED      = 100
    ERROR_MISSING_KEY       = 200


class Configuration(object):
    def __init__(self):
        self.confDir = POOF_CONFIG_DIR
        self.confFiles = POOF_CONFIG_FILES
        self.verbose = False


globalConf = click.make_pass_decorator(Configuration, ensure = True)
_startPoof = datetime.now()


# *** functions ***

@click.group()
@click.option('--confdir', default = POOF_CONFIG_DIR, help = 'poof configuration directory', show_default = True)
@click.option('--poofconf', default = POOF_CONFIG_FILES['poof.conf'], help = 'poof configuration file', show_default = True)
@click.option('--rcloneconf', default = POOF_CONFIG_FILES['rclone-poof.conf'], help = 'rclone configuration file', show_default = True)
@click.option('--verbose/--no-verbose', default = False, help = 'verbose output', show_default = True)
@globalConf
def main(conf, confdir, poofconf, rcloneconf, verbose):
    # IMPORTANT - it must exist before declaring the functions, top-down,
    # because of the decorator.
    conf.confDir   = confdir
    conf.confFiles = { 'poof.conf': poofconf, 'rclone-poof.conf': rcloneconf, }
    conf.verbose   = verbose


def _initializeConfigIn(confFile, confDir):
    if not os.path.exists(confFile):
        os.makedirs(confDir, exist_ok = True)
        with open(confFile, 'w') as outputFile:
            bucketID = str(uuid.uuid4()).split('-')[-1]
            paths = {
                confDir: 'unittest',
            }
            basicConfig = {
                # bucket name must be unique:
                'bucket': 'poofbackup-%s-%s' % (os.environ['USER'], bucketID),
                'confFile': confFile,
                'paths': paths,
                'remote': 'poof-backup',
            }
            json.dump(basicConfig, outputFile, indent = 2, sort_keys = True)
        os.chmod(confFile, stat.S_IRUSR | stat.S_IWUSR)


def _initCloningScaffold():
    conf = configparser.ConfigParser()

    section  = 'poof-backup'
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
    click.secho(message, fg = 'bright_yellow', bg = 'red')
    if exitCode:
        sys.exit(exitCode)


# TODO:  use the Python API instead of calling external OS-levels commands here?
#        Neither rm -P nor srm are standard, and neither has much effect on
#        actual security since they don't work on SSDs anyway.
#
#        https://github.com/poof-backup/poof/issues/59
def _getNukeDirectoryArgsMac(path):
	args = (
		'/bin/rm',
		'-Prf',
		path,
	)
	return args


def _getNukeDirectoryArgsLinux(path):
	args = (
		'/bin/rm',
		'-Rf',
		path,
	)
	return args


def _getNukeDirectoryArgsWindows(path):
    raise NotImplementedError


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


def _config(confFiles = POOF_CONFIG_FILES, confDir = POOF_CONFIG_DIR, showConfig = True):
    confFile = confFiles['poof.conf']
    _initializeConfigIn(confFile, confDir)

    configStr = open(confFile, 'r').read()
    try:
        actualConfiguration = json.loads(configStr)
    except:
        die('invalid JSON? Failed to load %s' % confFile, 5)

    if showConfig:
        click.secho(configStr)

        try:
            pyperclip.copy(configStr)
        except PyperclipException:
            pass # Linux?

    return actualConfiguration


@main.command()
@globalConf
def config(conf):
    """
Ensure that the poof.conf file exists;  creates it if not present.
"""
    return _config(conf.confFiles, conf.confDir)


def _encryptionIsEnabled(poofConf, cloneConf):
    enabled = False

    for section in cloneConf.sections():
        if cloneConf[section]['type'] == 'crypt' and cloneConf[section]['password'] != 'BOGUS-PASSWORD' and poofConf['remote'] == section:
            enabled = True
            break

    return enabled


def _clone(toCloud, confDir = POOF_CONFIG_DIR, confFiles = POOF_CONFIG_FILES, nukeLocal = True, verbose = False):
    _, status = _verify(confFiles = confFiles)

    if status != PoofStatus.OK:
        die("cannot poof the files to the cloud", 4)

    conf      = _config(confFiles = confFiles, showConfig = False)
    poofDir   = None
    cloneConf = _cconfig(confFiles, confDir, showConfig = False)

    for localDir, cloudDir in conf['paths'].items():
        if localDir.endswith(os.sep):
            localDir = localDir[:-1]

        cloudPath = '%s:%s' % (conf['remote'], cloudDir) if _encryptionIsEnabled(conf, cloneConf) else '%s:%s/%s' % (conf['remote'], conf['bucket'], cloudDir)
        if toCloud:
            args = (arg for arg in ( RCLONE_PROG,
                    '--config',
                    confFiles['rclone-poof.conf'],
                    '-P' if verbose else '',
                    '-L',
                    'sync',
                    localDir,
                    cloudPath,
                  ) if arg)
            processingItem = localDir
        else:
            args = (arg for arg in ( RCLONE_PROG,
                    '--config',
                    confFiles['rclone-poof.conf'],
                    '-P' if verbose else '',
                    'sync',
                    cloudPath,
                    localDir,
                  ) if arg)
            processingItem = cloudPath

        click.secho('\nprocessing: %s' % processingItem, fg = 'green')

        if toCloud and not os.path.exists(processingItem):
            click.secho('%s not found or not mounted; skipped'% processingItem, fg = 'red', bg = 'bright_yellow')
            continue
        result = subprocess.run(args)

        try:
            result.check_returncode()
        except:
            click.secho('%s failed = %d - see output for details' % (RCLONE_PROG, result.returncode), fg = 'bright_red')
            continue

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
    click.echo(click.style('v = %s' % conf.verbose, fg='yellow'))
    outcome = _clone(True, confDir = conf.confDir, confFiles = conf.confFiles, nukeLocal = False, verbose = conf.verbose)
    h, m, s = _timeLapsed()
    click.echo(click.style(('BACKUP COMPLETED in %d:%02d:%02d' % (h, m, s)), fg='green'))

    return outcome


@main.command()
@globalConf
def download(conf):
    """
Download the files from the cloud storage into their corresponding directories.
"""
    click.echo(click.style('DOWNLOAD SYNC IN PROGRESS - PLEASE DO NOT INTERRUPT', fg='yellow'))
    outcome = _clone(False, confDir = conf.confDir, confFiles = conf.confFiles, verbose = conf.verbose)
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
                'pip3',
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
Neuter this poof installation by deleting its configuration and executables.
"""
    _neuter(conf.confDir)


@main.command()
@globalConf
def upload(conf):
    """
Upload to remote and wipe out the local data.
"""
    click.echo(click.style('UPLOAD SYNC IN PROGRESS - PLEASE DO NOT INTERRUPT', fg='yellow'))
    outcome = _clone(True, confDir = conf.confDir, confFiles = conf.confFiles, verbose = conf.verbose)
    h, m, s = _timeLapsed()
    click.echo(click.style(('UPLOAD COMPLETED in %d:%02d:%02d' % (h, m, s)), fg='green'))

    return outcome


def _cconfig(confFiles = POOF_CONFIG_FILES, confDir = POOF_CONFIG_DIR, showConfig = True):
    confFile = confFiles['rclone-poof.conf']
    _initializeCloningConfigIn(confFile, confDir)

    cloningConfStr = open(confFile, 'r').read()
    cloningConf = configparser.ConfigParser()

    cloningConf.read_string(cloningConfStr)
    if showConfig:
        click.secho(cloningConfStr)
        try:
            pyperclip.copy(cloningConfStr)
        except PyperclipException:
            pass # Linux?

    return cloningConf


@main.command()
def cconfig():
    """
Ensure that the rclone-poof.conf file exists; creates it if not present.
"""
    _cconfig()


def _econfig(confFiles = POOF_CONFIG_FILES, confDir = POOF_CONFIG_DIR, password1 = None, password2 = None):
    raise NotImplementedError


@main.command()
def econfig():
    """
    Generate the encrypted rclone configuration scaffold.
    """
    click.secho('econfig is not implemented', fg = 'bright_red')
    sys.exit(99)


def _verifyBogusValuesIn(component, conf, section, bogusSecrets):
    for key, bogusValue in bogusSecrets.items():
        try:
            if conf[section][key] == bogusValue:
                status = PoofStatus.WARN_MISCONFIGURED
                click.echo('configuration %s [%s].%s = %s - %s' % (component, section, key, bogusValue, status))
                return status
        except:
            status = PoofStatus.ERROR_MISSING_KEY
            click.echo('configuration %s [%s].%s = %s - %s' % (component, section, key, bogusValue, status))
            return status

    return PoofStatus.OK


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
        poofConf = _config(confFiles, POOF_CONFIG_DIR, showConfig = False)
        if len(poofConf['paths']) == 1:
            component = 'poof.conf'
            status    = PoofStatus.WARN_MISCONFIGURED
            click.echo('configuration %s? - %s: set the poof.config cloud backup path to something other than unittest' % (component, status))

            return component, status

        # heuristic:
        cloningConf = _cconfig(confFiles, POOF_CONFIG_DIR, showConfig = False)

        component = confFiles['rclone-poof.conf']
        for section in cloningConf.sections():
            if cloningConf[section]['type'] == 'crypt':
                status = _verifyBogusValuesIn(component, cloningConf, section, _CRYPT_BOGUS_SECRETS)
                if status is not PoofStatus.OK:
                    return component, status

            if cloningConf[section]['type'] == 's3':
                status = _verifyBogusValuesIn(component, cloningConf, section, _S3_BOGUS_SECRETS)
                if status is not PoofStatus.OK:
                    return component, status

        encryptionEnabled = PoofStatus.ENCRYPTION_ENABLED if _encryptionIsEnabled(poofConf, cloningConf) else PoofStatus.ENCRYPTION_DISABLED
        click.echo('encryption enabled? - %s' % encryptionEnabled)

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


def _cryptoggle(poofConf, rcloneConf, confFiles = POOF_CONFIG_FILES):
    cryptRemote = None
    plainRemote = None
    status = PoofStatus.ENCRYPTION_DISABLED
    poofRemoteOrg = poofConf['remote']

    for section in rcloneConf.sections():
        # poof version < 2.0 assumes only two sections:  remote and crypt remote.
        # The order in which these sections appear in the rclone config file is
        # irrelevant.
        if 'crypt' == rcloneConf[section]['type']:
            cryptRemote = section
        else:
            plainRemote = section

    if poofConf['remote'] == plainRemote and cryptRemote:
        poofConf['remote'] = cryptRemote
        status = PoofStatus.ENCRYPTION_ENABLED
        foreground = 'bright_green'
    elif poofConf['remote'] == cryptRemote and plainRemote:
        poofConf['remote'] = plainRemote
        status = PoofStatus.ENCRYPTION_DISABLED
        foreground = 'bright_yellow'
    elif poofRemoteOrg == poofConf['remote']:
        foreground =  'bright_red'
        click.secho('No encrypted remote is available!', fg = foreground)

    if poofRemoteOrg != poofConf['remote']:
        with open(confFiles['poof.conf'], 'w') as outputFile:
            json.dump(poofConf, outputFile, sort_keys = True, indent = 2,)

    click.secho('Toggle target from %s to %s - %s' % (poofRemoteOrg, poofConf['remote'], status), fg = foreground)

    return status


@main.command()
@globalConf
def cryptoggle(conf):
    """
    Toggle remote target encryption ON/OFF.
    """
    poofConf = _config(confFiles = conf.confFiles, showConfig = False)
    cloneConf = _cconfig(confFiles = conf.confFiles, showConfig = False)
    _cryptoggle(poofConf, cloneConf, conf.confFiles)

