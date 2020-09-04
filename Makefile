# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


SHELL=/bin/bash

BUILD=./build
DEVPI_PASSWORD=nopasswordsetyet
DEVPI_USER=pr3d4t0r
DIST=./dist
DOCKER_IMAGE=pr3d4t0r/$(shell cat dockerimagename.txt)
DOCKER_VERSION=$(shell cat dockerimageversion.txt)
MODULE=$(shell cat modulename.txt)
REQUIREMENTS=requirements.txt
VERSION=$(shell cat version.txt)
SITE_DATA=./site-data

include ./build.mk


# Targets:

all: ALWAYS
	make test
	make module
	make publish


bootstrap: ALWAYS
	pipenv install --dev pipenv-setup
	pipenv install --dev pudb
	pipenv install --dev pytest


clean:
	rm -Rf $(BUILD)/*
	rm -Rf $(DIST)/*
	rm -Rfv $$(find basdtracks | awk '/__pycache__$$/')
	rm -Rfv $$(find test | awk '/__pycache__$$/')
	rm -Rfv $$(find . | awk '/.ipynb_checkpoints/')
	pip uninstall -y $(MODULE)==$(VERSION) || true
    

install:
	pushd resources/ && pip install -e .. && popd
	pip list | awk 'NR < 3 { print; } /basdtracks/'


module:
	pipenv install
	python setup.py bdist_wheel


nuke: ALWAYS
	make clean
	rm -Rf $(shell find basdtracks | awk '/__pycache__$$/')
	rm -Rf $(shell find test/ | awk '/__pycache__$$/')


refresh: ALWAYS
	pip install -U -r requirements.txt


resetpy: ALWAYS
	rm -Rfv ./.Python ./bin ./build ./dist ./include ./lib


test: ALWAYS
	[[ -d $(SITE_DATA) ]] || mkdir -p $(SITE_DATA)
	pip install -r requirements.txt
	pip install -e .
	pytest -v ./test/basdtracks/test_module.py
	pip uninstall -y $(MODULE)==$(VERSION) || true
	rm -Rfv $$(find basdtracks | awk '/__pycache__$$/')
	rm -Rfv $$(find test | awk '/__pycache__$$/')


update:
	pipenv update


ALWAYS:

