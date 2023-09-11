<div align="center" id = "top">
    <h2>Alioth</h2>
    <h3>Ingest data at scale into a Qdrant DB Cluster</h3>
</div>

## Contents
- [Introduction](#introduction)
- [Architecture](#architecture)
  - [Overview](#overview)
  - [Ingestion Pipeline](#ingestion-pipeline)
  - [Backup & Restore Mechanism](#backup--restore-mechanism)
- [Prerequisites](#prerequisites)
  - [For Development](#for-development)
  - [For Deployment](#for-deployment)
- [Development](#development)
- [Deploy](#deploy)
  - [Kubernetes](#kubernetes)
  - [Docker-Compose (Not Recommended) ](#docker-compose-not-recommended)
- [Load Test](#load-test)
   - [Setup and Configuration](#setup-and-configuration)
- [Observability](#observability)
  - [Dashboards](#dashboards)
  - [Alerts](#alerts)
- [Makefile Usage](#makefile-usage)
- [API Usage](#api-usage)
- [Further Improvements & Ideas](#further-improvements--ideas)
- [Authors](#authors)
- [License](#license)

## Introduction
1. Alioth is a Python application that uses Celery with RabbitMQ as broker and backend to ingest data at a very high rate into a distributed Qdrant Vector DB Cluster hosted primarily on Kubernetes.
2. It is designed with a goal to make it as easy as possible to be scaled horizonatally.
3. It supports automatic snapshotting and backup for collections as well as storage(disks) to any S3 Compliant Object Storage such as AWS S3, Minio etc.
4. There is an easy to use recovery mechanism that can restore a collection on a Qdrant host from the snapshots that are stored in S3 Compliant Object storage.
5. Observability and performance monitoring is configured using Grafana, Prometheus, Alert-manager and various exporters (ref: [Observability](#observability))

## Architecture

- ### Overview
  1. Alioth doesn't reimplement all the API endpoints available in Qdrant, it only implements endpoints that require resources and can be scaled horizontally.
     > To make it easier to use the Upstream Qdrant API use this Postman collection that implements the commonly used APIs. Do remember to change set the appropriate values in the environment[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/19694638-331c2888-b878-40e5-8bfa-0db7cc5887da?action=collection%2Ffork&source=rip_markdown&collection-url=entityId%3D19694638-331c2888-b878-40e5-8bfa-0db7cc5887da%26entityType%3Dcollection%26workspaceId%3Ddb115311-bd17-4c17-8706-8b8073f9afbb#?env%5BDevelopment%5D=W3sia2V5IjoicHJvdG9jb2wiLCJ2YWx1ZSI6Imh0dHAiLCJlbmFibGVkIjp0cnVlLCJ0eXBlIjoiZGVmYXVsdCIsInNlc3Npb25WYWx1ZSI6Imh0dHAiLCJzZXNzaW9uSW5kZXgiOjB9LHsia2V5IjoicWRyYW50X2hvc3QiLCJ2YWx1ZSI6ImxvY2FsaG9zdCIsImVuYWJsZWQiOnRydWUsInR5cGUiOiJkZWZhdWx0Iiwic2Vzc2lvblZhbHVlIjoibG9jYWxob3N0Iiwic2Vzc2lvbkluZGV4IjoxfSx7ImtleSI6InFkcmFudF9wb3J0IiwidmFsdWUiOiI2MzMzIiwiZW5hYmxlZCI6dHJ1ZSwidHlwZSI6ImRlZmF1bHQiLCJzZXNzaW9uVmFsdWUiOiI2MzMzIiwic2Vzc2lvbkluZGV4IjoyfSx7ImtleSI6InFkcmFudF9ncnBjX3BvcnQiLCJ2YWx1ZSI6IjYzMzQiLCJlbmFibGVkIjp0cnVlLCJ0eXBlIjoiZGVmYXVsdCIsInNlc3Npb25WYWx1ZSI6IjYzMzQiLCJzZXNzaW9uSW5kZXgiOjN9LHsia2V5IjoiYWxpb3RoX2hvc3QiLCJ2YWx1ZSI6ImxvY2FsaG9zdCIsImVuYWJsZWQiOnRydWUsInR5cGUiOiJkZWZhdWx0Iiwic2Vzc2lvblZhbHVlIjoibG9jYWxob3N0Iiwic2Vzc2lvbkluZGV4Ijo0fSx7ImtleSI6ImFsaW90aF9wb3J0IiwidmFsdWUiOiIxMzM3IiwiZW5hYmxlZCI6dHJ1ZSwidHlwZSI6ImRlZmF1bHQiLCJzZXNzaW9uVmFsdWUiOiIxMzM3Iiwic2Vzc2lvbkluZGV4Ijo1fSx7ImtleSI6ImNvbGxlY3Rpb25fbmFtZSIsInZhbHVlIjoibW92aWVfY29sbGVjdGlvbiIsImVuYWJsZWQiOnRydWUsInR5cGUiOiJkZWZhdWx0Iiwic2Vzc2lvblZhbHVlIjoibW92aWVfY29sbGVjdGlvbiIsInNlc3Npb25JbmRleCI6Nn1d)
  2. It is designed with scalability in mind and thus the API server and the Celery workers are stateless.
  3. The API server is the primary gateway for resource heavy workloads and is written with [FastAPI](https://fastapi.tiangolo.com/) and served using [Gunicorn](https://gunicorn.org/).
  4. The FastAPI endpoints accept requests and reponses both of which use predefined [pydantic](https://docs.pydantic.dev/latest/) models for the type of requests and responses. All the endpoints that implememnt Qdrant APIs, simply invokes a celery tasks based on the workload the endpoint implements.
  5. Celery is an open source asynchronous task queue or job queue which is based on distributed message passing. It basically has a bunch of workers that consumes and processes messages from a  queue (RabbitMQ queue in case of Alioth) and based on the settings stores the result.
  6. The tasks in Celery is any function that is run by the workers, these workers can be scaled horizonatally as well as vertically. As everything is async in celery, it needs a broker to coordinate everything. Celery supports multiple brokers but Alitoh uses RabbitMQ due to it's ease of use AND and it is cost-efficient to run at scale. Redis was considered but as it primarily uses memory to store data it would've been expensive to run at scale and data ingestion doesn't need real-time speed of processing.
  7. Kafka was also considered but Celery doesn't officially support it and most importantly running self-hosted Kafka on Kubernetes or bare-metal, it is a huge operational effort and using cloud would've been expensive.
  8. The API Docs are available at `/docs` from the Alioth Endpoint.

- ### Ingestion Pipeline
  1. The user has to create a collection manually by using Qdrant API or Client libraries. The reason to NOT include a collection endpoint in Alioth is simply because it would just act as proxy and increase latency for no performance gain. Collections are highly configurable and has lots of params that the user has to be aware of and abstracting it away is not the way to go. 
     > Do remember to disable indexing for the collection from the API if you are going to ingest large amounts of data.
  2. The ingestion endpoint (`/alioth/ingest`) accepts Post Request, and invokes `app.tasks.ingestion.ingest` celery task.
  3. Once a message or payload is `POST`ed to the API, the payload is first add to `ingest` queue and then the invoked tasks is spawned by the ingestion celery worker that consumes the `ingest` queue and takes care of processing the payload and upserting it in Qdrant DB.
  4. Alioth uses the `.upsert` function of the Qdrant Client and uses batches to upsert data into Qdrant DB as it can handle single as well as multiple records.  
  5. The ingestion celery worker can be horizonatally scaled based on the rate of ingestion of records. 

- ### Backup & Restore mechanism
  
  - #### Backup
  - #### Restore

## Prerequisites

-  ### For development
   1. Install pyenv for Python version management. (ref: https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)
   2. Install poetry for Python dependency management. (ref: https://python-poetry.org/docs/#installation)
   3. Install and configure docker w/ docker-compose (ref: https://docs.docker.com/engine/install/)
   4. Make sure `make` is properly installed and verify using  `make --help`
  
-  ### For deployment
    1. Install K3d for a Kubernetes Cluster (ref: https://k3d.io/v5.6.0/#install-current-latest-release)
    2. Install Helm for deploying to Kubernetes (ref: https://helm.sh/docs/intro/install/#through-package-managers)
 
## Development

## Deploy

- ### Kubernetes
    Kubernetes is the recommended way to deploy alioth as it abstracts away and takes care of many issues involved in building a high-scalable system that can ingest data at a very fast rate. 

    Although **Alioth** can be deployed on any Kubernetes cluster for demo purposes we are going to use K3d locally.

    1. #### Create Kubernetes cluster using K3d
       ```bash 
          make k3d-cluster
       ```
    2. #### Deploy using Helm
       ```bash
         make deploy-alioth-with-upstream-image
        ```
      
- ### Docker-compose (Not recommended)
   A barebones version of **Alioth** without any observability or multiple application replicas can be deployed using docker-compose although it's not recommended.
   - Deploy using docker-compose
      ```bash
          docker compose up
       ```

## Load Test

  1. Load testing is setup and configured using [locust](https://locust.io/)
  2. For load testing a collection (`movie_collection`) with a vector size of `100` and `6` shards is created using the official Qdrant client
  3. A payload (or) record is randomly generated from a movie dataset and a batch of `100` (default) is ingested at a time. The batch size can be configured by setting the environment variable `ALIOTH_LOAD_TEST_BATCH_SIZE` at runtime
  4. The vectors as previously stated are of size `100` and they are randomly generated at runtime.
- ### Setup and Configuration
  1. Get the IP of the Qdrant Host (or) Service as well as the REST API Port for Kubernetes as well as docker-compose based deployments and set them as environment variables `QDRANT_DB_HOST` and `QDRANT_DB_PORT` respectively.
     
     1. Docker-compose
     2. Kubernetes
  
  2. (Optional) Set the `ALIOTH_LOAD_TEST_BATCH_SIZE` environment variable using `export ALIOTH_LOAD_TEST_BATCH_SIZE=n`  if required
  4. Run the command: 
        ```bash 
           make load-test-alioth
        ```
  5. Visit the locust dashboard at http://0.0.0.0:8089
## Observability
  Observability is set up using Prometheus & Grafana. Following are the services that are deployed on Kubernetes for Observability purposes:
  
  1. **Prometheus** - A time-series database for storing metrics
  2. **Grafana** - An open-source application for creating beautiful visualizations
  3. **AlertManager** - Handles alerts sent by client applications such as the Prometheus server.
  4. **Kube-state-metrics** - A service that listens to the Kubernetes API server and generates metrics about the state of the objects (pods, deployments, ingress, etc etc)
  5. **Prometheus-node-exporter** - Exposes a wide variety of hardware- and kernel-related metrics
  6. **Prometheus-statsd-exporter** - It is a drop-in replacement for StatsD. This exporter translates StatsD metrics to Prometheus metrics via configured mapping rules (Used for gnuicorn monitoring, as it is officially instrumented to work only with statsd, ref: https://docs.gunicorn.org/en/stable/instrumentation.html)
  7. **Celery-exporter** - Exposes metrics for celery

Other than these services that are explicitly deployed for observability, various applications like RabbtitMQ, Qdrant, and Kubernetes themselves expose their metrics that are scraped by Prometheus.

  As the monitoring stack is deployed on Kubernetes, Prometheus uses service discovery for finding all the metrics endpoints and scraping them. Configuring custom scraping rules is not required.

  > Due to time constraint reasons only a custom-made Qdrant Dashboard is pre-loaded in Grafana and 2 alerts are created for alert-manager. More dashboards and alerts are on the way :))
- ### Dashboards
  - Qdrant Dashboard
- ### Alerts
  1. InstanceDown
  2. QdrantNodeDown

## Makefile Usage
- The following targets are available in the `Makefile` to make setting things up as well as deploying and cleaning up environments easier and predictable manner.

  1. 

## API Usage

## Further Improvements & Ideas:
- Improve health checks for all internal services.
- Implement Kubernetes Event-driven Autoscaling (KEDA) for scaling celery workers and Alioth API based on metrics such as Ready Messages in RabbitMQ, Database load experienced by Qdrant or the rate of data ingestion by Alioth API, etc.(ref: https://keda.sh/)
- Periodic clearing of snapshots to save costs on resources
- Right-size alioth API and workers by observing their resource usage to run a cost-efficient service at scale
- Write end-to-end tests
- Setup flower for celery-specific monitoring (ref: https://flower.readthedocs.io/en/latest/)
- Improve helm chart documentation (ref: https://github.com/norwoodj/helm-docs)
- Add dashboards for Gunicorn, Celery, RabbitMQ

## Authors

- [@coolfool](https://www.github.com/coolfool)

## License

[MIT](https://choosealicense.com/licenses/mit/)
