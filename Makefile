PROJECT = $(shell basename $$(pwd))
ID = pikesley/${PROJECT}
PIHOST = led.local

default: all

# Laptop targets

build: laptop-only
	docker build \
		--tag ${ID} .

docker-compose:
	docker-compose up

run: laptop-only
	docker-compose exec light-emitting-desk bash

# Docker targets

all: docker-only format lint test clean

black: docker-only
	python -m black .

isort: docker-only
	python -m isort .

format: docker-only black isort

lint: docker-only
	python -m pylama

test: python-tests jasmine-ci nightwatch-tests

jasmine-ci: docker-only
	@MOZ_HEADLESS=true jasmine ci -b firefox | grep -v "Mozilla/5.0" | grep -v Warning

nightwatch-tests: docker-only
	@nightwatch

python-tests: docker-only flush-redis
	python -m pytest \
		--random-order \
		--verbose \
		--capture no \
		--failed-first \
		--exitfirst \
		--cov

jasmine: docker-only
	jasmine server --host 0.0.0.0

flush-redis: docker-only redis
	redis-cli flushall

clean:
	@find . -depth -name __pycache__ -exec rm -fr {} \;
	@find . -depth -name .pytest_cache -exec rm -fr {} \;
	@find . -depth -name ".coverage.*" -exec rm {} \;
	@find . -depth -name reports -exec rm -fr {} \;
	@find . -depth -name geckodriver.log -exec rm {} \;

sass: docker-only
	sass --watch sass:static/css/

dev-install: docker-only
	python -m pip install -r requirements-dev.txt
	npm install

redis:
	service redis-server start

nginx:
	ln -sf $$(pwd)/etc/nginx/sites-available/dev-default /etc/nginx/sites-enabled/default
	service nginx restart

push-code: docker-only clean
	rsync --archive \
		  --verbose \
		  --exclude node_modules \
		  --exclude assets \
		  /opt/${PROJECT} \
		  pi@${PIHOST}:

# Pi targets

setup: pi-only apt-installs install system-install virtualhost

install: pi-only
	sudo python -m pip install --break-system-packages -r requirements.txt

set-python: pi-only
	sudo update-alternatives --install /usr/local/bin/python python /usr/bin/python2 1
	sudo update-alternatives --install /usr/local/bin/python python /usr/bin/python3 2

apt-installs: pi-only
	sudo apt-get update
	sudo apt-get install -y python3-pip nginx redis

virtualhost: pi-only
	sudo ln -sf $$(pwd)/etc/nginx/sites-available/default /etc/nginx/sites-enabled/
	sudo service nginx restart

prepare-logs: pi-only
	sudo mkdir -p /var/log/webserver/
	sudo chown pi /var/log/webserver/

	sudo mkdir -p /var/log/worker/
	sudo chown pi /var/log/worker/

system-install: systemd restart-services

systemd: pi-only prepare-logs
	sudo systemctl enable -f /home/pi/${PROJECT}/etc/systemd/webserver.service
	sudo systemctl enable -f /home/pi/${PROJECT}/etc/systemd/worker.service

restart-services:
	sudo service webserver restart
	sudo service worker restart

stop-services:
	sudo service webserver stop
	sudo service worker stop

# Guardrails

docker-only:
	@if ! [ "$(shell uname -a | grep 'x86_64 GNU/Linux')" ] ;\
	then \
		echo "This target can only be run inside the container" ;\
		exit 1 ;\
	fi

laptop-only:
	@if ! [ "$(shell uname -a | grep 'Darwin')" ] ;\
	then \
		echo "This target can only be run on the laptop" ;\
		exit 1 ;\
	fi

pi-only:
	@if ! [ "$(shell uname -a | grep 'armv.* GNU/Linux')" ] ;\
	then \
		echo "This target can only be run on the Pi" ;\
		exit 1 ;\
	fi
