# Get Node IP
NODE_IP_ALIOTH=$(kubectl get nodes -o custom-columns="INTERNAL-IP:.status.addresses[?(@.type=='InternalIP')].address" --no-headers=true)

get_node_port() {
  local SERVICE_NAME="$1"
  local CONTAINER_PORT="$2"

  # Get the NodePort for the specified container port
  local NODE_PORT=$(kubectl get svc $SERVICE_NAME -o jsonpath="{.spec.ports[?(@.port==$CONTAINER_PORT)].nodePort}")

  # Check if the NODE_PORT is not empty
  if [ -n "$NODE_PORT" ]; then
    echo "$NODE_PORT"
  else
    >&2 echo "Error: Container port $CONTAINER_PORT not found in service $SERVICE_NAME or NodePort not assigned."
    exit 1
  fi
}
echo "INFO: Assuming Local K3D Setup with a single K8s node cluster \n"

echo "Alioth: Ingest data at scale into Qdrant DB Cluster (https://github.com/coolfool/alioth) \n "

# Alioth
ALIOTH_K8S_NODE_PORT=$(get_node_port "alioth" 1337)
echo "-> Alioth: http://$NODE_IP_ALIOTH:$ALIOTH_K8S_NODE_PORT"
echo "-> Alioth Docs: http://$NODE_IP_ALIOTH:$ALIOTH_K8S_NODE_PORT/docs"

# Qdrant
QDRANT_K8S_REST_NODE_PORT=$(get_node_port "qdrant" 6333)
echo "-> Qdrant REST Endpoint: http://$NODE_IP_ALIOTH:$QDRANT_K8S_REST_NODE_PORT"
echo "-> Qdrant Dashboard: http://$NODE_IP_ALIOTH:$QDRANT_K8S_REST_NODE_PORT/dashboard"
QDRANT_K8S_GRPC_NODE_PORT=$(get_node_port "qdrant" 6334)
echo "-> Qdrant GRPC Endpoint: http://$NODE_IP_ALIOTH:$QDRANT_K8S_GRPC_NODE_PORT"

# Grafana
GRAFANA_K8S_NODE_PORT=$(get_node_port "alioth-grafana" 80)
echo "-> Grafana: http://$NODE_IP_ALIOTH:$GRAFANA_K8S_NODE_PORT (credentials => 'admin': 'supersecret')"

# Minio
MINIO_K8S_CONSOLE_NODE_PORT=$(get_node_port "minio-console" 9001)
echo "-> Minio Console: http://$NODE_IP_ALIOTH:$MINIO_K8S_CONSOLE_NODE_PORT (credentials => 'minio-console': 'supersecret')"

# RabbitMQ
RABBITMQ_K8S_MANAGEMENT_NODE_PORT=$(get_node_port "rabbitmq" 15672)
echo "-> RabbitMQ Management Console: http://$NODE_IP_ALIOTH:$RABBITMQ_K8S_MANAGEMENT_NODE_PORT (credentials => 'user': 'supersecret')"

# Prometheus
PROMETHEUS_K8S_NODE_PORT=$(get_node_port "alioth-prometheus-server" 80)
echo "-> Prometheus: http://$NODE_IP_ALIOTH:$PROMETHEUS_K8S_NODE_PORT"

