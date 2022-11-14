test:
	docker-compose -f tests/integration_tests.yml up -d
	python -m unittest tests/test_loadbalancer.py
	nohup ./main.py &
	molotov -w 9 -p 50 -d 30 tests/load_tests.py
	docker-compose -f tests/integration_tests.yml down
	pkill -INT -f "python3 ./main.py"

#ps -ef | grep python

