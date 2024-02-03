# See: https://github.com/poof-backup/poof/blob/master/LICENSE.txt


SHELL=/bin/bash

BUILD=./build
DEVPI_HOST=$(shell cat devpi-hostname.txt)
DEVPI_PASSWORD=$(shell cat ./devpi-password.txt)
DEVPI_USER=$(shell cat ./devpi-user.txt)
DIST=./dist
MANPAGES=./manpages
PACKAGE=$(shell cat package.txt)
REQUIREMENTS=requirements.txt
VERSION=$(shell echo "from poof import __VERSION__; print(__VERSION__)" | python)


# Targets:

all: ALWAYS
	make test
	make manpage
	make package


# TODO: Use rm -Rfv $$(find $(PACKAGE) | awk '/__pycache__$$/') after the poof
#       package is claimed to this project by PyPI.
clean:
	rm -Rf $(BUILD)/*
	rm -Rf $(DIST)/*
	rm -Rf $(MANPAGES)/*
	rm -Rfv $$(find poof/ | awk '/__pycache__$$/')
	rm -Rfv $$(find tests | awk '/__pycache__$$/')
	rm -Rfv $$(find . | awk '/.ipynb_checkpoints/')
	pushd ./dist ; pip uninstall -y $(PACKAGE)==$(VERSION) || true ; popd


devpi:
	devpi use $(DEVPI_HOST)
	@devpi login $(DEVPI_USER) --password="$(DEVPI_PASSWORD)"
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
	mkdir -p $(MANPAGES)
	t=$$(mktemp) && awk -v "v=$(VERSION)" '/^%/ { $$4 = v; print; next; } { print; }' README.md > "$$t" && cat "$$t" > README.md && rm -f "$$t"
	pandoc --standalone --to man README.md -o $(MANPAGES)/poof.1


nuke: ALWAYS
	make clean


package:
	pip install -r $(REQUIREMENTS)
	python setup.py bdist_wheel


# The publish: target is for PyPI, not for the devpi server.
publish:
	twine --no-color check $(DIST)/*
	twine --no-color upload --verbose $(DIST)/*


refresh: ALWAYS
	pip install -U -r requirements.txt


# Delete the Python virtual environment - necessary when updating the
# host's actual Python, e.g. upgrade from 3.7.5 to 3.7.6.
resetpy: ALWAYS
	rm -Rfv ./.Python ./bin ./build ./dist ./include ./lib


targets:
	@printf "Makefile targets:\n\n"
	@cat Makefile| awk '/:/ && !/^#/ && !/targets/ && !/Makefile/ { gsub("ALWAYS", ""); gsub(":", ""); print; } /^ALWAYS/ { next; }'


# TODO: Use rm -Rfv $$(find $(PACKAGE) | awk '/__pycache__$$/') after the poof
#       package is claimed to this project by PyPI.
test: ALWAYS
	@echo "Version = $(VERSION)"
	pip install -r requirements.txt
	pip install -e .
	pytest -v ./tests/poof-test.py
	pytest -v ./tests/launchd-test.py
	pip uninstall -y $(PACKAGE)==$(VERSION) || true
	rm -Rfv $$(find poof/ | awk '/__pycache__$$/')
	rm -Rfv $$(find tests | awk '/__pycache__$$/')


tools:
	pip install -U devpi-client pip ptpython pudb pytest


upload:
	devpi upload dist/*whl


ALWAYS:

