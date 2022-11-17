# Whirlwind

Whirlwind is a brutally simple HTTP loadbalancer, created using only the Tornado library's Web
framework features.

![](whirlwind.gif)

## Motivation/Influence

I was looking into deploying Web Services built using the Tornado framework and couldn't find
a loadbalancer '_dumb_' enough for my liking. I just wanted to cycle through many different
iterations of the same service one-by-one, with minimal configuration and other options. Then it came to me... 
I could also use Tornado for this purpose! 

A lot of the _underlying_ design of this project is influenced by the course
'_Creating an HTTP Load Balancer in Python_' by Neeran Gul. 
You can find the course on: http://testdriven.io.

## Features

Host and Path based-routing defined in a simple .yml file

```yaml
# example configuration, two different hosts and two different
# paths each routing to a pool of two servers

hosts:
  - host: www.peter.com
    servers:
      - localhost:8081
      - localhost:8082
  - host: www.simpson.com
    servers:
      - localhost:9081
      - localhost:9082
paths:
  - path: /pete
    servers:
      - localhost:8081
      - localhost:8082
  - path: /simpo
    servers:
      - localhost:9081
      - localhost:9082

```

Run the make file to spin up a suite of back end servers, 
to see the integration and load tests. 
```bash
$ make 
docker-compose -f tests/integration_tests.yml up -d
Creating network "tests_default" with the default driver
Creating tests_a1_1 ... done
Creating tests_b2_1 ... done
Creating tests_a2_1 ... done
Creating tests_b1_1 ... done
python -m unittest tests/test_loadbalancer.py
----------------------------------------------------------------------
Ran 6 tests in 0.126s
OK
nohup ./main.py &
molotov -w 9 -p 50 -d 30 tests/load_tests.py
Molotov v2.6 ~ Happy Breaking 🥛🔨 ~ Ctrl+C to abort
**** Molotov v2.6. Happy breaking! ****OCESSES: 1  ELAPSED: 41.02 seconds                                                                                                   
SUCCESSES: 2658 | FAILURES: 0
*** Bye ***
docker-compose -f tests/integration_tests.yml down
Stopping tests_b1_1 ... done
Stopping tests_a1_1 ... done
Stopping tests_a2_1 ... done
Stopping tests_b2_1 ... done
Removing tests_b1_1 ... done
Removing tests_a1_1 ... done
Removing tests_a2_1 ... done
Removing tests_b2_1 ... done
Removing network tests_default
pkill -INT -f "python3 ./main.py"
```
## Note

Whilst I'm pleasantly surprised at the results, (there seems to be a decent tolerance for concurrency),
this is a curio and shouldn't be used in production!