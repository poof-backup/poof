# poof backup

poof backup - 2-way secure data sync/backup/restore against a cloud drive.

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

This document contains diagrams and screen captures not visible in PyPI.  Please
refer to the original document at **https://github.com/poof-backup/poof#readme**
if you need to refer to them.


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

Verification fails because `poof` must have a minimum of two directories to
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

It shows these paths on Linux:

```
poof.conf = /home/joe-user/.config/poof/poof.conf
rclone-poof.conf = /home/joe-user/.config/poof/rclone-poof.conf
```

Enter the full path(s) to each directory you wish to back up, no `~` or `$HOME`.  In `poof.conf`:

```
{
  "bucket": "poofbackup",
  "confFile": "/Users/joe-user/Library/Application Support/poof/poof.conf",
  "paths": {
    "/Users/joe-user/Documents": "Documents",
    "/Users/joe-user/Downloads": "Downloads",
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


## Regular backups

`poof` validates its own configuration before backing up or restoring data.  It
will fail if its own configuration or any of its required tools configurations
are invalid.

Run `poof backup` as often as needed or required to copy all the directories in
the `poof` configuration to the cloud drive.

Run `poof upload` when there is need to sync the local file system directories,
then removing all the local files (selected directories wipe).

Run  `poof download` to sync the local file system with the most current files
in the cloud drive, as needed or required.


## Restore

**Restoring data from the cloud drive is a destructive operation in the target
file system.**  This is by design because `poof` clones and synchronizes the
source file system to the targets.  Backups are never incremental -- they are
considered to be "snapshots" in all cases.

To restore a backup from the cloud to the local file system:

1. Validate the configuration
1. Run `poof download`

The file system synchronization process may take from a few minutes to several
hours, depending on the number of files involved, the lengt of the files, and
the connection speed.


## Encrypted backups/uploads

`poof` leverages `rclone` encrypted remotes, if they are defined and available,
beginning with version **1.2.0**.  Future releases will implement *crypt*
configuration generators from within `poof`, for now this relies on `rclone`
until automation, key storage, and operational security issues are resolved.

Encryption details:

1. File content encryption uses [NaCl SecretBox](https://pkg.go.dev/golang.org/x/crypto/nacl/secretbox) 
1. File and directory names are separated by '/', padded to a multiple of 16
   bytes, then encrypted with EME and AES with a 256-bit key.

Implications:

- File and directory names with the same exact name will encrypt the same way
- File and directory names which start the same won't have a common prefix
- All names are encrypted to lower case alphanumeric strings
- Padding characters (e.g. =) are stripped
- Supports case-insensitve remotes (e.g. Windows)

The `rclone` Crypt documentation provides a thorough discussion of [how the
`crypt` remote implementation works](https://rclone.org/crypt).


### Pre-requisites

1. Working `poof` configuration
1. Working `rclone` configuration for poof with a working type *crypt* remote

Sample `poof.conf`:

```js
{
  "bucket": "poofbackup-joe-user-206ce7879351",
  "confFile": "/Users/joe-user/Library/Application Support/poof/poof.conf",
  "paths": {
    "/Users/joe-user/CryptoWallet": "CryptoWallet",
    "/Users/joe-user/Documents": "Documents",
    "/Users/joe-user/Downloads": "Downloads",
    "/Users/joe-user/Library/Application Support/poof": "poof-conf"
  },
  "remote": "poof-backup"
}
```

Sample valid `rclone-poof.conf`.  The `[poof-crypt[` section was generated using
`rclone` configuration for the password.  Notice that the remote definition uses
the target bucket in `poof.conf`:

```
[poof-backup]
type = s3
provider = AWS
env_auth = false
access_key_id = BOGUS-KEY-USE-YOURS
secret_access_key = BOGUS-SECRET-KEY-USE-YOURS
region = eu-west-1
location_constraint = eu-west-1
acl = private
storage_class = STANDARD_IA
chunk_size = 8M
upload_concurrency = 2
server_side_encryption = AES256

[poof-crypt]
type = crypt
remote = poof:poofbackup-joe-user-206ce7879351
password = BOGUS-PASSWORD
password2 = BOGUS-PASSWORD2

```


### Enabling and disabling encryption

Enabling and disabling encryption is accomplished by editing the `remote`
attribute in the `poof` configuration file, to point at the `poof-crypt` remote
instead of the `poof-backup` remote.

```json
{
  "bucket": "poofbackup-joe-user-206ce7879351",
  "confFile": "/Users/joe-user/Library/Application Support/poof/poof.conf",
  "paths": {
    "/Users/joe-user/CryptoWallet": "CryptoWallet",
    "/Users/joe-user/Documents": "Documents",
    "/Users/joe-user/Downloads": "Downloads",
    "/Users/joe-user/Library/Application Support/poof": "poof-conf"
  },
  "remote": "poof-crypt"
}
```

Running the upload or backup commands copies the files and directories to the
cloud storage using encrypted directory and file names, and encrypting the files
to prevent unauthorized viewing by the cloud storage provider:

```zsh
poof backup
```

Disabling encryption only requires to point the remote back to the cloud storage
remote definition, instead of the encrypted remote.


### Effects on backup/upload and download

File and directory names are preserved, as in the plaintext backup, in the local
file system.

File and directory names are encrypted in the cloud storage target.  File names
are transparent to `poof` and `rclone` - listing the encypted cloud file system
names with valid credentials shows them in plaintext on the client, but they are
obfuscated in the remote as described at the beginning of this section.

<img src='https://raw.githubusercontent.com/poof-backup/poof/master/assets/sample-S3-dir-list.png'>


## Operational security

_Section under development._


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
&#169; the poof-backup contributors

