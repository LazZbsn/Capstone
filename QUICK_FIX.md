# Quick Fix: ModuleNotFoundError: No module named 'flask'

## Problem
All nodes are failing with `ModuleNotFoundError: No module named 'flask'`

## Solution

### Step 1: Stop all running nodes
```bash
./stop.sh
```

### Step 2: Make sure dependencies are installed
```bash
# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Verify Flask is installed
python -c "import flask; print('Flask version:', flask.__version__)"
```

### Step 3: Deploy again
```bash
./deploy.sh
```

### Step 4: Check status
```bash
./check_status.sh
```

## Alternative: Manual Start (for testing)

If deploy.sh still doesn't work, you can start nodes manually:

```bash
source venv/bin/activate

# Start Edge Node 1 (in one terminal)
python src/edge/edge_node.py config/edge_config.json

# In another terminal, start Core Node 1
source venv/bin/activate
python src/core/core_node.py config/core_config.json

# In another terminal, start Cloud Node 1
source venv/bin/activate
python src/cloud/cloud_node.py config/cloud_config.json

# In another terminal, start GUI
source venv/bin/activate
python src/gui/gui_server.py
```

## Verify Installation

Check if all required packages are installed:
```bash
source venv/bin/activate
python -c "import flask, redis, grpcio; print('All packages installed!')"
```

If any package is missing, install it:
```bash
pip install flask flask-cors redis grpcio
```
