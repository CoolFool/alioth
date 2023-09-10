# QDRANT_DB_HOST = localhost
# QDRANT_DB_PORT = 60962
VERSION=v0.0.1

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
	docker buildx build -t coolfool/alioth:$(VERSION)  . --output type=docker

build-ci: 
	docker buildx build -t coolfool/alioth:$(VERSION)  --platform=linux/amd64,linux/arm64/v8 . --output type=docker

setup-dev-environment:
	docker compose up rabbitmq minio qdrant

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

deploy-alioth-local-with-local-image:
	k3d image import -c 'alioth' coolfool/alioth:$(VERSION) 
	cd deploy/ && helm upgrade --install alioth . --debug -f env/values.local.yaml

deploy-alioth-local-with-upstream-image:
	docker pull ghcr.io/coolfool/alioth:$(VERSION) 
	k3d image import -c 'alioth' ghcr.io/coolfool/alioth:$(VERSION) 
	cd deploy/ && helm upgrade --install alioth . --debug -f env/values.local.yaml --set alioth.image.repository="ghcr.io/coolfool/alioth"

delete-alioth-deployment:
	helm uninstall alioth 

clean: delete-alioth-deployment k3d-cluster-delete
