# poof

Poof!  2-way data sync/backup/restore against a cloud drive.

## Requirements

1. Python 3.8 or later
1. 'rclone`
1. A UNIX-like operating system and file system

_Note:_ `poof` may work well under Windows file systems but it hasn't been
tested at the time this README was posted.


### Installing `rclone`

Install `rclone` in your system via https://rclone.org/install/

`rclone` makes an identical copy of directories and their contents to the
desired cloud drive, including the correct time stamps and permissions.  It's 
a more reliable mechanism than building that logic in `poof`.


---
&#169; the poof! contributors

