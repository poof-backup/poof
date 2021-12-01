# Secrets and build 

The build uses [devpi](https://devpi.net/) as the builds target for all
development, and [PyPI](https://pypi.org) as the publication target for stable
versions.


## Secrets

The Makefile uses three different files (defined in `.gitignore`) for storing 
secrets:


### devpi-hostname.txt

Use your local devpi server, or you're welcome to use https://pypi.cime.dev


### devpi-password.txt

Your devpi user password.


### devpi-user.txt

Your devpi user name.


## Your devpi index and credentials

You must have valid credentials, a user, and an index (or more) before running
the Makefile for the first time.  Follow these steps to setup your working
index.  This example assumes that you're using `https://pypi.cime.dev` as your
devpi host, replace that name with your own if necessary.

First, install the devpi client in your current virtual environent:

```bash
pip install -U devpi-client
```

Specify the devpi host (https://pypi.cime.dev):

```bash
devpi use $(cat ./devpi-hostname.txt) 
```

Create your user name and root index:

```
devpi user -c $(cat devpi-user.txt) password="$(cat devpi-password.txt)" email="whatever@domain.tld"
```

Log on to the devpi server and create your index.  Best practice is to call that
index `dev` and the Makefile assumes this convetion:

```
devpi login $(cat devpi-user.txt)
devpi index -c dev bases=root/pypi
```

That's it!  Your index and secrets are defined and you're ready to build.
Create the `devpi-hostname.txt`, `devpi-password.txt`, and `devpi-user.txt`
files as described in the previous section, and run your first build.

You may view the **poof backup** development packages repository at:

https://pypi.cime.dev/ciurana/dev


---
&#169; the poof backup contributors

