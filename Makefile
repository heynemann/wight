test:
	@nosetests -vv --pdb --pdb-failures --with-yanc -s --with-coverage --cover-erase --cover-inclusive --cover-package=wight tests/

ci-test:
	@nosetests -vv --with-yanc -s --with-coverage --cover-erase --cover-inclusive --cover-package=wight tests/

setup:
	@pip install -e .[tests] -i http://f.pypi.python.org/simple
