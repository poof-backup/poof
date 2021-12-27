# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


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

LAUNCH_AGENT_OS = "Darwin"
LAUNCH_AGENT_PATH = os.path.join(os.environ['HOME'], 'Library/LaunchAgents') if platform.system() == LAUNCH_AGENT_OS else None
LAUNCH_AGENT_USER_ID = os.geteuid()
LAUNCH_AGENT_USER_NAME = getpass.getuser()
LAUNCH_AGENT_POOF = 'org.pypi.poof'
LAUNCH_AGENT_FILE = '.'.join((LAUNCH_AGENT_POOF, 'plist'))
LAUNCH_AGENT_FULL_PATH = os.path.join(LAUNCH_AGENT_PATH, LAUNCH_AGENT_FILE)
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
	<string>/tmp/poof/poof-%%LAUNCH_AGENT_USER_NAME%%-err.dat</string>
	<key>StandardOutPath</key>
	<string>/tmp/poof/poof-%%LAUNCH_AGENT_USER_NAME%%-out.dat</string>
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


# +++ implementation ***

def isSupported(targetOS = LAUNCH_AGENT_OS):
    return targetOS == LAUNCH_AGENT_OS


def _is_launchdReady(targetOS = LAUNCH_AGENT_OS, launchAgent = LAUNCH_AGENT_POOF):
    if isSupported(targetOS):
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
  

def isEnabled(targetOS = LAUNCH_AGENT_OS, launchAgentFile = LAUNCH_AGENT_FULL_PATH, launchAgent = LAUNCH_AGENT_POOF):
    if isSupported(targetOS):
        if os.path.exists(launchAgentFile):
            return _is_launchdReady(targetOS, launchAgent)
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


def enable(targetOS = LAUNCH_AGENT_OS,
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

    if not isEnabled(targetOS, agentFile, launchAgent) and targetOS == LAUNCH_AGENT_OS:
        _resolveTemplate(launchAgent, launchAgentProg, launchAgentUserName, agentFile)

        try:
            process = subprocess.run(args, capture_output = True)

            if process.returncode != 0:
                raise subprocess.CalledProcessError

        except subprocess.CalledProcessError:
            click.secho('Enabling poof in launchctl failed - operation aborted', fg = 'bright_red')
            sys.exit(21)

    return True


def disable(targetOS = LAUNCH_AGENT_OS,
            agentFile = LAUNCH_AGENT_FULL_PATH,
            launchAgent = LAUNCH_AGENT_POOF,
            launchAgentProg = LAUNCH_AGENT_PROG,
            launchAgentUserName = LAUNCH_AGENT_USER_NAME):
    args = (
        LAUNCHCTL_PROG,
        'bootout',
        LAUNCHCTL_PROG_DOMAIN_TARGET,
        agentFile,
    )

    if isEnabled(targetOS, agentFile, launchAgent) and targetOS == LAUNCH_AGENT_OS:
        try:
            process = subprocess.run(args, capture_output = False)

            if process.returncode != 0:
                raise subprocess.CalledProcessError

        except subprocess.CalledProcessError:
            click.secho('Enabling poof in launchctl failed - operation aborted', fg = 'bright_yellow', bg = 'bright_red')
            click.secho('To disable:  launchctl bootout %s %s' % (LAUNCHCTL_PROG_DOMAIN_TARGET, agentFile), fg = 'bright_yellow', bg = 'bright_red')
            sys.exit(22)
        finally:
            try:
                shutil.rmtree('/tmp/poof')
            except:
                pass
            try:
                os.unlink(agentFile)
            except:
                pass

    click.secho('%s purged' % agentFile, fg = 'bright_yellow')

    return True


def launchdConfig(targetOS = LAUNCH_AGENT_OS,
            agentFile = LAUNCH_AGENT_FULL_PATH,
            launchAgent = LAUNCH_AGENT_POOF,
            launchAgentProg = LAUNCH_AGENT_PROG,
            launchAgentUserName = LAUNCH_AGENT_USER_NAME):
    
    if not isEnabled(targetOS, agentFile, launchAgent):
        enable(targetOS, agentFile, launchAgent, launchAgentProg, launchAgentUserName)

    plist = open(agentFile, 'r').read()

    click.secho(plist)
    try:
        pyperclip.copy(plist)
    except PyperclipException:
        pass # Linux?

    return plist

