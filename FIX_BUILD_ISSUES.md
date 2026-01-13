# Fixing Build Issues for grpcio, grpcio-tools, and psycopg2-binary

## Problem
Getting "Failed to build installable wheels" errors for:
- grpcio
- grpcio-tools  
- psycopg2-binary

## Solutions

### Step 1: Install System Dependencies (Required)

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y build-essential python3-dev libpq-dev
```

**On CentOS/RHEL:**
```bash
sudo yum install -y gcc gcc-c++ python3-devel postgresql-devel
```

**On Fedora:**
```bash
sudo dnf install -y gcc gcc-c++ python3-devel postgresql-devel
```

### Step 2: Upgrade pip, setuptools, and wheel

```bash
pip install --upgrade pip setuptools wheel
```

### Step 3: Install Dependencies

**Option A: Install all at once (recommended)**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Option B: Install problematic packages separately**
```bash
source venv/bin/activate

# Install grpcio first (newer version supports Python 3.13)
pip install grpcio>=1.66.2 grpcio-tools>=1.66.2

# Install psycopg2-binary (requires libpq-dev)
pip install psycopg2-binary

# Then install the rest
pip install -r requirements.txt
```

### Step 4: If psycopg2-binary still fails (Optional - PostgreSQL is optional)

If you don't need PostgreSQL support, you can skip it:

```bash
# Install everything except psycopg2-binary
pip install grpcio>=1.66.2 grpcio-tools>=1.66.2 flask==3.0.0 flask-cors==4.0.0 redis==5.0.1 pymongo==4.6.0 pika==1.3.2 prometheus-client==0.19.0 psutil==5.9.6 numpy==1.26.2 protobuf==4.25.1 python-json-logger==2.0.7 click==8.1.7 pyyaml==6.0.1 requests==2.31.0
```

The system will work without PostgreSQL - cloud nodes will use in-memory storage instead.

## Quick Fix Script

Run this on your Linux machine:

```bash
#!/bin/bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y build-essential python3-dev libpq-dev

# Upgrade pip tools
pip install --upgrade pip setuptools wheel

# Activate venv and install
source venv/bin/activate
pip install -r requirements.txt
```

## Verify Installation

```bash
python -c "import grpcio; print('grpcio:', grpcio.__version__)"
python -c "import psycopg2; print('psycopg2 installed')" 2>/dev/null || echo "psycopg2 not installed (optional)"
```

## Notes

- **grpcio 1.59.0** doesn't support Python 3.13. Updated to >=1.66.2 in requirements.txt
- **psycopg2-binary** requires PostgreSQL development libraries (libpq-dev)
- PostgreSQL is **optional** - the system works without it using in-memory storage
