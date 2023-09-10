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
  - [Local Setup](#local-setup)
  - [Install Dependencies](#install-dependencies)
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
  
-  ### For deployment

## Development

- ### Install Dependencies
- ### Local Setup
  
## Deploy

- ### Kubernetes
    1. #### Create Kubernetes cluster using K3d
    2. #### Deploy using Helm
      
- ### Docker-compose (Not recommended)
    1. 

## Load Test

- ### Introduction
  
- ### Setup and Testing

## Observability

- ### Monitoring
- ### Alerts

## Usage

## Further Improvements & Ideas:
- health checks for all celery workers
- KEDA
- periodic clearing of snapshots
- Right-size alioth API and workers by observing their resource usage
- Write end-to-end tests
- Setup flower for celery-specific monitoring
- Improve helm chart documentation

## Authors

- [@coolfool](https://www.github.com/coolfool)

## License

[MIT](https://choosealicense.com/licenses/mit/)
