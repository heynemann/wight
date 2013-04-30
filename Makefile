test: redis
	@nosetests -vv --pdb --pdb-failures --with-yanc -s --with-coverage --cover-erase --cover-inclusive --cover-package=wight tests/

ci-test: redis
	@nosetests -vv --with-yanc -s --with-coverage --cover-erase --cover-inclusive --cover-package=wight tests/

tox:
	@PATH=$$PATH:~/.pythonbrew/pythons/Python-2.6.*/bin/:~/.pythonbrew/pythons/Python-2.7.*/bin/:~/.pythonbrew/pythons/Python-3.0.*/bin/:~/.pythonbrew/pythons/Python-3.1.*/bin/:~/.pythonbrew/pythons/Python-3.2.3/bin/:~/.pythonbrew/pythons/Python-3.3.0/bin/ tox

setup:
	@pip install -e .[tests] -i http://f.pypi.python.org/simple

kill_redis:
	-redis-cli -p 7780 shutdown

redis: kill_redis
	redis-server ./redis.conf; sleep 1
	redis-cli -p 7780 info
