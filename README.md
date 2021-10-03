# poof

poof 2-way secure data sync/backup/restore against a cloud drive.

Backup of local file system directories to a cloud drive or other storage, in a
secure manner, and preserving the original files' attributes for later recovery.
The poof! tool offers additional security options:

- Secure delete the local file system files upon successful process completion
- Encrypt the remote copies

poof! leverages tried-and-true tools to perform its tasks:

- [`rclone`](https://rclone.org/) - A command line program for managing files in
  cloud storage.

_Experimental versions of `poof` leverage other operating system and third-party
tools, discussed in the documentation.  For details, see the [`poof` GitHub 
repository](https://github.com/poof-backup/poof)._


## One-time set up

1. Install `poof`
1. Install `rclone`
1. Configure `poof`
1. Configure `rclone`


### Install `poof`

Use `pip` or `pip3` to install in the current Python scope (system or virtual
environment):

```
pip3 install poof
```

### Configuration

The `poof` configuration for `rclone` is specific to this tool.  `rclone` users
may have other configurations that in no way conflict with `poof` and vice
versa.

For the first time `poof` configuration, run:

```zsh
poof verify
```

`poof` validates that all component and configuration requirements are satisfied:

```
installed rclone? - PoofStatus.OK
exists poof.conf? - PoofStatus.MISSING_CONFIG_FILE
```

Generate a new, basic `poof` configuration file and validate its contents:

```
poof config  && poof verify
```

Results in:


```
installed rclone? - PoofStatus.OK
exists poof.conf? - PoofStatus.OK
exists rclone-poof.conf? - PoofStatus.MISSING_CONFIG_FILE
```

The `rclone` configuration file for `poof` is still missing.  Generate a simple
cloud drive `rclone` configuration file:


```
poof cconfig && poof verify

```

The verification fails because `poof` must have at least one directory to backup
in addition to the backup of its own configuration, which defaults to `unittest`
until overridden by the user.

Verification failes because `poof` must have a minimum of two directories to
backup or upload to the cloud drive:

- A `poof` configuration backup directory
- One end-user backup directory

In most cases, `Documents` ought to be the first end-user directory. 

List the configuration paths to make the necessary updates:

```
poof paths
```

Shows these paths on a Mac:

```
poof.conf = /Users/joe-user/Library/Application Support/poof/poof.conf
rclone-poof.conf = /Users/joe-user/Library/Application Support/poof/rclone-poof.conf
```

Edit the corresponding entries to confirm a valid configuration.  Enter the 
full path to each directory, no ~ or `$HOME`.  In `poof.conf`:

```
{
  "bucket": "poofbackup",
  "confFile": "/Users/joe-user/Library/Application Support/poof/poof.conf",
  "paths": {
    "/Users/joe-user/Documents": "Documents"
    "/Users/joe-user/Library/Application Support/poof": "poof-config"
  },
  "remote": "my-poof"
}
```

Last, configure the appropriate credentials in `rclone.conf` for the cloud drive
intended for backup.  This example uses an Amazon S3 configuration, replace the
bogus credentials with your own.

Verify the configuation one last time:

```
poof verify
```

Will show that `poof` is ready for normal operations:

```
installed rclone? - PoofStatus.OK
exists poof.conf? - PoofStatus.OK
exists rclone-poof.conf? - PoofStatus.OK
configuration appears to be valid and has valid credentials
```


### Regular backups

`poof` validates its own configuration before backing up or restoring data.  It
will fail if its own configuration or any of its required tools configurations
are invalid.

Run `poof backup` as often as needed or required to copy all the directories in
the `poof` configuration to the cloud drive.

Run `poof upload` when there is need to sync the local file system directories,
then removing all the local file (selected directories wipe).

Run  `poof download` to sync the local file system with the most current files
in the cloud drive, as needed or required.



## Requirements

1. Python 3.8 or later
1. `rclone`
1. A UNIX-like operating system and file system

_Note:_ `poof` may work well under Windows file systems but it hasn't been
tested at the time this README was posted.


### Installing `rclone`

Install `rclone` in your system via https://rclone.org/install/

`rclone` makes an identical copy of directories and their contents to the
desired cloud drive, including the correct time stamps and permissions.  It's 
a more reliable mechanism than building that logic in `poof`.


---
&#169; the poof contributors

