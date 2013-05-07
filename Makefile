test ci-test: mongo_test redis
	@sleep 3
	@rm -rf ~/.wighttest
	@WIGHT_USERDATA_PATH=~/.wighttest nosetests -vv --with-yanc -s --with-coverage --cover-erase --cover-inclusive --cover-package=wight tests/unit/

acceptance acc integration func functional: mongo_test redis kill_app
	@sleep 3
	@rm -rf ~/.wightacc
	@python wight/api/server.py --port 2368 --bind 0.0.0.0 --conf ./tests/acceptance/acceptance.conf &
	@WIGHT_USERDATA_PATH=~/.wightacc nosetests -vv --with-yanc -s tests/acceptance/

tox:
	@PATH=$$PATH:~/.pythonbrew/pythons/Python-2.6.*/bin/:~/.pythonbrew/pythons/Python-2.7.*/bin/:~/.pythonbrew/pythons/Python-3.0.*/bin/:~/.pythonbrew/pythons/Python-3.1.*/bin/:~/.pythonbrew/pythons/Python-3.2.3/bin/:~/.pythonbrew/pythons/Python-3.3.0/bin/ tox

tox26:
	@PATH=$$PATH:~/.pythonbrew/pythons/Python-2.6.*/bin/:~/.pythonbrew/pythons/Python-2.7.*/bin/:~/.pythonbrew/pythons/Python-3.0.*/bin/:~/.pythonbrew/pythons/Python-3.1.*/bin/:~/.pythonbrew/pythons/Python-3.2.3/bin/:~/.pythonbrew/pythons/Python-3.3.0/bin/ tox -e py26

tox27:
	@PATH=$$PATH:~/.pythonbrew/pythons/Python-2.6.*/bin/:~/.pythonbrew/pythons/Python-2.7.*/bin/:~/.pythonbrew/pythons/Python-3.0.*/bin/:~/.pythonbrew/pythons/Python-3.1.*/bin/:~/.pythonbrew/pythons/Python-3.2.3/bin/:~/.pythonbrew/pythons/Python-3.3.0/bin/ tox -e py27

tox32:
	@PATH=$$PATH:~/.pythonbrew/pythons/Python-2.6.*/bin/:~/.pythonbrew/pythons/Python-2.7.*/bin/:~/.pythonbrew/pythons/Python-3.0.*/bin/:~/.pythonbrew/pythons/Python-3.1.*/bin/:~/.pythonbrew/pythons/Python-3.2.3/bin/:~/.pythonbrew/pythons/Python-3.3.0/bin/ tox -e py32

tox33:
	@PATH=$$PATH:~/.pythonbrew/pythons/Python-2.6.*/bin/:~/.pythonbrew/pythons/Python-2.7.*/bin/:~/.pythonbrew/pythons/Python-3.0.*/bin/:~/.pythonbrew/pythons/Python-3.1.*/bin/:~/.pythonbrew/pythons/Python-3.2.3/bin/:~/.pythonbrew/pythons/Python-3.3.0/bin/ tox -e py33

toxpypy:
	@PATH=$$PATH:~/.pythonbrew/pythons/Python-2.6.*/bin/:~/.pythonbrew/pythons/Python-2.7.*/bin/:~/.pythonbrew/pythons/Python-3.0.*/bin/:~/.pythonbrew/pythons/Python-3.1.*/bin/:~/.pythonbrew/pythons/Python-3.2.3/bin/:~/.pythonbrew/pythons/Python-3.3.0/bin/ tox -e pypy

setup:
	@pip install -e .[tests]

kill_redis:
	-redis-cli -p 7780 shutdown

redis: kill_redis
	redis-server ./redis.conf; sleep 1
	redis-cli -p 7780 info > /dev/null

kill_mongo:
	@ps aux | awk '(/mongod/ && $$0 !~ /awk/){ system("kill -9 "$$2) }'

mongo: kill_mongo
	@rm -rf /tmp/wight/mongodata && mkdir -p /tmp/wight/mongodata
	@mongod --dbpath /tmp/wight/mongodata --logpath /tmp/wight/mongolog --port 7777 --quiet &

kill_mongo_test:
	@ps aux | awk '(/mongod.+test/ && $$0 !~ /awk/){ system("kill -9 "$$2) }'

mongo_test: kill_mongo_test
	@rm -rf /tmp/wight/mongotestdata && mkdir -p /tmp/wight/mongotestdata
	@mongod --dbpath /tmp/wight/mongotestdata --logpath /tmp/wight/mongotestlog --port 7778 --quiet &

run: mongo redis
	@python wight/api/server.py --port 2367 --bind 0.0.0.0 --conf ./wight/api/local.conf -vvv --debug

kill_app:
	@-ps aux | egrep server.py | egrep -v egrep | awk ' { print $$2 } ' | xargs kill -9
