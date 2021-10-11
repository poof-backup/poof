#!/usr/bin/env python3
# See: https://github.com/VirusTrack/COVIDvu/blob/master/LICENSE
# vim: set fileencoding=utf-8:


import pathlib
import sys

from setuptools import find_packages
from setuptools import setup

from poof import __VERSION__

# +++ constants +++

HERE = pathlib.Path(__file__).parent
README = (HERE / 'README.md').read_text()


# *** functions ***

def readToList(fileName):
    return [line.strip() for line in open(fileName).readlines()]


# *** main ***

if '__main__' == __name__:
    requirements = readToList('requirements.txt')

    setup(
        author                        = 'Eugene Ciurana pr3d4t0r',
        author_email                  = 'poof.project@cime.net',
        classifiers                   = [
            "License :: OST Approved :: BSD3 License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
        ],
        description                   = 'poof backup - instant, secure backup to a cloud drive',
        entry_points                  = {
                                    'console_scripts': {
                                        'poof=poof:main',
                                    }
                               },
        include_package_data          = True,
        install_requires              = requirements,
        license                       = "BSD3",
        long_description              = README,
        long_description_content_type = 'text/markdown',
        name                          = open('modulename.txt').read().replace('\n', ''),
        namespace_packages            = [ ],
        packages                      = find_packages(),
        url                           = 'https://github.com/poof-backup/poof',
        version                       = __VERSION__,
    )

sys.exit(0)
