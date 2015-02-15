all: tests

tests: build
	python setup.py test

build: clean
	python setup.py build

install: tests
	python setup.py install

clean:
	-@rm -rf dist build *.egg-info
	-@find . \( -name '*.pyc' -o -name '*.pyd' \) -exec rm {} \;
