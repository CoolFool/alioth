<div align="center" id = "top">
    <h2>Alioth</h2>
    <h3>Ingest data at scale into a Qdrant DB Cluster</h3>
</div>

## Contents
- [Introduction](#introduction)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
  - [For Development](#for-development)
  - [For Deployment](#for-deployment)
- [Development](#development)
- [Deploy](#deploy)
  - [Kubernetes](#kubernetes)
  - [Docker-Compose (Not Recommended) ](#docker-compose)
- [Load Test](#load-test)
   - [Introduction](#introduction)
   - [Setup and Testing](#setup-and-testing)
- [Observability](#observability)
  - [Introduction](#introduction)
  - [Dashboards](#dashboards)
  - [Alerts](#alerts)
- [Makefile Usage](#makefile-usage)
- [Further Improvements & Ideas](#further-improvements--ideas)
- [Authors](#authors)
- [License](#license)

## Introduction
1. Alioth is a Python application that uses Celery with RabbitMQ as broker and backend to ingest data in a distributed Qdrant Vector database
2. 

## Architecture
1. 

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

  > Due to time constraint reasons only a custom-made Qdrant Dashboard is pre-loaded in Grafana and 2 alerts are created for alert-manager. More dashboards and alerts are on the way :)
- ### Dashboards
  - Qdrant Dashboard
- ### Alerts
  1. InstanceDown
  2. QdrantNodeDown

## Makefile Usage
- The following targets are available in the `Makefile`

  1. 

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
