# Setup and Deployment Guide

## Prerequisites

### Required Software
- Python 3.9 or higher
- pip (Python package manager)

### Optional Software (Recommended)
- Redis (for caching)
- PostgreSQL (for persistent storage)
- Docker & Docker Compose (for containerized deployment)

## Installation Steps

### 1. Clone/Navigate to Project Directory

```bash
cd distributed-telecom-system
```

### 2. Setup Python Environment

#### Linux/macOS:
```bash
chmod +x setup.sh deploy.sh stop.sh
./setup.sh
```

#### Windows:
```powershell
# Run PowerShell as Administrator if needed
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install Optional Dependencies

#### Redis (for Edge Node Caching)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows:**
Download from: https://github.com/microsoftarchive/redis/releases

#### PostgreSQL (for Cloud Node Storage)

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download from: https://www.postgresql.org/download/windows/

### 4. Deploy the System

#### Linux/macOS:
```bash
./deploy.sh
```

#### Windows:
```powershell
.\deploy.ps1
```

#### Using Docker:
```bash
docker-compose up -d
```

### 5. Access the Dashboard

Open your web browser and navigate to:
```
http://localhost:8080
```

## Architecture Overview

The system consists of:

1. **3 Edge Nodes** (ports 5001-5003)
   - Handle user requests with low latency
   - Implement caching for frequently accessed data
   - Report load metrics to core nodes

2. **2 Core Nodes** (ports 6001-6002)
   - Coordinate distributed transactions (2PC)
   - Load balancing across edge and cloud nodes
   - Fault tolerance management

3. **2 Cloud Nodes** (ports 7001-7002)
   - Persistent data storage
   - Data replication (primary-replica)
   - Transaction participants

4. **GUI Dashboard** (port 8080)
   - Real-time monitoring
   - System metrics visualization
   - Transaction management interface

## Testing the System

### 1. Send a Test Request

```bash
curl -X POST http://localhost:5001/api/request \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-1",
    "operation": "test",
    "data": {"key": "value"}
  }'
```

### 2. Create a Transaction

```bash
curl -X POST http://localhost:6001/api/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn-1",
    "operations": [
      {
        "operation_id": "op-1",
        "node_id": "cloud-1",
        "operation_type": "write",
        "parameters": {"key": "test_key", "value": "test_value"}
      }
    ]
  }'
```

### 3. Check Node Metrics

```bash
# Edge Node
curl http://localhost:5001/api/metrics

# Core Node
curl http://localhost:6001/api/metrics

# Cloud Node
curl http://localhost:7001/api/metrics
```

## Stopping the System

#### Linux/macOS:
```bash
./stop.sh
```

#### Windows:
```powershell
.\stop.ps1
```

#### Using Docker:
```bash
docker-compose down
```

## Troubleshooting

### Port Already in Use
If you get "port already in use" errors:
1. Check what's using the port: `netstat -an | grep <port>` (Linux) or `netstat -an | findstr <port>` (Windows)
2. Kill the process or change the port in config files

### Redis Connection Error
- Ensure Redis is running: `redis-cli ping` (should return PONG)
- Check Redis is listening on default port 6379

### Module Not Found Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Nodes Not Starting
- Check logs in `logs/` directory
- Ensure all dependencies are installed
- Verify configuration files are correct

## Performance Tuning

### Adjust Node Counts
Edit configuration files in `config/` directory to adjust:
- Number of edge/core/cloud nodes
- Port numbers
- Timeout values
- Replication settings

### Monitoring
- Access Prometheus metrics: `http://localhost:9091/metrics` (Edge), `http://localhost:9092/metrics` (Core), etc.
- Check logs: `tail -f logs/*.log`

## Security Considerations

- **Production Deployment:**
  - Use HTTPS instead of HTTP
  - Implement authentication/authorization
  - Use secure database passwords
  - Enable firewall rules
  - Use secrets management for credentials

- **Network Security:**
  - Restrict port access to trusted networks
  - Use VPN for remote access
  - Implement rate limiting

## Next Steps

1. **Customize Configuration**: Edit files in `config/` directory
2. **Add Your Business Logic**: Implement your specific telecom operations
3. **Scale Horizontally**: Add more nodes as needed
4. **Integrate with External Services**: Connect to real databases, message queues, etc.
5. **Deploy to Production**: Use container orchestration (Kubernetes) for production

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review architecture documentation in `ARCHITECTURE.md`
3. Verify all prerequisites are installed correctly
