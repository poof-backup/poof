# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


SHELL=/bin/bash

BUILD=./build
DEVPI_HOST=$(shell cat devpi-hostname.txt)
DEVPI_PASSWORD=$(shell cat ./devpi-password.txt)
DEVPI_USER=$(shell cat ./devpi-user.txt)
DIST=./dist
DOCS=./docs
PACKAGE=$(shell cat package.txt)
REQUIREMENTS=requirements.txt
VERSION=$(shell echo "from poof import __VERSION__; print(__VERSION__)" | python)


# Targets:

all: ALWAYS
	make test
	make package
	make manpage


# TODO: Use rm -Rfv $$(find $(PACKAGE) | awk '/__pycache__$$/') after the poof
#       package is claimed to this project by PyPI.
clean:
	rm -Rf $(BUILD)/*
	rm -Rf $(DIST)/*
	rm -Rf $(DOCS)/*
	rm -Rfv $$(find poof/ | awk '/__pycache__$$/')
	rm -Rfv $$(find tests | awk '/__pycache__$$/')
	rm -Rfv $$(find . | awk '/.ipynb_checkpoints/')
	pushd ./dist ; pip uninstall -y $(PACKAGE)==$(VERSION) || true ; popd


devpi:
	devpi use $(DEVPI_HOST)
	devpi login $(DEVPI_USER) --password="$(DEVPI_PASSWORD)"
	devpi use $(DEVPI_USER)/dev
	devpi -v use --set-cfg $(DEVPI_USER)/dev
	@[[ -e "pip.conf-bak" ]] && rm -f "pip.conf-bak"


install:
	pip install -U $(PACKAGE)==$(VERSION)
	pip list | awk 'NR < 3 { print; } /$(PACKAGE)/'


libupdate:
	pip install -U pip
	pip install -Ur $(REQUIREMENTS)


local:
	pip install -e .


manpage:
	mkdir -p $(DOCS)
	t=$$(mktemp) && awk -v "v=$(VERSION)" '/^%/ { $$4 = v; print; next; } { print; }' README.md > "$$t" && cat "$$t" > README.md && rm -f "$$t"
	pandoc --standalone --to man README.md -o $(DOCS)/poof.1


# This target will be removed in a future Makefile release.  The correct semantics are to use the package target.
module:
	make package


nuke: ALWAYS
	make clean


package:
	pip install -r $(REQUIREMENTS)
	python setup.py bdist_wheel


# The publish: target is for PyPI, not for the devpi server.
# https://www.python.org/dev/peps/pep-0541/#how-to-request-a-name-transfer
#
# PyPI user name:  ciurana; pypi AT cime_net
publish:
	twine --no-color check $(DIST)/*
	twine --no-color upload --verbose $(DIST)/*


refresh: ALWAYS
	pip install -U -r requirements.txt


# Delete the Python virtual environment - necessary when updating the
# host's actual Python, e.g. upgrade from 3.7.5 to 3.7.6.
resetpy: ALWAYS
	rm -Rfv ./.Python ./bin ./build ./dist ./include ./lib


# TODO: Use rm -Rfv $$(find $(PACKAGE) | awk '/__pycache__$$/') after the poof
#       package is claimed to this project by PyPI.
test: ALWAYS
	@echo "Version = $(VERSION)"
	pip install -r requirements.txt
	pip install -e .
	pytest -v ./tests/test-poof.py
	pip uninstall -y $(PACKAGE)==$(VERSION) || true
	rm -Rfv $$(find poof/ | awk '/__pycache__$$/')
	rm -Rfv $$(find tests | awk '/__pycache__$$/')


upload:
	devpi upload dist/*whl


ALWAYS:

