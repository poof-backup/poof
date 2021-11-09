% POOF(1) Version 1.2.4 | Secure cloud storage backup documentation


NAME
====

**poof** - 2-way secure data sync/backup/restore against cloud storage.


SYNOPSIS
========

| **poof** _command_
| **poof** \[**--confdir** TEXT] _command_
| **poof** \[**--poofconf** TEXT] _command_
| **poof** \[**--rcloneconf** TEXT] _command_
| **poof** \[**--help**]


DESCRIPTION
===========

Backup of local file system directories to cloud storage or other storage, in a
secure manner, and preserving the original files' attributes for later recovery.
The poof! tool offers additional security options:

- Secure delete the local file system files upon successful process completion
- Encrypt the remote copies
- Eliminates all traces of itself in the local file system

poof! leverages tried-and-true tools to perform its tasks:

- [`rclone`](https://rclone.org/) - A command line program for managing files in
  cloud storage.

_Experimental versions of `poof` leverage other operating system and third-party
tools, discussed in this documentation.  For details, see the [`poof` GitHub 
repository](https://github.com/poof-backup/poof)._


Options
-------
--help

: Prints brief usage information

--confdir

: Specifies the configuration files directory

--poofconf

: Specifies the poof configuration file name

--rcloneconf

: Specifies the rclone configuration file name

Canonical file name merges _confdir_/_poofconf_ or _confdir_/_rcloneconf_.


FILES
=====

*poof.conf*

: Cloud storage remote specification, paths to backup/upload, bucket and file 
  system information.

*rclone-poof.conf*

: rclone cloud storage specification for plain and encrypted backups
  configuration and secrets.

These files location is system-dependent.

On macOS:  $HOME/Library/Application Support/poof

On Linux:  $HOME/.config/poof


BUGS
====

See GitHub issues:  https://github.com/poof-backup/poof/issues


AUTHOR
======

Eugene Ciurana and the poof! Development team <poof.project AT cime.net>


SEE ALSO
========

**rclone(1)**

