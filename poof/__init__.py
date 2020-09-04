# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


from appdirs import AppDirs

import argparse
import shutil
import os
import sys


# *** constants ***

RCLONE_PROG      = 'rclone'
RCLONE_PROG_TEST = 'ls'
VALID_COMMANDS   = ( 'upload', 'download', 'verify', 'test' )

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


def verifyEnvironment(program = RCLONE_PROG, configFiles = POOF_CONFIG_FILES):
    if not shutil.which(program):
        return False

    print('%s - OK' % program)

    status = 'OK'
    for key, value in configFiles.items():
        if not os.path.exists(value):
            status = 'MISSING'

        print('%s - %s' % (key, status))

        if status != 'OK':
            return False

    return True
    

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

