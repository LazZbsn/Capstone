#!/bin/bash

# Setup script for Distributed Telecom System

echo "========================================="
echo "Setting up Distributed Telecom System"
echo "========================================="

# Check Python version
echo "Checking Python version..."
python3 --version || python --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv || python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || venv\Scripts\activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Generate gRPC code from proto files
echo "Generating gRPC code..."
if command -v protoc &> /dev/null; then
    python -m grpc_tools.protoc -I src/common/proto --python_out=src/common/proto --grpc_python_out=src/common/proto src/common/proto/telecom.proto
    echo "gRPC code generated successfully"
else
    echo "Warning: protoc not found. gRPC code generation skipped."
    echo "Install protobuf compiler: https://grpc.io/docs/protoc-installation/"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p data logs

# Check for Redis (optional but recommended)
echo "Checking for Redis..."
if command -v redis-server &> /dev/null; then
    echo "Redis found. You can start it with: redis-server"
else
    echo "Warning: Redis not found. Install Redis for caching support."
    echo "On Ubuntu: sudo apt-get install redis-server"
    echo "On macOS: brew install redis"
fi

# Check for PostgreSQL (optional)
echo "Checking for PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "PostgreSQL found."
else
    echo "Info: PostgreSQL not found. Cloud nodes will use in-memory storage."
    echo "Install PostgreSQL for persistent storage."
fi

echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
echo "2. Start Redis: redis-server"
echo "3. Run deployment script: ./deploy.sh"
echo "4. Access GUI at: http://localhost:8080"
echo ""
