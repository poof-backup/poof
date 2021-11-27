# poof! Safe, secure, and forensics-resistant backup - request for comments

Hi!

poof! Backup is a tool for backing up local file system directories to cloud 
storage, in a secure manner, with forensics-resistant features:

- Secure delete the local file system files upon successful process completion
- Encrypt the remote copies
- Eliminates all traces of itself in the local file system
- Leverages best-of-breed cloud storage (S3) in its first public release
- Puts the end user in control of the backups, client-side encryption, and cloud
  storage access
- Better operational model than Cryptomator for cross-platform compatibility and
  high volumes of data (e.g. media servers, data lakes)

We are reaching out to the r/Privacy community with this Request For Comments as
we make the project public, because you are a well-informed and knowledgeable
group.  We hope to gain insights from you, and your feedback will be invaluable
for shaping future releases.

poof! is a purpose-specific wrapper around the robust [Rclone](https://rclone.org)
tool, optimized for fast copy/sync, local files and directories wipe, one-time
setup, and simple ongoing execution, either user-initiated or via a scheduler
like `launchd` or `cron`.

In a nutshell, we wanted to make secure, forensics-resistant backups as easy and
efficient as possible.

The project was in development and continuous production use for 16 months
before this public release.  The brief user manual, threat model, and general
instalation guide is avaliable in the project [README](https://github.com/poof-backup/poof/blob/master/README.md)
on GitHub.

This first public release works on macOS and Linux, probably on any UNIX-like 
operating and file system where Python 3 and `rclone` are available.
[The code is available on GitHub](https://github.com/poof-backup/poof) under the
BSD-3 license.

[poof! can be installed from the Python Package Index](https://pypi.org/project/poof-backup/)
via `pip`.  Future releases will also be available for Homebrew, Ubuntu/Debian,
and other package managers.  We hope that version 2.0 will also include Windows.

Thanks, and we look forward to your comments!
