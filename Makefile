# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


SHELL=/bin/bash

BUILD=./build
DEVPI_HOST=$(shell cat devpi-hostname.txt)
DEVPI_PASSWORD=$(shell cat ./devpi-password.txt)
DEVPI_USER=$(shell cat ./devpi-user.txt)
DIST=./dist
MODULE=$(shell cat modulename.txt)
# Preparation for devpi?
# REQUIREMENTS=$(shell cat requirements.txt)
REQUIREMENTS=requirements.txt
VERSION=$(shell cat version.txt)


# Targets:

all: ALWAYS
	make test
	make module
	make upload


clean:
	rm -Rf $(BUILD)/*
	rm -Rf $(DIST)/*
	rm -Rfv $$(find $(MODULE) | awk '/__pycache__$$/')
	rm -Rfv $$(find test | awk '/__pycache__$$/')
	rm -Rfv $$(find . | awk '/.ipynb_checkpoints/')
	rm -fv $$(find . | awk '/bogus/')
	rm -fv /usr/local/bin/poof
	pushd ./dist ; pip uninstall -y $(MODULE)==$(VERSION) || true ; popd
    

devpi:
	devpi use $(DEVPI_HOST)
	devpi login $(DEVPI_USER) --password="$(DEVPI_PASSWORD)"
	devpi use $(DEVPI_USER)/dev
	devpi -v use --set-cfg $(DEVPI_USER)/dev
	@[[ -e "pip.conf-bak" ]] && rm -f "pip.conf-bak"


install:
	pip install -U $(MODULE)==$(VERSION)
	pip list | awk 'NR < 3 { print; } /$(MODULE)/'


libupdate:
	pip install -U pip
	pip install -Ur $(REQUIREMENTS)


module:
	pip install -r $(REQUIREMENTS)
	python setup.py bdist_wheel


nuke: ALWAYS
	make clean
	rm -Rf $(shell find $(MODULE) | awk '/__pycache__$$/')
	rm -Rf $(shell find test/ | awk '/__pycache__$$/')


# The publish: target is for PyPI, not for the devpi server.
publish:
	@echo "publishing NOOP"


refresh: ALWAYS
	pip install -U -r requirements.txt


# Delete the Python virtual environment - necessary when updating the
# host's actual Python, e.g. upgrade from 3.7.5 to 3.7.6.
resetpy: ALWAYS
	rm -Rfv ./.Python ./bin ./build ./dist ./include ./lib


test: ALWAYS
	pip install -r requirements.txt
	pip install -e .
	pytest -v ./tests/test-poof.py
	pip uninstall -y $(MODULE)==$(VERSION) || true
	rm -Rfv $$(find $(MODULE) | awk '/__pycache__$$/')
	rm -Rfv $$(find test | awk '/__pycache__$$/')


upload:
	devpi upload dist/*whl


ALWAYS:

