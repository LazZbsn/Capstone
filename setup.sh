#!/bin/bash
# Refined Setup Script for Distributed Telecom System 

echo "========================================="
echo "Setting up Distributed Telecom System"
echo "========================================="

# 1. Install System Dependencies
echo "Installing system-level dependencies..."
sudo apt-get update && sudo apt-get install -y \
    build-essential python3-dev libpq-dev \
    redis-server protobuf-compiler

# 2. Setup Python Environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate 

echo "Upgrading pip tools..."
pip install --upgrade pip setuptools wheel

# 3. Install Dependencies
echo "Installing Python packages..."
pip install -r requirements.txt [cite: 84, 121]

# 4. gRPC Code Generation
echo "Generating gRPC code from proto files..."
python -m grpc_tools.protoc -I src/common/proto \
    --python_out=src/common/proto \
    --grpc_python_out=src/common/proto \
    src/common/proto/telecom.proto

# 5. Initialize Directories
mkdir -p data logs 
chmod +x deploy.sh stop.sh check_status.sh

echo "Setup complete! Start Redis with 'sudo service redis-server start'."
