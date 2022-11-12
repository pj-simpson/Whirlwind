test:
	docker-compose -f tests/integration_tests.yml up -d
	python -m unittest tests/test_loadbalancer.py
	docker-compose -f tests/integration_tests.yml down
