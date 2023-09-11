# QDRANT_DB_HOST = localhost
# QDRANT_DB_PORT = 60962
VERSION=v0.0.1
AUTHOR=coolfool
APPLICATION=alioth

run-alioth:
	gunicorn app.main:app -c gunicorn.conf.py

spawn-ingestion-celery-worker:
	celery -A app.tasks.ingestion worker -l info -O fair  -c 5 --without-mingle --without-gossip -P gevent -Q ingest

spawn-restore-celery-worker:
	celery -A app.tasks.restore worker  -l info -O fair -c 5 --without-mingle --without-gossip -P gevent -Q restore

spawn-backup-celery-worker:
	celery -A app.tasks.backup worker  -l info -O fair -c 5 --without-mingle --without-gossip -P gevent -Q backup

spawn-celery-beat-worker:
	celery -A app.tasks.celery_app beat

setup-buildx:
	docker buildx create --use --name alioth_buildx_instance

build: 
	AUTHOR=$(AUTHOR) APPLICATION=$(APPLICATION) docker buildx build -t $(AUTHOR)/$(APPLICATION):$(VERSION)  . --output type=docker

build-ci: 
	AUTHOR=$(AUTHOR) APPLICATION=$(APPLICATION) docker buildx build -t $(AUTHOR)/$(APPLICATION):$(VERSION)  --platform=linux/amd64,linux/arm64/v8 . --output type=docker

deps:
	pyenv install 3.11 -s
	pyenv local 3.11
	poetry config virtualenvs.create true --local
	poetry install
	poetry shell

dev-services:
	docker compose up rabbitmq minio qdrant

setup-dev-environment: deps dev-environment
# Yet to be implemented
# test:
# 	pytest

# Yet to be implemented
# run-tests-local: setup-test-environment test

setup-load-test:
	QDRANT_DB_HOST=$(QDRANT_DB_HOST) QDRANT_DB_PORT=$(QDRANT_DB_PORT) \
	python3 benchmark/setup_testbench.py

load-test-upstream: setup-load-test
	locust -f benchmark/ingestion_upstream_api.py 

load-test-alioth: setup-load-test
	locust -f benchmark/ingestion.py

welcome_k8s:
	./welcome_k8s.sh

k3d-cluster:
	k3d cluster create alioth --api-port 6550 -p "1337:80@loadbalancer"

k3d-cluster-delete:
	k3d cluster delete alioth 

k3d-restart-deployments:
	kubectl config set-context k3d-alioth
	./restart_k8s_deployments.sh

deploy-alioth-with-local-image:
	AUTHOR=$(AUTHOR) APPLICATION=$(APPLICATION) k3d image import -c 'alioth' $(AUTHOR)/$(APPLICATION):$(VERSION) 
	cd deploy/ && helm upgrade --install alioth . --debug -f env/values.local.yaml

deploy-alioth-with-upstream-image:
	AUTHOR=$(AUTHOR) APPLICATION=$(APPLICATION) docker pull ghcr.io/$(AUTHOR)/$(APPLICATION):$(VERSION) 
	AUTHOR=$(AUTHOR) APPLICATION=$(APPLICATION) k3d image import -c 'alioth' ghcr.io/$(AUTHOR)/$(APPLICATION):$(VERSION) 
	AUTHOR=$(AUTHOR) APPLICATION=$(APPLICATION) cd deploy/ && helm upgrade --install alioth . --debug -f env/values.local.yaml --set alioth.image.repository="ghcr.io/$(AUTHOR)/$(APPLICATION) --set alioth.image.tag="$(VERSION)"

delete-alioth-deployment:
	helm uninstall alioth 

clean: delete-alioth-deployment k3d-cluster-delete
