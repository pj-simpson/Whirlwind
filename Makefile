test:
	docker-compose up -d
	python -m unittest tests/test_loadbalancer.py
	docker-compose down
