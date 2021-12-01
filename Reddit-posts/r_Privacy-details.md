Excellent points, I will address each in order. Most of the answers to your
questions/comments are in the project README.md, I'll summarize them each here.

Is the project only CLI? Yes, for the time being. Version 2.0 will also have a
GUI. At this stage, for operational considerations, no GUI might be the best
option. poof does generate configuration files for itself and for rclone on
demand, and adding the keys is the only manual operation. Key management is the
reason why we haven't put a GUI front-end.

Encryption scheme robustness - Encryption is implemented in rclone, poof
leverages its existing features. Rclone has had 80 releases since 2015, and it's
considered robust and secure, plus it has an active community built around it.
Full details regarding rclone crypt are available at: https://rclone.org/crypt/

Who owns the servers/cloud for backups? - AWS S3 for now, which is arguably the
cheapest, most robust and accessible cloud storage system available worldwide.
We plan on adding Dropbox, Box, etc. in version 2.0. Figuring out which to
prioritize is one of the reasons why we are reaching out to the Reddit
community. Dropbox is the strongest candidate in addition to S3 because of its
pervasiveness.

Local file deletion after upload - There are two modes of operation: poof backup
which syncs files/directories then leaves the local file system alone afterward,
and poof upload which syncs then deletes the poof-managed local
files/directories. Deletion doesn't happen by accident. It requires active user
participation. This is discussed in the threat model level 4 section of the
README.md. poof upload is used prior to surrendering the hardware to a
distrusted third-party like a repair shop, a customs border crossing, etc. The
upload command also wipes out the poof command itself (whether installed from a
package manager or pip) and all traces of its own configuration.

Newness - While poof is new to the scene as a public project, we've been using
it for backing up production Ubuntu Server and macOS file systems since
28.Oct.2020. Public exposure will only help now to test its robustness and to
extend its user base.

Admin rights - No, poof runs in user space. It can only manipulate files to
which the user has access. There is no need to install or run poof with root
privileges.

Secure deletion - We've worked on this for several months already, here's the
status. Deletion under macOS uses rm -P for multipass in the current release. We
have an experimental Linux branch that uses srm but it's a bit slow. We also
have a native wiping function in yet a different dev branch that we're trying to
optimize. For the time being poof is as secure whatever protection rm -P and srm
provide.

The main issue with secure deletion is media. SSDs are a problem because of the
reason you mention, and also because there are no standard/cross-platform
SSD-level wiping tools, and last because a well-funded/state-level actor may
have the capability to lift the deleted blocks off the SSD.

The current robust backup/deletion assumes that the user is knowledgeable enough
to use full disk encryption in their machines (FileVault, whatever on Linux),
which helps reduce the SSD attack surface after deletion.

Workflow - We put a lot of handrails around poof so that "bad things" don't
happen to users by mistake. The biggest gap is secrets management (cloud storage
access and the Rclone crypt keys), similar to what happens with GPG.

Encryption is an extra option that must be enabled, the default is to back files
and directories in plaintext. At that point, the only risk is the users losing
their userID/password to Amazon (and Dropbox or whatever in the future), and
those are easy to recover. Please see threat levels under Operational security
for details.

Thanks for your questions -- they are the kind of questions we are expecting to
get from the r/Privacy users! This conversation in a public forum will both help
demystify how poof works and guide its future direction.

Please let us know if this is satisfactory for posting in r/Privacy -- have a
great weekend - Cheers!

AND

Ah, I forgot re: secure delete and SSDs -- we had public tickets open on that
since 03.Oct, https://github.com/poof-backup/poof/issues/30 and
https://github.com/poof-backup/poof/issues/35 (others touch on that, but these
are the main ones), plus we've closed a few. It's not implemented in this
release because there's no good answer for file systems in SSDs, for the time
being. Cheers!

