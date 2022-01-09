# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


"""
Reference for later (too cheap to buy Lingon): https://zerolaunched.herokuapp.com/
Background: https://foliovision.com/2014/01/os-x-scheduling-tools
launchd syntax and usage https://babodee.wordpress.com/2016/04/09/launchctl-2-0-syntax/
"""


from pyperclip import PyperclipException

import getpass
import os
import platform
import shutil
import subprocess
import sys

import click
import pyperclip


# --- constants ---

LAUNCH_AGENT_REQUIRED_OS = "Darwin"
LAUNCH_AGENT_PATH = os.path.join(os.environ['HOME'], 'Library/LaunchAgents') if platform.system() == LAUNCH_AGENT_REQUIRED_OS else None
LAUNCH_AGENT_USER_ID = os.geteuid()
LAUNCH_AGENT_USER_NAME = getpass.getuser()
LAUNCH_AGENT_POOF = 'org.pypi.poof'
LAUNCH_AGENT_FILE = '.'.join((LAUNCH_AGENT_POOF, 'plist')) if platform.system() == LAUNCH_AGENT_REQUIRED_OS else None
LAUNCH_AGENT_FULL_PATH = os.path.join(LAUNCH_AGENT_PATH, LAUNCH_AGENT_FILE) if platform.system() == LAUNCH_AGENT_REQUIRED_OS else None
LAUNCH_AGENT_PROG = '/usr/local/bin/poof'

LAUNCHCTL_PROG = '/bin/launchctl'
LAUNCHCTL_PROG_DOMAIN_TARGET = '/'.join(('gui', str(LAUNCH_AGENT_USER_ID, )))

LAUNCH_AGENT_PLIST_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>%%LAUNCH_AGENT_POOF%%</string>
	<key>ProgramArguments</key>
	<array>
		<string>sh</string>
		<string>-c</string>
		<string>%%LAUNCH_AGENT_PROG%% backup</string>
	</array>
	<key>RootDirectory</key>
	<string>%%HOME%%</string>
	<key>StandardErrorPath</key>
	<string>/tmp/6CC9-4821-827B-8596B684ECA9/com.apple.ContentStoreAgent-%%LAUNCH_AGENT_USER_NAME%%-err.dat</string>
	<key>StandardOutPath</key>
	<string>/tmp/6CC9-4821-827B-8596B684ECA9/com.apple.ContentStoreAgent-%%LAUNCH_AGENT_USER_NAME%%-out.dat</string>
	<key>StartCalendarInterval</key>
	<array>
		<dict>
			<key>Hour</key>
			<integer>0</integer>
			<key>Minute</key>
			<integer>0</integer>
		</dict>
		<dict>
			<key>Hour</key>
			<integer>6</integer>
			<key>Minute</key>
			<integer>0</integer>
		</dict>
		<dict>
			<key>Hour</key>
			<integer>12</integer>
			<key>Minute</key>
			<integer>0</integer>
		</dict>
		<dict>
			<key>Hour</key>
			<integer>18</integer>
			<key>Minute</key>
			<integer>0</integer>
		</dict>
	</array>
	<key>UserName</key>
	<string>%%LAUNCH_AGENT_USER_NAME%%</string>
	<key>WorkingDirectory</key>
	<string>%%HOME%%</string>
