# poof! Safe, secure, and forensics-resistant backup - request for comments

Hi!

poof! Backup is a tool for backing up local file system directories to cloud 
storage, in a secure manner, with forensics-resistant features:

- High data volume, high speed data sync to/from cloud storage
- Secure delete the local file system files upon successful process completion
- Encrypt the remote copies
- Eliminates all traces of itself in the local file system
- Leverages best-of-breed cloud storage (S3) in its first public release
- Puts the end user in control of the backups, client-side encryption, and cloud
  storage access
- Better operational model than Cryptomator for cross-platform compatibility and
  high volumes of data (e.g. media servers, data lakes)

We are reaching out to the r/DataHoarder community with this Request For
Comments as we make the project public, because you are a well-informed and
knowledgeable group.  Thanks to u/carrotcypher, u/trai_dep, and u/lugh for
reviewing this before we posted. Moving and syncing large amounts of data with
ease and peace of mind is one of this community's goals, and we feel confident
`poof` can help with that. We also hope to gain insights from you, and your
feedback will be invaluable for shaping future releases.

`poof backup` is a command-line utility at this point.  While it isn't hard to
use or understand, it requires some end-user technical proficiency:

- how to install software from the terminal command line (`poof` and `rclone`)
- basic knowledge of file system paths and what you store where
- use of a text editor to configure the paths that you want safekeep
- how to safely manage passwords and API keys

This release was designed to operate against the cheapest and arguably most
reliable and affordable cloud storage system, [AWS
S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html).
This means you'll need an Amazon Web Services account to use it.
We're trying to gauge which end user cloud storage ought to be next. You'll
help us figure that out with your comments...  Dropbox looks like the next
target.


poof! is a purpose-specific wrapper around the robust [Rclone](https://rclone.org)
tool, optimized for fast copy/sync, local files and directories wipe, one-time
setup, and simple ongoing execution, either user-initiated or via a scheduler
like `launchd` or `cron`.

In a nutshell, we wanted to make secure, forensics-resistant backups as easy and
efficient as possible.

The project was in development and continuous production use for 16 months
before this public release.  The brief user manual, threat model, and general
instalation guide are avaliable in the project [README](https://github.com/poof-backup/poof/blob/master/README.md)
on GitHub.  More detailed [operational considerations](https://github.com/poof-backup/poof/blob/master/ops-docs/index.md)
are also available in the same repository.

This first public release works on macOS and Linux, probably on any UNIX-like 
operating and file system where Python 3 and `rclone` are available.
[The code is available on GitHub](https://github.com/poof-backup/poof) under the
BSD-3 license.

[poof! can be installed from the Python Package Index](https://pypi.org/project/poof-backup/)
via `pip`.  Future releases will also be available for Homebrew, Ubuntu/Debian,
and other package managers.  We hope that version 2.0 will also support Windows
file systems.

Thanks, and we look forward to your comments!
