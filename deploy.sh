#!/bin/bash
# Complete Fixed Deployment Script

source venv/bin/activate
PYTHON_CMD="python3"
mkdir -p logs
mkdir -p config

echo "========================================="
echo "Generating Missing Configurations..."
echo "========================================="

# Helper to generate configs if they don't exist
generate_config() {
    local src=$1
    local dest=$2
    local old_id=$3
    local new_id=$4
    local old_port=$5
    local new_port=$6

    if [ -f "$src" ]; then
        cp "$src" "$dest"
        sed -i "s/\"node_id\": \"$old_id\"/\"node_id\": \"$new_id\"/" "$dest"
        sed -i "s/\"port\": $old_port/\"port\": $new_port/" "$dest"
        echo "✅ Generated $dest"
    else
        echo "❌ Error: Template $src not found!"
    fi
}

# Generate Cloud, Core, and Edge secondary configs
generate_config "config/cloud_config.json" "config/cloud_config_2.json" "cloud-1" "cloud-2" "7001" "7002"
generate_config "config/core_config.json" "config/core_config_2.json" "core-1" "core-2" "6001" "6002"
generate_config "config/edge_config.json" "config/edge_config_2.json" "edge-1" "edge-2" "5001" "5002"
generate_config "config/edge_config.json" "config/edge_config_3.json" "edge-1" "edge-3" "5001" "5003"

start_node() {
    local name=$1
    local script=$2
    local config=$3
    
    if [ ! -f "$config" ] && [ "$name" != "gui" ]; then
        echo "⚠️ Skipping $name: $config still missing."
        return
    fi

    echo "Starting $name..."
    $PYTHON_CMD "$script" "$config" > "logs/${name}.log" 2>&1 &
    echo $! > "logs/${name}.pid"
    sleep 2
}

echo -e "\nStep 1: Deploying Cloud Layer..."
start_node "cloud-1" "src/cloud/cloud_node.py" "config/cloud_config.json"
start_node "cloud-2" "src/cloud/cloud_node.py" "config/cloud_config_2.json"

echo -e "\nStep 2: Deploying Core Layer..."
start_node "core-1" "src/core/core_node.py" "config/core_config.json"
start_node "core-2" "src/core/core_node.py" "config/core_config_2.json"

echo -e "\nStep 3: Deploying Edge Layer..."
start_node "edge-1" "src/edge/edge_node.py" "config/edge_config.json"
start_node "edge-2" "src/edge/edge_node.py" "config/edge_config_2.json"
start_node "edge-3" "src/edge/edge_node.py" "config/edge_config_3.json"

echo -e "\nStep 4: Deploying GUI..."
start_node "gui" "src/gui/gui_server.py" ""

echo -e "\nDeployment Complete. Access Dashboard: http://localhost:8080"