</dict>
</plist>
"""

TEST_LAUNCH_AGENTS_PATH = './tests/LaunchAgents'
TEST_LAUNCH_AGENT_FULL_PATH = os.path.join(TEST_LAUNCH_AGENTS_PATH, LAUNCH_AGENT_FILE) if platform.system() == LAUNCH_AGENT_REQUIRED_OS else None
TEST_LAUNCH_AGENT_POOF = 'test.unit.poof'
TEST_LAUNCH_AGENT_PROG = LAUNCH_AGENT_PROG.replace('poof', 'poofbogus')


# +++ implementation ***

def isSupported(hostOS):
    """
    Usage:  hostOS = platform.system()
    """
    return hostOS == LAUNCH_AGENT_REQUIRED_OS


def _is_launchdReady(hostOS = LAUNCH_AGENT_REQUIRED_OS, launchAgent = LAUNCH_AGENT_POOF):
    if isSupported(hostOS):
        try:
            serviceTarget = '/'.join((LAUNCHCTL_PROG_DOMAIN_TARGET, launchAgent, ))
            args = (
                LAUNCHCTL_PROG,
                'print',
                serviceTarget,
            )
            process = subprocess.run(args, capture_output = True)

            return process.returncode == 0
        except subprocess.CalledProcessError:
            return False

        return True
    else:
        return False
  

def isEnabled(hostOS = LAUNCH_AGENT_REQUIRED_OS, launchAgentFile = LAUNCH_AGENT_FULL_PATH, launchAgent = LAUNCH_AGENT_POOF):
    if isSupported(hostOS):
        if os.path.exists(launchAgentFile):
            return _is_launchdReady(hostOS, launchAgent)
        else:
            return False
    else:
        return False


def _resolveTemplate(
        launchAgent = LAUNCH_AGENT_POOF,
        launchAgentProg = LAUNCH_AGENT_PROG, 
        launchAgentUserName = LAUNCH_AGENT_USER_NAME,
        launchAgentFile = LAUNCH_AGENT_FULL_PATH):

    output = LAUNCH_AGENT_PLIST_TEMPLATE.replace('%%LAUNCH_AGENT_POOF%%', launchAgent)
    output = output.replace('%%LAUNCH_AGENT_PROG%%', launchAgentProg)
    output = output.replace('%%LAUNCH_AGENT_USER_NAME%%', launchAgentUserName)
    output = output.replace('%%HOME%%', os.environ['HOME'])

    with open(launchAgentFile, 'w') as outputFile:
        outputFile.write(output)

    return output


def enable(hostOS = LAUNCH_AGENT_REQUIRED_OS,
            agentFile = LAUNCH_AGENT_FULL_PATH,
            launchAgent = LAUNCH_AGENT_POOF,
            launchAgentProg = LAUNCH_AGENT_PROG,
            launchAgentUserName = LAUNCH_AGENT_USER_NAME):

    args = (
        LAUNCHCTL_PROG,
        'bootstrap',
        LAUNCHCTL_PROG_DOMAIN_TARGET,
        agentFile,
    )

    if not isEnabled(hostOS, agentFile, launchAgent) and hostOS == LAUNCH_AGENT_REQUIRED_OS:
        _resolveTemplate(launchAgent, launchAgentProg, launchAgentUserName, agentFile)

        try:
            process = subprocess.run(args, capture_output = True)

            if process.returncode != 0:
                raise subprocess.CalledProcessError

            try:
                os.mkdir('/tmp/6CC9-4821-827B-8596B684ECA9')
            except:
                # Silent failure - no need to warn, let launchd deal with this
                pass

        except subprocess.CalledProcessError:
            click.secho('Enabling poof in launchctl failed - operation aborted', fg = 'bright_red')
            sys.exit(21)

    return True


def disable(hostOS = LAUNCH_AGENT_REQUIRED_OS,
            agentFile = LAUNCH_AGENT_FULL_PATH,
            launchAgent = LAUNCH_AGENT_POOF,
            launchAgentProg = LAUNCH_AGENT_PROG,
            launchAgentUserName = LAUNCH_AGENT_USER_NAME,
            unitTest = False):
    if not isSupported(platform.system()):
        click.secho('lpurge is only available on macOS', fg = 'bright_yellow')
        sys.exit(94)

    args = (
        LAUNCHCTL_PROG,
        'bootout',
        LAUNCHCTL_PROG_DOMAIN_TARGET,
        agentFile,
    )

    if isEnabled(hostOS, agentFile, launchAgent) and hostOS == LAUNCH_AGENT_REQUIRED_OS:
        try:
            process = subprocess.run(args, capture_output = False)

            if process.returncode != 0:
                raise subprocess.CalledProcessError

        except subprocess.CalledProcessError:
            click.secho('Disabling poof in launchctl failed - operation aborted', fg = 'bright_yellow', bg = 'bright_red')
            click.secho('To disable:  launchctl bootout %s %s' % (LAUNCHCTL_PROG_DOMAIN_TARGET, agentFile), fg = 'bright_yellow', bg = 'bright_red')
            sys.exit(22)
        finally:
            try:
                if not unitTest:
                    shutil.rmtree('/tmp/6CC9-4821-827B-8596B684ECA9')
            except:
                pass
            try:
                os.unlink(agentFile)
            except:
                pass

    click.secho('%s purged' % agentFile, fg = 'bright_yellow')

    return True


def launchdConfig(hostOS = LAUNCH_AGENT_REQUIRED_OS,
            agentFile = LAUNCH_AGENT_FULL_PATH,
            launchAgent = LAUNCH_AGENT_POOF,
            launchAgentProg = LAUNCH_AGENT_PROG,
            launchAgentUserName = LAUNCH_AGENT_USER_NAME):
    
    if isSupported(platform.system()):
        if not isEnabled(hostOS, agentFile, launchAgent):
            enable(hostOS, agentFile, launchAgent, launchAgentProg, launchAgentUserName)

        plist = open(agentFile, 'r').read()

        click.secho(plist)
        try:
            pyperclip.copy(plist)
        except PyperclipException:
            pass # Linux?

        return plist
    else:
        click.secho('lconfig is only available on macOS', fg = 'bright_yellow')
        sys.exit(95)

