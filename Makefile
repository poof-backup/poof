# See: https://github.com/pr3d4t0r/poof/blob/master/LICENSE.txt
# vim: set fileencoding=utf-8:


SHELL=/bin/zsh

BUILD=./build
DEVPI_PASSWORD=nopasswordsetyet
DEVPI_USER=pr3d4t0r
DIST=./dist
MODULE=$(shell awk -F "[\"]" '/name/ { printf("%s\n", $$2); }' pyproject.toml)
REQUIREMENTS=requirements.txt
SITE_DATA=./site-data
VERSION=$(shell awk -F "[\"]" '/version/ { printf("%s\n", $$2); }' pyproject.toml)


# Targets:

all: ALWAYS
	make test
	make module


clean:
	poetry check
	rm -Rf $(DIST)/* || true
	rm -Rfv $$(find $(MODULE) | awk '/__pycache__/')
	rm -Rfv $$(find tests | awk '/__pycache__/')
	poetry remove -n $(MODULE)==$(VERSION) || true
    

module:
	poetry check
	poetry build -n -f wheel


test: ALWAYS
	poetry check
	pytest -v ./tests/test_poof.py
	poetry remove -n $(MODULE)==$(VERSION) || true
	rm -Rfv $$(find $(MODULE) | awk '/__pycache__/')
	rm -Rfv $$(find tests | awk '/__pycache__/')


ALWAYS:

