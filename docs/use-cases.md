# Use cases

These use cases expand the details described in README.md regarding the backups
workflow and threat model.


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
configuration.  Hardening against forensic analysis is one of the main poof!
backup design goals.



---
#169; the poof backup contributors

