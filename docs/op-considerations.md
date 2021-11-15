# Operational considerations

These operational considerations expand the details described in README.md
regarding the backups workflow and threat model.


## Background

Off-site backups to a reliable storage provider (physical or cloud), to reliable
media, are imperative for sensitive data.  Cloud storage providers offer
off-site safekeeping and varying levels of privacy, but their feature set is 
incomplete for power users who need an unattended, reliable, secure, and private
storage solution.

Google Drive, Dropbox, Box, OneDrivem, etc. all reserve the right to leverage 
user data while it's at rest.  None of them provides enough *peace of mind* that
the stored documents won't be open to inspection without the user's knowledge or
permission.

AWS Simple Storage Service (S3) offers one of the best storage options thanks to
its built-in redundancy, and it also provides tools for data encryption at the
source, making it a good backup system for low and high data volumes.  S3, 
however, requires the use of third-party tools of varying complexity for backing
up and restoring data.

Power users and businesses use the `[rclone](https://rclone.org/)` for managing 
high volumes of data.  `rclone` is a complex tool.  The **poof! backup** 
contributors used `rclone` in production systems with excellent results for a 
year, before deciding that a wrapper around its powerful feature set was
required to handle reliable, private, and secure backups of sensitive data.

**poof! backup** enables users to create and update data backups with a minimum
of fuss.  Backups can be automated or user-initiated, and the user has peace of
mind knowing that the process is reliable, that data at rest in the cloud
storage is secure and remains private, and that their local systems can be
protected by wiping out the local data repositories and poof program + 
configuration.  Resilience against forensic analysis is one of the main poof!
backup design goals.


## Operational model

poof! backup treats data as existing only forward in time.  Backups are
implemented through synchronization of the source and cloud storage paths.  No
incremental backup capabilities are available.  This is by design.  Think of
these backups as **data store snapshots**.

Users can run `poof backup` as often as they want.  Manual or timer operation
(via `cron` or `launchd`) are supported.

Users may run `poof upload` if they need to ensure that a backup exists and must
delete the data and the `poof` tool and configuration, in response of a threat
or in the course of normal system maintenance when the machine must be
surrendered to an untrusted third-party.

Backups are destructive at the target.  A file that was deleted in the source
storage will be deleted in the target.  This holds true whether the user backs
up or restores the data.  A new file object present in the local system will
be deleted if it doesn't exist in the remote system/cloud storage and the user
runs `poof download` to get the original data.


### Backups:  source, target

<img src='https://raw.githubusercontent.com/poof-backup/poof/master/assets/uc-bk-src-targt.png'>


### Downloads:  source, target

<img src='https://raw.githubusercontent.com/poof-backup/poof/master/assets/uc-dn-src-targt.png'>


---
#169; the poof backup contributors

