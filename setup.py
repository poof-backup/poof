#!/usr/bin/env python3
# See: https://github.com/VirusTrack/COVIDvu/blob/master/LICENSE
# vim: set fileencoding=utf-8:


import sys

from setuptools import find_packages
from setuptools import setup


# *** functions ***

def readToList(fileName):
    return [line.strip() for line in open(fileName).readlines()]


# *** main ***

if '__main__' == __name__:
    requirements = readToList('requirements.txt')

    setup(
        author               = 'Eugene Ciurana pr3d4t0r',
        author_email         = 'poof.project@cime.net',
#         dependency_links     = [
#                                     'https://github.com/pr3d4t0r/repo/tarball/master#egg=vtrustler',
#                                ],
        description          = 'poof - instant, safe backup to a cloud drive',
        entry_points         = {
                                    'console_scripts': {
                                        'poof=poof:main',
                                    }
                               },
        include_package_data = True,
        install_requires     = requirements,
        license              = open('LICENSE.txt').read(),
        long_description     = open('README.md').read(),
        name                 = open('modulename.txt').read().replace('\n', ''),
        namespace_packages   = [ ],
        packages             = find_packages(),
        url                  = 'https://github.com/poof-backup/poof',
        version              = open('version.txt').read().strip(),
    )

sys.exit(0)

