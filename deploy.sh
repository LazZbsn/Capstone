#!/bin/bash

# Deployment script for Distributed Telecom System

echo "========================================="
echo "Deploying Distributed Telecom System"
echo "========================================="

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate || venv\Scripts\activate
fi

# Create logs directory
mkdir -p logs

# Function to start a process
start_node() {
    local name=$1
    local script=$2
    local config=$3
    local port=$4
    
    echo "Starting $name..."
    python "$script" "$config" > "logs/${name}.log" 2>&1 &
    echo $! > "logs/${name}.pid"
    sleep 1
    echo "$name started (PID: $(cat logs/${name}.pid))"
}

# Start Edge Nodes
echo "Starting Edge Nodes..."
start_node "edge-1" "src/edge/edge_node.py" "config/edge_config.json" "5001"

# Update config for edge-2 and edge-3
sed 's/"node_id": "edge-1"/"node_id": "edge-2"/' config/edge_config.json > config/edge_config_2.json
sed 's/"port": 5001/"port": 5002/' config/edge_config_2.json > config/edge_config_2_tmp.json && mv config/edge_config_2_tmp.json config/edge_config_2.json

sed 's/"node_id": "edge-1"/"node_id": "edge-3"/' config/edge_config.json > config/edge_config_3.json
sed 's/"port": 5001/"port": 5003/' config/edge_config_3.json > config/edge_config_3_tmp.json && mv config/edge_config_3_tmp.json config/edge_config_3.json

start_node "edge-2" "src/edge/edge_node.py" "config/edge_config_2.json" "5002"
start_node "edge-3" "src/edge/edge_node.py" "config/edge_config_3.json" "5003"

# Start Core Nodes
echo "Starting Core Nodes..."
start_node "core-1" "src/core/core_node.py" "config/core_config.json" "6001"

sed 's/"node_id": "core-1"/"node_id": "core-2"/' config/core_config.json > config/core_config_2.json
sed 's/"port": 6001/"port": 6002/' config/core_config_2.json > config/core_config_2_tmp.json && mv config/core_config_2_tmp.json config/core_config_2.json
sed 's/"coordinator_role": "primary"/"coordinator_role": "secondary"/' config/core_config_2.json > config/core_config_2_tmp.json && mv config/core_config_2_tmp.json config/core_config_2.json

start_node "core-2" "src/core/core_node.py" "config/core_config_2.json" "6002"

# Start Cloud Nodes
echo "Starting Cloud Nodes..."
start_node "cloud-1" "src/cloud/cloud_node.py" "config/cloud_config.json" "7001"

sed 's/"node_id": "cloud-1"/"node_id": "cloud-2"/' config/cloud_config.json > config/cloud_config_2.json
sed 's/"port": 7001/"port": 7002/' config/cloud_config_2.json > config/cloud_config_2_tmp.json && mv config/cloud_config_2_tmp.json config/cloud_config_2.json
sed 's/"role": "primary"/"role": "replica"/' config/cloud_config_2.json > config/cloud_config_2_tmp.json && mv config/cloud_config_2_tmp.json config/cloud_config_2.json

start_node "cloud-2" "src/cloud/cloud_node.py" "config/cloud_config_2.json" "7002"

# Start GUI
echo "Starting GUI Dashboard..."
start_node "gui" "src/gui/gui_server.py" "" "8080"

# Wait a bit for all services to start
sleep 3

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "All nodes started. Access the GUI at:"
echo "  http://localhost:8080"
echo ""
echo "Edge Nodes:"
echo "  - Edge-1: http://localhost:5001"
echo "  - Edge-2: http://localhost:5002"
echo "  - Edge-3: http://localhost:5003"
echo ""
echo "Core Nodes:"
echo "  - Core-1: http://localhost:6001"
echo "  - Core-2: http://localhost:6002"
echo ""
echo "Cloud Nodes:"
echo "  - Cloud-1: http://localhost:7001"
echo "  - Cloud-2: http://localhost:7002"
echo ""
echo "To stop all nodes, run: ./stop.sh"
echo "To view logs, check the logs/ directory"
echo ""
